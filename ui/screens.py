from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Grid
from textual.screen import Screen, ModalScreen
from textual.widgets import Button, DataTable, Header, Input, Label, Static
from textual.binding import Binding
from textual.worker import Worker, get_current_worker
import textual

from models.contact import Contact
from services.storage import ContactStorage


class ConfirmationModal(ModalScreen[bool]):
    BINDINGS = [
        Binding("y", "confirm", "Confirm"),
        Binding("n", "cancel", "Cancel"),
    ]

    def __init__(self, message: str):
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
            Static(
                "\\[A]dd • \\[D]elete • \\[E]dit • \\[Q]uit",
                id="shortcuts-text",
            ),
        )

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
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+c", "cancel", "Cancel"),
    ]

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
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+c", "cancel", "Cancel"),
    ]

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
        # text-style: bold;
        color: $text;
        background: $surface;
        dock: bottom;
    }

    Input {
        margin: 1;
        width: 100%;
    }

    ConfirmationModal {
        align: center middle;
    }

    #dialog {
        padding: 1;
        width: 60;
        height: 60%;
        border: thick $background 80%;
        background: $surface;
        grid-size: 1;
        grid-gutter: 1;
        grid-rows: 1fr 3;
        align: center middle;
    }

    #button-container {
        grid-size: 2;
        grid-gutter: 1;
        align: center middle;
    }

    #dialog Label {
        color: $text;
        text-align: center;
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    Button {
        height: 3;
        border: none;
    }

    .form-container {
        # width: 100;
        # margin-top: 2;
        # height: auto;
        # width: 100%;
        # padding: 2;
        border: tall $primary;
        background: $surface;
    }

    .form-container Label {
        text-align: center;
        text-style: bold;
        width: 100%;
        # padding: 1;
        # margin-bottom: 1;
        # border-bottom: heavy $primary;
    }

    .form-container Input {
        margin: 1 2;
        border: tall $primary-darken-2;
    }

    .button-container {
        layout: horizontal;
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1;
    }

    .button-container Button {
        margin: 0 1;
    }
    """

    def on_mount(self) -> None:
        self.push_screen(ContactList())
