# ShopEasy – AI-Powered E-commerce Platform

## Overview

ShopEasy is a full-stack AI-powered e-commerce platform built using Flask, MongoDB, Next.js, and React. The platform combines traditional online shopping functionality with Generative AI capabilities, enabling intelligent product discovery, personalized recommendations, AI-generated recommendation explanations, and review summarization using Google's Gemini API.

The application provides product catalog management, user authentication, shopping carts, order processing, product reviews, product comparison, and AI-enhanced search functionality through a modern responsive interface.

---

## Key Features

* AI-powered natural language product search
* Personalized product recommendations
* AI-generated recommendation explanations
* AI-powered review summarization
* Product comparison and analysis
* User authentication and account management
* Shopping cart and order management
* Responsive UI built with Next.js and Tailwind CSS
* RESTful backend APIs with Flask and MongoDB

---

## Application Screenshots

### Login Page

![Login](https://github.com/AyushJha004/ShopEasy-AI-Ecommerce/blob/6e89e4ab5e7fcc88a4b1714beb8a49091ad30a68/login.png)

### Product Catalog

![Catalog](https://github.com/AyushJha004/ShopEasy-AI-Ecommerce/blob/6e89e4ab5e7fcc88a4b1714beb8a49091ad30a68/catalog.png)

### Product Details

![Product Details](https://github.com/AyushJha004/ShopEasy-AI-Ecommerce/blob/6e89e4ab5e7fcc88a4b1714beb8a49091ad30a68/product-details.png)

### Shopping Cart

![Cart](https://github.com/AyushJha004/ShopEasy-AI-Ecommerce/blob/6e89e4ab5e7fcc88a4b1714beb8a49091ad30a68/cart.png)

### Customer Reviews

![Reviews](https://github.com/AyushJha004/ShopEasy-AI-Ecommerce/blob/6e89e4ab5e7fcc88a4b1714beb8a49091ad30a68/reviews.png)

---

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
* Natural Language Product Search
* Recommendation Engine
* Review Summarization

---

## Architecture

```text
Next.js + React Frontend
          ↓
      Flask API
          ↓
MongoDB Database
          ↓
 Gemini AI Services
```

---

## Quick Start

### 1. Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run Backend

```powershell
python app.py
```

Backend runs on:

```text
http://localhost:5000
```

### 3. Run Frontend

```bash
pnpm install
pnpm dev
```

or

```bash
npm install
npm run dev
```

Frontend runs on:

```text
http://localhost:3000
```

---

## Configuration

Create a local environment file:

```powershell
copy .env.example .env
```

Configure:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=ecommerce
GEMINI_API_KEY=your_gemini_api_key
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

### Important Note

AI-powered search, recommendation explanations, and review summarization require a valid Gemini API key configured through the `GEMINI_API_KEY` environment variable.

For security reasons, API keys are not included in this repository.

---

## Database Setup

Populate sample products:

```powershell
python run_seed.py
```

or

```bash
curl -X POST http://localhost:5000/api/seed
```

---

## AI Features

### Natural Language Search

Example:

```text
gaming laptop under 50000
```

The query is processed using Gemini and converted into structured search filters before retrieving matching products from MongoDB.

### Personalized Recommendations

Recommendations are generated based on user interactions and purchase history, with Gemini providing human-readable recommendation explanations.

### Review Summarization

Customer reviews can be summarized using Gemini-powered text generation to provide concise product insights.

---

## Project Structure

```text
app.py
services/
├── search_service.py
├── recommendation_service.py
├── review_service.py

utils/
├── ai_service.py
├── cache.py

app/
├── layout.tsx
├── page.tsx

templates/
static/
tests/
```

---

## Security

* `.env` is excluded from version control
* API keys are stored using environment variables
* `.env.example` provides safe configuration templates
* Sensitive credentials should never be committed to GitHub

---

## Future Improvements

* Conversational AI shopping assistant
* Advanced recommendation algorithms
* User behavior analytics
* Multi-agent shopping workflows
* Cloud deployment and monitoring
