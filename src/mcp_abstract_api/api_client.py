"""Async API client for Abstract API."""

import os
from typing import Any

import aiohttp
from aiohttp import ClientError

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


class AbstractAPIError(Exception):
    """Custom exception for Abstract API errors."""

    def __init__(self, status: int, message: str, details: dict[str, Any] | None = None) -> None:
        self.status = status
        self.message = message
        self.details = details
        super().__init__(f"Abstract API Error {status}: {message}")


class AbstractClient:
    """Async API client for Abstract API."""

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize the Abstract API client.

        Args:
            api_key: Abstract API key (or set ABSTRACT_API_KEY env var)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.environ.get("ABSTRACT_API_KEY")
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "AbstractClient":
        """Context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.close()

    async def _ensure_session(self) -> None:
        """Create session if it doesn't exist."""
        if not self._session:
            headers = {
                "User-Agent": "mcp-server-abstract-api/1.0",
                "Accept": "application/json",
            }

            self._session = aiohttp.ClientSession(
                headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def _request(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | bytes:
        """Make HTTP request with error handling.

        Args:
            url: Full URL to request
            params: Query parameters

        Returns:
            Parsed JSON response or raw bytes for binary content

        Raises:
            AbstractAPIError: If the API returns an error
        """
        await self._ensure_session()

        # Add API key to params
        if params is None:
            params = {}
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            if not self._session:
                raise RuntimeError("Session not initialized")

            async with self._session.get(url, params=params) as response:
                content_type = response.headers.get("Content-Type", "")

                # Handle binary content (images, etc.)
                if "image" in content_type or "application/octet-stream" in content_type:
                    return await response.read()

                # Handle JSON content
                if "application/json" in content_type:
                    result = await response.json()
                elif "text/plain" in content_type:
                    text = await response.text()
                    return {"result": text}
                else:
                    text = await response.text()
                    # Try to parse as JSON
                    if text.startswith("{") or text.startswith("["):
                        import json

                        try:
                            result = json.loads(text)
                        except json.JSONDecodeError:
                            result = {"result": text}
                    else:
                        result = {"result": text}

                # Check for errors
                if response.status >= 400:
                    error_msg = "Unknown error"
                    if isinstance(result, dict):
                        error_msg = (
                            result.get("error", {}).get("message")
                            if isinstance(result.get("error"), dict)
                            else result.get("message")
                            or result.get("title")
                            or str(result.get("error", error_msg))
                        )
                    raise AbstractAPIError(response.status, error_msg, result)

                return result  # type: ignore[no-any-return]

        except ClientError as e:
            raise AbstractAPIError(500, f"Network error: {str(e)}") from e

    # Email Validation
    async def validate_email(self, email: str) -> EmailValidationResponse:
        """Validate email address and check deliverability.

        Args:
            email: Email address to validate

        Returns:
            Email validation results
        """
        data = await self._request(
            "https://emailvalidation.abstractapi.com/v1/", params={"email": email}
        )
        return EmailValidationResponse(**data)  # type: ignore[arg-type]

    # Phone Validation
    async def validate_phone(
        self, phone: str, country_code: str | None = None
    ) -> PhoneValidationResponse:
        """Validate phone number and get carrier info.

        Args:
            phone: Phone number to validate
            country_code: ISO 3166-1 alpha-2 country code (optional)

        Returns:
            Phone validation results
        """
        params: dict[str, Any] = {"phone": phone}
        if country_code:
            params["country_code"] = country_code

        data = await self._request("https://phonevalidation.abstractapi.com/v1/", params=params)
        return PhoneValidationResponse(**data)  # type: ignore[arg-type]

    # VAT Validation
    async def validate_vat(self, vat_number: str) -> VATValidationResponse:
        """Validate EU VAT numbers.

        Args:
            vat_number: VAT number to validate (e.g., "SE556656688001")

        Returns:
            VAT validation results
        """
        data = await self._request(
            "https://vatapi.abstractapi.com/v1/", params={"vat_number": vat_number}
        )
        return VATValidationResponse(**data)  # type: ignore[arg-type]

    # IP Geolocation
    async def geolocate_ip(
        self, ip_address: str, fields: str | None = None
    ) -> IPGeolocationResponse:
        """Get location data from IP address.

        Args:
            ip_address: IP address to geolocate
            fields: Comma-separated fields to return (optional)

        Returns:
            IP geolocation information
        """
        params: dict[str, Any] = {"ip_address": ip_address}
        if fields:
            params["fields"] = fields

        data = await self._request("https://ipgeolocation.abstractapi.com/v1/", params=params)
        return IPGeolocationResponse(**data)  # type: ignore[arg-type]

    async def get_ip_info(self, ip_address: str) -> IPGeolocationResponse:
        """Get detailed IP information (ISP, ASN, etc.).

        Args:
            ip_address: IP address to query

        Returns:
            Complete IP information
        """
        return await self.geolocate_ip(ip_address)

    async def geolocate_ip_security(self, ip_address: str) -> IPGeolocationResponse:
        """Get IP geolocation with security/threat analysis.

        Analyzes IP address to determine if it's from a VPN, proxy server,
        tor exit node, or datacenter.

        Args:
            ip_address: IP address to analyze

        Returns:
            IP geolocation with security/threat information
        """
        return await self.geolocate_ip(ip_address, fields="security")

    # Timezone
    async def get_timezone(
        self,
        location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> TimezoneResponse:
        """Get timezone from location or coordinates.

        Args:
            location: Location name (e.g., "New York")
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Timezone information

        Raises:
            ValueError: If neither location nor coordinates provided
        """
        params: dict[str, Any] = {}

        if location:
            params["location"] = location
        elif latitude is not None and longitude is not None:
            params["latitude"] = latitude
            params["longitude"] = longitude
        else:
            raise ValueError("Either location or latitude/longitude must be provided")

        data = await self._request(
            "https://timezone.abstractapi.com/v1/current_time/", params=params
        )
        return TimezoneResponse(**data)  # type: ignore[arg-type]

    async def convert_timezone(
        self, base_location: str, base_datetime: str, target_location: str
    ) -> TimezoneConversionResponse:
        """Convert time between timezones.

        Args:
            base_location: Source location/timezone
            base_datetime: Datetime in ISO 8601 format
            target_location: Target location/timezone

        Returns:
            Timezone conversion results
        """
        data = await self._request(
            "https://timezone.abstractapi.com/v1/convert_time/",
            params={
                "base_location": base_location,
                "base_datetime": base_datetime,
                "target_location": target_location,
            },
        )
        return TimezoneConversionResponse(**data)  # type: ignore[arg-type]

    # Holidays
    async def get_holidays(
        self,
        country: str,
        year: int,
        month: int | None = None,
        day: int | None = None,
    ) -> HolidaysResponse:
        """Get public holidays for a country and year.

        Args:
            country: ISO 3166-1 alpha-2 country code (e.g., "US")
            year: Year (e.g., 2025)
            month: Month (1-12, optional)
            day: Day (1-31, optional)

        Returns:
            List of holidays
        """
        params: dict[str, Any] = {"country": country, "year": year}
        if month:
            params["month"] = month
        if day:
            params["day"] = day

        data = await self._request("https://holidays.abstractapi.com/v1/", params=params)
        # Handle both list and dict responses
        if isinstance(data, list):
            return HolidaysResponse(holidays=data)
        return HolidaysResponse(**data)  # type: ignore[arg-type]

    # Exchange Rates
    async def get_exchange_rates(
        self, base: str = "USD", target: str | None = None
    ) -> ExchangeRatesResponse:
        """Get current currency exchange rates.

        Args:
            base: Base currency code (e.g., "USD")
            target: Target currency code (optional, returns all if not specified)

        Returns:
            Exchange rates information
        """
        params: dict[str, Any] = {"base": base}
        if target:
            params["target"] = target

        data = await self._request("https://exchange-rates.abstractapi.com/v1/live/", params=params)
        return ExchangeRatesResponse(**data)  # type: ignore[arg-type]

    async def convert_currency(
        self, base: str, target: str, amount: float, date: str | None = None
    ) -> CurrencyConversionResponse:
        """Convert amount between currencies.

        Args:
            base: Base currency code (e.g., "USD")
            target: Target currency code (e.g., "EUR")
            amount: Amount to convert
            date: Historical date in YYYY-MM-DD format (optional)

        Returns:
            Currency conversion results
        """
        params: dict[str, Any] = {"base": base, "target": target}

        endpoint = "live" if not date else "historical"
        if date:
            params["date"] = date

        data = await self._request(
            f"https://exchange-rates.abstractapi.com/v1/{endpoint}/", params=params
        )

        # Calculate converted amount
        result_data = dict(data)  # type: ignore[arg-type]
        if "exchange_rates" in result_data and target in result_data["exchange_rates"]:
            rate = result_data["exchange_rates"][target]
            result_data["converted_amount"] = amount * rate
            result_data["amount"] = amount

        return CurrencyConversionResponse(**result_data)

    # Company Enrichment
    async def get_company_info(self, domain: str) -> CompanyInfoResponse:
        """Get company data from domain name.

        Args:
            domain: Company domain (e.g., "google.com")

        Returns:
            Company information
        """
        data = await self._request(
            "https://companyenrichment.abstractapi.com/v1/", params={"domain": domain}
        )
        return CompanyInfoResponse(**data)  # type: ignore[arg-type]

    # Web Scraping
    async def scrape_url(self, url: str, render_js: bool = False) -> ScrapeResponse:
        """Extract structured data from web pages.

        Args:
            url: URL to scrape
            render_js: Render JavaScript (default: false)

        Returns:
            Scraped content
        """
        # Use longer timeout for scraping
        original_timeout = self.timeout
        try:
            if self._session:
                self._session._timeout = aiohttp.ClientTimeout(total=60.0)

            data = await self._request(
                "https://scrape.abstractapi.com/v1/",
                params={"url": url, "render_js": str(render_js).lower()},
            )
            return ScrapeResponse(**data)  # type: ignore[arg-type]
        finally:
            if self._session:
                self._session._timeout = aiohttp.ClientTimeout(total=original_timeout)

    # Screenshot
    async def generate_screenshot(
        self,
        url: str,
        width: int = 1920,
        height: int = 1080,
        full_page: bool = False,
    ) -> ScreenshotResponse:
        """Generate website screenshot.

        Args:
            url: URL to screenshot
            width: Screenshot width in pixels (default: 1920)
            height: Screenshot height in pixels (default: 1080)
            full_page: Capture full page (default: false)

        Returns:
            Screenshot information with image data
        """
        # Use longer timeout for screenshots
        original_timeout = self.timeout
        try:
            if self._session:
                self._session._timeout = aiohttp.ClientTimeout(total=60.0)

            result = await self._request(
                "https://screenshot.abstractapi.com/v1/",
                params={
                    "url": url,
                    "width": width,
                    "height": height,
                    "full_page": str(full_page).lower(),
                },
            )

            # Handle binary image response
            if isinstance(result, bytes):
                return ScreenshotResponse(
                    success=True,
                    url=url,
                    image_data=result.hex()[:100] + "...",  # Preview only
                    content_type="image/png",
                    note="Full image data available in response",
                )

            return ScreenshotResponse(**result)
        finally:
            if self._session:
                self._session._timeout = aiohttp.ClientTimeout(total=original_timeout)
