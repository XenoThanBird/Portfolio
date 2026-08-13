# Agentic AI & Enterprise Tooling

End-to-end agentic architectures for enterprise IT service management and AI portfolio governance. This section contains three reusable templates demonstrating production patterns for RAG agents, MCP servers, and multi-agent frameworks.

No proprietary data, internal URLs, or employer-specific configurations are included.

---

## Templates

### 1. RAG Agent Starter

A production-ready Retrieval-Augmented Generation agent built on LangChain, LangGraph, and FAISS with structured output, tool integration, and observability.

| File | Description |
| ---- | ----------- |
| `rag_agent/agent.py` | LangGraph workflow — query analysis, retrieval, synthesis, validation |
| `rag_agent/config.py` | YAML + env var configuration with provider abstraction |
| `rag_agent/schemas.py` | Pydantic models for queries, responses, documents, and metrics |
| `rag_agent/vector_store.py` | FAISS vector store with persistence and similarity search |
| `rag_agent/tools.py` | External tool integrations (Wikipedia, ArXiv) |
| `rag_agent/config.yaml` | Default configuration (models, thresholds, tool toggles) |
| `rag_agent/requirements.txt` | Dependencies |
| `rag_agent/example.py` | Usage example |

### 2. MCP Server Template

A clean Model Context Protocol server template with tool registration, structured responses, and async HTTP client patterns.

| File | Description |
| ---- | ----------- |
| `mcp_server/server.py` | MCP server with `@list_tools` and `@call_tool` handlers |
| `mcp_server/client.py` | Async HTTP client with retry and exponential backoff |
| `mcp_server/config.py` | Immutable dataclass configuration from environment variables |
| `mcp_server/claude_desktop_config.json` | Registration config for Claude Desktop |
| `mcp_server/requirements.txt` | Dependencies |

### 3. Multi-Agent MCP Framework

A generic multi-agent orchestration scaffold with API key management, audit logging, and tool routing.

| File | Description |
| ---- | ----------- |
| `multi_agent/orchestrator.py` | Agent router — dispatches tasks to specialized agents |
| `multi_agent/audit_logger.py` | Structured audit logging (JSONL) with retention |
| `multi_agent/api_key_manager.py` | API key validation, rotation tracking, and usage logging |
| `multi_agent/.env.template` | Environment variable template |

---

## Tech Stack

`Python` `LangChain` `LangGraph` `FAISS` `MCP` `Pydantic` `OpenAI` `Anthropic` `httpx` `asyncio`
