# gclass-cli

Command-line interface for Google Classroom and Drive.

## Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\Activate.ps1
   # macOS/Linux: source .venv/bin/activate
   ```
2. Install the package:
   ```bash
   pip install -e .
   ```

## Authentication

1. Show configuration paths:
   ```bash
   gclass paths
   ```
2. Place your Google API `credentials.json` at the printed location.
3. Authorize the CLI:
   ```bash
   gclass auth
   ```

## Usage

Common commands include:

- `gclass whoami` – display the signed-in account
- `gclass list-courses [--page-size N] [--pick]` – list courses and optionally set a default
- `gclass list-students --course COURSE_ID` – show students in a course
- `gclass list-assignments --course COURSE_ID` – show coursework and due dates
- `gclass set-default --course COURSE_ID` – update the default course
- `gclass upload --file PATH` – upload a file to Drive
- `gclass open [--course COURSE_ID] [--assignment COURSEWORK_ID]` – open a course or assignment in the browser
- `gclass submit --assignment COURSEWORK_ID --file PATH [--course COURSE_ID]` – upload and turn in work

The CLI stores settings and tokens in the paths shown by `gclass paths`.

## Project structure

- `src/gclass/cli.py` – command-line interface built with Click and Rich
- `src/gclass/auth.py` – OAuth flow and token management
- `src/gclass/config.py` – configuration directories, scopes and settings
- `src/gclass/services.py` – helpers for Classroom and Drive API clients

## Development

Run tests with:
```bash
pytest
```
