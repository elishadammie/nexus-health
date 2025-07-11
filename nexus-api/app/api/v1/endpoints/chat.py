from fastapi import APIRouter
from app.schemas.chat import ChatMessage, AgentResponse
from app.services import nexus_agent

router = APIRouter()

@router.post("/", response_model=AgentResponse)
def handle_chat(chat_message: ChatMessage):
    """
    Receives a user message, runs it through the agent, 
    and returns the final response.
    """
    final_state = nexus_agent.run_agent(chat_message.message)
    
    # We now return the 'final_response' field from the agent's state
    return AgentResponse(response_message=final_state.get('final_response', 'An error occurred.'))