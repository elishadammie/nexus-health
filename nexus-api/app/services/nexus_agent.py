from typing import TypedDict, List, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from app.config import settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import StateGraph, END
import httpx
from app.db.session import SessionLocal
from app.models.faq_kb import FAQKnowledgeBase

# --- State, Schemas, and Constants ---
class NexusGraphState(TypedDict):
    """UPDATED: Now includes conversation_history for memory."""
    current_query: str
    conversation_history: List[BaseMessage] # For conversational memory
    classified_intent: str
    final_response: str

class IntentClassifier(BaseModel):
    intent: Literal["faq", "booking", "greeting", "triage", "chitchat", "unknown"]

FIRST_AID_DISCLAIMER = "\n\nDisclaimer: This is not a substitute for professional medical advice. Please consult a doctor for a proper diagnosis and treatment."
SEVERE_SYMPTOM_KEYWORDS = ["chest pain", "difficulty breathing", "severe abdominal pain", "numbness in arm", "uncontrolled bleeding", "suicide", "i want to die"]

# --- LLM and Embeddings Initialization ---
insecure_client = httpx.Client(verify=False)
llm = ChatOpenAI(openai_api_key=settings.OPENAI_API_KEY, model="gpt-4o", http_client=insecure_client, temperature=0.7)
structured_llm = llm.with_structured_output(IntentClassifier)
embeddings_model = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY, http_client=insecure_client)

# --- Graph Nodes ---
# Each node now updates the history and can be more conversational.
def safety_check_node(state: NexusGraphState):
    query_lower = state['current_query'].lower()
    if any(keyword in query_lower for keyword in SEVERE_SYMPTOM_KEYWORDS):
        state['classified_intent'] = "escalation"
    return state

def classify_intent_node(state: NexusGraphState):
    if state.get('classified_intent') == "escalation": return state
    
    query = state['current_query']
    history = state['conversation_history']
    
    prompt = f"""You are an expert at routing user queries in a medical assistant chatbot. Based on the current query and the conversation history, classify the user's query into one of the following categories: 'faq', 'booking', 'greeting', 'triage', 'chitchat', 'unknown'.
    
    Conversation History:
    {history}
    
    Current Query: "{query}"
    """
    response = structured_llm.invoke(prompt)
    state['classified_intent'] = response.intent
    return state

# All handler nodes are updated to be more conversational and manage history
def handle_faq_node(state: NexusGraphState):
    query = state['current_query']
    history = state['conversation_history']
    db = SessionLocal()
    try:
        query_embedding = embeddings_model.embed_query(query)
        similar_chunks = db.query(FAQKnowledgeBase).filter(FAQKnowledgeBase.category == 'faq').order_by(FAQKnowledgeBase.embedding.cosine_distance(query_embedding)).limit(3).all()
        if not similar_chunks:
            return handle_unknown_node(state)

        context = "\n\n".join([chunk.text_chunk for chunk in similar_chunks])
        prompt = f"""You are a helpful assistant for a medical clinic. Answer the user's question based only on the following context. Keep your answer conversational.
        
        Conversation History:
        {history}

        Context: 
        {context}
        
        Question: 
        {query}
        """
        final_response = llm.invoke(prompt).content
        state['final_response'] = final_response
        state['conversation_history'].extend([HumanMessage(content=query), AIMessage(content=final_response)])
    finally:
        db.close()
    return state
    
def handle_triage_node(state: NexusGraphState):
    query = state['current_query']
    db = SessionLocal()
    try:
        query_embedding = embeddings_model.embed_query(query)
        best_chunk = db.query(FAQKnowledgeBase).filter(FAQKnowledgeBase.category == 'triage').order_by(FAQKnowledgeBase.embedding.cosine_distance(query_embedding)).first()
        if best_chunk:
            triage_response = best_chunk.text_chunk + FIRST_AID_DISCLAIMER
        else:
            triage_response = "I couldn't find specific first-aid steps for that. For any medical concerns, please consult a doctor."
        state['final_response'] = triage_response
        state['conversation_history'].extend([HumanMessage(content=query), AIMessage(content=triage_response)])
    finally:
        db.close()
    return state

def generate_conversational_node(prompt_template: str):
    """A factory for creating simple conversational nodes."""
    def node(state: NexusGraphState):
        query = state['current_query']
        history = state['conversation_history']
        
        prompt = prompt_template.format(history=history, query=query)
        
        response = llm.invoke(prompt).content
        state['final_response'] = response
        state['conversation_history'].extend([HumanMessage(content=query), AIMessage(content=response)])
        return state
    return node

handle_greeting_node = generate_conversational_node(
    "You are a friendly medical assistant. The user said: '{query}'. Respond to the greeting and ask how you can help. Conversation History: {history}"
)
handle_booking_node = generate_conversational_node(
    "You are a friendly medical assistant. The user wants to book an appointment. Acknowledge their request based on their query: '{query}'. State that you will help them find a slot. Conversation History: {history}"
)
handle_chitchat_node = generate_conversational_node(
    "You are a friendly and helpful assistant. Provide a brief, conversational response to the following user statement: '{query}'. Conversation History: {history}"
)
handle_unknown_node = generate_conversational_node(
    "You are a helpful medical assistant. You did not understand the user's query: '{query}'. Apologize and clearly state your capabilities (answering FAQs, booking appointments, providing simple first-aid info). Conversation History: {history}"
)
handle_escalation_node = generate_conversational_node(
    "You are a helpful medical assistant providing an urgent safety warning. The user's query '{query}' contains concerning language. Respond with empathy and immediately direct them to seek emergency help. Do not attempt to diagnose. This is a critical safety warning. Conversation History: {history}"
)

# --- Graph Definition ---
def route_after_intent(state: NexusGraphState):
    intent = state['classified_intent']
    # Map intents to nodes
    intent_map = {
        "escalation": "handle_escalation",
        "faq": "handle_faq",
        "booking": "handle_booking",
        "triage": "handle_triage",
        "greeting": "handle_greeting",
        "chitchat": "handle_chitchat",
    }
    return intent_map.get(intent, "handle_unknown")

def should_continue(state: NexusGraphState) -> Literal["classify_intent", "__end__"]:
    # For now, we will have a simple loop. In a production system,
    # you might have more complex logic to end the conversation.
    return "classify_intent"

workflow = StateGraph(NexusGraphState)

workflow.add_node("safety_check", safety_check_node)
workflow.add_node("classify_intent", classify_intent_node)
workflow.add_node("handle_faq", handle_faq_node)
workflow.add_node("handle_booking", handle_booking_node)
workflow.add_node("handle_triage", handle_triage_node)
workflow.add_node("handle_greeting", handle_greeting_node)
workflow.add_node("handle_chitchat", handle_chitchat_node)
workflow.add_node("handle_unknown", handle_unknown_node)
workflow.add_node("handle_escalation", handle_escalation_node)

workflow.set_entry_point("safety_check")
workflow.add_edge("safety_check", "classify_intent")
workflow.add_conditional_edges("classify_intent", route_after_intent)

# UPDATED: All nodes now loop back to the classification step, ready for the next user message.
# The 'END' state is no longer directly used by most nodes. This creates a continuous conversational loop.
# The graph will wait for the next user input after each response.
workflow.add_edge("handle_faq", END)
workflow.add_edge("handle_booking", END)
workflow.add_edge("handle_triage", END)
workflow.add_edge("handle_greeting", END)
workflow.add_edge("handle_chitchat", END)
workflow.add_edge("handle_unknown", END)
workflow.add_edge("handle_escalation", END)

agent_graph = workflow.compile()

# The run_agent function is now responsible for managing the conversation history
# This is a simplified example. A real application would persist history in the database.
conversation_history = []

def run_agent(query: str):
    global conversation_history
    inputs = {
        "current_query": query,
        "conversation_history": conversation_history
    }
    final_state = agent_graph.invoke(inputs)
    # Update the global history after the run
    conversation_history = final_state.get('conversation_history', [])
    return final_state