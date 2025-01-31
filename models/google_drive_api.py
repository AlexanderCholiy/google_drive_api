from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError


class GoogleDriveAPI:
    """Класс для работы с Google Drive API."""

    SCOPES: list[str] = [
        'https://www.googleapis.com/auth/drive.metadata.readonly'
    ]

    def __init__(self, credential_email: str, file_key_path: str):
        """
        Инициализация класса.

        Parameters:
        ----------
        credential_email: Имя сервисного аккаунта Google.
        file_key_path: Путь к JSON файлу с токеном доступа к сервисному
        аккаунту.
        """
        self.service_account = credential_email
        self.file_key_path = file_key_path
        self.credentials = self._get_credentials()
        self.service: Resource = build(
            'drive', 'v3', credentials=self.credentials
        )

    def _get_credentials(self) -> Credentials:
        """Получение учетных данных из файла."""
        try:
            return Credentials.from_service_account_file(
                self.file_key_path, scopes=self.SCOPES
            )
        except Exception as e:
            print(f'Ошибка при загрузке учетных данных:\n{e}')
            raise

    def read_available_files(self) -> list[dict[str, str]]:
        """Чтение доступных файлов из Google Drive."""
        try:
            results = self.service.files().list(
                pageSize=1000,
                fields='nextPageToken, files(id, name, mimeType)'
            ).execute()
            files = results.get('files', [])
            return files
        except HttpError as error:
            print(f"Ошибка при получении файлов:\n{error}")
            raise
