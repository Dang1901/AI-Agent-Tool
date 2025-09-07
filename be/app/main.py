import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db.database import engine          # engine phải được tạo từ ENV trong app.db.database
from app.db import Base                     # import để SQLAlchemy biết model
from app.model import user, feature as feature_model, rbac as rbac_model, abac as abac_model
from app.routers import auth, feature, rbac, abac
from app.routers import user as user_router
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
    title="IAM System API",
    description="Identity and Access Management System with RBAC and ABAC",
    version="1.0.0",
)

# ==== CORS ====
# Có thể set ALLOW_ORIGINS="http://localhost:5173,https://your-frontend.app" trên Railway
allow_origins_env = os.getenv("ALLOW_ORIGINS", "http://localhost:5173")
ALLOW_ORIGINS = [o.strip() for o in allow_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==== Startup: kiểm tra DB + tạo bảng (nếu chưa dùng Alembic) ====
@app.on_event("startup")
async def startup_event():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Crash sớm để biết chắc đang thiếu biến môi trường
        raise RuntimeError("DATABASE_URL is not set. Please configure it in Railway Variables.")

    print("→ Using DATABASE_URL:", _mask_db_url(db_url))

    try:
        # Test kết nối trước
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # Nếu chưa dùng Alembic, giữ create_all; nếu có Alembic thì bỏ dòng dưới
        Base.metadata.create_all(bind=engine)
        print("✅ Database ready, tables ensured.")
    except OperationalError as e:
        # Trường hợp hay gặp: vẫn trỏ localhost khi chạy trên Railway
        print("❌ Cannot connect to database. Check DATABASE_URL. Detail:", e)
        raise
    except Exception as e:
        print("❌ Failed to initialize database:", e)
        raise


# ==== Root endpoint ====
@app.get("/")
def root():
    return {"ok": True, "message": "IAM System API is running", "docs": "/docs", "health": "/health"}

# ==== Health check ====
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}


# ==== Routers ====
app.include_router(auth.router)
app.include_router(user_router.router)
app.include_router(feature.router)
app.include_router(rbac.router)
app.include_router(abac.router)