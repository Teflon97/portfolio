from backend.server import app

# This entry point is required for Vercel deployment
# It exposes the Flask app instance to the Serverless environment

if __name__ == "__main__":
    app.run()
