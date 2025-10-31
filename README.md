# NHSUK MCP Server

A Model Context Protocol (MCP) server that provides tools for searching NHS organisations by type and location, plus accessing NHS health information using Azure API Management.

## Features

- **Get Organisation Types**: List all 24 available NHS organisation types
- **Convert Postcode**: Convert UK postcodes to latitude/longitude coordinates
- **Search by Postcode**: Find NHS organisations near a specific postcode
- **Search by Coordinates**: Find NHS organisations near specific coordinates
- **Get Health Topic**: Get detailed NHS health information and guidance on medical conditions

## Installation

### From PyPI (Recommended)

```bash
pip install nhsuk-mcp
```

### From Source

```bash
git clone https://github.com/sinclr4/nhsuk-mcp-python.git
cd nhsuk-mcp-python
pip install -e .
```

## Configuration

### Environment Variables

This server requires two environment variables:

- `API_MANAGEMENT_ENDPOINT` - The Azure API Management base URL (without service paths)
- `API_MANAGEMENT_SUBSCRIPTION_KEY` - Your subscription key for API Management

## Usage with Claude Desktop

### Installation

```bash
pip install nhsuk-mcp
```

### Configuration

Add to your Claude Desktop config file:

**macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nhsuk": {
      "command": "python",
      "args": ["-m", "nhsuk_mcp.server"],
      "env": {
        "API_MANAGEMENT_ENDPOINT": "https://nhsuk-apim-int-uks.azure-api.net",
        "API_MANAGEMENT_SUBSCRIPTION_KEY": "your-subscription-key-here"
      }
    }
  }
}
```

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nhsuk": {
      "command": "python",
      "args": ["-m", "nhsuk_mcp.server"],
      "env": {
        "API_MANAGEMENT_ENDPOINT": "https://nhsuk-apim-int-uks.azure-api.net",  
        "API_MANAGEMENT_SUBSCRIPTION_KEY": "your-subscription-key-here"
      }
    }
  }
}
```

### Restart Claude Desktop

After updating the configuration, restart Claude Desktop. The MCP server will be available with 5 tools.

## Available MCP Tools

### 1. get_organisation_types

Lists all NHS organisation types with descriptions.

**Returns**: Dictionary of organisation type codes and their descriptions.

**Example types**:
- `PHA` - Pharmacy
- `GPP` - GP Practice
- `HOS` - Hospital
- `DEN` - Dentists
- `CLI` - Clinics

### 2. convert_postcode_to_coordinates

Converts a UK postcode to latitude/longitude coordinates.

**Parameters**:
- `postcode` (string, required): UK postcode (e.g., "SW1A 1AA")

**Returns**: Latitude and longitude coordinates

### 3. search_organisations_by_postcode

Search for NHS organisations near a specific postcode.

**Parameters**:
- `organisationType` (string, required): Organisation type code (e.g., "PHA", "GPP", "HOS")
- `postcode` (string, required): UK postcode
- `maxResults` (integer, optional): Maximum number of results (1-50, default: 10)

**Returns**: List of organisations with name, address, postcode, distance, and coordinates

### 4. search_organisations_by_coordinates

Search for NHS organisations near specific coordinates.

**Parameters**:
- `organisationType` (string, required): Organisation type code
- `latitude` (number, required): Latitude coordinate
- `longitude` (number, required): Longitude coordinate
- `maxResults` (integer, optional): Maximum number of results (1-50, default: 10)

**Returns**: List of organisations with name, address, postcode, distance, and coordinates

### 5. get_health_topic

Get detailed information about a specific health condition or topic from the NHS API.

**Parameters**:
- `topic` (string, required): The health topic or condition slug (e.g., "asthma", "diabetes", "flu", "covid-19")

**Returns**: Comprehensive information including name, description, last reviewed date, URL, and content sections

**Example topics**: asthma, diabetes, flu, covid-19, heart-disease, stroke, cancer, depression, anxiety


## Supported Organisation Types

The server supports 24 NHS organisation types:

| Code | Description |
|------|-------------|
| CCG  | Clinical Commissioning Group |
| CLI  | Clinics |
| DEN  | Dentists |
| GDOS | Generic Directory of Services |
| GPB  | GP |
| GPP  | GP Practice |
| GSD  | Generic Service Directory |
| HA   | Health Authority |
| HOS  | Hospital |
| HWB  | Health and Wellbeing Board |
| LA   | Local Authority |
| LAT  | Area Team |
| MIU  | Minor Injury Unit |
| OPT  | Optician |
| PHA  | Pharmacy |
| RAT  | Regional Area Team |
| SCL  | Social Care Provider Location |
| SCP  | Social Care Provider |
| SHA  | Strategic Health Authority |
| STP  | Sustainability and Transformation Partnership |
| TRU  | Trust |
| UC   | Urgent Care |
| UNK  | UNKNOWN |

## Docker Deployment

### Build Image

```bash
docker build -t nhs-orgs-mcp-python .
```

### Run Container

```bash
docker run -i \
  -e API_MANAGEMENT_ENDPOINT="https://nhsuk-apim-int-uks.azure-api.net" \
  -e API_MANAGEMENT_SUBSCRIPTION_KEY="your-key" \
  nhs-orgs-mcp-python
```

## Example Usage

Once configured in Claude Desktop, you can ask questions like:

- "What NHS organisation types are available?"
- "Find pharmacies near postcode SW1A 1AA"
- "Show me GP practices within 5 miles of London"
- "What's the nearest hospital to coordinates 51.5074, -0.1278?"
- "Convert postcode M1 1AE to coordinates"

- "Get information about asthma"
- "Tell me about diabetes symptoms and treatment"
- "What is the NHS guidance on flu?"
## Development

### Local Setup

```bash
# Clone repository
git clone https://github.com/sinclr4/nhsuk-mcp-python.git
cd nhsuk-mcp-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Set environment variables
export API_MANAGEMENT_ENDPOINT="https://nhsuk-apim-int-uks.azure-api.net"
export API_MANAGEMENT_SUBSCRIPTION_KEY="your-key"

# Run the server
python -m nhsuk_mcp.server
```

### Project Structure

```
nhsuk-mcp-python/
├── nhsuk_mcp/
│   ├── __init__.py          # Package initialization
│   ├── server.py            # MCP server implementation
│   ├── models.py            # Data models (Organisation, PostcodeResult)
│   └── azure_search.py      # API Management service integration
├── pyproject.toml           # Project metadata and dependencies
├── Dockerfile               # Container build configuration
└── README.md                # This file
```

## Requirements

- Python 3.10 or higher
- Dependencies:
  - `mcp>=1.0.0` - Model Context Protocol SDK
  - `httpx>=0.27.0` - HTTP client
  - `pydantic>=2.0.0` - Data validation

## License

MIT License - See LICENSE file for details

## Links

- **PyPI**: https://pypi.org/project/nhsuk-mcp/
- **GitHub**: https://github.com/sinclr4/nhsuk-mcp-python  
- **Issues**: https://github.com/sinclr4/nhsuk-mcp-python/issues

## Author

Rob Sinclair - rob.sinclair@nhschoices.net

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
