from linkedin_api import Linkedin
import json
from src.app import run_app
import os
import sys

CLIENT_ID = os.getenv("LINKEDIN_USER")
CLIENT_SECRET = os.getenv("LINKEDIN_SECRET")

if not CLIENT_ID or not CLIENT_ID:
    raise RuntimeError(f"Missing required environment variables. Ensure you have LINKEDIN_USER and LINKEDIN_SECRET. ")

# Authenticate using any Linkedin user account credentials
api = Linkedin(CLIENT_ID, CLIENT_SECRET)

app = run_app(api)

if __name__ == '__main__':
    app.run(debug=True)