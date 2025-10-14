"""Unit tests for the MCP server tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from mcp_abstract_api.api_models import (
    CompanyInfoResponse,
    EmailValidationResponse,
    IPGeolocationResponse,
    PhoneValidationResponse,
)
from mcp_abstract_api.server import (
    geolocate_ip,
    get_company_info,
    validate_email,
    validate_phone,
)


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock MCP context."""
    ctx = MagicMock(spec=Context)
    ctx.warning = AsyncMock()
    ctx.error = AsyncMock()
    return ctx


class TestMCPTools:
    """Test the MCP server tools."""

    @pytest.mark.asyncio
    async def test_validate_email(self, mock_context: MagicMock) -> None:
        """Test validate_email tool."""
        with patch("mcp_abstract_api.server.get_client", new_callable=AsyncMock) as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_client.validate_email.return_value = EmailValidationResponse(
                email="test@example.com",
                deliverability="DELIVERABLE",
                quality_score=0.95,
                is_valid_format={"value": True},
                is_free_email={"value": False},
                is_disposable_email={"value": False},
                is_role_email={"value": False},
                is_catchall_email={"value": False},
                is_mx_found={"value": True},
                is_smtp_valid={"value": True},
            )

            result = await validate_email("test@example.com", mock_context)

            assert result.email == "test@example.com"
            assert result.quality_score == 0.95
            mock_client.validate_email.assert_called_once_with("test@example.com")

    @pytest.mark.asyncio
    async def test_validate_phone(self, mock_context: MagicMock) -> None:
        """Test validate_phone tool."""
        with patch("mcp_abstract_api.server.get_client", new_callable=AsyncMock) as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_client.validate_phone.return_value = PhoneValidationResponse(
                phone="+1234567890",
                valid=True,
                format={"international": "+1 234-567-890"},
                country={"code": "US", "name": "United States"},
                type="mobile",
            )

            result = await validate_phone("+1234567890", mock_context, "US")

            assert result.phone == "+1234567890"
            assert result.valid is True
            mock_client.validate_phone.assert_called_once_with("+1234567890", "US")

    @pytest.mark.asyncio
    async def test_geolocate_ip(self, mock_context: MagicMock) -> None:
        """Test geolocate_ip tool."""
        with patch("mcp_abstract_api.server.get_client", new_callable=AsyncMock) as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_client.geolocate_ip.return_value = IPGeolocationResponse(
                ip_address="8.8.8.8",
                city="Mountain View",
                country="United States",
                country_code="US",
                latitude=37.386,
                longitude=-122.0838,
            )

            result = await geolocate_ip("8.8.8.8", mock_context)

            assert result.ip_address == "8.8.8.8"
            assert result.city == "Mountain View"
            mock_client.geolocate_ip.assert_called_once_with("8.8.8.8", None)

    @pytest.mark.asyncio
    async def test_get_company_info(self, mock_context: MagicMock) -> None:
        """Test get_company_info tool."""
        with patch("mcp_abstract_api.server.get_client", new_callable=AsyncMock) as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_client.get_company_info.return_value = CompanyInfoResponse(
                name="Example Corp",
                domain="example.com",
                year_founded=2020,
                industry="Technology",
                employees_count=100,
            )

            result = await get_company_info("example.com", mock_context)

            assert result.name == "Example Corp"
            assert result.domain == "example.com"
            mock_client.get_company_info.assert_called_once_with("example.com")


class TestHealthEndpoint:
    """Test health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self) -> None:
        """Test health check returns healthy status."""
        from mcp_abstract_api.server import health_check

        mock_request = MagicMock()
        response = await health_check(mock_request)

        assert response.status_code == 200
        assert "healthy" in response.body.decode()
