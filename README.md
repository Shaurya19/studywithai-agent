# StudyWithAI Agent

This agent helps students create effective study materials from text content or PDF files. It uses specialized subagents to generate flashcards and quizzes tailored to the provided educational content.

## What is StudyWithAI Agent?

StudyWithAI is a multi-agent system in ADK that combines specialized agents to create comprehensive study materials. It analyzes educational content and produces either flashcards for memorization or quizzes for knowledge assessment based on user needs.

## Architecture

The system consists of:

1. **Main StudyWithAI Agent**: Coordinates between subagents and handles user interaction
2. **Flashcard Agent**: Specializes in creating flashcards for memorization and quick review
3. **Quiz Agent**: Specializes in generating various types of quiz questions for assessment

## Features

### Flashcard Agent
- Creates comprehensive flashcard sets from educational content
- Focuses on key terms, definitions, concepts, and facts
- Supports multiple flashcard types:
  - Definition cards
  - Concept explanation cards
  - Example cards
  - Formula cards
  - Date/event cards
  - Process cards
  - Comparison cards
- Formats flashcards with clear questions and concise answers

### Quiz Agent
- Generates various types of quiz questions
- Supports multiple question formats:
  - Multiple choice questions
  - True/false questions
  - Short answer questions
- Balances difficulty levels (easy, medium, hard)
- Provides explanations for correct answers
- Creates 8-15 questions per content piece

### REST API
- **FastAPI-based**: Modern, fast, and well-documented API
- **Multiple input methods**: Text content and PDF file upload
- **JSON responses**: Structured flashcards and quiz data
- **Session management**: Maintains context across requests
- **Error handling**: Comprehensive error responses
- **Interactive documentation**: Auto-generated API docs
- **CORS support**: Ready for web applications

## Getting Started

### Prerequisites

1. Activate the virtual environment from the root directory:
```bash
# macOS/Linux:
source ../.venv/bin/activate
# Windows CMD:
..\.venv\Scripts\activate.bat
# Windows PowerShell:
..\.venv\Scripts\Activate.ps1
```

2. Make sure your Google API key is set up:
   - Copy `.env.example` to `.env` if it exists
   - Add your Google API key: `GOOGLE_API_KEY=your_api_key_here`

### Local Development

1. Install API dependencies:
```bash
cd studywithai-agent
pip install -r api_requirements.txt
```

2. Launch the API server:
```bash
python run_api.py
# Or directly:
uvicorn api:app --reload
```

3. Access the API:
   - **API Base URL**: http://localhost:8000
   - **Interactive Documentation**: http://localhost:8000/docs
   - **ReDoc Documentation**: http://localhost:8000/redoc

### Using ADK Web Interface

```bash
cd studywithai-agent
adk web
```

Then select "studywithai_agent" from the dropdown menu in the web UI.

## API Usage

### REST API Endpoints

#### POST /generate-flashcards
Generate flashcards from prompt and optional files.

**Form Data:**
- `prompt`: The educational prompt or content to process
- `num_flashcards`: Number of flashcards to generate (default: 10)
- `files`: Optional PDF files to upload and process

#### POST /generate-quiz
Generate quiz from prompt and optional files.

**Form Data:**
- `prompt`: The educational prompt or content to process
- `num_questions`: Number of quiz questions to generate (default: 5)
- `files`: Optional PDF files to upload and process

#### GET /health
Health check endpoint.

#### GET /
API information and available endpoints.

### Example API Usage

**Using curl:**
```bash
# Generate flashcards from text
curl -X POST "http://localhost:8000/generate-flashcards" \
     -F "prompt=Photosynthesis is the process by which plants convert light energy, carbon dioxide, and water into glucose and oxygen." \
     -F "num_flashcards=5"

# Upload PDF and generate quiz
curl -X POST "http://localhost:8000/generate-quiz" \
     -F "file=@educational-content.pdf" \
     -F "num_questions=10"
```

**Using Python requests:**
```python
import requests

# Generate flashcards from text
response = requests.post("http://localhost:8000/generate-flashcards", data={
    "prompt": "Your educational content here...",
    "num_flashcards": 10
})

data = response.json()
flashcards = data["flashcards"]
```

## Content Types Supported

- **Plain Text**: Articles, notes, textbook excerpts
- **PDF Files**: Educational documents (text will be extracted automatically)
- **Specific Topics**: Subject matter you want to study

## Study Material Guidelines

### When to Use Flashcards
- Memorizing definitions and terminology
- Learning key facts and dates
- Studying formulas and equations
- Quick review sessions
- Building foundational knowledge

### When to Use Quizzes
- Testing comprehension and understanding
- Preparing for exams
- Assessing knowledge retention
- Identifying knowledge gaps
- Practicing problem-solving

## Best Practices

1. **Provide Context**: Give enough content for meaningful study materials
2. **Specify Preferences**: Choose the appropriate material type for your study goals
3. **Review and Practice**: Use the generated materials actively for studying
4. **Use Both Modes**: Combine flashcards for memorization and quizzes for testing

## Troubleshooting

### Common Issues
- **Import Errors**: Make sure you're running from the correct directory and have installed all dependencies
- **PDF Reading Issues**: Ensure PDF files are text-based (not scanned images)
- **Agent Connection**: Verify your Google API key is properly set
- **API Errors**: Check the interactive documentation at `/docs` for proper request format

### Getting Help
- Check the terminal output for detailed error messages
- Ensure all required packages are installed
- Verify the agent is working with `adk web` first
- Use the interactive API documentation at `/docs` for testing

## Additional Resources

- [ADK Multi-Agent Systems Documentation](https://google.github.io/adk-docs/agents/multi-agent-systems/)
- [ADK Getting Started Guide](https://google.github.io/adk-docs/get-started/quickstart/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)