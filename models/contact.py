from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Contact(BaseModel):
    name: str = Field(..., description="Contact's full name")
    phone: str = Field(..., description="Contact's phone number")
    email: Optional[str] = Field(None, description="Contact's email address")
    notes: Optional[str] = Field(None, description="Additional notes about the contact")
    last_contacted: Optional[datetime] = Field(
        None, description="When the contact was last contacted"
    )
