"""See, edit, create and delete all of your Google Drive files"""
import os

from config.config import google_service
from models.google_drive_api import GoogleDriveAPI


CURRENT_DIR: str = os.path.dirname(__file__)
SERVICE_ACCOUNT_FILE = os.path.join(
    CURRENT_DIR, 'config', 'uptc-449511-a4a6cb956463.json'
)


def main():
    instance = GoogleDriveAPI(
        google_service.CREDENTIAL_EMAIL,
        SERVICE_ACCOUNT_FILE
    )
    result = instance.read_available_files()
    print(result)


if __name__ == '__main__':
    main()
