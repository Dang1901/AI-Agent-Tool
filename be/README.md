# IAM System Backend

Identity and Access Management System with RBAC and ABAC.

## Features

- **Authentication** (Login/Logout with JWT)
- **User Management** (List all users with auto-sync)
- **RBAC** (Roles & Permissions management)
- **ABAC** (Policies management)
- **Search & Filter** with pagination
- **Auto-refresh** every 30 seconds

## API Endpoints

- `GET /health` - Health check
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user
- `GET /users` - List all users
- `GET /roles` - List roles
- `GET /permissions` - List permissions
- `GET /policies` - List policies

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `ENVIRONMENT` - Environment (staging/production)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload
```

## Railway Deployment

This app is configured for Railway deployment with:
- Automatic database provisioning
- Health checks
- Auto-restart on failure
- Environment variable management