"""See, edit, create and delete all of your Google Drive files"""
import os

from config.config import google_service
from models.google_drive_api import GoogleDriveAPI


CURRENT_DIR: str = os.path.dirname(__file__)
SERVICE_ACCOUNT_FILE = os.path.join(
    CURRENT_DIR, 'config', 'uptc-449511-a4a6cb956463.json'
)

def update_process(current_percent: float):
    print(f'Обновление данных в БД: {current_percent}%.', end='\r')


def run_update_poles_for_claims():
    instance = GoogleDriveAPI(
        google_service.CREDENTIAL_EMAIL,
        SERVICE_ACCOUNT_FILE
    )
    df = instance.read_google_sheet(
        '1sUR1rXN0TU3CcVMD6RnNxqXB7pzEBV74VvPNbojgDVI', 'Claims'
    )
    df = df.drop_duplicates().dropna()
    df.reset_index(drop=True, inplace=True)
    for row in df.itertuples(index=True):
        claim_number = str(row.claim_number.strip())
        claim_pole = str(row.claim_pole.strip())
        current_percent: float = round(100*(row.Index + 1)/len(df), 2)
        if not claim_number or not claim_pole or claim_number.lower() in (
            '-', 'б/н'
        ):
            update_process(current_percent)
            continue
        update_process(current_percent)
    print()


if __name__ == '__main__':
    run_update_poles_for_claims()
