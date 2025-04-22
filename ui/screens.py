from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Input, Label, Static
from textual.binding import Binding

from models.contact import Contact
from services.storage import ContactStorage


class ContactList(Screen):
    BINDINGS = [
        Binding("a", "add_contact", "Add Contact"),
        Binding("d", "delete_contact", "Delete Contact"),
        Binding("e", "edit_contact", "Edit Contact"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.storage = ContactStorage()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("Contacts", id="contacts-title"), DataTable(id="contacts-table")
        )

    def on_mount(self) -> None:
        table = self.query_one("#contacts-table", DataTable)
        table.add_columns("Name", "Phone", "Email", "Last Contacted")
        self.refresh_contacts()

    def refresh_contacts(self) -> None:
        table = self.query_one("#contacts-table", DataTable)
        table.clear()
        for contact in self.storage.get_all_contacts():
            table.add_row(
                contact.name,
                contact.phone,
                contact.email or "",
                (
                    contact.last_contacted.strftime("%Y-%m-%d")
                    if contact.last_contacted
                    else ""
                ),
            )

    def action_add_contact(self) -> None:
        self.app.push_screen(AddContact(self.storage))


class AddContact(Screen):
    def compose(self) -> ComposeResult:
        yield Container(
            Header(),
            Vertical(
                Label("Add New Contact"),
                Input(placeholder="Name", id="name"),
                Input(placeholder="Phone", id="phone"),
                Input(placeholder="Email (optional)", id="email"),
                Input(placeholder="Notes (optional)", id="notes"),
                Button("Save", variant="primary", id="save"),
                Button("Cancel", variant="default", id="cancel"),
            ),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
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
                self.app.pop_screen()
        elif event.button.id == "cancel":
            self.app.pop_screen()


class ContactsApp(App):
    CSS = """
    Screen {
        align: center middle;
    }

    #contacts-title {
        dock: top;
        padding: 1;
        text-align: center;
        text-style: bold;
    }

    #contacts-table {
        height: auto;
        width: 100%;
    }

    Input {
        margin: 1;
        width: 100%;
    }

    Button {
        margin: 1;
        width: 100%;
    }
    """

    def on_mount(self) -> None:
        self.push_screen(ContactList())
