#! python3

from settings import settings

from fastapi.security import OAuth2PasswordBearer

securityscheme = OAuth2PasswordBearer(tokenUrl="token")

if __name__ == "__main__":
  pass

