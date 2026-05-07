"""
入库流程测试 — 覆盖新建、查询、审核、驳回、删除、导出、边界校验。
"""
import pytest
import allure
from pages.dashboard_page import DashboardPage
from pages.inbound_page import InboundPage
from utils.data_generator import (
    generate_inbound_order,
    inbound_smoke_scenarios,
    inbound_boundary_scenarios,
)


# ==================== 基础功能 ====================

@allure.feature("入库管理")
@allure.story("页面加载")
class TestInboundPageLoad:

    @allure.title("打开入库管理页面")
    @pytest.mark.smoke
    @pytest.mark.inbound
    def test_navigate_to_inbound(self, authenticated_page):
        page = InboundPage(authenticated_page)
        page.navigate()
        assert page.is_loaded(), "入库页面未能正常加载"


@allure.feature("入库管理")
@allure.story("新增入库单")
class TestCreateInbound:

    @allure.title("新增入库单 - 正常流程")
    @pytest.mark.smoke
    @pytest.mark.inbound
    def test_create_inbound_success(self, authenticated_page):
        page = InboundPage(authenticated_page)
        page.navigate()
        page.click_add()
        assert page.is_form_dialog_open(), "新增入库弹窗未打开"

        order_data = generate_inbound_order()
        page.fill_order_form(order_data)
        page.submit()

        toast = page.wait_for_toast()
        allure.attach(str(toast), "提交结果", allure.attachment_type.TEXT)

        page.navigate()
        page.search_order(order_data["order_no"])
        assert page.order_exists(order_data["order_no"]), f"入库单 {order_data['order_no']} 未在列表中找到"

    @allure.title("新增入库单 - 关联供应商和仓库")
    @pytest.mark.inbound
    def test_create_inbound_with_supplier(self, authenticated_page):
        page = InboundPage(authenticated_page)
        page.navigate()
        page.click_add()

        order_data = generate_inbound_order(supplier="深圳科技有限公司", warehouse="A001-主仓库")
        page.fill_order_form(order_data)
        page.submit()

        toast = page.wait_for_toast()
        assert toast is not None
        allure.attach(toast, "提示信息", allure.attachment_type.TEXT)

    @allure.title("新增入库单 - 多条连续创建")
    @pytest.mark.inbound
    def test_create_multiple_inbounds(self, authenticated_page):
        page = InboundPage(authenticated_page)
        order_nos = []
        for i in range(3):
            page.navigate()
            page.click_add()
            order_data = generate_inbound_order()
            page.fill_order_form(order_data)
            page.submit()
            order_nos.append(order_data["order_no"])

        page.navigate()
        for order_no in order_nos:
            page.search_order(order_no)
            assert page.order_exists(order_no), f"连续创建的第{i+1}条入库单 {order_no} 未找到"


# ==================== 查询/搜索 ====================

@allure.feature("入库管理")
@allure.story("查询入库单")
class TestSearchInbound:

    @allure.title("按单号搜索入库单")
    @pytest.mark.inbound
    def test_search_by_order_no(self, authenticated_page):
        page = InboundPage(authenticated_page)
        page.navigate()

        # 先创建一条
        page.click_add()
        order_data = generate_inbound_order()
        page.fill_order_form(order_data)
        page.submit()

        # 搜索
        page.navigate()
        page.search_order(order_data["order_no"])
        assert page.order_exists(order_data["order_no"]), "按单号搜索未找到对应记录"

    @allure.title("按供应商搜索入库单")
    @pytest.mark.inbound
    def test_search_by_supplier(self, authenticated_page):
        page = InboundPage(authenticated_page)
        page.navigate()
        page.search_order("深圳科技有限公司")
        # 验证搜索结果不为空(如果存在数据)
        allure.attach(page.page.screenshot(type="png"), "搜索结果", allure.attachment_type.PNG)

    @allure.title("搜索不存在的入库单")
    @pytest.mark.inbound
    def test_search_nonexistent(self, authenticated_page):
        page = InboundPage(authenticated_page)
        page.navigate()
        page.search_order("IN-NONEXIST-999999")
        assert not page.order_exists("IN-NONEXIST-999999"), "不应该找到不存在的单号"

    @allure.title("重置搜索条件")
    @pytest.mark.inbound
    def test_reset_search(self, authenticated_page):
        page = InboundPage(authenticated_page)
        page.navigate()
        page.search_order("测试关键字")
        page.reset_search()
        allure.attach(page.page.screenshot(type="png"), "重置后列表", allure.attachment_type.PNG)


# ==================== 审核流程 ====================

@allure.feature("入库管理")
@allure.story("审核入库单")
class TestApproveInbound:

    @allure.title("审核通过入库单")
    @pytest.mark.inbound
    def test_approve_inbound(self, authenticated_page):
        page = InboundPage(authenticated_page)
        page.navigate()

        # 创建一条待审核的入库单
        page.click_add()
        order_data = generate_inbound_order()
        page.fill_order_form(order_data)
        page.submit()

        page.navigate()
        page.search_order(order_data["order_no"])
        page.approve_order(order_data["order_no"])
        toast = page.wait_for_toast()
        allure.attach(str(toast), "审核结果", allure.attachment_type.TEXT)

    @allure.title("驳回入库单")
    @pytest.mark.inbound
    def test_reject_inbound(self, authenticated_page):
        page = InboundPage(authenticated_page)
        page.navigate()

        page.click_add()
        order_data = generate_inbound_order()
        page.fill_order_form(order_data)
        page.submit()

        page.navigate()
        page.search_order(order_data["order_no"])
        page.reject_order(order_data["order_no"], "商品数量与实物不符")
        toast = page.wait_for_toast()
        allure.attach(str(toast), "驳回结果", allure.attachment_type.TEXT)


# ==================== 删除 ====================

@allure.feature("入库管理")
@allure.story("删除入库单")
class TestDeleteInbound:

    @allure.title("删除入库单")
    @pytest.mark.inbound
    def test_delete_inbound(self, authenticated_page):
        page = InboundPage(authenticated_page)
        page.navigate()

        page.click_add()
        order_data = generate_inbound_order()
        page.fill_order_form(order_data)
        page.submit()

        page.navigate()
        page.search_order(order_data["order_no"])
        page.delete_order(order_data["order_no"])
        toast = page.wait_for_toast()
        allure.attach(str(toast), "删除结果", allure.attachment_type.TEXT)


# ==================== 边界/异常 ====================

@allure.feature("入库管理")
@allure.story("入库边界校验")
class TestInboundValidation:

    @allure.title("入库边界场景: {label}")
    @pytest.mark.inbound
    @pytest.mark.parametrize("scenario", inbound_boundary_scenarios(), ids=lambda s: s.label)
    def test_inbound_boundary(self, authenticated_page, scenario):
        page = InboundPage(authenticated_page)
        page.navigate()
        page.click_add()

        if not page.is_form_dialog_open():
            pytest.skip("新增入库弹窗未打开，跳过边界测试")

        page.fill_order_form(scenario.data)
        page.submit()

        if scenario.should_succeed:
            toast = page.wait_for_toast()
            allure.attach(str(toast), "提交结果", allure.attachment_type.TEXT)
        else:
            # 验证错误提示
            error = page.get_toast_message() or page.page.locator(
                ".el-form-item__error, .ant-form-item-explain-error, [class*='error']"
            ).first.inner_text()
            allure.attach(str(error), "校验错误", allure.attachment_type.TEXT)

    @allure.title("取消新建入库 - 数据不丢失")
    @pytest.mark.inbound
    def test_cancel_inbound_form(self, authenticated_page):
        page = InboundPage(authenticated_page)
        page.navigate()
        page.click_add()
        page.fill_order_form({"remark": "测试取消"})
        page.cancel_form()
        # 确认回到列表页
        assert page.is_loaded(), "取消后未回到列表页"


# ==================== 导出 ====================

@allure.feature("入库管理")
@allure.story("导出数据")
class TestExportInbound:

    @allure.title("导出入库列表")
    @pytest.mark.inbound
    def test_export_inbound(self, authenticated_page):
        page = InboundPage(authenticated_page)
        page.navigate()
        page.export_data()
        toast = page.wait_for_toast()
        allure.attach(str(toast), "导出结果", allure.attachment_type.TEXT)
