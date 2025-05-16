import os
import sqlite3
from datetime import datetime
from typing import List, Optional

from models import Contact


class ContactStorage:
    def __init__(self):
        self.db_file = os.path.join(os.path.dirname(__file__), "contacts.db")
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    name TEXT PRIMARY KEY,
                    phone TEXT NOT NULL,
                    email TEXT,
                    notes TEXT,
                    last_contacted TEXT
                )
            """)
            conn.commit()

    def add_contact(self, contact: Contact) -> None:
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(
                """
                INSERT INTO contacts (name, phone, email, notes, last_contacted)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    contact.name,
                    contact.phone,
                    contact.email,
                    contact.notes,
                    contact.last_contacted.isoformat() if contact.last_contacted else None,
                ),
            )
            conn.commit()

    def get_all_contacts(self) -> List[Contact]:
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute("SELECT * FROM contacts")
            return [
                Contact(
                    name=row[0],
                    phone=row[1],
                    email=row[2],
                    notes=row[3],
                    last_contacted=datetime.fromisoformat(row[4]) if row[4] else None,
                )
                for row in cursor.fetchall()
            ]

    def get_contact_by_name(self, name: str) -> Optional[Contact]:
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute("SELECT * FROM contacts WHERE LOWER(name) = LOWER(?)", (name,))
            row = cursor.fetchone()
            if row:
                return Contact(
                    name=row[0],
                    phone=row[1],
                    email=row[2],
                    notes=row[3],
                    last_contacted=datetime.fromisoformat(row[4]) if row[4] else None,
                )
            return None

    def update_contact(self, name: str, updated_contact: Contact) -> bool:
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute(
                """
                UPDATE contacts
                SET name = ?, phone = ?, email = ?, notes = ?, last_contacted = ?
                WHERE LOWER(name) = LOWER(?)
                """,
                (
                    updated_contact.name,
                    updated_contact.phone,
                    updated_contact.email,
                    updated_contact.notes,
                    updated_contact.last_contacted.isoformat() if updated_contact.last_contacted else None,
                    name,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_contact(self, name: str) -> bool:
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute("DELETE FROM contacts WHERE LOWER(name) = LOWER(?)", (name,))
            conn.commit()
            return cursor.rowcount > 0
