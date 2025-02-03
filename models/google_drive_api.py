import io

import pandas as pd

from pandas import DataFrame
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError


SCOPES: list[str] = [
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
        Скачивание google docs и google sheets с конвертированием в word или
        excel.
        """
        request = self.service.files().get_media(fileId=file_id)
        print(request)

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
        try:
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

            if not sheet_result:
                return pd.DataFrame()
            try:
                df = pd.DataFrame(sheet_result[1:], columns=sheet_result[0])
                return df
            except ValueError as error:
                print(
                    'Не удалось преобразовать данные с Google Sheets ' +
                    f'(лист {sheet_name}) в DataFrame:\n{error}'
                )
                raise

        except HttpError as error:
            print(f'Ошибка при получении данных из Google Sheets:\n{error}')
            raise
