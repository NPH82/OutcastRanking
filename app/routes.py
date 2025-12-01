# Flask routes
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .services.ranking import get_top_managers, get_cached_rankings
from .models import db, UserSubmission
from datetime import datetime

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def leaderboard():
    managers = []
    season = "2024"  # Default to 2024 since it has complete data
    usernames_str = ""
    
    if request.method == "POST":
        usernames_str = request.form.get("usernames", "").strip()
        season = request.form.get("season", "2024")
        
        print(f"Processing request for usernames: '{usernames_str}' (length: {len(usernames_str)})")
        
        if usernames_str and len(usernames_str.strip()) > 0:
            usernames = [u.strip() for u in usernames_str.split(",") if u.strip()]
            print(f"Parsed {len(usernames)} usernames: {usernames}")
            
            if not usernames:
                flash("Please enter valid usernames separated by commas", "error")
            else:
                try:
                    # Save the submission
                    submission = UserSubmission(usernames=usernames_str, season=season)
                    db.session.add(submission)
                    db.session.commit()
                    
                    # Get managers with caching
                    managers = get_cached_rankings(usernames, season)
                    
                    if managers:
                        flash(f"Successfully processed {len(usernames)} usernames for {season} season! Found {len(managers)} managers.", "success")
                    else:
                        flash(f"No data found for the provided usernames in {season} season. Please check the usernames are correct.", "error")
                    
                except Exception as e:
                    print(f"Error in routes: {str(e)}")  # Log to console
                    db.session.rollback()  # Rollback any database changes
                    flash(f"Error processing request. Please check that the usernames are valid Sleeper usernames and try again.", "error")
                    managers = []
        else:
            flash("Please enter at least one username", "error")
    
    elif request.args.get("usernames"):
        # Handle GET requests with parameters (for backward compatibility)
        usernames_str = request.args.get("usernames", "")
        season = request.args.get("season", "2024")
        usernames = [u.strip() for u in usernames_str.split(",") if u.strip()]
        
        if usernames:
            try:
                managers = get_cached_rankings(usernames, season)
            except Exception as e:
                flash(f"Error loading data: {str(e)}", "error")
                managers = []
    else:
        # No cached data loading without usernames for now
        pass
    
    return render_template("leaderboard.html", 
                         managers=managers, 
                         usernames=usernames_str, 
                         season=season)

@main.route("/refresh")
def refresh():
    """Manual refresh endpoint"""
    try:
        from .services.ranking import refresh_all_data
        refresh_all_data()
        flash("Data refreshed successfully!", "success")
    except Exception as e:
        flash(f"Error refreshing data: {str(e)}", "error")
    
    return redirect(url_for("main.leaderboard"))

@main.route("/test-accessibility")
def test_accessibility():
    """Test page for accessibility improvements"""
    # Mock data for testing
    leaderboard_data = {
        'leaderboard': [
            {
                'rank': 1,
                'display_name': 'StoneColdCJ',
                'username': 'StoneColdCJ',
                'total_wins': 12,
                'total_losses': 3,
                'win_percentage': 0.80,
                'total_games': 15,
                'active_leagues': 3
            },
            {
                'rank': 2,
                'display_name': 'TestUser',
                'username': 'testuser',
                'total_wins': 8,
                'total_losses': 7,
                'win_percentage': 0.533,
                'total_games': 15,
                'active_leagues': 2
            }
        ],
        'stats': {
            'total_managers_processed': 2,
            'total_managers_found': 2
        },
        'source_league': {
            'league_name': 'Test League',
            'league_id': '123456789',
            'season': '2025'
        }
    }
    
    return render_template("cross_league_leaderboard.html", 
                         leaderboard_data=leaderboard_data,
                         league_id='123456789',
                         season='2025',
                         manager_name='Test')
