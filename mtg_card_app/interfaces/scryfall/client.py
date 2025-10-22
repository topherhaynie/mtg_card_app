"""Scryfall API client for fetching MTG card data."""

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any

from .exceptions import CardNotFoundError, InvalidRequestError, RateLimitError, ScryfallError


class ScryfallClient:
    """Client for interacting with the Scryfall API.

    Scryfall is a free, comprehensive MTG card database with a robust API.
    Rate limit: ~10 requests per second (we'll respect 100ms between requests).

    API Documentation: https://scryfall.com/docs/api
    """

    BASE_URL = "https://api.scryfall.com"
    RATE_LIMIT_DELAY = 0.1  # 100ms between requests

    def __init__(self):
        """Initialize the Scryfall client."""
        self._last_request_time: datetime | None = None
        self._request_count = 0

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        if self._last_request_time:
            elapsed = (datetime.now() - self._last_request_time).total_seconds()
            if elapsed < self.RATE_LIMIT_DELAY:
                time.sleep(self.RATE_LIMIT_DELAY - elapsed)

        self._last_request_time = datetime.now()
        self._request_count += 1

    def _make_request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a request to the Scryfall API.

        Args:
            endpoint: API endpoint (e.g., "/cards/named")
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            ScryfallError: On API errors
            RateLimitError: When rate limited
            CardNotFoundError: When card not found

        """
        self._rate_limit()

        url = f"{self.BASE_URL}{endpoint}"
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data

        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise CardNotFoundError(f"Card not found: {url}") from e
            if e.code == 429:
                raise RateLimitError("Scryfall API rate limit exceeded") from e
            if e.code == 400:
                raise InvalidRequestError(f"Invalid request to Scryfall: {e.reason}") from e
            raise ScryfallError(f"Scryfall API error {e.code}: {e.reason}") from e

        except Exception as e:
            raise ScryfallError(f"Failed to fetch from Scryfall: {e!s}") from e

    def get_card_by_name(self, name: str, fuzzy: bool = False) -> dict[str, Any]:
        """Get a card by its name.

        Args:
            name: The card name
            fuzzy: Whether to use fuzzy matching

        Returns:
            Card data from Scryfall

        """
        endpoint = "/cards/named"
        param_key = "fuzzy" if fuzzy else "exact"
        params = {param_key: name}

        return self._make_request(endpoint, params)

    def get_card_by_id(self, card_id: str) -> dict[str, Any]:
        """Get a card by its Scryfall ID.

        Args:
            card_id: The Scryfall UUID

        Returns:
            Card data from Scryfall

        """
        endpoint = f"/cards/{card_id}"
        return self._make_request(endpoint)

    def search_cards(
        self,
        query: str,
        unique: str = "cards",
        order: str = "name",
        include_extras: bool = False,
    ) -> list[dict[str, Any]]:
        """Search for cards using Scryfall search syntax.

        Args:
            query: Search query (e.g., "t:creature c:green cmc<=3")
            unique: How to handle duplicate cards ("cards", "art", "prints")
            order: Sort order ("name", "set", "released", "rarity", "cmc", etc.)
            include_extras: Include extra cards (tokens, emblems, etc.)

        Returns:
            List of matching cards

        Example queries:
            - "t:creature c:green": Green creatures
            - "oracle:draw cmc<=2": Cards with "draw" that cost 2 or less
            - "c:w c:u t:instant": White-blue instants
            - "f:commander": Cards legal in Commander

        """
        endpoint = "/cards/search"
        params = {
            "q": query,
            "unique": unique,
            "order": order,
        }

        if include_extras:
            params["include_extras"] = "true"

        all_cards = []

        # Handle pagination
        while True:
            data = self._make_request(endpoint, params)

            if "data" in data:
                all_cards.extend(data["data"])

            # Check for more pages
            if data.get("has_more", False) and "next_page" in data:
                endpoint = data["next_page"].replace(self.BASE_URL, "")
                params = {}  # Next page URL already has params
            else:
                break

        return all_cards

    def get_bulk_data(self, bulk_type: str = "default_cards") -> str:
        """Get URL for bulk data download.

        Bulk data is useful for downloading the entire card database.
        This method returns the download URL - you'll need to download it separately.

        Args:
            bulk_type: Type of bulk data
                - "oracle_cards": Unique cards (one per name)
                - "default_cards": All printings (recommended for combos)
                - "all_cards": Everything including tokens
                - "rulings": All card rulings

        Returns:
            Download URL for the bulk data

        """
        endpoint = "/bulk-data"
        data = self._make_request(endpoint)

        for item in data.get("data", []):
            if item.get("type") == bulk_type:
                return item.get("download_uri", "")

        raise ScryfallError(f"Bulk data type '{bulk_type}' not found")

    def get_random_card(self, query: str | None = None) -> dict[str, Any]:
        """Get a random card, optionally matching a search query.

        Args:
            query: Optional search query to filter random card

        Returns:
            Random card data

        """
        endpoint = "/cards/random"
        params = {"q": query} if query else None

        return self._make_request(endpoint, params)

    def get_card_rulings(self, card_id: str) -> list[dict[str, Any]]:
        """Get rulings for a specific card.

        Args:
            card_id: Scryfall card ID

        Returns:
            List of rulings

        """
        endpoint = f"/cards/{card_id}/rulings"
        data = self._make_request(endpoint)

        return data.get("data", [])

    def autocomplete(self, query: str, include_extras: bool = False) -> list[str]:
        """Get card name autocomplete suggestions.

        Args:
            query: Partial card name
            include_extras: Include extra cards

        Returns:
            List of card name suggestions

        """
        endpoint = "/cards/autocomplete"
        params = {"q": query}

        if include_extras:
            params["include_extras"] = "true"

        data = self._make_request(endpoint, params)
        return data.get("data", [])

    def get_sets(self) -> list[dict[str, Any]]:
        """Get all MTG sets.

        Returns:
            List of set data

        """
        endpoint = "/sets"
        data = self._make_request(endpoint)
        return data.get("data", [])

    def get_request_stats(self) -> dict[str, Any]:
        """Get statistics about requests made.

        Returns:
            Dictionary with request statistics

        """
        return {
            "total_requests": self._request_count,
            "last_request_time": self._last_request_time.isoformat() if self._last_request_time else None,
        }


# Utility functions for common searches


def build_combo_search_query(
    colors: list[str] | None = None,
    max_cmc: int | None = None,
    card_types: list[str] | None = None,
    keywords: list[str] | None = None,
) -> str:
    """Build a Scryfall search query for finding combo pieces.

    Args:
        colors: List of color codes (W, U, B, R, G)
        max_cmc: Maximum converted mana cost
        card_types: List of card types to include
        keywords: List of keywords to search for

    Returns:
        Scryfall search query string

    Example:
        >>> build_combo_search_query(colors=['U', 'R'], max_cmc=3, keywords=['draw'])
        "c:ur cmc<=3 oracle:draw"

    """
    parts = []

    if colors:
        color_str = "".join(colors).lower()
        parts.append(f"c:{color_str}")

    if max_cmc is not None:
        parts.append(f"cmc<={max_cmc}")

    if card_types:
        type_queries = [f"t:{t.lower()}" for t in card_types]
        parts.append(f"({' OR '.join(type_queries)})")

    if keywords:
        keyword_queries = [f"oracle:{kw}" for kw in keywords]
        parts.append(f"({' OR '.join(keyword_queries)})")

    return " ".join(parts)
