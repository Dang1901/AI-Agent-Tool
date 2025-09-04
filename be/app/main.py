from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
from app.routers import auth, feature, rbac, abac
from app.routers import user as user_router

# Import models to register them with SQLAlchemy
from app.db import Base
from app.model import user, feature as feature_model, rbac as rbac_model, abac as abac_model

# Create tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="IAM System API",
    description="Identity and Access Management System with RBAC and ABAC",
    version="1.0.0"
)


# Allow frontend (Vite, localhost)
app.add_middleware(
CORSMiddleware,
allow_origins=["http://localhost:5173"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

# Include routers
app.include_router(auth.router)
app.include_router(user_router.router)
app.include_router(feature.router)
app.include_router(rbac.router)
app.include_router(abac.router)