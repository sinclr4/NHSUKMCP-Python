# NHS Organizations MCP Server (Python)

A Model Context Protocol (MCP) server that provides tools for searching NHS organizations by type and location using Azure Cognitive Search.

## Features

- **Get Organization Types**: List all available NHS organization types
- **Convert Postcode**: Convert UK postcodes to latitude/longitude coordinates
- **Search by Postcode**: Find NHS organizations near a specific postcode
- **Search by Coordinates**: Find NHS organizations near specific coordinates

## Installation

### Local Development

```bash
cd NHSUKMCP-Python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Environment Variables

Set these environment variables:

```bash
export API_MANAGEMENT_ENDPOINT="https://nhsuksearchintuks.search.windows.net"
export API_MANAGEMENT_SUBSCRIPTION_KEY="your-api-key-here"
export AZURE_SEARCH_POSTCODE_INDEX="postcodesandplaces-1-0-b-int"
export AZURE_SEARCH_SERVICE_INDEX="service-search-internal-3-11"
```

## Usage

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

**macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nhs-organizations": {
      "command": "python",
      "args": ["-m", "nhs_orgs_mcp.server"],
      "cwd": "/Users/robsinclair/NHSUKMCP-Python",
      "env": {
        "API_MANAGEMENT_ENDPOINT": "https://nhsuksearchintuks.search.windows.net",
        "API_MANAGEMENT_SUBSCRIPTION_KEY": "your-api-key-here",
        "AZURE_SEARCH_POSTCODE_INDEX": "postcodesandplaces-1-0-b-int",
        "AZURE_SEARCH_SERVICE_INDEX": "service-search-internal-3-11"
      }
    }
  }
}
```

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nhs-organizations": {
      "command": "python",
      "args": ["-m", "nhs_orgs_mcp.server"],
      "cwd": "C:\\Users\\YourUsername\\NHSUKMCP-Python",
      "env": {
        "API_MANAGEMENT_ENDPOINT": "https://nhsuksearchintuks.search.windows.net",
        "API_MANAGEMENT_SUBSCRIPTION_KEY": "your-api-key-here",
        "AZURE_SEARCH_POSTCODE_INDEX": "postcodesandplaces-1-0-b-int",
        "AZURE_SEARCH_SERVICE_INDEX": "service-search-internal-3-11"
      }
    }
  }
}
```

### Run Standalone

```bash
# Activate virtual environment
source venv/bin/activate

# Run the server
python -m nhs_orgs_mcp.server
```

## Docker Deployment

### Build and Run Locally

```bash
# Build image
docker build -t nhsorgsmcp-python:latest .

# Run with environment variables
docker run -i \
  -e API_MANAGEMENT_ENDPOINT="https://nhsuksearchintuks.search.windows.net" \
  -e API_MANAGEMENT_SUBSCRIPTION_KEY="your-key" \
  -e AZURE_SEARCH_POSTCODE_INDEX="postcodesandplaces-1-0-b-int" \
  -e AZURE_SEARCH_SERVICE_INDEX="service-search-internal-3-11" \
  nhsorgsmcp-python:latest
```

### Deploy to Azure Container Apps

```bash
# Variables
RESOURCE_GROUP="rg-nhsorgsmcp"
ACR_NAME="nhsorgsmcpacr"
APP_NAME="nhs-orgs-mcp-python"

# Build and push to ACR
az acr login --name $ACR_NAME
docker tag nhsorgsmcp-python:latest $ACR_NAME.azurecr.io/nhsorgsmcp-python:latest
docker push $ACR_NAME.azurecr.io/nhsorgsmcp-python:latest

# Update or create container app
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_NAME.azurecr.io/nhsorgsmcp-python:latest \
  --set-env-vars \
    API_MANAGEMENT_ENDPOINT="https://nhsuksearchintuks.search.windows.net" \
    AZURE_SEARCH_POSTCODE_INDEX="postcodesandplaces-1-0-b-int" \
    AZURE_SEARCH_SERVICE_INDEX="service-search-internal-3-11" \
  --secrets API_MANAGEMENT_SUBSCRIPTION_KEY="your-api-key"
```

## Available MCP Tools

### 1. get_organization_types

Lists all NHS organization types with descriptions.

### 2. convert_postcode_to_coordinates

Converts a UK postcode to latitude/longitude.

**Parameters**:
- `postcode` (string): UK postcode (e.g., "SW1A 1AA")

### 3. search_organizations_by_postcode

Search NHS organizations by type near a postcode.

**Parameters**:
- `organizationType` (string): Organization type code (e.g., "PHA", "GPP")
- `postcode` (string): UK postcode
- `maxResults` (integer, optional): Maximum results (1-50, default: 10)

### 4. search_organizations_by_coordinates

Search NHS organizations by type near coordinates.

**Parameters**:
- `organizationType` (string): Organization type code
- `latitude` (number): Latitude
- `longitude` (number): Longitude  
- `maxResults` (integer, optional): Maximum results (1-50, default: 10)

## Project Structure

```
NHSUKMCP-Python/
├── nhs_orgs_mcp/
│   ├── __init__.py          # Package init
│   ├── server.py            # MCP server implementation
│   ├── models.py            # Data models
│   └── azure_search.py      # Azure Search service
├── pyproject.toml           # Project dependencies
├── Dockerfile               # Container build
└── README.md                # This file
```

## License

MIT

## Author

NHS Digital - rob.sinclair@nhschoices.net
