from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router, redirect
from app.core.database import engine, Base
from app.core.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="API service for shortening URLs with analytics",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(redirect.router)
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "URL Shortener API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)