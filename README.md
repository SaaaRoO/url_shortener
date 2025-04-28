Async URL Shortener 🚀
Project Description
A highly scalable, fully asynchronous URL shortener built with Django, Celery, Redis, and PostgreSQL.
Designed to efficiently handle high traffic by leveraging caching and background tasks to minimize database load.

Features ✨
Asynchronous URL shortening

🔗 Retrieve original URLs from shortened links

📈 Get URL usage statistics (click count)

🛡️ Rate limiting to prevent abuse

⚡ Caching layer using Redis

🧵 Background tasks with Celery

🐳 Full Docker support for easy setup

✨ Optimized for scalability and performance

Technologies Used 🛠
Django 4.x (Async views support)

Celery 5.x

Redis (Cache + Message broker)

PostgreSQL

Django Rest Framework (DRF)

Docker + Docker Compose

Uvicorn / Gunicorn ASGI server

Architecture Diagram 📈
+-------------+ +--------------+ +------------+ | web |<--->| redis |<--->| celery | | (Django App)| | (cache+broker)| | (worker) | +-------------+ +--------------+ +------------+ | | +-------------+ | db | | (PostgreSQL)| +-------------+

Workflow - Sequence Diagram

sequenceDiagram
    participant User
    participant API Gateway
    participant ShortenerService
    participant Cache
    participant Database
    participant CeleryWorker

    User ->> API Gateway: POST /api/shorten (original_url)
    API Gateway ->>+ ShortenerService: validate URL
    ShortenerService -->> Cache: check if URL already shortened
    alt URL already shortened
        Cache -->> ShortenerService: return existing shortened_url
    else URL not shortened
        ShortenerService ->> Database: create new shortened record
        ShortenerService ->> Cache: save shortened_url mapping
    end
    ShortenerService -->> User: shortened_url

    User ->> API Gateway: GET /api/{shortened_url}
    API Gateway ->>+ ShortenerService: fetch original_url
    ShortenerService -->> Cache: check cache
    alt found in cache
        Cache -->> ShortenerService: original_url
    else not in cache
        ShortenerService ->> Database: fetch original_url
        ShortenerService ->> Cache: save to cache
    end
    ShortenerService ->> CeleryWorker: async update click stats
    ShortenerService -->> User: redirect to original_url

    User ->> API Gateway: GET /api/stats/{shortened_url}
    API Gateway ->>+ ShortenerService: get statistics
    ShortenerService ->> Database: fetch statistics
    ShortenerService -->> User: stats data

    Note over API Gateway, ShortenerService: Rate limit checked at Gateway or View level
    Note over ShortenerService, Database: Async ORM operations

Project Structure 📂
src/ │ ├── url_shortener/ │ ├── application/ │ │ └── url_service.py # Business logic │ ├── infrastructure/ │ │ └── url_repository.py # Database and cache handling │ ├── events/ │ │ └── tasks.py # Celery background tasks │ └── views.py # Async API endpoints │ ├── config/ # Django settings ├── manage.py ├── Dockerfile ├── docker-compose.yml ├── requirements.txt └── README.md

Installation 🛠
Prerequisites
Docker and Docker Compose installed

Ports 8000, 6379, and 5432 available

Quick Start (Docker)
Clone the repository:


git clone https://github.com/your-username/async-url-shortener.git
cd async-url-shortener
Copy environment variables:


cp .env.example .env
Build and start containers:


docker-compose up --build
Django: http://localhost:8000/

Celery worker: started automatically

Redis and PostgreSQL: auto-configured

API Endpoints 🔥

Method	Endpoint	Description
POST	/api/shorten/	Shorten an original URL
GET	/api/{shortened_url}	Retrieve and redirect
GET	/api/stats/{shortened_url}	Get usage statistics
Example Requests 
Shorten a URL
Request:


POST /api/shorten/
Content-Type: application/json
{
    "original_url": "https://www.example.com"
}
Response:

{
    "shortened_url": "abc123"
}
Redirect from Shortened URL
Request:

GET /api/abc123
Redirects to https://www.example.com

URL Statistics
Request:


GET /api/stats/abc123
Response:


{
    "click_count": 10
}
Environment Variables 📜
Create a .env file based on .env.example:


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
Running Celery Worker 🚀
If you want to run manually:


docker-compose exec web celery -A config worker --loglevel=info
Caching Strategy 
Redis is checked before hitting the database.

URLs and click counters are stored temporarily in Redis for faster reads.

Heavy tasks (like updating click stats) are handled asynchronously with Celery.

Rate Limiting 
Protects APIs from abuse.

Can be enforced using Django Ratelimit or custom middleware.

Example: 100 shortenings per IP per hour.



