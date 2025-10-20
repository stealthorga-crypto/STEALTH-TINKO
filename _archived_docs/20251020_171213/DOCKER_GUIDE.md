# Docker Development Setup Guide

## Quick Start

Start all services (backend, frontend, database, redis, mailhog):

```bash
docker compose up
```

Access services:

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **MailHog UI**: http://localhost:8025 (email testing)
- **PostgreSQL**: localhost:5432 (user: postgres, password: postgres)
- **Redis**: localhost:6379

## Services

### Backend (FastAPI)

- Port: 8000
- Auto-runs migrations on startup
- Hot-reload enabled in development
- Volume-mounted for live code changes

### Frontend (Next.js)

- Port: 3000
- Production build with standalone output
- Connects to backend at http://localhost:8000

### Database (PostgreSQL)

- Port: 5432
- Persistent storage via Docker volume
- Healthcheck ensures backend waits for DB

### Redis

- Port: 6379
- For caching and background jobs (future use)

### MailHog

- SMTP: Port 1025
- Web UI: Port 8025
- Captures all emails sent by backend

## Commands

```bash
# Start all services in detached mode
docker compose up -d

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f backend

# Stop all services
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v

# Rebuild containers after code changes
docker compose up --build

# Run backend tests
docker compose exec backend pytest

# Access backend shell
docker compose exec backend bash

# Access database shell
docker compose exec db psql -U postgres -d stealth_recovery
```

## Development Workflow

1. **Code changes** are reflected immediately:

   - Backend: Uvicorn auto-reloads on file changes
   - Frontend: Requires rebuild (`docker compose up --build frontend`)

2. **Database migrations**:

   ```bash
   # Create new migration
   docker compose exec backend alembic revision -m "description"

   # Apply migrations
   docker compose exec backend alembic upgrade head
   ```

3. **Testing emails**:
   - Open http://localhost:8025
   - All emails sent by backend appear in MailHog UI

## Production Configuration

For production deployment, update `docker-compose.yml`:

1. Change `JWT_SECRET` to a secure random string
2. Update database password
3. Remove volume mounts (use built-in code)
4. Set `NODE_ENV=production` for frontend
5. Add reverse proxy (nginx/traefik) for HTTPS

## Troubleshooting

**Backend won't start:**

- Check DB health: `docker compose ps`
- View logs: `docker compose logs backend`
- Ensure port 8000 is available

**Frontend build fails:**

- Check Node version (requires 20+)
- Clear build cache: `docker compose build --no-cache frontend`

**Database connection errors:**

- Verify PostgreSQL is running: `docker compose ps db`
- Check DATABASE_URL environment variable

**Port conflicts:**

- Edit ports in `docker-compose.yml` if 3000/8000/5432 are in use
