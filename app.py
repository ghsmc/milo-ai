from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from milo_ai import MiloAI
import uvicorn
import os
import json
from typing import Optional, List
# Import will be done after app creation to avoid circular imports

print("🚀 Starting Milo AI Backend...")
print(f"📁 Working directory: {os.getcwd()}")
print(f"🔑 OpenAI API Key present: {'OPENAI_API_KEY' in os.environ}")

app = FastAPI()

# Add CORS middleware
import os
allowed_origins = [
    "http://localhost:5173", 
    "http://localhost:3000", 
    "http://127.0.0.1:5173",
    "https://milo.now",
    "https://www.milo.now",
    "https://milo-ai-frontend-production.up.railway.app",
    "https://milo-ai-frontend-production-*.up.railway.app"
]

# Add production origins from environment variable
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Initialize Milo AI
try:
    milo = MiloAI()
    print("✅ Milo AI initialized successfully")
except Exception as e:
    print(f"❌ Error initializing Milo AI: {e}")
    # Create a dummy milo object for basic functionality
    class DummyMilo:
        async def analyze_career(self, user_input: str):
            return {"error": "Milo AI not available", "message": "Backend is running but AI service is unavailable"}
    milo = DummyMilo()

class CareerRequest(BaseModel):
    user_input: str

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatHistoryResponse(BaseModel):
    messages: List[dict]
    session_info: dict

class SessionInfoResponse(BaseModel):
    session_id: str
    current_step: int
    student_interests: List[str]
    career_paths: List[str]
    message_count: int
    created_at: str
    last_updated: str

@app.get("/")
async def read_index():
    return {"message": "Milo AI Backend is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "milo-ai-backend", 
        "milo_available": hasattr(milo, 'client'),
        "streaming_chat_available": hasattr(milo, 'stream_chat_response'),
        "features": ["career_analysis", "streaming_chat", "session_management"]
    }

@app.post("/analyze")
async def analyze_career(request: CareerRequest):
    """Analyze career goals and provide actionable plan"""
    result = await milo.analyze_career(request.user_input)
    return result

# ===== NEW STREAMING CHAT ENDPOINTS =====

@app.post("/chat/stream")
async def stream_chat(chat_message: ChatMessage):
    """Stream chat response using the new 6-step conversation flow"""
    try:
        async def generate_response():
            try:
                async for chunk in milo.stream_chat_response(
                    chat_message.message, 
                    chat_message.session_id
                ):
                    # Format as Server-Sent Events
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                error_msg = f"Error in chat stream: {str(e)}"
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str = "default"):
    """Get chat history for a session"""
    try:
        messages = await milo.get_chat_history(session_id)
        session_info = milo.get_session_info(session_id)
        
        return ChatHistoryResponse(
            messages=messages,
            session_info=session_info
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error getting chat history: {str(e)}")

@app.get("/chat/session/{session_id}")
async def get_session_info(session_id: str = "default"):
    """Get session information"""
    try:
        session_info = milo.get_session_info(session_id)
        return SessionInfoResponse(**session_info)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error getting session info: {str(e)}")

@app.delete("/chat/session/{session_id}")
async def clear_session(session_id: str = "default"):
    """Clear a conversation session"""
    try:
        milo.clear_session(session_id)
        return {"message": f"Session {session_id} cleared successfully"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")

@app.get("/chat/sessions")
async def list_sessions():
    """List all active sessions"""
    try:
        sessions = {}
        for session_id in milo.conversation_sessions.keys():
            sessions[session_id] = milo.get_session_info(session_id)
        return {"sessions": sessions}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

# Mount the API endpoints
try:
    from api.simple_api import simple_api
    app.mount("/api", simple_api)
    print("✅ Simple API endpoints mounted successfully")
except Exception as e:
    print(f"⚠️  Could not mount API endpoints: {e}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
