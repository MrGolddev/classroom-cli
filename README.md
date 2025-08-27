# gclass-cli

Command-line interface for Google Classroom and Drive.

## Installation

Install the package:
```bash
pip install -e .
```

## Authentication

**Step 1. Make a Google Cloud project**

Go to [Google Cloud Console](https://console.cloud.google.com) and sign in with the same Google account you use for Classroom. Click the project dropdown → **New Project** → name it something like `gclass-cli`.

**Step 2. Enable the APIs**

Inside your new project:

1. Go to **APIs & Services > Library**.
2. Search for and enable:
   - **Google Classroom API**
   - **Google Drive API** (needed for file submissions)

**Step 3. OAuth consent screen**

Go to **APIs & Services > OAuth consent screen**. Choose **External** and fill in app name, support email, etc. Under **Test Users**, add your Gmail (the one that has Classroom access). If you don’t add yourself, login will fail.

**Step 4. Create OAuth credentials**

Go to **APIs & Services > Credentials**. Click **Create Credentials > OAuth Client ID**, choose **Desktop App**, name it `gclass-cli`, and click **Create**. Download the JSON file—this is your `credentials.json`.

**Step 5. Put creds in your CLI config**

Run:

```bash
gclass paths
```

It prints something like:

```
Config dir:       C:\Users\<you>\AppData\Local\gclass-cli
credentials.json: C:\Users\<you>\AppData\Local\gclass-cli\credentials.json
```

Copy the downloaded `credentials.json` file into that path.

**Step 6. First auth**

Run:

```bash
gclass auth
```

A browser window opens—log in with your Classroom account and allow permissions. A `token.json` is stored alongside your credentials. Now you’re authenticated; try:

```bash
gclass list-courses
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
