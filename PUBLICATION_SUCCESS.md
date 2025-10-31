# 🎉 Package Successfully Published to PyPI!

## Publication Details

- **Package Name**: `nhs-organisations-mcp`
- **Version**: 1.0.2  
- **PyPI URL**: https://pypi.org/project/nhs-organisations-mcp/
- **GitHub**: https://github.com/sinclr4/nhs-organisations-mcp-python
- **Author**: Rob Sinclair <rob.sinclair@nhschoices.net>
- **License**: MIT

## Installation

Anyone can now install the package globally using:

```bash
pip install nhs-organisations-mcp
```

## Quick Start for Users

### 1. Install the Package

```bash
pip install nhs-organisations-mcp
```

### 2. Configure Claude Desktop

Add to `claude_desktop_config.json`:

**macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nhs-organisations": {
      "command": "python",
      "args": ["-m", "nhs_orgs_mcp.server"],
      "env": {
        "API_MANAGEMENT_ENDPOINT": "https://nhsuk-apim-int-uks.azure-api.net/service-search",
        "API_MANAGEMENT_SUBSCRIPTION_KEY": "your-subscription-key-here"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

The MCP server will be available with 4 tools:
- `get_organisation_types` - List all NHS organisation types
- `convert_postcode_to_coordinates` - Convert UK postcodes to coordinates
- `search_organisations_by_postcode` - Find organisations near a postcode
- `search_organisations_by_coordinates` - Find organisations near coordinates

## Package Statistics

- **Dependencies**: mcp>=1.0.0, httpx>=0.27.0, pydantic>=2.0.0
- **Python Support**: 3.10, 3.11, 3.12
- **Package Size**: ~9KB (wheel), ~8KB (source)
- **Installation**: Pure Python, no compilation required

## What's Included

The package provides:
- Complete MCP protocol implementation
- 4 MCP tools for NHS organisation search
- 24 NHS organisation types supported
- API Management integration
- Full type hints with Pydantic models

## Future Updates

To publish future versions:

1. Update version in `pyproject.toml`
2. Make your code changes
3. Commit to Git
4. Build: `python3 -m build`
5. Upload: `python3 -m twine upload dist/*`
6. Tag release: `git tag v1.0.1 && git push --tags`

## Support

- **Issues**: https://github.com/sinclr4/nhs-organisations-mcp-python/issues
- **Documentation**: https://github.com/sinclr4/nhs-organisations-mcp-python#readme

## Thank You!

The package is now publicly available for anyone to use! 🚀
