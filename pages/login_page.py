"""
登录页面 — 处理登录表单提交和错误验证。
"""
import allure
from pages.base_page import BasePage


class LoginPage(BasePage):

    # 常见登录页元素选择器（兼容多种UI框架）
    USERNAME_INPUT = "input[placeholder*='用户名'], input[placeholder*='账号'], input[name='username'], #username, [data-testid='username-input']"
    PASSWORD_INPUT = "input[placeholder*='密码'], input[name='password'], #password, [data-testid='password-input']"
    LOGIN_BTN = "button:has-text('登录'), button:has-text('登 录'), button[type='submit'], [data-testid='login-btn']"
    ERROR_MSG = ".el-message--error, .ant-message-error, [class*='error'], .error-message, .login-error"

    def navigate(self) -> None:
        super().navigate("/login")
        self.page.wait_for_load_state("networkidle")

    def fill_username(self, username: str) -> None:
        with allure.step(f"输入用户名: {username}"):
            self.page.locator(self.USERNAME_INPUT).first.fill(username)

    def fill_password(self, password: str) -> None:
        with allure.step("输入密码"):
            self.page.locator(self.PASSWORD_INPUT).first.fill(password)

    def click_login(self) -> None:
        with allure.step("点击登录按钮"):
            self.page.locator(self.LOGIN_BTN).first.click()

    def login(self, username: str, password: str) -> None:
        with allure.step(f"执行登录 — 用户: {username}"):
            self.fill_username(username)
            self.fill_password(password)
            self.click_login()

    def get_error_message(self) -> str | None:
        error = self.page.locator(self.ERROR_MSG)
        if error.count() > 0:
            return error.first.inner_text()
        return None

    def assert_login_success(self) -> None:
        self.page.wait_for_url("**/app**", timeout=15000)
        allure.attach(self.page.screenshot(type="png"), "登录成功", allure.attachment_type.PNG)

    def assert_login_error(self, expected_text: str = "") -> None:
        error_msg = self.get_error_message()
        if not error_msg:
            raise AssertionError("未显示错误提示")
        if expected_text and expected_text not in error_msg:
            raise AssertionError(f"期望错误包含 '{expected_text}'，实际: '{error_msg}'")
