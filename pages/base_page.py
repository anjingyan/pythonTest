"""
页面对象基类 — 封装通用操作：导航、等待、元素交互、断言。
"""
import allure
from pathlib import Path
from playwright.sync_api import Page, Locator, expect


class BasePage:
    BASE_URL = "http://localhost:8080/app"

    def __init__(self, page: Page):
        self.page = page

    # ---------- 导航 ----------
    def navigate(self, path: str = "") -> None:
        url = f"{self.BASE_URL}{path}"
        with allure.step(f"导航到 {url}"):
            self.page.goto(url, wait_until="domcontentloaded")

    def get_current_url(self) -> str:
        return self.page.url

    # ---------- 等待 ----------
    def wait_for_url(self, pattern: str, timeout: int = 15000) -> None:
        self.page.wait_for_url(pattern, timeout=timeout)

    def wait_for_visible(self, locator, timeout: int = 10000) -> None:
        locator.wait_for(state="visible", timeout=timeout)

    def wait_for_load(self) -> None:
        self.page.wait_for_load_state("networkidle")

    # ---------- 元素查找 ----------
    def get_by_text(self, text: str, exact: bool = False) -> Locator:
        return self.page.get_by_text(text, exact=exact)

    def get_by_role(self, role: str, **kwargs) -> Locator:
        return self.page.get_by_role(role, **kwargs)

    def get_by_label(self, text: str) -> Locator:
        return self.page.get_by_label(text)

    def get_by_placeholder(self, text: str) -> Locator:
        return self.page.get_by_placeholder(text)

    def get_by_testid(self, testid: str) -> Locator:
        return self.page.get_by_test_id(testid)

    def get_input(self, label_text: str) -> Locator:
        """通过label文本定位input，适配常见组件库模式"""
        label = self.page.locator("label", has_text=label_text)
        input_id = label.get_attribute("for")
        if input_id:
            return self.page.locator(f"#{input_id}")
        return label.locator("input, textarea, select")

    # ---------- 交互 ----------
    def click(self, locator: Locator) -> None:
        locator.click()

    def fill(self, locator: Locator, value: str) -> None:
        locator.fill(value)

    def select_option(self, locator: Locator, value: str) -> None:
        locator.select_option(value)

    def type(self, locator: Locator, text: str, delay: int = 50) -> None:
        locator.type(text, delay=delay)

    # ---------- 断言 ----------
    def assert_visible(self, locator: Locator, message: str = "") -> None:
        expect(locator).to_be_visible()

    def assert_has_text(self, locator: Locator, text: str) -> None:
        expect(locator).to_contain_text(text)

    def assert_url_contains(self, text: str) -> None:
        expect(self.page).to_have_url(f"**{text}**")

    # ---------- 弹窗与提示 ----------
    def close_dialog(self) -> None:
        self.page.on("dialog", lambda dialog: dialog.accept())

    def get_toast_message(self) -> str | None:
        toast = self.page.locator(".el-message, .ant-message-notice, .toast, [class*=toast], [class*=notification]")
        if toast.count() > 0:
            return toast.first.inner_text()
        return None

    def wait_for_toast(self, timeout: int = 5000) -> str | None:
        toast = self.page.locator(".el-message, .ant-message-notice, .toast, [class*=toast], [class*=notification]")
        try:
            toast.first.wait_for(state="visible", timeout=timeout)
            return toast.first.inner_text()
        except Exception:
            return None

    # ---------- 表格操作 ----------
    def get_table_rows(self, table_locator: Locator = None) -> list[Locator]:
        """获取表格所有数据行"""
        if table_locator is None:
            table_locator = self.page.locator("table, .el-table, .ant-table")
        return table_locator.locator("tbody tr, .el-table__body tr, .ant-table-tbody tr").all()

    def find_row_by_text(self, text: str) -> Locator | None:
        """在表格中查找包含指定文本的行"""
        rows = self.get_table_rows()
        for row in rows:
            if text in (row.inner_text() or ""):
                return row
        return None

    def click_row_action(self, row_text: str, action_text: str) -> None:
        """在包含row_text的行中点击action按钮"""
        row = self.find_row_by_text(row_text)
        if row is None:
            raise ValueError(f"未找到包含 '{row_text}' 的表格行")
        row.get_by_text(action_text).click()

    # ---------- 滚动 ----------
    def scroll_to_bottom(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def scroll_into_view(self, locator: Locator) -> None:
        locator.scroll_into_view_if_needed()
