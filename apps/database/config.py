from os.path import sep, exists
from os import getcwd
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = sep.join([getcwd(), '.env'])

class DataBaseConfig(BaseSettings):
    POSTGRES_HOST: str = 'postgres'
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = 'wallets'
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres_password'
    model_config = SettingsConfigDict(
        env_file=env_file
    )
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

database_config = DataBaseConfig()