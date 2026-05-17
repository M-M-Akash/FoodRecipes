from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: str = "1521"
    db_sid: str = "XE"
    db_user: str = "SYSTEM"
    db_password: str = "secret"

    @property
    def db_url(self) -> str:
        return (
            f"oracle+oracledb://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_sid}"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
