import os

from dotenv import load_dotenv
from sqlmodel import create_engine

# Load environment variables
load_dotenv()

# Create db engine instance
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_ECHO = os.getenv("DB_ECHO")

mysql_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(mysql_url, echo=DB_ECHO)
