#!/bin/bash
# This script scaffolds the Nexus project directory structure.

echo "Creating top-level directories..."
mkdir -p .devcontainer .github/workflows nexus-api nexus-web

echo "Creating backend directory structure for /nexus-api..."
mkdir -p nexus-api/alembic nexus-api/app nexus-api/tests
mkdir -p nexus-api/app/api/v1/endpoints
mkdir -p nexus-api/app/core
mkdir -p nexus-api/app/db
mkdir -p nexus-api/app/models
mkdir -p nexus-api/app/schemas
mkdir -p nexus-api/app/services

echo "Creating placeholder files and Python packages..."
# Top-level files
touch .devcontainer/devcontainer.json
touch .devcontainer/Dockerfile
touch .github/workflows/ci.yml
touch nexus-web/.gitkeep
touch README.md

# Backend files
touch nexus-api/app/__init__.py
touch nexus-api/app/main.py
touch nexus-api/app/config.py

# API structure
touch nexus-api/app/api/__init__.py
touch nexus-api/app/api/v1/__init__.py
touch nexus-api/app/api/v1/endpoints/__init__.py
touch nexus-api/app/api/v1/endpoints/chat.py
touch nexus-api/app/api/v1/endpoints/appointments.py

# Core structure
touch nexus-api/app/core/__init__.py
touch nexus-api/app/core/security.py
touch nexus-api/app/core/dependencies.py

# DB structure
touch nexus-api/app/db/__init__.py

# Models and Schemas
touch nexus-api/app/models/__init__.py
touch nexus-api/app/schemas/__init__.py

# Services (Agent Logic)
touch nexus-api/app/services/__init__.py
touch nexus-api/app/services/nexus_agent.py

# Tests
touch nexus-api/tests/__init__.py

echo "Scaffolding complete. Project structure created successfully."