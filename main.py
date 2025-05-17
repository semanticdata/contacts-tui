"""
Main entry point for the Textual Contacts application.

This module initializes and runs the Textual-based contacts management application.
"""

import sys
from typing import NoReturn

from screens import ContactsApp


def main() -> None:
    """Run the Textual Contacts application.

    Handles application startup, execution, and graceful shutdown.
    """
    try:
        app = ContactsApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


def handle_exception(exc_type, exc_value, exc_traceback) -> NoReturn:
    """Handle uncaught exceptions by printing them to stderr."""
    import traceback

    # Skip if the exception is a keyboard interrupt (handled by main)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.exit(0)

    print("\nUnhandled exception:", file=sys.stderr)
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    # Set up global exception handler
    import sys

    sys.excepthook = handle_exception

    # Run the application
    main()
