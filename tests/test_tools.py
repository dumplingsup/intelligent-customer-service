"""Tests for agent tools module."""

import pytest
from unittest.mock import patch, MagicMock

from src.agent_core.tools import (
    OrderQueryTool,
    RefundTool,
    CustomerInfoTool,
    create_tools,
    get_tool_names
)


class TestOrderQueryTool:
    """Test OrderQueryTool functionality."""

    def test_order_query_found(self):
        """Test querying an existing order."""
        tool = OrderQueryTool()
        result = tool._run("ORD001")

        assert "ORD001" in result
        assert "已发货" in result
        assert "SF123456789" in result
        assert "预计送达" in result

    def test_order_query_not_found(self):
        """Test querying a non-existent order."""
        tool = OrderQueryTool()
        result = tool._run("INVALID001")

        assert "未找到订单" in result
        assert "INVALID001" in result

    def test_order_query_case_insensitive(self):
        """Test that order ID is case insensitive."""
        tool = OrderQueryTool()
        result_lower = tool._run("ord001")
        result_upper = tool._run("ORD001")

        assert result_lower == result_upper

    def test_order_query_strips_whitespace(self):
        """Test that order ID is stripped of whitespace."""
        tool = OrderQueryTool()
        result_stripped = tool._run("  ORD001  ")
        result_normal = tool._run("ORD001")

        assert result_stripped == result_normal

    def test_order_query_without_tracking(self):
        """Test querying an order without tracking number."""
        tool = OrderQueryTool()
        result = tool._run("ORD002")

        assert "ORD002" in result
        assert "处理中" in result
        assert "物流单号" not in result

    def test_order_query_completed_order(self):
        """Test querying a completed order."""
        tool = OrderQueryTool()
        result = tool._run("ORD004")

        assert "已完成" in result
        assert "SF111222333" in result

    @pytest.mark.asyncio
    async def test_order_query_async(self):
        """Test async version of order query."""
        tool = OrderQueryTool()
        result = await tool._arun("ORD001")

        assert "已发货" in result
        assert "ORD001" in result


class TestRefundTool:
    """Test RefundTool functionality."""

    def test_refund_order_not_found(self):
        """Test refund for non-existent order."""
        tool = RefundTool()
        result = tool._run("INVALID001", "产品损坏")

        assert "退款申请失败" in result
        assert "未找到订单" in result

    def test_refund_completed_order(self):
        """Test refund for completed order (should be rejected)."""
        tool = RefundTool()
        result = tool._run("ORD004", "不想要了")

        assert "无法申请退款" in result
        assert "已完成" in result

    def test_refund_shipping_order(self):
        """Test refund for order being shipped."""
        tool = RefundTool()
        result = tool._run("ORD003", "商品有瑕疵")

        assert "退款申请已提交" in result
        assert "正在配送中" in result
        assert "拒收" in result

    def test_refund_processing_order(self):
        """Test refund for order in processing state."""
        tool = RefundTool()
        result = tool._run("ORD002", "拍错了")

        assert "退款申请已受理" in result
        assert "1-3 个工作日" in result

    def test_refund_default_reason(self):
        """Test refund with default (empty) reason."""
        tool = RefundTool()
        result = tool._run("ORD002")

        assert "未指定" in result

    def test_refund_case_insensitive(self):
        """Test that order ID is case insensitive."""
        tool = RefundTool()
        result_lower = tool._run("ord002", "测试")
        result_upper = tool._run("ORD002", "测试")

        assert result_lower == result_upper

    @pytest.mark.asyncio
    async def test_refund_async(self):
        """Test async version of refund processing."""
        tool = RefundTool()
        result = await tool._arun("ORD002", "测试原因")

        assert "退款申请已受理" in result


class TestCustomerInfoTool:
    """Test CustomerInfoTool functionality."""

    def test_customer_info_found(self):
        """Test querying an existing customer."""
        tool = CustomerInfoTool()
        result = tool._run("C001")

        assert "C001" in result
        assert "张三" in result
        assert "黄金会员" in result
        assert "138****1234" in result

    def test_customer_info_not_found(self):
        """Test querying a non-existent customer."""
        tool = CustomerInfoTool()
        result = tool._run("INVALID001")

        assert "未找到客户" in result
        assert "INVALID001" in result

    def test_customer_info_case_insensitive(self):
        """Test that customer ID is case insensitive."""
        tool = CustomerInfoTool()
        result_lower = tool._run("c001")
        result_upper = tool._run("C001")

        assert result_lower == result_upper

    def test_customer_info_strips_whitespace(self):
        """Test that customer ID is stripped of whitespace."""
        tool = CustomerInfoTool()
        result_stripped = tool._run("  C001  ")
        result_normal = tool._run("C001")

        assert result_stripped == result_normal

    def test_customer_info_all_customers(self):
        """Test querying all mock customers."""
        tool = CustomerInfoTool()

        for customer_id in ["C001", "C002", "C003"]:
            result = tool._run(customer_id)
            assert customer_id in result

    @pytest.mark.asyncio
    async def test_customer_info_async(self):
        """Test async version of customer info query."""
        tool = CustomerInfoTool()
        result = await tool._arun("C001")

        assert "张三" in result


class TestCreateTools:
    """Test create_tools function."""

    def test_create_tools_returns_list(self):
        """Test that create_tools returns a list."""
        tools = create_tools()
        assert isinstance(tools, list)

    def test_create_tools_returns_three_tools(self):
        """Test that create_tools returns exactly 3 tools."""
        tools = create_tools()
        assert len(tools) == 3

    def test_create_tools_correct_types(self):
        """Test that create_tools returns correct tool types."""
        tools = create_tools()

        tool_types = [type(t).__name__ for t in tools]
        assert "OrderQueryTool" in tool_types
        assert "RefundTool" in tool_types
        assert "CustomerInfoTool" in tool_types

    def test_create_tools_inherits_from_base_tool(self):
        """Test that created tools inherit from BaseTool."""
        from langchain_core.tools import BaseTool

        tools = create_tools()
        for tool in tools:
            assert isinstance(tool, BaseTool)


class TestGetToolNames:
    """Test get_tool_names function."""

    def test_get_tool_names_returns_list(self):
        """Test that get_tool_names returns a list."""
        names = get_tool_names()
        assert isinstance(names, list)

    def test_get_tool_names_returns_three_names(self):
        """Test that get_tool_names returns exactly 3 names."""
        names = get_tool_names()
        assert len(names) == 3

    def test_get_tool_names_correct_names(self):
        """Test that get_tool_names returns correct tool names."""
        names = get_tool_names()

        assert "order_query" in names
        assert "refund_process" in names
        assert "customer_info" in names


class TestToolsIntegration:
    """Integration tests for tools."""

    def test_tool_names_match_created_tools(self):
        """Test that tool names match created tools."""
        tools = create_tools()
        names = get_tool_names()

        tool_names = [t.name for t in tools]
        assert sorted(tool_names) == sorted(names)

    def test_tool_descriptions_not_empty(self):
        """Test that all tools have non-empty descriptions."""
        tools = create_tools()

        for tool in tools:
            assert tool.description
            assert len(tool.description) > 0

    def test_tool_names_are_strings(self):
        """Test that all tool names are strings."""
        tools = create_tools()

        for tool in tools:
            assert isinstance(tool.name, str)
