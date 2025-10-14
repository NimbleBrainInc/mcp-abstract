"""FastMCP server for Abstract API with comprehensive tooling."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import Context, FastMCP

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


async def get_client(ctx: Context[Any, Any, Any], service: str = "general") -> AbstractClient:
    """Get or create the API client instance for a specific service.

    Args:
        ctx: MCP context
        service: Service name (e.g., "email", "phone", "ip")

    Returns:
        AbstractClient instance configured for the service
    """
    global _clients

    if service not in _clients:
        api_key = _get_api_key_for_service(service)
        if not api_key:
            await ctx.warning(
                f"No API key configured for {service} service. "
                f"Set ABSTRACT_{service.upper()}_API_KEY or ABSTRACT_API_KEY in your .env file"
            )
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
async def validate_email(email: str, ctx: Context[Any, Any, Any]) -> EmailValidationResponse:
    """Validate email address and check deliverability.

    Checks email format, domain validity, MX records, SMTP validation,
    and detects disposable/role-based emails.

    Args:
        email: Email address to validate
        ctx: MCP context

    Returns:
        Complete email validation results including deliverability score
    """
    client = await get_client(ctx, service="email")
    try:
        return await client.validate_email(email)
    except AbstractAPIError as e:
        await ctx.error(f"Email validation error: {e.message}")
        raise


# Phone Validation Tools
@mcp.tool()
async def validate_phone(
    phone: str, ctx: Context[Any, Any, Any], country_code: str | None = None
) -> PhoneValidationResponse:
    """Validate phone number and get carrier info.

    Validates phone format, identifies carrier, determines phone type
    (mobile/landline), and provides location information.

    Args:
        phone: Phone number to validate
        country_code: ISO 3166-1 alpha-2 country code (optional)
        ctx: MCP context

    Returns:
        Phone validation results with carrier and location info
    """
    if ctx is None:
        raise ValueError("Context is required")
    client = await get_client(ctx, service="phone")
    try:
        return await client.validate_phone(phone, country_code)
    except AbstractAPIError as e:
        await ctx.error(f"Phone validation error: {e.message}")
        raise


# VAT Validation Tools
@mcp.tool()
async def validate_vat(vat_number: str, ctx: Context[Any, Any, Any]) -> VATValidationResponse:
    """Validate EU VAT numbers.

    Checks VAT number validity and returns associated company information.

    Args:
        vat_number: VAT number to validate (e.g., "SE556656688001")
        ctx: MCP context

    Returns:
        VAT validation results with company details
    """
    client = await get_client(ctx, service="vat")
    try:
        return await client.validate_vat(vat_number)
    except AbstractAPIError as e:
        await ctx.error(f"VAT validation error: {e.message}")
        raise


# IP Geolocation Tools
@mcp.tool()
async def geolocate_ip(
    ip_address: str, ctx: Context[Any, Any, Any], fields: str | None = None
) -> IPGeolocationResponse:
    """Get location data from IP address.

    Returns comprehensive geolocation data including city, region, country,
    coordinates, timezone, currency, and ISP information.

    Args:
        ip_address: IP address to geolocate
        fields: Comma-separated fields to return (e.g., "city,country,timezone")
        ctx: MCP context

    Returns:
        Complete IP geolocation information
    """
    if ctx is None:
        raise ValueError("Context is required")
    client = await get_client(ctx, service="ip")
    try:
        return await client.geolocate_ip(ip_address, fields)
    except AbstractAPIError as e:
        await ctx.error(f"IP geolocation error: {e.message}")
        raise


@mcp.tool()
async def get_ip_info(ip_address: str, ctx: Context[Any, Any, Any]) -> IPGeolocationResponse:
    """Get detailed IP information (ISP, ASN, connection details).

    Provides complete IP information including ISP, autonomous system number,
    connection type, and network details.

    Args:
        ip_address: IP address to query
        ctx: MCP context

    Returns:
        Detailed IP information
    """
    client = await get_client(ctx, service="ip")
    try:
        return await client.get_ip_info(ip_address)
    except AbstractAPIError as e:
        await ctx.error(f"IP info error: {e.message}")
        raise


@mcp.tool()
async def geolocate_ip_security(ip_address: str, ctx: Context[Any, Any, Any]) -> IPGeolocationResponse:
    """Get IP geolocation with security/threat analysis.

    Analyzes IP address to determine if it's from a VPN, proxy server,
    tor exit node, or datacenter. Returns full geolocation data along with
    security information.

    Args:
        ip_address: IP address to analyze
        ctx: MCP context

    Returns:
        IP geolocation with security/threat information
    """
    client = await get_client(ctx, service="ip")
    try:
        return await client.geolocate_ip_security(ip_address)
    except AbstractAPIError as e:
        await ctx.error(f"IP geolocation security error: {e.message}")
        raise


# Timezone Tools
@mcp.tool()
async def get_timezone(
    ctx: Context[Any, Any, Any],
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
        ctx: MCP context

    Returns:
        Timezone and current time information
    """
    if ctx is None:
        raise ValueError("Context is required")
    client = await get_client(ctx, service="timezone")
    try:
        return await client.get_timezone(location, latitude, longitude)
    except (AbstractAPIError, ValueError) as e:
        await ctx.error(f"Timezone error: {str(e)}")
        raise


@mcp.tool()
async def convert_timezone(
    base_location: str,
    base_datetime: str,
    target_location: str,
    ctx: Context[Any, Any, Any],
) -> TimezoneConversionResponse:
    """Convert time between timezones.

    Converts a datetime from one timezone to another, handling daylight
    saving time automatically.

    Args:
        base_location: Source location/timezone
        base_datetime: Datetime in ISO 8601 format
        target_location: Target location/timezone
        ctx: MCP context

    Returns:
        Timezone conversion results with converted datetime
    """
    client = await get_client(ctx, service="timezone")
    try:
        return await client.convert_timezone(base_location, base_datetime, target_location)
    except AbstractAPIError as e:
        await ctx.error(f"Timezone conversion error: {e.message}")
        raise


# Holidays Tools
@mcp.tool()
async def get_holidays(
    country: str,
    year: int,
    ctx: Context[Any, Any, Any],
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
        ctx: MCP context

    Returns:
        List of holidays matching the criteria
    """
    if ctx is None:
        raise ValueError("Context is required")
    client = await get_client(ctx, service="holidays")
    try:
        return await client.get_holidays(country, year, month, day)
    except AbstractAPIError as e:
        await ctx.error(f"Holidays error: {e.message}")
        raise


# Exchange Rates Tools
@mcp.tool()
async def get_exchange_rates(
    ctx: Context[Any, Any, Any], base: str = "USD", target: str | None = None
) -> ExchangeRatesResponse:
    """Get current currency exchange rates.

    Returns live exchange rates for a base currency. If target is specified,
    returns only that rate; otherwise returns all available rates.

    Args:
        base: Base currency code (e.g., "USD")
        target: Target currency code (optional, returns all if not specified)
        ctx: MCP context

    Returns:
        Current exchange rates
    """
    if ctx is None:
        raise ValueError("Context is required")
    client = await get_client(ctx, service="exchange")
    try:
        return await client.get_exchange_rates(base, target)
    except AbstractAPIError as e:
        await ctx.error(f"Exchange rates error: {e.message}")
        raise


@mcp.tool()
async def convert_currency(
    base: str,
    target: str,
    amount: float,
    ctx: Context[Any, Any, Any],
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
        ctx: MCP context

    Returns:
        Currency conversion results with converted amount
    """
    if ctx is None:
        raise ValueError("Context is required")
    client = await get_client(ctx, service="exchange")
    try:
        return await client.convert_currency(base, target, amount, date)
    except AbstractAPIError as e:
        await ctx.error(f"Currency conversion error: {e.message}")
        raise


# Company Enrichment Tools
@mcp.tool()
async def get_company_info(domain: str, ctx: Context[Any, Any, Any]) -> CompanyInfoResponse:
    """Get company data from domain name.

    Returns comprehensive company information including name, industry,
    employee count, founding year, and social media profiles.

    Args:
        domain: Company domain (e.g., "google.com")
        ctx: MCP context

    Returns:
        Complete company information
    """
    client = await get_client(ctx, service="company")
    try:
        return await client.get_company_info(domain)
    except AbstractAPIError as e:
        await ctx.error(f"Company info error: {e.message}")
        raise


# Web Scraping Tools
@mcp.tool()
async def scrape_url(
    url: str, ctx: Context[Any, Any, Any], render_js: bool = False
) -> ScrapeResponse:
    """Extract structured data from web pages.

    Scrapes web pages and extracts content, links, images, and metadata.
    Can optionally render JavaScript for dynamic sites.

    Args:
        url: URL to scrape
        render_js: Render JavaScript (default: false)
        ctx: MCP context

    Returns:
        Scraped content and extracted data
    """
    if ctx is None:
        raise ValueError("Context is required")
    client = await get_client(ctx, service="scrape")
    try:
        return await client.scrape_url(url, render_js)
    except AbstractAPIError as e:
        await ctx.error(f"Scraping error: {e.message}")
        raise


# Screenshot Tools
@mcp.tool()
async def generate_screenshot(
    url: str,
    ctx: Context[Any, Any, Any],
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
        ctx: MCP context

    Returns:
        Screenshot information with image data
    """
    if ctx is None:
        raise ValueError("Context is required")
    client = await get_client(ctx, service="screenshot")
    try:
        return await client.generate_screenshot(url, width, height, full_page)
    except AbstractAPIError as e:
        await ctx.error(f"Screenshot error: {e.message}")
        raise


# Create ASGI application for uvicorn
app = mcp.streamable_http_app()


# Shutdown handler to clean up client sessions
# Note: Using on_event (deprecated) because FastMCP creates the app for us
# and lifespan context managers must be set during app creation
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Clean up all client sessions on shutdown."""
    global _clients
    for client in _clients.values():
        await client.close()
    _clients.clear()


if __name__ == "__main__":
    mcp.run()
