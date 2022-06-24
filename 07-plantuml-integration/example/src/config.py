from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    BASE_DIR = Path(__file__).resolve().parent
    PLANTUML_SERVER_URL = "http://localhost:8080/png/"
    CURRENT_TO_BE = "v1.1.0"


settings = Settings()
