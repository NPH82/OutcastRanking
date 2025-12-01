from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .services.sleeper_api import get_user_id, get_leagues
from .services.manager_leagues import get_manager_leagues_structured
from .services.league_rankings import get_league_leaderboard
from .services.cross_league_rankings import generate_cross_league_leaderboard, get_manager_league_details, compare_multiple_managers
from .services.roster_utils import extract_roster_record, calculate_manager_rivalries_fast, calculate_manager_rivalries_from_data
from .models import db, UserSubmission
from datetime import datetime
import time

manager_bp = Blueprint("manager", __name__)

# Add logging for all requests
@manager_bp.before_request
def log_request():
    print(f"[REQUEST] {request.method} {request.path} - Form data: {dict(request.form)}")

@manager_bp.route("/test")
def test_route():
    print("Test route accessed!")
    return "Flask is working!"

@manager_bp.route("/", methods=["GET", "POST"])
def manager_search():
    """Main page for searching a manager and viewing their leagues"""
    print("=== MANAGER SEARCH ROUTE CALLED ===")
    print(f"Request method: {request.method}")
    print(f"Form data: {dict(request.form)}")
    print("===================================")
    
    manager_data = None
    season = "2025"  # Default season
    
    print(f"Manager search route accessed - Method: {request.method}")
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        season = request.form.get("season", "2025")
        
        print(f"POST request received - Username: {username}, Season: {season}")
        
        if not username:
            flash("Please enter a manager username.", "error")
            return render_template("manager_search.html", season=season)
        
        try:
            # Start timing the entire manager search process
            search_start_time = time.time()
            print(f"=== STARTING MANAGER SEARCH AT {datetime.now().strftime('%H:%M:%S')} ===")
            
            # Get manager's leagues data
            leagues_start_time = time.time()
            manager_data = get_manager_leagues_structured(username, season)
            leagues_end_time = time.time()
            leagues_duration = leagues_end_time - leagues_start_time
            print(f"Manager leagues data retrieved in {leagues_duration:.2f} seconds")
            
            if not manager_data:
                flash(f"Manager '{username}' not found or has no leagues in {season} season.", "error")
            else:
                # Debug: Check if display_name is set
                print(f"DEBUG: Manager data display_name: {manager_data.get('display_name', 'NOT SET')}")
                
                # Calculate summary stats
                total_wins = 0
                total_losses = 0
                active_leagues = 0
                
                for table in manager_data["tables"]:
                    for column in table["columns"]:
                        for league in column:
                            total_wins += league["user_wins"]
                            total_losses += league["user_losses"]
                            if league["total_games"] > 0:
                                active_leagues += 1
                
                total_games = total_wins + total_losses
                overall_win_percentage = (total_wins / total_games) if total_games > 0 else 0
                
                manager_data["summary"] = {
                    "active_leagues": active_leagues,
                    "total_wins": total_wins,
                    "total_losses": total_losses,
                    "total_games": total_games,
                    "overall_win_percentage": overall_win_percentage
                }
                
                # HIGH-PERFORMANCE RIVALRY CALCULATION with Advanced Optimizations
                rivalry_start_time = time.time()
                # Return manager data immediately WITHOUT rivalry calculation for faster response
                manager_data["most_wins_against"] = None
                manager_data["most_losses_to"] = None
                manager_data["rivalry_pending"] = True  # Flag to show pending state
                
                flash(f"Found {manager_data['total_leagues']} leagues for {manager_data['display_name']} in {season} season.", "success")
                
                # Calculate total time and display comprehensive performance summary
                search_end_time = time.time()
                total_duration = search_end_time - search_start_time
                
                print(f"\n🎯 === HIGH-PERFORMANCE MANAGER SEARCH COMPLETED ===")
                print(f"🚀 Total Duration: {total_duration:.2f} seconds")
                print(f"📊 Performance Breakdown:")
                print(f"  - League Data Retrieval: {leagues_duration:.2f}s")
                print(f"  - Rivalry Analysis: ASYNC (pending)")
                
                # No rivalry performance metrics since it's async
                print(f"===============================================\n")
                
        except Exception as e:
            flash(f"Error searching for manager: {str(e)}", "error")
            print(f"Error in manager search: {e}")
    
    return render_template("manager_search.html", 
                         manager_data=manager_data, 
                         season=season)

@manager_bp.route("/league/<league_id>")
def league_leaderboard(league_id):
    """Show cross-league leaderboard for all managers in a specific league"""
    season = request.args.get("season", "2025")
    manager_name = request.args.get("manager", "")
    
    try:
        # Generate cross-league leaderboard based on all managers in this league
        leaderboard_data = generate_cross_league_leaderboard(league_id, season)
        
        if not leaderboard_data:
            flash(f"Could not load cross-league leaderboard for league {league_id}", "error")
            return redirect(url_for("manager.manager_search"))
        
        return render_template("cross_league_leaderboard.html", 
                             leaderboard_data=leaderboard_data,
                             league_id=league_id,
                             season=season,
                             manager_name=manager_name)
        
    except Exception as e:
        flash(f"Error loading cross-league leaderboard: {str(e)}", "error")
        return redirect(url_for("manager.manager_search"))

@manager_bp.route("/compare", methods=["POST"])
def compare_managers():
    """Compare multiple specific managers across all their leagues"""
    try:
        manager_list = request.form.get("manager_list", "").strip()
        season = request.form.get("season", "2025")
        
        if not manager_list:
            flash("Please enter at least 2 manager usernames to compare.", "error")
            return redirect(url_for("manager.manager_search"))
        
        # Parse manager list - handle multiple formats:
        # - One per line
        # - Space separated on same line  
        # - Comma separated on same line
        # - Mixed formats
        manager_usernames = []
        
        # Split by lines first
        lines = manager_list.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains commas or spaces
            if ',' in line:
                # Split by comma
                parts = [part.strip() for part in line.split(',') if part.strip()]
                manager_usernames.extend(parts)
            elif ' ' in line:
                # Split by space (but not if it looks like a single name with spaces)
                words = line.split()
                # If it's multiple distinct usernames (no spaces in individual names typically)
                if len(words) > 1 and all(len(word) > 2 for word in words):
                    manager_usernames.extend(words)
                else:
                    # Treat as single username with spaces
                    manager_usernames.append(line)
            else:
                # Single username
                manager_usernames.append(line)
        
        # Remove duplicates and empty strings
        manager_usernames = list(set([m.strip() for m in manager_usernames if m.strip()]))
        
        if len(manager_usernames) < 2:
            flash("Please enter at least 2 manager usernames to compare.", "error")
            return redirect(url_for("manager.manager_search"))
        
        if len(manager_usernames) > 100:
            flash("Maximum 100 managers allowed for comparison.", "error")
            return redirect(url_for("manager.manager_search"))
        
        # Generate comparison data
        comparison_data = compare_multiple_managers(manager_usernames, season)
        
        if not comparison_data or not comparison_data.get('managers'):
            missing_managers = manager_usernames
            if comparison_data and comparison_data.get('comparison_info'):
                missing_managers = comparison_data['comparison_info'].get('missing_managers', manager_usernames)
            
            if missing_managers:
                flash(f"Could not find data for managers: {', '.join(missing_managers)}", "error")
            else:
                flash("Could not load comparison data. Please check manager usernames and try again.", "error")
            return redirect(url_for("manager.manager_search"))
        
        return render_template("manager_comparison.html", 
                             comparison_data=comparison_data,
                             season=season)
        
    except Exception as e:
        flash(f"Error comparing managers: {str(e)}", "error")
        return redirect(url_for("manager.manager_search"))
        flash(f"Error loading league leaderboard: {str(e)}", "error")
        print(f"Error in league leaderboard: {e}")
        return redirect(url_for("manager.manager_search"))

@manager_bp.route("/api/league/<league_id>/info")
def league_info_api(league_id):
    """API endpoint to get basic league info for previews"""
    try:
        from .services.sleeper_api import get_rosters
        
        rosters = get_rosters(league_id)
        if not rosters:
            return jsonify({"error": "League not found"}), 404
        
        # Count active managers (those with games played)
        active_managers = 0
        for roster in rosters:
            # Use utility function to extract wins/losses
            wins, losses, ties = extract_roster_record(roster)
            if wins > 0 or losses > 0:
                active_managers += 1
        
        return jsonify({
            "total_managers": len(rosters),
            "active_managers": active_managers,
            "league_id": league_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@manager_bp.route("/api/manager/<username>/details")
def api_manager_details(username):
    """API endpoint to get detailed league breakdown for a manager"""
    season = request.args.get("season", "2025")
    
    try:
        manager_details = get_manager_league_details(username, season)
        if manager_details:
            return jsonify({
                "success": True, 
                "leagues": manager_details['leagues'],
                "manager": {
                    "username": manager_details['username'],
                    "display_name": manager_details['display_name']
                }
            })
        else:
            return jsonify({"success": False, "error": "Manager not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@manager_bp.route('/calculate_rivalry', methods=['POST'])
def calculate_rivalry():
    """
    Async endpoint for calculating manager rivalries.
    Called via AJAX after the initial manager search loads.
    """
    import threading
    from flask import jsonify
    import time
    from datetime import datetime
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        manager_data = data.get('manager_data')
        season = data.get('season', '2025')
        
        if not manager_data:
            return jsonify({"success": False, "error": "Manager data required"}), 400
        
        print(f"🚀 Starting ASYNC rivalry calculation for {manager_data.get('display_name', 'Unknown')} at {datetime.now().strftime('%H:%M:%S')}")
        
        rivalry_start_time = time.time()
        
        try:
            print(f"🔥 Calculating rivalries for {manager_data.get('display_name', 'Unknown')} (using optimized high-traffic techniques)...")
            print(f"Manager has {manager_data.get('total_leagues', 0)} total leagues")
            
            rivalries = calculate_manager_rivalries_from_data(manager_data, season)
            rivalry_end_time = time.time()
            rivalry_duration = rivalry_end_time - rivalry_start_time
            
            # Extract and display performance metrics
            performance = rivalries.get("performance", {})
            
            print(f"🎯 ASYNC RIVALRY ANALYSIS COMPLETE:")
            print(f"  ⏱️  Total Duration: {rivalry_duration:.2f}s")
            print(f"  💾 Cache Performance: {performance.get('cache_hits', 0)} hits, {performance.get('cache_misses', 0)} misses")
            print(f"  🌐 API Efficiency: {performance.get('api_calls_made', 0)} calls made, {performance.get('api_calls_saved', 0)} calls saved")
            print(f"  📊 League Processing: {performance.get('leagues_processed', 0)} processed, {performance.get('leagues_skipped', 0)} skipped")
            
            # Calculate performance metrics
            total_api_operations = performance.get('api_calls_made', 0) + performance.get('api_calls_saved', 0)
            cache_hit_rate = (performance.get('api_calls_saved', 0) / total_api_operations * 100) if total_api_operations > 0 else 0
            print(f"  🚄 Cache Hit Rate: {cache_hit_rate:.1f}% (High-Traffic Optimization)")
            
            return jsonify({
                "success": True,
                "most_wins_against": rivalries["most_wins_against"],
                "most_losses_to": rivalries["most_losses_to"],
                "performance": performance,
                "duration": rivalry_duration
            })
            
        except Exception as e:
            rivalry_end_time = time.time()
            rivalry_duration = rivalry_end_time - rivalry_start_time
            print(f"❌ Error in async rivalry calculation after {rivalry_duration:.2f} seconds: {e}")
            import traceback
            traceback.print_exc()
            
            return jsonify({
                "success": False,
                "error": str(e),
                "duration": rivalry_duration
            }), 500
            
    except Exception as e:
        print(f"❌ Error in async rivalry endpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500