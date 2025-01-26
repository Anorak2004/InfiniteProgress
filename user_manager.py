import sqlite3


class UserManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def login(self, username, password):
        query = "SELECT * FROM users WHERE username=? AND password=?"
        user = self.db_manager.fetch_query(query, (username, password))
        return user[0] if user else None

    def register(self, username, password, is_admin=0):
        try:
            query = "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)"
            self.db_manager.execute_query(query, (username, password, is_admin))
            return "用户注册成功！"
        except sqlite3.IntegrityError:
            return "用户名已存在！"