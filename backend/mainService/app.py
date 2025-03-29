import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.startup import startup_event
from src.controllers.citation_controller import router as citation_router
from src.controllers.health_controller import router as health_router

# Detect if running in Azure Functions (serverless)
IS_SERVERLESS = os.getenv("SERVERLESS").lower() == "true"  

origins = [
    "http://localhost:5173",  # Frontend running on localhost (React, Vue, etc.)
    "https://cite-me.vercel.app"
]

# Conditionally assign lifespan
lifespan = startup_event if not IS_SERVERLESS else None

# Create FastAPI instance
app = FastAPI(title="Citation API", version="1.0.0", lifespan=lifespan)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,  
    allow_methods=["POST", "GET", "OPTIONS", "HEAD"],  
    allow_headers=["*"],  
)

# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(citation_router, prefix="/citation", tags=["Citation"])

