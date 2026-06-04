# ShopEasy – AI-Powered E-commerce Platform

## Overview

ShopEasy is a full-stack AI-powered e-commerce platform built using Flask, MongoDB, Next.js, and React. The application combines traditional online shopping functionality with Generative AI capabilities, enabling intelligent product discovery, personalized recommendations, and AI-driven customer assistance.

The platform provides product catalog management, user authentication, shopping carts, order processing, product reviews, product comparison, and advanced AI-powered search features using Google's Gemini API.

## Key Features

* AI-powered natural language product search
* Personalized product recommendations
* AI-generated review summarization
* Product comparison and analysis
* User authentication and account management
* Shopping cart and order management
* Responsive modern UI built with Next.js and Tailwind CSS
* RESTful backend APIs with Flask and MongoDB

## Tech Stack

### Backend

* Python
* Flask
* MongoDB (PyMongo)
* Redis
* REST APIs

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

### AI & Machine Learning

* Google Gemini API
* Recommendation Engine
* Natural Language Product Search
* Review Summarization

## Architecture

Frontend (Next.js + React)
↓
Flask REST API
↓
MongoDB Database
↓
Gemini AI Services

## Quick start (developer)

1. Create and activate a Python virtual environment, then install Python deps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run backend (development):

```powershell
python app.py
# Backend listens on http://localhost:5000 by default
```

3. Install and run frontend (from project root):

```bash
pnpm install
pnpm dev
# or with npm:
npm install
npm run dev
# Next dev server typically runs on http://localhost:3000
```

## Configuration

This project uses a `.env` file to store runtime configuration (database URI, API keys, etc.). A `.env.example` with placeholders is included at the repo root — copy it and fill in real values before running:

```powershell
copy .env.example .env
```

Important environment variables (add these to your local `.env`):

- `MONGODB_URI` — MongoDB connection string (e.g. `mongodb://localhost:27017`)
- `MONGODB_DB` — database name (default: `ecommerce`)
- `GEMINI_API_KEY` — API key for Gemini / Google generative AI (leave blank if not using AI features)
- `REDIS_URL` — Redis connection URL for caching (optional)
- `CACHE_TTL` — cache TTL in seconds (optional)
- `RATE_LIMIT` — requests per minute (optional)
- `FLASK_ENV` — e.g. `development` or `production`
- `FLASK_DEBUG` — `True`/`False`

Security notes:

- Never commit your `.env` file. Add `.env` to `.gitignore` before pushing. The included `.env.example` is safe to commit and shows required keys.
- Remove any real API keys from repo history if they were accidentally committed (use tools like `git filter-repo` or rotate the keys).

## Seeding data

- Use the provided seed utilities to populate sample products:

```powershell
python run_seed.py
# or POST to the API:
# curl -X POST http://localhost:5000/api/seed
```

## AI Features

- Natural language product search, AI-generated review summaries, and personalized recommendations are exposed under the API (see `/api/search/natural`, `/api/recommendations/<user_id>`, and review endpoints). Implementation references: `utils/ai_service.py` and `services/review_service.py`.

## Key files

- [app.py](app.py) — Flask application and API surface
- [requirements.txt](requirements.txt) — Python dependencies
- [package.json](package.json) — frontend dependencies and scripts
- [run_seed.py](run_seed.py) — seed script for sample products
- [services/search_service.py](services/search_service.py)
- [services/recommendation_service.py](services/recommendation_service.py)
- [services/review_service.py](services/review_service.py)
- [utils/ai_service.py](utils/ai_service.py)
- [app/layout.tsx](app/layout.tsx) — Next.js app layout
- [app/page.tsx](app/page.tsx) — Next.js home page
- [templates/index.html](templates/index.html) and other `templates/` pages for server-rendered views

## Next steps

- Run the backend and frontend locally, then open the site at `http://localhost:3000` (Next) or `http://localhost:5000` (Flask templates).
