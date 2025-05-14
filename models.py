from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from pydantic.json import timedelta_isoformat


class Contact(BaseModel):
    name: str = Field(..., description="Contact's full name")
    phone: str = Field(..., description="Contact's phone number")
    email: Optional[str] = Field(None, description="Contact's email address")
    notes: Optional[str] = Field(None, description="Additional notes about the contact")
    last_contacted: Optional[datetime] = Field(
        None, description="When the contact was last contacted"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}

    @classmethod
    def from_json(cls, json_dict: dict) -> "Contact":
        if "last_contacted" in json_dict and json_dict["last_contacted"]:
            json_dict["last_contacted"] = datetime.fromisoformat(
                json_dict["last_contacted"]
            )
        return cls(**json_dict)
