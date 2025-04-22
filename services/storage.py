from typing import List, Optional
from models.contact import Contact


class ContactStorage:
    def __init__(self):
        self.contacts: List[Contact] = []

    def add_contact(self, contact: Contact) -> None:
        self.contacts.append(contact)

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
                return True
        return False

    def delete_contact(self, name: str) -> bool:
        for i, contact in enumerate(self.contacts):
            if contact.name.lower() == name.lower():
                del self.contacts[i]
                return True
        return False
