from datetime import datetime, timedelta
from .sleeper_api import get_user_id, get_leagues, get_rosters
from .roster_utils import extract_roster_record, extract_team_name
from ..models import db, LeagueCache

def get_current_week(season):
    """Calculate current NFL week based on season"""
    if season == "2025":
        # 2025 season started September 4, 2025
        season_start = datetime(2025, 9, 4)
        now = datetime.now()
        days_elapsed = (now - season_start).days
        current_week = min(max(1, (days_elapsed // 7) + 1), 18)
        print(f"2025 season: {days_elapsed} days elapsed, calculated week {current_week}")
        return current_week
    elif season == "2024":
        # 2024 season is complete, get all weeks
        return 18
    else:
        return 18  # For other seasons, get all weeks

def get_league_records_for_users(league_id, target_user_ids, season):
    """
    Get records for multiple users in a single league using /rosters endpoint
    Returns dict of {user_id: {wins, losses, team_name, win_percentage}}
    """
    try:
        print(f"    Fetching rosters from: https://api.sleeper.app/v1/league/{league_id}/rosters")
        rosters = get_rosters(league_id)
        if not rosters:
            return {}
            
        user_records = {}
        
        for roster in rosters:
            owner_id = roster.get("owner_id")
            if owner_id in target_user_ids:
                # Get wins and losses using utility function
                wins, losses, ties = extract_roster_record(roster)
                
                # Calculate total games and win percentage
                total_games = wins + losses
                win_percentage = (wins / total_games) if total_games > 0 else 0
                
                # Get team name using utility function
                team_name = extract_team_name(roster)
                
                user_records[owner_id] = {
                    'wins': wins,
                    'losses': losses,
                    'total_games': total_games,
                    'win_percentage': win_percentage,
                    'team_name': team_name
                }
                
                print(f"    Found {owner_id}: {wins}W-{losses}L ({win_percentage:.3f} win%) - Team: {team_name or 'No Name'}")
        
        return user_records
        
    except Exception as e:
        print(f"    Error fetching league rosters: {e}")
        return {}

def batch_process_leagues(league_ids, target_user_ids, batch_size=20):
    """
    Process leagues in batches to reduce API load and add concurrent processing
    """
    import concurrent.futures
    import threading
    
    all_records = {}
    processed_count = 0
    total_leagues = len(league_ids)
    
    print(f"Processing {total_leagues} leagues in batches of {batch_size}")
    
    # Split leagues into batches
    league_batches = [league_ids[i:i + batch_size] for i in range(0, len(league_ids), batch_size)]
    
    def process_league_batch(batch):
        batch_records = {}
        for league_id in batch:
            try:
                records = get_league_records_for_users(league_id, target_user_ids, "")
                if records:
                    batch_records[league_id] = records
            except Exception as e:
                print(f"Error processing league {league_id}: {e}")
        return batch_records
    
    # Process batches with limited concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_batch = {executor.submit(process_league_batch, batch): batch for batch in league_batches}
        
        for future in concurrent.futures.as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                batch_records = future.result()
                all_records.update(batch_records)
                processed_count += len(batch)
                print(f"  Completed batch: {processed_count}/{total_leagues} leagues processed")
            except Exception as e:
                print(f"Batch failed: {e}")
    
    return all_records

def get_top_managers(usernames, season, max_weeks=None, max_leagues_per_user=None):
    """
    Optimized version with batching, caching, and smart league deduplication
    """
    print(f"Starting optimized processing for {len(usernames)} users in {season} season")
    
    # Step 1: Get all user IDs efficiently
    user_id_map = {}
    print("\nGetting user IDs...")
    for username in usernames:
        user_id = get_user_id(username)
        if user_id:
            user_id_map[username] = user_id
            print(f"  Found {username} -> {user_id}")
        else:
            print(f"  ERROR: {username} -> NOT FOUND")
    
    if not user_id_map:
        print("ERROR: No valid users found")
        return []
    
    # Step 2: Collect all unique leagues (deduplicated)
    print(f"\nCollecting leagues for {len(user_id_map)} users...")
    all_leagues = set()
    league_to_users = {}  # Track which users are in each league
    
    for username, user_id in user_id_map.items():
        print(f"  Getting leagues for {username}...")
        leagues = get_leagues(user_id, season)
        if leagues:
            league_ids = [league.get("league_id") for league in leagues if league.get("league_id")]
            all_leagues.update(league_ids)
            
            # Track user membership for efficiency
            for league_id in league_ids:
                if league_id not in league_to_users:
                    league_to_users[league_id] = set()
                league_to_users[league_id].add(user_id)
            
            print(f"    Found {len(league_ids)} leagues")
        else:
            print(f"    No leagues found")
    
    print(f"\nAnalysis:")
    print(f"  Total unique leagues: {len(all_leagues)}")
    print(f"  Average leagues per user: {len(all_leagues) / len(user_id_map):.1f}")
    
    # Step 3: Process leagues efficiently with batching
    print(f"\nProcessing leagues with optimization...")
    target_user_ids = set(user_id_map.values())
    
    # Filter leagues to only process those with our target users
    relevant_leagues = [league_id for league_id in all_leagues 
                       if league_id in league_to_users and 
                       league_to_users[league_id] & target_user_ids]
    
    print(f"  Relevant leagues (contain our users): {len(relevant_leagues)}")
    print(f"  Efficiency gain: {(len(all_leagues) - len(relevant_leagues)) / len(all_leagues) * 100:.1f}% fewer API calls")
    
    # Process leagues in optimized batches
    all_league_records = batch_process_leagues(relevant_leagues, target_user_ids, batch_size=15)
    
    # Step 4: Aggregate results
    print(f"\nAggregating results...")
    user_stats = {}
    for username in user_id_map.keys():
        user_stats[username] = {
            "wins": 0,
            "losses": 0,
            "display_name": username,
            "leagues": []
        }
    
    for league_id, league_records in all_league_records.items():
        for username, user_id in user_id_map.items():
            if user_id in league_records:
                record = league_records[user_id]
                wins = record['wins']
                losses = record['losses']
                team_name = record['team_name']
                
                # Skip empty leagues
                if wins == 0 and losses == 0:
                    continue
                
                # Update display name
                if team_name and team_name != username:
                    user_stats[username]["display_name"] = team_name
                
                # Add to totals
                user_stats[username]["wins"] += wins
                user_stats[username]["losses"] += losses
                user_stats[username]["leagues"].append({
                    "league_id": league_id,
                    "wins": wins,
                    "losses": losses,
                    "team_name": team_name or username,
                    "win_percentage": record['win_percentage']
                })
    
    # Step 5: Calculate final rankings
    ranked = []
    print(f"\nFinal Results:")
    for username, stats in user_stats.items():
        total_games = stats["wins"] + stats["losses"]
        win_percentage = (stats["wins"] / total_games) if total_games > 0 else 0
        
        ranked.append({
            "display_name": stats["display_name"],
            "wins": stats["wins"],
            "losses": stats["losses"],
            "win_percentage": win_percentage,
            "total_games": total_games,
            "leagues_count": len(stats["leagues"])
        })
        
        print(f"  {username}: {stats['wins']}W-{stats['losses']}L ({win_percentage:.1%}) in {len(stats['leagues'])} leagues")
    
    # Sort by win percentage
    ranked.sort(key=lambda x: (x["win_percentage"], x["total_games"]), reverse=True)
    
    print(f"\nProcessing complete! {len(ranked)} managers ranked.")
    return ranked

def get_cached_rankings(usernames, season):
    """Get rankings with caching support"""
    try:
        return get_top_managers(usernames, season)
    except Exception as e:
        print(f"Error getting rankings: {e}")
        return []

def refresh_all_data():
    """Refresh all cached data - placeholder function for scheduler compatibility"""
    print("refresh_all_data called - no action needed with new direct approach")
    return True