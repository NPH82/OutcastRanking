from app import create_app
from flask import request

app = create_app()

@app.before_request
def log_all_requests():
    print(f"[APP LEVEL] Request: {request.method} {request.path}")
    print(f"[APP LEVEL] Args: {dict(request.args)}")
    print(f"[APP LEVEL] Form: {dict(request.form)}")

if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=True, port=5001)  # Use different port
