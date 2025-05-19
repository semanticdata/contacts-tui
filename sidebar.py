from datetime import datetime

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, DataTable, Footer, Header, Input, Label

from models import Contact
from storage import ContactStorage

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class Sidebar(Widget):
    DEFAULT_CSS = """
    Sidebar {
        width: 30;
        /* Needs to go in its own layer to sit above content */
        layer: sidebar; 
        /* Dock the sidebar to the appropriate side */
        dock: left;
        /* Offset x to be -100% to move it out of view by default */
        offset-x: -100%;

        background: $primary;
        border-right: vkey $background;    

        /* Enable animation */
        transition: offset 200ms;
        
        &.-visible {
            /* Set offset.x to 0 to make it visible when class is applied */
            offset-x: 0;
        }

        & > Vertical {
            margin: 1 2;
        }
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Your sidebar here!")


class AddContact(Widget):
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
            contact_list = next(screen for screen in self.app.screen_stack if isinstance(screen, ContactList))
            contact_list.refresh_contacts()
            self.app.pop_screen()

    def action_cancel(self) -> None:
        self.app.pop_screen()


class EditContact(Widget):
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
            contact_list = next(screen for screen in self.app.screen_stack if isinstance(screen, ContactList))
            contact_list.refresh_contacts()
            self.app.pop_screen()

    def action_cancel(self) -> None:
        self.app.pop_screen()


class ContactManager(App):
    DEFAULT_CSS = """
    Screen {    
        layers: sidebar;
    }

    """

    BINDINGS = [("s", "toggle_sidebar", "Toggle Sidebar")]

    show_sidebar = reactive(False)

    def __init__(self):
        super().__init__()
        self.storage = ContactStorage()

    def compose(self) -> ComposeResult:
        yield Sidebar()
        # yield Label(TEXT)
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

    def action_toggle_sidebar(self) -> None:
        """Toggle the sidebar visibility."""
        self.show_sidebar = not self.show_sidebar

    def watch_show_sidebar(self, show_sidebar: bool) -> None:
        """Set or unset visible class when reactive changes."""
        self.query_one(Sidebar).set_class(show_sidebar, "-visible")


if __name__ == "__main__":
    app = ContactManager()
    app.run()
