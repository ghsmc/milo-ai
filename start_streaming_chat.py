#!/usr/bin/env python3
"""
Startup script for the Milo Streaming Chat API
"""
import uvicorn
import os
from dotenv import load_dotenv

def main():
    """Start the streaming chat API server"""
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key in a .env file or environment variable")
        return
    
    print("🚀 Starting Milo Streaming Chat API...")
    print("📡 API will be available at: http://localhost:8000")
    print("🧪 Test interface available at: test_chat_interface.html")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "streaming_chat_api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enable auto-reload for development
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
