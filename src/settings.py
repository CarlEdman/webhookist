from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  fpt_port: int = 80
  fpt_host: str = "127.0.0.1"
  fpt_sqlurl: str = "sqlite:///database.db"
# postgresql://[user[:password]@][hostspec][:port][/dbname][?paramspec]

settings = Settings()
