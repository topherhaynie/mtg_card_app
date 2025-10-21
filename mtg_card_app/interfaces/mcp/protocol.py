"""Abstract protocol for MCP communication (stdio, socket, etc.)."""

from abc import ABC, abstractmethod
from typing import Any


class MCPProtocol(ABC):
    """Abstract base class for MCP communication protocols."""

    @abstractmethod
    def read_request(self) -> Any:
        """Read a request from the client (blocking)."""

    @abstractmethod
    def send_response(self, response: Any) -> None:
        """Send a response to the client."""

    @abstractmethod
    def close(self) -> None:
        """Close the protocol connection."""
