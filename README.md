# Textual Contacts

A modern terminal user interface (TUI) application for managing contacts, built with Python, Pydantic, and Textual.

## Features

- Add, view, edit, and delete contacts
- Clean and intuitive terminal interface
- Data validation using Pydantic
- Modern UI components with Textual

## Usage

Run the application:

```bash
uv run main.py
```

Keyboard shortcuts:

- `a`: Add a new contact
- `d`: Delete selected contact
- `e`: Edit selected contact
- `q`: Quit application

## Useful Commands

- `uv run ruff check`: Check code for linting errors
- `uv run ruff check --fix`: Automatically fix linting errors
- `uv run ruff format`: Format code according to project style guide
- `uv run ruff format --check`: Check if code is formatted according to project style guide

## Implementation Details

### Contact Model

Contacts are represented using Pydantic models with the following fields:

- `name`: string (required)
- `phone`: string (required)
- `email`: Optional[str]
- `notes`: Optional[str]
- `last_contacted`: Optional[datetime]

### Architecture

- **UI Layer**: Built with Textual, providing a responsive and modern terminal interface
- **Service Layer**: Handles contact management operations
- **Model Layer**: Uses Pydantic for data validation and type checking

### Key Design Features

- Loose Coupling: UI layer interacts only with the service layer
- Cross-Platform: Unicode-safe text handling
- Type Safety: Leverages Python's type hints and Pydantic validation
