"""Unit tests for the MCP server tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import Client

from mcp_abstract_api.api_models import (
    CompanyInfoResponse,
    EmailValidationResponse,
    IPGeolocationResponse,
    PhoneValidationResponse,
)
from mcp_abstract_api.server import mcp


@pytest.fixture
def mcp_server():
    """Return the MCP server instance."""
    return mcp


class TestMCPTools:
    """Test the MCP server tools."""

    @pytest.mark.asyncio
    async def test_validate_email(self, mcp_server) -> None:
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

            async with Client(mcp_server) as client:
                result = await client.call_tool("validate_email", {"email": "test@example.com"})

            assert result.data.email == "test@example.com"
            assert result.data.quality_score == 0.95
            mock_client.validate_email.assert_called_once_with("test@example.com")

    @pytest.mark.asyncio
    async def test_validate_phone(self, mcp_server) -> None:
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

            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "validate_phone", {"phone": "+1234567890", "country_code": "US"}
                )

            assert result.data.phone == "+1234567890"
            assert result.data.valid is True
            mock_client.validate_phone.assert_called_once_with("+1234567890", "US")

    @pytest.mark.asyncio
    async def test_geolocate_ip(self, mcp_server) -> None:
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

            async with Client(mcp_server) as client:
                result = await client.call_tool("geolocate_ip", {"ip_address": "8.8.8.8"})

            assert result.data.ip_address == "8.8.8.8"
            assert result.data.city == "Mountain View"
            mock_client.geolocate_ip.assert_called_once_with("8.8.8.8", None)

    @pytest.mark.asyncio
    async def test_get_company_info(self, mcp_server) -> None:
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

            async with Client(mcp_server) as client:
                result = await client.call_tool("get_company_info", {"domain": "example.com"})

            assert result.data.name == "Example Corp"
            assert result.data.domain == "example.com"
            mock_client.get_company_info.assert_called_once_with("example.com")


class TestToolsList:
    """Test tool registration."""

    @pytest.mark.asyncio
    async def test_tools_are_registered(self, mcp_server) -> None:
        """Test that all tools are properly registered."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "validate_email",
            "validate_phone",
            "validate_vat",
            "geolocate_ip",
            "get_ip_info",
            "geolocate_ip_security",
            "get_timezone",
            "convert_timezone",
            "get_holidays",
            "get_exchange_rates",
            "convert_currency",
            "get_company_info",
            "scrape_url",
            "generate_screenshot",
        ]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool {expected_tool} not found"


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
