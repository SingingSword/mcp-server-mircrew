#!/bin/bash
# Script to run integration tests for MirCrew MCP Server
#
# Usage:
#   export MIRCREW_USERNAME='your_username'
#   export MIRCREW_PASSWORD='your_password'
#   ./run_integration_tests.sh

set -e

echo "MirCrew MCP Server - Integration Test Runner"
echo "=============================================="
echo ""

# Check if credentials are set
if [ -z "$MIRCREW_USERNAME" ] || [ -z "$MIRCREW_PASSWORD" ]; then
    echo "❌ Error: Credentials not set"
    echo ""
    echo "Please set the following environment variables:"
    echo "  export MIRCREW_USERNAME='your_username'"
    echo "  export MIRCREW_PASSWORD='your_password'"
    echo ""
    exit 1
fi

echo "✓ Credentials found"
echo "  Username: $MIRCREW_USERNAME"
echo ""

# Activate virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo "❌ Error: Virtual environment not found"
        echo "Please create it with: python -m venv venv"
        exit 1
    fi
fi

# Run the integration tests
echo "Running integration tests..."
echo ""
PYTHONPATH=. python tests/test_integration.py
