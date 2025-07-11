from fastapi import FastAPI
from app.api.v1.endpoints import chat as chat_router
from app.api.v1.endpoints import appointments as appointments_router # Import the new router

app = FastAPI(
    title="Nexus Virtual Health Assistant API",
    version="1.0.0",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Nexus API"}

# Include the chat router
app.include_router(chat_router.router, prefix="/api/v1/chat", tags=["Chat"])

# Include the appointments router
app.include_router(appointments_router.router, prefix="/api/v1/appointments", tags=["Appointments"])