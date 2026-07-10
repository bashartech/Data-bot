# Enterprise AI Chatbot

A production-ready enterprise chatbot built with **FastAPI**, **OpenAI Agents SDK** (with **Groq**), **Next.js 16**, **Shadcn UI**, and **Neon PostgreSQL**. Employees authenticate via Google Workspace SSO and chat with an AI assistant that answers questions about products stored in PostgreSQL.

## Architecture

```
frontend/          Next.js 16 + TypeScript + TailwindCSS v4 + Shadcn UI (base-nova)
       ↕ HTTP / SSE
backend/           FastAPI + Python 3.12+
  ├── config/      Settings (pydantic-settings), Logging (structlog)
  ├── database/    SQLAlchemy async engine, session factory, seed data
  ├── models/      ORM models (User, AllowedUser, Product, ProductDetail, Conversation, Message)
  ├── repositories/Data access layer (UserRepo, ProductRepo, ConversationRepo, AllowedUserRepo)
  ├── services/    Business logic (ChatService)
  ├── api/         FastAPI routers (chat, conversations, products)
  ├── auth/        JWT auth, Google OAuth, session management, FastAPI dependencies
  ├── ai/          ModelProvider abstraction, Groq client, Agent, Tools
  └── alembic/     Database migrations
       ↕ SQLAlchemy (async)
Neon PostgreSQL
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | FastAPI |
| AI SDK | OpenAI Agents SDK (`openai-agents>=0.0.7`) |
| LLM Provider | Groq (OpenAI-compatible API) |
| Database | Neon PostgreSQL (async via asyncpg) |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Auth | Google OAuth 2.0 + JWT (python-jose) + email allowlist |
| Frontend | Next.js 16, TypeScript, TailwindCSS v4 |
| UI Library | Shadcn UI (base-nova style, @base-ui/react primitives) |
| Streaming | Server-Sent Events (SSE) |

## Features

- **Google Workspace SSO** — authenticate with corporate Google accounts
- **Email Allowlist Auth** — restrict access to specific users
- **AI Chat** — streaming responses via Groq LLM
- **Product Knowledge** — agent queries PostgreSQL for product data
- **Conversation Management** — multiple chats, history, rename, delete
- **Dark Mode** — light/dark theme toggle
- **Responsive** — mobile sidebar with slide-out sheet
- **Markdown Rendering** — AI responses render formatted markdown
- **Clean Architecture** — API → Service → Repository → Model separation

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- Neon PostgreSQL database
- Groq API key
- Google Cloud Console OAuth 2.0 credentials

### 1. Clone and Install Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate     # Windows
pip install -e .
```

### 2. Configure Environment

Copy the `.env` files and fill in your secrets:

```env
# backend/.env
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=openai/gpt-oss-120b
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=2048

NEON_DATABASE_URL=postgresql://user:pass@host/neondb?sslmode=require

GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret

AUTH_MODE=allowlist
AUTH_REDIRECT_URI=http://localhost:8000/auth/callback

SESSION_SECRET_KEY=change-me-in-production
SESSION_EXPIRY_MINUTES=60

CORS_ORIGIN_STRING=http://localhost:3001
```

### 3. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Seed the Database

```bash
cd backend
python database/seed_runner.py
```

### 5. Start the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API available at `http://localhost:8000/docs`

### 6. Install and Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at `http://localhost:3001`

### 7. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create an OAuth 2.0 Client ID (Web application)
3. Add **Authorized redirect URI**: `http://localhost:8000/auth/callback`
4. Add **Authorized JavaScript origins**: `http://localhost:3001`, `http://localhost:8000`
5. Copy `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to `.env`

## API Reference

### Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/login` | No | Email allowlist login `{ "email": "..." }` |
| GET | `/auth/login` | No | Google SSO redirect |
| GET | `/auth/callback` | No | Google OAuth callback |
| GET | `/auth/me` | Yes | Current user profile |
| POST | `/auth/logout` | Yes | Logout |

### Chat & Conversations

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/chat` | Yes | Streaming chat `{ "message": "...", "conversation_id": null }` |
| GET | `/conversations` | Yes | List conversations |
| POST | `/conversations` | Yes | Create conversation |
| GET | `/conversations/{id}` | Yes | Get conversation |
| PATCH | `/conversations/{id}` | Yes | Rename conversation `{ "title": "..." }` |
| DELETE | `/conversations/{id}` | Yes | Delete conversation |
| GET | `/conversations/{id}/messages` | Yes | Get messages |

### Products

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/products` | Yes | List products (`?skip=0&limit=20`) |
| GET | `/products/search` | Yes | Search products (`?q=laptop&limit=10`) |
| GET | `/products/{id}` | Yes | Get product with details |

### Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |

## Project Structure

```
.
├── .env
├── details.md              # Full project specification
├── README.md
├── backend/
│   ├── main.py             # FastAPI entry point
│   ├── pyproject.toml      # Python dependencies
│   ├── middleware.py        # Request ID, security headers, error handler
│   ├── config/
│   │   ├── settings.py     # pydantic-settings
│   │   └── logging.py      # structlog
│   ├── database/
│   │   ├── base.py         # DeclarativeBase
│   │   ├── engine.py       # Async engine + session
│   │   ├── seed.py         # Seed data
│   │   └── seed_runner.py
│   ├── models/             # SQLAlchemy ORM models
│   ├── repositories/       # Data access layer
│   ├── services/           # Business logic
│   ├── api/                # FastAPI routers
│   ├── auth/               # JWT + Google OAuth
│   ├── ai/                 # ModelProvider + Agent + Tools
│   └── alembic/            # Database migrations
└── frontend/
    ├── package.json
    ├── components.json      # Shadcn config
    └── src/
        ├── lib/
        │   ├── utils.ts     # cn() helper
        │   ├── api.ts       # API client
        │   └── auth-context.tsx
        ├── components/
        │   ├── ui/          # Shadcn components
        │   └── theme-provider.tsx
        └── app/
            ├── globals.css
            ├── layout.tsx
            ├── page.tsx
            └── auth/callback/page.tsx
```

## AI Agent Tools

The LLM never executes SQL directly. It uses typed tools:

| Tool | Description |
|------|-------------|
| `get_product_by_name(name)` | Look up a product by name |
| `get_product_price(name)` | Get the price of a specific product |
| `get_product_details(name)` | Get full specifications |
| `list_products(category?)` | List all products, optionally filtered |
| `search_products(query)` | Search across name, description, category, manufacturer |

## ModelProvider Abstraction

Switch LLM providers with minimal changes:

```python
# Current: Groq
class GroqModelProvider(ModelProvider):
    def __init__(self):
        self._provider = OpenAIProvider(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.groq_api_key,
        )

# Future: Any OpenAI-compatible provider
class OtherModelProvider(ModelProvider):
    def __init__(self):
        self._provider = OpenAIProvider(
            base_url="https://api.other.com/v1",
            api_key=settings.other_api_key,
        )
```

Only the provider class and `.env` config change — agent code stays the same.

## Authentication Flow

```
[Login with Google] → GET /auth/login
  → redirect to Google consent screen
  → user authorizes → redirect to /auth/callback?code=...
  → exchange code → verify Google ID token
  → check allowlist/domain → upsert user in DB
  → generate JWT → redirect to frontend?token=JWT
  → frontend stores JWT in localStorage
  → all subsequent requests include Authorization: Bearer <token>
```

## Development Rules

- No placeholder implementations — every phase produces working code
- No mock APIs — always integrate with real services
- After every phase, verify both projects build/start
- Clean Architecture: API → Service → Repository → Model
- Never expose raw SQL to the LLM

## License

Private — Enterprise use
