#! python3

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  port: int = 80
  host: str = "127.0.0.1"
  sqlurl: str = "sqlite:///database.db"
# sqlurl: str = "postgresql://user:password@hostspec:port/dbname?paramspec"
  salt: str = "webhooker"

settings = Settings(
  _env_prefix='FPT_', # Prefix for all env vars
  _env_file='.env', # Load from .env file
  _env_file_encoding='utf-8',
  _env_ignore_empty=True)

if __name__ == "__main__":
  pass
