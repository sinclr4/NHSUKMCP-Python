# Multi-stage build for NHS Organizations MCP Server (Python)

FROM python:3.11-slim AS base
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip

# Copy project files
COPY pyproject.toml ./
COPY nhs_orgs_mcp/ ./nhs_orgs_mcp/

# Install the package
RUN pip install --no-cache-dir .

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO

# The MCP server runs on stdio - no port needed
# But we can accept stdin from the container runtime
ENTRYPOINT ["python", "-m", "nhs_orgs_mcp.server"]
