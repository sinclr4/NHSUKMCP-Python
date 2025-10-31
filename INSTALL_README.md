# NHS Organizations MCP Server - Installation

Search NHS organizations by type and location using Claude Desktop or any MCP client.

## Installation

```bash
pip install nhs-organizations-mcp
```

## Configuration for Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nhs-organizations": {
      "command": "nhs-orgs-mcp",
      "env": {
        "AZURE_SEARCH_ENDPOINT": "https://your-search.search.windows.net",
        "AZURE_SEARCH_API_KEY": "your-api-key-here",
        "AZURE_SEARCH_POSTCODE_INDEX": "your-postcode-index",
        "AZURE_SEARCH_SERVICE_INDEX": "your-service-index"
      }
    }
  }
}
```

## Available Tools

1. **get_organisation_types** - List all NHS organisation types (Pharmacy, GP, Hospital, etc.)
2. **convert_postcode_to_coordinates** - Convert UK postcode to latitude/longitude
3. **search_organizations_by_postcode** - Find organizations near a postcode
4. **search_organizations_by_coordinates** - Find organizations near coordinates

## Example Usage in Claude

> "What types of NHS organizations can you search for?"

> "Find pharmacies near SW1A 1AA"

> "Show me hospitals within 2 miles of coordinates 51.5, -0.14"

## Development

```bash
# Clone and install locally
git clone https://github.com/yourusername/nhs-organizations-mcp
cd nhs-organizations-mcp
pip install -e .
```

## License

MIT
