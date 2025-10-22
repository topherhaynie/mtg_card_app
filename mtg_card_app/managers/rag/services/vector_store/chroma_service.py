"""ChromaDB implementation of the vector store service."""

import logging
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class ChromaVectorStoreService:
    """ChromaDB implementation of vector storage.

    Uses ChromaDB's persistent client for local vector storage with HNSW indexing.
    """

    def __init__(
        self,
        data_dir: str = "data/chroma",
        collection_name: str = "embeddings",
    ):
        """Initialize ChromaDB vector store.

        Args:
            data_dir: Directory for ChromaDB persistence
            collection_name: Name of the collection

        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name

        # Lazy initialization
        self._client: chromadb.Client | None = None
        self._collection: chromadb.Collection | None = None

        logger.info(f"Initialized ChromaVectorStoreService with data_dir: {data_dir}")

    @property
    def client(self) -> chromadb.Client:
        """Get or create the ChromaDB client."""
        if self._client is None:
            logger.info(f"Initializing ChromaDB at: {self.data_dir}")
            self._client = chromadb.PersistentClient(
                path=str(self.data_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
            logger.debug("ChromaDB client initialized")
        return self._client

    @property
    def collection(self) -> chromadb.Collection:
        """Get or create the collection."""
        if self._collection is None:
            try:
                self._collection = self.client.get_collection(
                    name=self.collection_name,
                )
                logger.debug(f"Loaded existing collection: {self.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                self._collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Vector embeddings collection"},
                )
                logger.info(f"Created new collection: {self.collection_name}")
        return self._collection

    def add_embedding(
        self,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any],
        document: str,
    ) -> bool:
        """Add a single embedding to ChromaDB."""
        try:
            self.collection.add(
                ids=[id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[document],
            )
            logger.debug(f"Added embedding: {id}")
            return True
        except Exception as e:
            logger.error(f"Error adding embedding {id}: {e}")
            return False

    def add_embeddings(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
    ) -> bool:
        """Add multiple embeddings in batch."""
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents,
            )
            logger.debug(f"Added {len(ids)} embeddings")
            return True
        except Exception as e:
            logger.error(f"Error adding embeddings: {e}")
            return False

    def get_embedding(self, id: str) -> list[float] | None:
        """Retrieve an embedding by ID."""
        try:
            result = self.collection.get(
                ids=[id],
                include=["embeddings"],
            )
            # Check if we got results - ChromaDB returns empty lists if not found
            if not result or not result.get("ids") or len(result["ids"]) == 0:
                return None

            # If we have IDs, check if embeddings were included
            if "embeddings" not in result:
                return None

            embeddings_list = result["embeddings"]
            # embeddings_list should be a list; check length first to avoid numpy array truthiness issues
            if embeddings_list is None or len(embeddings_list) == 0:
                return None

            embedding = embeddings_list[0]
            if embedding is None:
                return None

            # Convert numpy array to list if needed
            if hasattr(embedding, "tolist"):
                return embedding.tolist()
            return list(embedding)
        except Exception as e:
            logger.error(f"Error retrieving embedding {id}: {e}")
            return None

    def exists(self, id: str) -> bool:
        """Check if an embedding exists."""
        try:
            result = self.collection.get(ids=[id])
            return bool(result and result["ids"])
        except Exception as e:
            logger.error(f"Error checking existence for {id}: {e}")
            return False

    def search_similar(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Search for similar embeddings using ChromaDB."""
        try:
            where_filter = filters if filters else None
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
            )

            # Parse results
            similar_items = []
            if results and results["ids"] and results["ids"][0]:
                for i, item_id in enumerate(results["ids"][0]):
                    distance = results["distances"][0][i]
                    # Convert distance to similarity (1 - distance)
                    similarity = 1 - distance
                    metadata = results["metadatas"][0][i]
                    similar_items.append((item_id, similarity, metadata))

            logger.debug(f"Found {len(similar_items)} similar items")
            return similar_items

        except Exception as e:
            logger.error(f"Error searching similar items: {e}")
            return []

    def delete(self, id: str) -> bool:
        """Delete an embedding from ChromaDB."""
        try:
            self.collection.delete(ids=[id])
            logger.debug(f"Deleted embedding: {id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting embedding {id}: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all embeddings from the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self._collection = None  # Force recreation
            logger.info("Cleared all embeddings")
            return True
        except Exception as e:
            logger.error(f"Error clearing embeddings: {e}")
            return False

    def count(self) -> int:
        """Get the total number of embeddings."""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error counting embeddings: {e}")
            return 0

    def get_stats(self) -> dict[str, Any]:
        """Get ChromaDB-specific statistics."""
        try:
            count = self.count()

            # Get disk usage
            chroma_size = sum(f.stat().st_size for f in self.data_dir.rglob("*") if f.is_file())

            return {
                "service": "ChromaDB",
                "collection_name": self.collection_name,
                "total_embeddings": count,
                "disk_usage_bytes": chroma_size,
                "disk_usage_mb": round(chroma_size / (1024 * 1024), 2),
                "storage_path": str(self.data_dir),
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}

    def get_service_name(self) -> str:
        """Get the service name."""
        return "ChromaDB"

    def export_embeddings(self, path: str) -> bool:
        """Export all embeddings to a specified path.

        Copies the entire ChromaDB persistence directory to the target path
        for creating data bundles or backups.

        Args:
            path: Destination path for the exported embeddings

        Returns:
            True if export successful, False otherwise

        """
        import shutil

        try:
            src_path = Path(self.data_dir)
            dest_path = Path(path)

            # Ensure ChromaDB has persisted everything
            # (ChromaDB auto-persists, but good to be explicit)
            if self._client is not None:
                logger.debug("Ensuring ChromaDB persistence before export")

            # Copy the entire ChromaDB directory
            if dest_path.exists():
                shutil.rmtree(dest_path)

            shutil.copytree(src_path, dest_path)
            logger.info("Exported embeddings to %s", path)
        except OSError:
            logger.exception("Failed to export embeddings to %s", path)
            return False
        else:
            return True

    def import_embeddings(self, path: str) -> bool:
        """Import embeddings from a specified path.

        Replaces the current ChromaDB directory with the one at the
        specified path, then reinitializes the client.

        Args:
            path: Source path containing embeddings to import

        Returns:
            True if import successful, False otherwise

        """
        import shutil

        try:
            src_path = Path(path)
            dest_path = Path(self.data_dir)

            if not src_path.exists():
                logger.error("Source embeddings not found at %s", path)
                return False

            # Close existing client/collection if open
            self._collection = None
            self._client = None

            # Replace the ChromaDB directory
            if dest_path.exists():
                shutil.rmtree(dest_path)

            shutil.copytree(src_path, dest_path)

            # Reinitialize client and collection
            # (will happen lazily on next access)
            logger.info("Imported embeddings from %s", path)
        except (OSError, FileNotFoundError):
            logger.exception("Failed to import embeddings from %s", path)
            return False
        else:
            return True

    def get_embedding_count(self) -> int:
        """Get the total number of embeddings in the store.

        This is an alias for count() to maintain consistency with the
        data bundle manifest naming conventions.

        Returns:
            Count of embeddings in the store

        """
        return self.count()
