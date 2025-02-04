import pandas as pd

from pandas import DataFrame
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


SCOPES: list[str] = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/spreadsheets.readonly',
]

MIME_TYPES: dict[str, str] = {
    'xlsx': (
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ),
    'docx': (
        'application/vnd.openxmlformats-officedocument.wordprocessingml' +
        '.document'
    )
}


class GoogleDriveAPI:
    """Класс для работы с Google Drive API."""

    def __init__(
        self, credential_email: str, file_key_path: str
    ):
        """
        Parameters:
        ----------
        credential_email: Имя сервисного аккаунта Google.
        file_key_path: Путь к JSON файлу с токеном доступа к сервисному
        аккаунту.
        """
        self.service_account = credential_email
        self.file_key_path = file_key_path
        self.credentials = self._get_credentials(SCOPES)

        self.service: Resource = build(
            'drive', 'v3', credentials=self.credentials
        )
        self.sheets_service: Resource = build(
            'sheets', 'v4', credentials=self.credentials
        )

    def _get_credentials(self, scopes: list[str]) -> Credentials:
        """Получение учетных данных из файла."""
        try:
            return Credentials.from_service_account_file(
                self.file_key_path, scopes=scopes
            )
        except Exception as e:
            print(f'Ошибка при загрузке учетных данных:\n{e}')
            raise

    def read_available_files(self) -> list[dict[str, str]]:
        """Чтение доступных файлов из Google Drive."""
        try:
            results: dict[str, str] = self.service.files().list(
                pageSize=100,
                fields='nextPageToken, files(id, name, mimeType)'
            ).execute()

            nextPageToken = results.get('nextPageToken')
            while nextPageToken:
                nextPage: dict[str, str] = self.service.files().list(
                    pageSize=10,
                    fields='nextPageToken, files(id, name, mimeType, parents)',
                    pageToken=nextPageToken
                ).execute()
                nextPageToken = nextPage.get('nextPageToken')
                results['files'] = results['files'] + nextPage['files']
            files = results.get('files', [])
            return files
        except HttpError as error:
            print(f"Ошибка при получении файлов:\n{error}")
            raise

    def download_google_sheets_and_docs(
        self, file_id: str, file_save_path: str
    ):
        """
        Скачивание google docs и google sheets с конвертированием в word
        (.docx) или excel (.xlsx).

        Parameters:
        ----------
        file_id: ID файла (есть в ссылке на файл).
        file_save_path: Путь к файлу.
        """
        file_metadata = self.service.files().get(fileId=file_id).execute()
        mime_type = file_metadata.get('mimeType')
        if mime_type == 'application/vnd.google-apps.spreadsheet':
            export_mime_type = MIME_TYPES['xlsx']
        elif mime_type == 'application/vnd.google-apps.document':
            export_mime_type = MIME_TYPES['xlsx']
        else:
            raise ValueError('Неверный формат файла.')

        request = self.service.files().export_media(
            fileId=file_id, mimeType=export_mime_type
        )

        with open(file_save_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(
                    f'Загрузка {file_save_path}: ' +
                    f'{int(status.progress() * 100)}%',
                    end='\r'
                )
            print()

    def read_google_sheet(
        self, spreadsheet_id: str, sheet_name_or_index: str | int
    ) -> DataFrame:
        """
        Чтение данных из Google Sheets и преобразование их в DataFrame.

        Parameters:
        ----------
        spreadsheet_id: ID таблицы Google Sheets (есть в ссылке документа).
        sheet_name_or_index: Имя листа для чтения (например, 'Sheet1') или его
        номер (например, 0).

        Returns:
        -------
        pandas.DataFrame: Данные таблицы в формате DataFrame.
        """
        spreadsheet = self.sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        sheets = spreadsheet.get('sheets', [])

        if isinstance(sheet_name_or_index, int):
            if sheet_name_or_index < 0 or sheet_name_or_index >= len(
                sheets
            ):
                print(
                    f'Индекс листа - {sheet_name_or_index} вне диапазона.'
                )
                raise
            sheet_name = sheets[sheet_name_or_index]['properties']['title']
        else:
            sheet_name = sheet_name_or_index

        sheet_result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=sheet_name
        ).execute()

        if 'values' not in sheet_result or not sheet_result['values']:
            return pd.DataFrame()
        try:
            df = pd.DataFrame(
                sheet_result['values'][1:], columns=sheet_result['values'][0]
            )
            return df
        except ValueError as error:
            print(
                'Не удалось преобразовать данные с Google Sheets ' +
                f'(лист {sheet_name}) в DataFrame:\n{error}'
            )
            raise
