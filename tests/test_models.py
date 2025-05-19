from datetime import datetime

import pytest
from pydantic import ValidationError

from models import Contact


def test_contact_required_fields():
    contact = Contact(name="Alice", phone="1234567890")
    assert contact.name == "Alice"
    assert contact.phone == "1234567890"
    assert contact.email is None
    assert contact.notes is None
    assert contact.last_contacted is None


def test_contact_optional_fields():
    now = datetime.now()
    contact = Contact(
        name="Bob",
        phone="9876543210",
        email="bob@example.com",
        notes="Friend from work",
        last_contacted=now,
    )
    assert contact.email == "bob@example.com"
    assert contact.notes == "Friend from work"
    assert contact.last_contacted == now


def test_contact_validation():
    with pytest.raises(ValidationError):
        Contact(name="", phone="123")
    with pytest.raises(ValidationError):
        Contact(name="Alice", phone="")


def test_contact_from_json():
    data = {
        "name": "Charlie",
        "phone": "555-5555",
        "email": "charlie@example.com",
        "notes": "Test note",
        "last_contacted": "2024-06-01T12:00:00",
    }
    contact = Contact.from_json(data)
    assert contact.name == "Charlie"
    assert contact.phone == "555-5555"
    assert contact.email == "charlie@example.com"
    assert contact.notes == "Test note"
    assert contact.last_contacted == datetime(2024, 6, 1, 12, 0, 0)
