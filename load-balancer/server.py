import os

from fastapi import FastAPI

app = FastAPI()
SERVER_ID = os.getenv("SERVER_ID", "unknown")

@app.get("/")
async def home():
    return {
        "message": "Hello from backend server!",
        "server_id": SERVER_ID,
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "server_id": SERVER_ID,
    }
