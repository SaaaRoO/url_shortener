# Async URL Shortener 🚀

A **highly scalable**, fully **asynchronous URL shortener** built with **Django**, **Celery**, **Redis**, and **PostgreSQL**.  
Designed to efficiently handle high traffic using caching and background tasks to minimize database load and optimize performance.

---

## Features ✨

- ⚡ Asynchronous URL shortening
- 🔗 Retrieve original URLs from shortened links
- 📈 Track URL usage statistics (click counts)
- 🛡️ Rate limiting to prevent abuse
- 🚀 Caching layer using Redis
- 🧅 Background tasks with Celery
- 🐳 Full Docker support for easy setup
- 📈 Optimized for scalability and performance

---

## Technologies Used 🛠

- Django 4.x (Async views support)
- Django REST Framework (DRF)
- Celery 5.x
- Redis (Cache + Message Broker)
- PostgreSQL
- Uvicorn / Gunicorn (ASGI Servers)
- Docker + Docker Compose

---

## Architecture Diagram 📈

```plaintext
+-------------+    +--------------+    +------------+
|   Web App   |<-->|     Redis     |<-->|   Celery    |
| (Django App)|    |(Cache+Broker) |    |  (Worker)   |
+-------------+    +--------------+    +------------+
       |
       v
+-------------+
|    DB       |
| (PostgreSQL)|
+-------------+
```

---

## Workflow - Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant API Gateway
    participant ShortenerService
    participant Cache
    participant Database
    participant CeleryWorker

    User ->> API Gateway: POST /api/shorten (original_url)
    API Gateway ->>+ ShortenerService: Validate URL
    ShortenerService -->> Cache: Check if URL already shortened
    alt URL already shortened
        Cache -->> ShortenerService: Return existing shortened_url
    else URL not shortened
        ShortenerService ->> Database: Create new shortened record
        ShortenerService ->> Cache: Save shortened_url mapping
    end
    ShortenerService -->> User: shortened_url

    User ->> API Gateway: GET /api/{shortened_url}
    API Gateway ->>+ ShortenerService: Fetch original_url
    ShortenerService -->> Cache: Check cache
    alt Found in cache
        Cache -->> ShortenerService: Return original_url
    else Not found in cache
        ShortenerService ->> Database: Fetch original_url
        ShortenerService ->> Cache: Save to cache
    end
    ShortenerService ->> CeleryWorker: Async update click stats
    ShortenerService -->> User: Redirect to original_url

    User ->> API Gateway: GET /api/stats/{shortened_url}
    API Gateway ->>+ ShortenerService: Get statistics
    ShortenerService ->> Database: Fetch statistics
    ShortenerService -->> User: Stats data

    Note over API Gateway, ShortenerService: Rate limiting enforced at Gateway/View
    Note over ShortenerService, Database: Async ORM operations used

```

---

## Project Structure 📂

```bash
src/
├── url_shortener/
│   ├── application/
│   │   └── url_service.py       # Business logic
│   ├── infrastructure/
│   │   └── url_repository.py    # Database and cache handling
│   ├── events/
│   │   └── tasks.py             # Celery background tasks
│   └── views.py                  # Async API endpoints
├── config/                             # Django settings
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Installation 🛠

### Prerequisites

- Docker and Docker Compose installed
- Ports `8000`, `6379`, and `5432` available

### Quick Start (Docker)

Clone the repository:

```bash
git clone https://github.com/your-username/async-url-shortener.git
cd async-url-shortener
```

Copy environment variables:

```bash
cp .env.example .env
```

Build and start containers:

```bash
docker-compose up --build
```

Access:

- Django App: [http://localhost:8000/](http://localhost:8000/)
- Celery Worker: Started automatically
- Redis and PostgreSQL: Auto-configured

---

## API Endpoints 🔥

| Method | Endpoint | Description |
|:------:|:--------:|:-----------:|
| POST | `/api/shorten/` | Shorten an original URL |
| GET  | `/api/{shortened_url}` | Retrieve and redirect |
| GET  | `/api/stats/{shortened_url}` | Get usage statistics |

---

## Example Requests

### Shorten a URL

**Request:**
```http
POST /api/shorten/
Content-Type: application/json
{
    "original_url": "https://www.example.com"
}
```

**Response:**
```json
{
    "shortened_url": "abc123"
}
```

### Redirect from Shortened URL

**Request:**
```http
GET /api/abc123
```

**Behavior:** Redirects to `https://www.example.com`

### URL Statistics

**Request:**
```http
GET /api/stats/abc123
```

**Response:**
```json
{
    "click_count": 10
}
```

---

## Environment Variables 📜

Create a `.env` file based on `.env.example`:

```bash
# PostgreSQL settings
POSTGRES_DB=url_shortener_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Django settings
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1
```

---

## Running Celery Worker 🚀

If you want to run it manually:

```bash
docker-compose exec web celery -A config worker --loglevel=info
```

---

## Caching Strategy

- Redis is checked before hitting the database.
- URLs and click counters are cached in Redis for faster reads.
- Heavy operations (like updating click stats) are handled asynchronously with Celery.

---

## Rate Limiting

- Protects APIs from abuse.
- Can be enforced using Django Ratelimit or custom middleware.
- Example: Allow max 100 shortenings per IP per hour.

---

> **Made with ❤️ for high performance and scalability.**

