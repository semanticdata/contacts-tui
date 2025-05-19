import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional

from models import Contact

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContactStorage:
    """A class to handle contact storage operations using SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the contact storage.

        Args:
            db_path: Optional path to the SQLite database file.
                   If not provided, uses 'contacts.db' in the current directory.
        """
        self.db_file = db_path or os.path.join(os.path.dirname(__file__), "contacts.db")
        self._init_db()
        logger.info(f"Initialized contact storage at {self.db_file}")

    def _init_db(self) -> None:
        """Initialize the database tables and indexes if they don't exist."""
        try:
            with self._get_connection() as conn:
                # Enable foreign key support
                conn.execute("PRAGMA foreign_keys = ON")

                # Create contacts table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        name TEXT PRIMARY KEY COLLATE NOCASE,
                        phone TEXT NOT NULL,
                        email TEXT,
                        notes TEXT,
                        last_contacted TEXT,
                        created_at TEXT DEFAULT (datetime('now')),
                        updated_at TEXT DEFAULT (datetime('now'))
                    )
                """)

                # Create indexes
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_contacts_name 
                    ON contacts(name)
                """)

                conn.commit()
                logger.debug("Database initialized")
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    @contextmanager
    def _get_connection(self) -> sqlite3.Connection:
        """Context manager for database connections.

        Yields:
            sqlite3.Connection: A database connection

        Raises:
            sqlite3.Error: If connection or cursor operations fail
        """
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def _validate_contact(self, contact: Contact) -> bool:
        """Validate contact data before saving.

        Args:
            contact: The contact to validate

        Returns:
            bool: True if contact is valid, False otherwise
        """
        if not contact.name or not isinstance(contact.name, str) or not contact.name.strip():
            logger.warning("Contact validation failed: Invalid name")
            return False
        if not contact.phone or not isinstance(contact.phone, str) or not contact.phone.strip():
            logger.warning("Contact validation failed: Invalid phone")
            return False
        return True

    def __enter__(self):
        """Support context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support context manager exit."""
        # No need for explicit cleanup since we use context manager for connections
        pass

    def add_contact(self, contact: Contact) -> bool:
        """Add a new contact to the database.

        Args:
            contact: The contact to add

        Returns:
            bool: True if contact was added successfully, False otherwise
        """
        if not self._validate_contact(contact):
            return False

        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO contacts (name, phone, email, notes, last_contacted)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        contact.name.strip(),
                        contact.phone.strip(),
                        contact.email.strip() if contact.email else None,
                        contact.notes.strip() if contact.notes else None,
                        contact.last_contacted.isoformat() if contact.last_contacted else None,
                    ),
                )
                conn.commit()
                logger.info(f"Added contact: {contact.name}")
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            logger.warning(f"Contact already exists: {contact.name}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Failed to add contact {contact.name}: {e}")
            return False

    def update_contact(self, existing_contact: Contact, updated_contact: Contact) -> bool:
        """Update an existing contact in the database.

        Args:
            existing_contact: The contact to update
            updated_contact: The updated contact data

        Returns:
            bool: True if contact was updated successfully, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    UPDATE contacts 
                    SET phone = ?, email = ?, notes = ?, last_contacted = ?, updated_at = datetime('now')
                    WHERE name = ?
                    """,
                    (
                        updated_contact.phone.strip(),
                        updated_contact.email.strip() if updated_contact.email else None,
                        updated_contact.notes.strip() if updated_contact.notes else None,
                        updated_contact.last_contacted.isoformat() if updated_contact.last_contacted else None,
                        existing_contact.name.strip(),
                    ),
                )
                conn.commit()
                logger.info(f"Updated contact: {existing_contact.name}")
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Failed to update contact {existing_contact.name}: {e}")
            return False

    def get_all_contacts(self) -> List[Contact]:
        """Retrieve all contacts from the database.

        Returns:
            List[Contact]: A list of all contacts
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT name, phone, email, notes, last_contacted 
                    FROM contacts 
                    ORDER BY name COLLATE NOCASE
                """)
                return [
                    Contact(
                        name=row["name"],
                        phone=row["phone"],
                        email=row["email"],
                        notes=row["notes"],
                        last_contacted=datetime.fromisoformat(row["last_contacted"]) if row["last_contacted"] else None,
                    )
                    for row in cursor.fetchall()
                ]
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve contacts: {e}")
            return []

    def get_contact_by_name(self, name: str) -> Optional[Contact]:
        """Retrieve a contact by name (case-insensitive).

        Args:
            name: The name of the contact to retrieve

        Returns:
            Optional[Contact]: The contact if found, None otherwise
        """
        if not name or not isinstance(name, str) or not name.strip():
            return None

        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT name, phone, email, notes, last_contacted 
                    FROM contacts 
                    WHERE name = ? COLLATE NOCASE
                    """,
                    (name.strip(),),
                )
                row = cursor.fetchone()
                if row:
                    return Contact(
                        name=row["name"],
                        phone=row["phone"],
                        email=row["email"],
                        notes=row["notes"],
                        last_contacted=datetime.fromisoformat(row["last_contacted"]) if row["last_contacted"] else None,
                    )
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve contact {name}: {e}")
            return None

    def update_contact(self, name: str, updated_contact: Contact) -> bool:
        """Update an existing contact.

        Args:
            name: The current name of the contact to update
            updated_contact: The updated contact information

        Returns:
            bool: True if the contact was updated successfully, False otherwise
        """
        if not name or not isinstance(name, str) or not name.strip():
            return False

        if not self._validate_contact(updated_contact):
            return False

        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    UPDATE contacts
                    SET name = ?, phone = ?, email = ?, notes = ?, last_contacted = ?,
                        updated_at = datetime('now')
                    WHERE name = ? COLLATE NOCASE
                    """,
                    (
                        updated_contact.name.strip(),
                        updated_contact.phone.strip(),
                        updated_contact.email.strip() if updated_contact.email else None,
                        updated_contact.notes.strip() if updated_contact.notes else None,
                        updated_contact.last_contacted.isoformat() if updated_contact.last_contacted else None,
                        name.strip(),
                    ),
                )
                conn.commit()
                updated = cursor.rowcount > 0
                if updated:
                    logger.info(f"Updated contact: {name} -> {updated_contact.name}")
                else:
                    logger.warning(f"Contact not found for update: {name}")
                return updated
        except sqlite3.Error as e:
            logger.error(f"Failed to update contact {name}: {e}")
            return False

    def delete_contact(self, name: str) -> bool:
        """Delete a contact by name.

        Args:
            name: The name of the contact to delete

        Returns:
            bool: True if the contact was deleted, False otherwise
        """
        if not name or not isinstance(name, str) or not name.strip():
            return False

        try:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM contacts WHERE name = ? COLLATE NOCASE", (name.strip(),))
                conn.commit()
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Deleted contact: {name}")
                else:
                    logger.warning(f"Contact not found for deletion: {name}")
                return deleted
        except sqlite3.Error as e:
            logger.error(f"Failed to delete contact {name}: {e}")
            return False

    def check_connection(self) -> bool:
        """Check if the database connection is healthy.

        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            with self._get_connection() as conn:
                conn.execute("SELECT 1")
                return True
        except sqlite3.Error as e:
            logger.error(f"Database connection check failed: {e}")
            return False

    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database.

        Args:
            backup_path: Path where to save the backup

        Returns:
            bool: True if backup was successful, False otherwise
        """
        try:
            # Check if we're using an in-memory database
            if self.db_file == ":memory:":
                # For in-memory database, create a new file and initialize it
                with sqlite3.connect(backup_path) as conn:
                    self._init_db()
                    # Copy all data from in-memory to file
                    with self._get_connection() as src:
                        src.backup(conn)
            else:
                # For regular file database, use direct backup
                with self._get_connection() as src:
                    with sqlite3.connect(backup_path) as dst:
                        src.backup(dst)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Database backup failed: {e}")
            # Clean up the failed backup file if it exists
            if os.path.exists(backup_path):
                try:
                    os.unlink(backup_path)
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up backup file: {cleanup_error}")
            return False
