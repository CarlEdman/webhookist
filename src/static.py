#! python3

from fastapi.staticfiles import StaticFiles
from settings import settings

static = StaticFiles(directory="static")

if __name__ == "__main__":
  pass
