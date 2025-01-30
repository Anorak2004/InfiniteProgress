# app.py
import streamlit as st

from admin_pages import AdminPages
from database_manager import DatabaseManager
from user_manager import UserManager
from user_pages import UserPages

if __name__=="__main__":
    db_path = "data/data.db"
    db_manager = DatabaseManager(db_path)
    user_manager = UserManager(db_manager)
    user_pages = UserPages(db_manager, user_manager)
    admin_pages = AdminPages(db_manager)

    st.sidebar.title("无限进步 - 菜单")

    # 登出按钮
    if "is_logged_in" in st.session_state and st.session_state["is_logged_in"]:
        if st.sidebar.button("退出登录"):
            st.session_state.clear()
            st.session_state["page"] = "login"
            st.rerun()

    # 页面路由
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    page = st.session_state["page"]

    if page == "login":
        user_pages.login_page()
    elif page == "register":
        user_pages.register_page()
    elif page == "dashboard":
        user_pages.dashboard_page()
    elif page == "upload":
        user_pages.upload_record_page()
    elif page == "lottery":
        user_pages.lottery_page()
    elif page == "admin":
        admin_pages.admin_dashboard()
    elif page == "redemption":
        user_pages.redemption_page()

