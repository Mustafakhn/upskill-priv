# AI Learning Platform - Backend

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create MySQL database (if not exists):
```sql
CREATE DATABASE learning_platform;
```

Or use the helper script:
```bash
python init_db_manual.py
```

3. Create environment file:

```bash
# Copy the example file
cp .env.example .env
```

   Or create `.env` manually. See `.env.example` for all available variables.

4. Update `.env` with your configuration:
   - Database URLs (MySQL and MongoDB)
   - AI endpoint
   - Secret keys (CHANGE IN PRODUCTION!)
   - Free journeys limit (default: 5)
   - Optional API keys for search providers

5. Run the server (database will auto-initialize on startup):
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The database tables will be automatically created when the server starts.

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

The backend uses environment variables from a `.env` file. Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

Key variables:
- `MYSQL_URL`: MySQL database connection string
- `MONGODB_URL`: MongoDB connection string
- `AI_ENDPOINT`: AI service endpoint URL
- `SECRET_KEY`: JWT secret key (CHANGE IN PRODUCTION!)
- `REFRESH_SECRET_KEY`: JWT refresh token secret (CHANGE IN PRODUCTION!)
- `FREE_JOURNEYS_LIMIT`: Number of free journeys per user (default: 5)
- `SERPAPI_KEY`, `BING_API_KEY`, `GOOGLE_CSE_API_KEY`: Optional search provider API keys

All variables have defaults in `app/config.py`, but you should override them in `.env` for production.

## Background Tasks

The platform uses background tasks for scraping. For production, consider using:
- Celery with Redis/RabbitMQ
- Or another task queue system

Currently, it uses threading for background processing.

## Database Schema

### MySQL Tables
- `users`: User accounts
- `journeys`: Learning journeys
- `journey_resources`: Links between journeys and resources

### MongoDB Collections
- `resources`: Scraped and curated learning resources
- `raw_scrapes`: Raw HTML content from scraped pages

