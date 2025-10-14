"""Unit tests for the Abstract API client."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_abstract_api.api_client import AbstractAPIError, AbstractClient
from mcp_abstract_api.api_models import (
    EmailValidationResponse,
    IPGeolocationResponse,
    PhoneValidationResponse,
)


@pytest.fixture
def client() -> AbstractClient:
    """Create a client instance for testing."""
    return AbstractClient(api_key="test_key")


class TestAbstractClient:
    """Test the AbstractClient class."""

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test client can be used as context manager."""
        async with AbstractClient(api_key="test_key") as client:
            assert client is not None
            assert client._session is not None

    @pytest.mark.asyncio
    async def test_validate_email(self, client: AbstractClient) -> None:
        """Test email validation."""
        mock_response = {
            "email": "test@example.com",
            "deliverability": "DELIVERABLE",
            "quality_score": 0.95,
            "is_valid_format": {"value": True},
            "is_free_email": {"value": False},
            "is_disposable_email": {"value": False},
            "is_role_email": {"value": False},
            "is_catchall_email": {"value": False},
            "is_mx_found": {"value": True},
            "is_smtp_valid": {"value": True},
        }

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.validate_email("test@example.com")

            assert isinstance(result, EmailValidationResponse)
            assert result.email == "test@example.com"
            assert result.quality_score == 0.95

    @pytest.mark.asyncio
    async def test_validate_phone(self, client: AbstractClient) -> None:
        """Test phone validation."""
        mock_response = {
            "phone": "+1234567890",
            "valid": True,
            "format": {"international": "+1 234-567-890"},
            "country": {"code": "US", "name": "United States"},
            "type": "mobile",
        }

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.validate_phone("+1234567890", "US")

            assert isinstance(result, PhoneValidationResponse)
            assert result.phone == "+1234567890"
            assert result.valid is True

    @pytest.mark.asyncio
    async def test_geolocate_ip(self, client: AbstractClient) -> None:
        """Test IP geolocation."""
        mock_response = {
            "ip_address": "8.8.8.8",
            "city": "Mountain View",
            "country": "United States",
            "country_code": "US",
            "latitude": 37.386,
            "longitude": -122.0838,
        }

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.geolocate_ip("8.8.8.8")

            assert isinstance(result, IPGeolocationResponse)
            assert result.ip_address == "8.8.8.8"
            assert result.city == "Mountain View"

    @pytest.mark.asyncio
    async def test_api_error_handling(self, client: AbstractClient) -> None:
        """Test API error handling."""
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = AbstractAPIError(status=401, message="Invalid API key")

            with pytest.raises(AbstractAPIError) as exc_info:
                await client.validate_email("test@example.com")

            assert exc_info.value.status == 401
            assert "Invalid API key" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_get_timezone_requires_params(self, client: AbstractClient) -> None:
        """Test that get_timezone raises error without location or coordinates."""
        with pytest.raises(ValueError, match="Either location or latitude/longitude"):
            await client.get_timezone()

    @pytest.mark.asyncio
    async def test_session_initialization(self, client: AbstractClient) -> None:
        """Test session is initialized properly."""
        await client._ensure_session()
        assert client._session is not None

        await client.close()
        assert client._session is None
