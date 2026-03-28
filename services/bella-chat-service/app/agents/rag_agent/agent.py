"""RAG agent for handling retrieval-augmented generation tasks."""

import json
from pathlib import Path
from typing import (
    TYPE_CHECKING,
)
from uuid import uuid4

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.agents.base_agent import BaseAgent
from app.agents.prompts import ABOUT_BELLA_SYSTEM_PROMPT
from app.agents.rag_agent.models import State
from app.agents.rag_agent.prompts import (
    GENERATE_RESPONSE_PROMPT_TEMPLATE,
    RAG_AGENT_SYSTEM_PROMPT,
)
from app.dependencies.ai_dependencies import (
    get_app_vector_store,
)
from utilities.logger import GetAppLogger

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel


_logger = GetAppLogger().get_logger()


class RAGAgent(BaseAgent):
    """A retrieval-augmented generation (RAG) agent implementation.

    Attributes:
        model (BaseChatModel): The chat model used by the agent.
        graph (StateGraph): The graph associated with the agent. Defines the workflow.
        chain: The chain associated with the agent. Compiled graph.
    """

    def __init__(self, model: "BaseChatModel"):
        """Initialize the simple chat agent.

        Args:
            model (BaseChatModel): The chat model to be used by the agent.
        """
        super().__init__(model=model)
        self.vector_store = get_app_vector_store()
        self._logger = GetAppLogger().get_logger()

    async def _retrieve_relevant_nodes(self, state: State) -> dict:
        """Find relevant contexts from the vector store based on the question.

        Args:
            state (State): The current state containing user input.

        Returns:
            dict: A dictionary containing relevant contexts.
        """
        question = state["messages"][-1].content
        relevant_docs = self.vector_store.similarity_search(query=question, k=3)
        self._logger.debug(f"Found {len(relevant_docs)} relevant documents for the question.")

        return {"retrieved_nodes": relevant_docs}

    async def _generate_response(self, state: State) -> dict:
        """Generate a response based on user input.

        Args:
            state (State): The current state containing user input.

        Returns:
            dict: A dictionary containing the generated messages.
        """
        # Frame context from relevant documents
        context = {}
        sources = set()
        for doc, score in state["retrieved_nodes"]:
            context[doc.metadata.get("id", str(uuid4()))] = {
                "page_content": doc.page_content,
                "score": score,
                "source": doc.metadata.get("source", "unknown"),
                "metadata": doc.metadata,
            }
            if doc.metadata.get("source"):
                sources.add(doc.metadata.get("source"))
        _logger.debug(f"Collected {len(sources)} unique sources from relevant documents: {len(context)}")

        # Create numbered sources list
        sources_list = {f"Source {i + 1}": source for i, source in enumerate(sources)}

        # Construct messages for the LLM
        messages = [
            SystemMessage(
                content=ABOUT_BELLA_SYSTEM_PROMPT + "\nAgent Role: RAG Agent\n" + RAG_AGENT_SYSTEM_PROMPT + "\n"
            ),
            HumanMessage(
                content=GENERATE_RESPONSE_PROMPT_TEMPLATE.format(
                    question=state["messages"][-1].content,
                    context=json.dumps(context, indent=2),
                    sources=json.dumps(sources_list, indent=2),
                )
            ),
        ]
        if len(state["messages"]) > 1:
            messages += state["messages"][:-1]

        _logger.info("Generating response for your query...")
        return {
            "messages": [await self.model.ainvoke(messages)],
            "sources": sources_list,
        }

    def _build_graph(self):
        """Build the state graph for the agent."""
        # Create the state graph
        self.graph = StateGraph(State)

        # Add the nodes
        self.graph.add_node("find_relevant_contexts", self._retrieve_relevant_nodes)
        self.graph.add_node("generate_response", self._generate_response)

        # Add edges
        self.graph.add_edge(START, "find_relevant_contexts")
        self.graph.add_edge("find_relevant_contexts", "generate_response")
        self.graph.add_edge("generate_response", END)

    def _display_graph(self):
        """Display the agent's state graph. Development use only."""
        output_file_path = Path(__file__).parent / "rag_agent_graph.png"

        # get PNG bytes from the graph
        png_bytes = self.chain.get_graph().draw_mermaid_png()

        # save to file
        output_file_path.write_bytes(png_bytes)

        self._logger.info(f"Graph saved to {output_file_path}")


if __name__ == "__main__":
    # Example usage
    import asyncio

    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_ollama import ChatOllama

    provider = "google"

    async def _test_agent():
        """Internal test function for the RAGAgent."""
        if provider == "google":
            chat_model = ChatGoogleGenerativeAI(model="models/gemini-3.1-flash-lite-preview", temperature=0.1)
        else:
            chat_model = ChatOllama(model="qwen3.5:4b", temperature=0.1, num_ctx=32000)

        agent = RAGAgent(model=chat_model)
        agent._display_graph()

        response = await agent.run(user_input="Hello, tell me about Key's Experience?", stream=True)
        async for token in response:
            print(token, end="", flush=True)

    asyncio.run(_test_agent())
