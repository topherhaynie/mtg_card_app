"""Exceptions for Scryfall API interactions."""


class ScryfallError(Exception):
    """Base exception for Scryfall API errors."""


class RateLimitError(ScryfallError):
    """Raised when Scryfall API rate limit is exceeded."""


class CardNotFoundError(ScryfallError):
    """Raised when a card is not found in Scryfall."""


class InvalidRequestError(ScryfallError):
    """Raised when the request to Scryfall is invalid."""
