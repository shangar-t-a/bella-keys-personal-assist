"""Retrieval tool module for Bella v2 Deep Agent using LangChain vectorstore retriever."""

from langchain_core.tools import BaseTool, create_retriever_tool

from app.dependencies.ai_dependencies import get_app_vector_store


def get_personal_wiki_retriever_tool() -> BaseTool:
    """Create a retriever tool directly connected to the application vector store.

    Returns:
        BaseTool: Configured retriever tool for searching personal notes and wiki facts.
    """
    vector_store = get_app_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    return create_retriever_tool(
        retriever=retriever,
        name="search_personal_wiki",
        description="Searches user's personal notes, wiki facts, and document archive for relevant information.",
    )
