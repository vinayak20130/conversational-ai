"""
FastAPI application for the conversational AI system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import chat

# Create FastAPI application
app = FastAPI(
    title="Conversational AI MCP",
    description="Model Control Plane for Conversational AI",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Conversational AI MCP API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
