"""RAG Retrieval QA with modern LangChain API."""

from typing import Optional, List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLLM
from langchain_openai import ChatOpenAI
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# RAG Prompt Template
RAG_PROMPT_TEMPLATE = """You are a professional customer service assistant. Please answer user questions based on the following context information.
If there is no relevant information in the context, please politely inform the user.

Context information:
{context}

User question: {question}

Please answer in a concise and friendly tone:"""

# System prompt for better responses
SYSTEM_PROMPT = """You are a professional customer service assistant. Your role is to:
1. Answer user questions accurately based on the provided context
2. Cite sources when possible
3. Be polite and friendly in your tone
4. If you don't know the answer based on the context, politely say so
5. Keep answers concise and helpful"""


def format_docs(docs) -> str:
    """Format documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


def create_rag_prompt(
    system_prompt: str = SYSTEM_PROMPT,
    rag_template: str = RAG_PROMPT_TEMPLATE
) -> ChatPromptTemplate:
    """
    Create the RAG prompt template.

    Args:
        system_prompt: System instruction prompt
        rag_template: RAG-specific template

    Returns:
        ChatPromptTemplate instance
    """
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", rag_template)
    ])


def create_rag_chain(
    retriever: VectorStoreRetriever,
    llm: Optional[BaseLLM] = None,
    prompt: Optional[ChatPromptTemplate] = None
):
    """
    Create RAG retrieval QA chain using modern LangChain LCEL API.

    Args:
        retriever: Vector store retriever
        llm: Language model instance (creates default if None)
        prompt: Custom prompt template (creates default if None)

    Returns:
        RAG chain (Runnable)
    """
    if llm is None:
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            max_tokens=2000
        )

    if prompt is None:
        prompt = create_rag_prompt()

    # Build RAG chain using LCEL
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def create_conversational_rag_prompt(
    system_prompt: str = SYSTEM_PROMPT
) -> ChatPromptTemplate:
    """
    Create conversational RAG prompt with chat history support.

    Args:
        system_prompt: System instruction prompt

    Returns:
        ChatPromptTemplate instance
    """
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{chat_history}"),
        ("human", """Context information:
{context}

User question: {question}

Please answer in a concise and friendly tone, considering the conversation history:""")
    ])


class RAGService:
    """
    RAG Service for handling document QA operations.
    """

    def __init__(
        self,
        retriever: VectorStoreRetriever,
        llm: Optional[BaseLLM] = None
    ):
        """
        Initialize RAG service.

        Args:
            retriever: Vector store retriever
            llm: Language model instance
        """
        self.retriever = retriever
        self.llm = llm or ChatOpenAI(model="gpt-4", temperature=0.7)
        self.chain = None

    def get_chain(self, with_history: bool = False):
        """
        Get or create the RAG chain.

        Args:
            with_history: Whether to include chat history support

        Returns:
            RAG chain instance
        """
        if with_history:
            prompt = create_conversational_rag_prompt()
        else:
            prompt = create_rag_prompt()

        if with_history:
            # For conversational RAG, we need to handle history differently
            # This is a simplified version
            return (
                {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
        else:
            return create_rag_chain(self.retriever, self.llm, prompt)

    def query(
        self,
        question: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a query and return answer with sources.

        Args:
            question: User question
            chat_history: Optional conversation history

        Returns:
            Dictionary with answer and source documents
        """
        # Get context from retriever
        context_docs = self.retriever.invoke(question)
        context = format_docs(context_docs)

        # Create chain and invoke
        chain = self.get_chain()
        answer = chain.invoke(question)

        return {
            "answer": answer,
            "source_documents": context_docs,
            "context": [doc.page_content for doc in context_docs]
        }
