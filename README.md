# Nexus: Virtual Health Assistant

Nexus is an intelligent, AI-powered virtual assistant designed for healthcare providers. It provides patients with a conversational interface to get information, receive first-aid guidance, and book appointments, improving efficiency and patient engagement.

## Features

The Nexus agent has a variety of skills built on a safety-first principle:

* [cite_start]**Symptom Triage & First Aid:** Provides pre-approved first-aid instructions for minor injuries from a controlled knowledge base and directs users to seek immediate help for severe symptoms[cite: 75].
* [cite_start]**FAQ & Information Retrieval (RAG):** Answers questions about the clinic (e.g., hours, services, insurance) using a Retrieval-Augmented Generation pipeline to ensure factual, accurate responses[cite: 85].
* [cite_start]**Appointment Booking:** Guides users through the process of booking an appointment[cite: 94].
* **Conversational Memory:** Remembers the context of the conversation to handle follow-up questions and topic changes seamlessly.

## Tech Stack

The project is built with a modern, scalable tech stack:

* [cite_start]**Backend:** FastAPI (Python) [cite: 18]
* [cite_start]**Conversational AI Core:** LangGraph [cite: 27]
* [cite_start]**Database:** PostgreSQL with pgvector for vector search [cite: 33]
* [cite_start]**LLM Provider:** OpenAI [cite: 8, 43]
* [cite_start]**Environment:** Docker & VS Code Dev Containers [cite: 138, 241]

## Setup & Installation

[cite_start]The project uses VS Code Dev Containers to provide a one-click, consistent development environment[cite: 138, 241].

1.  **Prerequisites:** Install Docker Desktop, WSL 2 (with Ubuntu), and VS Code with the Dev Containers extension.
2.  **Clone the Repository:** Clone the project into your WSL 2 filesystem (not your Windows C: drive).
3.  **Launch:** Open the project folder in VS Code and click **"Reopen in Container"** when prompted.

## Running the Application

1.  Once inside the container, open a terminal.
2.  Navigate to the API directory: `cd nexus-api`
3.  Install dependencies: `pip install -r requirements.txt`
4.  Run the database seeder (one time): `python -m scripts.seed_db`
5.  Start the server: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
6.  Access the interactive API docs at `http://localhost:8000/docs`.