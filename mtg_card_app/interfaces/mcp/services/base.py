"""Abstract base class for MCP services (protocol layer)."""

from abc import ABC, abstractmethod


class MCPService(ABC):
    """Protocol for MCP communication services (stdio, socket, etc.)."""

    @abstractmethod
    def read_request(self) -> dict[str, object]:
        """Read a request from the client (blocking) and return a JSON object."""

    @abstractmethod
    def send_response(self, response: object) -> None:
        """Send a JSON-serializable response to the client."""

    @abstractmethod
    def close(self) -> None:
        """Close the protocol connection."""
