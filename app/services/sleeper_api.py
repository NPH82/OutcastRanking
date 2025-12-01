# Sleeper API integration
import requests
import time
from functools import wraps
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.sleeper.app/v1"

# Create optimized session with connection pooling and retries
def create_optimized_session():
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    # Configure adapter with connection pooling
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# Global session for reuse
_session = create_optimized_session()

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    response = func(*args, **kwargs)
                    if response:
                        return response
                except requests.RequestException as e:
                    print(f"API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        raise
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=2, delay=0.5)
def get_user_id(username):
    try:
        res = _session.get(f"{BASE_URL}/user/{username}", timeout=5)
        res.raise_for_status()
        json_response = res.json()
        
        if json_response is None:
            print(f"API returned null response for username: {username}")
            return None
            
        if not isinstance(json_response, dict):
            print(f"API returned unexpected response type for {username}: {type(json_response)}")
            return None
            
        user_id = json_response.get("user_id")
        if not user_id:
            print(f"No user_id found in response for username: {username}")
            print(f"Response: {json_response}")
            
        return user_id
    except requests.RequestException as e:
        print(f"Error fetching user ID for {username}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching user ID for {username}: {e}")
        return None

@retry_on_failure(max_retries=2, delay=0.5)
def get_user_info(user_id):
    """Get user information by user ID"""
    try:
        res = _session.get(f"{BASE_URL}/user/{user_id}", timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"Error fetching user info for {user_id}: {e}")
        return None

@retry_on_failure(max_retries=2, delay=0.5)
def get_leagues(user_id, season):
    try:
        res = _session.get(f"{BASE_URL}/user/{user_id}/leagues/nfl/{season}", timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"Error fetching leagues for user {user_id}: {e}")
        return []

@retry_on_failure()
def get_matchups(league_id, week):
    try:
        res = _session.get(f"{BASE_URL}/league/{league_id}/matchups/{week}", timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"Error fetching matchups for league {league_id}, week {week}: {e}")
        return []

@retry_on_failure(max_retries=2, delay=0.5)
def get_rosters(league_id):
    try:
        res = _session.get(f"{BASE_URL}/league/{league_id}/rosters", timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"Error fetching rosters for league {league_id}: {e}")
        return []
