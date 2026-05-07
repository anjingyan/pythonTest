"""
出库管理页面 — 新建出库单、查询、审核、撤销、缺货校验。
"""
import allure
from pages.base_page import BasePage


class OutboundPage(BasePage):

    PAGE_PATH = "/outbound"

    ADD_BTN = "button:has-text('新增出库'), button:has-text('新建出库'), button:has-text('添加出库'), [data-testid='add-outbound']"
    SEARCH_INPUT = "input[placeholder*='搜索'], input[placeholder*='单号'], input[placeholder*='查询'], [data-testid='search-input']"
    SEARCH_BTN = "button:has-text('搜索'), button:has-text('查询'), [data-testid='search-btn']"
    RESET_BTN = "button:has-text('重置'), button:has-text('清空'), [data-testid='reset-btn']"
    SAVE_BTN = "button:has-text('保存'), button:has-text('提交'), button:has-text('确认出库'), [data-testid='save-outbound']"
    CANCEL_BTN = "button:has-text('取消'), button:has-text('返回'), [data-testid='cancel-outbound']"
    STOCK_CHECK_BTN = "button:has-text('库存校验'), button:has-text('校验库存'), [data-testid='check-stock']"

    def navigate(self) -> None:
        super().navigate(self.PAGE_PATH)
        self.page.wait_for_load_state("networkidle")

    def is_loaded(self) -> bool:
        return self.page.locator(self.ADD_BTN).first.is_visible(timeout=5000)

    # ---------- 列表操作 ----------
    def search_order(self, keyword: str) -> None:
        with allure.step(f"搜索出库单: {keyword}"):
            self.page.locator(self.SEARCH_INPUT).first.fill(keyword)
            self.page.locator(self.SEARCH_BTN).first.click()
            self.wait_for_load()

    def reset_search(self) -> None:
        with allure.step("重置搜索条件"):
            self.page.locator(self.RESET_BTN).first.click()

    def get_order_list(self) -> list[dict]:
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

    def order_exists(self, order_no: str) -> bool:
        return self.page.locator(f"text={order_no}").first.is_visible(timeout=3000)

    def open_order_detail(self, order_no: str) -> None:
        with allure.step(f"打开出库单详情: {order_no}"):
            row = self.find_row_by_text(order_no)
            if row:
                row.locator("a, .link, button:has-text('详情'), button:has-text('查看')").first.click()

    # ---------- 新建出库 ----------
    def click_add(self) -> None:
        with allure.step("点击新增出库按钮"):
            self.page.locator(self.ADD_BTN).first.click()
            self.wait_for_load()

    def fill_order_form(self, order_data: dict) -> None:
        """
        填充出库单表单。order_data支持:
        - order_no: 出库单号
        - customer: 客户/领用人
        - warehouse: 出库仓库
        - product_code: 商品编码
        - product_name: 商品名称
        - quantity: 数量
        - unit: 单位
        - unit_price: 单价
        - total_amount: 总金额
        - outbound_date: 出库日期
        - operator: 操作员
        - order_type: 出库类型 (销售出库/领料出库/退货出库等)
        - remark: 备注
        """
        with allure.step("填写出库单信息"):
            self._fill_field("出库单号", order_data.get("order_no", ""))
            self._fill_field("客户", order_data.get("customer", ""))
            self._fill_field("领用人", order_data.get("customer", ""))
            self._fill_field("出库仓库", order_data.get("warehouse", ""))
            self._fill_field("商品编码", order_data.get("product_code", ""))
            self._fill_field("商品名称", order_data.get("product_name", ""))
            self._fill_field("数量", order_data.get("quantity", ""))
            self._fill_field("单位", order_data.get("unit", ""))
            self._fill_field("单价", order_data.get("unit_price", ""))
            self._fill_field("总金额", order_data.get("total_amount", ""))
            self._fill_field("出库日期", order_data.get("outbound_date", ""))
            self._fill_field("操作员", order_data.get("operator", ""))
            self._fill_field("出库类型", order_data.get("order_type", ""))
            self._fill_field("备注", order_data.get("remark", ""))

    def _fill_field(self, label: str, value: str) -> None:
        if not value:
            return
        input_locator = self.get_input(label)
        if input_locator.count() == 0:
            input_locator = self.get_by_placeholder(label)
        if input_locator.count() > 0:
            input_locator.first.fill(str(value))

    def submit(self) -> None:
        with allure.step("提交出库单"):
            self.page.locator(self.SAVE_BTN).first.click()

    def cancel_form(self) -> None:
        with allure.step("取消填写"):
            self.page.locator(self.CANCEL_BTN).first.click()

    def confirm_dialog(self) -> None:
        dialog = self.page.locator(
            ".el-message-box, .ant-modal-confirm, [class*='confirm'], [class*='dialog']"
        )
        confirm_btn = dialog.locator(
            "button:has-text('确定'), button:has-text('确认'), button:has-text('是')"
        )
        if confirm_btn.count() > 0:
            confirm_btn.first.click()

    def is_form_dialog_open(self) -> bool:
        return self.page.locator(
            ".el-dialog, .ant-modal, .modal, [class*='dialog'], [class*='drawer']"
        ).first.is_visible(timeout=3000)

    # ---------- 库存校验 ----------
    def check_stock(self) -> None:
        with allure.step("点击库存校验"):
            self.page.locator(self.STOCK_CHECK_BTN).first.click()

    def get_stock_check_result(self) -> str | None:
        result = self.page.locator(".stock-result, [class*='stock-check'], .alert, [class*='warning']")
        if result.count() > 0:
            return result.first.inner_text()
        return None

    def is_stock_insufficient_warning(self) -> bool:
        warning = self.page.locator(
            ".el-message--warning, .ant-message-warning, [class*='insufficient'], [class*='warning']"
        )
        return warning.count() > 0

    # ---------- 审核操作 ----------
    def approve_order(self, order_no: str) -> None:
        with allure.step(f"审核出库单: {order_no}"):
            self.click_row_action(order_no, "审核")
            self.confirm_dialog()

    def reject_order(self, order_no: str, reason: str = "") -> None:
        with allure.step(f"驳回出库单: {order_no}"):
            self.click_row_action(order_no, "驳回")
            if reason:
                self.page.locator("textarea, input[placeholder*='原因']").first.fill(reason)
            self.confirm_dialog()

    # ---------- 删除 ----------
    def delete_order(self, order_no: str) -> None:
        with allure.step(f"删除出库单: {order_no}"):
            self.click_row_action(order_no, "删除")
            self.confirm_dialog()

    # ---------- 导出 ----------
    def export_data(self) -> None:
        with allure.step("导出出库数据"):
            self.page.locator("button:has-text('导出'), button:has-text('下载')").first.click()
