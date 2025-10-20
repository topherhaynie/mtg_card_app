"""Card data service interfaces."""

from .base import CardDataService
from .scryfall_service import ScryfallCardDataService

__all__ = ["CardDataService", "ScryfallCardDataService"]
