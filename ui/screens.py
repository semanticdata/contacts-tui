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
            Label("Contacts", id="contacts-title"),
            DataTable(id="contacts-table"),
            # Label("Keyboard Shortcuts", id="shortcuts-title"),
            Static(
                "\\[A]dd Contact • \\[D]elete Contact • \\[E]dit Contact • \\[Q]uit",
                id="shortcuts-text",
            ),
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

    def action_delete_contact(self) -> None:
        table = self.query_one("#contacts-table", DataTable)
        if table.cursor_coordinate is not None:
            row = table.cursor_coordinate.row
            contact_name = table.get_cell_at((row, 0))  # Name is in the first column
            if contact_name and self.storage.delete_contact(contact_name):
                self.refresh_contacts()

    def action_edit_contact(self) -> None:
        table = self.query_one("#contacts-table", DataTable)
        if table.cursor_coordinate is not None:
            row = table.cursor_coordinate.row
            contact_name = table.get_cell_at((row, 0))  # Name is in the first column
            if contact_name:
                contact = self.storage.get_contact_by_name(contact_name)
                if contact:
                    self.app.push_screen(EditContact(self.storage, contact))


class AddContact(Screen):
    def __init__(self, storage: ContactStorage):
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
                # Get the contact list screen by type instead of index
                contact_list = next(
                    screen
                    for screen in self.app.screen_stack
                    if isinstance(screen, ContactList)
                )
                contact_list.refresh_contacts()
                self.app.pop_screen()
        elif event.button.id == "cancel":
            self.app.pop_screen()


class EditContact(Screen):
    def __init__(self, storage: ContactStorage, contact: Contact):
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
        elif event.button.id == "cancel":
            self.app.pop_screen()


class ContactsApp(App):
    CSS = """
    Screen {
        align: center middle;
        overflow: hidden;
    }

    Container {
        height: 100vh;
        width: 100%;
        layout: grid;
        grid-size: 1;
        grid-rows: auto 1fr auto;
        padding: 0 1;
        overflow: hidden;
    }

    #contacts-title {
        padding: 1;
        text-align: center;
        text-style: bold;
    }

    #contacts-table {
        width: 100%;
        height: 100%;
        overflow-y: auto;
    }

    #shortcuts-text {
        padding: 1;
        margin: 0 0 1 0;
        text-align: center;
        text-style: bold;
        color: $text;
        background: $surface;
        dock: bottom;
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
