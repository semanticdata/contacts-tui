import os

# Get the user's home directory
HOME_DIR = os.path.expanduser("~")

# Define the app's data directory
APP_DATA_DIR = os.path.join(HOME_DIR, ".contacts-tui")

# Define the contacts file path
CONTACTS_FILE = os.path.join(APP_DATA_DIR, "contacts.json")

# Ensure the data directory exists
os.makedirs(APP_DATA_DIR, exist_ok=True)