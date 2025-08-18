"""
StudyWithAI API

A simplified REST API for generating flashcards and quizzes from educational content.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import io
import PyPDF2
import re
import importlib.util
from pathlib import Path
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import uuid
import json
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("studywithai.api")

# Configure Google AI API
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    raise ValueError("GOOGLE_API_KEY is required")

# Set the Google API key as environment variable for the SDK
os.environ["GOOGLE_API_KEY"] = google_api_key
logger.info("Google API key configured successfully")

# Load the StudyWithAI agent
agent_path = Path(__file__).parent / "studywithai-agent" / "agent.py"
spec = importlib.util.spec_from_file_location("agent_module", agent_path)
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)
root_agent = agent_module.root_agent

# Initialize FastAPI app
app = FastAPI(
    title="StudyWithAI API",
    description="Generate flashcards and quizzes from educational content",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize session service
session_service = InMemorySessionService()
logger.info("Initialized InMemorySessionService for StudyWithAI API")

# Pydantic models for response
class Flashcard(BaseModel):
    number: int
    front: str
    back: str

class QuizQuestion(BaseModel):
    number: int
    type: str
    difficulty: str
    question: str
    options: List[str]
    answer: str
    explanation: str

class FlashcardResponse(BaseModel):
    success: bool
    message: str
    session_id: str
    flashcards: List[Flashcard]

class QuizResponse(BaseModel):
    success: bool
    message: str
    session_id: str
    quiz_questions: List[QuizQuestion]

# Helper functions
def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extract text content from PDF bytes."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def parse_flashcards(response: str) -> List[dict]:
    """Parse flashcard response from JSON format."""
    try:
        # Log the raw response for debugging
        logger.info(f"Raw flashcard response: {response[:500]}...")
        
        # Clean up the response - remove markdown code blocks if present
        clean_response = response.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        logger.info(f"Cleaned response: {clean_response[:500]}...")
        
        data = json.loads(clean_response)
        flashcards = []
        
        if 'flashcards' in data:
            raw_flashcards = data['flashcards']
            logger.info(f"Found {len(raw_flashcards)} raw flashcards")
        else:
            logger.warning("No 'flashcards' key found in response data")
            raw_flashcards = []
        
        # Ensure each flashcard has the required fields
        for i, card in enumerate(raw_flashcards, 1):
            if isinstance(card, dict):
                flashcard = {
                    'number': card.get('number', i),
                    'front': card.get('front', ''),
                    'back': card.get('back', '')
                }
                if flashcard['front'] and flashcard['back']:  # Only add if both front and back exist
                    flashcards.append(flashcard)
                    logger.info(f"Added flashcard {i}: front='{flashcard['front'][:50]}...', back='{flashcard['back'][:50]}...'")
                else:
                    logger.warning(f"Skipped flashcard {i}: missing front or back content")
        
        logger.info(f"Returning {len(flashcards)} valid flashcards")
        return flashcards
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        logger.error(f"Failed to parse response: {response[:200]}...")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in parse_flashcards: {e}")
        return []

def parse_quiz_questions(response: str) -> List[dict]:
    """Parse quiz response from JSON format."""
    try:
        # Clean up the response - remove markdown code blocks if present
        clean_response = response.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        data = json.loads(clean_response)
        quiz_questions = []
        
        if 'quiz_questions' in data:
            raw_questions = data['quiz_questions']
        else:
            raw_questions = []
        
        # Ensure each quiz question has the required fields
        for i, question in enumerate(raw_questions, 1):
            if isinstance(question, dict):
                quiz_question = {
                    'number': question.get('number', i),
                    'type': question.get('type', 'multiple_choice'),
                    'difficulty': question.get('difficulty', 'medium'),
                    'question': question.get('question', ''),
                    'options': question.get('options', []) if question.get('options') else [],
                    'answer': question.get('answer', ''),
                    'explanation': question.get('explanation', '')
                }
                if quiz_question['question'] and quiz_question['answer']:  # Only add if question and answer exist
                    quiz_questions.append(quiz_question)
        
        return quiz_questions
    except json.JSONDecodeError:
        return []

async def generate_study_materials(content: str, material_type: str, session_id: str, num_items: int) -> str:
    """Generate study materials using the StudyWithAI agent."""
    try:
        app_name = "studywithai_api"
        user_id = "api_user"
        
        # Create or get session
        try:
            session = session_service.get_session(app_name, user_id, session_id)
        except:
            session = session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                state={}
            )
        
        # Create the prompt based on material type
        if material_type.lower() == "flashcards":
            prompt = f"Create {num_items} flashcards from this educational content:\n\n{content}"
        elif material_type.lower() == "quiz":
            prompt = f"Create a quiz with {num_items} questions from this educational content:\n\n{content}"
        
        # Create a runner for the agent
        runner = Runner(
            agent=root_agent,
            app_name=app_name,
            session_service=session_service,
        )
        
        # Format message to the agent
        content_obj = types.Content(role="user", parts=[types.Part(text=prompt)])
        final_response = None
        
        # Process the agent's response
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content_obj
        ):
            if event.is_final_response():
                final_response = event
        
        # Extract the response text
        if final_response and final_response.content and final_response.content.parts:
            response_text = ""
            for part in final_response.content.parts:
                if hasattr(part, 'text'):
                    response_text += part.text
            return response_text
        else:
            raise HTTPException(status_code=500, detail="No response received from agent")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating study materials: {str(e)}")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "StudyWithAI API",
        "version": "2.0.0",
        "description": "Generate flashcards and quizzes from educational content",
        "endpoints": {
            "POST /generate-flashcards": "Generate flashcards from prompt and optional files",
            "POST /generate-quiz": "Generate quiz from prompt and optional files",
            "GET /health": "Health check endpoint",
            "GET /docs": "API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "StudyWithAI API"}

@app.post("/generate-flashcards", response_model=FlashcardResponse)
async def generate_flashcards(
    prompt: str = Form(...),
    num_flashcards: int = Form(10, description="Number of flashcards to generate (default: 10)"),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Generate flashcards from prompt and optional files.
    
    - **prompt**: The educational prompt or content to process
    - **num_flashcards**: Number of flashcards to generate (default: 10)
    - **files**: Optional PDF files to upload and process
    """
    try:
        # Start with the prompt content
        content = prompt
        
        # Process uploaded files if any
        if files:
            for file in files:
                if file.filename.endswith('.pdf'):
                    pdf_content = await file.read()
                    file_text = extract_text_from_pdf(pdf_content)
                    content += f"\n\nContent from {file.filename}:\n{file_text}"
                else:
                    raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Generate flashcards with specified number
        response = await generate_study_materials(content, "flashcards", session_id, num_flashcards)
        
        # Parse the response
        flashcards = parse_flashcards(response)
        
        return FlashcardResponse(
            success=True,
            message=f"Generated {len(flashcards)} flashcards successfully",
            session_id=session_id,
            flashcards=[Flashcard(**card) for card in flashcards]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(
    prompt: str = Form(...),
    num_questions: int = Form(5, description="Number of quiz questions to generate (default: 5)"),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Generate quiz from prompt and optional files.
    
    - **prompt**: The educational prompt or content to process
    - **num_questions**: Number of quiz questions to generate (default: 5)
    - **files**: Optional PDF files to upload and process
    """
    try:
        # Start with the prompt content
        content = prompt
        
        # Process uploaded files if any
        if files:
            for file in files:
                if file.filename.endswith('.pdf'):
                    pdf_content = await file.read()
                    file_text = extract_text_from_pdf(pdf_content)
                    content += f"\n\nContent from {file.filename}:\n{file_text}"
                else:
                    raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Generate quiz with specified number of questions
        response = await generate_study_materials(content, "quiz", session_id, num_questions)
        
        # Parse the response
        quiz_questions = parse_quiz_questions(response)
        
        return QuizResponse(
            success=True,
            message=f"Generated {len(quiz_questions)} quiz questions successfully",
            session_id=session_id,
            quiz_questions=[QuizQuestion(**question) for question in quiz_questions]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error": f"HTTP {exc.status_code}"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "error": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)