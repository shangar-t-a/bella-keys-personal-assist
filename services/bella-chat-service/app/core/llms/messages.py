"""Messages Module built for Langchain."""

from langchain_core.messages import HumanMessage, SystemMessage


class FrameLangChainMessage:
    """Frame LangChain Message."""

    @staticmethod
    def system(prompt: str) -> SystemMessage:
        """Frame system prompt."""
        message = SystemMessage(content=prompt)
        return message

    @staticmethod
    def user_text(prompt: str) -> HumanMessage:
        """Frame text input."""
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": prompt,
                }
            ],
        )
        return message

    @staticmethod
    def user_image(b64_image_str: str) -> HumanMessage:
        """Frame image input."""
        message = HumanMessage(
            content=[
                {
                    "type": "image",
                    "source_type": "base64",
                    "data": b64_image_str,
                    "mime_type": "image/jpeg",
                },
            ],
        )
        return message
