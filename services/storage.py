import json
from typing import List, Optional
from models.contact import Contact
from config import CONTACTS_FILE


class ContactStorage:
    def __init__(self):
        self.contacts: List[Contact] = []
        self.load_contacts()

    def load_contacts(self) -> None:
        try:
            with open(CONTACTS_FILE, 'r') as f:
                contacts_data = json.load(f)
                self.contacts = [Contact.from_json(c) for c in contacts_data]
        except FileNotFoundError:
            self.contacts = []

    def save_contacts(self) -> None:
        with open(CONTACTS_FILE, 'w') as f:
            contacts_data = [json.loads(c.json()) for c in self.contacts]
            json.dump(contacts_data, f, indent=2)

    def add_contact(self, contact: Contact) -> None:
        self.contacts.append(contact)
        self.save_contacts()

    def get_all_contacts(self) -> List[Contact]:
        return self.contacts

    def get_contact_by_name(self, name: str) -> Optional[Contact]:
        for contact in self.contacts:
            if contact.name.lower() == name.lower():
                return contact
        return None

    def update_contact(self, name: str, updated_contact: Contact) -> bool:
        for i, contact in enumerate(self.contacts):
            if contact.name.lower() == name.lower():
                self.contacts[i] = updated_contact
                self.save_contacts()
                return True
        return False

    def delete_contact(self, name: str) -> bool:
        for i, contact in enumerate(self.contacts):
            if contact.name.lower() == name.lower():
                del self.contacts[i]
                self.save_contacts()
                return True
        return False
