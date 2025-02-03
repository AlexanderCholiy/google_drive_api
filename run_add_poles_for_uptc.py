import os

import pandas as pd

from config.config import google_service
from models.google_drive_api import GoogleDriveAPI
from database.db_conn import sql_queries
from database.requests.add_poles_for_claims_and_messages import (
    add_poles_for_claims_and_messages
)
from app.write_df_to_excel import write_df_to_excel


CURRENT_DIR: str = os.path.dirname(__file__)
SERVICE_ACCOUNT_FILE: str = os.path.join(
    CURRENT_DIR, 'config', 'uptc-449511-a4a6cb956463.json'
)
UPTC_FILE_DIR: str = os.path.join(
    CURRENT_DIR, 'data'
)
os.makedirs(UPTC_FILE_DIR, exist_ok=True)
UPTC_FILE_NAME: str = 'uptc.xlsx'
UPTC_FILE_PATH: str = os.path.join(UPTC_FILE_DIR, UPTC_FILE_NAME)


def update_process(current_percent: float):
    print(f'Обновление данных в БД: {current_percent}%', end='\r')


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
    df = df.mask(df.isna() | (df == ''), None)

    diff_df = None
    if any(f == UPTC_FILE_NAME for f in os.listdir(UPTC_FILE_DIR)):
        try:
            archive_df = pd.read_excel(UPTC_FILE_PATH, sheet_name='Claims')
            archive_df = archive_df.mask(
                archive_df.isna() | (archive_df == ''), None
            )
            merged = df.merge(archive_df, how='outer', indicator=True)
            diff_df = merged[merged['_merge'] != 'both'].drop(
                columns=['_merge']
            )
        except ValueError:
            pass

    diff_df = df if diff_df is None else diff_df

    for row in diff_df.itertuples(index=True):
        claim_number = str(row.claim_number.strip())
        claim_pole = str(row.claim_pole.strip())
        current_percent: float = round(100*(row.Index + 1)/len(df), 2)
        if not claim_number or not claim_pole or claim_number.lower() in (
            '-', 'б/н'
        ):
            update_process(current_percent)
            continue

        sql_queries(
            add_poles_for_claims_and_messages(1000, claim_number, claim_pole)
        )

        update_process(current_percent)

    if len(diff_df) > 0:
        print()
        write_df_to_excel(UPTC_FILE_PATH, df, 'Claims')


if __name__ == '__main__':
    run_update_poles_for_claims()
