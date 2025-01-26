from database_manager import DatabaseManager
from user_manager import UserManager
from user_pages import UserPages
from admin_pages import AdminPages
import streamlit as st

if __name__ == "__main__":
    db_path = "data/main.db"
    db_manager = DatabaseManager(db_path)
    user_manager = UserManager(db_manager)
    user_pages = UserPages(db_manager, user_manager)
    admin_pages = AdminPages(db_manager)

    st.sidebar.title("无限进步 - 菜单")

    query_params = st.experimental_get_query_params()
    page = query_params.get("page", ["login"])[0]

    if "user" not in st.session_state:
        if page == "register":
            user_pages.register_page()
        else:
            user_pages.login_page()
    else:
        user = st.session_state["user"]
        if user[4]:  # 管理员
            if page == "admin":
                admin_pages.admin_dashboard()
            else:
                st.experimental_set_query_params(page="admin")
        else:
            if page == "dashboard":
                user_pages.dashboard_page()
            elif page == "upload":
                user_pages.upload_record_page()
            else:
                st.experimental_set_query_params(page="dashboard")
