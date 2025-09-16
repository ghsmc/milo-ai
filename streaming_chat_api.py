from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import asyncio
from milo_ai import MiloAI

app = FastAPI(title="Milo Streaming Chat API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MiloAI
milo_ai = MiloAI()

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
async def root():
    return {"message": "Milo Streaming Chat API", "version": "1.0.0"}

@app.post("/chat/stream")
async def stream_chat(chat_message: ChatMessage):
    """Stream chat response using the new 6-step conversation flow"""
    try:
        async def generate_response():
            try:
                async for chunk in milo_ai.stream_chat_response(
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
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str = "default"):
    """Get chat history for a session"""
    try:
        messages = await milo_ai.get_chat_history(session_id)
        session_info = milo_ai.get_session_info(session_id)
        
        return ChatHistoryResponse(
            messages=messages,
            session_info=session_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chat history: {str(e)}")

@app.get("/chat/session/{session_id}")
async def get_session_info(session_id: str = "default"):
    """Get session information"""
    try:
        session_info = milo_ai.get_session_info(session_id)
        return SessionInfoResponse(**session_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session info: {str(e)}")

@app.delete("/chat/session/{session_id}")
async def clear_session(session_id: str = "default"):
    """Clear a conversation session"""
    try:
        milo_ai.clear_session(session_id)
        return {"message": f"Session {session_id} cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")

@app.get("/chat/sessions")
async def list_sessions():
    """List all active sessions"""
    try:
        sessions = {}
        for session_id in milo_ai.conversation_sessions.keys():
            sessions[session_id] = milo_ai.get_session_info(session_id)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Milo Streaming Chat API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
