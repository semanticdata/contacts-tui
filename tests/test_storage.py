import os
import tempfile
import uuid

import pytest

from models import Contact
from storage import ContactStorage


def make_contact(name="Test User", phone="1234567890", **kwargs):
    return Contact(name=name, phone=phone, **kwargs)


@pytest.fixture
def storage():
    # Use a temporary file for the database to persist across connections
    fd, path = tempfile.mkstemp()
    os.close(fd)
    store = ContactStorage(db_path=path)
    yield store
    if os.path.exists(path):
        os.remove(path)


def test_add_and_get_contact(storage):
    contact = make_contact()
    assert storage.add_contact(contact)
    fetched = storage.get_contact_by_name(contact.name)
    assert fetched is not None
    assert fetched.name == contact.name
    assert fetched.phone == contact.phone


def test_add_duplicate_contact(storage):
    contact = make_contact()
    assert storage.add_contact(contact)
    assert not storage.add_contact(contact)  # Duplicate


def test_get_all_contacts(storage):
    storage.add_contact(make_contact(name="A"))
    storage.add_contact(make_contact(name="B"))
    contacts = storage.get_all_contacts()
    names = {c.name for c in contacts}
    assert {"A", "B"}.issubset(names)


def test_update_contact(storage):
    contact = make_contact()
    storage.add_contact(contact)
    updated = make_contact(name="Test User", phone="9999999999", email="new@example.com")
    assert storage.update_contact("Test User", updated)
    fetched = storage.get_contact_by_name("Test User")
    assert fetched.phone == "9999999999"
    assert fetched.email == "new@example.com"


def test_delete_contact(storage):
    contact = make_contact()
    storage.add_contact(contact)
    assert storage.delete_contact(contact.name)
    assert storage.get_contact_by_name(contact.name) is None


def test_check_connection(storage):
    assert storage.check_connection()


@pytest.fixture
def backup_path(request):
    path = os.path.join(tempfile.gettempdir(), f"contacts-backup-{uuid.uuid4().hex}.db")

    def cleanup():
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except PermissionError:
            pass

    request.addfinalizer(cleanup)
    return path


def test_backup_database(storage, backup_path):
    contact = make_contact()
    storage.add_contact(contact)
    assert storage.backup_database(backup_path)
    assert os.path.exists(backup_path)
