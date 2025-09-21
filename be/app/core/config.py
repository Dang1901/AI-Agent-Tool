import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==== Security ====
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
ENCRYPTION_MASTER_KEY = os.getenv("ENCRYPTION_MASTER_KEY", "encryption-master-key-for-development-only")

# ==== Database URL ====
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    # Default to local PostgreSQL database
    DB_URL = "postgresql://postgres:password@localhost:5432/test_env"

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
