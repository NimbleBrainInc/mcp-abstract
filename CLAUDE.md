# Abstract MCP Server

Multi-service API wrapper requiring separate API keys per service.

## API Keys

Abstract API uses DIFFERENT keys for each service. Get keys from https://app.abstractapi.com/api

| Service | Config Key | Env Var |
|---------|------------|---------|
| Email Validation | email_api_key | ABSTRACT_EMAIL_API_KEY |
| Phone Validation | phone_api_key | ABSTRACT_PHONE_API_KEY |
| VAT Validation | vat_api_key | ABSTRACT_VAT_API_KEY |
| IP Geolocation | ip_api_key | ABSTRACT_IP_API_KEY |
| Timezone | timezone_api_key | ABSTRACT_TIMEZONE_API_KEY |
| Holidays | holidays_api_key | ABSTRACT_HOLIDAYS_API_KEY |
| Exchange Rates | exchange_api_key | ABSTRACT_EXCHANGE_API_KEY |
| Company Enrichment | company_api_key | ABSTRACT_COMPANY_API_KEY |
| Web Scraping | scrape_api_key | ABSTRACT_SCRAPE_API_KEY |
| Screenshot | screenshot_api_key | ABSTRACT_SCREENSHOT_API_KEY |

Configure only the services you need:
```bash
mpak config set @nimblebraininc/abstract email_api_key=xxx ip_api_key=yyy
```

## Testing

```bash
mpak bundle run @nimblebraininc/abstract --update
```

## Debugging 401 Errors

"Invalid API key" means a key IS being sent but it's wrong. Verify you're using the correct service-specific key from Abstract's dashboard.
