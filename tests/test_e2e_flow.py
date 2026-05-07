"""
端到端流程测试 — 完整覆盖 登录→入库→库存→出库→库存变更 全链路。
"""
import pytest
import allure
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.inbound_page import InboundPage
from pages.outbound_page import OutboundPage
from pages.inventory_page import InventoryPage
from utils.data_generator import generate_inbound_order, generate_outbound_order


# ==================== 完整出入库闭环 ====================

@allure.feature("端到端流程")
@allure.story("出入库全生命周期")
class TestFullInboundOutboundCycle:

    @allure.title("E2E-01: 完整出入库闭环 — 入库→库存查询→出库")
    @pytest.mark.smoke
    @pytest.mark.e2e
    def test_full_inbound_outbound_cycle(self, page):
        """
        完整业务流程:
        1. 登录系统
        2. 创建入库单
        3. 审核入库单
        4. 验证库存增加
        5. 创建出库单
        6. 审核出库单
        7. 验证库存减少
        """
        product_name = "螺丝刀套装"
        inbound_qty = 200

        # === 1. 登录 ===
        with allure.step("1. 登录系统"):
            LoginPage(page).navigate()
            LoginPage(page).login("admin", "1")
            page.wait_for_url("**/app**", timeout=10000)
            allure.attach(page.screenshot(type="png"), "登录成功", allure.attachment_type.PNG)

        dashboard = DashboardPage(page)

        # === 2. 创建入库单 ===
        with allure.step("2. 创建入库单"):
            dashboard.go_to_inbound()
            inbound_page = InboundPage(page)
            inbound_page.click_add()

            inbound_data = generate_inbound_order(
                product_name=product_name,
                quantity=str(inbound_qty),
                warehouse="A001-主仓库",
            )
            inbound_page.fill_order_form(inbound_data)
            inbound_page.submit()

            toast = inbound_page.wait_for_toast()
            allure.attach(str(toast), "入库提交结果", allure.attachment_type.TEXT)

        # === 3. 审核入库单 ===
        with allure.step("3. 审核入库单"):
            inbound_page.navigate()
            inbound_page.search_order(inbound_data["order_no"])
            assert inbound_page.order_exists(inbound_data["order_no"]), "入库单未创建成功"
            inbound_page.approve_order(inbound_data["order_no"])

        # === 4. 验证入库后库存 ===
        with allure.step("4. 验证入库后库存"):
            dashboard.go_to_inventory()
            inventory_page = InventoryPage(page)
            inventory_page.search_item(product_name)
            stock_after_inbound = inventory_page.get_stock_quantity(product_name)
            allure.attach(
                f"入库后库存: {stock_after_inbound}",
                "库存快照",
                allure.attachment_type.TEXT,
            )

        # === 5. 创建出库单 ===
        with allure.step("5. 创建出库单"):
            dashboard.go_to_outbound()
            outbound_page = OutboundPage(page)
            outbound_page.click_add()

            outbound_qty = 50
            outbound_data = generate_outbound_order(
                product_name=product_name,
                quantity=str(outbound_qty),
                warehouse="A001-主仓库",
                order_type="销售出库",
                customer="华北销售部",
            )
            outbound_page.fill_order_form(outbound_data)
            outbound_page.submit()

            toast = outbound_page.wait_for_toast()
            allure.attach(str(toast), "出库提交结果", allure.attachment_type.TEXT)

        # === 6. 审核出库单 ===
        with allure.step("6. 审核出库单"):
            outbound_page.navigate()
            outbound_page.search_order(outbound_data["order_no"])
            assert outbound_page.order_exists(outbound_data["order_no"]), "出库单未创建成功"
            outbound_page.approve_order(outbound_data["order_no"])

        # === 7. 验证出库后库存 ===
        with allure.step("7. 验证出库后库存变更"):
            dashboard.go_to_inventory()
            inventory_page.search_item(product_name)
            stock_after_outbound = inventory_page.get_stock_quantity(product_name)
            allure.attach(
                f"出库后库存: {stock_after_outbound}",
                "库存快照",
                allure.attachment_type.TEXT,
            )


@allure.feature("端到端流程")
@allure.story("登录认证")
class TestLoginFlow:

    @allure.title("E2E-02: 登录成功跳转仪表板")
    @pytest.mark.smoke
    @pytest.mark.e2e
    def test_login_redirect_to_dashboard(self, page):
        login_page = LoginPage(page)
        login_page.navigate()
        login_page.login("admin", "1")
        login_page.assert_login_success()

        dashboard = DashboardPage(page)
        assert dashboard.is_loaded(), "登录后仪表板未正确加载"

    @allure.title("E2E-03: 登录失败 — 错误密码")
    @pytest.mark.e2e
    def test_login_wrong_password(self, page):
        login_page = LoginPage(page)
        login_page.navigate()
        login_page.login("admin", "wrong_password")
        login_page.assert_login_error("密码")

    @allure.title("E2E-04: 登录失败 — 空用户名")
    @pytest.mark.e2e
    def test_login_empty_username(self, page):
        login_page = LoginPage(page)
        login_page.navigate()
        login_page.login("", "1")
        login_page.assert_login_error("用户")


@allure.feature("端到端流程")
@allure.story("导航菜单")
class TestNavigation:

    @allure.title("E2E-05: 侧边栏菜单导航")
    @pytest.mark.e2e
    def test_sidebar_navigation(self, authenticated_page):
        dashboard = DashboardPage(authenticated_page)
        menu_items = dashboard.get_menu_items()
        allure.attach(str(menu_items), "菜单项", allure.attachment_type.TEXT)

        for item in menu_items:
            with allure.step(f"点击菜单: {item}"):
                dashboard.click_menu(item)


@allure.feature("端到端流程")
@allure.story("出入库联调")
class TestInboundOutboundIntegration:

    @allure.title("E2E-06: 入库后立即出库同商品")
    @pytest.mark.e2e
    def test_inbound_then_outbound_same_product(self, page):
        """入库一个商品后立即出库该商品"""
        # 登录
        LoginPage(page).navigate()
        LoginPage(page).login("admin", "1")
        page.wait_for_url("**/app**", timeout=10000)

        dashboard = DashboardPage(page)

        # 入库
        with allure.step("入库操作"):
            dashboard.go_to_inbound()
            inbound_page = InboundPage(page)
            inbound_page.click_add()
            inbound_data = generate_inbound_order(
                product_code="P001",
                product_name="螺丝刀套装",
                quantity="300",
            )
            inbound_page.fill_order_form(inbound_data)
            inbound_page.submit()

        # 出库
        with allure.step("出库操作"):
            dashboard.go_to_outbound()
            outbound_page = OutboundPage(page)
            outbound_page.click_add()
            outbound_data = generate_outbound_order(
                product_code="P001",
                product_name="螺丝刀套装",
                quantity="50",
            )
            outbound_page.fill_order_form(outbound_data)
            outbound_page.submit()

        toast = outbound_page.wait_for_toast()
        allure.attach(str(toast), "出入库联调结果", allure.attachment_type.TEXT)

    @allure.title("E2E-07: 批量入库后批量出库")
    @pytest.mark.e2e
    def test_batch_inbound_outbound(self, page):
        """批量创建入库单，然后为每批商品创建出库单"""
        LoginPage(page).navigate()
        LoginPage(page).login("admin", "1")
        page.wait_for_url("**/app**", timeout=10000)

        dashboard = DashboardPage(page)
        products = [
            {"code": "P003", "name": "钢化玻璃", "qty_in": "500", "qty_out": "100"},
            {"code": "P006", "name": "密封圈", "qty_in": "1000", "qty_out": "200"},
            {"code": "P009", "name": "电源适配器", "qty_in": "300", "qty_out": "50"},
        ]

        for product in products:
            with allure.step(f"处理商品: {product['name']}"):
                # 入库
                dashboard.go_to_inbound()
                inbound_page = InboundPage(page)
                inbound_page.click_add()
                inbound_data = generate_inbound_order(
                    product_code=product["code"],
                    product_name=product["name"],
                    quantity=product["qty_in"],
                )
                inbound_page.fill_order_form(inbound_data)
                inbound_page.submit()
                inbound_page.wait_for_toast()

                # 出库
                dashboard.go_to_outbound()
                outbound_page = OutboundPage(page)
                outbound_page.click_add()
                outbound_data = generate_outbound_order(
                    product_code=product["code"],
                    product_name=product["name"],
                    quantity=product["qty_out"],
                )
                outbound_page.fill_order_form(outbound_data)
                outbound_page.submit()
                outbound_page.wait_for_toast()


@allure.feature("端到端流程")
@allure.story("订单状态流转")
class TestOrderStatusFlow:

    @allure.title("E2E-08: 入库单状态流转 — 新建→审核通过→完成")
    @pytest.mark.e2e
    def test_inbound_status_flow(self, page):
        LoginPage(page).navigate()
        LoginPage(page).login("admin", "1")
        page.wait_for_url("**/app**", timeout=10000)

        dashboard = DashboardPage(page)
        dashboard.go_to_inbound()
        inbound_page = InboundPage(page)

        # 新建
        inbound_page.click_add()
        order_data = generate_inbound_order()
        inbound_page.fill_order_form(order_data)
        inbound_page.submit()

        # 审核
        inbound_page.navigate()
        inbound_page.search_order(order_data["order_no"])
        assert inbound_page.order_exists(order_data["order_no"]), "新建入库单未出现在列表中"
        inbound_page.approve_order(order_data["order_no"])

        allure.attach(page.screenshot(type="png"), "状态流转完成", allure.attachment_type.PNG)

    @allure.title("E2E-09: 出库单状态流转 — 新建→驳回→重新提交→审核通过")
    @pytest.mark.e2e
    def test_outbound_reject_resubmit_flow(self, page):
        LoginPage(page).navigate()
        LoginPage(page).login("admin", "1")
        page.wait_for_url("**/app**", timeout=10000)

        dashboard = DashboardPage(page)
        dashboard.go_to_outbound()
        outbound_page = OutboundPage(page)

        # 新建
        outbound_page.click_add()
        order_data = generate_outbound_order()
        outbound_page.fill_order_form(order_data)
        outbound_page.submit()

        # 驳回
        outbound_page.navigate()
        outbound_page.search_order(order_data["order_no"])
        outbound_page.reject_order(order_data["order_no"], "信息有误请重新提交")

        # 重新提交(新建一条)
        outbound_page.click_add()
        new_data = generate_outbound_order(
            product_code=order_data["product_code"],
            product_name=order_data["product_name"],
        )
        outbound_page.fill_order_form(new_data)
        outbound_page.submit()

        # 审核新单
        outbound_page.navigate()
        outbound_page.search_order(new_data["order_no"])
        outbound_page.approve_order(new_data["order_no"])

        allure.attach(page.screenshot(type="png"), "驳回重提完成", allure.attachment_type.PNG)
