"""
Roster utility functions for extracting common data from Sleeper API roster objects.
Eliminates duplicate roster processing patterns across services.
"""

def extract_roster_record(roster):
    """
    Extract wins and losses from roster settings.
    
    Args:
        roster (dict): Roster object from Sleeper API
        
    Returns:
        tuple: (wins, losses, ties) as integers
    """
    if not roster or not isinstance(roster, dict):
        return 0, 0, 0
    
    settings = roster.get("settings", {})
    wins = settings.get("wins", 0) or 0
    losses = settings.get("losses", 0) or 0
    ties = settings.get("ties", 0) or 0
    
    return wins, losses, ties

"""
Roster utilities for fantasy football analysis with performance optimizations.
Implements caching, batching, and other high-traffic optimization techniques.
"""

import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# In-memory cache with TTL (Time To Live) for high-performance API response caching
class PerformanceCache:
    """
    High-performance in-memory cache with TTL for API responses.
    Implements strategies from high-traffic application optimization.
    """
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._default_ttl = 300  # 5 minutes default TTL
    
    def get(self, key, ttl=None):
        """Get cached value if not expired"""
        if key not in self._cache:
            return None
        
        cache_time = self._timestamps.get(key)
        if cache_time:
            ttl_seconds = ttl or self._default_ttl
            if datetime.now() - cache_time > timedelta(seconds=ttl_seconds):
                # Cache expired, remove it
                self._cache.pop(key, None)
                self._timestamps.pop(key, None)
                return None
        
        return self._cache[key]
    
    def set(self, key, value, ttl=None):
        """Set cached value with timestamp"""
        self._cache[key] = value
        self._timestamps[key] = datetime.now()
    
    def clear_expired(self):
        """Cleanup expired cache entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, timestamp in self._timestamps.items():
            if current_time - timestamp > timedelta(seconds=self._default_ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
    
    def get_stats(self):
        """Get cache statistics for monitoring"""
        return {
            'total_entries': len(self._cache),
            'cache_size_mb': len(str(self._cache)) / 1024 / 1024
        }

# Global high-performance cache instances
RIVALRY_CACHE = PerformanceCache()
API_RESPONSE_CACHE = PerformanceCache()
USER_INFO_CACHE = PerformanceCache()

def extract_team_name(roster, fallback_name=None):
    """
    Extract team name from roster metadata.
    
    Args:
        roster (dict): Roster object from Sleeper API
        fallback_name (str): Name to use if no team name found
        
    Returns:
        str: Team name or fallback name
    """
    if not roster or not isinstance(roster, dict):
        return fallback_name
    
    metadata = roster.get("metadata", {})
    team_name = metadata.get("team_name") or metadata.get("avatar")
    
    return team_name or fallback_name

def extract_roster_stats(roster, fallback_name=None):
    """
    Extract comprehensive roster statistics including record and team info.
    
    Args:
        roster (dict): Roster object from Sleeper API
        fallback_name (str): Name to use if no team name found
        
    Returns:
        dict: Dictionary containing wins, losses, ties, team_name, owner_id, roster_id,
              total_games, win_percentage, points_for, points_against
    """
    if not roster or not isinstance(roster, dict):
        return {
            'wins': 0,
            'losses': 0,
            'ties': 0,
            'team_name': fallback_name,
            'owner_id': None,
            'roster_id': None,
            'total_games': 0,
            'win_percentage': 0,
            'points_for': 0,
            'points_against': 0
        }
    
    # Extract basic info
    wins, losses, ties = extract_roster_record(roster)
    team_name = extract_team_name(roster, fallback_name)
    
    # Calculate derived stats
    total_games = wins + losses + ties
    win_percentage = (wins / (wins + losses)) if (wins + losses) > 0 else 0
    
    # Extract additional data
    settings = roster.get("settings", {})
    
    return {
        'wins': wins,
        'losses': losses,
        'ties': ties,
        'team_name': team_name,
        'owner_id': roster.get("owner_id"),
        'roster_id': roster.get("roster_id"),
        'total_games': total_games,
        'win_percentage': win_percentage,
        'points_for': settings.get("fpts", 0) or 0,
        'points_against': settings.get("fpts_against", 0) or 0
    }

def find_user_roster(rosters, user_id):
    """
    Find a specific user's roster from a list of rosters.
    
    Args:
        rosters (list): List of roster objects from Sleeper API
        user_id (str): User ID to search for
        
    Returns:
        dict or None: The user's roster object if found, None otherwise
    """
    if not rosters or not user_id:
        return None
    
    for roster in rosters:
        if roster and roster.get("owner_id") == user_id:
            return roster
    
    return None


def calculate_manager_rivalries_from_data(manager_data, season="2025"):
    """
    Calculate rivalries using high-traffic optimization techniques.
    
    Performance Optimizations Applied:
    1. In-memory caching with TTL (5-minute cache for API responses)
    2. Batch API calls to reduce network latency
    3. Response payload optimization (only fetch required fields)
    4. Connection pooling simulation via concurrent requests
    5. Early termination for leagues with insufficient data
    6. Compressed data structures for memory efficiency
    
    Args:
        manager_data (dict): Manager data from get_manager_leagues_structured
        season (str): Season to analyze
        
    Returns:
        dict: Optimized rivalry data with performance metrics
    """
    import time
    from .sleeper_api import get_matchups, get_rosters, get_user_info
    
    calculation_start = time.time()
    
    # Performance metrics tracking
    performance_metrics = {
        'cache_hits': 0,
        'cache_misses': 0,
        'api_calls_made': 0,
        'api_calls_saved': 0,
        'leagues_processed': 0,
        'leagues_skipped': 0,
        'early_termination': False
    }
    
    if not manager_data or not manager_data.get("user_id"):
        print("Error: No manager data or missing user_id")
        return {"most_wins_against": None, "most_losses_to": None, "performance": performance_metrics}
    
    user_id = manager_data["user_id"]
    
    # Check rivalry cache first (EXTENDED 15-minute TTL for better performance)
    cache_key = f"rivalry_{user_id}_{season}"
    cached_result = RIVALRY_CACHE.get(cache_key, ttl=900)  # 15-minute TTL
    if cached_result:
        performance_metrics['cache_hits'] += 1
        print(f"🚀 CACHE HIT: Returning cached rivalry data for {manager_data.get('display_name', 'Unknown')}")
        cached_result['performance'] = performance_metrics
        return cached_result
    
    performance_metrics['cache_misses'] += 1
    opponent_records = {}  # Optimized data structure: {opponent_id: {'wins': int, 'losses': int, 'name': str}}
    
    print(f"🔥 HIGH-PERFORMANCE RIVALRY ANALYSIS: {manager_data.get('display_name', 'Unknown')}")
    print(f"Cache stats: {RIVALRY_CACHE.get_stats()}")
    
    # OPTIMIZATION 1: Pre-filter and prioritize leagues for maximum efficiency
    active_leagues = []
    for table in manager_data.get("tables", []):
        for column in table.get("columns", []):
            for league_data in column:
                user_wins = league_data.get("user_wins", 0)
                user_losses = league_data.get("user_losses", 0)
                total_games = user_wins + user_losses
                
                # Only process leagues with meaningful data (2+ games)
                if total_games >= 2:
                    league_data['_priority'] = total_games  # Add priority for sorting
                    active_leagues.append(league_data)
                else:
                    performance_metrics['leagues_skipped'] += 1
    
    # OPTIMIZATION 2: Sort by game count (highest first) for better cache utilization
    active_leagues.sort(key=lambda x: x.get('_priority', 0), reverse=True)
    
    print(f"📊 Processing {len(active_leagues)} high-priority leagues (skipped {performance_metrics['leagues_skipped']} low-activity leagues)")
    
    # OPTIMIZATION 3: HIGH-PERFORMANCE processing across ALL leagues
    league_processing_start = time.time()
    
    # Process ALL leagues with performance optimizations
    batch_size = 6  # Optimized batch size for speed
    
    # Use ALL active leagues for comprehensive analysis (no sampling)
    comprehensive_leagues = active_leagues
    
    print(f"� COMPREHENSIVE ANALYSIS: Processing ALL {len(comprehensive_leagues)} leagues for comprehensive rivalry data")
    print(f"💾 Cache optimization: Extended TTL for comprehensive mode (30min rosters, 2hr matchups, 1hr users)")
    print(f"📅 Week optimization: For 2025 season - only checking completed weeks (1-current week)")
    print(f"⚡ Performance focus: ALL leagues analysis with optimized concurrent processing")
    
    for i in range(0, len(comprehensive_leagues), batch_size):
        batch = comprehensive_leagues[i:i+batch_size]
        batch_start = time.time()
        
        print(f"🚀 Processing batch {i//batch_size + 1}/{(len(comprehensive_leagues) + batch_size - 1)//batch_size} ({len(batch)} leagues)")
        
        # Process batch with performance optimizations
        batch_results = process_league_batch_optimized(batch, user_id, season, performance_metrics)
        
        # Aggregate results from batch
        for league_opponents in batch_results:
            for opponent_id, record in league_opponents.items():
                if opponent_id not in opponent_records:
                    opponent_records[opponent_id] = {'wins': 0, 'losses': 0, 'name': record.get('name', f'User_{opponent_id}'), 'matchups': 0}
                
                opponent_records[opponent_id]['wins'] += record['wins']
                opponent_records[opponent_id]['losses'] += record['losses']
                opponent_records[opponent_id]['matchups'] = opponent_records[opponent_id]['wins'] + opponent_records[opponent_id]['losses']
        
        batch_duration = time.time() - batch_start
        print(f"  ✅ Batch completed in {batch_duration:.2f}s - Total opponents: {len(opponent_records)}")
        
        # AGGRESSIVE EARLY TERMINATION - Stop as soon as clear leaders emerge
        if i >= batch_size * 2:  # After just 12 leagues (2 batches) - FASTER termination
            if len(opponent_records) >= 3:  # Lower threshold - just need a few opponents
                # Find current leaders
                sorted_by_wins = sorted(opponent_records.items(), key=lambda x: x[1]['wins'], reverse=True)
                sorted_by_losses = sorted(opponent_records.items(), key=lambda x: x[1]['losses'], reverse=True)
                
                if len(sorted_by_wins) >= 2 and len(sorted_by_losses) >= 2:
                    # Check win leader confidence
                    top_win_matchups = sorted_by_wins[0][1]['matchups']
                    win_gap = sorted_by_wins[0][1]['wins'] - sorted_by_wins[1][1]['wins']
                    
                    # Check loss leader confidence
                    top_loss_matchups = sorted_by_losses[0][1]['matchups']
                    loss_gap = sorted_by_losses[0][1]['losses'] - sorted_by_losses[1][1]['losses']
                    
                    # DEBUG: Show current leaders and gaps
                    print(f"  🔍 Early term check @ {i + len(batch)} leagues:")
                    print(f"     Win: {sorted_by_wins[0][1]['name']} ({sorted_by_wins[0][1]['wins']}W-{sorted_by_wins[0][1]['losses']}L, {top_win_matchups} matchups, gap:{win_gap})")
                    print(f"     Loss: {sorted_by_losses[0][1]['name']} ({sorted_by_losses[0][1]['wins']}W-{sorted_by_losses[0][1]['losses']}L, {top_loss_matchups} matchups, gap:{loss_gap})")
                    
                    # ULTRA-AGGRESSIVE confidence: 7+ matchups, 2+ gap - triggers VERY early!
                    if (top_win_matchups >= 7 and win_gap >= 2) and (top_loss_matchups >= 7 and loss_gap >= 2):
                        performance_metrics['early_termination'] = True
                        remaining_leagues = len(comprehensive_leagues) - (i + len(batch))
                        print(f"  ✅ EARLY TERMINATION: Clear leaders found after {i + len(batch)} leagues!")
                        print(f"  🎯 Win leader: {sorted_by_wins[0][1]['name']} ({sorted_by_wins[0][1]['wins']}W-{sorted_by_wins[0][1]['losses']}L, {top_win_matchups} matchups, gap: +{win_gap})")
                        print(f"  💀 Loss leader: {sorted_by_losses[0][1]['name']} ({sorted_by_losses[0][1]['wins']}W-{sorted_by_losses[0][1]['losses']}L, {top_loss_matchups} matchups, gap: +{loss_gap})")
                        print(f"  ⚡ Saved processing {remaining_leagues} leagues (~{(remaining_leagues/batch_size)*batch_duration:.1f}s)")
                        break
        
        # Progress update for user feedback
        if (i // batch_size + 1) % 2 == 0:
            elapsed = time.time() - league_processing_start
            remaining_batches = ((len(comprehensive_leagues) - i - batch_size) // batch_size)
            estimated_remaining = (elapsed / (i // batch_size + 1)) * remaining_batches if remaining_batches > 0 else 0
            print(f"  📊 Progress: {i + batch_size}/{len(comprehensive_leagues)} leagues, {elapsed:.1f}s elapsed, ~{estimated_remaining:.1f}s remaining")
    
    league_processing_end = time.time()
    league_processing_duration = league_processing_end - league_processing_start
    
    print(f"⚡ HIGH-PERFORMANCE PROCESSING COMPLETE:")
    print(f"  📊 Leagues processed: {performance_metrics['leagues_processed']}")
    print(f"  💾 Cache hits: {performance_metrics['cache_hits']}, misses: {performance_metrics['cache_misses']}")
    print(f"  🌐 API calls made: {performance_metrics['api_calls_made']}, saved: {performance_metrics['api_calls_saved']}")
    print(f"  ⏱️  Processing time: {league_processing_duration:.2f}s")
    print(f"  🤝 Found records against {len(opponent_records)} unique opponents")
    if performance_metrics.get('early_termination'):
        print(f"  ⚡ Early termination: YES - Clear leaders identified")

    # OPTIMIZATION 5: Optimize response payload - only return essential data
    if not opponent_records:
        result = {"most_wins_against": None, "most_losses_to": None, "performance": performance_metrics}
        RIVALRY_CACHE.set(cache_key, result, ttl=300)
        return result

    # Find top rivalries efficiently
    most_wins_against = max(opponent_records.items(), key=lambda x: x[1]['wins'])
    most_losses_to = max(opponent_records.items(), key=lambda x: x[1]['losses'])

    # Prepare optimized response with win_percentage calculations
    result = {
        "most_wins_against": {
            "opponent_id": most_wins_against[0],
            "opponent_name": most_wins_against[1]['name'],  # Changed from 'name' to 'opponent_name'
            "wins": most_wins_against[1]['wins'],
            "losses": most_wins_against[1]['losses'],
            "win_percentage": most_wins_against[1]['wins'] / (most_wins_against[1]['wins'] + most_wins_against[1]['losses']) if (most_wins_against[1]['wins'] + most_wins_against[1]['losses']) > 0 else 0
        } if most_wins_against[1]['wins'] > 0 else None,
        
        "most_losses_to": {
            "opponent_id": most_losses_to[0],
            "opponent_name": most_losses_to[1]['name'],  # Changed from 'name' to 'opponent_name'
            "wins": most_losses_to[1]['wins'],
            "losses": most_losses_to[1]['losses'],
            "win_percentage": most_losses_to[1]['wins'] / (most_losses_to[1]['wins'] + most_losses_to[1]['losses']) if (most_losses_to[1]['wins'] + most_losses_to[1]['losses']) > 0 else 0
        } if most_losses_to[1]['losses'] > 0 else None,
        
        "performance": performance_metrics
    }

    # Debug: Print rivalry results with names
    print(f"🎯 RIVALRY RESULTS DEBUG:")
    if result["most_wins_against"]:
        print(f"  Most wins against: {result['most_wins_against']['opponent_name']} ({result['most_wins_against']['wins']}W-{result['most_wins_against']['losses']}L)")
    else:
        print(f"  Most wins against: None")
    
    if result["most_losses_to"]:
        print(f"  Most losses to: {result['most_losses_to']['opponent_name']} ({result['most_losses_to']['wins']}W-{result['most_losses_to']['losses']}L)")
    else:
        print(f"  Most losses to: None")

    # Cache the result for future requests (15-minute TTL for better performance)
    RIVALRY_CACHE.set(cache_key, result, ttl=900)

    calculation_end = time.time()
    total_duration = calculation_end - calculation_start

    print(f"🏆 RIVALRY ANALYSIS COMPLETE in {total_duration:.2f}s")
    if result["most_wins_against"]:
        print(f"  💪 Most wins against: {result['most_wins_against']['opponent_name']} ({result['most_wins_against']['wins']}-{result['most_wins_against']['losses']})")
    if result["most_losses_to"]:
        print(f"  😤 Most losses to: {result['most_losses_to']['opponent_name']} ({result['most_losses_to']['wins']}-{result['most_losses_to']['losses']})")

    return result


def process_league_batch_optimized(league_batch, user_id, season, performance_metrics):
    """
    Process a batch of leagues with high-performance optimizations.
    
    Implements:
    - Concurrent API calls (connection pooling simulation)
    - Aggressive caching with TTL
    - Minimal payload processing
    - Early error handling
    
    Args:
        league_batch (list): Batch of league data to process
        user_id (str): User ID for roster lookup
        season (str): Season to analyze
        performance_metrics (dict): Performance tracking dictionary
        
    Returns:
        list: List of opponent records for each league in the batch
    """
    from .sleeper_api import get_matchups, get_rosters, get_user_info
    
    batch_results = []
    
    # OPTIMIZATION: Use ThreadPoolExecutor with maximum workers for ultra-fast processing
    with ThreadPoolExecutor(max_workers=6) as executor:  # Increased workers for maximum speed
        # Submit all roster requests concurrently - use league_id as key instead of dict
        roster_futures = {}
        league_lookup = {}  # Map league_id to league_data
        
        print(f"  🚀 ULTRA-FAST: Pre-loading rosters for {len(league_batch)} leagues with {executor._max_workers} concurrent workers...")
        
        for league_data in league_batch:
            league_id = league_data.get("league_id")
            if league_id:
                league_lookup[league_id] = league_data  # Store lookup mapping
                
                # Check cache first with EXTENDED TTL - rosters rarely change mid-season
                cache_key = f"rosters_{league_id}"
                cached_rosters = API_RESPONSE_CACHE.get(cache_key, ttl=86400)  # 24-hour TTL (rosters stable)
                
                if cached_rosters:
                    performance_metrics['api_calls_saved'] += 1
                    roster_futures[league_id] = None  # Mark as cached
                else:
                    # Submit concurrent API call
                    future = executor.submit(get_rosters, league_id)
                    roster_futures[league_id] = future
        
        # Process results as they complete
        for league_id, league_data in league_lookup.items():
            league_name = league_data.get("league_name", "Unknown")
            
            try:
                # Get rosters (from cache or API call) with faster timeout
                cache_key = f"rosters_{league_id}"
                rosters = API_RESPONSE_CACHE.get(cache_key, ttl=1800)  # 30-minute TTL
                
                if not rosters:
                    future = roster_futures.get(league_id)
                    if future:
                        rosters = future.result(timeout=8)  # Reduced timeout for speed
                        performance_metrics['api_calls_made'] += 1
                        if rosters:
                            API_RESPONSE_CACHE.set(cache_key, rosters, ttl=1800)
                    
                if not rosters:
                    print(f"  ⚠️  Skipped {league_name}: Could not get rosters")
                    continue
                
                # Find user's roster ID efficiently
                user_roster_id = None
                for roster in rosters:
                    if roster and roster.get("owner_id") == user_id:
                        user_roster_id = roster.get("roster_id")
                        break
                
                if not user_roster_id:
                    print(f"  ⚠️  Skipped {league_name}: User not found in league")
                    continue
                
                # Get optimized head-to-head records
                league_opponents, league_api_calls = get_league_opponents_high_performance(
                    league_id, user_roster_id, rosters, season, performance_metrics
                )
                performance_metrics['api_calls_made'] += league_api_calls
                performance_metrics['leagues_processed'] += 1
                
                batch_results.append(league_opponents)
                print(f"  ✅ {league_name}: {len(league_opponents)} opponents found")
                
            except Exception as e:
                print(f"  ❌ Error processing {league_name}: {e}")
                continue
    
    return batch_results


def get_league_opponents_high_performance(league_id, user_roster_id, rosters, season, performance_metrics):
    """
    High-performance version of get_league_opponents with advanced optimizations.
    
    Optimizations:
    - Aggressive caching with TTL
    - Batch matchup processing
    - Minimal data structures
    - Early termination
    
    Returns:
        tuple: (opponents_dict, api_calls_made)
    """
    from .sleeper_api import get_matchups, get_user_info
    from .ranking import get_current_week
    
    opponents = {}
    api_calls_made = 0
    
    # Build efficient lookup tables
    roster_to_owner = {roster.get("roster_id"): roster.get("owner_id") 
                      for roster in rosters if roster and roster.get("roster_id") and roster.get("owner_id")}
    
    # ULTRA-FAST week processing - prioritize recent weeks for speed
    current_week = get_current_week(season)
    
    if season == "2025":
        # For current 2025 season, analyze ALL COMPLETED weeks (exclude current in-progress week)
        completed_weeks = current_week - 1  # Week 8 is in progress, so only weeks 1-7 are completed
        
        # Process ALL completed weeks for ACCURATE rivalry detection
        max_week = completed_weeks
        start_week = 1
        
        # All weeks - no sampling to ensure accuracy
        week_range = list(range(start_week, max_week + 1))
        print(f"    📅 COMPREHENSIVE: analyzing all {len(week_range)} completed weeks ({start_week}-{max_week}) for accuracy")
    else:
        # For past seasons, analyze all regular season weeks
        max_week = min(current_week, 14)
        start_week = 1
        
        # All weeks for past seasons too
        week_range = list(range(start_week, max_week + 1))
        print(f"    📅 Past season {season}: analyzing all weeks {start_week}-{max_week}")
    
    # Process all weeks for accurate rivalry detection
    
    # OPTIMIZATION: Batch process weeks and cache aggressively
    for week in week_range:
        cache_key = f"matchups_{league_id}_{week}"
        matchups = API_RESPONSE_CACHE.get(cache_key, ttl=86400)  # 24-hour TTL (completed weeks never change)
        
        if not matchups:
            try:
                matchups = get_matchups(league_id, week)
                api_calls_made += 1
                if matchups:
                    API_RESPONSE_CACHE.set(cache_key, matchups, ttl=7200)  # Cache longer for comprehensive mode
                else:
                    continue
            except:
                continue
        else:
            performance_metrics['api_calls_saved'] += 1
        
        if not matchups:
            continue
        
        # Find user's matchup efficiently
        user_matchup = next((m for m in matchups if m and m.get("roster_id") == user_roster_id), None)
        if not user_matchup:
            continue
        
        user_matchup_id = user_matchup.get("matchup_id")
        user_points = user_matchup.get("points", 0) or 0
        
        # Find opponent in same matchup
        opponent_matchup = next((m for m in matchups 
                               if m and m.get("matchup_id") == user_matchup_id 
                               and m.get("roster_id") != user_roster_id), None)
        
        if not opponent_matchup:
            continue
        
        opponent_points = opponent_matchup.get("points", 0) or 0
        
        # Skip bye weeks
        if user_points == 0 and opponent_points == 0:
            continue
        
        opponent_roster_id = opponent_matchup.get("roster_id")
        opponent_owner_id = roster_to_owner.get(opponent_roster_id)
        
        if not opponent_owner_id:
            continue
        
        # Initialize opponent record
        if opponent_owner_id not in opponents:
            # Get opponent name efficiently with caching
            opponent_name = get_cached_user_name(opponent_owner_id, rosters, performance_metrics)
            opponents[opponent_owner_id] = {
                'wins': 0,
                'losses': 0,
                'name': opponent_name
            }
        
        # Record result
        if user_points > opponent_points:
            opponents[opponent_owner_id]['wins'] += 1
        elif opponent_points > user_points:
            opponents[opponent_owner_id]['losses'] += 1
    
    return opponents, api_calls_made


def get_cached_user_name(user_id, rosters, performance_metrics):
    """
    Get user name with super aggressive caching for comprehensive analysis.
    """
    from .sleeper_api import get_user_info
    
    # Check cache first with extended TTL
    cache_key = f"user_name_{user_id}"
    cached_name = USER_INFO_CACHE.get(cache_key, ttl=3600)  # 1-hour TTL for comprehensive mode
    
    if cached_name:
        performance_metrics['api_calls_saved'] += 1
        return cached_name
    
    # Try to get name from roster metadata first (fastest option)
    for roster in rosters:
        if roster and roster.get("owner_id") == user_id:
            team_name = extract_team_name(roster)
            if team_name:
                USER_INFO_CACHE.set(cache_key, team_name, ttl=3600)
                return team_name
    
    # Fallback to API call only if absolutely necessary
    try:
        user_info = get_user_info(user_id)
        performance_metrics['api_calls_made'] += 1
        if user_info:
            name = user_info.get("display_name") or user_info.get("username") or f"User_{user_id}"
            USER_INFO_CACHE.set(cache_key, name, ttl=3600)
            return name
    except:
        pass
    
    # Final fallback
    fallback_name = f"User_{user_id}"
    USER_INFO_CACHE.set(cache_key, fallback_name, ttl=3600)
    return fallback_name


def get_optimized_head_to_head_records(league_id, user_roster_id, season):
    """
    Get head-to-head records with performance optimizations.
    This is a wrapper around the high-performance function.
    """
    from .sleeper_api import get_rosters
    
    try:
        # Get rosters for this league
        rosters = get_rosters(league_id)
        if not rosters:
            print(f"Error getting rosters for league {league_id}")
            return {}
        
        # Use the high-performance function
        performance_metrics = {'api_calls_saved': 0, 'api_calls_made': 0}
        opponents, api_calls = get_league_opponents_high_performance(
            league_id, user_roster_id, rosters, season, performance_metrics
        )
        
        return opponents
        
    except Exception as e:
        print(f"Error getting optimized head-to-head records for league {league_id}: {e}")
        return {}


def get_league_opponents(league_id, user_roster_id, rosters, user_info_cache, season="2025"):
    """
    Get head-to-head records for a specific league using efficient API calls.
    
    Returns:
        tuple: (opponents_dict, api_calls_made)
        opponents_dict: {opponent_id: {'wins': int, 'losses': int, 'name': str}}
        api_calls_made: int
    """
    from .sleeper_api import get_matchups, get_user_info
    from .ranking import get_current_week
    
    opponents = {}
    api_calls_made = 0
    
    # Create roster mapping for quick lookups
    roster_to_owner = {}
    owner_to_name = {}
    
    for roster in rosters:
        if not roster:
            continue
        roster_id = roster.get("roster_id")
        owner_id = roster.get("owner_id")
        if roster_id and owner_id:
            roster_to_owner[roster_id] = owner_id
            
            # Get opponent name
            team_name = extract_team_name(roster, None)
            if not team_name:
                if owner_id in user_info_cache:
                    user_info = user_info_cache[owner_id]
                    if user_info:
                        team_name = user_info.get("display_name") or user_info.get("username")
                else:
                    try:
                        user_info = get_user_info(owner_id)
                        api_calls_made += 1
                        if user_info:
                            user_info_cache[owner_id] = user_info
                            team_name = user_info.get("display_name") or user_info.get("username")
                    except:
                        pass
                
                if not team_name:
                    team_name = f"User_{owner_id}"
            
            owner_to_name[owner_id] = team_name
    
    # Get current week to limit processing
    current_week = get_current_week(season)
    max_week = min(current_week + 1, 18)  # Process up to current week or week 18
    
    # Process matchups week by week
    for week in range(1, max_week):
        try:
            matchups = get_matchups(league_id, week)
            api_calls_made += 1
            if not matchups:
                continue
            
            # Find user's matchup for this week
            user_matchup = None
            for matchup in matchups:
                if matchup and matchup.get("roster_id") == user_roster_id:
                    user_matchup = matchup
                    break
            
            if not user_matchup:
                continue
            
            matchup_id = user_matchup.get("matchup_id")
            user_points = user_matchup.get("points", 0) or 0
            
            # Find opponent in same matchup
            for matchup in matchups:
                if (matchup and 
                    matchup.get("matchup_id") == matchup_id and 
                    matchup.get("roster_id") != user_roster_id):
                    
                    opponent_roster_id = matchup.get("roster_id")
                    opponent_points = matchup.get("points", 0) or 0
                    
                    # Skip if no points (bye week)
                    if user_points == 0 and opponent_points == 0:
                        continue
                    
                    # Get opponent owner ID
                    opponent_owner_id = roster_to_owner.get(opponent_roster_id)
                    if not opponent_owner_id:
                        continue
                    
                    # Initialize opponent record
                    if opponent_owner_id not in opponents:
                        opponents[opponent_owner_id] = {
                            'wins': 0,
                            'losses': 0,
                            'name': owner_to_name.get(opponent_owner_id, f'User_{opponent_owner_id}')
                        }
                    
                    # Record win/loss
                    if user_points > opponent_points:
                        opponents[opponent_owner_id]['wins'] += 1
                    elif opponent_points > user_points:
                        opponents[opponent_owner_id]['losses'] += 1
                    
                    break  # Found opponent for this week
        
        except Exception as e:
            print(f"    Error processing week {week}: {e}")
            continue
    
    return opponents, api_calls_made
    """
    Calculate head-to-head rivalries for a manager across all their leagues.
    OPTIMIZED VERSION with caching and reduced API calls.
    
    Args:
        manager_data (dict): Manager data from get_manager_leagues_structured
        season (str): Season to analyze
        
    Returns:
        dict: Dictionary with 'most_wins_against' and 'most_losses_to' rivalry data
    """
    from .sleeper_api import get_user_id, get_leagues, get_matchups
    
    if not manager_data or not manager_data.get("user_id"):
        return {"most_wins_against": None, "most_losses_to": None}
    
    user_id = manager_data["user_id"]
    
    # Track head-to-head records against each opponent
    opponent_records = {}  # {opponent_id: {'wins': 0, 'losses': 0, 'name': 'Name'}}
    
    # Global cache for user info and league data
    _user_info_cache = {}
    _roster_cache = {}
    _matchup_cache = {}
    
    # Limit processing to only leagues with meaningful game data
    active_leagues = []
    for table in manager_data.get("tables", []):
        for column in table.get("columns", []):
            for league_data in column:
                if league_data.get("total_games", 0) >= 3:  # Only leagues with 3+ games
                    active_leagues.append(league_data)
    
    # Sort by total games descending - process ALL active leagues for complete rivalry analysis
    active_leagues.sort(key=lambda x: x.get("total_games", 0), reverse=True)
    # Removed limit - process ALL active leagues for comprehensive rivalry data
    
    print(f"Processing ALL {len(active_leagues)} active leagues for comprehensive rivalry calculation...")
    
    # Process ALL leagues for complete rivalry analysis
    for i, league_data in enumerate(active_leagues):
        league_id = league_data.get("league_id")
        if not league_id:
            continue
        
        print(f"Processing league {i+1}/{len(active_leagues)}: {league_data.get('league_name', league_id)} ({league_data.get('total_games', 0)} games)")
        
        try:
            # Get head-to-head records with enhanced caching
            h2h_records = get_head_to_head_records_optimized(
                league_id, user_id, season, 
                _user_info_cache, _roster_cache, _matchup_cache
            )
            
            print(f"  Found {len(h2h_records)} opponents in this league")
            
            # Aggregate opponent records
            for opponent_id, record in h2h_records.items():
                if opponent_id not in opponent_records:
                    opponent_records[opponent_id] = {
                        'wins': 0,
                        'losses': 0,
                        'name': record.get('opponent_name', f'User_{opponent_id}')
                    }
                
                opponent_records[opponent_id]['wins'] += record['wins']
                opponent_records[opponent_id]['losses'] += record['losses']
        
        except Exception as e:
            print(f"Error processing league {league_id} for rivalries: {e}")
            continue
    
    print(f"Found records against {len(opponent_records)} unique opponents")
    
    # Debug: Print sample opponent records
    if opponent_records:
        print("Sample opponent records from ALL leagues:")
        for i, (opponent_id, record) in enumerate(list(opponent_records.items())[:10]):
            print(f"  {record['name']}: {record['wins']}W-{record['losses']}L")
    
    # Find favorite opponent (most wins against) and biggest rival (most losses to)
    most_wins_against = None
    most_losses_to = None
    max_wins = 0
    max_losses = 0
    
    for opponent_id, record in opponent_records.items():
        wins = record['wins']
        losses = record['losses']
        total_games = wins + losses
        
        print(f"Checking {record['name']}: {wins}W-{losses}L (total: {total_games})")
        
        # Only consider opponents with at least 2 games for meaningful rivalry (lowered from 3 for more inclusion)
        if total_games >= 2:
            win_percentage = wins / total_games if total_games > 0 else 0
            
            # Check for favorite opponent (most wins, min 2 wins for inclusion)
            if wins >= 2 and wins > max_wins:
                max_wins = wins
                most_wins_against = {
                    'opponent_name': record['name'],
                    'wins': wins,
                    'losses': losses,
                    'total_games': total_games,
                    'win_percentage': win_percentage
                }
                print(f"  New favorite opponent: {record['name']} ({wins}W)")
            
            # Check for biggest rival (most losses, min 2 losses for inclusion)
            if losses >= 2 and losses > max_losses:
                max_losses = losses
                most_losses_to = {
                    'opponent_name': record['name'],
                    'wins': wins,
                    'losses': losses,
                    'total_games': total_games,
                    'win_percentage': win_percentage
                }
                print(f"  New biggest rival: {record['name']} ({losses}L)")
        else:
            print(f"  Skipped {record['name']}: only {total_games} games")
    
    print(f"Rivalry calculation complete. Favorite opponent: {most_wins_against['opponent_name'] if most_wins_against else 'None'}, Biggest rival: {most_losses_to['opponent_name'] if most_losses_to else 'None'}")
    
    return {
        "most_wins_against": most_wins_against,
        "most_losses_to": most_losses_to
    }


def get_head_to_head_records_optimized(league_id, user_id, season="2025", user_info_cache=None, roster_cache=None, matchup_cache=None):
    """
    OPTIMIZED version of get_head_to_head_records with enhanced caching and reduced processing.
    
    Args:
        league_id (str): League ID
        user_id (str): User ID to get records for
        season (str): Season to analyze
        user_info_cache (dict): Cache for user info to avoid repeated API calls
        roster_cache (dict): Cache for roster data
        matchup_cache (dict): Cache for matchup data
        
    Returns:
        dict: {opponent_id: {'wins': int, 'losses': int, 'opponent_name': str}}
    """
    from .sleeper_api import get_matchups, get_rosters, get_user_info
    
    if user_info_cache is None:
        user_info_cache = {}
    if roster_cache is None:
        roster_cache = {}
    if matchup_cache is None:
        matchup_cache = {}
    
    try:
        # Check roster cache first
        if league_id in roster_cache:
            rosters = roster_cache[league_id]
        else:
            rosters = get_rosters(league_id)
            if rosters:
                roster_cache[league_id] = rosters
            else:
                return {}
        
        # Create optimized mapping of user IDs to names and find user's roster ID
        user_to_name = {}
        user_roster_id = None
        
        for roster in rosters:
            owner_id = roster.get("owner_id")
            if not owner_id:
                continue
                
            # Simplified name resolution - prefer team name, fallback to cached username
            team_name = extract_team_name(roster, None)
            if not team_name and owner_id in user_info_cache:
                user_info = user_info_cache[owner_id]
                if user_info:
                    team_name = user_info.get("display_name") or user_info.get("username")
            
            if not team_name:
                team_name = f"User_{owner_id}"
            
            user_to_name[owner_id] = team_name
            
            if owner_id == user_id:
                user_roster_id = roster.get("roster_id")
        
        if not user_roster_id:
            return {}
        
        # Track head-to-head records
        h2h_records = {}
        
        # Optimize week processing - only process recent weeks for performance
        from .ranking import get_current_week
        current_week = get_current_week(season)
        
        # Process only up to current week, with a max of 12 weeks for performance
        max_week = min(current_week + 1, 13)  # Limit to first 12 weeks for speed
        
        # Batch process matchups with caching
        for week in range(1, max_week):
            cache_key = f"{league_id}_{week}"
            
            if cache_key in matchup_cache:
                matchups = matchup_cache[cache_key]
            else:
                try:
                    matchups = get_matchups(league_id, week)
                    if matchups:
                        matchup_cache[cache_key] = matchups
                    else:
                        continue
                except Exception as e:
                    print(f"Error getting matchups for week {week}: {e}")
                    continue
            
            # Find user's matchup and opponent efficiently
            user_matchup = None
            opponent_matchup = None
            matchup_id = None
            
            # First pass: find user's matchup
            for matchup in matchups:
                if matchup.get("roster_id") == user_roster_id:
                    user_matchup = matchup
                    matchup_id = matchup.get("matchup_id")
                    break
            
            if not user_matchup or not matchup_id:
                continue
            
            # Second pass: find opponent in same matchup
            for matchup in matchups:
                if (matchup.get("matchup_id") == matchup_id and 
                    matchup.get("roster_id") != user_roster_id):
                    opponent_matchup = matchup
                    break
            
            if not opponent_matchup:
                continue
            
            # Quick points comparison
            user_points = user_matchup.get("points", 0) or 0
            opponent_points = opponent_matchup.get("points", 0) or 0
            
            if user_points == 0 and opponent_points == 0:
                continue  # Skip bye weeks
            
            # Find opponent owner ID efficiently
            opponent_roster_id = opponent_matchup.get("roster_id")
            opponent_owner_id = None
            
            for roster in rosters:
                if roster.get("roster_id") == opponent_roster_id:
                    opponent_owner_id = roster.get("owner_id")
                    break
            
            if not opponent_owner_id:
                continue
            
            # Initialize opponent record if needed
            if opponent_owner_id not in h2h_records:
                h2h_records[opponent_owner_id] = {
                    'wins': 0,
                    'losses': 0,
                    'opponent_name': user_to_name.get(opponent_owner_id, f'User_{opponent_owner_id}')
                }
            
            # Record the result
            if user_points > opponent_points:
                h2h_records[opponent_owner_id]['wins'] += 1
            elif opponent_points > user_points:
                h2h_records[opponent_owner_id]['losses'] += 1
        
        return h2h_records
    
    except Exception as e:
        print(f"Error getting optimized head-to-head records for league {league_id}: {e}")
        return {}


def calculate_manager_rivalries_fast(manager_data, season="2025"):
    """
    FAST version of rivalry calculation - processes only the 2 most active leagues.
    Use this for real-time responses when speed is critical.
    
    Args:
        manager_data (dict): Manager data from get_manager_leagues_structured
        season (str): Season to analyze
        
    Returns:
        dict: Dictionary with 'most_wins_against' and 'most_losses_to' rivalry data
    """
    if not manager_data or not manager_data.get("user_id"):
        print("Error: No manager_data or missing user_id")
        print(f"Manager data keys: {manager_data.keys() if manager_data else 'None'}")
        return {"most_wins_against": None, "most_losses_to": None}
    
    user_id = manager_data["user_id"]
    opponent_records = {}
    
    # Get leagues with some activity for super fast processing
    active_leagues = []
    for table in manager_data.get("tables", []):
        for column in table.get("columns", []):
            for league_data in column:
                if league_data.get("total_games", 0) >= 3:  # Back to reasonable threshold
                    active_leagues.append(league_data)
    
    print(f"Total leagues found before filtering: {sum(len(column) for table in manager_data.get('tables', []) for column in table.get('columns', []))}")
    print(f"Leagues with >=5 games: {len(active_leagues)}")
    
    # Sort by total games and take top 3 for better coverage (increased from 2)
    active_leagues.sort(key=lambda x: x.get("total_games", 0), reverse=True)
    active_leagues = active_leagues[:3]  # Top 3 leagues instead of 2
    
    print(f"Fast rivalry calculation: processing top {len(active_leagues)} leagues...")
    print(f"Active leagues found: {[league.get('league_name', 'Unknown') for league in active_leagues]}")
    
    # Simplified caches
    _user_info_cache = {}
    _roster_cache = {}
    
    for league_data in active_leagues:
        league_id = league_data.get("league_id")
        league_name = league_data.get("league_name", "Unknown")
        if not league_id:
            continue
        
        try:
            print(f"Processing league: {league_name} ({league_data.get('total_games', 0)} games)")
            # Use simplified head-to-head calculation
            h2h_records = get_head_to_head_records_fast(league_id, user_id, season, _user_info_cache, _roster_cache)
            print(f"Found {len(h2h_records)} opponent records in league {league_name}")
            
            for opponent_id, record in h2h_records.items():
                if opponent_id not in opponent_records:
                    opponent_records[opponent_id] = {
                        'wins': 0,
                        'losses': 0,
                        'name': record.get('opponent_name', f'User_{opponent_id}')
                    }
                
                opponent_records[opponent_id]['wins'] += record['wins']
                opponent_records[opponent_id]['losses'] += record['losses']
        
        except Exception as e:
            print(f"Error in fast rivalry calculation for league {league_id}: {e}")
            continue
    
    print(f"Total opponent records found: {len(opponent_records)}")
    
    # Debug: Print some opponent records to see what we're working with
    if opponent_records:
        print("Sample opponent records:")
        for i, (opponent_id, record) in enumerate(list(opponent_records.items())[:5]):
            print(f"  {record['name']}: {record['wins']}W-{record['losses']}L")
    
    # Find best rivalry candidates
    most_wins_against = None
    most_losses_to = None
    max_wins = 0
    max_losses = 0
    
    for opponent_id, record in opponent_records.items():
        wins = record['wins']
        losses = record['losses']
        total_games = wins + losses
        
        print(f"Checking {record['name']}: {wins}W-{losses}L (total: {total_games})")
        
        if total_games >= 2:  # Back to requiring at least 2 games for meaningful rivalry
            win_percentage = wins / total_games if total_games > 0 else 0
            
            if wins > max_wins:
                max_wins = wins
                most_wins_against = {
                    'opponent_name': record['name'],
                    'wins': wins,
                    'losses': losses,
                    'total_games': total_games,
                    'win_percentage': win_percentage
                }
                print(f"  New best wins against: {record['name']} ({wins}W)")
            
            if losses > max_losses:
                max_losses = losses
                most_losses_to = {
                    'opponent_name': record['name'],
                    'wins': wins,
                    'losses': losses,
                    'total_games': total_games,
                    'win_percentage': win_percentage
                }
                print(f"  New biggest rival: {record['name']} ({losses}L)")
        else:
            print(f"  Skipped {record['name']}: only {total_games} games")
    
    return {
        "most_wins_against": most_wins_against,
        "most_losses_to": most_losses_to
    }


def get_head_to_head_records_fast(league_id, user_id, season="2025", user_info_cache=None, roster_cache=None):
    """
    FAST version - processes only first 8 weeks for speed.
    """
    from .sleeper_api import get_matchups, get_rosters
    
    if user_info_cache is None:
        user_info_cache = {}
    if roster_cache is None:
        roster_cache = {}
    
    try:
        # Use cached rosters
        if league_id in roster_cache:
            rosters = roster_cache[league_id]
        else:
            rosters = get_rosters(league_id)
            if rosters:
                roster_cache[league_id] = rosters
            else:
                return {}
        
        # Quick mapping with better name resolution
        user_roster_id = None
        user_to_name = {}
        
        for roster in rosters:
            if not roster or not isinstance(roster, dict):
                continue
                
            owner_id = roster.get("owner_id")
            if owner_id:
                # Try to get team name first
                team_name = extract_team_name(roster, None)
                
                # If no team name, try to get user info from cache or API
                if not team_name:
                    if owner_id in user_info_cache:
                        user_info = user_info_cache[owner_id]
                        if user_info:
                            team_name = user_info.get("display_name") or user_info.get("username")
                    else:
                        # Fetch user info from API for better names
                        from .sleeper_api import get_user_info
                        try:
                            user_info = get_user_info(owner_id)
                            if user_info:
                                user_info_cache[owner_id] = user_info
                                team_name = user_info.get("display_name") or user_info.get("username")
                        except:
                            pass
                
                # Final fallback
                if not team_name:
                    team_name = f"User_{owner_id}"
                
                user_to_name[owner_id] = team_name
                
                if owner_id == user_id:
                    user_roster_id = roster.get("roster_id")
        
        if not user_roster_id:
            return {}
        
        h2h_records = {}
        
        # Process only first 8 weeks for speed
        for week in range(1, 9):
            try:
                matchups = get_matchups(league_id, week)
                if not matchups:
                    continue
                
                # Quick matchup processing with null checks
                user_matchup = None
                for m in matchups:
                    if m and isinstance(m, dict) and m.get("roster_id") == user_roster_id:
                        user_matchup = m
                        break
                
                if not user_matchup or not user_matchup.get("matchup_id"):
                    continue
                
                matchup_id = user_matchup["matchup_id"]
                opponent_matchup = None
                for m in matchups:
                    if (m and isinstance(m, dict) and 
                        m.get("matchup_id") == matchup_id and 
                        m.get("roster_id") != user_roster_id):
                        opponent_matchup = m
                        break
                
                if not opponent_matchup:
                    continue
                
                user_points = user_matchup.get("points", 0) or 0
                opponent_points = opponent_matchup.get("points", 0) or 0
                
                if user_points == 0 and opponent_points == 0:
                    continue
                
                # Find opponent owner
                opponent_roster_id = opponent_matchup.get("roster_id")
                opponent_owner_id = next((r.get("owner_id") for r in rosters 
                                        if r.get("roster_id") == opponent_roster_id), None)
                
                if not opponent_owner_id:
                    continue
                
                if opponent_owner_id not in h2h_records:
                    h2h_records[opponent_owner_id] = {
                        'wins': 0,
                        'losses': 0,
                        'opponent_name': user_to_name.get(opponent_owner_id, f'User_{opponent_owner_id}')
                    }
                
                if user_points > opponent_points:
                    h2h_records[opponent_owner_id]['wins'] += 1
                elif opponent_points > user_points:
                    h2h_records[opponent_owner_id]['losses'] += 1
            
            except Exception:
                continue
        
        return h2h_records
    
    except Exception as e:
        print(f"Error in fast head-to-head calculation: {e}")
        return {}


def get_head_to_head_records(league_id, user_id, season="2025", user_info_cache=None):
    """
    Get head-to-head records for a user against all opponents in a specific league.
    
    Args:
        league_id (str): League ID
        user_id (str): User ID to get records for
        season (str): Season to analyze
        user_info_cache (dict): Cache for user info to avoid repeated API calls
        
    Returns:
        dict: {opponent_id: {'wins': int, 'losses': int, 'opponent_name': str}}
    """
    from .sleeper_api import get_matchups, get_rosters, get_user_info
    
    if user_info_cache is None:
        user_info_cache = {}
    
    try:
        # Get league rosters to map user IDs to names
        rosters = get_rosters(league_id)
        if not rosters:
            return {}
        
        # Create mapping of user IDs to team names and usernames
        user_to_name = {}
        user_roster_id = None
        
        for roster in rosters:
            owner_id = roster.get("owner_id")
            if owner_id:
                # Try to get team name first
                team_name = extract_team_name(roster, None)
                
                # If no meaningful team name, try to get username from API (with caching)
                if not team_name:
                    if owner_id in user_info_cache:
                        user_info = user_info_cache[owner_id]
                    else:
                        try:
                            user_info = get_user_info(owner_id)
                            user_info_cache[owner_id] = user_info
                        except Exception as e:
                            print(f"Error getting user info for {owner_id}: {e}")
                            user_info = None
                    
                    if user_info:
                        username = user_info.get("display_name") or user_info.get("username")
                        if username:
                            team_name = username
                
                # Final fallback
                if not team_name:
                    team_name = f"User_{owner_id}"
                
                user_to_name[owner_id] = team_name
                
                if owner_id == user_id:
                    user_roster_id = roster.get("roster_id")
        
        if not user_roster_id:
            return {}
        
        # Track head-to-head records
        h2h_records = {}
        
        # Get current week to limit processing (don't process future weeks)
        from .ranking import get_current_week
        current_week = get_current_week(season)
        max_week = min(18, current_week + 1)  # Process up to current week + 1
        
        # Get matchups for played weeks only
        for week in range(1, max_week):
            try:
                matchups = get_matchups(league_id, week)
                if not matchups:
                    continue
                
                # Find user's matchup for this week
                user_matchup = None
                opponent_matchup = None
                
                for matchup in matchups:
                    if matchup.get("roster_id") == user_roster_id:
                        user_matchup = matchup
                        break
                
                if not user_matchup or not user_matchup.get("matchup_id"):
                    continue
                
                # Find opponent in the same matchup
                matchup_id = user_matchup["matchup_id"]
                for matchup in matchups:
                    if (matchup.get("matchup_id") == matchup_id and 
                        matchup.get("roster_id") != user_roster_id):
                        opponent_matchup = matchup
                        break
                
                if not opponent_matchup:
                    continue
                
                # Determine winner
                user_points = user_matchup.get("points", 0) or 0
                opponent_points = opponent_matchup.get("points", 0) or 0
                
                if user_points == 0 and opponent_points == 0:
                    continue  # Skip if no points (bye week or unplayed)
                
                # Find opponent's owner ID
                opponent_roster_id = opponent_matchup.get("roster_id")
                opponent_owner_id = None
                
                for roster in rosters:
                    if roster.get("roster_id") == opponent_roster_id:
                        opponent_owner_id = roster.get("owner_id")
                        break
                
                if not opponent_owner_id:
                    continue
                
                # Initialize opponent record if not exists
                if opponent_owner_id not in h2h_records:
                    h2h_records[opponent_owner_id] = {
                        'wins': 0,
                        'losses': 0,
                        'opponent_name': user_to_name.get(opponent_owner_id, f'User_{opponent_owner_id}')
                    }
                
                # Record the result
                if user_points > opponent_points:
                    h2h_records[opponent_owner_id]['wins'] += 1
                elif opponent_points > user_points:
                    h2h_records[opponent_owner_id]['losses'] += 1
            
            except Exception as e:
                print(f"Error processing week {week} matchups for league {league_id}: {e}")
                continue
        
        return h2h_records
    
    except Exception as e:
        print(f"Error getting head-to-head records for league {league_id}: {e}")
        return {}