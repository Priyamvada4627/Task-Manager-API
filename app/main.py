from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.routers import auth, tasks, admin

# ── Rate limiter ──────────────────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_MAX}/15minute"],
)

# ── App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    description="FastAPI port of the Task Manager Node.js backend",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Validation error handler (mirrors JS 400 responses) ──────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(l) for l in e["loc"]), "message": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"status": "fail", "message": "Validation error", "errors": errors},
    )


# ── Health check ──────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    from datetime import datetime, timezone
    return {"status": "success", "message": "API is healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


# ── API v1 routes ─────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
# ── Serve frontend ────────────────────────────────────────────────
import pathlib
_frontend = pathlib.Path(__file__).parent.parent / "frontend"
if _frontend.exists():
    app.mount("/", StaticFiles(directory=str(_frontend), html=True), name="frontend")
