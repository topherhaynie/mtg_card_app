"""Stdio-based implementation of MCPService."""

import json
import sys

from .base import MCPService


class StdioMCPService(MCPService):
    """MCP service using standard input/output for communication."""

    def read_request(self) -> dict[str, object]:
        """Read one JSON object from stdin as a request."""
        line = sys.stdin.readline()
        if not line:
            raise EOFError
        return json.loads(line)

    def send_response(self, response: object) -> None:
        """Write the JSON-serializable response to stdout as a single line."""
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

    def close(self) -> None:
        """No resources to release for stdio transport."""
        return
