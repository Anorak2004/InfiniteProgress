import streamlit as st


class AdminPages:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def admin_dashboard(self):
        st.title("无限进步 - 管理员后台")

        tab1, tab2, tab3 = st.tabs(["👤 用户管理", "📖 积分记录管理", "🎁 奖品管理"])

        # 1️⃣ 用户管理
        with tab1:
            st.subheader("👤 用户管理")
            users = self.db_manager.fetch_query("SELECT id, username, points, is_admin FROM users")

            for user in users:
                st.write(
                    f"**用户ID:** {user[0]} | **用户名:** {user[1]} | **积分:** {user[2]} | {'管理员' if user[3] else '普通用户'}")

                if not user[3]:  # 禁止修改管理员积分
                    new_points = st.number_input(f"修改 {user[1]} 的积分", value=user[2], key=f"points_{user[0]}")
                    if st.button(f"更新 {user[1]} 的积分", key=f"update_{user[0]}"):
                        self.db_manager.execute_query(
                            "UPDATE users SET points = ? WHERE id = ?", (new_points, user[0])
                        )
                        st.success(f"✅ 成功更新 {user[1]} 的积分为 {new_points}")

        # 2️⃣ 积分记录管理
        with tab2:
            st.subheader("📖 积分记录管理")
            records = self.db_manager.fetch_query("""
                        SELECT r.id, u.username, r.date, r.start_time, r.end_time, r.activity_type, r.points, r.approved 
                        FROM records r JOIN users u ON r.user_id = u.id
                    """)

            for record in records:
                st.write(
                    f"**记录ID:** {record[0]} | **用户:** {record[1]} | **日期:** {record[2]} | **时间:** {record[3]}-{record[4]} | **活动:** {record[5]} | **积分:** {record[6]} | {'✅ 已审核' if record[7] else '⏳ 未审核'}")

                if not record[7]:  # 仅允许审核未审核记录
                    if st.button(f"审核记录 {record[0]}", key=f"approve_{record[0]}"):
                        self.db_manager.execute_query("UPDATE records SET approved = 1 WHERE id = ?", (record[0],))
                        st.success(f"✅ 记录 {record[0]} 已审核")

                # 允许管理员删除记录
                if st.button(f"🗑️ 删除记录 {record[0]}", key=f"delete_{record[0]}"):
                    self.db_manager.execute_query("DELETE FROM records WHERE id = ?", (record[0],))
                    st.warning(f"🚮 记录 {record[0]} 已删除")

        # 3️⃣ 奖品管理
        with tab3:
            st.subheader("🎁 奖品管理")

            # 查看奖品列表
            prizes = self.db_manager.fetch_query("SELECT id, item_name, points_required, stock FROM redeemable_items")

            for prize in prizes:
                st.write(
                    f"**奖品ID:** {prize[0]} | **名称:** {prize[1]} | **兑换积分:** {prize[2]} | **库存:** {prize[3]}")

                # 修改奖品积分
                new_price = st.number_input(f"🎟️ 设置 {prize[1]} 的兑换积分", value=prize[2], key=f"price_{prize[0]}")
                if st.button(f"💰 更新 {prize[1]} 兑换积分", key=f"update_price_{prize[0]}"):
                    self.db_manager.execute_query("UPDATE redeemable_items SET points_required = ? WHERE id = ?",
                                                  (new_price, prize[0]))
                    st.success(f"✅ {prize[1]} 的兑换积分已更新为 {new_price}")

                # 修改库存
                new_stock = st.number_input(f"📦 设置 {prize[1]} 的库存", value=prize[3], key=f"stock_{prize[0]}")
                if st.button(f"📊 更新 {prize[1]} 库存", key=f"update_stock_{prize[0]}"):
                    self.db_manager.execute_query("UPDATE redeemable_items SET stock = ? WHERE id = ?",
                                                  (new_stock, prize[0]))
                    st.success(f"✅ {prize[1]} 的库存已更新为 {new_stock}")

            st.write("---")
            st.subheader("➕ 添加新奖品")

            new_prize_name = st.text_input("🏆 奖品名称")
            new_prize_points = st.number_input("🎟️ 兑换积分", min_value=1, step=1)
            new_prize_stock = st.number_input("📦 奖品库存", min_value=1, step=1)
            new_prize_description = st.text_area("📖 奖品描述")
            new_prize_image = st.text_input("🖼️ 奖品图片URL（static/prizes/xxx.png）")

            if st.button("✅ 添加奖品"):
                if new_prize_name and new_prize_points > 0 and new_prize_stock > 0:
                    self.db_manager.execute_query(
                        "INSERT INTO redeemable_items (item_name, points_required, stock, description, image_url) VALUES (?, ?, ?, ?, ?)",
                        (new_prize_name, new_prize_points, new_prize_stock, new_prize_description, new_prize_image),
                    )
                    st.success(f"✅ 成功添加奖品: {new_prize_name}")
                else:
                    st.error("⚠️ 请输入完整的奖品信息！")

        # # 奖池管理
        # with tab4:
        #     st.subheader("奖池管理")
        #
        #     # 获取所有奖品（包含隐藏奖品）
        #     prizes = self.db_manager.fetch_prizes(include_hidden=True)
        #     for prize in prizes:
        #         st.write(
        #             f"奖品ID: {prize[0]}, 奖品名: {prize[1]}, 数量: {prize[2]}, 权重: {prize[3]}, 隐藏: {'是' if prize[6] else '否'}")
        #
        #         # 修改是否隐藏
        #         is_hidden_new = st.checkbox(f"隐藏 {prize[1]}", value=bool(prize[6]), key=f"hidden_{prize[0]}")
        #         if st.button(f"更新 {prize[1]} 的隐藏状态", key=f"update_hidden_{prize[0]}"):
        #             self.db_manager.execute_query("UPDATE prize_pool SET is_hidden = ? WHERE id = ?",
        #                                           (int(is_hidden_new), prize[0]))
        #             st.success(f"奖品 {prize[1]} 的隐藏状态已更新")
        #
        #         # 修改奖品权重
        #         new_weight = st.number_input(
        #             f"设置 {prize[1]} 的概率权重",
        #             value=float(prize[3]),  # 确保 value 是 float
        #             min_value=0.0,  # 确保 min_value 是 float
        #             step=0.1,  # 确保 step 是 float
        #             key=f"weight_{prize[0]}"
        #         )
        #         if st.button(f"更新 {prize[1]} 的概率权重", key=f"update_weight_{prize[0]}"):
        #             self.db_manager.execute_query(
        #                 "UPDATE prize_pool SET weight = ? WHERE id = ?", (new_weight, prize[0])
        #             )
        #             st.success(f"成功更新 {prize[1]} 的概率权重为 {new_weight}")
        #
        #     for prize in prizes:
        #         st.write(f"奖品ID: {prize[0]}, 奖品名: {prize[1]}, 数量: {prize[2]}")
        #
        #         # 修改奖品数量
        #         new_quantity = st.number_input(
        #             f"修改 {prize[1]} 的数量", value=prize[2], key=f"quantity_{prize[0]}"
        #         )
        #         if st.button(f"更新 {prize[1]} 的数量", key=f"update_prize_{prize[0]}"):
        #             self.db_manager.execute_query(
        #                 "UPDATE prize_pool SET quantity = ? WHERE id = ?", (new_quantity, prize[0])
        #             )
        #             st.success(f"奖品 {prize[1]} 的数量已更新为 {new_quantity}")
        #
        #     # 添加奖品
        #     st.write("---")
        #     st.write("添加新奖品")
        #     new_prize_name = st.text_input("奖品名称")
        #     new_prize_quantity = st.number_input("奖品数量", min_value=1, step=1)
        #     new_prize_weight = st.number_input("奖品权重", min_value=1, step=1)
        #     new_prize_description = st.text_area("奖品描述")
        #     new_prize_image = st.text_input("奖品图片URL")
        #
        #     if st.button("添加奖品"):
        #         if new_prize_name and new_prize_quantity > 0 and new_prize_weight > 0:
        #             self.db_manager.execute_query(
        #                 "INSERT INTO prize_pool (prize_name, quantity, weight, description, image_url) VALUES (?, ?, ?, ?, ?)",
        #                 (new_prize_name, new_prize_quantity, new_prize_weight, new_prize_description, new_prize_image),
        #             )
        #             st.success(f"成功添加奖品: {new_prize_name}")
        #         else:
        #             st.error("请输入完整有效的奖品信息")
        #
        #     # 显示和更新奖品
        #     prizes = self.db_manager.fetch_query(
        #         "SELECT id, prize_name, quantity, weight, description, image_url FROM prize_pool")
        #     for prize in prizes:
        #         st.write(f"奖品：{prize[1]}，数量：{prize[2]}，权重：{prize[3]}")
        #         st.text_area("奖品描述", value=prize[4], key=f"description_{prize[0]}")
        #         st.text_input("奖品图片URL", value=prize[5], key=f"image_{prize[0]}")
