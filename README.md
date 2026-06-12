# Task Manager API — FastAPI

Python/FastAPI port of the Node.js Task Manager backend.  
Same routes, same response shapes, same role-based logic.

## Stack

| Layer | Library |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2 (async) |
| Database | PostgreSQL (asyncpg driver) |
| Migrations | Alembic |
| Auth | python-jose (JWT) + passlib (bcrypt) |
| Validation | Pydantic v2 |
| Rate limiting | slowapi |

## Project layout

```
task-manager-api/
├── app/
│   ├── core/
│   │   ├── config.py       # Settings from .env
│   │   ├── database.py     # Async engine + Base + get_db
│   │   ├── exceptions.py   # HTTP exception classes
│   │   └── jwt.py          # Token generation + verification
│   ├── middleware/
│   │   └── auth.py         # get_current_user, require_role()
│   ├── models/
│   │   ├── user.py
│   │   └── task.py
│   ├── routers/
│   │   ├── auth.py         # /api/v1/auth/*
│   │   ├── tasks.py        # /api/v1/tasks/*
│   │   └── admin.py        # /api/v1/admin/*
│   ├── schemas/            # Pydantic request/response models
│   └── main.py             # App factory + middleware setup
├── alembic/                # Migrations
├── requirements.txt
└── .env.example
```

## Setup

```bash
# 1. Clone & create venv
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — at minimum set DB_PASSWORD, JWT_SECRET, JWT_REFRESH_SECRET

# 4. Run migrations
alembic upgrade head

# 5. (Optional) Seed dev users
python seed.py

# 6. Start server
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

All routes are under `/api/v1`.

### Auth  `/api/v1/auth`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/register` | Public | Register new user |
| POST | `/login` | Public | Login, returns tokens |
| POST | `/refresh` | Public | Get new access token |
| GET | `/me` | Bearer | Current user profile |

### Tasks  `/api/v1/tasks`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/` | Bearer | Create task |
| GET | `/` | Bearer | List tasks (own / all for admin) |
| GET | `/:id` | Bearer | Get task by ID |
| PATCH | `/:id` | Bearer | Update task |
| DELETE | `/:id` | Bearer | Delete task |

Query params for `GET /`: `status`, `priority`, `page`, `limit`, `userId` (admin only).

### Admin  `/api/v1/admin`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/users` | Admin | List all users (paginated) |
| PATCH | `/users/:id/role` | Admin | Update user role |

### Other

| Path | Description |
|---|---|
| `GET /health` | Health check |
| `GET /api-docs` | Swagger UI |
| `GET /api-redoc` | ReDoc |

## Token usage

```
Authorization: Bearer <access_token>
```

Access token expires after `JWT_EXPIRES_IN` days (default 1).  
Use `POST /auth/refresh` with your `refresh_token` to get a new one.
