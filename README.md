# Async URL Shortener 🚀

## Project Description
A highly scalable, fully asynchronous URL shortener built with Django, designed to handle high traffic with low database load using caching and Celery for async processing.

---

## Features
- Shorten URLs asynchronously.
- Retrieve original URLs from shortened links.
- Get URL usage statistics.
- Rate limiting to prevent abuse.
- Caching using Redis.
- Background tasks with Celery.

---

## Diagram - Full Workflow


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


3. Docker Architecture UML

+-------------+     +--------------+     +------------+
|    web      |<--->|     redis     |<--->|   celery   |
| (Django App)|     | (cache+broker)|     | (worker)   |
+-------------+     +--------------+     +------------+
      |
      |
+-------------+
|     db      |
| (PostgreSQL)|
+-------------+
