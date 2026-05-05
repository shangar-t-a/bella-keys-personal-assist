# 🤖 Bella Chat Service

The AI Orchestration engine for Bella Keys. This service handles multi-turn reasoning, RAG (Retrieval-Augmented Generation), and agentic workflows using **LangGraph**.

## Core Features

* **Agentic Orchestration:** Built with LangGraph to handle complex, stateful AI interactions.
* **Multi-Agent System:**
  * `expense-manager-agent`: Interfaces with the EMS MCP server to reason about financial data.
  * `keys-personal-wiki-agent`: Performs RAG against your local vector database (Qdrant).
* **Flexible LLM Support:** Integrated with Ollama (local) and cloud providers (Gemini/OpenAI).
* **Semantic Memory:** Uses Qdrant for storing and retrieving personal knowledge.

## Hybrid Architecture

This service follows the project-wide **Inside-Out** model:

* **Logic:** Runs in Docker to manage complex Python dependencies (LangChain, PyTorch, etc.).
* **Intelligence:** Connects to **Ollama** running on your host machine.
* **Storage:** Connects to your host's **PostgreSQL** for chat checkpointers and **Qdrant** for vector storage.

## Technical Stack

* FastAPI
* LangGraph & LangChain
* Pydantic AI
* SQLAlchemy (Async)
