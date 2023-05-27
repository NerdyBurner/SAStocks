# database.py
import sqlite3
from config import Config

class Database:
    def __init__(self):
        self.connection = sqlite3.connect(Config.DATABASE_NAME)

    def save_article(self, article):
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO articles VALUES (?, ?, ?)', (article['title'], article['summary'], article['timestamp']))
        self.connection.commit()

    def save_sentiment(self, sentiment):
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO sentiments VALUES (?, ?)', (sentiment['ticker'], sentiment['score']))
        self.connection.commit()

    def get_article(self, id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM articles WHERE id = ?', (id,))
        return cursor.fetchone()

    def get_sentiment(self, id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM sentiments WHERE id = ?', (id,))
        return cursor.fetchone()

    def get_all_articles(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM articles')
        return cursor.fetchall()

    def get_all_sentiments(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM sentiments')
        return cursor.fetchall()
