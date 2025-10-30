
# ----------------------------------------------------------
# Minimal Flask web server used for health checks.
# Render (or any hosting platform) requires an open port to 
# verify that the service is running, so this module provides 
# a simple HTTP endpoint ("/") returning a status message.
# ----------------------------------------------------------

from flask import Flask

# Create a minimal Flask application instance
app = Flask(__name__)

@app.get("/")
def root():
    """
    Health-check endpoint.
    Returns a simple OK message and HTTP 200 status.
    """
    return "Calendar digest is running ✅", 200

def run():
    """
    Start the Flask server.
    Render automatically sets a PORT environment variable, 
    which must be used to bind the process to the correct port.
    Host is set to 0.0.0.0 so the container accepts external traffic.
    """
    import os
    port = int(os.environ.get("PORT", 10000))  # Render provides PORT env var
    app.run(host="0.0.0.0", port=port)
