"""
Textual UI screens for the Contacts application.

This module contains all the screen classes used in the application.
"""

from datetime import datetime
from typing import Optional, cast

import textual
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label

from models import Contact
from storage import ContactStorage


class ConfirmationModal(ModalScreen[bool]):
    """A modal dialog that asks for confirmation.

    Args:
        message: The confirmation message to display.
    """

    BINDINGS = [
        Binding("y", "confirm", "Confirm"),
        Binding("n", "cancel", "Cancel"),
    ]

    def __init__(self, message: str):
        """Initialize the confirmation modal."""
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.message),
            Grid(
                Button("\\[Y]es", id="yes", variant="error"),
                Button("\\[N]o", id="no", variant="primary"),
                id="button-container",
            ),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class ContactList(Screen):
    """Main screen displaying the list of contacts."""

    BINDINGS = [
        Binding("a", "add_contact", "Add Contact"),
        Binding("d", "delete_contact", "Delete Contact"),
        Binding("e", "edit_contact", "Edit Contact"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self):
        """Initialize the contact list screen."""
        super().__init__()
        self.storage = ContactStorage()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("Contacts", id="contacts-title"),
            DataTable(id="contacts-table"),
        )
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#contacts-table", DataTable)
        table.add_columns("Name", "Phone", "Email", "Last Contacted", "Notes")
        self.refresh_contacts()

    def refresh_contacts(self) -> None:
        table = self.query_one("#contacts-table", DataTable)
        table.clear()
        for contact in self.storage.get_all_contacts():
            table.add_row(
                contact.name,
                contact.phone,
                contact.email or "",
                contact.last_contacted.strftime("%Y-%m-%d") or "",
                contact.notes or "",
            )

    def action_add_contact(self) -> None:
        self.app.push_screen(AddContact(self.storage))

    def action_delete_contact(self) -> None:
        table = self.query_one("#contacts-table", DataTable)
        if table.cursor_coordinate is not None:
            row = table.cursor_coordinate.row
            contact_name = table.get_cell_at((row, 0))
            if contact_name:
                self.show_delete_confirmation(contact_name)

    @textual.work(exclusive=True)
    async def show_delete_confirmation(self, contact_name: str) -> None:
        confirm = await self.app.push_screen_wait(
            ConfirmationModal(
                f"Are you sure you want to delete contact '{contact_name}'?"
            )
        )
        if confirm and self.storage.delete_contact(contact_name):
            self.refresh_contacts()

    def action_edit_contact(self) -> None:
        table = self.query_one("#contacts-table", DataTable)
        if table.cursor_coordinate is not None:
            row = table.cursor_coordinate.row
            contact_name = table.get_cell_at((row, 0))
            if contact_name:
                contact = self.storage.get_contact_by_name(contact_name)
                if contact:
                    self.app.push_screen(EditContact(self.storage, contact))

    @textual.work(exclusive=True)
    async def action_quit(self) -> None:
        confirm = await self.app.push_screen_wait(
            ConfirmationModal("Are you sure you want to quit?")
        )
        if confirm:
            self.app.exit()


class AddContact(Screen):
    """Screen for adding a new contact."""

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+c", "cancel", "Cancel"),
    ]

    def __init__(self, storage: ContactStorage):
        """Initialize the add contact screen.

        Args:
            storage: The contact storage instance to use.
        """
        super().__init__()
        self.storage = storage

    def compose(self) -> ComposeResult:
        yield Container(
            Header(),
            Vertical(
                Label("Add New Contact"),
                Input(placeholder="Name", id="name"),
                Input(placeholder="Phone", id="phone"),
                Input(placeholder="Email (optional)", id="email"),
                Input(placeholder="Notes (optional)", id="notes"),
                Vertical(
                    Button("Save", variant="primary", id="save"),
                    Button("Cancel", variant="default", id="cancel"),
                    classes="button-container",
                ),
                classes="form-container",
            ),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.action_save()
        elif event.button.id == "cancel":
            self.action_cancel()

    def action_save(self) -> None:
        name = self.query_one("#name", Input).value
        phone = self.query_one("#phone", Input).value
        email = self.query_one("#email", Input).value
        notes = self.query_one("#notes", Input).value

        if name and phone:
            contact = Contact(
                name=name,
                phone=phone,
                email=email if email else None,
                notes=notes if notes else None,
                last_contacted=datetime.now(),
            )
            self.storage.add_contact(contact)
            contact_list = next(
                screen
                for screen in self.app.screen_stack
                if isinstance(screen, ContactList)
            )
            contact_list.refresh_contacts()
            self.app.pop_screen()

    def action_cancel(self) -> None:
        self.app.pop_screen()


class EditContact(Screen):
    """Screen for editing an existing contact."""

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+c", "cancel", "Cancel"),
    ]

    def __init__(self, storage: ContactStorage, contact: Contact):
        """Initialize the edit contact screen.

        Args:
            storage: The contact storage instance to use.
            contact: The contact to edit.
        """
        super().__init__()
        self.storage = storage
        self.contact = contact
        self.original_name = contact.name

    def compose(self) -> ComposeResult:
        yield Container(
            Header(),
            Vertical(
                Label("Edit Contact"),
                Input(id="name", value=self.contact.name),
                Input(id="phone", value=self.contact.phone),
                Input(id="email", value=self.contact.email or ""),
                Input(id="notes", value=self.contact.notes or ""),
                Vertical(
                    Button("Save", variant="primary", id="save"),
                    Button("Cancel", variant="default", id="cancel"),
                    classes="button-container",
                ),
                classes="form-container",
            ),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.action_save()
        elif event.button.id == "cancel":
            self.action_cancel()

    def action_save(self) -> None:
        name = self.query_one("#name", Input).value
        phone = self.query_one("#phone", Input).value
        email = self.query_one("#email", Input).value
        notes = self.query_one("#notes", Input).value

        if name and phone:
            updated_contact = Contact(
                name=name,
                phone=phone,
                email=email if email else None,
                notes=notes if notes else None,
                last_contacted=datetime.now(),
            )
            self.storage.update_contact(self.original_name, updated_contact)
            contact_list = next(
                screen
                for screen in self.app.screen_stack
                if isinstance(screen, ContactList)
            )
            contact_list.refresh_contacts()
            self.app.pop_screen()

    def action_cancel(self) -> None:
        self.app.pop_screen()


class ContactsApp(App):
    """Main application class for the Contacts app."""

    CSS_PATH = "styles.css"  # External CSS file

    def __init__(self):
        """Initialize the application."""
        super().__init__()

    def on_mount(self) -> None:
        """Set up the initial screen when the app starts."""
        self.push_screen(ContactList())
