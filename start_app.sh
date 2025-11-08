#!/bin/bash

#############################################
# Contractor Pay Tracker - App Launcher
# Activates virtual environment and starts Flask app
#############################################

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Contractor Pay Tracker${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv "$SCRIPT_DIR/venv"

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Virtual environment created${NC}"

    # Activate and install dependencies
    source "$SCRIPT_DIR/venv/bin/activate"

    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    pip install -q --upgrade pip
    pip install -q -r "$SCRIPT_DIR/flask-app/requirements.txt"

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    # Activate existing virtual environment
    source "$SCRIPT_DIR/venv/bin/activate"
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
fi

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/flask-app/.env" ]; then
    if [ -f "$SCRIPT_DIR/flask-app/.env.example" ]; then
        echo -e "${YELLOW}⚠️  .env file not found. Creating from example...${NC}"
        cp "$SCRIPT_DIR/flask-app/.env.example" "$SCRIPT_DIR/flask-app/.env"
        echo -e "${GREEN}✅ Created .env file. Please update with your AWS credentials.${NC}"
    fi
fi

# Change to flask-app directory
cd "$SCRIPT_DIR/flask-app"

# Start the Flask app
echo -e "${BLUE}🚀 Starting Flask application...${NC}"
echo ""

python app.py

# Deactivate virtual environment on exit
deactivate
