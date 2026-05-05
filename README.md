# 🌌 Bella Keys: AI-Powered Personal Intelligence

Bella Keys is a premium desktop application that combines professional-grade **Expense Management** with a sophisticated **AI Personal Assistant** (Bella).

Designed for data sovereignty and high performance, it leverages a unique "Inside-Out" architecture where your application logic is containerized while your data stays firmly on your host PC.

---

## ✨ Key Features

### 💰 Professional Expense Management

* **Deep Financial Tracking:** Manage multiple spending accounts with detailed debit/credit history.
* **Smart Dashboards:** Monthly summaries and trend analysis.
* **AI-Ready Data:** Built-in MCP (Model Context Protocol) support so your AI agent can reason about your finances.

### 🤖 Bella AI Assistant

* **Local-First Intelligence:** Powered by LangGraph and Ollama for private, fast, and local AI reasoning.
* **Personal Knowledge Base:** RAG-powered chat that understands your own documents and codebases.
* **Observability:** Built-in tracing with Arize Phoenix to see exactly how your AI agent thinks.

---

## 🏗️ The Hybrid "Inside-Out" Architecture

Bella Keys follows a unique design philosophy:

1. **Logic in Docker:** All backends (FastAPI, Qdrant) run in Docker for a consistent, zero-config experience.
2. **Data on Host:** Your primary database (PostgreSQL) and AI models (Ollama) live on your host machine.
3. **Complete Privacy:** Your data never leaves your system unless you explicitly configure a cloud provider.

---

## 📚 Documentation & Setup

To ensure a clear separation of concerns, our documentation is split into dedicated guides:

* **🚀 [Master Setup Guide](docs/user/master-setup-guide.md):** The definitive end-to-end guide for installing, configuring databases, and running the app.
* **🛠️ [Developer Workflow](docs/developer/development-workflow.md):** Technical structure, building from source, and contribution standards.
* **🏛️ [Architecture Deep-Dive](services/expense-manager-service/README.md):** Detailed look at the Clean Architecture and EMS patterns.

---

## 📂 Project Modules

* **[Desktop UI](keys-personal-assist-ui/README.md):** The Electron/React frontend.
* **[Expense Manager](services/expense-manager-service/README.md):** Financial tracking backend.
* **[Bella Chat Service](services/bella-chat-service/README.md):** AI orchestration engine.
* **[ETL Pipelines](services/etl-pipelines/README.md):** Knowledge base ingestion.
* **[MCP Servers](mcps/ems-mcp-server/README.md):** Model Context Protocol integrations.

---

> *Bella Keys: Professional Management. Personal Intelligence. Private by Design.*
