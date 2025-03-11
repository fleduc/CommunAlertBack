"""
Module: main.py
Description: This module initializes and configures the FastAPI application. It sets up logging,
CORS middleware, and includes the route modules for authentication, users, alerts, and messages.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import auth, users, alerts, messages

# Indicate that FastAPI is starting.
print("✅ FastAPI is starting")

# Configure logging to output to stdout.
logging.basicConfig(
    level=logging.INFO,  # Log level (INFO, DEBUG, etc.)
    format="%(levelname)s -> %(message)s"
)

logger = logging.getLogger(__name__)
logger.info("Starting FastAPI application")

# Initialize the FastAPI application.
app = FastAPI(title="CommunAlert API")

# Configure CORS middleware.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure static files serving
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include authentication routes.
print("✅ Importing AUTH routes")
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Include user routes.
print("✅ Importing USERS routes")
app.include_router(users.router, prefix="/api/users", tags=["users"])

# Include alert routes.
print("✅ Importing ALERTS routes")
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])

# Include message routes.
print("✅ Importing MESSAGES routes")
app.include_router(messages.router, prefix="/api/alerts/{alert_id}/messages", tags=["messages"])


@app.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": "Welcome to CommunAlert API"}
