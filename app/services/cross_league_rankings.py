"""
Cross-league rankings service for generating cumulative manager leaderboards
"""
from .sleeper_api import get_user_id, get_leagues, get_rosters, create_optimized_session
from .manager_leagues import get_manager_leagues_structured
import concurrent.futures
import logging
import requests

logger = logging.getLogger(__name__)

# Create session for API calls
session = create_optimized_session()

def get_user_info(user_id):
    """Get user information from Sleeper API"""
    try:
        response = session.get(f"https://api.sleeper.app/v1/user/{user_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Error fetching user info for {user_id}: {e}")
        return None

def get_league_info(league_id):
    """Get league information from Sleeper API"""
    try:
        response = session.get(f"https://api.sleeper.app/v1/league/{league_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Error fetching league info for {league_id}: {e}")
        return None

def get_league_managers(league_id, season="2025"):
    """Get all managers from a specific league"""
    try:
        # Get league rosters to find all users
        rosters = get_rosters(league_id)
        if not rosters:
            return []
        
        # Get league info for additional context
        league_info = get_league_info(league_id)
        
        # Extract unique user IDs
        user_ids = set()
        for roster in rosters:
            if roster and roster.get('owner_id'):
                user_ids.add(roster.get('owner_id'))
        
        # Get user details for each manager
        managers = []
        for user_id in user_ids:
            user_info = get_user_info(user_id)
            if user_info:
                managers.append({
                    'user_id': user_id,
                    'username': user_info.get('username', f'User_{user_id}'),
                    'display_name': user_info.get('display_name', user_info.get('username', f'User_{user_id}'))
                })
        
        return {
            'managers': managers,
            'league_info': league_info,
            'total_managers': len(managers)
        }
        
    except Exception as e:
        logger.error(f"Error getting managers for league {league_id}: {e}")
        return []

def get_manager_cumulative_stats(username, season="2025"):
    """Get cumulative stats for a manager across all their leagues"""
    try:
        print(f"DEBUG: Getting cumulative stats for {username}")
        
        # Use existing service to get structured league data
        manager_data = get_manager_leagues_structured(username, season)
        
        if not manager_data:
            print(f"DEBUG: No manager data returned for {username}")
            return None
            
        total_wins = 0
        total_losses = 0
        total_leagues = 0
        active_leagues = 0
        
        # Sum up stats from all leagues
        for table in manager_data.get("tables", []):
            for column in table.get("columns", []):
                for league in column:
                    try:
                        wins = league.get("user_wins", 0) or 0
                        losses = league.get("user_losses", 0) or 0
                        total_wins += wins
                        total_losses += losses
                        total_leagues += 1
                        if (wins + losses) > 0:
                            active_leagues += 1
                    except Exception as e:
                        print(f"DEBUG: Error processing league for {username}: {e}")
                        continue
        
        total_games = total_wins + total_losses
        win_percentage = (total_wins / total_games) if total_games > 0 else 0
        
        result = {
            'username': username,
            'display_name': manager_data.get('display_name', username),
            'total_wins': total_wins,
            'total_losses': total_losses,
            'total_games': total_games,
            'win_percentage': win_percentage,
            'total_leagues': total_leagues,
            'active_leagues': active_leagues,
            'leagues_detail': manager_data.get("tables", [])
        }
        
        print(f"DEBUG: Stats for {username}: {total_wins}-{total_losses}, {active_leagues} active leagues")
        return result
        
    except Exception as e:
        logger.error(f"Error getting cumulative stats for {username}: {e}")
        print(f"DEBUG: Exception in get_manager_cumulative_stats for {username}: {e}")
        return None

def generate_cross_league_leaderboard(league_id, season="2025"):
    """Generate a leaderboard of all managers in a league based on their cumulative performance across all leagues"""
    try:
        # Get all managers from the source league
        league_data = get_league_managers(league_id, season)
        if not league_data or not league_data.get('managers'):
            return None
        
        managers = league_data['managers']
        league_info = league_data.get('league_info', {})
        
        # Get cumulative stats for each manager using concurrent processing
        leaderboard_entries = []
        
        def process_manager(manager):
            username = manager['username']
            stats = get_manager_cumulative_stats(username, season)
            if stats:
                return stats
            return None
        
        # Process managers concurrently for better performance
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_manager = {
                executor.submit(process_manager, manager): manager 
                for manager in managers
            }
            
            for future in concurrent.futures.as_completed(future_to_manager):
                try:
                    result = future.result()
                    if result:
                        leaderboard_entries.append(result)
                except Exception as e:
                    manager = future_to_manager[future]
                    logger.error(f"Error processing manager {manager['username']}: {e}")
        
        # Sort by win percentage (descending), then by total wins (descending), then by total games (descending)
        leaderboard_entries.sort(key=lambda x: (x['win_percentage'], x['total_wins'], x['total_games']), reverse=True)
        
        # Add ranking positions
        for i, entry in enumerate(leaderboard_entries, 1):
            entry['rank'] = i
        
        return {
            'leaderboard': leaderboard_entries,
            'source_league': {
                'league_id': league_id,
                'league_name': league_info.get('name', f'League {league_id}'),
                'season': season,
                'total_managers': len(managers)
            },
            'stats': {
                'total_managers_processed': len(leaderboard_entries),
                'total_managers_found': len(managers),
                'season': season
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating cross-league leaderboard for league {league_id}: {e}")
        return None

def get_manager_league_details(username, season="2025"):
    """Get detailed breakdown of a manager's performance in each league"""
    try:
        manager_data = get_manager_leagues_structured(username, season)
        
        if not manager_data:
            return None
            
        leagues_detail = []
        
        # Extract individual league details
        for table in manager_data.get("tables", []):
            for column in table.get("columns", []):
                for league in column:
                    total_games = league.get('total_games', 0)
                    leagues_detail.append({
                        'league_id': league.get('league_id'),
                        'league_name': league.get('league_name'),
                        'wins': league.get('user_wins', 0),
                        'losses': league.get('user_losses', 0),
                        'total_games': total_games,
                        'win_percentage': league.get('win_percentage', 0),
                        'status': 'active' if total_games > 0 else 'inactive',
                        'is_active': total_games > 0
                    })
        
        return {
            'username': username,
            'display_name': manager_data.get('display_name', username),
            'leagues': leagues_detail,
            'season': season
        }
        
    except Exception as e:
        logger.error(f"Error getting league details for {username}: {e}")
        return None

def compare_multiple_managers(manager_usernames, season="2025"):
    """Compare multiple specific managers based on their cumulative performance across all leagues"""
    try:
        if not manager_usernames or len(manager_usernames) < 2:
            return None
            
        # Remove duplicates and empty strings, limit to 100 managers
        unique_managers = list(set([m.strip() for m in manager_usernames if m.strip()]))[:100]
        
        if len(unique_managers) < 2:
            return None
        
        # Get cumulative stats for each manager using concurrent processing
        comparison_data = []
        
        def process_manager_for_comparison(username):
            try:
                stats = get_manager_cumulative_stats(username, season)
                if stats:
                    # Add additional fields for comparison
                    stats['rank'] = 0  # Will be set after sorting
                    stats['comparison_id'] = username.lower()
                    return stats
                return None
            except Exception as e:
                logger.error(f"Error processing {username}: {e}")
                return None
        
        # Process managers concurrently for better performance
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_manager = {
                executor.submit(process_manager_for_comparison, username): username 
                for username in unique_managers
            }
            
            for future in concurrent.futures.as_completed(future_to_manager):
                try:
                    result = future.result()
                    if result:
                        comparison_data.append(result)
                except Exception as e:
                    username = future_to_manager[future]
                    logger.error(f"Error processing manager {username} for comparison: {e}")
        
        if not comparison_data:
            return None
            
        # Sort by win percentage (descending), then by total wins (descending), then by total games (descending)
        comparison_data.sort(key=lambda x: (x['win_percentage'], x['total_wins'], x['total_games']), reverse=True)
        
        # Add ranking positions
        for i, manager in enumerate(comparison_data, 1):
            manager['rank'] = i
        
        # Calculate comparison statistics
        total_wins = sum(m['total_wins'] for m in comparison_data)
        total_games = sum(m['total_games'] for m in comparison_data)
        avg_win_percentage = sum(m['win_percentage'] for m in comparison_data) / len(comparison_data)
        
        result = {
            'managers': comparison_data,
            'stats': {
                'total_managers': len(comparison_data),
                'managers_requested': len(unique_managers),
                'managers_found': len(comparison_data),
                'total_wins': total_wins,
                'total_games': total_games,
                'average_win_percentage': avg_win_percentage,
                'season': season
            },
            'comparison_info': {
                'requested_managers': unique_managers,
                'missing_managers': [m for m in unique_managers if not any(cm['username'].lower() == m.lower() for cm in comparison_data)],
                'season': season,
                'comparison_type': 'multi_manager'
            }
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error comparing multiple managers: {e}")
        return None