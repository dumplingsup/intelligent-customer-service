"""Streamlit Frontend for Intelligent Customer Service System."""

import os
import requests
import streamlit as st

# Configuration
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="智能客服系统",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = ""
if "messages" not in st.session_state:
    st.session_state.messages = []


def query_api(query: str, session_id: str) -> dict:
    """Send query to API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/query",
            json={"query": query, "session_id": session_id},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def upload_documents(files) -> dict:
    """Upload documents to API."""
    try:
        files_data = [("files", (f.name, f.read(), f.type)) for f in files]
        response = requests.post(
            f"{API_BASE_URL}/api/upload",
            files=files_data,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# Sidebar
with st.sidebar:
    st.title("⚙️ 设置")

    # Session ID
    st.subheader("会话管理")
    if st.session_state.session_id:
        st.text_input(
            "当前会话 ID",
            value=st.session_state.session_id,
            disabled=True
        )
        if st.button("新建会话"):
            st.session_state.session_id = ""
            st.session_state.messages = []
            st.rerun()
    else:
        st.info("开始对话后将自动生成会话 ID")

    # Document Upload
    st.subheader("📄 知识库管理")
    uploaded_files = st.file_uploader(
        "上传文档（PDF/Word/TXT）",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    if st.button("上传文档"):
        if uploaded_files:
            with st.spinner("正在上传文档..."):
                result = upload_documents(uploaded_files)
                if "error" in result:
                    st.error(f"上传失败：{result['error']}")
                else:
                    st.success(
                        f"已处理 {result.get('documents_processed', 0)} 个文件，"
                        f"创建 {result.get('chunks_created', 0)} 个文本块"
                    )

    # API Status
    st.subheader("🔗 API 状态")
    try:
        health_response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if health_response.status_code == 200:
            st.success("API 在线")
            health_data = health_response.json()
            st.json(health_data)
        else:
            st.error("API 响应异常")
    except Exception:
        st.error("无法连接到 API")

    # Footer
    st.markdown("---")
    st.markdown("**智能客服系统 v0.1.0**")


# Main content
st.title("🤖 智能客服系统")
st.markdown("欢迎使用企业级智能客服助手，请输入您的问题。")

# Chat messages display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 查看参考来源"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"**来源 {i}:**")
                    st.text(source[:500] + "..." if len(source) > 500 else source)

# Chat input
if prompt := st.chat_input("请输入您的问题..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("正在思考..."):
            # Ensure session ID exists
            if not st.session_state.session_id:
                import uuid
                st.session_state.session_id = str(uuid.uuid4())

            # Query API
            result = query_api(prompt, st.session_state.session_id)

            if "error" in result:
                st.error(f"查询失败：{result['error']}")
                assistant_message = "抱歉，处理您的请求时出现错误。"
            else:
                assistant_message = result.get("answer", "抱歉，我没有理解您的问题。")
                sources = result.get("sources", [])

                # Display response
                st.markdown(assistant_message)

                if sources:
                    with st.expander("📚 查看参考来源"):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**来源 {i}:**")
                            st.text(source[:500] + "..." if len(source) > 500 else source)

                # Add to messages
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "sources": sources
                })

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Powered by LangChain + RAG | 基于 GPT-4 和 Chroma DB"
    "</div>",
    unsafe_allow_html=True
)
