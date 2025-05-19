"""
Textual Contacts Main Application
"""

from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, DataTable, Footer, Header, Input, Label

from models import Contact
from storage import ContactStorage


# --- Sidebar Widget ---
class Sidebar(Widget):
    """Sidebar navigation widget."""

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


# --- AddContactSidebar Widget ---
class AddContactSidebar(Widget):
    """Sidebar for adding a new contact."""

    DEFAULT_CSS = """
    AddContactSidebar {
        width: 40;
        layer: sidebar;
        dock: left;
        offset-x: -100%;
        background: $primary;
        border-right: vkey $background;
        transition: offset 200ms;
        &.-visible {
            offset-x: 0;
        }
        & > Container {
            margin: 1 2;
        }
    }
    """

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
            self.app.refresh_contacts()
            self.app.hide_add_contact_sidebar()

    def action_cancel(self) -> None:
        self.app.hide_add_contact_sidebar()


# --- EditContactSidebar Widget ---
class EditContactSidebar(Widget):
    """Sidebar for editing an existing contact."""

    DEFAULT_CSS = """
    EditContactSidebar {
        width: 40;
        layer: sidebar;
        dock: left;
        offset-x: -100%;
        background: $primary;
        border-right: vkey $background;
        transition: offset 200ms;
        &.-visible {
            offset-x: 0;
        }
        & > Container {
            margin: 1 2;
        }
    }
    """

    def __init__(self, storage: ContactStorage):
        super().__init__()
        self.storage = storage
        self.contact = None
        self.original_name = None

    def set_contact(self, contact: Contact):
        self.contact = contact
        self.original_name = contact.name
        self.refresh()
        self.populate_fields()

    def populate_fields(self):
        contact = self.contact or Contact(name="", phone="")
        try:
            self.query_one("#name", Input).value = contact.name
            self.query_one("#phone", Input).value = contact.phone
            self.query_one("#email", Input).value = contact.email or ""
            self.query_one("#notes", Input).value = contact.notes or ""
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        contact = self.contact or Contact(name="", phone="")
        yield Container(
            Header(),
            Vertical(
                Label("Edit Contact"),
                Input(id="name", value=contact.name),
                Input(id="phone", value=contact.phone),
                Input(id="email", value=contact.email or ""),
                Input(id="notes", value=contact.notes or ""),
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
        if name and phone and self.original_name:
            updated_contact = Contact(
                name=name,
                phone=phone,
                email=email if email else None,
                notes=notes if notes else None,
                last_contacted=datetime.now(),
            )
            self.storage.update_contact(self.original_name, updated_contact)
            self.app.refresh_contacts()
            self.app.hide_edit_contact_sidebar()

    def action_cancel(self) -> None:
        self.app.hide_edit_contact_sidebar()


# --- ContactManager App ---
class ContactManager(App):
    """Main application class for managing contacts."""

    CSS_PATH = "contacts.tcss"
    DEFAULT_CSS = """
    Screen {    
        layers: sidebar;
    }
    """
    BINDINGS = [
        ("s", "toggle_sidebar", "Toggle Sidebar"),
        ("a", "add_contact", "Add Contact"),
        ("e", "edit_contact", "Edit Contact"),
        ("q", "quit_application", "Quit"),
    ]
    show_sidebar = reactive(False)
    show_add_contact = reactive(False)
    show_edit_contact = reactive(False)

    def __init__(self):
        super().__init__()
        self.storage = ContactStorage()
        self._edit_contact_data = None

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Container(
            Label("Contacts", id="contacts-title"),
            DataTable(id="contacts-table"),
        )
        yield Footer()
        self.add_contact_sidebar = AddContactSidebar(self.storage)
        yield self.add_contact_sidebar
        self.edit_contact_sidebar = EditContactSidebar(self.storage)
        yield self.edit_contact_sidebar

    def on_mount(self) -> None:
        table = self.query_one("#contacts-table", DataTable)
        table.add_columns("Name", "Phone", "Email", "Last Contacted", "Notes")
        self.refresh_contacts()
        self._update_sidebars()

    def refresh_contacts(self) -> None:
        table = self.query_one("#contacts-table", DataTable)
        table.clear()
        for contact in self.storage.get_all_contacts():
            table.add_row(
                contact.name,
                contact.phone,
                contact.email or "",
                contact.last_contacted.strftime("%Y-%m-%d") if contact.last_contacted else "",
                contact.notes or "",
            )

    def action_toggle_sidebar(self) -> None:
        self.show_sidebar = not self.show_sidebar

    def action_add_contact(self) -> None:
        self.show_add_contact = True
        self._update_sidebars()

    def action_edit_contact(self) -> None:
        table = self.query_one("#contacts-table", DataTable)
        if table.cursor_coordinate is not None:
            row = table.cursor_coordinate.row
            name = table.get_cell_at((row, 0))
            if name:
                contact = self.storage.get_contact_by_name(name)
                if contact:
                    self.edit_contact_sidebar.set_contact(contact)
                    self.show_edit_contact = True
                    self._update_sidebars()

    def watch_show_sidebar(self, show_sidebar: bool) -> None:
        self.query_one(Sidebar).set_class(show_sidebar, "-visible")

    def watch_show_add_contact(self, show: bool) -> None:
        self.add_contact_sidebar.set_class(show, "-visible")

    def watch_show_edit_contact(self, show: bool) -> None:
        self.edit_contact_sidebar.set_class(show, "-visible")

    def hide_add_contact_sidebar(self):
        self.show_add_contact = False
        self._update_sidebars()

    def hide_edit_contact_sidebar(self):
        self.show_edit_contact = False
        self._update_sidebars()

    def _update_sidebars(self):
        self.watch_show_add_contact(self.show_add_contact)
        self.watch_show_edit_contact(self.show_edit_contact)

    def action_quit_application(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = ContactManager()
    app.run()
