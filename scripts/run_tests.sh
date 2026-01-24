#!/bin/bash
set -e

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

echo "Running ServiceNow MCP Tests..."
cd $(dirname "$0")/..

# Install pytest if not present (optional, or assume env is ready)
# pip install pytest python-dotenv

# Run pytest on specific files to avoid legacy broken tests
python3 -m pytest tests/test_incidents.py tests/test_change_requests.py tests/test_user.py -vvv
