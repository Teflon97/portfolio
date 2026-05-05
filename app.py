import os
import sys

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app from backend/server.py
from backend.server import app

# This is required for Vercel to detect the Flask app
if __name__ == "__main__":
    app.run()