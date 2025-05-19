from main import ContactManager


def test_app_instantiation():
    app = ContactManager()
    assert app is not None
    assert hasattr(app, "storage")

    # The following assertions are removed as per the instructions
    # assert hasattr(app, "add_contact_sidebar")
    # assert hasattr(app, "edit_contact_sidebar")
