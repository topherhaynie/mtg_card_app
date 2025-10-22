"""Base protocol for vector store services.

This defines the interface for any vector database that can store and search embeddings.
"""

from typing import Any, Protocol


class VectorStoreService(Protocol):
    """Protocol for vector storage services.

    This abstraction allows switching between different vector databases
    (ChromaDB, Pinecone, Weaviate, etc.) without changing the RAG manager.
    """

    def add_embedding(
        self,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any],
        document: str,
    ) -> bool:
        """Add a single embedding to the store.

        Args:
            id: Unique identifier for the embedding
            embedding: Vector embedding
            metadata: Metadata for filtering/retrieval
            document: Original text document

        Returns:
            True if successfully added, False otherwise

        """
        ...

    def add_embeddings(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
    ) -> bool:
        """Add multiple embeddings in batch.

        Args:
            ids: List of unique identifiers
            embeddings: List of vector embeddings
            metadatas: List of metadata dictionaries
            documents: List of original text documents

        Returns:
            True if successfully added, False otherwise

        """
        ...

    def get_embedding(self, id: str) -> list[float] | None:
        """Retrieve an embedding by ID.

        Args:
            id: Identifier to retrieve

        Returns:
            Embedding vector or None if not found

        """
        ...

    def exists(self, id: str) -> bool:
        """Check if an embedding exists.

        Args:
            id: Identifier to check

        Returns:
            True if exists, False otherwise

        """
        ...

    def search_similar(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Search for similar embeddings.

        Args:
            query_embedding: Query vector
            n_results: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of (id, similarity_score, metadata) tuples

        """
        ...

    def delete(self, id: str) -> bool:
        """Delete an embedding.

        Args:
            id: Identifier to delete

        Returns:
            True if deleted, False otherwise

        """
        ...

    def clear_all(self) -> bool:
        """Clear all embeddings from the store.

        Returns:
            True if successful, False otherwise

        """
        ...

    def count(self) -> int:
        """Get the total number of embeddings.

        Returns:
            Count of embeddings in the store

        """
        ...

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store.

        Returns:
            Dictionary with statistics (implementation-specific)

        """
        ...

    def get_service_name(self) -> str:
        """Get the name of the vector store service.

        Returns:
            Service name (e.g., "ChromaDB", "Pinecone")

        """
        ...

    def export_embeddings(self, path: str) -> bool:
        """Export all embeddings to a specified path.

        This method should export the vector store data (collection,
        embeddings, metadata, etc.) to the specified path for creating
        data bundles or backups.

        Args:
            path: Destination path for the exported embeddings

        Returns:
            True if export successful, False otherwise

        """
        ...

    def import_embeddings(self, path: str) -> bool:
        """Import embeddings from a specified path.

        This method should restore/import embeddings from the specified
        path, replacing or merging with existing data as appropriate for
        the implementation.

        Args:
            path: Source path containing embeddings to import

        Returns:
            True if import successful, False otherwise

        """
        ...

    def get_embedding_count(self) -> int:
        """Get the total number of embeddings in the store.

        This is an alias for count() to maintain consistency with the
        data bundle manifest naming conventions.

        Returns:
            Count of embeddings in the store

        """
        ...
