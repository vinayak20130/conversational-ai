"""
FastAPI router for chat endpoints.
"""
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from models.llm_factory import LLMFactory
from services.conversation import ConversationService
from config import ModelProvider, AVAILABLE_MODELS

router = APIRouter()

# Dictionary to store conversation services by session ID
conversation_services: Dict[str, ConversationService] = {}

class MessageRequest(BaseModel):
    """Request model for chat messages."""
    session_id: str
    message: str

class ModelConfigRequest(BaseModel):
    """Request model for configuring the model."""
    session_id: str
    provider: str
    model_name: str
    api_key: str

class MessageResponse(BaseModel):
    """Response model for chat messages."""
    session_id: str
    response: str

class ModelsResponse(BaseModel):
    """Response model for available models."""
    providers: List[str]
    models: Dict[str, List[str]]

@router.get("/models", response_model=ModelsResponse)
async def get_available_models():
    """
    Get available model providers and models.
    
    Returns:
        Dictionary with providers and models
    """
    return {
        "providers": [provider.value for provider in ModelProvider],
        "models": {provider.value: models for provider, models in AVAILABLE_MODELS.items()}
    }

@router.post("/configure", response_model=Dict)
async def configure_model(config: ModelConfigRequest):
    """
    Configure the model for a session.
    
    Args:
        config: Model configuration request
        
    Returns:
        Status message
    """
    try:
        # Create LLM based on the configuration
        llm = LLMFactory.create_from_params(
            provider=config.provider,
            model_name=config.model_name,
            api_key=config.api_key
        )
        
        # Create or update the conversation service
        conversation_services[config.session_id] = ConversationService(llm=llm)
        
        return {"status": "success", "message": f"Configured {config.provider} model: {config.model_name}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error configuring model: {str(e)}")

def get_conversation_service(session_id: str) -> ConversationService:
    """
    Get the conversation service for a session.
    
    Args:
        session_id: Session ID
        
    Returns:
        Conversation service
        
    Raises:
        HTTPException: If the session is not configured
    """
    if session_id not in conversation_services:
        raise HTTPException(
            status_code=400, 
            detail="Session not configured. Please configure a model first."
        )
    
    return conversation_services[session_id]

@router.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    """
    Generate a response to a chat message.
    
    Args:
        request: Message request
        
    Returns:
        Response message
    """
    conversation = get_conversation_service(request.session_id)
    
    # Add the user message to the conversation
    conversation.add_user_message(request.message)
    
    # Generate a response
    response = await conversation.generate_response()
    
    return {"session_id": request.session_id, "response": response}

@router.post("/chat/stream")
async def chat_stream(request: MessageRequest):
    """
    Generate a streaming response to a chat message.
    
    Args:
        request: Message request
        
    Returns:
        Streaming response
    """
    conversation = get_conversation_service(request.session_id)
    
    # Add the user message to the conversation
    conversation.add_user_message(request.message)
    
    # Create a streaming response
    async def stream_generator():
        async for chunk in conversation.generate_response_stream():
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream"
    )

@router.post("/reset", response_model=Dict)
async def reset_conversation(request: MessageRequest):
    """
    Reset a conversation.
    
    Args:
        request: Message request with session ID
        
    Returns:
        Status message
    """
    conversation = get_conversation_service(request.session_id)
    conversation.reset_conversation()
    
    return {"status": "success", "message": "Conversation reset"}