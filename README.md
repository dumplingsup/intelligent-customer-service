# Intelligent Customer Service System

企业级智能客服系统，基于 LangChain + RAG 技术，支持从非结构化文档中精确检索知识并处理复杂业务操作。

## 功能特性

- **智能问答**：支持自然语言问题输入，自动检索知识库提供准确答案
- **文档管理**：支持 PDF、Word、TXT 格式文档上传、解析和分块
- **工具集成**：订单查询、退款处理、客户信息查询
- **对话管理**：支持多轮对话上下文理解，会话历史记录
- **数据统计**：问题分类、响应时间监控（开发中）

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| Agent 框架 | LangChain | 1.x |
| LLM | OpenAI GPT-4 | - |
| 向量数据库 | Chroma | 1.x |
| Embedding | OpenAI text-embedding-3-small | - |
| Web 框架 | FastAPI | 0.x |
| 前端 UI | Streamlit | 1.x |

## 快速开始

### 环境要求

- Python 3.10+
- Poetry 2.x
- OpenAI API Key

### 安装

1. **克隆项目**
```bash
cd /home/chy/workproject/intelligent-customer-service
```

2. **安装依赖**
```bash
poetry install
```

3. **配置环境变量**
```bash
cp config/.env.example .env
# 编辑 .env 文件，填入 OPENAI_API_KEY
```

4. **启动 API 服务**
```bash
poetry run python -m uvicorn src.api.routes:app --host 0.0.0.0 --port 8000 --reload
```

5. **启动前端（另开终端）**
```bash
poetry run streamlit run src/frontend/app.py
```

6. **访问系统**
- API 文档：http://localhost:8000/docs
- 前端界面：http://localhost:8501

## Docker 部署

```bash
# 设置环境变量
export OPENAI_API_KEY=your_api_key

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 项目结构

```
intelligent-customer-service/
├── src/
│   ├── document_processor/     # 文档处理模块
│   │   ├── __init__.py
│   │   └── processor.py
│   ├── vector_database/        # 向量数据库模块
│   │   ├── __init__.py
│   │   └── store.py
│   ├── agent_core/             # Agent 核心模块
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── tools.py
│   ├── rag_chain/              # RAG 检索链
│   │   ├── __init__.py
│   │   └── chain.py
│   ├── api/                    # FastAPI 服务
│   │   ├── __init__.py
│   │   └── routes.py
│   └── frontend/               # Streamlit 前端
│       ├── __init__.py
│       └── app.py
├── data/                       # 示例文档
├── chroma_db/                  # 向量数据库存储
├── tests/                      # 测试用例
├── config/                     # 配置文件
│   └── .env.example
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## API 接口

### POST /api/query
处理用户查询
```json
{
  "query": "产品 A 的价格是多少？",
  "session_id": "optional-session-id"
}
```

### POST /api/upload
上传知识文档
- Content-Type: multipart/form-data
- 支持：.pdf, .docx, .txt

### GET /api/history/{session_id}
获取会话历史

### DELETE /api/history/{session_id}
清除会话历史

### GET /api/health
健康检查

## 运行测试

```bash
poetry run pytest tests/ -v
```

## 配置说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| OPENAI_API_KEY | OpenAI API 密钥 | - |
| APP_HOST | API 监听地址 | 0.0.0.0 |
| APP_PORT | API 监听端口 | 8000 |
| CHROMA_PERSIST_DIR | Chroma DB 存储路径 | ./chroma_db |
| LLM_MODEL | LLM 模型 | gpt-4 |
| EMBEDDING_MODEL | Embedding 模型 | text-embedding-3-small |
| CHUNK_SIZE | 文本分块大小 | 500 |
| CHUNK_OVERLAP | 分块重叠 | 50 |

## 开发计划

- [ ] 添加 Rerank 重排序，提升检索准确率
- [ ] 添加常用问题缓存，降低 LLM 调用成本
- [ ] 支持多模型切换
- [ ] 添加日志监控和异常告警

## License

MIT License

## Author

dumplingsup <421730156@qq.com>
