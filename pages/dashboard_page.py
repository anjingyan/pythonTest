"""
仪表板/首页 — 验证登录后跳转、菜单导航、数据概览。
"""
import allure
from pages.base_page import BasePage


class DashboardPage(BasePage):

    # 菜单选择器
    SIDEBAR_MENU = ".el-menu, .ant-menu, .sidebar-menu, nav, [class*='sidebar'], [class*='menu']"
    MENU_ITEM = "li, .el-menu-item, .ant-menu-item, a[class*='menu']"

    def navigate(self) -> None:
        super().navigate("/dashboard")
        self.page.wait_for_load_state("networkidle")

    def is_loaded(self) -> bool:
        return self.page.locator(
            ".dashboard, [class*='home'], [class*='welcome'], h1, .page-title"
        ).first.is_visible()

    # ---------- 菜单导航 ----------
    def get_menu_items(self) -> list[str]:
        sidebar = self.page.locator(self.SIDEBAR_MENU)
        items = sidebar.locator(self.MENU_ITEM).all()
        return [item.inner_text().strip() for item in items if item.inner_text().strip()]

    def click_menu(self, menu_text: str) -> None:
        with allure.step(f"点击菜单: {menu_text}"):
            sidebar = self.page.locator(self.SIDEBAR_MENU)
            sidebar.get_by_text(menu_text).first.click()
            self.page.wait_for_load_state("networkidle")

    def go_to_inbound(self) -> None:
        self.click_menu("入库")
        from pages.inbound_page import InboundPage
        return InboundPage(self.page)

    def go_to_outbound(self) -> None:
        self.click_menu("出库")
        from pages.outbound_page import OutboundPage
        return OutboundPage(self.page)

    def go_to_inventory(self) -> None:
        self.click_menu("库存")
        from pages.inventory_page import InventoryPage
        return InventoryPage(self.page)

    # ---------- 用户信息 ----------
    def get_current_user(self) -> str | None:
        user_info = self.page.locator(".user-info, .user-name, [class*='avatar'] + span, .header-user")
        if user_info.count() > 0:
            return user_info.first.inner_text()
        return None

    def logout(self) -> None:
        with allure.step("退出登录"):
            self.page.locator(".user-avatar, .avatar, [class*='logout'], button:has-text('退出')").first.click()
            self.page.get_by_text("退出登录", exact=False).click()
