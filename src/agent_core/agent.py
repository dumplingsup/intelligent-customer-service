"""Agent initialization and management."""

import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load environment variables
load_dotenv()

# ConversationBufferMemory is not available in LangChain 1.x
# We use manual session management instead


# Agent system prompt
AGENT_SYSTEM_PROMPT = """You are a professional customer service assistant for an e-commerce platform.

Your responsibilities include:
1. Answering customer questions using the provided context from the knowledge base
2. Helping customers query their order status using the order_query tool
3. Assisting with refund applications using the refund_process tool
4. Looking up customer information using the customer_info tool

Guidelines:
- Be polite, friendly, and professional in all interactions
- Use the knowledge base context when available to answer questions
- Use tools when you need to query order information or process refunds
- If you're not sure about something, politely let the customer know
- Keep responses concise and helpful
- Always prioritize customer satisfaction

Remember to cite sources when answering from the knowledge base."""


def create_agent(
    tools: Optional[List[BaseTool]] = None,
    model: str = "gpt-4",
    temperature: float = 0.7,
    system_prompt: str = AGENT_SYSTEM_PROMPT,
    with_memory: bool = True
):
    """
    Create a ReAct agent with tools and memory.

    Args:
        tools: List of tools for the agent (uses default tools if None)
        model: LLM model name
        temperature: Model temperature
        system_prompt: System prompt for the agent
        with_memory: Whether to enable conversation memory

    Returns:
        ReAct agent instance
    """
    from src.agent_core.tools import create_tools

    if tools is None:
        tools = create_tools()

    # Create LLM with DeepSeek configuration
    llm = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", model),
        temperature=temperature,
        max_tokens=2000,
        openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
        openai_api_base=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    )

    # Create prompt template for ReAct agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages", optional=True),
    ])

    # Create ReAct agent using LangGraph
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=prompt
    )

    return agent


class CustomerServiceAgent:
    """
    Customer Service Agent wrapper with conversation management.
    """

    def __init__(
        self,
        tools: Optional[List[BaseTool]] = None,
        model: str = "gpt-4",
        temperature: float = 0.7
    ):
        """
        Initialize customer service agent.

        Args:
            tools: List of tools for the agent
            model: LLM model name
            temperature: Model temperature
        """
        try:
            from src.agent_core.tools import create_tools
        except ImportError:
            from agent_core.tools import create_tools

        self.tools = tools or create_tools()
        self.model_name = model
        self.temperature = temperature

        # Initialize LLM with DeepSeek configuration
        self.llm = ChatOpenAI(
            model=os.getenv("DEEPSEEK_MODEL", model),
            temperature=temperature,
            max_tokens=2000,
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        )

        # Create prompt template for ReAct agent
        agent_prompt = ChatPromptTemplate.from_messages([
            ("system", AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="messages", optional=True),
        ])
        
        # Create ReAct agent
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=agent_prompt
        )

        # Conversation history per session
        self._sessions: Dict[str, List[Dict[str, Any]]] = {}

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get or create session history."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        return self._sessions[session_id]

    def clear_session(self, session_id: str) -> None:
        """Clear session history."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    def process_message(
        self,
        message: str,
        session_id: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return response.

        Args:
            message: User message
            session_id: Session identifier
            context: Optional RAG context

        Returns:
            Response dictionary with answer and metadata
        """
        history = self.get_session_history(session_id)

        # Build input with context if provided
        if context:
            enhanced_message = f"""Context information:
{context}

User message: {message}"""
        else:
            enhanced_message = message

        # Prepare messages for agent
        messages = []

        # Add system prompt
        messages.append(("system", AGENT_SYSTEM_PROMPT))

        # Add conversation history (last 10 turns)
        for msg in history[-10:]:
            if msg["role"] == "user":
                messages.append(("human", msg["content"]))
            else:
                messages.append(("assistant", msg["content"]))

        # Add current message
        messages.append(("human", enhanced_message))

        try:
            # Invoke agent
            response = self.agent.invoke({"messages": messages})

            # Extract assistant message from response
            assistant_message = ""
            if "messages" in response:
                for msg in response["messages"]:
                    if hasattr(msg, "content") and msg.content:
                        assistant_message = msg.content
                        break

            # Save to history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": assistant_message})

            return {
                "answer": assistant_message,
                "session_id": session_id
            }

        except Exception as e:
            error_message = f"抱歉，处理您的请求时出现错误：{str(e)}"
            return {
                "answer": error_message,
                "session_id": session_id,
                "error": str(e)
            }

    def query(
        self,
        question: str,
        session_id: str,
        context: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process a query with optional RAG context.

        Args:
            question: User question
            session_id: Session identifier
            context: Optional list of context strings from RAG

        Returns:
            Response dictionary
        """
        context_str = "\n\n".join(context) if context else None
        return self.process_message(question, session_id, context_str)
