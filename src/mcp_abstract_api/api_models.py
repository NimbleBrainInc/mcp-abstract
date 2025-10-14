"""Pydantic models for Abstract API responses."""

from typing import Any

from pydantic import BaseModel, Field


# Email Validation Models
class EmailValidationResponse(BaseModel):
    """Response model for email validation endpoint."""

    email: str = Field(..., description="Email address that was validated")
    autocorrect: str | None = Field(None, description="Suggested correction if typo detected")
    deliverability: str = Field(..., description="Deliverability status")
    quality_score: float = Field(..., description="Quality score (0-1)")
    is_valid_format: dict[str, bool] = Field(..., description="Format validation results")
    is_free_email: dict[str, bool] = Field(..., description="Free email provider check")
    is_disposable_email: dict[str, bool] = Field(..., description="Disposable email check")
    is_role_email: dict[str, bool] = Field(..., description="Role-based email check")
    is_catchall_email: dict[str, bool] = Field(..., description="Catch-all domain check")
    is_mx_found: dict[str, bool] = Field(..., description="MX record check")
    is_smtp_valid: dict[str, bool] = Field(..., description="SMTP validation check")


# Phone Validation Models
class PhoneValidationResponse(BaseModel):
    """Response model for phone validation endpoint."""

    phone: str = Field(..., description="Phone number that was validated")
    valid: bool = Field(..., description="Whether phone number is valid")
    format: dict[str, str] = Field(..., description="Phone number formats")
    country: dict[str, str] = Field(..., description="Country information")
    location: str | None = Field(None, description="Location name")
    type: str | None = Field(None, description="Phone type (mobile, landline, etc)")
    carrier: str | None = Field(None, description="Carrier name")


# VAT Validation Models
class VATValidationResponse(BaseModel):
    """Response model for VAT validation endpoint."""

    vat_number: str = Field(..., description="VAT number that was validated")
    valid: bool = Field(..., description="Whether VAT number is valid")
    company: dict[str, str | None] = Field(..., description="Company information")
    country: dict[str, str] = Field(..., description="Country information")


# IP Geolocation Models
class IPGeolocationResponse(BaseModel):
    """Response model for IP geolocation endpoint."""

    ip_address: str = Field(..., description="IP address that was queried")
    city: str | None = Field(None, description="City name")
    city_geoname_id: int | None = Field(None, description="GeoNames city ID")
    region: str | None = Field(None, description="Region/state name")
    region_iso_code: str | None = Field(None, description="Region ISO code")
    region_geoname_id: int | None = Field(None, description="GeoNames region ID")
    postal_code: str | None = Field(None, description="Postal/ZIP code")
    country: str | None = Field(None, description="Country name")
    country_code: str | None = Field(None, description="ISO country code")
    country_geoname_id: int | None = Field(None, description="GeoNames country ID")
    country_is_eu: bool | None = Field(None, description="Whether country is in EU")
    continent: str | None = Field(None, description="Continent name")
    continent_code: str | None = Field(None, description="Continent code")
    continent_geoname_id: int | None = Field(None, description="GeoNames continent ID")
    longitude: float | None = Field(None, description="Longitude coordinate")
    latitude: float | None = Field(None, description="Latitude coordinate")
    security: dict[str, Any] | None = Field(None, description="Security information")
    timezone: dict[str, Any] | None = Field(None, description="Timezone information")
    flag: dict[str, str] | None = Field(None, description="Country flag information")
    currency: dict[str, str] | None = Field(None, description="Currency information")
    connection: dict[str, Any] | None = Field(None, description="ISP/connection information")


# Timezone Models
class TimezoneResponse(BaseModel):
    """Response model for timezone endpoint."""

    requested_location: str | None = Field(None, description="Location that was requested")
    latitude: float | None = Field(None, description="Latitude coordinate")
    longitude: float | None = Field(None, description="Longitude coordinate")
    timezone_name: str = Field(..., description="Timezone name (e.g., 'America/New_York')")
    timezone_abbreviation: str = Field(..., description="Timezone abbreviation")
    timezone_offset: int = Field(..., description="UTC offset in seconds")
    timezone_location: str | None = Field(None, description="Timezone location")
    datetime: str = Field(..., description="Current datetime in timezone")
    date: str = Field(..., description="Current date")
    time: str = Field(..., description="Current time")
    year: str = Field(..., description="Current year")
    month: str = Field(..., description="Current month")
    day: str = Field(..., description="Current day")
    hour: str = Field(..., description="Current hour")
    minute: str = Field(..., description="Current minute")
    second: str = Field(..., description="Current second")
    gmt_offset: int | None = Field(None, description="GMT offset")
    is_dst: bool | None = Field(None, description="Whether daylight saving time is active")


class TimezoneConversionResponse(BaseModel):
    """Response model for timezone conversion endpoint."""

    base_location: str = Field(..., description="Source location")
    base_timezone: dict[str, Any] = Field(..., description="Source timezone info")
    base_datetime: str = Field(..., description="Source datetime")
    target_location: str = Field(..., description="Target location")
    target_timezone: dict[str, Any] = Field(..., description="Target timezone info")
    target_datetime: str = Field(..., description="Converted datetime")


# Holidays Models
class Holiday(BaseModel):
    """Model for a single holiday."""

    name: str = Field(..., description="Holiday name")
    name_local: str | None = Field(None, description="Local language name")
    language: str | None = Field(None, description="Language code")
    description: str | None = Field(None, description="Holiday description")
    country: str = Field(..., description="Country code")
    location: str | None = Field(None, description="Specific location")
    type: str = Field(..., description="Holiday type")
    date: str = Field(..., description="Holiday date")
    date_year: str = Field(..., description="Year")
    date_month: str = Field(..., description="Month")
    date_day: str = Field(..., description="Day")
    week_day: str = Field(..., description="Day of week")


class HolidaysResponse(BaseModel):
    """Response model for holidays endpoint."""

    holidays: list[Holiday] = Field(default_factory=list, description="List of holidays")


# Exchange Rates Models
class ExchangeRatesResponse(BaseModel):
    """Response model for exchange rates endpoint."""

    base: str = Field(..., description="Base currency code")
    last_updated: int = Field(..., description="Last update timestamp")
    exchange_rates: dict[str, float] = Field(..., description="Exchange rates by currency")


class CurrencyConversionResponse(BaseModel):
    """Response model for currency conversion endpoint."""

    base: str = Field(..., description="Base currency code")
    target: str | None = Field(None, description="Target currency code")
    date: str | None = Field(None, description="Date for historical conversion")
    last_updated: int = Field(..., description="Last update timestamp")
    exchange_rates: dict[str, float] = Field(..., description="Exchange rates by currency")
    converted_amount: float | None = Field(None, description="Converted amount")
    amount: float | None = Field(None, description="Original amount")


# Company Enrichment Models
class CompanyInfoResponse(BaseModel):
    """Response model for company enrichment endpoint."""

    name: str | None = Field(None, description="Company name")
    domain: str = Field(..., description="Company domain")
    year_founded: int | None = Field(None, description="Year founded")
    industry: str | None = Field(None, description="Industry")
    employees_count: int | None = Field(None, description="Number of employees")
    locality: str | None = Field(None, description="City/locality")
    country: str | None = Field(None, description="Country")
    linkedin_url: str | None = Field(None, description="LinkedIn profile URL")
    logo_url: str | None = Field(None, description="Company logo URL")


# Web Scraping Models
class ScrapeResponse(BaseModel):
    """Response model for web scraping endpoint."""

    url: str = Field(..., description="URL that was scraped")
    content: str | None = Field(None, description="Extracted content")
    html: str | None = Field(None, description="Raw HTML")
    links: list[str] | None = Field(None, description="Extracted links")
    images: list[str] | None = Field(None, description="Extracted images")
    metadata: dict[str, Any] | None = Field(None, description="Page metadata")


# Screenshot Models
class ScreenshotResponse(BaseModel):
    """Response model for screenshot endpoint."""

    success: bool = Field(..., description="Whether screenshot was successful")
    url: str = Field(..., description="URL that was captured")
    image_data: str = Field(..., description="Image data (base64 or hex)")
    content_type: str | None = Field(None, description="Image content type")
    note: str | None = Field(None, description="Additional notes")


# Error Response Model
class ErrorResponse(BaseModel):
    """Error response model."""

    status: int | None = None
    error: dict[str, str] | str | None = None
    message: str | None = None
