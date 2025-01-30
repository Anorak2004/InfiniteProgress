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

        c.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT NULL,  -- 允许为空
                end_time TEXT NULL,    -- 允许为空
                activity_type TEXT NOT NULL,
                points REAL NOT NULL,
                approved INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # 奖励表
        c.execute('''CREATE TABLE IF NOT EXISTS rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reward_name TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')

        # 奖品池表（增加 is_hidden 字段）
        c.execute('''CREATE TABLE IF NOT EXISTS prize_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prize_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            weight REAL NOT NULL DEFAULT 1.0,
            description TEXT,
            image_url TEXT,
            is_hidden INTEGER DEFAULT 0  -- 0: 可见, 1: 隐藏
        )''')

        # 兑换商品表
        c.execute('''
                    CREATE TABLE IF NOT EXISTS redeemable_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_name TEXT NOT NULL,
                        points_required INTEGER NOT NULL,
                        stock INTEGER NOT NULL DEFAULT 0,
                        description TEXT,
                        image_url TEXT
                    )
                ''')

        # 兑换记录表
        c.execute('''
                    CREATE TABLE IF NOT EXISTS redemptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        item_id INTEGER NOT NULL,
                        redeem_date TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        admin_comment TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(item_id) REFERENCES redeemable_items(id)
                    )
                ''')

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

    # def fetch_prizes(self):
    #     query = "SELECT id, prize_name, quantity FROM prize_pool WHERE quantity > 0"
    #     return self.fetch_query(query)

    def update_prize_quantity(self, prize_id, new_quantity):
        query = "UPDATE prize_pool SET quantity = ? WHERE id = ?"
        self.execute_query(query, (new_quantity, prize_id))

    def fetch_prizes(self, include_hidden=False):
        """ 获取奖品，默认不包含隐藏奖品 """
        query = "SELECT id, prize_name, quantity, weight, description, image_url, is_hidden FROM prize_pool"
        if not include_hidden:
            query += " WHERE is_hidden = 0"
        return self.fetch_query(query)

    # 添加商品
    def add_redeemable_item(self, item_name, points_required, stock, description="", image_url=""):
        query = "INSERT INTO redeemable_items (item_name, points_required, stock, description, image_url) VALUES (?, ?, ?, ?, ?)"
        self.execute_query(query, (item_name, points_required, stock, description, image_url))

    # 获取所有可兑换商品
    def fetch_redeemable_items(self):
        query = "SELECT id, item_name, points_required, stock, description, image_url FROM redeemable_items WHERE stock > 0"
        return self.fetch_query(query)

    # 兑换商品（减少库存）
    def redeem_item(self, user_id, item_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # 获取商品信息
        c.execute("SELECT points_required, stock FROM redeemable_items WHERE id = ?", (item_id,))
        item = c.fetchone()
        if not item or item[1] <= 0:
            conn.close()
            return "商品库存不足或不存在"

        points_required, stock = item

        # 获取用户积分
        c.execute("SELECT points FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        if not user or user[0] < points_required:
            conn.close()
            return "积分不足"

        # 扣除积分 & 更新库存
        new_points = user[0] - points_required
        c.execute("UPDATE users SET points = ? WHERE id = ?", (new_points, user_id))
        c.execute("UPDATE redeemable_items SET stock = stock - 1 WHERE id = ?", (item_id,))
        c.execute("INSERT INTO redemptions (user_id, item_id, redeem_date) VALUES (?, ?, datetime('now'))",
                  (user_id, item_id))

        conn.commit()
        conn.close()
        return "兑换成功"

    # 获取用户兑换记录
    def fetch_user_redemptions(self, user_id):
        query = '''
            SELECT r.id, i.item_name, r.redeem_date, r.status, r.admin_comment
            FROM redemptions r
            JOIN redeemable_items i ON r.item_id = i.id
            WHERE r.user_id = ?
        '''
        return self.fetch_query(query, (user_id,))