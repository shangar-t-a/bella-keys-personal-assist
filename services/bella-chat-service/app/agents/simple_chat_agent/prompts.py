"""Prompts for the Simple Chat Agent."""

from langchain_core.prompts import PromptTemplate

SYNTHESIS_PROMPT = """
You are `Simple Chat Agent`, part of Bella, a precise, context-focused assistant.

INSTRUCTIONS to answer the user's `question`:
1. Provide a friendly, concise and factual reply.
2. Use markdown **bold**, __italics__ for emphasis and md tables where appropriate.
3. Try to provide short sectioned answers with headings and bullet points where appropriate to improve readability.

User Question:
```
{question}
```
"""
SYNTHESIS_PROMPT_TEMPLATE = PromptTemplate(
    template=SYNTHESIS_PROMPT,
    input_variables=[
        "question",
    ],
)

if __name__ == "__main__":
    prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
        question="Hey Bella, can you tell me a joke?",
    )
    print(prompt)
