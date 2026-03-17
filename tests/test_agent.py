"""Tests for agent core module."""

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.tools import BaseTool

from src.agent_core.agent import (
    CustomerServiceAgent,
    create_agent,
    AGENT_SYSTEM_PROMPT
)


def create_mock_llm():
    """Create a mock LLM for testing."""
    mock_llm = MagicMock()
    mock_llm.invoke = MagicMock(return_value=MagicMock(content="Mock response"))
    return mock_llm


def setup_getenv_mock(mock_getenv):
    """Setup getenv mock with default values."""
    mock_getenv.side_effect = lambda key, default=None: {
        'DEEPSEEK_MODEL': 'gpt-4',
        'DEEPSEEK_API_KEY': 'test-key',
        'DEEPSEEK_BASE_URL': 'https://api.deepseek.com'
    }.get(key, default)
    return mock_getenv


class TestCreateAgent:
    """Test create_agent function."""

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_create_agent_with_default_tools(self, mock_react, mock_chat):
        """Test create_agent with default tools."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = create_agent()

                assert agent is not None
                mock_create_tools.assert_called_once()

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_create_agent_with_custom_tools(self, mock_react, mock_chat):
        """Test create_agent with custom tools."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        custom_tools = [MagicMock(spec=BaseTool) for _ in range(2)]

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            with patch('os.getenv', return_value='test-key'):
                agent = create_agent(tools=custom_tools)

                assert agent is not None
                mock_create_tools.assert_not_called()

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_create_agent_with_custom_model(self, mock_react, mock_chat):
        """Test create_agent with custom model."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv') as mock_getenv:
                setup_getenv_mock(mock_getenv)
                create_agent(model="gpt-4")

                mock_chat.assert_called_once()
                call_kwargs = mock_chat.call_args[1]
                assert call_kwargs["model"] == "gpt-4"

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_create_agent_with_custom_temperature(self, mock_react, mock_chat):
        """Test create_agent with custom temperature."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                create_agent(temperature=0.9)

                mock_chat.assert_called_once()
                call_kwargs = mock_chat.call_args[1]
                assert call_kwargs["temperature"] == 0.9

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_create_agent_with_custom_system_prompt(self, mock_react, mock_chat):
        """Test create_agent with custom system prompt."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        custom_prompt = "You are a custom assistant."

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                create_agent(system_prompt=custom_prompt)

                mock_react.assert_called_once()


class TestCustomerServiceAgentInit:
    """Test CustomerServiceAgent initialization."""

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_agent_init_with_default_params(self, mock_react, mock_chat):
        """Test agent initialization with default parameters."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                assert agent.model_name == "gpt-4"
                assert agent.temperature == 0.7
                assert hasattr(agent, '_sessions')

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_agent_init_with_custom_params(self, mock_react, mock_chat):
        """Test agent initialization with custom parameters."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent(
                    model="custom-model",
                    temperature=0.8
                )

                assert agent.model_name == "custom-model"
                assert agent.temperature == 0.8

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_agent_init_with_custom_tools(self, mock_react, mock_chat):
        """Test agent initialization with custom tools."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        custom_tools = [MagicMock(spec=BaseTool) for _ in range(2)]

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent(tools=custom_tools)

                assert agent.tools == custom_tools
                mock_create_tools.assert_not_called()

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_agent_init_empty_sessions(self, mock_react, mock_chat):
        """Test that agent initializes with empty sessions dict."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                assert agent._sessions == {}


class TestSessionManagement:
    """Test session management functionality."""

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_get_session_history_new_session(self, mock_react, mock_chat):
        """Test getting history for a new session."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                history = agent.get_session_history("new-session")

                assert history == []
                assert "new-session" in agent._sessions

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_get_session_history_existing_session(self, mock_react, mock_chat):
        """Test getting history for an existing session."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()
                agent._sessions["existing-session"] = [{"role": "user", "content": "Hello"}]

                history = agent.get_session_history("existing-session")

                assert len(history) == 1
                assert history[0]["content"] == "Hello"

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_get_session_history_same_session_reused(self, mock_react, mock_chat):
        """Test that same session is reused."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                history1 = agent.get_session_history("test-session")
                history2 = agent.get_session_history("test-session")

                assert history1 is history2

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_clear_session_existing_session(self, mock_react, mock_chat):
        """Test clearing an existing session."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()
                agent._sessions["test-session"] = [{"role": "user", "content": "Hello"}]

                agent.clear_session("test-session")

                assert "test-session" not in agent._sessions

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_clear_session_nonexistent_session(self, mock_react, mock_chat):
        """Test clearing a nonexistent session (no-op)."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm
        mock_react.return_value = MagicMock()

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                agent.clear_session("nonexistent-session")

                assert agent._sessions == {}


class TestQueryProcessing:
    """Test query processing functionality."""

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_query_without_context(self, mock_react, mock_chat):
        """Test query processing without context."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm

        mock_agent = MagicMock()
        mock_agent.invoke = MagicMock(return_value={
            "messages": [MagicMock(content="Test response")]
        })
        mock_react.return_value = mock_agent

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                result = agent.query(
                    question="测试问题",
                    session_id="test-session"
                )

                assert "answer" in result
                assert result["session_id"] == "test-session"
                assert mock_agent.invoke.called

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_query_with_context(self, mock_react, mock_chat):
        """Test query processing with context."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm

        mock_agent = MagicMock()
        mock_agent.invoke = MagicMock(return_value={
            "messages": [MagicMock(content="Test response")]
        })
        mock_react.return_value = mock_agent

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                context = ["上下文 1", "上下文 2"]
                result = agent.query(
                    question="测试问题",
                    session_id="test-session",
                    context=context
                )

                assert "answer" in result
                assert mock_agent.invoke.called

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_query_with_empty_context_list(self, mock_react, mock_chat):
        """Test query processing with empty context list."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm

        mock_agent = MagicMock()
        mock_agent.invoke = MagicMock(return_value={
            "messages": [MagicMock(content="Test response")]
        })
        mock_react.return_value = mock_agent

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                result = agent.query(
                    question="测试问题",
                    session_id="test-session",
                    context=[]
                )

                assert "answer" in result

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_query_saves_to_history(self, mock_react, mock_chat):
        """Test that query saves to session history."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm

        mock_agent = MagicMock()
        mock_agent.invoke = MagicMock(return_value={
            "messages": [MagicMock(content="Test response")]
        })
        mock_react.return_value = mock_agent

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                agent.query(
                    question="测试问题",
                    session_id="test-session"
                )

                history = agent.get_session_history("test-session")
                assert len(history) == 2
                assert history[0]["role"] == "user"
                assert history[0]["content"] == "测试问题"

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_query_handles_error(self, mock_react, mock_chat):
        """Test that query handles errors gracefully."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm

        mock_agent = MagicMock()
        mock_agent.invoke = MagicMock(side_effect=Exception("Test error"))
        mock_react.return_value = mock_agent

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                result = agent.query(
                    question="测试问题",
                    session_id="test-session"
                )

                assert "answer" in result
                assert "error" in result
                assert "抱歉" in result["answer"]

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_query_limits_history_to_10_turns(self, mock_react, mock_chat):
        """Test that query only uses last 10 turns of history."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm

        mock_agent = MagicMock()
        mock_agent.invoke = MagicMock(return_value={
            "messages": [MagicMock(content="Test response")]
        })
        mock_react.return_value = mock_agent

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                agent._sessions["test-session"] = [
                    {"role": "user" if i % 2 == 0 else "assistant", "content": f"Message {i}"}
                    for i in range(20)
                ]

                agent.query(
                    question="测试问题",
                    session_id="test-session"
                )

                assert mock_agent.invoke.called


class TestProcessMessage:
    """Test process_message functionality."""

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_process_message_with_context(self, mock_react, mock_chat):
        """Test process_message with context string."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm

        mock_agent = MagicMock()
        mock_agent.invoke = MagicMock(return_value={
            "messages": [MagicMock(content="Test response")]
        })
        mock_react.return_value = mock_agent

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                result = agent.process_message(
                    message="测试消息",
                    session_id="test-session",
                    context="这是上下文信息"
                )

                assert "answer" in result
                assert result["session_id"] == "test-session"

    @patch('src.agent_core.agent.ChatOpenAI')
    @patch('src.agent_core.agent.create_react_agent')
    def test_process_message_without_context(self, mock_react, mock_chat):
        """Test process_message without context."""
        mock_llm = create_mock_llm()
        mock_chat.return_value = mock_llm

        mock_agent = MagicMock()
        mock_agent.invoke = MagicMock(return_value={
            "messages": [MagicMock(content="Test response")]
        })
        mock_react.return_value = mock_agent

        with patch('src.agent_core.tools.create_tools') as mock_create_tools:
            mock_create_tools.return_value = [MagicMock(spec=BaseTool)]
            with patch('os.getenv', return_value='test-key'):
                agent = CustomerServiceAgent()

                result = agent.process_message(
                    message="测试消息",
                    session_id="test-session"
                )

                assert "answer" in result


class TestAgentSystemPrompt:
    """Test agent system prompt."""

    def test_system_prompt_not_empty(self):
        """Test that system prompt is defined."""
        assert AGENT_SYSTEM_PROMPT
        assert len(AGENT_SYSTEM_PROMPT) > 0

    def test_system_prompt_contains_responsibilities(self):
        """Test that system prompt contains responsibilities."""
        assert "customer service" in AGENT_SYSTEM_PROMPT.lower()
        assert "order" in AGENT_SYSTEM_PROMPT.lower()

    def test_system_prompt_contains_guidelines(self):
        """Test that system prompt contains guidelines."""
        assert "polite" in AGENT_SYSTEM_PROMPT.lower() or "professional" in AGENT_SYSTEM_PROMPT.lower()
