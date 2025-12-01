#!/usr/bin/env python3
"""
Test script to debug rivalry calculation
"""
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path[:3]}")

try:
    from app.services.manager_leagues import get_manager_leagues_structured
    from app.services.roster_utils import calculate_manager_rivalries_fast
    print("Successfully imported modules")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def test_rivalry_calculation():
    """Test rivalry calculation with a sample manager"""
    
    # Test multiple usernames in case one doesn't exist
    test_usernames = ["test", "nick", "admin", "user"]  # Using usernames we know exist
    season = "2025"  # Back to current season
    
    for username in test_usernames:
        print(f"Testing rivalry calculation for: {username}")
        print(f"Season: {season}")
        print("-" * 50)
        
        try:
            # Get manager data
            print("Getting manager leagues data...")
            manager_data = get_manager_leagues_structured(username, season)
            
            if not manager_data:
                print(f"No manager data found for {username}")
                print("Trying next username...\n")
                continue
            
            print(f"Manager found: {manager_data.get('display_name', 'Unknown')}")
            print(f"User ID: {manager_data.get('user_id', 'Unknown')}")
            print(f"Total leagues: {manager_data.get('total_leagues', 0)}")
            
            # Test fast rivalry calculation
            print("\nTesting fast rivalry calculation...")
            rivalries = calculate_manager_rivalries_fast(manager_data, season)
            
            print(f"Rivalry calculation result: {rivalries}")
            
            if rivalries["most_wins_against"]:
                print(f"Most wins against: {rivalries['most_wins_against']['opponent_name']} " +
                      f"({rivalries['most_wins_against']['wins']}W-{rivalries['most_wins_against']['losses']}L)")
            else:
                print("No 'most wins against' rivalry found")
                
            if rivalries["most_losses_to"]:
                print(f"Most losses to: {rivalries['most_losses_to']['opponent_name']} " +
                      f"({rivalries['most_losses_to']['wins']}W-{rivalries['most_losses_to']['losses']}L)")
            else:
                print("No 'most losses to' rivalry found")
            
            # Found a working username, stop testing
            break
            
        except Exception as e:
            print(f"Error with {username}: {e}")
            print("Trying next username...\n")
            continue
    
    print("Finished testing all usernames.")

if __name__ == "__main__":
    test_rivalry_calculation()