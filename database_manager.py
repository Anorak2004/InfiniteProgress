import sqlite3
import os


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # 用户表
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            points REAL DEFAULT 0,
            is_admin INTEGER DEFAULT 0  -- 0 为普通用户，1 为管理员
        )''')

        # 学习记录表
        c.execute('''CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            points REAL NOT NULL,
            approved INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')

        # 奖励表
        c.execute('''CREATE TABLE IF NOT EXISTS rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reward_name TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')

        conn.commit()
        conn.close()

    def execute_query(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()
        conn.close()

    def fetch_query(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(query, params)
        results = c.fetchall()
        conn.close()
        return results