"""Base protocol for vector store services.

This defines the interface for any vector database that can store and search embeddings.
"""

from typing import Any, Dict, List, Optional, Protocol, Tuple


class VectorStoreService(Protocol):
    """Protocol for vector storage services.

    This abstraction allows switching between different vector databases
    (ChromaDB, Pinecone, Weaviate, etc.) without changing the RAG manager.
    """

    def add_embedding(
        self,
        id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
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
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        documents: List[str],
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

    def get_embedding(self, id: str) -> Optional[List[float]]:
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
        query_embedding: List[float],
        n_results: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
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

    def get_stats(self) -> Dict[str, Any]:
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
