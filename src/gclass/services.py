from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from .auth import get_credentials

def classroom_service():
    creds = get_credentials()
    return build("classroom", "v1", credentials=creds)

def drive_service():
    creds = get_credentials()
    return build("drive", "v3", credentials=creds)

def media_upload(path):
    return MediaFileUpload(path, resumable=True)
