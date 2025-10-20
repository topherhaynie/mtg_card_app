"""Base service class for database operations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseService(ABC, Generic[T]):
    """Abstract base class for database services.

    Provides a consistent interface for CRUD operations across all services.
    This follows the Repository pattern for data access.
    """

    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity in the database.

        Args:
            entity: The entity to create

        Returns:
            The created entity with ID populated

        """

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Retrieve an entity by its ID.

        Args:
            entity_id: The entity's unique identifier

        Returns:
            The entity if found, None otherwise

        """

    @abstractmethod
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """Retrieve all entities.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entities

        """

    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an existing entity.

        Args:
            entity: The entity with updated values

        Returns:
            The updated entity

        """

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete an entity by ID.

        Args:
            entity_id: The entity's unique identifier

        Returns:
            True if deleted, False if not found

        """

    @abstractmethod
    def search(self, query: Dict[str, Any]) -> List[T]:
        """Search for entities matching criteria.

        Args:
            query: Search criteria as a dictionary

        Returns:
            List of matching entities

        """

    @abstractmethod
    def exists(self, entity_id: str) -> bool:
        """Check if an entity exists.

        Args:
            entity_id: The entity's unique identifier

        Returns:
            True if exists, False otherwise

        """

    @abstractmethod
    def count(self) -> int:
        """Count total number of entities.

        Returns:
            Total count

        """
