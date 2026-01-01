# AI-Powered Learning Platform

A complete full-stack application that creates personalized learning journeys using AI and web scraping.

## Features

- 🤖 AI-powered chat interface for understanding learning goals
- 🔍 Intelligent web scraping from multiple sources
- 📚 Automated resource curation and organization
- 🎯 Personalized learning paths based on skill level
- 💾 Dual database architecture (MySQL + MongoDB)
- 🎨 Modern, mobile-first responsive UI with dark mode
- 📱 Progressive Web App (PWA) support for offline use
- ⚡ Auto-initialized database on backend startup

## Architecture

### Backend
- **Framework**: FastAPI (Python)
- **Databases**: MySQL (metadata) + MongoDB (content)
- **AI**: Custom LLM endpoint integration
- **Scraping**: DuckDuckGo, Bing API, BeautifulSoup, Playwright
- **Architecture**: Clean architecture with DAO → Service → Router layers

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **State**: Zustand

## Quick Start

### Backend Setup

The backend automatically initializes the database on startup. Just run:

```bash
cd backend
pip install -r requirements.txt
# Database will be auto-initialized on server start
uvicorn app.main:app --reload
```

**Note**: Make sure the MySQL database exists. If you need to create it manually, use:
```bash
python init_db_manual.py  # Optional: creates database if it doesn't exist
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

**PWA Icons**: For full PWA functionality, add icon files to `frontend/public/`:
- `icon-192.png` (192x192)
- `icon-512.png` (512x512)

Or run: `npx pwa-asset-generator logo.svg public`

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── db/                     # Database connections
│   ├── api/v1/
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   └── dao/               # Data access objects
│   ├── agents/                # AI agents
│   ├── scraping/              # Web scraping logic
│   └── utils/                 # Utilities

frontend/
├── app/
│   ├── page.tsx              # Home page
│   ├── chat/                 # Chat interface
│   ├── journey/              # Journey pages
│   ├── components/           # React components
│   └── services/             # API client
```

## API Endpoints

- `POST /api/v1/user/register` - Register user
- `POST /api/v1/user/login` - Login
- `POST /api/v1/chat/start` - Start chat
- `POST /api/v1/chat/respond` - Respond to chat
- `GET /api/v1/journey/{id}` - Get journey
- `GET /api/v1/journey/` - List user journeys

## Configuration

Update database connections in `backend/app/config.py`:
- MySQL: Connection string
- MongoDB: Connection string
- AI Endpoint: LLM API endpoint

## License

MIT

