# goit-pythonweb-hw-10
Master of Science (Neoversity): Fullstack Web Development with Python - Homework №10

# FastAPI Contacts App

A REST API for managing contacts, built with FastAPI, PostgreSQL, SQLAlchemy, and Alembic for migrations. Dockerized for easy setup.

---

## Prerequisites

* [Docker](https://docs.docker.com/get-docker/) installed
* [Docker Compose](https://docs.docker.com/compose/install/) installed
* `.env` file configured (example below)

### Example `.env`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=567234
POSTGRES_DB=contacts_app
POSTGRES_PORT=5432
DB_URL=postgresql+asyncpg://postgres:567234@db:5432/contacts_app

JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=3600

MAIL_USERNAME=example@meta.ua
MAIL_PASSWORD=secretPassword
MAIL_FROM=example@meta.ua
MAIL_PORT=587
```

---

## Setup & Running

1. Clone the repository:

```bash
git clone <repo-url>
cd <repo-folder>
```

2. Build and start containers:

```bash
docker-compose up --build
```

This will:

* Start PostgreSQL container
* Start FastAPI container
* Automatically run Alembic migrations (`alembic upgrade head`)
* Start the FastAPI server at `http://localhost:8000`

3. Check health:

```bash
curl http://localhost:8000/api/healthchecker
```

---

## Running Migrations Manually

If you need to create new migrations or upgrade manually:

1. Generate a new migration:

```bash
docker-compose run --rm app alembic revision --autogenerate -m "migration_name"
```

2. Apply migrations:

```bash
docker-compose run --rm app alembic upgrade head
```

---

## API Endpoints

* `/api/auth/register` → Register a new user
* `/api/auth/login` → User login
* `/api/contacts` → CRUD for contacts (requires authentication)

Use tools like [Postman](https://www.postman.com/) or [HTTPie](https://httpie.io/) to test the endpoints.

---

## Notes

* The database is persisted in a Docker volume named `postgres_data`.
* FastAPI is served with `--reload` for development purposes.
* Alembic migrations are automatically applied at container startup.
