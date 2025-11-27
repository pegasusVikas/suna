#!/bin/bash
# Debug script for Dramatiq worker
# Runs with a single process and thread for easier debugging

echo "🐛 Starting Dramatiq in DEBUG mode..."
echo "🐛 Debugger will listen on port 5678"
echo "🐛 Use VS Code 'Attach to Dramatiq Worker' configuration to attach"
echo ""

export DEBUG_DRAMATIQ=true
export DRAMATIQ_PROCESS_INDEX=0

# Run with single process and thread for easier debugging
uv run dramatiq --verbose --processes 1 --threads 1 run_agent_background
