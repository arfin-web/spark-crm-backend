# Spark CRM Backend

A FastAPI based backend for building a CRM with a PostgreSQl database. Built with FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, and PostgreSQL.

## 🚀 Key Features

* **FastAPI**: Fully asynchronous endpoints, interactive Swagger/OpenAPI docs (`/docs`).
* **SQLAlchemy 2.0**: Modern async database queries and type-safe model mappings.
* **Alembic**: Pre-configured database migration environment.
* **Pydantic v2 Settings**: Secure, validate, and parse configuration automatically from `.env` files.
* **CORS Middleware**: Pre-configured for seamless integration with frontend frameworks (like Next.js).
* **Modern Lifespan Management**: Handles clean startup/shutdown hooks for database connection pooling.

---

## 🛠️ Quick Start

Follow these steps to get the API running locally in less than 2 minutes.

### 1. Clone the repository & Navigate
```bash
git clone <your-repository-url>
cd fastapi-starter
```

### 2. Setup Virtual Environment
```bash
uv venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
uv pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template `.env` file and replace the `DATABASE_URL` with your database connection string (supporting `postgresql+asyncpg` for async capabilities):
```bash
cp .env.example .env
```

### 5. Run Database Migrations
If you've defined your models under `app/models/`, register them in `app/models/__init__.py`, then generate and run migrations:
```bash
# Generate the migration script
alembic revision --autogenerate -m "initial_migration"

# Apply migrations to the database
alembic upgrade head
```

### 6. Start the Development Server
Run the FastAPI development server:
```bash
uvicorn app.main:app --reload
```