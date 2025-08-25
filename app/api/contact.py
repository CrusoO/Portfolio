"""
Contact form endpoints
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactResponse

router = APIRouter(prefix="/api/contact", tags=["Contact"])


@router.post("/submit", response_model=dict)
async def submit_contact(contact_data: ContactCreate, db: Session = Depends(get_db)):
    """Submit contact form"""
    contact = Contact(
        contact_type=contact_data.contact_type,
        first_name=contact_data.first_name,
        last_name=contact_data.last_name,
        email=contact_data.email,
        message=contact_data.message
    )
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return {"message": "Contact submitted successfully!", "contact_id": contact.id}


@router.get("", response_model=List[ContactResponse])
async def get_contacts(limit: int = 50, db: Session = Depends(get_db)):
    """Get contact submissions (admin only in production)"""
    contacts = db.query(Contact).order_by(Contact.created_at.desc()).limit(limit).all()
    return contacts


@router.delete("/{contact_id}")
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """Delete a contact submission"""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    if not contact:
        return {"message": "Contact not found"}
    
    db.delete(contact)
    db.commit()
    
    return {"message": "Contact deleted successfully"}
