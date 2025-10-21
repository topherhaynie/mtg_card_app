"""Protocol compliance tests for CardDataService implementations.

Tests that all implementations of CardDataService follow the protocol contract.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from mtg_card_app.managers.card_data.services import ScryfallCardDataService


# Parametrize with all CardDataService implementations
@pytest.fixture(
    params=[
        pytest.param("scryfall", id="ScryfallCardDataService"),
    ],
)
def card_data_service(request):
    """Fixture that provides all CardDataService implementations."""
    if request.param == "scryfall":
        # Mock the ScryfallClient to avoid actual API calls
        with patch("mtg_card_app.managers.card_data.services.scryfall_service.ScryfallClient") as mock_client_class:
            mock_client = MagicMock()
            # Configure mock to return proper types
            mock_client.get_request_stats.return_value = {"requests": 0, "errors": 0}
            mock_client_class.return_value = mock_client
            service = ScryfallCardDataService()
            service._mock_client = mock_client  # Store for test access
            yield service
    # Add more implementations here as they're created


class TestGetCardByName:
    """Test get_card_by_name protocol compliance."""

    def test_returns_dict_on_success(self, card_data_service, sample_card_data):
        """Test that get_card_by_name returns a dict when card is found."""
        # Arrange
        card_data_service._mock_client.get_card_by_name.return_value = sample_card_data

        # Act
        result = card_data_service.get_card_by_name("Sol Ring", exact=True)

        # Assert
        assert isinstance(result, dict)
        assert "name" in result
        assert "id" in result

    def test_returns_none_when_not_found(self, card_data_service):
        """Test that get_card_by_name returns None when card is not found."""
        # Arrange
        from mtg_card_app.interfaces.scryfall.exceptions import CardNotFoundError

        card_data_service._mock_client.get_card_by_name.side_effect = CardNotFoundError("Not found")

        # Act
        result = card_data_service.get_card_by_name("Nonexistent Card")

        # Assert
        assert result is None

    @pytest.mark.parametrize(
        ("name", "exact"),
        [
            ("Sol Ring", True),
            ("Lightning Bolt", True),
            ("Black Lotus", False),  # Fuzzy search
        ],
    )
    def test_exact_parameter(self, card_data_service, sample_card_data, name, exact):
        """Test that exact parameter is respected."""
        # Arrange
        card_data_service._mock_client.get_card_by_name.return_value = sample_card_data

        # Act
        result = card_data_service.get_card_by_name(name, exact=exact)

        # Assert
        assert result is not None
        # Verify the client was called with the right fuzzy parameter
        card_data_service._mock_client.get_card_by_name.assert_called_once()
        call_args = card_data_service._mock_client.get_card_by_name.call_args
        assert call_args[1]["fuzzy"] == (not exact)  # fuzzy is inverse of exact


class TestGetCardById:
    """Test get_card_by_id protocol compliance."""

    def test_returns_dict_on_success(self, card_data_service, sample_card_data):
        """Test that get_card_by_id returns a dict when card is found."""
        # Arrange
        card_id = "fd0c3051-a334-427b-9294-e42c43c93fab"
        card_data_service._mock_client.get_card_by_id.return_value = sample_card_data

        # Act
        result = card_data_service.get_card_by_id(card_id)

        # Assert
        assert isinstance(result, dict)
        assert result["id"] == sample_card_data["id"]

    def test_returns_none_when_not_found(self, card_data_service):
        """Test that get_card_by_id returns None when card is not found."""
        # Arrange
        from mtg_card_app.interfaces.scryfall.exceptions import CardNotFoundError

        card_data_service._mock_client.get_card_by_id.side_effect = CardNotFoundError("Not found")

        # Act
        result = card_data_service.get_card_by_id("invalid-id")

        # Assert
        assert result is None


class TestServiceInfo:
    """Test service information methods."""

    def test_get_service_name(self, card_data_service):
        """Test that get_service_name returns a string."""
        # Act
        result = card_data_service.get_service_name()

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_stats(self, card_data_service):
        """Test that get_stats returns a dictionary."""
        # Act
        result = card_data_service.get_stats()

        # Assert
        assert isinstance(result, dict)

