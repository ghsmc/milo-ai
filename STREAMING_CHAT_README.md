# Milo Streaming Chat API

## Overview

The Milo Streaming Chat API provides a real-time, conversational interface for Yale students to discover their career paths through a structured 6-step process. It features:

- **Latest OpenAI Model**: Uses GPT-4o for enhanced responses
- **Real-time Streaming**: Responses stream in real-time for better user experience
- **Conversation Context**: Maintains conversation history and context across messages
- **6-Step Career Discovery**: Structured conversation flow for comprehensive career guidance
- **Yale-Specific Resources**: Deep knowledge of Yale programs, courses, and alumni networks

## Features

### 🎯 6-Step Career Discovery Process

1. **DISCOVER**: Identify student interests and passions
2. **EXPLORE DREAM JOBS**: Suggest specific career paths
3. **NEXT MOVES THIS SEMESTER**: Concrete actions for current semester
4. **REAL OPPORTUNITIES**: Actual programs and funding opportunities
5. **CONNECT**: Networking templates and outreach strategies
6. **REFLECT & ITERATE**: Deep dive or explore alternatives

### 💬 Streaming Chat Features

- Real-time response streaming
- Conversation context management
- Session-based conversations
- Interest extraction and tracking
- Step progression tracking

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn openai python-dotenv
```

### 2. Set Environment Variables

Create a `.env` file with your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start the API Server

```bash
python start_streaming_chat.py
```

The API will be available at `http://localhost:8000`

### 4. Test the Chat Interface

Open `test_chat_interface.html` in your browser to test the streaming chat functionality.

## API Endpoints

### POST `/chat/stream`
Stream chat responses using Server-Sent Events (SSE).

**Request Body:**
```json
{
  "message": "I love data science and global issues",
  "session_id": "optional_session_id"
}
```

**Response:** Server-Sent Events stream with real-time chat responses.

### GET `/chat/history/{session_id}`
Get chat history for a session.

**Response:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "I love data science",
      "timestamp": "2024-01-01T12:00:00"
    }
  ],
  "session_info": {
    "session_id": "default",
    "current_step": 1,
    "student_interests": ["data science"],
    "career_paths": [],
    "message_count": 1,
    "created_at": "2024-01-01T12:00:00",
    "last_updated": "2024-01-01T12:00:00"
  }
}
```

### GET `/chat/session/{session_id}`
Get session information.

### DELETE `/chat/session/{session_id}`
Clear a conversation session.

### GET `/chat/sessions`
List all active sessions.

## Testing

### Python Test Script

Run the comprehensive test script:

```bash
python test_streaming_chat.py
```

This will test:
- Streaming chat functionality
- Session management
- Conversation context
- Interest extraction

### HTML Test Interface

Open `test_chat_interface.html` in your browser for an interactive test interface.

## Architecture

### Core Components

1. **MiloAI Class** (`milo_ai.py`)
   - Enhanced with streaming capabilities
   - Conversation context management
   - New 6-step master prompt
   - Session management

2. **Streaming Chat API** (`streaming_chat_api.py`)
   - FastAPI-based REST API
   - Server-Sent Events for streaming
   - Session management endpoints
   - CORS support

3. **Test Interface** (`test_chat_interface.html`)
   - Interactive web interface
   - Real-time streaming display
   - Session management UI

### Key Features

- **Context Awareness**: Maintains conversation history and extracts student interests
- **Step Tracking**: Tracks progress through the 6-step career discovery process
- **Yale Integration**: Deep knowledge of Yale-specific resources, courses, and programs
- **Real-time Streaming**: Uses OpenAI's streaming API for immediate responses

## Master Prompt

The system uses a comprehensive master prompt that includes:

- 6-step conversation structure
- Yale-specific resources and programs
- Funding opportunities and deadlines
- Networking templates
- Course recommendations
- Alumni network integration

## Session Management

Each conversation session maintains:

- Message history
- Current step in the 6-step process
- Extracted student interests
- Suggested career paths
- Timestamps and metadata

## Error Handling

The API includes comprehensive error handling:

- OpenAI API errors
- Session management errors
- Streaming connection errors
- Input validation

## Development

### Adding New Features

1. **Modify the Master Prompt**: Update the prompt in `MiloAI.__init__()`
2. **Add New Endpoints**: Extend `streaming_chat_api.py`
3. **Update Session Data**: Modify session management methods
4. **Test Changes**: Use the provided test scripts

### Environment Variables

- `OPENAI_API_KEY`: Required for OpenAI API access
- `DATABASE_URL`: Optional for Yale alumni data (PostgreSQL)
- Other database configurations as needed

## Production Deployment

For production deployment:

1. Set up proper CORS origins
2. Configure environment variables
3. Set up database connections
4. Use a production WSGI server
5. Configure proper logging and monitoring

## Support

For issues or questions:

1. Check the test scripts for examples
2. Review the API documentation at `/docs`
3. Check environment variable configuration
4. Review error logs for debugging

## License

This project is part of the Milo AI system for Yale University career guidance.
