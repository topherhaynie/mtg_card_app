"""JSON-RPC over stdio service supporting MCP-style Content-Length framing.

This service is backward-compatible with the current line-delimited JSON used by tests.
If a header block with Content-Length is present, it will parse and read exactly that many
bytes as the JSON request body. Otherwise, it falls back to reading a single line.
"""

from __future__ import annotations

import contextlib
import json
import sys

from .base import MCPService


class JSONRPCStdioService(MCPService):
    """Stdio transport that can read/write JSON-RPC messages.

    Read behavior:
    - If the first non-empty data looks like headers (e.g., Content-Length: N),
      it will parse headers until a blank line, then read N bytes as the body.
    - Otherwise, it falls back to reading one line of JSON.

    Write behavior:
    - Writes a single JSON line. Upstream manager already wraps JSON-RPC envelopes
      when required.
    """

    def read_request(self) -> dict[str, object]:
        """Read a single request from stdin.

        Supports MCP-style Content-Length framing and falls back to
        line-delimited JSON if no headers are present.
        """
        # Peek first line to determine framing
        first_pos = sys.stdin.tell() if hasattr(sys.stdin, "tell") else None
        first_line = sys.stdin.readline()
        if not first_line:
            raise EOFError

        # Detect headers (Content-Length style)
        if first_line.lower().startswith("content-length:"):
            # Parse Content-Length
            try:
                content_length = int(first_line.split(":", 1)[1].strip())
            except ValueError as exc:
                raise EOFError from exc

            # Consume header lines until blank line
            while True:
                line = sys.stdin.readline()
                if line is None or line == "":
                    # Unexpected EOF while parsing headers
                    raise EOFError
                if line.strip() == "":
                    break

            # Read exact body length
            body = sys.stdin.read(content_length)
            if body is None or len(body) == 0:
                raise EOFError
            return json.loads(body)

        # Fallback to line-delimited JSON
        try:
            return json.loads(first_line)
        except json.JSONDecodeError:
            # If we can seek back, try to restore and re-raise
            if first_pos is not None and hasattr(sys.stdin, "seek"):
                with contextlib.suppress(OSError, ValueError):
                    sys.stdin.seek(first_pos)
            raise

    def send_response(self, response: object) -> None:
        """Write the JSON-serialized response as a single line to stdout."""
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

    def close(self) -> None:
        """No-op close for stdio transport."""
        return
