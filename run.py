from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Get configuration from environment variables
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    port = int(os.environ.get('PORT', 5001))
    
    print(f"Starting Flask app on port {port}...")
    if debug_mode:
        print("⚠️  WARNING: Debug mode is enabled. Do not use in production!")
    
    app.run(debug=debug_mode, port=port, host='127.0.0.1')
