import os

from dotenv import load_dotenv


CURRENT_DIR: str = os.path.dirname(__file__)
ENV_PATH: str = os.path.join(CURRENT_DIR, '.env')
load_dotenv(ENV_PATH)


class GoogleService:
    CREDENTIAL_EMAIL: str = os.getenv('CREDENTIAL_EMAIL')


google_service = GoogleService()
