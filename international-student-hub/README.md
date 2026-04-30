# 🇹🇼 International Student Hub — Taiwan

A full-stack, API-first web platform helping international students navigate their first weeks in Taiwan. Covers arrival checklists, a searchable service directory, university-specific tips, community Q&A, and a LINE Bot for real-time FAQ.

Built by Jason Supala | NSYSU Computer Science | 2026

---

## ✨ Features

| Feature | Status |
|---|---|
| JWT Authentication (register, login, logout, refresh) | ✅ Phase 1 |
| User profiles (country, university, arrival date) | ✅ Phase 1 |
| Arrival checklist with per-user progress tracking | ✅ Phase 1 |
| Searchable service directory (food, banks, SIM, clinics) | ✅ Phase 1 |
| LINE Bot with keyword-based FAQ responses | ✅ Phase 1 |
| React frontend consuming DRF API | ✅ Phase 1 |
| Community Q&A board with upvotes and accepted answers | 🔄 Phase 2 |
| Google Maps pins on directory entries | 🔄 Phase 2 |
| Google Sheets export for checklists | 🔄 Phase 2 |
| International student events board | 🔄 Phase 2 |
| AI-powered LINE Bot (Claude/GPT integration) | 🎯 Stretch |
| React Native mobile app | 🎯 Stretch |
| Multi-language support (ID, VI, JA, ZH) | 🎯 Stretch |
| Buddy matching for new arrivals | 🎯 Stretch |

---

## 🏗️ Architecture

**API-first design.** The Django backend serves JSON only — no HTML rendering. The React frontend and a future React Native mobile app both consume the same REST API, with no backend changes required.

```
React Frontend  ──────────┐
                           ├──► Django REST API ──► PostgreSQL
React Native (future) ────┘         │
                                     ├──► Redis (cache)
LINE Bot ────────────────────────────┤
                                     └──► Celery (async tasks)
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | Django 4.2 + DRF | Strong foundation, clean API design |
| Database | PostgreSQL 15 | Production-grade, handles real users |
| Auth | JWT (simplejwt) | Stateless, works for web and mobile |
| Cache / Queue | Redis + Celery | Async tasks (LINE replies, exports) |
| LINE Bot | LINE Messaging API | Huge in Taiwan, familiar to students |
| Frontend | React + Vite | Fast build, reusable for mobile later |
| Deployment | Docker → Railway/Render | Free tier, public URL, easy CI/CD |

---

## 🚀 Local Setup

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/international-student-hub.git
cd international-student-hub
```

### 2. Create your `.env` file

```bash
cp .env.example .env
```

Open `.env` and fill in at minimum:
- `DJANGO_SECRET_KEY` — generate one with the command below
- `LINE_CHANNEL_ACCESS_TOKEN` and `LINE_CHANNEL_SECRET` — from the LINE Developers Console

```bash
# Generate a Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Build and start all services

```bash
docker-compose up --build
```

This starts:
- **Django** at `http://localhost:8000`
- **PostgreSQL** at `localhost:5432`
- **Redis** at `localhost:6379`
- **Celery worker** (background tasks)

### 4. Create a superuser (for Django admin)

```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. Load sample data (optional)

```bash
docker-compose exec web python manage.py loaddata initial_data.json
```

### 6. Access the API

- **Django Admin:** http://localhost:8000/admin/
- **API root:** http://localhost:8000/api/v1/

---

## 📡 API Endpoint Reference

All endpoints are prefixed with `/api/v1/`.

### Authentication

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/auth/register/` | Create account, returns JWT tokens | No |
| `POST` | `/auth/login/` | Login, returns access + refresh tokens | No |
| `POST` | `/auth/logout/` | Blacklist refresh token | Yes |
| `POST` | `/auth/token/refresh/` | Exchange refresh for new access token | No |
| `POST` | `/auth/token/verify/` | Check if token is valid | No |
| `GET` | `/auth/profile/` | Get current user's profile | Yes |
| `PATCH` | `/auth/profile/` | Update profile fields | Yes |

### Checklist

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/checklist/categories/` | All categories with items + user progress | Optional |
| `GET` | `/checklist/items/` | All items; filter: `?category=<id>&university=NSYSU` | Optional |
| `GET` | `/checklist/progress/` | Current user's progress records | Yes |
| `POST` | `/checklist/progress/` | Mark item complete: `{"item": 1, "completed": true}` | Yes |
| `GET` | `/checklist/progress/summary/` | `{total, completed, percent_complete}` | Yes |

### Directory

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/directory/categories/` | All service categories | No |
| `GET` | `/directory/entries/` | All verified entries; filter: `?category__slug=sim-cards&university=NSYSU` | No |
| `GET` | `/directory/entries/?search=halal` | Full-text search | No |
| `GET` | `/directory/entries/map/` | Lightweight pin data for map; filter: `?category=sim-cards` | No |

### Community

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/community/posts/` | All posts; filter: `?university=NSYSU&search=banking` | No |
| `POST` | `/community/posts/` | Create a post | Yes |
| `GET` | `/community/posts/<id>/` | Post detail with replies | No |
| `PATCH` | `/community/posts/<id>/` | Edit own post | Yes (author) |
| `DELETE` | `/community/posts/<id>/` | Delete own post | Yes (author) |
| `POST` | `/community/posts/<id>/upvote/` | Upvote a post | Yes |
| `GET` | `/community/replies/?post=<id>` | Replies for a post | No |
| `POST` | `/community/replies/` | Create a reply | Yes |
| `POST` | `/community/replies/<id>/upvote/` | Upvote a reply | Yes |
| `POST` | `/community/replies/<id>/accept/` | Mark as accepted answer (post author only) | Yes |

### LINE Bot

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/bot/webhook/` | LINE Messaging API webhook | LINE signature |
| `GET` | `/bot/faqs/` | List FAQ entries | Admin only |
| `POST` | `/bot/faqs/` | Create FAQ entry | Admin only |
| `PATCH` | `/bot/faqs/<id>/` | Update FAQ entry | Admin only |

---

## 🔐 Authentication Flow

```
1. POST /api/v1/auth/register/  →  { access, refresh, user }
2. Store tokens in localStorage (or secure httpOnly cookie)
3. Attach to every request:  Authorization: Bearer <access_token>
4. When access token expires (401):  POST /api/v1/auth/token/refresh/
5. On logout:  POST /api/v1/auth/logout/  { refresh: <token> }
```

---

## 🤖 LINE Bot Setup

1. Go to [LINE Developers Console](https://developers.line.biz/console/)
2. Create a **Provider** → create a **Messaging API** channel
3. Under **Basic Settings**, copy the **Channel Secret** → `LINE_CHANNEL_SECRET` in `.env`
4. Under **Messaging API**, issue a **Channel Access Token** → `LINE_CHANNEL_ACCESS_TOKEN`
5. Deploy your backend to Railway/Render (needs a public HTTPS URL)
6. Set the webhook URL to: `https://your-domain.up.railway.app/api/v1/bot/webhook/`
7. Enable **Use webhook** in the LINE console
8. Add FAQ entries via Django Admin at `/admin/bot/botfaq/`

---

## 🚢 Deployment (Railway)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables
railway variables set DJANGO_SECRET_KEY="..." DJANGO_SETTINGS_MODULE="config.settings.prod" ...

# Run migrations on Railway
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

---

## 📁 Project Structure

```
international-student-hub/
├── backend/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py     # Shared settings
│   │   │   ├── dev.py      # Local development overrides
│   │   │   └── prod.py     # Production (Railway/Render)
│   │   ├── urls.py         # Root URL configuration
│   │   ├── celery.py       # Celery app instance
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/       # JWT auth, user profiles
│   │   ├── checklist/      # Arrival checklist + progress tracking
│   │   ├── directory/      # Searchable service directory
│   │   ├── community/      # Q&A board
│   │   └── bot/            # LINE Bot webhook + FAQ
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React app (separate)
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🗺️ Roadmap

### ✅ Phase 1 
- JWT auth + user profiles
- Arrival checklist with progress tracking
- Service directory with search
- LINE Bot FAQ
- React frontend deployed

### 🔄 Phase 2 
- Community Q&A board
- Google Maps on directory entries
- Google Sheets checklist export
- International student events board

### 🎯 Stretch Goals
- AI-powered LINE Bot
- React Native mobile app
- Multi-language UI (Bahasa, Vietnamese, Japanese)
- Buddy matching system
- Housing sublet board

---

## 📝 License

MIT — free to use and build on.

---

*Built for NSYSU international students, by an international student.*
