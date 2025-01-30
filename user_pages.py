import random

import streamlit as st
from datetime import datetime, time


class UserPages:
    def __init__(self, db_manager, user_manager):
        self.db_manager = db_manager
        self.user_manager = user_manager

    def calculate_points(self, start_time, end_time, activity_type):
        points = 0
        start = datetime.combine(datetime.today(), start_time)
        end = datetime.combine(datetime.today(), end_time)
        total_hours = int((end - start).seconds / 3600)

        # 每小时未进行低价值娱乐+1分
        points += total_hours

        # 学习时间每小时再+1分
        if activity_type == "学习":
            points += total_hours

        # 早睡规则
        if end_time <= time(23, 0):
            extra_points = (23 - end_time.hour) * 0.5
            if end_time.minute == 0:
                points += extra_points

        # 早起规则
        if start_time < time(7, 30):
            extra_points = (7 - start_time.hour + 0.5) * 0.5
            if start_time.minute == 0:
                points += extra_points

        return points

    def login_page(self):
        st.title("无限进步 - 用户登录")
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        if st.button("登录"):
            user = self.user_manager.login(username, password)
            if user:
                st.session_state["user"] = user
                st.session_state["is_logged_in"] = True
                st.session_state["page"] = "admin" if user[4] else "dashboard"
                st.success("登录成功！正在跳转...")
                st.rerun()
            else:
                st.error("用户名或密码错误")
        if st.button("还没有账号？点击注册"):
            st.session_state["page"] = "register"
            st.rerun()

    def register_page(self):
        st.title("无限进步 - 用户注册")
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        if st.button("注册"):
            message = self.user_manager.register(username, password)
            st.success(message) if "成功" in message else st.error(message)

    def dashboard_page(self):
        if "is_logged_in" in st.session_state and st.session_state["is_logged_in"]:
            user = st.session_state["user"]
            st.title(f"无限进步 - 欢迎，{user[1]}！")

            # 实时从数据库获取积分
            query = "SELECT points FROM users WHERE id=?"
            points = self.db_manager.fetch_query(query, (user[0],))[0][0]
            st.subheader(f"您的积分：{points}")

            st.write("### 您的活动记录")
            query = """
                SELECT date, start_time, end_time, activity_type, points 
                FROM records 
                WHERE user_id=?
            """
            records = self.db_manager.fetch_query(query, (user[0],))
            for record in records:
                st.write(f"日期：{record[0]}，时间：{record[1]}-{record[2]}，活动：{record[3]}，积分：{record[4]}")

            # 获得奖品
            st.write("### 您获得的奖品")
            query = "SELECT reward_name, date FROM rewards WHERE user_id=?"
            rewards = self.db_manager.fetch_query(query, (user[0],))
            if rewards:
                for reward in rewards:
                    st.write(f"奖品：{reward[0]}，获得日期：{reward[1]}")
            else:
                st.write("您还没有获得奖品！")
        else:
            st.session_state["page"] = "login"
            st.error("请先登录")
            st.rerun()

    def upload_record_page(self):
        if "is_logged_in" in st.session_state and st.session_state["is_logged_in"]:
            user = st.session_state["user"]
            st.title("无限进步 - 上传活动记录")
            date = st.date_input("日期", value=datetime.today())
            start_time = st.time_input("开始时间")
            end_time = st.time_input("结束时间")
            activity_type = st.selectbox("活动类型", ["学习", "自律"])

            if st.button("提交记录"):
                points = self.calculate_points(start_time, end_time, activity_type)
                query = """
                    INSERT INTO records (user_id, date, start_time, end_time, activity_type, points) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                self.db_manager.execute_query(
                    query, (user[0], str(date), str(start_time), str(end_time), activity_type, points)
                )

                # 更新用户积分
                update_query = "UPDATE users SET points = points + ? WHERE id = ?"
                self.db_manager.execute_query(update_query, (points, user[0]))

                st.success(f"记录上传成功！本次获得积分：{points}")
                st.session_state["page"] = "dashboard"
                st.rerun()
        else:
            st.session_state["page"] = "login"
            st.error("请先登录")
            st.rerun()

    # user_pages.py
    def lottery_page(self):
        if "is_logged_in" in st.session_state and st.session_state["is_logged_in"]:
            user = st.session_state["user"]
            st.title("无限进步 - 抽奖")

            # 获取当前用户积分
            query = "SELECT points FROM users WHERE id=?"
            points = self.db_manager.fetch_query(query, (user[0],))[0][0]
            st.subheader(f"您的当前积分：{points}")

            # 只显示非隐藏奖品
            prizes = self.db_manager.fetch_prizes(include_hidden=False)
            if not prizes:
                st.warning("奖品池为空，稍后再试！")
                return

            # 显示奖品池（排除隐藏奖品）
            st.write("### 当前奖品池：")
            for prize in prizes:
                st.subheader(f"奖品：{prize[1]}")
                st.write(f"剩余数量：{prize[2]}")
                if prize[4]:
                    st.write(f"描述：{prize[4]}")
                if prize[5]:
                    st.image(prize[5], use_container_width=True)

            if st.button("抽奖"):
                if points < 10:
                    st.error("您的积分不足，至少需要 10 积分！")
                else:
                    # **抽取奖品（包含隐藏奖品）**
                    all_prizes = self.db_manager.fetch_prizes(include_hidden=True)
                    prize_weights = [prize[3] for prize in all_prizes]
                    selected_prize_index = random.choices(range(len(all_prizes)), weights=prize_weights, k=1)[0]
                    selected_prize = all_prizes[selected_prize_index]

                    prize_id, prize_name, quantity, weight, _, _, is_hidden = selected_prize

                    # 扣除积分
                    new_points = points - 10
                    self.db_manager.execute_query("UPDATE users SET points = ? WHERE id = ?", (new_points, user[0]))

                    # 更新奖品库
                    self.db_manager.execute_query("UPDATE prize_pool SET quantity = quantity - 1 WHERE id = ?",
                                                  (prize_id,))

                    # 添加到奖励记录
                    self.db_manager.execute_query(
                        "INSERT INTO rewards (user_id, reward_name, date) VALUES (?, ?, ?)",
                        (user[0], prize_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    )

                    if is_hidden:
                        st.success("恭喜！您抽中了一个神秘奖品，查看‘已获得的奖品’解锁惊喜！")
                    else:
                        st.success(f"恭喜您抽中奖品：{prize_name}！")

                    st.session_state["page"] = "lottery"
                    st.rerun()
        else:
            st.session_state["page"] = "login"
            st.error("请先登录")
            st.rerun()

