import os
import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DigitalIDClient:
    """
    Client for communicating with the Digital ID & Blockchain Service
    Handles secure tourist data registration and emergency access requests
    """
    
    def __init__(self):
        self.base_url = os.environ.get("DIGITAL_ID_SERVICE_URL", "http://localhost:8002")
        self.api_key = os.environ.get("DIGITAL_ID_SERVICE_API_KEY", "test_api_key_12345")
        self.timeout = 30.0
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for service authentication"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def register_tourist_data(self, tourist_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register sensitive tourist data with the Digital ID service
        
        Args:
            tourist_data: Dictionary containing tourist information
            
        Returns:
            Registration response with hashes and confirmation
        """
        try:
            url = f"{self.base_url}/api/register"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=tourist_data,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully registered tourist data: {tourist_data.get('tourist_id')}")
                    return result
                else:
                    error_msg = f"Failed to register tourist data: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except httpx.TimeoutException:
            error_msg = "Timeout while registering tourist data"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error registering tourist data: {e}")
            raise
    
    async def request_emergency_access(self, access_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request emergency access to decrypted tourist data
        
        Args:
            access_request: Dictionary containing access request details
            
        Returns:
            Decrypted tourist data with access log information
        """
        try:
            tourist_id = access_request.get("tourist_id")
            url = f"{self.base_url}/api/request-access/{tourist_id}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=access_request,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Emergency access granted for tourist: {tourist_id}")
                    return result
                elif response.status_code == 404:
                    error_msg = f"Tourist data not found: {tourist_id}"
                    logger.warning(error_msg)
                    raise Exception(error_msg)
                else:
                    error_msg = f"Failed to get emergency access: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except httpx.TimeoutException:
            error_msg = "Timeout while requesting emergency access"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error requesting emergency access: {e}")
            raise
    
    async def verify_data_integrity(self, tourist_id: str) -> Dict[str, Any]:
        """
        Verify data integrity for a tourist
        
        Args:
            tourist_id: Tourist ID to verify
            
        Returns:
            Verification result
        """
        try:
            url = f"{self.base_url}/api/verify-integrity/{tourist_id}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Data integrity verified for tourist: {tourist_id}")
                    return result
                else:
                    error_msg = f"Failed to verify data integrity: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except httpx.TimeoutException:
            error_msg = "Timeout while verifying data integrity"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error verifying data integrity: {e}")
            raise
    
    async def get_audit_logs(self, tourist_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Get audit logs from the Digital ID service
        
        Args:
            tourist_id: Optional tourist ID to filter logs
            limit: Maximum number of logs to retrieve
            
        Returns:
            Audit logs response
        """
        try:
            url = f"{self.base_url}/api/audit-logs"
            params = {"limit": limit}
            if tourist_id:
                params["tourist_id"] = tourist_id
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Retrieved {result.get('count', 0)} audit logs")
                    return result
                else:
                    error_msg = f"Failed to get audit logs: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except httpx.TimeoutException:
            error_msg = "Timeout while getting audit logs"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            raise
    
    async def check_service_health(self) -> bool:
        """
        Check if the Digital ID service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            url = f"{self.base_url}/status"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    result = response.json()
                    is_healthy = result.get("status") == "operational"
                    logger.info(f"Digital ID service health check: {'healthy' if is_healthy else 'unhealthy'}")
                    return is_healthy
                else:
                    logger.warning(f"Digital ID service health check failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.warning(f"Digital ID service health check error: {e}")
            return False

# Global client instance
digital_id_client = DigitalIDClient()