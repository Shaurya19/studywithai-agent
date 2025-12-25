from google.adk.agents import Agent
import importlib.util
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google AI API key
google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    os.environ["GOOGLE_API_KEY"] = google_api_key

# Load flashcard agent
flashcard_agent_path = Path(__file__).parent / "sub_agents" / "flashcard_agent" / "agent.py"
flashcard_spec = importlib.util.spec_from_file_location("flashcard_agent_module", flashcard_agent_path)
flashcard_module = importlib.util.module_from_spec(flashcard_spec)
flashcard_spec.loader.exec_module(flashcard_module)
flashcard_agent = flashcard_module.flashcard_agent

# Load quiz agent
quiz_agent_path = Path(__file__).parent / "sub_agents" / "quiz_agent" / "agent.py"
quiz_spec = importlib.util.spec_from_file_location("quiz_agent_module", quiz_agent_path)
quiz_module = importlib.util.module_from_spec(quiz_spec)
quiz_spec.loader.exec_module(quiz_module)
quiz_agent = quiz_module.quiz_agent

# Create the root StudyWithAI agent
root_agent = Agent(
    name="studywithai_agent",
    model="gemini-2.5-flash-lite",
    description="StudyWithAI agent that helps create flashcards and quizzes from text content or PDF files",
    instruction="""
    You are StudyWithAI, an intelligent educational assistant that helps students create effective study materials.
    Your role is to analyze content provided by users and create appropriate study materials based on their needs.

    **IMPORTANT: When educational content is provided to you, immediately process it and delegate to the appropriate agent. Do NOT ask for more content or clarification unless the content is truly insufficient.**

    You are responsible for delegating tasks to the following agents:
    - flashcard_agent: Returns JSON with flashcards array
    - quiz_agent: Returns JSON with quiz_questions array

    **Task Processing Guidelines:**

    When users request study materials:

    1. **If they request flashcards**: Immediately delegate to the flashcard_agent with the provided content
    2. **If they request a quiz**: Immediately delegate to the quiz_agent with the provided content  
    3. **If they request both**: Delegate to both agents sequentially and combine their JSON responses
    4. **If the request type is unclear**: Default to creating flashcards

    **Response Format:**
    
    For flashcards only requests, return the exact JSON from flashcard_agent:
    ```json
    {
        "flashcards": [...]
    }
    ```

    For quiz only requests, return the exact JSON from quiz_agent:
    ```json
    {
        "quiz_questions": [...]
    }
    ```

    For both flashcards and quiz requests, combine the JSON responses:
    ```json
    {
        "flashcards": [...],
        "quiz_questions": [...]
    }
    ```

    **CRITICAL: Always return valid JSON only. Do not include any explanatory text outside the JSON structure. Pass the educational content directly to the sub-agents without modification.**

    Always be helpful, educational, and focused on creating high-quality study materials that enhance learning.
    """,
    sub_agents=[flashcard_agent, quiz_agent],
)