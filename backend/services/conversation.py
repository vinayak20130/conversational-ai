"""
Service for managing conversations with LLMs.
"""

from typing import Dict, List, Optional, AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel

from config import DEFAULT_SYSTEM_PROMPT


class ConversationService:
    """Service for managing conversations with LLMs."""

    def __init__(self, llm: BaseChatModel, system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        """
        Initialize the conversation service.

        Args:
            llm: LangChain chat model
            system_prompt: System prompt for the conversation
        """
        self.llm = llm
        self.system_prompt = system_prompt
        self.messages: List[Dict] = []
        self._initialize_conversation()

    def _initialize_conversation(self):
        """Initialize the conversation with a system prompt."""
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def add_user_message(self, content: str):
        """
        Add a user message to the conversation.

        Args:
            content: Message content
        """
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        """
        Add an assistant message to the conversation.

        Args:
            content: Message content
        """
        self.messages.append({"role": "assistant", "content": content})

    def get_messages(self) -> List[Dict]:
        """
        Get all messages in the conversation.

        Returns:
            List of message dictionaries
        """
        return self.messages

    def reset_conversation(self):
        """Reset the conversation."""
        self._initialize_conversation()

    def _convert_to_langchain_messages(self):
        """
        Convert the messages to LangChain format.

        Returns:
            List of LangChain message objects
        """
        lc_messages = []

        for message in self.messages:
            if message["role"] == "system":
                lc_messages.append(SystemMessage(content=message["content"]))
            elif message["role"] == "user":
                lc_messages.append(HumanMessage(content=message["content"]))
            elif message["role"] == "assistant":
                lc_messages.append(AIMessage(content=message["content"]))

        return lc_messages

    async def generate_response(self) -> str:
        """
        Generate a response from the LLM.

        Returns:
            Response text
        """
        lc_messages = self._convert_to_langchain_messages()
        response = await self.llm.ainvoke(lc_messages)
        response_text = response.content

        # Add the response to the conversation
        self.add_assistant_message(response_text)

        return response_text

    async def generate_response_stream(self) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the LLM.

        Yields:
            Response text chunks
        """
        lc_messages = self._convert_to_langchain_messages()
        response_text = ""

        async for chunk in self.llm.astream(lc_messages):
            if hasattr(chunk, "content"):
                chunk_text = chunk.content
                response_text += chunk_text
                yield chunk_text

        # Add the complete response to the conversation
        self.add_assistant_message(response_text)
