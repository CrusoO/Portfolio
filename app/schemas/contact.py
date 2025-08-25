"""
Contact schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    message: str


class ContactCreate(ContactBase):
    contact_type: str = "work"


class ContactResponse(ContactBase):
    id: int
    contact_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True
