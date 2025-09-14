from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from milo_ai import MiloAI
import uvicorn

app = FastAPI()

# Add CORS middleware
import os
allowed_origins = [
    "http://localhost:5173", 
    "http://localhost:3000", 
    "http://127.0.0.1:5173"
]

# Add production origins from environment variable
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Initialize Milo AI
milo = MiloAI()

class CareerRequest(BaseModel):
    user_input: str

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.post("/analyze")
async def analyze_career(request: CareerRequest):
    """Analyze career goals and provide actionable plan"""
    result = await milo.analyze_career(request.user_input)
    return result

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
