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

        # 奖品池表
        c.execute('''CREATE TABLE IF NOT EXISTS prize_pool (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prize_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL
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

    # 奖品池管理方法
    def add_prize(self, prize_name, quantity):
        query = "INSERT INTO prize_pool (prize_name, quantity) VALUES (?, ?)"
        self.execute_query(query, (prize_name, quantity))

    def fetch_prizes(self):
        query = "SELECT id, prize_name, quantity FROM prize_pool WHERE quantity > 0"
        return self.fetch_query(query)

    def update_prize_quantity(self, prize_id, new_quantity):
        query = "UPDATE prize_pool SET quantity = ? WHERE id = ?"
        self.execute_query(query, (new_quantity, prize_id))
