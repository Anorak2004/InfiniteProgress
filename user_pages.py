import calendar
import random

import pandas as pd
import streamlit as st
from datetime import datetime, time, timedelta
import time as t


def return_to_dashboard():
    """ 返回仪表盘按钮 """
    if st.button("🏠 返回主页"):
        st.session_state["page"] = "dashboard"
        st.rerun()


def calculate_points(start_time, end_time, activity_type):
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


class UserPages:
    def __init__(self, db_manager, user_manager):
        self.db_manager = db_manager
        self.user_manager = user_manager

    def reveal_hidden_reward(self, reward_name):
        """ 解锁隐藏奖品 """
        real_name = self.db_manager.fetch_query("SELECT prize_name FROM prize_pool WHERE id=?", (reward_name,))[0][0]
        st.success(f"🎁 恭喜！你的隐藏奖品是：{real_name}")

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
        return_to_dashboard()

    def dashboard_page(self):
        """ 用户仪表盘页面（增加学习记录 & 日历打卡 & 已兑换奖品） """
        if "is_logged_in" not in st.session_state or not st.session_state["is_logged_in"]:
            st.error("请先登录！")
            return

        user = st.session_state["user"]
        st.title(f"📊 欢迎，{user[1]}！")

        # 1️⃣ 显示用户积分
        query = "SELECT points FROM users WHERE id=?"
        points = self.db_manager.fetch_query(query, (user[0],))[0][0]
        st.subheader(f"💰 你的当前积分：{points}")

        # 5️⃣ 按钮跳转
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📖 上传自律记录"):
                st.session_state["page"] = "upload"
                st.rerun()

        with col2:
            if st.button("🎁 进入兑换商城"):
                st.session_state["page"] = "redemption"
                st.rerun()

        # 2️⃣ 最近学习记录
        st.write("### 📝 最近学习记录")
        study_records_query = """
            SELECT date, start_time, end_time, points 
            FROM records 
            WHERE user_id=? AND activity_type='学习'
            ORDER BY date DESC 
            LIMIT 5
        """
        study_records = self.db_manager.fetch_query(study_records_query, (user[0],))

        if study_records:
            records_df = pd.DataFrame(study_records, columns=["日期", "开始时间", "结束时间", "积分"])
            st.dataframe(records_df, hide_index=True)
        else:
            st.write("❌ 暂无学习记录，快去学习吧！")

        # 3️⃣ 日历打卡（本月学习天数）
        st.write("### 📅 学习打卡日历")

        today = datetime.today()
        first_day = f"{today.year}-{today.month:02d}-01"
        last_day = f"{today.year}-{today.month:02d}-{calendar.monthrange(today.year, today.month)[1]}"

        calendar_query = """
            SELECT DISTINCT strftime('%Y-%m-%d', date) FROM records 
            WHERE user_id=? AND activity_type='学习' 
            AND date >= ? AND date <= ?
        """
        calendar_data = self.db_manager.fetch_query(calendar_query, (user[0], first_day, last_day))
        study_dates = {record[0] for record in calendar_data if record[0] is not None}

        # 生成日历表格
        cal = calendar.Calendar()
        days_matrix = list(cal.monthdayscalendar(today.year, today.month))

        calendar_html = "<table style='border-collapse: collapse; width: 100%; text-align: center;'>"
        calendar_html += "<tr>" + "".join(f"<th style='border: 1px solid black; padding: 5px;'> {day} </th>" for day in
                                          ["一", "二", "三", "四", "五", "六", "日"]) + "</tr>"

        for week in days_matrix:
            calendar_html += "<tr>"
            for day in week:
                if day == 0:  # 空白天数
                    calendar_html += "<td style='border: 1px solid black; padding: 10px; background-color: #f0f0f0;'> </td>"
                else:
                    date_str = f"{today.year}-{today.month:02d}-{day:02d}"
                    if date_str in study_dates:
                        bg_color = "#90EE90"  # 绿色，表示已学习
                        tooltip = "✅ 已学习"
                    else:
                        bg_color = "#ffcccb"  # 红色，未学习
                        tooltip = "❌ 未学习"
                    calendar_html += f"<td style='border: 1px solid black; padding: 10px; background-color: {bg_color};' title='{tooltip}'> {day} </td>"
            calendar_html += "</tr>"

        calendar_html += "</table>"
        st.markdown(calendar_html, unsafe_allow_html=True)

        # 4️⃣ 已兑换奖品
        st.write("### 🎁 已兑换奖品")
        rewards_query = """
            SELECT i.item_name, i.description, i.image_url, r.redeem_date
            FROM redemptions r
            JOIN redeemable_items i ON r.item_id = i.id
            WHERE r.user_id = ?
            ORDER BY r.redeem_date DESC
        """
        rewards = self.db_manager.fetch_query(rewards_query, (user[0],))

        if rewards:
            for reward in rewards:
                st.subheader(f"🏆 {reward[0]}")  # 奖品名称
                st.write(f"📖 描述：{reward[1]}")  # 奖品描述
                if reward[2]:  # 图片URL
                    st.image(reward[2], use_container_width=True)
                st.write(f"📅 兑换时间：{reward[3]}")
                st.write("---")
        else:
            st.write("❌ 你还没有兑换任何奖品")

    def upload_record_page(self):
        """ 自律记录上传页面（确保学习记录包含时间段） """
        if "is_logged_in" not in st.session_state or not st.session_state["is_logged_in"]:
            st.error("请先登录！")
            return

        user = st.session_state["user"]
        st.title("📖 上传自律记录")

        date = st.date_input("📅 请选择记录日期", value=datetime.today())

        # 1️⃣ 早睡 & 早起复选框（无需具体时间）
        col1, col2 = st.columns(2)
        with col1:
            early_sleep = st.checkbox("🌙 我昨晚23:00前睡觉（+1积分）")
        with col2:
            early_wake = st.checkbox("🌞 我今天7:30前起床（+1积分）")

        # 2️⃣ 选择学习时间段
        # 查询最近一次学习记录的结束时间
        last_record_query = """
                SELECT end_time FROM records 
                WHERE user_id = ? AND activity_type='学习' 
                ORDER BY date DESC, end_time DESC LIMIT 1
            """
        last_record = self.db_manager.fetch_query(last_record_query, (user[0],))

        # 计算默认开始时间
        if last_record and last_record[0][0]:  # 有历史记录
            default_start_time = datetime.strptime(last_record[0][0], "%H:%M").time()
        else:  # 没有历史记录，默认当前小时
            now = datetime.now()
            default_start_time = (now.replace(minute=0, second=0, microsecond=0)).time()

        # 默认结束时间（+1 小时）
        default_end_time = (datetime.combine(datetime.today(), default_start_time) + timedelta(minutes=40)).time()

        # 选择学习时间段
        st.write("⏳ 请选择学习时间段（至少 40 分钟）")
        start_time = st.time_input("📍 开始时间", value=default_start_time)
        end_time = st.time_input("📍 结束时间", value=default_end_time)

        # 计算学习时长
        study_points = 0
        study_duration = 0

        if start_time and end_time:
            start_dt = datetime.combine(datetime.today(), start_time)
            end_dt = datetime.combine(datetime.today(), end_time)

            if end_dt > start_dt:  # 确保时间合法
                study_duration = (end_dt - start_dt).seconds // 60  # 计算分钟数
                study_points = (study_duration // 40) * 5  # 40分钟+5积分
            else:
                st.error("⛔ 结束时间必须晚于开始时间！")

        # 计算总积分
        sleep_points = 1 if early_sleep else 0
        wake_points = 1 if early_wake else 0
        total_points = study_points + sleep_points + wake_points

        st.subheader(f"💰 本次可获得积分：{total_points}")

        if st.button("✅ 提交记录"):
            if 0 < study_duration < 40:
                st.error("⛔ 学习时间至少 40 分钟才能获得积分！")
                return

            # 记录早睡 & 早起（如有）
            if early_sleep:
                self.db_manager.execute_query(
                    "INSERT INTO records (user_id, date, start_time, end_time, activity_type, points, approved) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user[0], str(date), None, None, "早睡", 1, 1)
                )

            if early_wake:
                self.db_manager.execute_query(
                    "INSERT INTO records (user_id, date, start_time, end_time, activity_type, points, approved) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user[0], str(date), None, None, "早起", 1, 1)
                )

            # 记录学习时间段（如有）
            if study_duration >= 40:
                self.db_manager.execute_query(
                    "INSERT INTO records (user_id, date, start_time, end_time, activity_type, points, approved) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user[0], str(date), str(start_time), str(end_time), "学习", study_points, 1)
                )

            # 更新用户总积分
            self.db_manager.execute_query(
                "UPDATE users SET points = points + ? WHERE id = ?",
                (total_points, user[0])
            )

            st.success(f"🎉 记录上传成功！总积分 +{total_points}")
            st.session_state["page"] = "dashboard"
            st.rerun()

        # 3️⃣ 返回仪表盘
        if st.button("🏠 返回仪表盘"):
            st.session_state["page"] = "dashboard"
            st.rerun()

    # user_pages.py
    def lottery_page(self):
        if "is_logged_in" in st.session_state and st.session_state["is_logged_in"]:
            user = st.session_state["user"]
            st.title("无限进步 - 抽奖")

            # 获取用户积分
            query = "SELECT points FROM users WHERE id=?"
            points = self.db_manager.fetch_query(query, (user[0],))[0][0]
            st.subheader(f"您的当前积分：{points}")

            # 获取奖品（排除隐藏奖品）
            prizes = self.db_manager.fetch_prizes(include_hidden=False)
            if not prizes:
                st.warning("奖品池为空，稍后再试！")
                return

            # 显示奖品池
            st.write("### 🎁 当前奖品池：")
            for prize in prizes:
                st.subheader(f"🏆 {prize[1]}")
                st.write(f"📦 剩余数量：{prize[2]}")
                if prize[4]:
                    st.write(f"📝 描述：{prize[4]}")
                if prize[5]:
                    st.image(prize[5], use_container_width=True)

            # 抽奖按钮
            if st.button("🎰 立即抽奖"):
                if points < 10:
                    st.error("您的积分不足，至少需要 10 积分！")
                else:
                    with st.spinner("🎡 正在抽奖中..."):
                        t.sleep(2)  # 模拟抽奖过程

                    # 获取所有奖品（包括隐藏奖品）
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

                    # 记录中奖
                    self.db_manager.execute_query(
                        "INSERT INTO rewards (user_id, reward_name, date) VALUES (?, ?, ?)",
                        (user[0], prize_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    )

                    # **✨ 中奖反馈**
                    st.balloons()  # 🎈 放气球动画
                    st.success(f"🎉 恭喜您抽中奖品：{prize_name}！")

                    if is_hidden:
                        st.info("🎁 这是一个隐藏奖品，快去‘已获得的奖品’查看你的惊喜！")

                    st.session_state["page"] = "lottery"
                    st.rerun()
        else:
            st.session_state["page"] = "login"
            st.error("请先登录")
            st.rerun()

    def redemption_page(self):
        if "is_logged_in" not in st.session_state or not st.session_state["is_logged_in"]:
            st.error("请先登录！")
            return

        user = st.session_state["user"]
        st.title("🎁 兑换商城")

        # 获取用户积分
        query = "SELECT points FROM users WHERE id=?"
        points = self.db_manager.fetch_query(query, (user[0],))[0][0]
        st.subheader(f"💰 你的积分：{points}")

        # 显示可兑换商品
        items = self.db_manager.fetch_redeemable_items()
        if not items:
            st.warning("暂无可兑换商品")
            return_to_dashboard()
            return

        for item in items:
            st.subheader(item[1])
            st.write(f"💎 所需积分：{item[2]}")
            st.write(f"📦 剩余库存：{item[3]}")
            if item[4]:
                st.write(f"📖 介绍：{item[4]}")
            if item[5]:
                st.image(item[5], use_container_width=True)

            if st.button(f"兑换 {item[1]}", key=f"redeem_{item[0]}"):
                message = self.db_manager.redeem_item(user[0], item[0])
                st.success(message)
                st.rerun()

        return_to_dashboard()
