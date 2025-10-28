"""Conversation history management for chat interface.

This module manages conversation context across multiple messages,
maintaining a sliding window of recent exchanges to provide to the LLM.
"""

import logging
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)


class ConversationHistory:
    """Manages conversation history with a sliding window.
    
    Stores user queries and assistant responses, maintaining context
    for natural follow-up questions. Uses a deque for efficient
    memory management with automatic oldest-message eviction.
    """

    def __init__(self, max_turns: int = 5):
        """Initialize conversation history.
        
        Args:
            max_turns: Maximum number of conversation turns to remember.
                      One turn = user message + assistant response.
                      Default is 5 turns (10 messages total).
        """
        self.max_turns = max_turns
        self.messages: deque[dict[str, str]] = deque(maxlen=max_turns * 2)
        logger.info(f"Initialized conversation history (max {max_turns} turns)")
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history.
        
        Args:
            content: The user's message text
        """
        self.messages.append({
            "role": "user",
            "content": content
        })
        logger.debug(f"Added user message (total: {len(self.messages)} messages)")
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation history.
        
        Args:
            content: The assistant's response text
        """
        self.messages.append({
            "role": "assistant",
            "content": content
        })
        logger.debug(f"Added assistant message (total: {len(self.messages)} messages)")
    
    def get_messages(self) -> list[dict[str, str]]:
        """Get all messages in the conversation history.
        
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        return list(self.messages)
    
    def get_context_string(self) -> str:
        """Format conversation history as a readable string for LLM context.
        
        Returns:
            Formatted conversation history, or empty string if no history
        """
        if not self.messages:
            return ""
        
        context_lines = ["Previous conversation:"]
        for msg in self.messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            # Truncate long messages for context (keep first 200 chars)
            content = msg["content"]
            if len(content) > 200:
                content = content[:197] + "..."
            context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)
    
    def clear(self) -> None:
        """Clear all conversation history."""
        self.messages.clear()
        logger.info("Cleared conversation history")
    
    def get_turn_count(self) -> int:
        """Get the number of conversation turns (user+assistant pairs).
        
        Returns:
            Number of complete turns in history
        """
        return len(self.messages) // 2
    
    def get_message_count(self) -> int:
        """Get the total number of messages in history.
        
        Returns:
            Total message count
        """
        return len(self.messages)
    
    def to_dict(self) -> dict[str, Any]:
        """Export conversation history to a dictionary.
        
        Useful for serialization, debugging, or display.
        
        Returns:
            Dictionary with history metadata and messages
        """
        return {
            "max_turns": self.max_turns,
            "turn_count": self.get_turn_count(),
            "message_count": self.get_message_count(),
            "messages": self.get_messages()
        }
