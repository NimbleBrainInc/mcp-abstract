# MCP Server - Abstract

[![NimbleTools Registry](https://img.shields.io/badge/NimbleTools-Registry-green)](https://github.com/nimbletoolsinc/mcp-registry)
[![NimbleBrain Platform](https://img.shields.io/badge/NimbleBrain-Platform-blue)](https://www.nimblebrain.ai)
[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?logo=discord&logoColor=white)](https://www.nimblebrain.ai/discord?utm_source=github&utm_medium=readme&utm_campaign=mcp-abstract&utm_content=discord-badge)


[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/NimbleBrainInc/mcp-abstract/actions/workflows/ci.yaml/badge.svg)](https://github.com/NimbleBrainInc/mcp-abstract/actions)


## About

**MCP Server - Abstract** is a production-ready Model Context Protocol (MCP) server that provides seamless integration with [Abstract's](https://www.abstractapi.com/)'s comprehensive suite of data validation, enrichment, and intelligence services. Built with enterprise-grade architecture, this server enables AI assistants and agents to validate emails and phone numbers, enrich company data, perform IP geolocation, convert currencies, and much more—all through a type-safe, async-first interface.

## Features

- **Full API Coverage**: Complete implementation of 15+ Abstract API endpoints
- **Strongly Typed**: All responses use Pydantic models for type safety
- **HTTP Transport**: Supports streamable-http with health endpoint
- **Async/Await**: Built on aiohttp for high performance
- **Type Safe**: Full mypy strict mode compliance
- **Production Ready**: Docker support, comprehensive tests, linting
- **Developer Friendly**: Makefile commands, auto-formatting, fast feedback

## Supported APIs

### Data Validation
- **Email Validation** - Verify email deliverability, detect disposable emails
- **Phone Validation** - Validate phone numbers, identify carriers
- **VAT Validation** - Validate EU VAT numbers

### IP Intelligence
- **IP Geolocation** - Get location from IP address
- **IP Geolocation with Security** - Get location with VPN/proxy/datacenter detection
- **IP Info** - ISP, ASN, and connection details

### Time & Location
- **Timezone** - Get timezone from location or coordinates
- **Timezone Conversion** - Convert times between timezones
- **Holidays** - Get public holidays by country/year

### Financial
- **Exchange Rates** - Live currency exchange rates
- **Currency Conversion** - Convert amounts between currencies

### Web & Business
- **Company Enrichment** - Get company data from domain
- **Web Scraping** - Extract structured data from websites
- **Screenshots** - Generate website screenshots

## Installation

### Using uv (recommended)

```bash
# Install dependencies
uv pip install -e .

# Install with dev dependencies
uv pip install -e . --group dev
```

### Using pip

```bash
pip install -e .
```

## Configuration

**Important**: Abstract API uses **different API keys for different services**. You need to get a separate key for each service you want to use.

### Setup

1. Get your API keys from [Abstract API Dashboard](https://app.abstractapi.com/api)
   - Each service (Email, Phone, IP, etc.) has its own API key
   - You only need keys for the services you plan to use

2. Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your service-specific keys
```

3. Add your keys to `.env`:

```bash
# Example: If you only use IP geolocation and phone validation
ABSTRACT_IP_API_KEY=your_ip_key_here
ABSTRACT_PHONE_API_KEY=your_phone_key_here
```

Available service key names:
- `ABSTRACT_EMAIL_API_KEY` - Email validation
- `ABSTRACT_PHONE_API_KEY` - Phone validation
- `ABSTRACT_VAT_API_KEY` - VAT validation
- `ABSTRACT_IP_API_KEY` - IP geolocation (also used for VPN detection)
- `ABSTRACT_TIMEZONE_API_KEY` - Timezone services
- `ABSTRACT_HOLIDAYS_API_KEY` - Holiday lookup
- `ABSTRACT_EXCHANGE_API_KEY` - Currency exchange rates
- `ABSTRACT_COMPANY_API_KEY` - Company enrichment
- `ABSTRACT_SCRAPE_API_KEY` - Web scraping
- `ABSTRACT_SCREENSHOT_API_KEY` - Screenshot generation

**Note**: The `.env` file is automatically loaded when the server starts.

## Running the Server

### Stdio Mode (for Claude Desktop)

```bash
make run-stdio
# or
uv run fastmcp run src/mcp_abstract_api/server.py
```

### HTTP Mode

```bash
make run-http
# or
uv run uvicorn mcp_abstract_api.server:app --host 0.0.0.0 --port 8000

# Test the server is running
make test-http
```

### Docker

```bash
# Build image locally
make docker-build

# Build and push multi-platform image (amd64 + arm64)
make docker-buildx VERSION=1.0.0

# Run container
make docker-run
```

## Claude Desktop Configuration

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

### Option 1: HTTP Mode (Recommended)

First, start the HTTP server:
```bash
make run-http
```

Then add this to your Claude Desktop config:
```json
{
  "mcpServers": {
    "abstract-api": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8000/mcp"
      ]
    }
  }
}
```

**Benefits**: Better performance, easier debugging, can be deployed remotely

### Option 2: Stdio Mode

```json
{
  "mcpServers": {
    "abstract-api": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-abstract-api",
        "run",
        "fastmcp",
        "run",
        "src/mcp_abstract_api/server.py"
      ]
    }
  }
}
```

**Note**: With stdio mode, the `.env` file in the project directory will be automatically loaded. With HTTP mode, ensure the server is running in the correct directory or that environment variables are set.

## Available MCP Tools

### Email Validation
- `validate_email(email)` - Validate email and check deliverability

### Phone Validation
- `validate_phone(phone, country_code?)` - Validate phone number

### VAT Validation
- `validate_vat(vat_number)` - Validate EU VAT number

### IP Intelligence
- `geolocate_ip(ip_address, fields?)` - Get location from IP
- `get_ip_info(ip_address)` - Get detailed IP information
- `geolocate_ip_security(ip_address)` - Get IP location with security/threat analysis

### Time & Location
- `get_timezone(location?, latitude?, longitude?)` - Get timezone info
- `convert_timezone(base_location, base_datetime, target_location)` - Convert time
- `get_holidays(country, year, month?, day?)` - Get public holidays

### Financial
- `get_exchange_rates(base, target?)` - Get currency exchange rates
- `convert_currency(base, target, amount, date?)` - Convert currency

### Web & Business
- `get_company_info(domain)` - Get company data from domain
- `scrape_url(url, render_js?)` - Scrape web pages
- `generate_screenshot(url, width?, height?, full_page?)` - Screenshot websites

## Development

### Quick Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make dev-install   # Install with dev dependencies
make format        # Format code with ruff
make lint          # Lint code with ruff
make typecheck     # Type check with mypy
make test          # Run tests with pytest
make test-cov      # Run tests with coverage
make test-http     # Test HTTP server is running
make check         # Run all checks (lint + typecheck + test)
make clean         # Clean up artifacts
make all           # Full workflow (clean + install + format + check)
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file
uv run pytest tests/test_server.py -v
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Fix linting issues automatically
make lint-fix

# Type check
make typecheck

# Run all checks
make check
```

### Docker Commands

```bash
# Build local image
make docker-build

# Build and push multi-platform image
make docker-buildx VERSION=1.0.0

# Run container
make docker-run
```

**Multi-Platform Build Setup** (first time only):

```bash
# Create and use a new buildx builder
docker buildx create --name multiplatform --use

# Verify the builder
docker buildx inspect --bootstrap
```

The `docker-buildx` command builds for both `linux/amd64` and `linux/arm64` architectures and pushes directly to your container registry.

## Project Structure

```
.
├── src/
│   └── mcp_abstract_api/
│       ├── __init__.py
│       ├── server.py          # FastMCP server with tool definitions
│       ├── api_client.py      # Async API client class
│       └── api_models.py      # Pydantic models for type safety
├── tests/
│   ├── __init__.py
│   ├── test_server.py         # Server tool tests
│   └── test_api_client.py     # API client tests
├── pyproject.toml             # Project config with dependencies
├── Makefile                   # Development workflow commands
├── Dockerfile                 # Container deployment
├── pytest.ini                 # Pytest configuration
├── .gitignore                 # Comprehensive ignores
├── .python-version            # Python version (3.13)
└── README.md                  # This file
```

## Architecture

This project follows the **S-Tier MCP Server Architecture**:

- **Separation of Concerns**: API client, models, and server are separate
- **Type Safety First**: Strong typing with Pydantic and mypy strict mode
- **Async All the Way**: Async/await for all I/O operations
- **Error Handling**: Custom exceptions, context logging, graceful failures
- **Testability**: Mock-friendly design with dependency injection
- **Production Ready**: Docker, health checks, monitoring support

## Requirements

- Python 3.13+
- aiohttp
- fastapi
- fastmcp
- pydantic

## Health Check & Troubleshooting

The server exposes a health check endpoint at `/health`:

```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"mcp-abstract-api"}

# Or use the Makefile command
make test-http
```

### Troubleshooting HTTP Mode

If Claude Desktop can't connect to the server:

1. **Check server is running**: `make test-http`
2. **Verify port**: Ensure port 8000 is not in use by another service
3. **Check logs**: Look at the server output for any errors
4. **Test MCP endpoint**: `curl http://localhost:8000/` should return MCP protocol info
5. **Verify .env**: Ensure `ABSTRACT_API_KEY` is set in your `.env` file

### Changing the Port

To use a different port (e.g., 9000):

```bash
uv run uvicorn mcp_abstract_api.server:app --host 0.0.0.0 --port 9000
```

Then update your Claude Desktop config to use `http://localhost:9000/mcp`

## Error Handling

All API errors are wrapped in `AbstractAPIError` with:
- HTTP status code
- Error message
- Optional error details

Errors are logged via the MCP context for debugging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make check` to ensure quality
5. Submit a pull request



## Support

For issues, questions, or contributions, please open an issue on GitHub.

## License

MIT License - see LICENSE file for details

## Links

Part of the [NimbleTools Registry](https://github.com/nimbletoolsinc/mcp-registry) - an open source collection of production-ready MCP servers. For enterprise deployment, check out [NimbleBrain](https://www.nimblebrain.ai).

- [Abstract API Documentation](https://www.abstractapi.com/api)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Documentation](https://modelcontextprotocol.io)