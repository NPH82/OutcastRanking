# OutcastRanking

A Flask-based web application for ranking and analyzing fantasy football managers across multiple Sleeper leagues.

## Features

- **Manager Search**: Look up individual managers and view their performance across all leagues
- **Cross-League Rankings**: Compare managers from the same league across all their other leagues
- **Multi-Manager Comparison**: Rank up to 100 managers simultaneously
- **Head-to-Head Analysis**: Discover your biggest rivals and favorite opponents
- **Performance Statistics**: Track wins, losses, and win percentages across multiple seasons
- **Dark Mode Support**: Toggle between light and dark themes

## Security Features

✅ Environment-based configuration  
✅ Secure session cookies with HTTPOnly and SameSite flags  
✅ Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)  
✅ HSTS enabled in production  
✅ No hardcoded secrets  
✅ Input validation and error handling  
✅ SQL injection protection via SQLAlchemy ORM  

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd OutcastRanking
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and set your SECRET_KEY
   # On Windows, you can generate a secret key with:
   # python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:5001`

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///outcast_ranking.db
FLASK_ENV=development
FLASK_DEBUG=0
PORT=5001
```

### Production Deployment

⚠️ **Important Security Considerations for Production:**

1. **Set a strong SECRET_KEY**: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
2. **Disable Debug Mode**: Set `FLASK_DEBUG=0`
3. **Use HTTPS**: Enable SSL/TLS for secure connections
4. **Use a Production Server**: Deploy with Gunicorn, uWSGI, or similar (not Flask's development server)
5. **Set FLASK_ENV=production**: Enables additional security features like HSTS
6. **Database**: Consider using PostgreSQL or MySQL instead of SQLite for production
7. **Rate Limiting**: Implement rate limiting for API endpoints
8. **Regular Updates**: Keep dependencies updated with `pip install --upgrade -r requirements.txt`

Example production deployment with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## Project Structure

```
OutcastRanking/
├── app/
│   ├── __init__.py           # Flask app initialization
│   ├── models.py             # Database models
│   ├── routes.py             # Main routes (legacy)
│   ├── manager_routes.py     # Manager search routes
│   ├── scheduler.py          # Background task scheduler
│   ├── services/             # Business logic
│   │   ├── cross_league_rankings.py
│   │   ├── league_rankings.py
│   │   ├── manager_leagues.py
│   │   ├── ranking.py
│   │   ├── roster_utils.py
│   │   └── sleeper_api.py    # Sleeper API integration
│   ├── static/               # CSS and JavaScript
│   └── templates/            # HTML templates
├── instance/                 # Instance-specific files (ignored by git)
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore rules
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
└── run.py                    # Application entry point
```

## API Integration

This application integrates with the [Sleeper API](https://docs.sleeper.com/) to fetch fantasy football league data. No API key is required.

## Database

The application uses SQLite by default for simplicity. The database file is created automatically in the `instance/` directory.

### Models

- **Manager**: Stores manager profiles
- **ManagerStats**: Season-specific statistics for managers
- **LeagueCache**: Cached league data for performance
- **UserSubmission**: Tracks user search submissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (if available)
5. Submit a pull request

## License

This project is provided as-is for personal and educational use.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Data provided by [Sleeper API](https://docs.sleeper.com/)
- Scheduling powered by [APScheduler](https://apscheduler.readthedocs.io/)
