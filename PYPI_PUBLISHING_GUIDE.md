# Publishing to PyPI

## Prerequisites

1. **Create a PyPI Account**
   - Go to https://pypi.org/account/register/
   - Verify your email address

2. **Generate an API Token**
   - Log in to PyPI
   - Go to Account Settings → API tokens
   - Click "Add API token"
   - Set scope to "Entire account" (or specific project after first upload)
   - Copy the token (starts with `pypi-`)
   - Store it securely - you won't see it again!

## Publishing Steps

### 1. Update Version (if needed)

Edit `pyproject.toml` and update the version number:
```toml
version = "1.0.1"  # Increment as needed
```

### 2. Build the Package

```bash
cd /Users/robsinclair/NHSUKMCP-Python
python3 -m build
```

This creates:
- `dist/nhs_organizations_mcp-X.Y.Z.tar.gz` (source distribution)
- `dist/nhs_organizations_mcp-X.Y.Z-py3-none-any.whl` (wheel)

### 3. Upload to PyPI

```bash
python3 -m twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: Your API token (paste the full token including `pypi-` prefix)

### 4. Verify Publication

Visit: https://pypi.org/project/nhs-organizations-mcp/

## Installation Test

After publication, anyone can install with:

```bash
pip install nhs-organizations-mcp
```

## Subsequent Releases

For future releases:

1. Make your code changes
2. Update version in `pyproject.toml`
3. Commit changes to Git
4. Clean old builds: `rm -rf dist/ build/ *.egg-info`
5. Build: `python3 -m build`
6. Upload: `python3 -m twine upload dist/*`
7. Tag in Git: `git tag v1.0.1 && git push --tags`

## Test PyPI (Optional)

To test before publishing to real PyPI:

1. Create account at https://test.pypi.org/
2. Upload: `python3 -m twine upload --repository testpypi dist/*`
3. Install: `pip install --index-url https://test.pypi.org/simple/ nhs-organizations-mcp`

## Package Information

- **Package Name**: `nhs-organizations-mcp`
- **PyPI URL**: https://pypi.org/project/nhs-organizations-mcp/
- **GitHub**: https://github.com/sinclr4/nhs-organizations-mcp-python
- **Install Command**: `pip install nhs-organizations-mcp`
- **Current Version**: 1.0.0

## Troubleshooting

### 403 Forbidden Error
- Check your API token is correct
- Ensure token scope allows uploading
- First upload must use account-scoped token

### Version Already Exists
- PyPI doesn't allow re-uploading same version
- Increment version number in `pyproject.toml`
- Rebuild and upload

### Missing Dependencies
```bash
pip install --upgrade build twine
```

## After Publishing

Users can install and use with:

```bash
# Install
pip install nhs-organizations-mcp

# Configure in Claude Desktop
{
  "mcpServers": {
    "nhs-organizations": {
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
