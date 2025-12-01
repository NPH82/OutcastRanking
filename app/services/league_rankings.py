from .sleeper_api import get_rosters
from .roster_utils import extract_roster_stats, extract_roster_record
from datetime import datetime

def get_league_leaderboard(league_id, season):
    """
    Get leaderboard for all managers in a specific league
    Returns ranked list of managers with their records and win percentages
    """
    try:
        # Get all rosters in the league
        rosters = get_rosters(league_id)
        if not rosters:
            return None
        
        # Process each roster to get manager data
        managers = []
        for roster in rosters:
            owner_id = roster.get("owner_id")
            if not owner_id:
                continue
            
            # Use utility function to extract all roster stats
            stats = extract_roster_stats(roster, f"Team {roster.get('roster_id', 'Unknown')}")
            
            managers.append({
                "owner_id": owner_id,
                "roster_id": stats['roster_id'],
                "team_name": stats['team_name'],
                "wins": stats['wins'],
                "losses": stats['losses'],
                "ties": stats['ties'],
                "total_games": stats['total_games'],
                "win_percentage": stats['win_percentage'],
                "points_for": stats['points_for'],
                "points_against": stats['points_against']
            })
        
        # Sort by win percentage (descending), then by points for as tiebreaker
        managers.sort(key=lambda x: (x["win_percentage"], x["points_for"]), reverse=True)
        
        # Add rank to each manager
        for i, manager in enumerate(managers, 1):
            manager["rank"] = i
        
        # Calculate league summary stats
        total_managers = len(managers)
        active_managers = len([m for m in managers if m["total_games"] > 0])
        avg_games = sum(m["total_games"] for m in managers) / total_managers if total_managers > 0 else 0
        
        return {
            "league_id": league_id,
            "season": season,
            "managers": managers,
            "summary": {
                "total_managers": total_managers,
                "active_managers": active_managers,
                "average_games_played": round(avg_games, 1)
            }
        }
        
    except Exception as e:
        print(f"Error getting league leaderboard for {league_id}: {e}")
        return None

def get_league_basic_info(league_id):
    """Get basic info about a league without full roster processing"""
    try:
        rosters = get_rosters(league_id)
        if not rosters:
            return None
        
        total_managers = len(rosters)
        active_managers = 0
        
        for roster in rosters:
            # Use utility function to extract wins/losses
            wins, losses, ties = extract_roster_record(roster)
            if wins > 0 or losses > 0:
                active_managers += 1
        
        return {
            "league_id": league_id,
            "total_managers": total_managers,
            "active_managers": active_managers
        }
        
    except Exception as e:
        print(f"Error getting basic league info for {league_id}: {e}")
        return None