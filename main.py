#!/usr/bin/env python3
import sys
from screens import ContactsApp
from config import APP_DATA_DIR

def main():
    try:
        app = ContactsApp()
        app.run()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
