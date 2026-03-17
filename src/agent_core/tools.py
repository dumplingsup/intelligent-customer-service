"""Custom tools for customer service agent.

This module provides custom tools for the customer service agent to interact with
external systems such as order management, refund processing, and customer information.

Note: The current implementation uses mock data for demonstration purposes.
In production, these tools should connect to real external APIs.
"""

import os
import httpx
from typing import Optional, Dict, Any
from langchain_core.tools import BaseTool

# ============================================================================
# MOCK DATA - For demo/development purposes
# ============================================================================
# In production, replace these with actual API calls to your backend systems.
# See the commented sections in each tool for examples of how to integrate
# with real APIs.

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


# ============================================================================
# CONFIGURATION - API endpoints and settings
# ============================================================================
# Set these environment variables to connect to real APIs:
#   ORDER_API_URL: URL for order query API
#   ORDER_API_KEY: API key for authentication
#   REFUND_API_URL: URL for refund processing API
#   CUSTOMER_API_URL: URL for customer information API
#   USE_MOCK_DATA: Set to "false" to use real APIs instead of mock data

USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
ORDER_API_URL = os.getenv("ORDER_API_URL", "https://api.example.com/orders")
ORDER_API_KEY = os.getenv("ORDER_API_KEY", "")
REFUND_API_URL = os.getenv("REFUND_API_URL", "https://api.example.com/refunds")
CUSTOMER_API_URL = os.getenv("CUSTOMER_API_URL", "https://api.example.com/customers")


class OrderQueryTool(BaseTool):
    """Query order status by order ID.

    This tool queries the order management system to retrieve order status,
    tracking information, and estimated delivery date.

    Example:
        >>> tool = OrderQueryTool()
        >>> result = tool._run("ORD001")
        >>> print(result)
        订单 ORD001 状态：已发货，物流单号：SF123456789, 预计送达：2026-03-08

    Production Integration:
        To connect to a real order API, set the following environment variables:
        - ORDER_API_URL: Your order query API endpoint
        - ORDER_API_KEY: Your API authentication key
        - USE_MOCK_DATA: Set to "false"

        The tool will automatically use the real API when mock data is disabled.
    """

    name: str = "order_query"
    description: str = "Query order status. Input should be an order ID (e.g., ORD001)."

    def _run(self, order_id: str) -> str:
        """
        Query order status by order ID.

        Args:
            order_id: Order ID to query

        Returns:
            Order status information
        """
        order_id = order_id.upper().strip()

        # Production API integration example:
        # if not USE_MOCK_DATA:
        #     try:
        #         response = httpx.get(
        #             f"{ORDER_API_URL}/{order_id}",
        #             headers={"Authorization": f"Bearer {ORDER_API_KEY}"},
        #             timeout=10.0
        #         )
        #         response.raise_for_status()
        #         order = response.json()
        #         return self._format_order_response(order)
        #     except httpx.HTTPStatusError as e:
        #         if e.response.status_code == 404:
        #             return f"未找到订单 {order_id}，请检查订单号是否正确。"
        #         return f"查询订单时发生错误：{e.response.status_code}"
        #     except httpx.RequestError as e:
        #         return f"无法连接到订单服务：{str(e)}"

        # Mock implementation for demo purposes
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

    def _format_order_response(self, order: Dict[str, Any]) -> str:
        """Format order API response into human-readable string."""
        status = order.get("status", "未知状态")
        tracking = order.get("tracking_number")
        estimated = order.get("estimated_delivery")

        tracking_info = f", 物流单号：{tracking}" if tracking else ""
        delivery_info = f", 预计送达：{estimated}" if estimated else ""

        return f"订单 {order.get('order_id')} 状态：{status}{tracking_info}{delivery_info}"


class RefundTool(BaseTool):
    """Process refund application.

    This tool processes refund requests for orders. It checks the order status
    and applies business rules to determine if the refund can be processed.

    Example:
        >>> tool = RefundTool()
        >>> result = tool._run("ORD002", "商品有瑕疵")
        >>> print(result)
        退款申请已受理：订单 ORD002，原因：商品有瑕疵。
        退款将在 1-3 个工作日内处理完成。

    Production Integration:
        To connect to a real refund API, set the following environment variables:
        - REFUND_API_URL: Your refund processing API endpoint
        - ORDER_API_URL: URL to check order status (required)
        - ORDER_API_KEY: API authentication key
        - USE_MOCK_DATA: Set to "false"
    """

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
        order_id = order_id.upper().strip()

        # Production API integration example:
        # if not USE_MOCK_DATA:
        #     try:
        #         # First check order status
        #         order_response = httpx.get(
        #             f"{ORDER_API_URL}/{order_id}",
        #             headers={"Authorization": f"Bearer {ORDER_API_KEY}"},
        #             timeout=10.0
        #         )
        #         order_response.raise_for_status()
        #         order = order_response.json()
        #
        #         # Then submit refund request
        #         refund_response = httpx.post(
        #             REFUND_API_URL,
        #             json={"order_id": order_id, "reason": reason},
        #             headers={"Authorization": f"Bearer {ORDER_API_KEY}"},
        #             timeout=10.0
        #         )
        #         refund_response.raise_for_status()
        #         return self._format_refund_response(refund_response.json())
        #     except httpx.HTTPStatusError as e:
        #         return f"退款申请失败：{e.response.status_code}"
        #     except httpx.RequestError as e:
        #         return f"无法连接到退款服务：{str(e)}"

        # Mock implementation for demo purposes
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

    def _format_refund_response(self, refund_data: Dict[str, Any]) -> str:
        """Format refund API response into human-readable string."""
        status = refund_data.get("status", "unknown")
        refund_id = refund_data.get("refund_id")
        message = refund_data.get("message", "")

        if status == "approved":
            return f"退款申请已批准（退款单号：{refund_id}）。{message}"
        elif status == "pending":
            return f"退款申请已提交（申请单号：{refund_id}），等待审核。{message}"
        else:
            return f"退款申请失败：{message}"


class CustomerInfoTool(BaseTool):
    """Query customer information.

    This tool retrieves customer profile information including name, membership level,
    and contact details.

    Example:
        >>> tool = CustomerInfoTool()
        >>> result = tool._run("C001")
        >>> print(result)
        客户 C001: 张三，会员等级：黄金会员，联系电话：138****1234

    Production Integration:
        To connect to a real customer API, set the following environment variables:
        - CUSTOMER_API_URL: Your customer information API endpoint
        - ORDER_API_KEY: API authentication key
        - USE_MOCK_DATA: Set to "false"
    """

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
        customer_id = customer_id.upper().strip()

        # Production API integration example:
        # if not USE_MOCK_DATA:
        #     try:
        #         response = httpx.get(
        #             f"{CUSTOMER_API_URL}/{customer_id}",
        #             headers={"Authorization": f"Bearer {ORDER_API_KEY}"},
        #             timeout=10.0
        #         )
        #         response.raise_for_status()
        #         customer = response.json()
        #         return self._format_customer_response(customer)
        #     except httpx.HTTPStatusError as e:
        #         if e.response.status_code == 404:
        #             return f"未找到客户 {customer_id}，请检查客户 ID 是否正确。"
        #         return f"查询客户信息时发生错误：{e.response.status_code}"
        #     except httpx.RequestError as e:
        #         return f"无法连接到客户服务：{str(e)}"

        # Mock implementation for demo purposes
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

    def _format_customer_response(self, customer: Dict[str, Any]) -> str:
        """Format customer API response into human-readable string."""
        name = customer.get("name", "未知")
        level = customer.get("membership_level", "未知")
        phone = customer.get("phone", "未提供")
        email = customer.get("email")

        email_info = f", 邮箱：{email}" if email else ""
        return (
            f"客户 {customer.get('customer_id')}: {name}, "
            f"会员等级：{level}, "
            f"联系电话：{phone}{email_info}"
        )


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
