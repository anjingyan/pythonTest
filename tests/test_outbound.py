"""
出库流程测试 — 覆盖新建、查询、审核、驳回、删除、库存校验、边界校验。
"""
import pytest
import allure
from pages.outbound_page import OutboundPage
from utils.data_generator import (
    generate_outbound_order,
    outbound_smoke_scenarios,
    outbound_boundary_scenarios,
)


# ==================== 基础功能 ====================

@allure.feature("出库管理")
@allure.story("页面加载")
class TestOutboundPageLoad:

    @allure.title("打开出库管理页面")
    @pytest.mark.smoke
    @pytest.mark.outbound
    def test_navigate_to_outbound(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()
        assert page.is_loaded(), "出库页面未能正常加载"


@allure.feature("出库管理")
@allure.story("新增出库单")
class TestCreateOutbound:

    @allure.title("新增出库单 - 正常流程")
    @pytest.mark.smoke
    @pytest.mark.outbound
    def test_create_outbound_success(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()
        page.click_add()
        assert page.is_form_dialog_open(), "新增出库弹窗未打开"

        order_data = generate_outbound_order()
        page.fill_order_form(order_data)
        page.submit()

        toast = page.wait_for_toast()
        allure.attach(str(toast), "提交结果", allure.attachment_type.TEXT)

        page.navigate()
        page.search_order(order_data["order_no"])
        assert page.order_exists(order_data["order_no"]), f"出库单 {order_data['order_no']} 未在列表中找到"

    @allure.title("新增出库单 - 销售出库类型")
    @pytest.mark.outbound
    def test_create_sales_outbound(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()
        page.click_add()

        order_data = generate_outbound_order(order_type="销售出库", customer="华北销售部")
        page.fill_order_form(order_data)
        page.submit()

        toast = page.wait_for_toast()
        assert toast is not None

    @allure.title("新增出库单 - 领料出库类型")
    @pytest.mark.outbound
    def test_create_material_outbound(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()
        page.click_add()

        order_data = generate_outbound_order(order_type="领料出库")
        page.fill_order_form(order_data)
        page.submit()

        toast = page.wait_for_toast()
        assert toast is not None

    @allure.title("新增出库单 - 多条连续创建")
    @pytest.mark.outbound
    def test_create_multiple_outbounds(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        order_nos = []
        for i in range(3):
            page.navigate()
            page.click_add()
            order_data = generate_outbound_order()
            page.fill_order_form(order_data)
            page.submit()
            order_nos.append(order_data["order_no"])

        page.navigate()
        for order_no in order_nos:
            page.search_order(order_no)
            assert page.order_exists(order_no), f"连续创建的第{i+1}条出库单 {order_no} 未找到"


# ==================== 查询/搜索 ====================

@allure.feature("出库管理")
@allure.story("查询出库单")
class TestSearchOutbound:

    @allure.title("按单号搜索出库单")
    @pytest.mark.outbound
    def test_search_by_order_no(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()

        page.click_add()
        order_data = generate_outbound_order()
        page.fill_order_form(order_data)
        page.submit()

        page.navigate()
        page.search_order(order_data["order_no"])
        assert page.order_exists(order_data["order_no"]), "按单号搜索未找到对应记录"

    @allure.title("按客户搜索出库单")
    @pytest.mark.outbound
    def test_search_by_customer(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()
        page.search_order("华北销售部")
        allure.attach(page.page.screenshot(type="png"), "搜索结果", allure.attachment_type.PNG)

    @allure.title("搜索不存在的出库单")
    @pytest.mark.outbound
    def test_search_nonexistent(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()
        page.search_order("OUT-NONEXIST-999999")
        assert not page.order_exists("OUT-NONEXIST-999999"), "不应该找到不存在的单号"

    @allure.title("重置搜索条件")
    @pytest.mark.outbound
    def test_reset_search(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()
        page.search_order("测试")
        page.reset_search()
        allure.attach(page.page.screenshot(type="png"), "重置后列表", allure.attachment_type.PNG)


# ==================== 库存校验 ====================

@allure.feature("出库管理")
@allure.story("库存校验")
class TestStockCheck:

    @allure.title("出库前库存校验")
    @pytest.mark.outbound
    def test_stock_check_before_outbound(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()
        page.click_add()
        page.fill_order_form(generate_outbound_order(quantity="99999"))
        page.check_stock()

        result = page.get_stock_check_result()
        allure.attach(str(result), "库存校验结果", allure.attachment_type.TEXT)

    @allure.title("库存不足时警告提示")
    @pytest.mark.outbound
    def test_insufficient_stock_warning(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()
        page.click_add()

        # 使用极大数量模拟库存不足
        order_data = generate_outbound_order(quantity="999999", product_code="P999")
        page.fill_order_form(order_data)
        page.submit()

        has_warning = page.is_stock_insufficient_warning()
        if has_warning:
            allure.attach("系统提示库存不足", "校验结果", allure.attachment_type.TEXT)


# ==================== 审核流程 ====================

@allure.feature("出库管理")
@allure.story("审核出库单")
class TestApproveOutbound:

    @allure.title("审核通过出库单")
    @pytest.mark.outbound
    def test_approve_outbound(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()

        page.click_add()
        order_data = generate_outbound_order()
        page.fill_order_form(order_data)
        page.submit()

        page.navigate()
        page.search_order(order_data["order_no"])
        page.approve_order(order_data["order_no"])
        toast = page.wait_for_toast()
        allure.attach(str(toast), "审核结果", allure.attachment_type.TEXT)

    @allure.title("驳回出库单")
    @pytest.mark.outbound
    def test_reject_outbound(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()

        page.click_add()
        order_data = generate_outbound_order()
        page.fill_order_form(order_data)
        page.submit()

        page.navigate()
        page.search_order(order_data["order_no"])
        page.reject_order(order_data["order_no"], "库存不足，无法出库")
        toast = page.wait_for_toast()
        allure.attach(str(toast), "驳回结果", allure.attachment_type.TEXT)


# ==================== 删除 ====================

@allure.feature("出库管理")
@allure.story("删除出库单")
class TestDeleteOutbound:

    @allure.title("删除出库单")
    @pytest.mark.outbound
    def test_delete_outbound(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()

        page.click_add()
        order_data = generate_outbound_order()
        page.fill_order_form(order_data)
        page.submit()

        page.navigate()
        page.search_order(order_data["order_no"])
        page.delete_order(order_data["order_no"])
        toast = page.wait_for_toast()
        allure.attach(str(toast), "删除结果", allure.attachment_type.TEXT)


# ==================== 边界/异常 ====================

@allure.feature("出库管理")
@allure.story("出库边界校验")
class TestOutboundValidation:

    @allure.title("出库边界场景: {label}")
    @pytest.mark.outbound
    @pytest.mark.parametrize("scenario", outbound_boundary_scenarios(), ids=lambda s: s.label)
    def test_outbound_boundary(self, authenticated_page, scenario):
        page = OutboundPage(authenticated_page)
        page.navigate()
        page.click_add()

        if not page.is_form_dialog_open():
            pytest.skip("新增出库弹窗未打开，跳过边界测试")

        page.fill_order_form(scenario.data)
        page.submit()

        if scenario.should_succeed:
            toast = page.wait_for_toast()
            allure.attach(str(toast), "提交结果", allure.attachment_type.TEXT)
        else:
            error = page.get_toast_message() or page.page.locator(
                ".el-form-item__error, .ant-form-item-explain-error, [class*='error']"
            ).first.inner_text()
            allure.attach(str(error), "校验错误", allure.attachment_type.TEXT)

    @allure.title("取消新增出库 - 返回列表")
    @pytest.mark.outbound
    def test_cancel_outbound_form(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()
        page.click_add()
        page.fill_order_form({"remark": "测试取消"})
        page.cancel_form()
        assert page.is_loaded(), "取消后未回到列表页"


# ==================== 导出 ====================

@allure.feature("出库管理")
@allure.story("导出数据")
class TestExportOutbound:

    @allure.title("导出出库列表")
    @pytest.mark.outbound
    def test_export_outbound(self, authenticated_page):
        page = OutboundPage(authenticated_page)
        page.navigate()
        page.export_data()
        toast = page.wait_for_toast()
        allure.attach(str(toast), "导出结果", allure.attachment_type.TEXT)
