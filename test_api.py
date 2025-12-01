#!/usr/bin/env python3
"""
Simple test to check Sleeper API connectivity
"""
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_api():
    try:
        from app.services.sleeper_api import get_user_id
        print("Testing Sleeper API connectivity...")
        
        # Test with a few different usernames
        test_usernames = ["test", "nick", "admin", "user"]
        
        for username in test_usernames:
            print(f"Testing username: {username}")
            user_id = get_user_id(username)
            print(f"Result: {user_id}")
            
            if user_id:
                print(f"Success! Found user_id: {user_id}")
                break
            else:
                print("No user_id returned")
            print("-" * 30)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()