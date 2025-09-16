#!/usr/bin/env python3
"""
Test script for the new streaming chat functionality
"""
import asyncio
import json
from milo_ai import MiloAI

async def test_streaming_chat():
    """Test the streaming chat functionality"""
    print("🚀 Testing Milo Streaming Chat...")
    
    # Initialize MiloAI
    milo = MiloAI()
    
    # Test messages
    test_messages = [
        "Hi, I'm a Yale student interested in data science and global issues.",
        "I love working with data and want to make an impact on climate change.",
        "What specific courses should I take this semester?"
    ]
    
    session_id = "test_session"
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*50}")
        print(f"TEST MESSAGE {i}: {message}")
        print(f"{'='*50}")
        
        # Stream the response
        print("MILO RESPONSE:")
        print("-" * 30)
        
        full_response = ""
        async for chunk in milo.stream_chat_response(message, session_id):
            print(chunk, end="", flush=True)
            full_response += chunk
        
        print("\n" + "-" * 30)
        
        # Get session info
        session_info = milo.get_session_info(session_id)
        print(f"\nSESSION INFO:")
        print(f"- Current Step: {session_info['current_step']}")
        print(f"- Student Interests: {session_info['student_interests']}")
        print(f"- Message Count: {session_info['message_count']}")
        
        # Small delay between messages
        await asyncio.sleep(1)
    
    # Test getting chat history
    print(f"\n{'='*50}")
    print("CHAT HISTORY:")
    print(f"{'='*50}")
    
    history = await milo.get_chat_history(session_id)
    for msg in history:
        role = "STUDENT" if msg['role'] == 'user' else "MILO"
        print(f"\n{role}: {msg['content'][:100]}...")
        print(f"Time: {msg['timestamp']}")

async def test_session_management():
    """Test session management functionality"""
    print("\n🔧 Testing Session Management...")
    
    milo = MiloAI()
    
    # Create multiple sessions
    session1 = milo.get_or_create_session("session1")
    session2 = milo.get_or_create_session("session2")
    
    print(f"Created session1: {session1['current_step']}")
    print(f"Created session2: {session2['current_step']}")
    
    # Test session updates
    milo.update_session("session1", current_step=3, student_interests=["data science"])
    
    updated_info = milo.get_session_info("session1")
    print(f"Updated session1: {updated_info}")
    
    # Test session clearing
    milo.clear_session("session2")
    print("Cleared session2")
    
    # List all sessions
    print(f"Active sessions: {list(milo.conversation_sessions.keys())}")

if __name__ == "__main__":
    print("🧪 Starting Milo Streaming Chat Tests...")
    
    try:
        # Run the streaming chat test
        asyncio.run(test_streaming_chat())
        
        # Run the session management test
        asyncio.run(test_session_management())
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
