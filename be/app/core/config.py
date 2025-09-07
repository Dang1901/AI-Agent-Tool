import os
from dotenv import load_dotenv

# Optional: chỉ load .env khi không phải production (Railway không cần .env)
ENV = os.getenv("ENV", "development").lower()
if ENV != "production":
    load_dotenv()

# ==== Security ====
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")  # nhớ đặt trên Railway
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# ==== Database URL ====
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    if ENV == "development":
        # Chỉ fallback khi DEV local
        DB_URL = os.getenv(
            "DEV_DATABASE_URL",
            "postgresql://postgres:190123@localhost:5432/myapp",
        )
    else:
        # Trên Railway/production: bắt buộc phải có, để tránh trỏ nhầm localhost
        raise RuntimeError("DATABASE_URL is not set. Configure it in Railway Variables.")

def mask_db_url(url: str) -> str:
    try:
        scheme, rest = url.split("://", 1)
        creds, host = rest.split("@", 1)
        user, _ = creds.split(":", 1)
        return f"{scheme}://{user}:***@{host}"
    except Exception:
        return "***"

# Log gọn để debug, KHÔNG lộ mật khẩu
print("🔍 DATABASE_URL =", mask_db_url(DB_URL))
