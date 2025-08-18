# StudyWithAI Agent

This agent helps students create effective study materials from text content or PDF files. It uses specialized subagents to generate flashcards and quizzes tailored to the provided educational content.

## What is StudyWithAI Agent?

StudyWithAI is a multi-agent system in ADK that combines specialized agents to create comprehensive study materials. It analyzes educational content and produces either flashcards for memorization or quizzes for knowledge assessment based on user needs.

## Architecture

The system consists of:

1. **Main StudyWithAI Agent**: Coordinates between subagents and handles user interaction
2. **Flashcard Agent**: Specializes in creating flashcards for memorization and quick review
3. **Quiz Agent**: Specializes in generating various types of quiz questions for assessment

## Project Structure

```
14-studywithai-agent/
├── README.md                       # This documentation
├── api.py                         # FastAPI REST API
├── api_requirements.txt           # API dependencies
├── run_api.py                     # API launch script
└── studywithai-agent/             # Agent package
    ├── __init__.py                # Package initialization
    ├── agent.py                   # Main StudyWithAI agent (root_agent)
    └── sub_agents/                # Sub-agents folder
        ├── __init__.py            # Sub-agents initialization
        ├── flashcard_agent/       # Flashcard creation agent
        │   └── agent.py
        └── quiz_agent/            # Quiz generation agent
            └── agent.py
```

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
  - Fill-in-the-blank questions
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

### Using the REST API

1. Install API dependencies:
```bash
cd 14-studywithai-agent
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

#### POST /generate
Generate study materials from text content.

**Request Body:**
```json
{
  "content": "Your educational text content here...",
  "material_type": "both",  // "flashcards", "quiz", or "both"
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Study materials generated successfully",
  "session_id": "generated-session-id",
  "flashcards": [
    {
      "number": 1,
      "front": "What is photosynthesis?",
      "back": "The process by which plants convert light energy..."
    }
  ],
  "quiz_questions": [
    {
      "number": 1,
      "type": "Multiple Choice",
      "difficulty": "Medium",
      "question": "Which organelle is responsible for photosynthesis?",
      "options": ["Mitochondria", "Chloroplast", "Nucleus", "Ribosome"],
      "answer": "B) Chloroplast",
      "explanation": "Chloroplasts contain chlorophyll..."
    }
  ],
  "raw_response": "Full agent response..."
}
```

#### POST /generate-from-pdf
Generate study materials from an uploaded PDF file.

**Form Data:**
- `file`: PDF file to upload
- `material_type`: "flashcards", "quiz", or "both"
- `session_id`: Optional session ID

#### GET /health
Health check endpoint.

#### GET /
API information and available endpoints.

### Example API Usage

**Using curl:**
```bash
# Generate flashcards from text
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Photosynthesis is the process by which plants convert light energy, carbon dioxide, and water into glucose and oxygen.",
       "material_type": "flashcards"
     }'

# Upload PDF and generate quiz
curl -X POST "http://localhost:8000/generate-from-pdf" \
     -F "file=@educational-content.pdf" \
     -F "material_type=quiz"
```

**Using Python requests:**
```python
import requests

# Generate study materials from text
response = requests.post("http://localhost:8000/generate", json={
    "content": "Your educational content here...",
    "material_type": "both"
})

data = response.json()
flashcards = data["flashcards"]
quiz_questions = data["quiz_questions"]
```

## Example Usage

### Creating Flashcards via API
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Photosynthesis is the process by which plants convert light energy, carbon dioxide, and water into glucose and oxygen. This process occurs in chloroplasts and involves two main stages: the light-dependent reactions and the Calvin cycle.",
       "material_type": "flashcards"
     }'
```

### Creating Quizzes via API
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "World War II ended in 1945 with the surrender of Germany in May and Japan in August. The war involved over 30 countries and resulted in significant changes to the global political landscape.",
       "material_type": "quiz"
     }'
```

### Creating Both via API
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Quadratic equations are polynomial equations of degree 2. They can be solved using the quadratic formula: x = (-b ± √(b²-4ac)) / 2a",
       "material_type": "both"
     }'
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
4. **Iterate**: Use session IDs to maintain context across multiple requests
5. **Use Both Modes**: Combine flashcards for memorization and quizzes for testing

## Deployment

### Production Considerations

1. **API Security**: 
   - Configure CORS origins for production
   - Add API authentication if needed
   - Use environment variables for sensitive data

2. **Performance**:
   - Use a production ASGI server like Gunicorn with Uvicorn workers
   - Implement rate limiting
   - Add caching for frequently requested content

3. **Monitoring**:
   - Add logging and monitoring
   - Implement health checks
   - Track API usage and performance

### Docker Deployment (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY api_requirements.txt .
RUN pip install -r api_requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

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