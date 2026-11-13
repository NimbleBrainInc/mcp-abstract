"""FastMCP server for Abstract API with comprehensive tooling."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from starlette.requests import Request
from starlette.responses import JSONResponse

from .api_client import AbstractAPIError, AbstractClient
from .api_models import (
    CompanyInfoResponse,
    CurrencyConversionResponse,
    EmailValidationResponse,
    ExchangeRatesResponse,
    HolidaysResponse,
    IPGeolocationResponse,
    PhoneValidationResponse,
    ScrapeResponse,
    ScreenshotResponse,
    TimezoneConversionResponse,
    TimezoneResponse,
    VATValidationResponse,
)

# Load environment variables from .env file
# Look for .env in the project root (2 levels up from this file)
_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

# Logging setup - all logs to stderr (stdout is reserved for JSON-RPC). Diagnostics go
# here, never to the client: MCP's logging capability is deprecated as of the 2026-07-28
# protocol (SEP-2577). A failure the caller must see is raised as a ToolError.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp_abstract_api")

# Create MCP server
mcp = FastMCP("AbstractAPI")

# Cache for service-specific clients
_clients: dict[str, AbstractClient] = {}


def _get_api_key_for_service(service: str) -> str | None:
    """Get the appropriate API key for a specific service.

    Args:
        service: Service name (e.g., "email", "phone", "ip")

    Returns:
        API key for the service, or None if not configured
    """
    # Only use service-specific keys (Abstract API requires different keys per service)
    return os.environ.get(f"ABSTRACT_{service.upper()}_API_KEY")


async def get_client(service: str = "general") -> AbstractClient:
    """Get or create the API client instance for a specific service.

    Args:
        service: Service name (e.g., "email", "phone", "ip")

    Returns:
        AbstractClient instance configured for the service

    Raises:
        ToolError: when neither the service's key nor ABSTRACT_API_KEY is set, so the
            caller sees why the tool failed.
    """
    global _clients

    if service not in _clients:
        api_key = _get_api_key_for_service(service)
        if not api_key and not os.environ.get("ABSTRACT_API_KEY"):
            key_var = f"ABSTRACT_{service.upper()}_API_KEY"
            logger.error("No API key for the %s service (%s)", service, key_var)
            raise ToolError(f"Set {key_var} or ABSTRACT_API_KEY to use the {service} service")
        _clients[service] = AbstractClient(api_key=api_key)

    return _clients[service]


# Health endpoint for HTTP transport
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring.

    Args:
        request: FastAPI request object

    Returns:
        JSON response with health status
    """
    return JSONResponse({"status": "healthy", "service": "mcp-abstract-api"})


# Email Validation Tools
@mcp.tool()
async def validate_email(email: str) -> EmailValidationResponse:
    """Validate email address and check deliverability.

    Checks email format, domain validity, MX records, SMTP validation,
    and detects disposable/role-based emails.

    Args:
        email: Email address to validate

    Returns:
        Complete email validation results including deliverability score
    """
    client = await get_client(service="email")
    try:
        return await client.validate_email(email)
    except AbstractAPIError as e:
        logger.warning("validate_email failed: %s", e)
        raise ToolError(str(e)) from e


# Phone Validation Tools
@mcp.tool()
async def validate_phone(phone: str, country_code: str | None = None) -> PhoneValidationResponse:
    """Validate phone number and get carrier info.

    Validates phone format, identifies carrier, determines phone type
    (mobile/landline), and provides location information.

    Args:
        phone: Phone number to validate
        country_code: ISO 3166-1 alpha-2 country code (optional)

    Returns:
        Phone validation results with carrier and location info
    """
    client = await get_client(service="phone")
    try:
        return await client.validate_phone(phone, country_code)
    except AbstractAPIError as e:
        logger.warning("validate_phone failed: %s", e)
        raise ToolError(str(e)) from e


# VAT Validation Tools
@mcp.tool()
async def validate_vat(vat_number: str) -> VATValidationResponse:
    """Validate EU VAT numbers.

    Checks VAT number validity and returns associated company information.

    Args:
        vat_number: VAT number to validate (e.g., "SE556656688001")

    Returns:
        VAT validation results with company details
    """
    client = await get_client(service="vat")
    try:
        return await client.validate_vat(vat_number)
    except AbstractAPIError as e:
        logger.warning("validate_vat failed: %s", e)
        raise ToolError(str(e)) from e


# IP Geolocation Tools
@mcp.tool()
async def geolocate_ip(ip_address: str, fields: str | None = None) -> IPGeolocationResponse:
    """Get location data from IP address.

    Returns comprehensive geolocation data including city, region, country,
    coordinates, timezone, currency, and ISP information.

    Args:
        ip_address: IP address to geolocate
        fields: Comma-separated fields to return (e.g., "city,country,timezone")

    Returns:
        Complete IP geolocation information
    """
    client = await get_client(service="ip")
    try:
        return await client.geolocate_ip(ip_address, fields)
    except AbstractAPIError as e:
        logger.warning("geolocate_ip failed: %s", e)
        raise ToolError(str(e)) from e


@mcp.tool()
async def get_ip_info(ip_address: str) -> IPGeolocationResponse:
    """Get detailed IP information (ISP, ASN, connection details).

    Provides complete IP information including ISP, autonomous system number,
    connection type, and network details.

    Args:
        ip_address: IP address to query

    Returns:
        Detailed IP information
    """
    client = await get_client(service="ip")
    try:
        return await client.get_ip_info(ip_address)
    except AbstractAPIError as e:
        logger.warning("get_ip_info failed: %s", e)
        raise ToolError(str(e)) from e


@mcp.tool()
async def geolocate_ip_security(ip_address: str) -> IPGeolocationResponse:
    """Get IP geolocation with security/threat analysis.

    Analyzes IP address to determine if it's from a VPN, proxy server,
    tor exit node, or datacenter. Returns full geolocation data along with
    security information.

    Args:
        ip_address: IP address to analyze

    Returns:
        IP geolocation with security/threat information
    """
    client = await get_client(service="ip")
    try:
        return await client.geolocate_ip_security(ip_address)
    except AbstractAPIError as e:
        logger.warning("geolocate_ip_security failed: %s", e)
        raise ToolError(str(e)) from e


# Timezone Tools
@mcp.tool()
async def get_timezone(
    location: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> TimezoneResponse:
    """Get timezone from location or coordinates.

    Returns current time and timezone information for a location or coordinate pair.
    Either location OR latitude/longitude must be provided.

    Args:
        location: Location name (e.g., "New York")
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        Timezone and current time information
    """
    client = await get_client(service="timezone")
    try:
        return await client.get_timezone(location, latitude, longitude)
    except (AbstractAPIError, ValueError) as e:
        logger.warning("get_timezone failed: %s", e)
        raise ToolError(str(e)) from e


@mcp.tool()
async def convert_timezone(
    base_location: str,
    base_datetime: str,
    target_location: str,
) -> TimezoneConversionResponse:
    """Convert time between timezones.

    Converts a datetime from one timezone to another, handling daylight
    saving time automatically.

    Args:
        base_location: Source location/timezone
        base_datetime: Datetime in ISO 8601 format
        target_location: Target location/timezone

    Returns:
        Timezone conversion results with converted datetime
    """
    client = await get_client(service="timezone")
    try:
        return await client.convert_timezone(base_location, base_datetime, target_location)
    except AbstractAPIError as e:
        logger.warning("convert_timezone failed: %s", e)
        raise ToolError(str(e)) from e


# Holidays Tools
@mcp.tool()
async def get_holidays(
    country: str,
    year: int,
    month: int | None = None,
    day: int | None = None,
) -> HolidaysResponse:
    """Get public holidays for a country and year.

    Returns list of public holidays with names, dates, types, and descriptions.
    Can be filtered by month and/or day.

    Args:
        country: ISO 3166-1 alpha-2 country code (e.g., "US")
        year: Year (e.g., 2025)
        month: Month (1-12, optional)
        day: Day (1-31, optional)

    Returns:
        List of holidays matching the criteria
    """
    client = await get_client(service="holidays")
    try:
        return await client.get_holidays(country, year, month, day)
    except AbstractAPIError as e:
        logger.warning("get_holidays failed: %s", e)
        raise ToolError(str(e)) from e


# Exchange Rates Tools
@mcp.tool()
async def get_exchange_rates(base: str = "USD", target: str | None = None) -> ExchangeRatesResponse:
    """Get current currency exchange rates.

    Returns live exchange rates for a base currency. If target is specified,
    returns only that rate; otherwise returns all available rates.

    Args:
        base: Base currency code (e.g., "USD")
        target: Target currency code (optional, returns all if not specified)

    Returns:
        Current exchange rates
    """
    client = await get_client(service="exchange")
    try:
        return await client.get_exchange_rates(base, target)
    except AbstractAPIError as e:
        logger.warning("get_exchange_rates failed: %s", e)
        raise ToolError(str(e)) from e


@mcp.tool()
async def convert_currency(
    base: str,
    target: str,
    amount: float,
    date: str | None = None,
) -> CurrencyConversionResponse:
    """Convert amount between currencies.

    Converts an amount from one currency to another using live or historical
    exchange rates. Includes the calculated converted amount.

    Args:
        base: Base currency code (e.g., "USD")
        target: Target currency code (e.g., "EUR")
        amount: Amount to convert
        date: Historical date in YYYY-MM-DD format (optional)

    Returns:
        Currency conversion results with converted amount
    """
    client = await get_client(service="exchange")
    try:
        return await client.convert_currency(base, target, amount, date)
    except AbstractAPIError as e:
        logger.warning("convert_currency failed: %s", e)
        raise ToolError(str(e)) from e


# Company Enrichment Tools
@mcp.tool()
async def get_company_info(domain: str) -> CompanyInfoResponse:
    """Get company data from domain name.

    Returns comprehensive company information including name, industry,
    employee count, founding year, and social media profiles.

    Args:
        domain: Company domain (e.g., "google.com")

    Returns:
        Complete company information
    """
    client = await get_client(service="company")
    try:
        return await client.get_company_info(domain)
    except AbstractAPIError as e:
        logger.warning("get_company_info failed: %s", e)
        raise ToolError(str(e)) from e


# Web Scraping Tools
@mcp.tool()
async def scrape_url(url: str, render_js: bool = False) -> ScrapeResponse:
    """Extract structured data from web pages.

    Scrapes web pages and extracts content, links, images, and metadata.
    Can optionally render JavaScript for dynamic sites.

    Args:
        url: URL to scrape
        render_js: Render JavaScript (default: false)

    Returns:
        Scraped content and extracted data
    """
    client = await get_client(service="scrape")
    try:
        return await client.scrape_url(url, render_js)
    except AbstractAPIError as e:
        logger.warning("scrape_url failed: %s", e)
        raise ToolError(str(e)) from e


# Screenshot Tools
@mcp.tool()
async def generate_screenshot(
    url: str,
    width: int = 1920,
    height: int = 1080,
    full_page: bool = False,
) -> ScreenshotResponse:
    """Generate website screenshot.

    Captures a screenshot of a website at specified dimensions. Can capture
    full page or viewport only.

    Args:
        url: URL to screenshot
        width: Screenshot width in pixels (default: 1920)
        height: Screenshot height in pixels (default: 1080)
        full_page: Capture full page (default: false)

    Returns:
        Screenshot information with image data
    """
    client = await get_client(service="screenshot")
    try:
        return await client.generate_screenshot(url, width, height, full_page)
    except AbstractAPIError as e:
        logger.warning("generate_screenshot failed: %s", e)
        raise ToolError(str(e)) from e


# Create ASGI application for deployment
app = mcp.http_app()


if __name__ == "__main__":
    mcp.run()
