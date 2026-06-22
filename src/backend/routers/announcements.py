"""
Announcement endpoints for the High School Management System API
"""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


class AnnouncementPayload(BaseModel):
    """Announcement create or update payload."""

    title: str = Field(..., min_length=1, max_length=80)
    message: str = Field(..., min_length=1, max_length=500)
    start_date: Optional[str] = None
    expiration_date: str

    @field_validator("title", "message", "expiration_date")
    @classmethod
    def strip_required_fields(cls, value: str) -> str:
        """Trim required string fields and reject blank values."""
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("This field is required")
        return trimmed

    @field_validator("start_date")
    @classmethod
    def normalize_optional_date(cls, value: Optional[str]) -> Optional[str]:
        """Normalize an optional date string."""
        if value is None:
            return None

        trimmed = value.strip()
        if not trimmed:
            return None

        date.fromisoformat(trimmed)
        return trimmed

    @field_validator("expiration_date")
    @classmethod
    def validate_expiration_date(cls, value: str) -> str:
        """Validate expiration date uses ISO format."""
        date.fromisoformat(value)
        return value

    @field_validator("expiration_date")
    @classmethod
    def validate_date_order(cls, expiration_date: str, info) -> str:
        """Require expiration date to fall after the optional start date."""
        start_date = info.data.get("start_date")
        if start_date and date.fromisoformat(expiration_date) < date.fromisoformat(start_date):
            raise ValueError("Expiration date must be on or after the start date")
        return expiration_date


def require_signed_in_user(teacher_username: Optional[str]) -> Dict[str, Any]:
    """Validate that the supplied teacher username belongs to a signed-in user."""
    if not teacher_username:
        raise HTTPException(
            status_code=401,
            detail="Authentication required for this action"
        )

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(
            status_code=401,
            detail="Invalid teacher credentials"
        )

    return teacher


def serialize_announcement(document: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a MongoDB document into API response data."""
    return {
        "id": document["_id"],
        "title": document["title"],
        "message": document["message"],
        "start_date": document.get("start_date"),
        "expiration_date": document["expiration_date"]
    }


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Return active announcements for the public site."""
    today = date.today().isoformat()
    query = {
        "expiration_date": {"$gte": today},
        "$or": [
            {"start_date": None},
            {"start_date": {"$exists": False}},
            {"start_date": {"$lte": today}}
        ]
    }

    announcements = announcements_collection.find(query).sort([
        ("expiration_date", 1),
        ("title", 1)
    ])
    return [serialize_announcement(document) for document in announcements]


@router.get("/manage", response_model=List[Dict[str, Any]])
def get_all_announcements(
    teacher_username: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    """Return all announcements for authenticated management screens."""
    require_signed_in_user(teacher_username)

    announcements = announcements_collection.find().sort([
        ("expiration_date", 1),
        ("title", 1)
    ])
    return [serialize_announcement(document) for document in announcements]


@router.post("", response_model=Dict[str, Any])
@router.post("/", response_model=Dict[str, Any])
def create_announcement(
    payload: AnnouncementPayload,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Create a new announcement."""
    require_signed_in_user(teacher_username)

    announcement_id = uuid4().hex
    announcement = {
        "_id": announcement_id,
        "title": payload.title,
        "message": payload.message,
        "start_date": payload.start_date,
        "expiration_date": payload.expiration_date
    }
    announcements_collection.insert_one(announcement)
    return serialize_announcement(announcement)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    payload: AnnouncementPayload,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Update an existing announcement."""
    require_signed_in_user(teacher_username)

    result = announcements_collection.update_one(
        {"_id": announcement_id},
        {
            "$set": {
                "title": payload.title,
                "message": payload.message,
                "start_date": payload.start_date,
                "expiration_date": payload.expiration_date
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    updated = announcements_collection.find_one({"_id": announcement_id})
    if not updated:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return serialize_announcement(updated)


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, str]:
    """Delete an announcement."""
    require_signed_in_user(teacher_username)

    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted"}
