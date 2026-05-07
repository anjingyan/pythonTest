"""
项目配置 — 基础URL、超时时间、测试账号等。
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    BASE_URL: str = "http://localhost:8080/app"
    LOGIN_URL: str = "/login"
    DASHBOARD_URL: str = "/dashboard"
    INBOUND_URL: str = "/inbound"
    OUTBOUND_URL: str = "/outbound"
    INVENTORY_URL: str = "/inventory"

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "1"

    TIMEOUT: int = 15_000
    NETWORK_IDLE_TIMEOUT: int = 10_000
    WAIT_AFTER_ACTION: int = 500

    HEADLESS: bool = True


config = Config()
