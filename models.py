"""
Data models for the Contacts application.

This module defines the data structures used throughout the application.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Contact(BaseModel):
    """Represents a contact in the address book.

    Attributes:
        name: The contact's full name.
        phone: The contact's phone number.
        email: The contact's email address (optional).
        notes: Additional notes about the contact (optional).
        last_contacted: When the contact was last contacted (optional).
    """

    name: str = Field(
        ...,
        description="Contact's full name",
        min_length=1,
        max_length=100,
    )
    phone: str = Field(
        ...,
        description="Contact's phone number",
        min_length=5,
        max_length=20,
    )
    email: Optional[str] = Field(
        None,
        description="Contact's email address",
        max_length=100,
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about the contact",
        max_length=1000,
    )
    last_contacted: Optional[datetime] = Field(
        None,
        description="When the contact was last contacted",
    )

    class Config:
        """Pydantic model configuration."""

        json_encoders = {datetime: lambda v: v.isoformat() if v else None}
        schema_extra = {
            "example": {
                "name": "John Doe",
                "phone": "+1234567890",
                "email": "john@example.com",
                "notes": "Met at the conference",
                "last_contacted": "2023-05-17T10:00:00",
            }
        }

    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> "Contact":
        """Create a Contact instance from a JSON dictionary.

        Args:
            json_dict: Dictionary containing contact data.

        Returns:
            A new Contact instance.

        Note:
            Handles conversion of ISO format datetime strings to datetime objects.
        """
        if "last_contacted" in json_dict and json_dict["last_contacted"]:
            json_dict["last_contacted"] = datetime.fromisoformat(
                json_dict["last_contacted"]
            )
        return cls(**json_dict)
