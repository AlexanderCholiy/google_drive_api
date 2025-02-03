import os

from dotenv import load_dotenv


CURRENT_DIR: str = os.path.dirname(__file__)
ENV_PATH: str = os.path.join(CURRENT_DIR, '.env')
load_dotenv(ENV_PATH)


class GoogleService:
    CREDENTIAL_EMAIL: str = os.getenv('CREDENTIAL_EMAIL')


class DbSettings:
    """Параметры подключения к БД."""
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: int = int(os.getenv('DB_PORT'))
    DB_USER: str = os.getenv('DB_USER')
    DB_PSWD: str = os.getenv('DB_PSWD')
    DB_NAME_TECH_PRIS: str = os.getenv('DB_NAME_TECH_PRIS')


google_service = GoogleService()
db_settings = DbSettings()
