from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from milo_ai import MiloAI
import uvicorn
import os
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

@app.get("/")
async def read_index():
    return {"message": "Milo AI Backend is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "milo-ai-backend", "milo_available": hasattr(milo, 'client')}

@app.post("/analyze")
async def analyze_career(request: CareerRequest):
    """Analyze career goals and provide actionable plan"""
    result = await milo.analyze_career(request.user_input)
    return result

# Mount the API endpoints
try:
    from api.simple_api import simple_api
    app.mount("/api", simple_api)
    print("✅ Simple API endpoints mounted successfully")
except Exception as e:
    print(f"⚠️  Could not mount API endpoints: {e}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
