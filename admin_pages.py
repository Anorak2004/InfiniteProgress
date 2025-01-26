import streamlit as st

class AdminPages:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def admin_dashboard(self):
        if "user" in st.session_state and st.session_state["user"][4]:
            st.title("无限进步 - 管理员后台")
            st.write("欢迎进入管理员后台，可以管理用户、审核记录和分配奖励。")
            # 管理员功能：显示所有用户
            users = self.db_manager.fetch_query("SELECT id, username, points, is_admin FROM users")
            st.write("### 用户列表")
            for user in users:
                st.write(f"用户ID: {user[0]}, 用户名: {user[1]}, 积分: {user[2]}, 管理员: {'是' if user[3] else '否'}")
        else:
            st.experimental_set_query_params(page="login")
            st.error("请先登录管理员账号。")
            st.stop()