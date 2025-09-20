import aiohttp
import logging
import os
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class GeoapifyService:
    """Service for Geoapify reverse geocoding API integration"""
    
    def __init__(self):
        self.api_key = os.getenv("GEOAPIFY_API_KEY")
        self.base_url = "https://api.geoapify.com/v1/geocode"
        
    async def reverse_geocode(self, longitude: float, latitude: float) -> Optional[Dict[str, Any]]:
        """
        Perform reverse geocoding to get human-readable address from coordinates
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            
        Returns:
            Dictionary with address information or None if failed
        """
        if not self.api_key:
            logger.warning("GEOAPIFY_API_KEY not configured, skipping reverse geocoding")
            return None
            
        try:
            url = f"{self.base_url}/reverse"
            params = {
                "lat": latitude,
                "lon": longitude,
                "apiKey": self.api_key,
                "format": "json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._parse_geoapify_response(data)
                    else:
                        logger.error(f"Geoapify API error: {response.status} - {await response.text()}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error during reverse geocoding: {e}")
            return None
    
    async def _parse_geoapify_response(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Geoapify API response and extract useful address information"""
        try:
            if not data.get("results"):
                return None
                
            result = data["results"][0]
            
            # Extract address components
            address_info = {
                "formatted_address": result.get("formatted"),
                "country": result.get("country"),
                "state": result.get("state"),
                "county": result.get("county"), 
                "city": result.get("city"),
                "district": result.get("district"),
                "suburb": result.get("suburb"),
                "street": result.get("street"),
                "house_number": result.get("housenumber"),
                "postcode": result.get("postcode"),
                "place_type": result.get("result_type"),
                "confidence": result.get("confidence", 0)
            }
            
            # Create a readable address string for alerts
            readable_address = self._create_readable_address(address_info)
            address_info["readable_address"] = readable_address
            
            return address_info
            
        except Exception as e:
            logger.error(f"Error parsing Geoapify response: {e}")
            return None
    
    def _create_readable_address(self, address_info: Dict[str, Any]) -> str:
        """Create a human-readable address string for alerts"""
        try:
            # Try to build a meaningful address string
            parts = []
            
            # Add street/location info
            if address_info.get("street"):
                if address_info.get("house_number"):
                    parts.append(f"{address_info['house_number']} {address_info['street']}")
                else:
                    parts.append(address_info["street"])
            elif address_info.get("suburb"):
                parts.append(f"Near {address_info['suburb']}")
            elif address_info.get("district"):
                parts.append(f"Near {address_info['district']}")
            
            # Add city/area info
            if address_info.get("city"):
                parts.append(address_info["city"])
            elif address_info.get("county"):
                parts.append(address_info["county"])
                
            # Add state/country for context
            if address_info.get("state"):
                parts.append(address_info["state"])
            
            if parts:
                return ", ".join(parts)
            elif address_info.get("formatted_address"):
                return address_info["formatted_address"]
            else:
                return "Location address unavailable"
                
        except Exception as e:
            logger.error(f"Error creating readable address: {e}")
            return "Address formatting error"
    
    async def get_nearby_landmarks(self, longitude: float, latitude: float, radius: int = 1000) -> Optional[List[Dict[str, Any]]]:
        """
        Get nearby landmarks and points of interest
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate  
            radius: Search radius in meters (default: 1000)
            
        Returns:
            List of nearby landmarks or None if failed
        """
        if not self.api_key:
            logger.warning("GEOAPIFY_API_KEY not configured, skipping landmarks search")
            return None
            
        try:
            url = f"{self.base_url}/search"
            params = {
                "lat": latitude,
                "lon": longitude,
                "apiKey": self.api_key,
                "bias": f"proximity:{longitude},{latitude}",
                "limit": 5,
                "format": "json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._parse_landmarks_response(data)
                    else:
                        logger.error(f"Geoapify landmarks API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting nearby landmarks: {e}")
            return None
    
    async def _parse_landmarks_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse landmarks response"""
        try:
            landmarks = []
            
            for result in data.get("results", []):
                landmark = {
                    "name": result.get("name", result.get("formatted")),
                    "category": result.get("result_type"),
                    "distance": result.get("distance"),
                    "place_id": result.get("place_id")
                }
                landmarks.append(landmark)
                
            return landmarks
            
        except Exception as e:
            logger.error(f"Error parsing landmarks response: {e}")
            return []

# Global instance
geoapify_service = GeoapifyService()