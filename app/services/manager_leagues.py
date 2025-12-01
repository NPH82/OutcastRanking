from .sleeper_api import get_user_id, get_leagues, get_rosters
from .roster_utils import extract_roster_record, extract_team_name
from datetime import datetime

def get_manager_leagues_structured(username, season):
    """
    Get a manager's leagues organized in a structured format for display
    Returns leagues grouped by tables (50 per table), with columns (10 per column)
    """
    # Get user ID
    user_id = get_user_id(username)
    if not user_id:
        return None
    
    # Get all leagues for this user
    leagues = get_leagues(user_id, season)
    if not leagues:
        return None
    
    # Process leagues to get additional info
    processed_leagues = []
    display_name = username  # Default fallback
    
    for league in leagues:
        # Check for None league entries
        if not league:
            continue
            
        league_id = league.get("league_id")
        if not league_id:
            continue
            
        try:
            # Get basic league info
            league_name = league.get("name", f"League {league_id}")
            total_teams = league.get("total_rosters", 0)
            
            # Try to get user's team name and record from rosters
            rosters = get_rosters(league_id)
            user_wins = 0
            user_losses = 0
            user_team_name = username
            
            if rosters:
                for roster in rosters:
                    if roster.get("owner_id") == user_id:
                        # Use utility functions for roster data extraction
                        user_wins, user_losses, ties = extract_roster_record(roster)
                        user_team_name = extract_team_name(roster, username)
                        
                        if user_team_name and user_team_name != username:
                            if display_name == username:  # Use first good team name as display name
                                display_name = user_team_name
                        break
            
            # Calculate win percentage
            total_games = user_wins + user_losses
            win_percentage = (user_wins / total_games) if total_games > 0 else 0
            
            processed_leagues.append({
                "league_id": league_id,
                "league_name": league_name,
                "total_teams": total_teams,
                "user_wins": user_wins,
                "user_losses": user_losses,
                "user_team_name": user_team_name,
                "win_percentage": win_percentage,
                "total_games": total_games
            })
            
        except Exception as e:
            print(f"Error processing league {league_id}: {e}")
            # Add basic info even if detailed processing fails
            # Only if we have a valid league object
            if league:
                processed_leagues.append({
                    "league_id": league_id,
                    "league_name": league.get("name", f"League {league_id}"),
                    "total_teams": league.get("total_rosters", 0),
                    "user_wins": 0,
                    "user_losses": 0,
                    "user_team_name": username,
                    "win_percentage": 0,
                    "total_games": 0
                })
            else:
                # If league is None, add minimal info
                processed_leagues.append({
                    "league_id": league_id or "unknown",
                    "league_name": f"League {league_id or 'unknown'}",
                    "total_teams": 0,
                    "user_wins": 0,
                    "user_losses": 0,
                    "user_team_name": username,
                    "win_percentage": 0,
                    "total_games": 0
                })
    
    # Structure leagues into tables and columns
    structured_data = {
        "username": username,
        "display_name": display_name,
        "user_id": user_id,
        "season": season,
        "total_leagues": len(processed_leagues),
        "tables": []
    }
    
    # Group leagues into tables of 50
    leagues_per_table = 50
    for table_start in range(0, len(processed_leagues), leagues_per_table):
        table_leagues = processed_leagues[table_start:table_start + leagues_per_table]
        
        # Group table leagues into columns of 10
        leagues_per_column = 10
        columns = []
        for col_start in range(0, len(table_leagues), leagues_per_column):
            column_leagues = table_leagues[col_start:col_start + leagues_per_column]
            columns.append(column_leagues)
        
        table_data = {
            "table_number": len(structured_data["tables"]) + 1,
            "league_count": len(table_leagues),
            "columns": columns
        }
        structured_data["tables"].append(table_data)
    
    return structured_data

def get_manager_summary_stats(username, season):
    """Get summary statistics for a manager across all leagues"""
    data = get_manager_leagues_structured(username, season)
    if not data:
        return None
    
    total_wins = 0
    total_losses = 0
    active_leagues = 0
    
    for table in data["tables"]:
        for column in table["columns"]:
            for league in column:
                total_wins += league["user_wins"]
                total_losses += league["user_losses"]
                if league["total_games"] > 0:
                    active_leagues += 1
    
    total_games = total_wins + total_losses
    overall_win_percentage = (total_wins / total_games) if total_games > 0 else 0
    
    return {
        "display_name": data["display_name"],
        "total_leagues": data["total_leagues"],
        "active_leagues": active_leagues,
        "total_wins": total_wins,
        "total_losses": total_losses,
        "total_games": total_games,
        "overall_win_percentage": overall_win_percentage
    }