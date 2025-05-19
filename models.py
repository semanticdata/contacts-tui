"""
Models for Textual Contacts app.
Defines the Contact data structure using Pydantic.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Contact(BaseModel):
    """Represents a contact entry in the address book."""

    name: str = Field(..., min_length=1, description="Contact's full name")  # Required name
    phone: str = Field(..., min_length=1, description="Contact's phone number")  # Required phone
    email: Optional[str] = Field(None, description="Contact's email address")  # Optional email
    notes: Optional[str] = Field(None, description="Additional notes about the contact")  # Optional notes
    last_contacted: Optional[datetime] = Field(
        None, description="When the contact was last contacted"
    )  # Optional last contacted date

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat() if v else None}}

    @classmethod
    def from_json(cls, json_dict: dict) -> "Contact":
        """Create a Contact instance from a JSON dictionary, parsing the date if present."""
        if "last_contacted" in json_dict and json_dict["last_contacted"]:
            json_dict["last_contacted"] = datetime.fromisoformat(json_dict["last_contacted"])
        return cls(**json_dict)
