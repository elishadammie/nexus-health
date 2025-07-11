from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Schema for a user's incoming message."""

    message: str


class AgentResponse(BaseModel):
    """Schema for the agent's response."""

    response_message: str
