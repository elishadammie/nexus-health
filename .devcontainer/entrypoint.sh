#!/bin/bash
set -e

echo "🔧 Entrypoint: initializing dev container..."

# Add any one-time setup here
# Example: run background services or setup scripts

echo "✅ Entrypoint complete. Handing over to: $@"

# Replace shell with passed command to ensure correct PID 1
exec "$@"

