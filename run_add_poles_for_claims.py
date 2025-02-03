"""See, edit, create and delete all of your Google Drive files"""
import os

from config.config import google_service
from models.google_drive_api import GoogleDriveAPI


CURRENT_DIR: str = os.path.dirname(__file__)
SERVICE_ACCOUNT_FILE = os.path.join(
    CURRENT_DIR, 'config', 'uptc-449511-a4a6cb956463.json'
)


# def main():
#     instance = GoogleDriveAPI(
#         google_service.CREDENTIAL_EMAIL,
#         os.path.join(SERVICE_ACCOUNT_FILE, 'tmp.csv')
#     )
#     # print(instance.read_available_files())
#     instance.download_google_sheets_and_docs(
#         '1sUR1rXN0TU3CcVMD6RnNxqXB7pzEBV74VvPNbojgDVI',
#         CURRENT_DIR
#     )
#     # df = instance.read_google_sheet(
#     #     '1sUR1rXN0TU3CcVMD6RnNxqXB7pzEBV74VvPNbojgDVI', 'claims'
#     # )
#     # print(df)


# if __name__ == '__main__':
#     main()
