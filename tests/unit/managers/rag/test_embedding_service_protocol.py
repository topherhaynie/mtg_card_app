"""Protocol compliance tests for EmbeddingService implementations.

Tests that all implementations of EmbeddingService follow the protocol contract.
"""

from __future__ import annotations

import pytest

from mtg_card_app.managers.rag.services import SentenceTransformerEmbeddingService


# Parametrize with all EmbeddingService implementations
@pytest.fixture(
    params=[
        pytest.param("sentence_transformer", id="SentenceTransformerEmbeddingService"),
    ],
)
def embedding_service(request):
    """Fixture that provides all EmbeddingService implementations."""
    if request.param == "sentence_transformer":
        # Use a lightweight model for testing, or mock if too slow
        service = SentenceTransformerEmbeddingService(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
        )
        yield service
    # Add more implementations here (OpenAI, Cohere, etc.)


class TestEmbedText:
    """Test embed_text protocol compliance."""

    def test_returns_list_of_floats(self, embedding_service):
        """Test that embed_text returns a list of floats."""
        # Act
        result = embedding_service.embed_text("Test text")

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(x, float) for x in result)

    def test_consistent_dimensions(self, embedding_service):
        """Test that multiple embeddings have consistent dimensions."""
        # Act
        result1 = embedding_service.embed_text("First text")
        result2 = embedding_service.embed_text("Second text")

        # Assert
        assert len(result1) == len(result2)

    @pytest.mark.parametrize(
        "text",
        [
            "Simple text",
            "Text with {special} [characters]!",
            "Multi\nline\ntext",
            "",  # Edge case: empty string
        ],
    )
    def test_handles_various_inputs(self, embedding_service, text):
        """Test embedding various text inputs."""
        # Act
        result = embedding_service.embed_text(text)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0


class TestEmbedTexts:
    """Test embed_texts protocol compliance (batch)."""

    def test_returns_list_of_embeddings(self, embedding_service):
        """Test that embed_texts returns a list of embeddings."""
        # Arrange
        texts = ["First text", "Second text", "Third text"]

        # Act
        result = embedding_service.embed_texts(texts)

        # Assert
        assert isinstance(result, list)
        assert len(result) == len(texts)
        assert all(isinstance(emb, list) for emb in result)
        assert all(all(isinstance(x, float) for x in emb) for emb in result)


class TestServiceInfo:
    """Test service information methods."""

    def test_get_embedding_dimension(self, embedding_service):
        """Test that get_embedding_dimension returns an integer."""
        # Act
        result = embedding_service.get_embedding_dimension()

        # Assert
        assert isinstance(result, int)
        assert result > 0

    def test_dimension_matches_actual_output(self, embedding_service):
        """Test that reported dimension matches actual embedding size."""
        # Act
        dimension = embedding_service.get_embedding_dimension()
        embedding = embedding_service.embed_text("Test")

        # Assert
        assert len(embedding) == dimension

    def test_get_model_name(self, embedding_service):
        """Test that get_model_name returns a string."""
        # Act
        result = embedding_service.get_model_name()

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_service_name(self, embedding_service):
        """Test that get_service_name returns a string."""
        # Act
        result = embedding_service.get_service_name()

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_stats(self, embedding_service):
        """Test that get_stats returns a dictionary."""
        # Act
        result = embedding_service.get_stats()

        # Assert
        assert isinstance(result, dict)
