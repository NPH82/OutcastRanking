# PostgreSQL Setup Guide

## Render.com (Automatic - Recommended)

Your `render.yaml` is already configured to automatically create a PostgreSQL database!

### Deployment Steps:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add PostgreSQL support"
   git push origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your `NPH82/OutcastRanking` repository
   - Render will automatically:
     - Create a PostgreSQL database (free tier)
     - Create the web service
     - Link them together
     - Initialize the database

3. **Done!** Your app will use PostgreSQL automatically.

---

## Manual Database Initialization (If Needed)

If tables aren't created automatically, run this in Render's Shell:

```bash
python init_db.py
```

---

## Local Development with PostgreSQL

### Option 1: Keep SQLite for Local (Recommended)
Your app will automatically use SQLite locally and PostgreSQL in production. No changes needed!

### Option 2: Use PostgreSQL Locally

1. **Install PostgreSQL**:
   - Windows: Download from [postgresql.org](https://www.postgresql.org/download/)
   - Mac: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql`

2. **Create local database**:
   ```bash
   psql -U postgres
   CREATE DATABASE outcast_ranking;
   CREATE USER outcast_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE outcast_ranking TO outcast_user;
   \q
   ```

3. **Update .env**:
   ```env
   DATABASE_URL=postgresql://outcast_user:your_password@localhost/outcast_ranking
   SECRET_KEY=your-secret-key-here
   ```

4. **Initialize database**:
   ```bash
   python init_db.py
   ```

---

## Railway.app Alternative

If using Railway instead of Render:

1. **Deploy app to Railway**
2. **Add PostgreSQL plugin**:
   - Click "New" → "Database" → "PostgreSQL"
   - Railway auto-sets `DATABASE_URL` environment variable
3. **Done!** Railway handles the rest.

---

## Verifying PostgreSQL Connection

After deployment, check the logs:

```
✅ Connected to PostgreSQL
✅ Database tables created successfully!
📊 Created tables: manager, league, matchup, ...
```

If you see `sqlite` in the logs, the `DATABASE_URL` wasn't set correctly.

---

## Database Migrations (Future)

When you modify models, you'll need migrations:

1. **Install Flask-Migrate**:
   ```bash
   pip install Flask-Migrate
   ```

2. **Add to requirements.txt**:
   ```
   Flask-Migrate==4.0.5
   ```

3. **Initialize migrations** (first time only):
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

4. **After model changes**:
   ```bash
   flask db migrate -m "Add new field"
   flask db upgrade
   ```

---

## Free Tier Limits

### Render PostgreSQL (Free)
- 1 GB storage
- 90 days data retention
- Shared CPU
- Perfect for this app

### Railway PostgreSQL (Free $5 credit)
- 1 GB storage  
- Shared CPU
- Credit resets monthly

### Supabase (Alternative Free)
- 500 MB storage
- No time limit
- Good for long-term free hosting

---

## Troubleshooting

**Error: `relation "manager" does not exist`**
- Run: `python init_db.py` in Render Shell

**Error: `password authentication failed`**
- Check `DATABASE_URL` in environment variables
- Ensure PostgreSQL service is running

**SQLite still being used**
- Verify `DATABASE_URL` environment variable is set
- Check `config.py` has the postgres:// → postgresql:// conversion

**Data not persisting**
- Confirm you're using PostgreSQL (check logs)
- Ensure DATABASE_URL points to Render's database

---

## Cost Comparison

| Provider | Free Tier | Limit | Persistence |
|----------|-----------|-------|-------------|
| **Render** | ✅ Free | 1GB, 90 days | ✅ Yes |
| **Railway** | $5/mo credit | 1GB | ✅ Yes |
| **Supabase** | ✅ Free | 500MB | ✅ Yes |
| **Heroku** | ❌ ($5/mo) | 1GB | ✅ Yes |

**Recommendation**: Use Render's free PostgreSQL with your web service.
