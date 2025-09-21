"""
Audit endpoints for environment variable management
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.db.database import get_db
from app.model.audit_event import AuditEventModel

router = APIRouter(prefix="/audit", tags=["audit"])

# Sample audit events to seed the database
SAMPLE_AUDIT_EVENTS = [
    {
        "actor": "user1",
        "action": "CREATE_ENV_VAR",
        "action_description": "Created environment variable",
        "target_type": "ENV_VAR",
        "target_id": "env_1",
        "change_summary": "Added DATABASE_URL",
        "before_json": None,
        "after_json": {"key": "DATABASE_URL", "type": "SECRET"},
        "is_sensitive": True,
        "reason": "Initial setup"
    },
    {
        "actor": "user2",
        "action": "UPDATE_ENV_VAR",
        "action_description": "Updated environment variable",
        "target_type": "ENV_VAR",
        "target_id": "env_2",
        "change_summary": "Changed API_KEY value",
        "before_json": {"key": "API_KEY", "value": "old_key"},
        "after_json": {"key": "API_KEY", "value": "new_key"},
        "is_sensitive": True,
        "reason": "Key rotation"
    },
    {
        "actor": "user1", 
        "action": "REVEAL_SECRET",
        "action_description": "Revealed secret value",
        "target_type": "ENV_VAR",
        "target_id": "env_1",
        "change_summary": "Secret revealed for debugging",
        "before_json": None,
        "after_json": None,
        "is_sensitive": True,
        "reason": "Debugging production issue"
    },
    {
        "actor": "user3",
        "action": "CREATE_RELEASE",
        "action_description": "Created release",
        "target_type": "RELEASE", 
        "target_id": "release_1",
        "change_summary": "Release v1.0.0 with 5 changes",
        "before_json": None,
        "after_json": {"title": "Release v1.0.0", "changes_count": 5},
        "is_sensitive": False,
        "reason": "Production deployment"
    },
    {
        "actor": "user2",
        "action": "APPROVE_RELEASE", 
        "action_description": "Approved release",
        "target_type": "RELEASE",
        "target_id": "release_1", 
        "change_summary": "Release approved for production",
        "before_json": {"status": "PENDING_APPROVAL"},
        "after_json": {"status": "APPROVED"},
        "is_sensitive": False,
        "reason": "Code review completed"
    }
]

class AuditEvent(BaseModel):
    id: str
    actor: str
    action: str
    action_description: str
    target_type: str
    target_id: str
    change_summary: str
    before_json: Optional[dict] = None
    after_json: Optional[dict] = None
    timestamp: str
    is_sensitive: bool
    reason: str

class AuditEventsResponse(BaseModel):
    events: List[AuditEvent]
    total: int
    page: int
    size: int

@router.get("/events", response_model=AuditEventsResponse)
async def list_audit_events(
    actor: Optional[str] = Query(None, description="Filter by actor"),
    action: Optional[str] = Query(None, description="Filter by action"),
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    target_id: Optional[str] = Query(None, description="Filter by target ID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """List audit events with filtering and pagination"""
    try:
        # Build query with filters
        query = db.query(AuditEventModel)
        
        if actor:
            query = query.filter(AuditEventModel.actor.ilike(f"%{actor}%"))
        
        if action:
            query = query.filter(AuditEventModel.action.ilike(f"%{action}%"))
            
        if target_type:
            query = query.filter(AuditEventModel.target_type == target_type)
            
        if target_id:
            query = query.filter(AuditEventModel.target_id == target_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        events = query.order_by(desc(AuditEventModel.timestamp)).offset((page - 1) * size).limit(size).all()
        
        # Convert to AuditEvent objects
        audit_events = [AuditEvent(**event.to_dict()) for event in events]
        
        return AuditEventsResponse(
            events=audit_events,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list audit events: {str(e)}")

@router.get("/events/{event_id}", response_model=AuditEvent)
async def get_audit_event(event_id: str, db: Session = Depends(get_db)):
    """Get a specific audit event by ID"""
    try:
        event = db.query(AuditEventModel).filter(AuditEventModel.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Audit event not found")
        
        return AuditEvent(**event.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit event: {str(e)}")

@router.get("/stats")
async def get_audit_stats(db: Session = Depends(get_db)):
    """Get audit statistics"""
    try:
        # Get total events
        total_events = db.query(AuditEventModel).count()
        sensitive_events = db.query(AuditEventModel).filter(AuditEventModel.is_sensitive == True).count()
        
        # Group by action
        action_counts = db.query(
            AuditEventModel.action, 
            func.count(AuditEventModel.id)
        ).group_by(AuditEventModel.action).all()
        action_counts_dict = {action: count for action, count in action_counts}
        
        # Group by actor
        actor_counts = db.query(
            AuditEventModel.actor, 
            func.count(AuditEventModel.id)
        ).group_by(AuditEventModel.actor).all()
        actor_counts_dict = {actor: count for actor, count in actor_counts}
        
        return {
            "total_events": total_events,
            "sensitive_events": sensitive_events,
            "action_counts": action_counts_dict,
            "actor_counts": actor_counts_dict
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit stats: {str(e)}")

@router.post("/seed")
async def seed_audit_events(db: Session = Depends(get_db)):
    """Seed database with sample audit events"""
    try:
        # Check if events already exist
        existing_count = db.query(AuditEventModel).count()
        if existing_count > 0:
            return {"message": f"Database already has {existing_count} audit events", "seeded": False}
        
        # Create sample events
        for event_data in SAMPLE_AUDIT_EVENTS:
            audit_event = AuditEventModel(**event_data)
            db.add(audit_event)
        
        db.commit()
        
        return {
            "message": f"Successfully seeded {len(SAMPLE_AUDIT_EVENTS)} audit events",
            "seeded": True,
            "count": len(SAMPLE_AUDIT_EVENTS)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to seed audit events: {str(e)}")
