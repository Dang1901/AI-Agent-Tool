# 🚀 Quick Start Guide

## Cài đặt nhanh

### 1. Backend Setup

```bash
cd be

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình database
cp env.example .env
# Chỉnh sửa .env với thông tin database

# Chạy migrations
alembic upgrade head

# Khởi động server
python -m app
```

### 2. Frontend Setup

```bash
cd fe

# Cài đặt dependencies
npm install

# Khởi động development server
npm run dev
```

### 3. Truy cập ứng dụng

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Cấu hình cơ bản

### Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://admin:password@localhost:5432/env_vars_db
ENCRYPTION_KEY=your-32-byte-encryption-key
SECRET_KEY=your-secret-key
DEBUG=True

# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8000
```

### Database Setup

```sql
-- Tạo database
CREATE DATABASE env_vars_db;

-- Tạo user
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE env_vars_db TO admin;
```

## 🎯 Sử dụng cơ bản

### 1. Tạo biến môi trường

1. Truy cập http://localhost:3000
2. Đăng nhập với tài khoản admin
3. Vào **Environment Variables**
4. Click **Create**
5. Điền thông tin:
   - **Key**: `DATABASE_URL`
   - **Value**: `postgres://user:pass@host:5432/db`
   - **Type**: `STRING`
   - **Scope**: `GLOBAL`
   - **Tags**: `database, production`

### 2. Tạo Release

1. Vào **Releases**
2. Click **Create Release**
3. Điền thông tin:
   - **Service ID**: `my-service`
   - **Environment**: `production`
   - **Title**: `Database Configuration Update`
   - **Description**: `Updated database credentials`

### 3. Approve và Apply Release

1. Click **Approve** trên release
2. Click **Apply** để deploy
3. Xem kết quả trong **Audit Log**

### 4. Xem Logs

1. Vào **API Logs**
2. Xem real-time API calls
3. Click vào log để xem chi tiết

## 🐛 Troubleshooting

### Lỗi thường gặp

#### 1. Database connection failed
```bash
# Kiểm tra PostgreSQL đang chạy
sudo systemctl status postgresql

# Kiểm tra connection
psql -h localhost -U admin -d env_vars_db
```

#### 2. Frontend không kết nối được backend
```bash
# Kiểm tra backend đang chạy
curl http://localhost:8000/health

# Kiểm tra CORS settings
```

#### 3. Encryption key error
```bash
# Tạo encryption key mới
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 📚 Tài liệu chi tiết

- [README.md](README.md) - Hướng dẫn đầy đủ
- [ARCHITECTURE.md](ARCHITECTURE.md) - Kiến trúc hệ thống
- [API Documentation](http://localhost:8000/docs) - API docs

## 🆘 Hỗ trợ

Nếu gặp vấn đề, hãy kiểm tra:

1. **Logs Console** tại `/logs`
2. **Backend logs** trong terminal
3. **Database logs** trong PostgreSQL
4. **Network tab** trong browser dev tools

---

**Lưu ý**: Đây là hướng dẫn setup cho development. Để deploy production, hãy tham khảo [README.md](README.md) để biết thêm chi tiết về bảo mật và cấu hình.
