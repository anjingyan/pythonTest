"""
库存查询页面 — 库存列表查询、盘点、库存预警查看。
"""
import allure
from pages.base_page import BasePage


class InventoryPage(BasePage):

    PAGE_PATH = "/inventory"

    SEARCH_INPUT = "input[placeholder*='搜索'], input[placeholder*='商品'], input[placeholder*='编码'], [data-testid='search-input']"
    SEARCH_BTN = "button:has-text('搜索'), button:has-text('查询'), [data-testid='search-btn']"
    RESET_BTN = "button:has-text('重置'), [data-testid='reset-btn']"

    def navigate(self) -> None:
        super().navigate(self.PAGE_PATH)
        self.page.wait_for_load_state("networkidle")

    def is_loaded(self) -> bool:
        return self.page.locator(self.SEARCH_INPUT).first.is_visible(timeout=5000)

    def search_item(self, keyword: str) -> None:
        with allure.step(f"搜索库存商品: {keyword}"):
            self.page.locator(self.SEARCH_INPUT).first.fill(keyword)
            self.page.locator(self.SEARCH_BTN).first.click()
            self.wait_for_load()

    def reset_search(self) -> None:
        with allure.step("重置搜索条件"):
            self.page.locator(self.RESET_BTN).first.click()

    def get_inventory_list(self) -> list[dict]:
        rows = self.get_table_rows()
        if not rows:
            return []
        headers = self._get_table_headers()
        result = []
        for row in rows:
            cells = row.locator("td, th").all()
            values = [cell.inner_text().strip() for cell in cells]
            if len(values) == len(headers):
                result.append(dict(zip(headers, values)))
        return result

    def _get_table_headers(self) -> list[str]:
        headers = self.page.locator("thead th, .el-table__header th, .ant-table-thead th").all()
        return [h.inner_text().strip() for h in headers] if headers else []

    def get_stock_quantity(self, product_name: str) -> str | None:
        with allure.step(f"查询商品 '{product_name}' 的库存数量"):
            row = self.find_row_by_text(product_name)
            if row:
                cells = row.locator("td, th").all()
                return cells[-1].inner_text().strip() if cells else None
            return None

    def assert_stock_quantity(self, product_name: str, expected: str) -> None:
        actual = self.get_stock_quantity(product_name)
        if actual is None:
            raise AssertionError(f"未找到商品 '{product_name}' 的库存记录")
        if actual != expected:
            raise AssertionError(
                f"库存数量不匹配 — 期望: {expected}, 实际: {actual}"
            )

    def get_low_stock_items(self) -> list[str]:
        items = self.page.locator("[class*='warning'], [class*='danger'], [class*='low-stock']").all()
        return [item.inner_text() for item in items]
