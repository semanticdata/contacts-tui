"""
Data storage and persistence for the Contacts application.

This module handles loading and saving contacts to persistent storage.
"""

import json
import os
from pathlib import Path
from typing import List, Optional

from models import Contact


class ContactStorage:
    """Handles storage and retrieval of contacts from persistent storage.

    Attributes:
        contacts: In-memory list of contacts.
        contacts_file: Path to the JSON file where contacts are stored.
    """

    def __init__(self) -> None:
        """Initialize the storage and load existing contacts."""
        self.contacts: List[Contact] = []
        self.contacts_file = Path(__file__).parent / "contacts.json"
        self.load_contacts()

    def load_contacts(self) -> None:
        """Load contacts from the JSON file.

        If the file doesn't exist, initializes an empty contact list.
        """
        try:
            if self.contacts_file.exists():
                with open(self.contacts_file, "r", encoding="utf-8") as f:
                    contacts_data = json.load(f)
                    self.contacts = [Contact.from_json(c) for c in contacts_data]
            else:
                self.contacts = []
        except (json.JSONDecodeError, OSError) as e:
            # If there's an error reading the file, start with an empty list
            self.contacts = []
            print(f"Warning: Could not load contacts: {e}")

    def save_contacts(self) -> None:
        """Save the current contacts to the JSON file.

        Creates the file if it doesn't exist.
        """
        try:
            # Ensure the directory exists
            self.contacts_file.parent.mkdir(parents=True, exist_ok=True)

            # Save with pretty-printing for readability
            with open(self.contacts_file, "w", encoding="utf-8") as f:
                contacts_data = [
                    json.loads(contact.json()) for contact in self.contacts
                ]
                json.dump(contacts_data, f, indent=2, ensure_ascii=False)
        except (OSError, TypeError) as e:
            print(f"Error saving contacts: {e}")

    def add_contact(self, contact: Contact) -> bool:
        """Add a new contact to the storage.

        Args:
            contact: The contact to add.

        Returns:
            bool: True if the contact was added, False if a contact with the
                  same name already exists.
        """
        # Check for duplicate names (case-insensitive)
        if any(c.name.lower() == contact.name.lower() for c in self.contacts):
            return False

        self.contacts.append(contact)
        self.save_contacts()
        return True

    def get_all_contacts(self) -> List[Contact]:
        """Get all contacts.

        Returns:
            A list of all contacts, sorted by name.
        """
        return sorted(self.contacts, key=lambda c: c.name.lower())

    def get_contact_by_name(self, name: str) -> Optional[Contact]:
        """Find a contact by name (case-insensitive).

        Args:
            name: The name of the contact to find.

        Returns:
            The contact if found, None otherwise.
        """
        name_lower = name.lower()
        return next(
            (
                contact
                for contact in self.contacts
                if contact.name.lower() == name_lower
            ),
            None,
        )

    def update_contact(self, name: str, updated_contact: Contact) -> bool:
        """Update an existing contact.

        Args:
            name: The current name of the contact to update.
            updated_contact: The updated contact data.

        Returns:
            bool: True if the contact was updated, False if not found.
        """
        name_lower = name.lower()
        for i, contact in enumerate(self.contacts):
            if contact.name.lower() == name_lower:
                # Preserve the original contact date if not specified in the update
                if updated_contact.last_contacted is None:
                    updated_contact.last_contacted = contact.last_contacted

                self.contacts[i] = updated_contact
                self.save_contacts()
                return True
        return False

    def delete_contact(self, name: str) -> bool:
        """Delete a contact by name.

        Args:
            name: The name of the contact to delete.

        Returns:
            bool: True if the contact was deleted, False if not found.
        """
        name_lower = name.lower()
        for i, contact in enumerate(self.contacts):
            if contact.name.lower() == name_lower:
                del self.contacts[i]
                self.save_contacts()
                return True
        return False
