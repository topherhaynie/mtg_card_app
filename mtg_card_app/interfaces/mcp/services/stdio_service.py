"""Stdio-based implementation of MCPService."""

import json
import sys
from typing import Any

from .base import MCPService


class StdioMCPService(MCPService):
    """MCP service using standard input/output for communication."""

    def read_request(self) -> Any:
        line = sys.stdin.readline()
        if not line:
            raise EOFError
        return json.loads(line)

    def send_response(self, response: Any) -> None:
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

    def close(self) -> None:
        pass  # Nothing to close for stdio
