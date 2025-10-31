"""Azure API Management service integration"""

import os
import logging
from typing import List, Optional
import httpx
from .models import PostcodeResult, Organisation

logger = logging.getLogger(__name__)


class AzureSearchService:
    """Service for interacting with Azure API Management for NHS service search"""
    
    def __init__(self):
        # API Management base endpoint
        self.base_endpoint = os.getenv(
            "API_MANAGEMENT_ENDPOINT", 
            "https://nhsuk-apim-int-uks.azure-api.net"
        )
        # Subscription key
        self.subscription_key = os.getenv("API_MANAGEMENT_SUBSCRIPTION_KEY", "")
        
        if not self.subscription_key:
            logger.warning("API_MANAGEMENT_SUBSCRIPTION_KEY not configured")
    
    @property
    def is_configured(self) -> bool:
        """Check if API Management is properly configured"""
        return bool(self.subscription_key)
    
    async def get_postcode_coordinates(self, postcode: str) -> Optional[PostcodeResult]:
        """Convert a UK postcode to latitude/longitude coordinates using API Management
        
        Args:
            postcode: UK postcode (e.g., 'SW1A 1AA')
            
        Returns:
            PostcodeResult with coordinates if found, None otherwise
        """
        if not self.is_configured:
            logger.error("API Management not configured")
            return None
        
        # Use query parameter instead of path parameter
        url = f"{self.base_endpoint}/service-search/postcodesandplaces/"
        params = {
            "search": postcode,
            "api-version": "2"
        }
        
        headers = {
            "subscription-key": self.subscription_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Searching for postcode: {postcode}")
                response = await client.get(url, params=params, headers=headers, timeout=30.0)
                response.raise_for_status()
                
                data = response.json()
                logger.debug(f"Postcode search response: {data}")
                
                # Handle both direct object and array responses
                if isinstance(data, dict):
                    if "value" in data and isinstance(data["value"], list) and len(data["value"]) > 0:
                        # Response is wrapped in "value" array
                        result = data["value"][0]
                    elif "Latitude" in data and "Longitude" in data:
                        # Direct response object
                        result = data
                    else:
                        logger.warning(f"Unexpected response format: {data}")
                        return None
                else:
                    logger.warning(f"Unexpected response type: {type(data)}")
                    return None
                
                return PostcodeResult(
                    Latitude=result.get("Latitude"),
                    Longitude=result.get("Longitude"),
                    Postcode=postcode
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting postcode coordinates: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error getting postcode coordinates: {str(e)}")
            return None
    
    async def search_organisations(
        self,
        organisation_type: str,
        latitude: float, 
        longitude: float, 
        max_results: int = 10
    ) -> List[Organisation]:
        """Search for NHS organisations near a location using API Management
        
        Args:
            organisation_type: Type of organisation (e.g., 'PHA', 'GPP', 'HOS')
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            max_results: Maximum number of results to return
            
        Returns:
            List of Organisation objects
        """
        if not self.is_configured:
            logger.error("API Management not configured")
            return []
        
        url = f"{self.base_endpoint}/service-search/search"
        params = {"api-version": "2"}
        
        # Create search body with geo filter
        search_body = {
            "search": "*",
            "filter": f"OrganisationTypeID eq '{organisation_type}'",
            "orderby": f"geo.distance(Geocode, geography'POINT({longitude} {latitude})')",
            "top": max_results,
            "count": True
        }
        
        headers = {
            "subscription-key": self.subscription_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Searching for {organisation_type} near ({latitude}, {longitude})")
                response = await client.post(
                    url,
                    params=params,
                    json=search_body,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                logger.debug(f"Organisation search response: {data}")
                
                # Handle both direct array and wrapped responses
                if isinstance(data, dict) and "value" in data:
                    results = data["value"]
                elif isinstance(data, list):
                    results = data
                else:
                    logger.warning(f"Unexpected response format: {data}")
                    return []
                
                organisations = []
                for item in results:
                    geocode = item.get("Geocode", {})
                    
                    # Calculate distance
                    distance = self._calculate_distance(
                        latitude, longitude,
                        geocode.get("Latitude", 0),
                        geocode.get("Longitude", 0)
                    )
                    
                    org = Organisation(
                        organisation_name=item.get("OrganisationName"),
                        organisation_type=item.get("OrganisationTypeID"),
                        organisation_code=item.get("ODSCode"),
                        address_line_1=item.get("Address1", ""),
                        postcode=item.get("Postcode"),
                        distance_miles=distance
                    )
                    organisations.append(org)
                
                return organisations
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching organisations: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Error searching organisations: {str(e)}")
            return []
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in miles using Haversine formula"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 3959  # Earth's radius in miles
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

    def _extract_content_sections(self, data: dict) -> list:
        """Recursively extract content sections from hasPart elements
        
        Args:
            data: The JSON data structure to extract sections from
            
        Returns:
            List of content sections with headline and text
        """
        sections = []
        
        def extract_from_part(part):
            """Recursively extract content from a part"""
            if not isinstance(part, dict):
                return
                
            # Extract basic content from this part
            section = {}
            if part.get("headline"):
                section["headline"] = part.get("headline")
            if part.get("text"):
                section["text"] = part.get("text")
            if part.get("description") and not part.get("text"):
                section["text"] = part.get("description")
                
            # Only add section if it has meaningful content
            if section.get("headline") or section.get("text"):
                sections.append(section)
            
            # Recursively process hasPart elements
            if "hasPart" in part:
                has_parts = part["hasPart"]
                if isinstance(has_parts, list):
                    for sub_part in has_parts:
                        extract_from_part(sub_part)
                elif isinstance(has_parts, dict):
                    extract_from_part(has_parts)
        
        # Start extraction from multiple possible root elements
        root_elements = []
        
        # Check mainEntityOfPage
        if "mainEntityOfPage" in data:
            main_content = data["mainEntityOfPage"]
            if isinstance(main_content, list):
                root_elements.extend(main_content)
            elif isinstance(main_content, dict):
                root_elements.append(main_content)
        
        # Check direct hasPart
        if "hasPart" in data:
            has_parts = data["hasPart"]
            if isinstance(has_parts, list):
                root_elements.extend(has_parts)
            elif isinstance(has_parts, dict):
                root_elements.append(has_parts)
        
        # Also check the root data itself
        root_elements.append(data)
        
        # Process all root elements
        for element in root_elements:
            extract_from_part(element)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_sections = []
        for section in sections:
            # Create a simple key from headline and first 50 chars of text
            key = f"{section.get('headline', '')[:50]}_{section.get('text', '')[:50]}"
            if key not in seen:
                seen.add(key)
                unique_sections.append(section)
        
        return unique_sections

    async def get_health_topic(self, topic_slug: str) -> Optional[dict]:
        """Get health condition/topic information from NHS API
        
        Args:
            topic_slug: The URL slug for the condition (e.g., 'asthma', 'diabetes', 'flu')
            
        Returns:
            Dictionary with health topic information including name, description, and content
        """
        if not self.is_configured:
            logger.error("API Management not configured")
            return None
        
        # Conditions API endpoint (different from service-search)
        url = f"{self.base_endpoint}/conditions/{topic_slug}"
        
        headers = {
            "subscription-key": self.subscription_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Fetching health topic: {topic_slug}")
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                
                data = response.json()
                logger.debug(f"Health topic response: {data.get('name', 'Unknown')}")
                
                # Extract relevant information
                # Always use www.nhs.uk for the public-facing URL
                api_url = data.get("url")
                if api_url:
                    website_url = api_url.replace("api.nhs.uk", "www.nhs.uk")
                else:
                    website_url = None
                result = {
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "url": website_url,
                    "dateModified": data.get("dateModified"),
                    "lastReviewed": data.get("lastReviewed", [None, None]),
                    "genre": data.get("genre", [])
                }
                
                # Extract content sections using recursive hasPart processing
                result["sections"] = self._extract_content_sections(data)
                
                return result
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Health topic not found: {topic_slug}")
                return None
            logger.error(f"HTTP error fetching health topic: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error fetching health topic: {str(e)}")
            return None
