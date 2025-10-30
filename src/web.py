
from flask import Flask

app = Flask(__name__)

@app.get("/")
def root():
    return "Calendar digest is running ✅", 200

def run():
    import os
    port = int(os.environ.get("PORT", 10000))  # Render נותן PORT
    # 0.0.0.0 כדי ש-Render יראה שהפורט פתוח
    app.run(host="0.0.0.0", port=port)
