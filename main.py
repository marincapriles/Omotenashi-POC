from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import OPENAI_API_KEY
import openai

# Initialize FastAPI app
app = FastAPI(
    title="Omotenashi API",
    description="API for the Omotenashi POC project",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "status": "healthy",
        "message": "Welcome to Omotenashi API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_key_configured": bool(OPENAI_API_KEY)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 