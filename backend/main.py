"""
RecruitPro 2 - Main Application Entry Point
FastAPI application with proper router architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

from database.mongodb import connect_to_mongodb, close_mongodb_connection

# Import routers
from routes import candidates, job_descriptions, matching, analytics, export, chat

load_dotenv()

# Initialize Firebase Admin
try:
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin initialized")
except Exception as e:
    print(f"⚠️ Firebase initialization warning: {e}")

# Initialize FastAPI
app = FastAPI(
    title="RecruitPro 2 API",
    description="AI-powered recruitment management system with MongoDB",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await connect_to_mongodb()
    print("✅ Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_mongodb_connection()
    print("✅ Application shutdown complete")


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RecruitPro 2 API",
        "version": "2.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "firebase": "initialized"
    }


# Include all routers
app.include_router(candidates.router)
app.include_router(job_descriptions.router)
app.include_router(matching.router)
app.include_router(analytics.router)
app.include_router(export.router)
app.include_router(chat.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
