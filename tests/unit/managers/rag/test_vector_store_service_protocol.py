"""Protocol compliance tests for VectorStoreService implementations.

Tests that all implementations of VectorStoreService follow the protocol contract.
"""

from __future__ import annotations

import pytest

from mtg_card_app.managers.rag.services import ChromaVectorStoreService


# Parametrize with all VectorStoreService implementations
@pytest.fixture(
    params=[
        pytest.param("chroma", id="ChromaVectorStoreService"),
    ],
)
def vector_store_service(request, tmp_path):
    """Fixture that provides all VectorStoreService implementations."""
    if request.param == "chroma":
        service = ChromaVectorStoreService(
            data_dir=str(tmp_path / "chroma_test"),
            collection_name="test_collection",
        )
        yield service
        # Cleanup after test
        service.clear_all()
    # Add more implementations here (Pinecone, Weaviate, etc.)


class TestAddEmbedding:
    """Test add_embedding protocol compliance."""

    def test_returns_true_on_success(self, vector_store_service):
        """Test that add_embedding returns True on success."""
        # Arrange
        card_id = "test-card-123"
        embedding = [0.1, 0.2, 0.3, 0.4] * 96  # 384-dim for all-MiniLM
        metadata = {"name": "Test Card", "type": "Creature"}
        document = "Test Card oracle text"

        # Act
        result = vector_store_service.add_embedding(
            card_id,
            embedding,
            metadata,
            document,
        )

        # Assert
        assert result is True

    def test_can_retrieve_added_embedding(self, vector_store_service):
        """Test that added embeddings can be retrieved."""
        # Arrange
        card_id = "test-card-456"
        embedding = [0.5, 0.6, 0.7, 0.8] * 96
        metadata = {"name": "Test Card 2"}
        document = "Test document"

        # Act
        add_result = vector_store_service.add_embedding(
            card_id,
            embedding,
            metadata,
            document,
        )
        get_result = vector_store_service.get_embedding(card_id)

        # Assert
        assert add_result is True
        assert get_result is not None
        assert len(get_result) == len(embedding)

    @pytest.mark.parametrize(
        "embedding_dim",
        [
            384,   # all-MiniLM-L6-v2
            768,   # BERT-based models
            1536,  # OpenAI ada-002
        ],
    )
    def test_handles_various_dimensions(self, vector_store_service, embedding_dim):
        """Test adding embeddings with various dimensions."""
        # Arrange
        card_id = f"card-{embedding_dim}"
        embedding = [0.1] * embedding_dim
        metadata = {"dimension": embedding_dim}
        document = f"Test with {embedding_dim} dimensions"

        # Act
        result = vector_store_service.add_embedding(
            card_id,
            embedding,
            metadata,
            document,
        )

        # Assert
        assert result is True
        assert vector_store_service.exists(card_id)


class TestAddEmbeddings:
    """Test add_embeddings protocol compliance (batch)."""

    def test_returns_true_on_success(self, vector_store_service):
        """Test that add_embeddings returns True on success."""
        # Arrange
        ids = ["card-1", "card-2", "card-3"]
        embeddings = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
        metadatas = [{"name": f"Card {i}"} for i in range(3)]
        documents = [f"Document {i}" for i in range(3)]

        # Act
        result = vector_store_service.add_embeddings(
            ids,
            embeddings,
            metadatas,
            documents,
        )

        # Assert
        assert result is True
        assert vector_store_service.count() >= 3


class TestGetEmbedding:
    """Test get_embedding protocol compliance."""

    def test_returns_none_for_nonexistent_id(self, vector_store_service):
        """Test that get_embedding returns None for nonexistent IDs."""
        # Act
        result = vector_store_service.get_embedding("nonexistent-id")

        # Assert
        assert result is None

    def test_returns_embedding_for_existing_id(self, vector_store_service):
        """Test that get_embedding returns the embedding for existing IDs."""
        # Arrange
        card_id = "test-card-get"
        embedding = [0.1] * 384
        vector_store_service.add_embedding(
            card_id,
            embedding,
            {"test": "data"},
            "test doc",
        )

        # Act
        result = vector_store_service.get_embedding(card_id)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == len(embedding)


class TestExists:
    """Test exists protocol compliance."""

    def test_returns_false_for_nonexistent_id(self, vector_store_service):
        """Test that exists returns False for nonexistent IDs."""
        # Act
        result = vector_store_service.exists("nonexistent-id")

        # Assert
        assert result is False

    def test_returns_true_for_existing_id(self, vector_store_service):
        """Test that exists returns True for existing IDs."""
        # Arrange
        card_id = "test-card-exists"
        vector_store_service.add_embedding(
            card_id,
            [0.1] * 384,
            {"test": "data"},
            "test doc",
        )

        # Act
        result = vector_store_service.exists(card_id)

        # Assert
        assert result is True


class TestSearchSimilar:
    """Test search_similar protocol compliance."""

    def test_returns_list_of_tuples(self, vector_store_service):
        """Test that search_similar returns a list of tuples."""
        # Arrange
        # Add some embeddings first
        for i in range(5):
            vector_store_service.add_embedding(
                f"card-{i}",
                [0.1 * i] * 384,
                {"index": i},
                f"Document {i}",
            )

        query_embedding = [0.15] * 384

        # Act
        result = vector_store_service.search_similar(query_embedding, n_results=3)

        # Assert
        assert isinstance(result, list)
        assert len(result) <= 3
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 3  # (id, score, metadata)
            assert isinstance(item[0], str)  # id
            assert isinstance(item[1], (int, float))  # score
            assert isinstance(item[2], dict)  # metadata


class TestDelete:
    """Test delete protocol compliance."""

    def test_returns_true_on_successful_delete(self, vector_store_service):
        """Test that delete returns True when successful."""
        # Arrange
        card_id = "test-card-delete"
        vector_store_service.add_embedding(
            card_id,
            [0.1] * 384,
            {"test": "data"},
            "test doc",
        )

        # Act
        result = vector_store_service.delete(card_id)

        # Assert
        assert result is True
        assert not vector_store_service.exists(card_id)


class TestCount:
    """Test count protocol compliance."""

    def test_returns_integer(self, vector_store_service):
        """Test that count returns an integer."""
        # Act
        result = vector_store_service.count()

        # Assert
        assert isinstance(result, int)
        assert result >= 0

    def test_count_increases_after_add(self, vector_store_service):
        """Test that count increases after adding embeddings."""
        # Arrange
        initial_count = vector_store_service.count()

        # Act
        vector_store_service.add_embedding(
            "test-count",
            [0.1] * 384,
            {"test": "data"},
            "test doc",
        )
        new_count = vector_store_service.count()

        # Assert
        assert new_count == initial_count + 1


class TestServiceInfo:
    """Test service information methods."""

    def test_get_service_name(self, vector_store_service):
        """Test that get_service_name returns a string."""
        # Act
        result = vector_store_service.get_service_name()

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_stats(self, vector_store_service):
        """Test that get_stats returns a dictionary."""
        # Act
        result = vector_store_service.get_stats()

        # Assert
        assert isinstance(result, dict)

