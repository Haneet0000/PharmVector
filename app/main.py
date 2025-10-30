from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, documents
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="PharmVector API",
    description="Document search API with pgvector and semantic search",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.get("/")
async def root():
    return {
        "message": "PharmVector API",
        "version": "1.0.0",
        "docs": "/docs"
    }
