# config.py
import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

class Config:
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    POLYGON_API_KEY = os.environ['POLYGON_API_KEY']
    DATABASE_NAME = 'database.sqlite'
    TICKERS_FILE = 'Tickers.csv'
