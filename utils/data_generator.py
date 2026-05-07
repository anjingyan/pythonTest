"""
测试数据生成器 — 生成入库/出库单数据，支持随机和固定两种模式。
"""
import random
import string
from datetime import datetime, timedelta
from dataclasses import dataclass, field


# ---------- 预设数据 ----------
PRODUCTS = [
    {"code": "P001", "name": "螺丝刀套装", "unit": "套", "price": 25.00},
    {"code": "P002", "name": "电动扳手", "unit": "台", "price": 380.00},
    {"code": "P003", "name": "钢化玻璃", "unit": "块", "price": 120.00},
    {"code": "P004", "name": "焊接面罩", "unit": "个", "price": 65.00},
    {"code": "P005", "name": "润滑油", "unit": "桶", "price": 280.00},
    {"code": "P006", "name": "密封圈", "unit": "个", "price": 3.50},
    {"code": "P007", "name": "电脑主板", "unit": "块", "price": 850.00},
    {"code": "P008", "name": "内存条16GB", "unit": "根", "price": 320.00},
    {"code": "P009", "name": "电源适配器", "unit": "个", "price": 45.00},
    {"code": "P010", "name": "网线水晶头", "unit": "盒", "price": 18.00},
]

WAREHOUSES = ["A001-主仓库", "A002-原料仓", "B001-成品仓", "B002-备件仓", "C001-退货仓"]

SUPPLIERS = ["深圳科技有限公司", "广州五金配件厂", "上海电子材料公司", "北京精密仪器厂", "杭州日用品有限公司"]

CUSTOMERS = ["华北销售部", "华东分销中心", "零售门店001", "电商平台仓库", "售后维修中心"]

ORDER_TYPES = ["销售出库", "领料出库", "退货出库", "调拨出库", "报废出库"]


def _random_suffix(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def _random_date(days_back: int = 30) -> str:
    """生成过去N天内的随机日期"""
    delta = timedelta(days=random.randint(0, days_back))
    return (datetime.now() - delta).strftime("%Y-%m-%d")


# ---------- 入库数据 ----------
def generate_inbound_order(**overrides) -> dict:
    """生成一条入库单测试数据"""
    product = random.choice(PRODUCTS)
    quantity = random.randint(10, 500)
    base = {
        "order_no": f"IN{datetime.now().strftime('%Y%m%d%H%M%S')}{_random_suffix()}",
        "supplier": random.choice(SUPPLIERS),
        "warehouse": random.choice(WAREHOUSES),
        "product_code": product["code"],
        "product_name": product["name"],
        "quantity": str(quantity),
        "unit": product["unit"],
        "unit_price": str(product["price"]),
        "total_amount": str(round(quantity * product["price"], 2)),
        "inbound_date": _random_date(),
        "operator": "测试操作员",
        "remark": f"自动化测试入库_{_random_suffix(4)}",
    }
    base.update(overrides)
    return base


@dataclass
class InboundScenario:
    label: str
    data: dict
    should_succeed: bool = True


def inbound_smoke_scenarios() -> list[InboundScenario]:
    """入库冒烟测试场景集"""
    return [
        InboundScenario("正常入库-单一商品", generate_inbound_order(), True),
        InboundScenario("正常入库-大数量", generate_inbound_order(quantity="99999"), True),
        InboundScenario("正常入库-不同仓库", generate_inbound_order(warehouse="B001-成品仓"), True),
    ]


def inbound_boundary_scenarios() -> list[InboundScenario]:
    """入库边界测试场景集"""
    return [
        InboundScenario("数量为1", generate_inbound_order(quantity="1"), True),
        InboundScenario("金额为0", generate_inbound_order(unit_price="0", total_amount="0"), True),
        InboundScenario("缺少供应商", generate_inbound_order(supplier=""), False),
        InboundScenario("缺少商品", generate_inbound_order(product_code="", product_name=""), False),
        InboundScenario("负数量", generate_inbound_order(quantity="-10"), False),
    ]


# ---------- 出库数据 ----------
def generate_outbound_order(**overrides) -> dict:
    """生成一条出库单测试数据"""
    product = random.choice(PRODUCTS)
    quantity = random.randint(1, 100)
    base = {
        "order_no": f"OUT{datetime.now().strftime('%Y%m%d%H%M%S')}{_random_suffix()}",
        "customer": random.choice(CUSTOMERS),
        "warehouse": random.choice(WAREHOUSES),
        "product_code": product["code"],
        "product_name": product["name"],
        "quantity": str(quantity),
        "unit": product["unit"],
        "unit_price": str(product["price"]),
        "total_amount": str(round(quantity * product["price"], 2)),
        "outbound_date": _random_date(),
        "operator": "测试操作员",
        "order_type": random.choice(ORDER_TYPES),
        "remark": f"自动化测试出库_{_random_suffix(4)}",
    }
    base.update(overrides)
    return base


@dataclass
class OutboundScenario:
    label: str
    data: dict
    should_succeed: bool = True


def outbound_smoke_scenarios() -> list[OutboundScenario]:
    """出库冒烟测试场景集"""
    return [
        OutboundScenario("正常出库-单一商品", generate_outbound_order(), True),
        OutboundScenario("正常出库-销售出库", generate_outbound_order(order_type="销售出库"), True),
        OutboundScenario("正常出库-领料出库", generate_outbound_order(order_type="领料出库"), True),
    ]


def outbound_boundary_scenarios() -> list[OutboundScenario]:
    """出库边界测试场景集"""
    return [
        OutboundScenario("数量为1", generate_outbound_order(quantity="1"), True),
        OutboundScenario("缺少客户", generate_outbound_order(customer=""), False),
        OutboundScenario("缺少商品", generate_outbound_order(product_code="", product_name=""), False),
        OutboundScenario("负数量", generate_outbound_order(quantity="-5"), False),
        OutboundScenario("超库存出库", generate_outbound_order(quantity="999999"), False),
    ]
