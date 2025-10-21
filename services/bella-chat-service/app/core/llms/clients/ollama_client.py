"""Ollama LLM client implementation."""

from langchain_core.messages.base import BaseMessage
from langchain_ollama import ChatOllama
from pydantic import BaseModel

from app.core.llms.clients import LLMClientInterface
from utilities.logger import GetAppLogger
from utilities.time_profile import log_exec_time


class OllamaClient(ChatOllama, LLMClientInterface):
    """Ollama LLM client implementation."""

    def __init__(self, model: str, temperature: float = 0.1, **kwargs):
        """Initialize the Ollama client with model and temperature.

        Args:
            model (str): The Ollama model to use.
            temperature (float): The temperature for response generation. Defaults to 0.1.
            **kwargs: Additional keyword arguments for the ChatOllama.

        Examples:
            ### Imports
            >>> from app.core.llms.clients import OllamaClient

            ### Initialize the Ollama client
            >>> client = OllamaClient(model="qwen2.5vl:7b", temperature=0.1)

            ### Simple message query
            >>> messages = [
            ...     {"role": "user", "content": "Hello, how are you?"}
            ... ]

            ### Query the Ollama LLM
            >>> response = client.query(messages)
            >>> print(response)
            Hello, how are you?

            ### Query Structured LLM
            #### Assume pydantic model `MyResponseModel` is defined
            >>> response = client.query_structured(messages, response_model=MyResponseModel)
            >>> print(response)
            MyResponseModel(field1='value1', field2='value2')

            ### Stream LLM response
            >>> for chunk in client.stream_query(messages):
            ...     print(chunk.content, end="", flush=True)
            Hello, how are you?
        """
        super().__init__(model=model, temperature=temperature, **kwargs)
        self._logger = GetAppLogger().get_logger()

    @log_exec_time
    def query(self, messages: list[BaseMessage]) -> str:
        """Query the Ollama LLM with a list of messages and return the response as a string."""
        self._logger.debug("Querying Ollama LLM with messages: %s", messages)
        response = self.invoke(messages)
        self._logger.debug("Ollama LLM response: %s", response)
        self._logger.debug("Ollama LLM response metadata: %s", response.response_metadata)
        return response.content

    @log_exec_time
    def query_structured(self, messages: list[BaseMessage], response_model: BaseModel) -> BaseModel:
        """Query the Ollama LLM and return the response as a structured pydantic model."""
        self._logger.debug("Querying Ollama LLM with messages: %s", messages)
        structured_llm = self.with_structured_output(response_model)
        response = structured_llm.invoke(messages)
        self._logger.debug("Ollama LLM response: %s", response)
        return response

    @log_exec_time
    def stream_query(self, messages: list[BaseMessage]):
        """Stream the Ollama LLM response for a list of messages."""
        self._logger.debug("Streaming Ollama LLM response for messages: %s", messages)
        response = ""
        for chunk in self.stream(messages):
            response += chunk.content
            yield chunk.content
        self._logger.debug("Completed streaming LLM response: %s", response)

    @log_exec_time
    async def aquery(self, messages: list[BaseMessage]) -> str:
        """Asynchronously query the Ollama LLM with a list of messages and return the response as a string."""
        self._logger.debug("Asynchronously querying Ollama LLM with messages: %s", messages)
        response = await self.ainvoke(messages)
        self._logger.debug("Ollama LLM response: %s", response)
        return response.content

    @log_exec_time
    async def aquery_structured(self, messages: list[BaseMessage], response_model: BaseModel) -> BaseModel:
        """Asynchronously query the Ollama LLM and return the response as a structured pydantic model."""
        self._logger.debug("Asynchronously querying Ollama LLM with messages: %s", messages)
        structured_llm = self.with_structured_output(response_model)
        response = await structured_llm.ainvoke(messages)
        self._logger.debug("Ollama LLM response: %s", response)
        return response

    @log_exec_time
    async def astream_query(self, messages: list[BaseMessage]):
        """Asynchronously stream the Ollama LLM response for a list of messages."""
        self._logger.debug("Asynchronously streaming Ollama LLM response for messages: %s", messages)
        response = ""
        async for chunk in self.astream(messages):
            response += chunk.content
            yield chunk.content
        self._logger.debug("Completed streaming LLM response: %s", response)


if __name__ == "__main__":
    # Example usage (for testing purposes)
    from langchain_core.messages import HumanMessage
    from pydantic import BaseModel, Field

    class NewtonLawsResponse(BaseModel):
        """Pydantic model for Newton's Laws response."""

        first_law: str = Field(..., description="Description of Newton's First Law")
        second_law: str = Field(..., description="Description of Newton's Second Law")
        third_law: str = Field(..., description="Description of Newton's Third Law")

    client = OllamaClient(model="qwen2.5vl:7b", temperature=0.1)

    messages = [
        HumanMessage(content="Explain Newton's three laws of motion in single sentence each."),
    ]

    response = client.query(messages=messages)
    print("-" * 20, "LLM Response:", "-" * 20, "\n", response, "\n" + "-" * 50)

    structured_response = client.query_structured(messages=messages, response_model=NewtonLawsResponse)
    print("-" * 20, "Structured LLM Response:", "-" * 20, "\n", structured_response, "\n" + "-" * 50)
    print(type(structured_response))

    # Stream LLM response
    print("-" * 20, "Streaming LLM Response:", "-" * 20)
    for chunk in client.stream_query(messages=messages):
        print(chunk, end="", flush=True)
    print("\n" + "-" * 50)

    # Async query LLM & Structured LLM & Stream LLM response
    import asyncio

    async def main():
        """Main async function to demonstrate async LLM queries."""
        response = await client.aquery(messages=messages)
        structured_response = await client.aquery_structured(messages=messages, response_model=NewtonLawsResponse)
        print("-" * 20, "Async LLM Response:", "-" * 20, "\n", response, "\n" + "-" * 50)
        print("-" * 20, "Async Structured LLM Response:", "-" * 20, "\n", structured_response, "\n" + "-" * 50)
        print(type(structured_response))

        print("-" * 20, "Async Streaming LLM Response:", "-" * 20)
        async for chunk in client.astream_query(messages=messages):
            print(chunk, end="", flush=True)
        print("\n", "-" * 50)

    asyncio.run(main())
