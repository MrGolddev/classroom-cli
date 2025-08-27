from pathlib import Path
from platformdirs import user_config_dir
import json

APP_NAME = "gclass-cli"
APP_AUTHOR = "mrgolddev"

CONFIG_DIR = Path(user_config_dir(APP_NAME, APP_AUTHOR))
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

CREDENTIALS_PATH = CONFIG_DIR / "credentials.json"
TOKEN_PATH = CONFIG_DIR / "token.json"
SETTINGS_PATH = CONFIG_DIR / "settings.json"

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses",
    "https://www.googleapis.com/auth/classroom.coursework.me",
    "https://www.googleapis.com/auth/classroom.coursework.students",
    "https://www.googleapis.com/auth/classroom.rosters",
    "https://www.googleapis.com/auth/drive.file",
]

def load_settings():
    if SETTINGS_PATH.exists():
        txt = SETTINGS_PATH.read_text(encoding="utf-8")
        return json.loads(txt or "{}")
    return {}

def save_settings(d):
    SETTINGS_PATH.write_text(json.dumps(d, indent=2), encoding="utf-8")
