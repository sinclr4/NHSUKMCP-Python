"""NHS Organizations MCP Server

A Model Context Protocol server providing tools for searching NHS organizations.
"""

import asyncio
import logging
import os
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types

from .models import ORGANIZATION_TYPES
from .azure_search import AzureSearchService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
search_service = AzureSearchService()

# Create MCP server
server = Server("nhs-organizations-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available MCP tools"""
    return [
        types.Tool(
            name="get_organization_types",
            description="Get a list of all available NHS organization types with their descriptions",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="convert_postcode_to_coordinates",
            description="Convert a UK postcode to latitude and longitude coordinates using Azure Search",
            inputSchema={
                "type": "object",
                "properties": {
                    "postcode": {
                        "type": "string",
                        "description": "UK postcode to convert (e.g., 'SW1A 1AA')"
                    }
                },
                "required": ["postcode"]
            }
        ),
        types.Tool(
            name="search_organizations_by_postcode",
            description="Search for NHS organizations by type and postcode. First converts postcode to coordinates, then searches for nearby organizations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "organizationType": {
                        "type": "string",
                        "description": "NHS organization type code (e.g., 'PHA', 'GPP', 'HOS'). Use get_organization_types to see all available types."
                    },
                    "postcode": {
                        "type": "string",
                        "description": "UK postcode to search near (e.g., 'SW1A 1AA')"
                    },
                    "maxResults": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-50, default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["organizationType", "postcode"]
            }
        ),
        types.Tool(
            name="search_organizations_by_coordinates",
            description="Search for NHS organizations by type and coordinates (latitude/longitude)",
            inputSchema={
                "type": "object",
                "properties": {
                    "organizationType": {
                        "type": "string",
                        "description": "NHS organization type code (e.g., 'PHA', 'GPP', 'HOS'). Use get_organization_types to see all available types."
                    },
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate"
                    },
                    "maxResults": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-50, default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["organizationType", "latitude", "longitude"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict[str, Any] | None
) -> list[types.TextContent]:
    """Handle tool execution"""
    
    if name == "get_organization_types":
        return [types.TextContent(
            type="text",
            text=str(ORGANIZATION_TYPES)
        )]
    
    elif name == "convert_postcode_to_coordinates":
        if not arguments or "postcode" not in arguments:
            raise ValueError("postcode parameter is required")
        
        postcode = arguments["postcode"]
        
        if not search_service.is_configured:
            return [types.TextContent(
                type="text",
                text="Error: Azure Search service is not configured. Please set AZURE_SEARCH_API_KEY environment variable."
            )]
        
        try:
            result = await search_service.get_postcode_coordinates(postcode)
            if result is None:
                return [types.TextContent(
                    type="text",
                    text=f"Postcode '{postcode}' not found"
                )]
            
            return [types.TextContent(
                type="text",
                text=f"Postcode: {result.postcode}\nLatitude: {result.latitude}\nLongitude: {result.longitude}"
            )]
        except Exception as e:
            logger.error(f"Error converting postcode: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    elif name == "search_organizations_by_postcode":
        if not arguments:
            raise ValueError("Arguments required")
        
        org_type = arguments.get("organizationType", "").upper()
        postcode = arguments.get("postcode", "")
        max_results = arguments.get("maxResults", 10)
        
        if not org_type or not postcode:
            raise ValueError("organizationType and postcode are required")
        
        if org_type not in ORGANIZATION_TYPES:
            return [types.TextContent(
                type="text",
                text=f"Invalid organization type '{org_type}'. Available types: {', '.join(ORGANIZATION_TYPES.keys())}"
            )]
        
        if not search_service.is_configured:
            return [types.TextContent(
                type="text",
                text="Error: Azure Search service is not configured. Please set AZURE_SEARCH_API_KEY environment variable."
            )]
        
        try:
            # Convert postcode to coordinates
            coords = await search_service.get_postcode_coordinates(postcode)
            if coords is None:
                return [types.TextContent(
                    type="text",
                    text=f"Postcode '{postcode}' not found"
                )]
            
            # Search organizations
            organizations = await search_service.search_organizations(
                org_type,
                coords.latitude,
                coords.longitude,
                max_results
            )
            
            if not organizations:
                return [types.TextContent(
                    type="text",
                    text=f"No {ORGANIZATION_TYPES[org_type]} organizations found near {postcode}"
                )]
            
            result_text = f"Found {len(organizations)} {ORGANIZATION_TYPES[org_type]} near {postcode} ({coords.latitude}, {coords.longitude}):\n\n"
            
            for org in organizations:
                result_text += f"• {org.organisation_name} ({org.organisation_code})\n"
                if org.address_line_1:
                    result_text += f"  {org.address_line_1}\n"
                if org.town:
                    result_text += f"  {org.town}"
                if org.postcode:
                    result_text += f", {org.postcode}\n"
                else:
                    result_text += "\n"
                if org.distance_miles is not None:
                    result_text += f"  Distance: {org.distance_miles} miles\n"
                result_text += "\n"
            
            return [types.TextContent(
                type="text",
                text=result_text
            )]
            
        except Exception as e:
            logger.error(f"Error searching organizations: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    elif name == "search_organizations_by_coordinates":
        if not arguments:
            raise ValueError("Arguments required")
        
        org_type = arguments.get("organizationType", "").upper()
        latitude = arguments.get("latitude")
        longitude = arguments.get("longitude")
        max_results = arguments.get("maxResults", 10)
        
        if not org_type or latitude is None or longitude is None:
            raise ValueError("organizationType, latitude, and longitude are required")
        
        if org_type not in ORGANIZATION_TYPES:
            return [types.TextContent(
                type="text",
                text=f"Invalid organization type '{org_type}'. Available types: {', '.join(ORGANIZATION_TYPES.keys())}"
            )]
        
        if not search_service.is_configured:
            return [types.TextContent(
                type="text",
                text="Error: Azure Search service is not configured. Please set AZURE_SEARCH_API_KEY environment variable."
            )]
        
        try:
            organizations = await search_service.search_organizations(
                org_type,
                latitude,
                longitude,
                max_results
            )
            
            if not organizations:
                return [types.TextContent(
                    type="text",
                    text=f"No {ORGANIZATION_TYPES[org_type]} organizations found near ({latitude}, {longitude})"
                )]
            
            result_text = f"Found {len(organizations)} {ORGANIZATION_TYPES[org_type]} near ({latitude}, {longitude}):\n\n"
            
            for org in organizations:
                result_text += f"• {org.organisation_name} ({org.organisation_code})\n"
                if org.address_line_1:
                    result_text += f"  {org.address_line_1}\n"
                if org.town:
                    result_text += f"  {org.town}"
                if org.postcode:
                    result_text += f", {org.postcode}\n"
                else:
                    result_text += "\n"
                if org.distance_miles is not None:
                    result_text += f"  Distance: {org.distance_miles} miles\n"
                result_text += "\n"
            
            return [types.TextContent(
                type="text",
                text=result_text
            )]
            
        except Exception as e:
            logger.error(f"Error searching organizations: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def run_server():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        logger.info("NHS Organizations MCP Server starting...")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="nhs-organizations-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main():
    """Entry point for the MCP server"""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
