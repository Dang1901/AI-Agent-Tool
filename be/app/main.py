import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db.database import engine
from app.core.config import mask_db_url


def _mask_db_url(url: str) -> str:
    """Mask password trong DB URL khi in log."""
    try:
        scheme, rest = url.split("://", 1)
        creds, host = rest.split("@", 1)
        user, _ = creds.split(":", 1)
        return f"{scheme}://{user}:***@{host}"
    except Exception:
        return "***"


# ==== FastAPI app ====
app = FastAPI(
    title="Simple API",
    description="Simple API System",
    version="1.0.0",
)

# ==== CORS ====
allow_origins_env = os.getenv("ALLOW_ORIGINS", "http://localhost:5173")
ALLOW_ORIGINS = [o.strip() for o in allow_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==== Startup: kiểm tra DB ====
@app.on_event("startup")
async def startup_event():
    from app.core.config import DB_URL
    
    print("→ Using DATABASE_URL:", _mask_db_url(DB_URL))

    try:
        # Test kết nối trước
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        print("✅ Database connection successful.")
    except OperationalError as e:
        print("❌ Cannot connect to database. Check DATABASE_URL. Detail:", e)
        raise
    except Exception as e:
        print("❌ Failed to initialize database:", e)
        raise


# ==== Root endpoint ====
@app.get("/")
def root():
    return {"ok": True, "message": "Simple API is running", "docs": "/docs", "health": "/health"}

# ==== Health check ====
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}


# ==== Routers ====
from app.routers import env_vars, releases, audit

app.include_router(env_vars.router)
app.include_router(releases.router)
app.include_router(audit.router)