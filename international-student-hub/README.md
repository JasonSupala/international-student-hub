# International Student Hub

A full-stack web platform that helps international students settle in Taiwan with practical arrival guidance, a service directory, community Q&A, and LINE Bot FAQ support.

Built by **Jason Supala**, Computer Science student at NSYSU.

## Why This Project

Moving to a new country creates many small but high-impact problems: finding the right government office, opening a bank account, getting a SIM card, understanding university-specific procedures, and asking questions without knowing who to ask. International Student Hub brings those workflows into one focused platform for students arriving in Taiwan.

The project is designed as an API-first product: a Django REST backend powers a React frontend, while the same backend can support integrations such as a LINE Bot or a future mobile client.

## Highlights

- JWT-based registration, login, logout, token refresh, and profile management
- Student profiles with country, university, arrival date, bio, avatar, and preferred language fields
- Personalized arrival checklist with per-user completion tracking
- Searchable service directory for essentials such as banks, clinics, food, housing, and SIM cards
- Community Q&A board with posts, replies, upvotes, and accepted answers
- LINE Bot webhook with database-managed FAQ responses
- Admin panel endpoints for managing platform content
- Markdown-powered detail pages for rich checklist and directory guidance
- Dockerized backend services for local development with PostgreSQL, Redis, and Celery

## Tech Stack

| Area | Technologies |
| --- | --- |
| Frontend | React, Vite, React Router, Axios, React Markdown |
| Backend | Django, Django REST Framework |
| Authentication | Simple JWT |
| Database | PostgreSQL |
| Async / Cache | Redis, Celery, django-redis |
| Integrations | LINE Messaging API webhook |
| Deployment-ready tooling | Docker, Gunicorn, WhiteNoise, CORS configuration |

## Product Features

### Student Accounts

Users can register, authenticate with JWT, manage their profile, and keep their student context attached to platform activity. Profiles include university and arrival data so future recommendations can be scoped to a student's situation.

### Arrival Checklist

Checklist content is organized by category and can be global or university-specific. Students can track completion progress across tasks such as immigration steps, housing, banking, and campus onboarding.

### Service Directory

The directory stores verified service entries with category, address, contact information, website, Google Maps links, tags, university targeting, and long-form Markdown descriptions. This makes the app useful as both a quick search tool and a practical guide.

### Community Q&A

Students can create posts, reply to questions, upvote useful content, and mark accepted answers. The data model supports university-scoped discussions while still allowing Taiwan-wide questions.

### LINE Bot FAQ

The backend includes a LINE webhook that checks incoming messages against active FAQ keywords stored in the database. This keeps common answers editable through admin tooling instead of hardcoding bot responses.

## Architecture

```text
React + Vite frontend
        |
        v
Django REST Framework API
        |
        +-- PostgreSQL for application data
        +-- Redis for cache and Celery broker
        +-- Celery for async tasks
        +-- LINE Messaging API webhook
```

The backend exposes versioned API routes under `/api/v1/`. Feature domains are separated into Django apps for accounts, checklist, directory, community, bot, and admin panel.

## Repository Structure

```text
international-student-hub/
|-- backend/
|   |-- apps/
|   |   |-- accounts/
|   |   |-- admin_panel/
|   |   |-- bot/
|   |   |-- checklist/
|   |   |-- community/
|   |   `-- directory/
|   |-- config/
|   |   |-- settings/
|   |   |-- urls.py
|   |   `-- celery.py
|   |-- manage.py
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- api/
|   |   |-- components/
|   |   |-- context/
|   |   |-- pages/
|   |   `-- styles/
|   |-- package.json
|   `-- vite.config.js
|-- docker-compose.yml
`-- README.md
```

## Local Development

### Backend

```powershell
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The backend runs at `http://127.0.0.1:8000`.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend usually runs at `http://localhost:5173`.

### Docker Services

From the repository root:

```powershell
docker-compose up --build
```

Use Docker when you want the backend dependencies, PostgreSQL, Redis, and Celery running together.

## Key API Areas

All backend routes are versioned under `/api/v1/`.

| Area | Example Routes |
| --- | --- |
| Auth | `/auth/register/`, `/auth/login/`, `/auth/profile/`, `/auth/token/refresh/` |
| Checklist | `/checklist/categories/`, `/checklist/items/`, `/checklist/progress/` |
| Directory | `/directory/categories/`, `/directory/entries/`, `/directory/entries/map/` |
| Community | `/community/posts/`, `/community/replies/` |
| LINE Bot | `/bot/webhook/`, `/bot/faqs/` |
| Admin Panel | `/admin-panel/` |

## Testing

Backend tests:

```powershell
cd backend
python manage.py test
```

Frontend production build:

```powershell
cd frontend
npm run build
```

## Engineering Notes

- The backend is split by domain to keep feature ownership clear.
- API permissions default to authenticated-or-read-only behavior, with stricter rules applied where needed.
- Checklist and directory detail content supports Markdown, allowing richer guidance without frontend code changes.
- Slugs are generated at the model layer for stable detail URLs.
- LINE Bot FAQ content is stored in the database so responses can be managed operationally.

## Future Improvements

- Interactive map views for directory entries
- More granular moderation tools for community posts and replies
- Multi-language UI support for international student groups
- Smarter recommendation logic based on university and arrival date
- AI-assisted FAQ responses using curated platform content

## License

MIT
