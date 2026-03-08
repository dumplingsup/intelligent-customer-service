"""Custom tools for customer service agent."""

import os
from typing import Optional, Dict, Any
from langchain_core.tools import BaseTool

# Mock data for demo purposes
MOCK_ORDERS = {
    "ORD001": {"status": "已发货", "tracking": "SF123456789", "estimated": "2026-03-08"},
    "ORD002": {"status": "处理中", "tracking": None, "estimated": "2026-03-10"},
    "ORD003": {"status": "已配送", "tracking": "SF987654321", "estimated": "2026-03-07"},
    "ORD004": {"status": "已完成", "tracking": "SF111222333", "estimated": "2026-03-01"},
}

MOCK_CUSTOMERS = {
    "C001": {"name": "张三", "level": "黄金会员", "phone": "138****1234"},
    "C002": {"name": "李四", "level": "普通会员", "phone": "139****5678"},
    "C003": {"name": "王五", "level": "铂金会员", "phone": "137****9012"},
}


class OrderQueryTool(BaseTool):
    """Query order status by order ID."""

    name: str = "order_query"
    description: str = "Query order status. Input should be an order ID (e.g., ORD001)."

    def _run(self, order_id: str) -> str:
        """
        Call external API to query order status.

        Args:
            order_id: Order ID to query

        Returns:
            Order status information
        """
        # Mock implementation - replace with real API call
        order_id = order_id.upper().strip()

        if order_id in MOCK_ORDERS:
            order = MOCK_ORDERS[order_id]
            tracking_info = f", 物流单号：{order['tracking']}" if order.get('tracking') else ""
            return (
                f"订单 {order_id} 状态：{order['status']}"
                f"{tracking_info}"
                f", 预计送达：{order['estimated']}"
            )
        else:
            return f"未找到订单 {order_id}，请检查订单号是否正确。"

    async def _arun(self, order_id: str) -> str:
        """Async version of order query."""
        return self._run(order_id)


class RefundTool(BaseTool):
    """Process refund application."""

    name: str = "refund_process"
    description: str = "Process refund application. Input should be order ID and reason, separated by comma."

    def _run(self, order_id: str, reason: str = "") -> str:
        """
        Process refund application.

        Args:
            order_id: Order ID for refund
            reason: Reason for refund

        Returns:
            Refund processing result
        """
        # Mock implementation - replace with real API call
        order_id = order_id.upper().strip()

        if order_id not in MOCK_ORDERS:
            return f"退款申请失败：未找到订单 {order_id}"

        order = MOCK_ORDERS[order_id]
        if order["status"] == "已完成":
            return f"订单 {order_id} 已完成，无法申请退款。"

        if order["status"] == "已配送":
            return (
                f"退款申请已提交：订单 {order_id}，原因：{reason or '未指定'}。\n"
                f"请注意：商品正在配送中，如需退款可能需要拒收或申请退货。"
            )

        return (
            f"退款申请已受理：订单 {order_id}，原因：{reason or '未指定'}。\n"
            f"退款将在 1-3 个工作日内处理完成。"
        )

    async def _arun(self, order_id: str, reason: str = "") -> str:
        """Async version of refund processing."""
        return self._run(order_id, reason)


class CustomerInfoTool(BaseTool):
    """Query customer information."""

    name: str = "customer_info"
    description: str = "Query customer information by customer ID."

    def _run(self, customer_id: str) -> str:
        """
        Query customer information.

        Args:
            customer_id: Customer ID to query

        Returns:
            Customer information
        """
        # Mock implementation
        customer_id = customer_id.upper().strip()

        if customer_id in MOCK_CUSTOMERS:
            customer = MOCK_CUSTOMERS[customer_id]
            return (
                f"客户 {customer_id}: {customer['name']}, "
                f"会员等级：{customer['level']}, "
                f"联系电话：{customer['phone']}"
            )
        else:
            return f"未找到客户 {customer_id}，请检查客户 ID 是否正确。"

    async def _arun(self, customer_id: str) -> str:
        """Async version of customer info query."""
        return self._run(customer_id)


def create_tools() -> list:
    """
    Create all available tools for the agent.

    Returns:
        List of tool instances
    """
    return [
        OrderQueryTool(),
        RefundTool(),
        CustomerInfoTool()
    ]


def get_tool_names() -> list:
    """
    Get names of all available tools.

    Returns:
        List of tool names
    """
    return ["order_query", "refund_process", "customer_info"]
