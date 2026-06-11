# Y-MONEY

A personal finance web application for tracking expenses, income, and budgets in one place.

**Stack:** Django · PostgreSQL · Redis · Nginx · Docker Compose · ASGI (uvicorn)

---

## Screenshots

| |
|---|
| TBA |
| *Dashboard — financial overview* |
| <img width="812" height="530" alt="image" src="https://github.com/user-attachments/assets/fdce9491-b812-4cc1-b286-005d9a5761dd" /> |
| *Transaction list* |
| <img width="812" height="530" alt="image" src="https://github.com/user-attachments/assets/2575f578-9f96-4578-a408-c4cf3b4d84bd" /> | 
| *Add transaction form* |
| <img width="812" height="530" alt="image" src="https://github.com/user-attachments/assets/57396f8b-2e7b-4e24-bb65-26e1190c6c8f" />|
| *Wallet list* |

---

## Running locally

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) >= 24
- [Docker Compose](https://docs.docker.com/compose/install/) >= 2.20

### 1. Clone the repository

```bash
git clone https://github.com/JedrzejSobkow/Y-MONEY.git
cd Y-MONEY
```

### 2. Configure environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and adjust:

```env
# Database
POSTGRES_DB=y_money_db
POSTGRES_USER=y_money_user
POSTGRES_PASSWORD=your_password

# Django
DJANGO_SECRET_KEY=generate_a_random_key_at_least_50_chars
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Nginx ports (optional)
NGINX_PORT=80
NGINX_SSL_PORT=443
```

> To quickly generate a `SECRET_KEY`:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(50))"
> ```

### 3. Start the application

```bash
docker compose up -d --build
```

Docker will automatically:
- start PostgreSQL and Redis,
- apply migrations (`manage.py migrate`),
- collect static files (`manage.py collectstatic`),
- start the uvicorn application server (3 workers),
- set up Nginx as a reverse proxy.

### 4. Open in your browser

```
http://localhost
```

*(or `http://localhost:NGINX_PORT` if you set a custom port)*

---

### Stopping and cleanup

```bash
# Stop containers
docker compose down

# Stop and remove volumes (warning: deletes all data)
docker compose down -v
```

### Viewing logs

```bash
docker compose logs -f app
docker compose logs -f db
```

---

## Project structure

```
Y-MONEY/
|
+-- y_money/                  # Main Django application directory
|   +-- config/               # Project configuration
|   |   +-- settings.py       # Django settings
|   |   +-- urls.py           # Root URL router
|   |   \-- asgi.py           # ASGI entry point (uvicorn)
|   |
|   +-- <app modules>/        # Individual Django apps
|   |   +-- models.py
|   |   +-- views.py
|   |   +-- urls.py
|   |   \-- templates/
|   |
|   +-- static/               # Static files (CSS, JS, images)
|   +-- templates/            # HTML templates (base, layout)
|   +-- requirements.txt      # Python dependencies
|   \-- Dockerfile            # Application container image
|
+-- .github/
|   \-- workflows/            # CI/CD configuration (GitHub Actions)
|
+-- nginx.conf                # Reverse proxy configuration
+-- docker-compose.yml        # Service orchestration
+-- .env.example              # Environment variable template
\-- README.md
```

---

## Architecture

```
Browser
     |
     v
  Nginx :80/:443          <- reverse proxy, serves static files
     |
     v
  Django / uvicorn :8000  <- application logic (3 ASGI workers)
     |           |
     v           v
PostgreSQL      Redis     <- database / cache & sessions
```

All services communicate over an isolated Docker network (`y_money_network`). Data is persisted in named volumes (`db_data`, `redis_data`, `static_volume`).

---

## Environment variables

| Variable | Description | Example |
|---|---|---|
| `POSTGRES_DB` | Database name | `y_money_db` |
| `POSTGRES_USER` | Database user | `y_money_user` |
| `POSTGRES_PASSWORD` | Database password | `secret_password` |
| `POSTGRES_HOST` | Database host (container name) | `y-money-db-1` |
| `DJANGO_SECRET_KEY` | Django cryptographic key | *(min. 50 random characters)* |
| `DEBUG` | Debug mode | `False` (production) |
| `ALLOWED_HOSTS` | Allowed hosts, comma-separated | `localhost,example.com` |
| `NGINX_PORT` | Nginx HTTP port | `80` |
| `NGINX_SSL_PORT` | Nginx HTTPS port | `443` |

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python · Django |
| ASGI server | uvicorn |
| Database | PostgreSQL 16 |
| Cache / sessions | Redis 7 |
| Reverse proxy | Nginx (Alpine) |
| Containerization | Docker · Docker Compose |
| Frontend | HTML · CSS (Django templates) |
| CI/CD | GitHub Actions |
