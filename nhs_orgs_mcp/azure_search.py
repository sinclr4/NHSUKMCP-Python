"""Azure API Management service integration"""

import os
import logging
from typing import List, Optional
import httpx
from .models import PostcodeResult, Organization

logger = logging.getLogger(__name__)


class AzureSearchService:
    """Service for interacting with Azure API Management for NHS service search"""
    
    def __init__(self):
        # API Management endpoint
        self.endpoint = os.getenv(
            "AZURE_SEARCH_ENDPOINT", 
            "https://nhsuk-apim-int-uks.azure-api.net/service-search"
        )
        # Subscription key (not API key)
        self.subscription_key = os.getenv("AZURE_SEARCH_API_KEY", "")
        
        # These are no longer used with API Management but kept for backwards compatibility
        self.postcode_index = os.getenv("AZURE_SEARCH_POSTCODE_INDEX", "postcodesandplaces")
        self.service_index = os.getenv("AZURE_SEARCH_SERVICE_INDEX", "service-search")
        
        if not self.subscription_key:
            logger.warning("AZURE_SEARCH_API_KEY (subscription key) not configured")
    
    @property
    def is_configured(self) -> bool:
        """Check if API Management is properly configured"""
        return bool(self.subscription_key)
    
    async def get_postcode_coordinates(self, postcode: str) -> Optional[PostcodeResult]:
        """Convert a UK postcode to latitude/longitude coordinates using API Management
        
        Args:
            postcode: UK postcode (e.g., 'SW1A 1AA')
            
        Returns:
            PostcodeResult with coordinates, or None if not found
        """
        if not self.is_configured:
            raise ValueError(
                "API Management is not configured. Set AZURE_SEARCH_API_KEY "
                "(subscription key) environment variable."
            )
        
        # Normalize postcode - remove spaces and uppercase
        normalized_postcode = postcode.strip().upper().replace(" ", "")
        
        # API Management endpoint: /postcodesandplaces/?search={postcode}&api-version=2
        url = f"{self.endpoint}/postcodesandplaces/"
        params = {
            "search": normalized_postcode,
            "api-version": "2"
        }
        headers = {
            "Content-Type": "application/json",
            "subscription-key": self.subscription_key
        }
        
        logger.info(f"Searching for postcode: {normalized_postcode}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Check if we got results (could be array or single object)
                if isinstance(data, dict) and data.get("value"):
                    # Results in array
                    if len(data["value"]) > 0:
                        first_result = data["value"][0]
                        return PostcodeResult(
                            latitude=first_result.get("Latitude") or first_result.get("latitude", 0.0),
                            longitude=first_result.get("Longitude") or first_result.get("longitude", 0.0),
                            postcode=postcode.strip().upper()
                        )
                elif isinstance(data, dict) and ("Latitude" in data or "latitude" in data):
                    # Direct result object
                    return PostcodeResult(
                        latitude=data.get("Latitude") or data.get("latitude", 0.0),
                        longitude=data.get("Longitude") or data.get("longitude", 0.0),
                        postcode=postcode.strip().upper()
                    )
                
                logger.warning(f"Postcode not found: {normalized_postcode}")
                return None
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.warning(f"Postcode not found: {normalized_postcode}")
                    return None
                logger.error(f"Error searching postcode: {e}")
                raise
            except httpx.HTTPError as e:
                logger.error(f"Error searching postcode: {e}")
                raise
    
    async def search_organizations(
        self,
        org_type: str,
        latitude: float,
        longitude: float,
        max_results: int = 10
    ) -> List[Organization]:
        """Search for NHS organizations by type and location using API Management
        
        Args:
            org_type: Organization type code (e.g., 'PHA', 'GPP')
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            max_results: Maximum number of results (1-50)
            
        Returns:
            List of Organization objects sorted by distance
        """
        if not self.is_configured:
            raise ValueError(
                "API Management is not configured. Set AZURE_SEARCH_API_KEY "
                "(subscription key) environment variable."
            )
        
        # API Management endpoint: /search?api-version=2
        url = f"{self.endpoint}/search"
        params = {"api-version": "2"}
        headers = {
            "Content-Type": "application/json",
            "subscription-key": self.subscription_key
        }
        
        payload = {
            "search": "*",
            "filter": f"OrganisationTypeId eq '{org_type.upper()}'",
            "searchMode": "all",
            "orderby": f"geo.distance(Geocode, geography'POINT({longitude} {latitude})')",
            "top": min(max_results, 50),
            "count": True
        }
        
        logger.info(f"Searching for {org_type} near {latitude}, {longitude}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, params=params, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                organizations = []
                for item in data.get("value", []):
                    # Calculate distance in miles
                    item_lat = item.get("Latitude", 0.0)
                    item_lon = item.get("Longitude", 0.0)
                    distance = self._calculate_distance(
                        latitude, longitude,
                        item_lat, item_lon
                    )
                    
                    # Build address from components
                    address_parts = []
                    for key in ["Address1", "Address2", "Address3", "City", "County"]:
                        val = item.get(key)
                        if val and val.strip():
                            address_parts.append(val.strip())
                    
                    organizations.append(Organization(
                        organisation_code=item.get("ODSCode", ""),
                        organisation_name=item.get("OrganisationName", ""),
                        organisation_type=item.get("OrganisationTypeId", ""),
                        address_line_1=", ".join(address_parts) if address_parts else None,
                        address_line_2=None,
                        town=item.get("City"),
                        county=item.get("County"),
                        postcode=item.get("Postcode"),
                        latitude=item_lat if item_lat else None,
                        longitude=item_lon if item_lon else None,
                        distance_miles=round(distance, 2)
                    ))
                
                logger.info(f"Found {len(organizations)} organizations")
                return organizations
                
            except httpx.HTTPError as e:
                logger.error(f"Error searching organizations: {e}")
                raise
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in miles using Haversine formula"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 3959  # Earth's radius in miles
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
