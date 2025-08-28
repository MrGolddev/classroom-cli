      # gclass-cli

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/tests-pytest-orange.svg)]()

Command-line interface for **Google Classroom** and **Google Drive**.  
Lets you list courses, view assignments, upload files, and submit work—all from your terminal.


## Installation & setup

1. Create & activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\Activate.ps1
   # macOS/Linux: source .venv/bin/activate
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

3. Show paths where config/creds are stored:
   ```bash
   gclass paths
   ```

4. Place your Google API `credentials.json` there, then run:
   ```bash
   gclass auth
   ```

Now you’re ready—try:
```bash
gclass list-courses
```

---

## Full Setup (Google Cloud Project)

If Quickstart fails (like fresh accounts or new APIs), follow the full setup:

### Step 1. Make a Google Cloud project
- Go to [Google Cloud Console](https://console.cloud.google.com)  
- Click **New Project** → name it `gclass-cli`

### Step 2. Enable APIs
- Enable **Google Classroom API**  
- Enable **Google Drive API**

### Step 3. OAuth consent screen
- Choose **External** → fill details  
- Under **Test Users**, add your Gmail (the account with Classroom access)  

### Step 4. Create OAuth credentials
- Credentials → **Create Credentials > OAuth Client ID**  
- App type: **Desktop App**  
- Download the JSON as `credentials.json`

### Step 5. Put creds in CLI config
```bash
gclass paths
```
Copy the JSON into the printed path.

### Step 6. First auth
```bash
gclass auth
```
Log in, grant permissions. A `token.json` will be saved.  

Test it:
```bash
gclass list-courses
```

---

## Usage

Common commands:

- `gclass whoami` → display signed-in account  
- `gclass list-courses [--page-size N] [--pick]` → list courses / set default  
- `gclass list-students --course COURSE_ID` → show course students  
- `gclass list-assignments --course COURSE_ID` → show coursework & due dates  
- `gclass set-default --course COURSE_ID` → set default course  
- `gclass upload --file PATH` → upload a file to Drive  
- `gclass open [--course COURSE_ID] [--assignment COURSEWORK_ID]` → open in browser  
- `gclass submit --assignment COURSEWORK_ID --file PATH [--course COURSE_ID]` → turn in work  

---

## Example Workflow

```bash
# Pick a course
gclass list-courses --pick

# See assignments
gclass list-assignments --course 613975195696

# Submit work
gclass submit --assignment 790062231156 --file "report.pdf"
```

---

## Project Structure

- `src/gclass/cli.py` → CLI with Click & Rich  
- `src/gclass/auth.py` → OAuth + token handling  
- `src/gclass/config.py` → paths, settings, scopes  
- `src/gclass/services.py` → Classroom & Drive API helpers  

---

## Development

Run tests with:
```bash
pytest
```
