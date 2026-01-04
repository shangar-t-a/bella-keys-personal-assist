"""Simple chat agent for handling basic conversations."""

from pathlib import Path
from typing import TYPE_CHECKING

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from langgraph.prebuilt import (
    ToolNode,
    tools_condition,
)

from app.agents.base_agent import BaseAgent
from app.agents.prompts import ABOUT_BELLA_SYSTEM_PROMPT
from app.agents.simple_chat_agent.models import State
from app.agents.simple_chat_agent.prompts import SYNTHESIS_PROMPT_TEMPLATE

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel


class SimpleChatAgent(BaseAgent):
    """A simple chat agent implementation.

    Attributes:
        model (BaseChatModel): The chat model used by the agent.
        graph (StateGraph): The graph associated with the agent. Defines the workflow.
        chain: The chain associated with the agent. Compiled graph.
    """

    def __init__(self, model: "BaseChatModel", tools: list | None = None):
        """Initialize the simple chat agent.

        Args:
            model (BaseChatModel): The chat model to be used by the agent.
            tools (list, optional): List of tools to be added to the agent. Defaults to None.
        """
        super().__init__(model=model, tools=tools)

    async def _generate_response(self, state: State) -> dict:
        """Generate a response based on user input.

        Args:
            state (State): The current state containing user input.

        Returns:
            dict: A dictionary containing the generated messages.
        """
        messages = [
            SystemMessage(content=ABOUT_BELLA_SYSTEM_PROMPT),
            HumanMessage(
                content=SYNTHESIS_PROMPT_TEMPLATE.format(
                    question=state["messages"][-1].content,
                )
            ),
        ]
        if len(state["messages"]) > 1:
            messages += state["messages"][:-1]

        return {"messages": [await self.model.ainvoke(messages)]}

    def _build_graph_with_tools(self):
        """Build the state graph for the agent with tools."""
        # Create the state graph
        self.graph = StateGraph(State)

        # Add the nodes
        self.graph.add_node("generate_response", self._generate_response)
        self.graph.add_node("tools", ToolNode(self.tools))

        # Add edges
        self.graph.add_edge(START, "generate_response")
        self.graph.add_conditional_edges(
            "generate_response",
            # When the LLM response is tool calling, this condition will be true
            tools_condition,
        )
        # Loop back to tools node for multiple tool calls
        self.graph.add_edge("tools", "generate_response")

    def _build_graph_without_tools(self):
        """Build the state graph for the agent without tools."""
        # Create the state graph
        self.graph = StateGraph(State)

        # Add the nodes
        self.graph.add_node("generate_response", self._generate_response)

        # Add edges
        self.graph.add_edge(START, "generate_response")
        self.graph.add_edge("generate_response", END)

    def _display_graph(self):
        """Display the agent's state graph. Development use only."""
        output_file_path = Path(__file__).parent / "simple_chat_agent_graph.png"

        # get PNG bytes from the graph
        png_bytes = self.chain.get_graph().draw_mermaid_png()

        # save to file
        output_file_path.write_bytes(png_bytes)

        print(f"Graph saved to {output_file_path}")


if __name__ == "__main__":
    # Example usage
    import asyncio

    from langchain_ollama import ChatOllama

    async def _test_agent():
        """Internal test function for the SimpleChatAgent."""
        chat_model = ChatOllama(model="qwen3:4b", temperature=0.7)
        agent = SimpleChatAgent(model=chat_model)
        agent._display_graph()
        async for chunk in await agent.run(user_input="Hello, how are you?", stream=True):
            print(chunk, end="", flush=True)

    asyncio.run(_test_agent())
