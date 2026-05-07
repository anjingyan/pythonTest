"""
项目根级conftest — 提供全局fixtures：浏览器、页面、上下文、截图、 allure集成。
"""
import pytest
import allure
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext


ROOT_DIR = Path(__file__).parent


# ---------- 钩子 ----------
def pytest_runtest_setup(item):
    """动态添加allure标签"""
    for marker in item.iter_markers():
        if marker.name not in ("parametrize",):
            allure.dynamic.tag(marker.name)


# ---------- 全局fixtures ----------
@pytest.fixture(scope="session")
def browser_context_args():
    """自定义浏览器启动上下文"""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "locale": "zh-CN",
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def browser():
    """会话级浏览器实例"""
    with sync_playwright() as p:
        chromium = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        yield chromium


@pytest.fixture(scope="session")
def browser_context(browser: Browser, browser_context_args: dict):
    """会话级浏览器上下文"""
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()


@pytest.fixture
def page(browser_context: BrowserContext) -> Page:
    """函数级页面 — 每个测试独立页面，确保隔离"""
    page = browser_context.new_page()
    page.set_default_timeout(15000)
    yield page
    page.close()


@pytest.fixture
def authenticated_page(page: Page) -> Page:
    """已登录的页面 — 自动完成登录流程"""
    from pages.login_page import LoginPage

    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("admin", "1")
    page.wait_for_url("**/app**", timeout=10000)
    return page


# ---------- 报告增强 ----------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动截图并附加到allure报告"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = ROOT_DIR / "reports" / f"fail_{item.name}_{timestamp}.png"
            screenshot_path.parent.mkdir(exist_ok=True)
            page.screenshot(path=str(screenshot_path), full_page=True)
            allure.attach.file(
                str(screenshot_path),
                name=f"失败截图 - {item.name}",
                attachment_type=allure.attachment_type.PNG,
            )
