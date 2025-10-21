"""Abstract base class for MCP services (protocol layer)."""

from abc import ABC, abstractmethod
from typing import Any


class MCPService(ABC):
    """Protocol for MCP communication services (stdio, socket, etc.)."""

    @abstractmethod
    def read_request(self) -> Any:
        """Read a request from the client (blocking)."""

    @abstractmethod
    def send_response(self, response: Any) -> None:
        """Send a response to the client."""

    @abstractmethod
    def close(self) -> None:
        """Close the protocol connection."""
