import json
import asyncio
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

try:
    from .models import WebSocketMessage, LocationWebSocketData
except ImportError:
    from models import WebSocketMessage, LocationWebSocketData

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket connection manager for real-time updates"""
    
    def __init__(self):
        # Active WebSocket connections by type
        self.dashboard_connections: Set[WebSocket] = set()
        self.location_connections: Dict[str, WebSocket] = {}  # tourist_id -> WebSocket
        self.admin_connections: Set[WebSocket] = set()
    
    async def connect_dashboard(self, websocket: WebSocket):
        """Connect a dashboard client"""
        await websocket.accept()
        self.dashboard_connections.add(websocket)
        logger.info(f"Dashboard client connected. Total: {len(self.dashboard_connections)}")
    
    async def connect_location_tracker(self, websocket: WebSocket, tourist_id: str):
        """Connect a location tracker (tourist mobile app)"""
        await websocket.accept()
        self.location_connections[tourist_id] = websocket
        logger.info(f"Location tracker connected for tourist {tourist_id}")
    
    async def connect_admin(self, websocket: WebSocket):
        """Connect an admin client"""
        await websocket.accept()
        self.admin_connections.add(websocket)
        logger.info(f"Admin client connected. Total: {len(self.admin_connections)}")
    
    def disconnect_dashboard(self, websocket: WebSocket):
        """Disconnect a dashboard client"""
        self.dashboard_connections.discard(websocket)
        logger.info(f"Dashboard client disconnected. Total: {len(self.dashboard_connections)}")
    
    def disconnect_location_tracker(self, tourist_id: str):
        """Disconnect a location tracker"""
        if tourist_id in self.location_connections:
            del self.location_connections[tourist_id]
            logger.info(f"Location tracker disconnected for tourist {tourist_id}")
    
    def disconnect_admin(self, websocket: WebSocket):
        """Disconnect an admin client"""
        self.admin_connections.discard(websocket)
        logger.info(f"Admin client disconnected. Total: {len(self.admin_connections)}")
    
    async def send_to_dashboard(self, message: WebSocketMessage):
        """Send message to all dashboard clients"""
        if not self.dashboard_connections:
            return
        
        message_data = message.dict()
        message_json = json.dumps(message_data, default=str)
        
        disconnected = set()
        for connection in self.dashboard_connections.copy():
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending to dashboard: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.dashboard_connections.discard(connection)
    
    async def send_to_admin(self, message: WebSocketMessage):
        """Send message to all admin clients"""
        if not self.admin_connections:
            return
        
        message_data = message.dict()
        message_json = json.dumps(message_data, default=str)
        
        disconnected = set()
        for connection in self.admin_connections.copy():
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending to admin: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.admin_connections.discard(connection)
    
    async def send_to_specific_dashboard(self, websocket: WebSocket, message: WebSocketMessage):
        """Send message to a specific dashboard client"""
        try:
            message_data = message.dict()
            message_json = json.dumps(message_data, default=str)
            await websocket.send_text(message_json)
        except Exception as e:
            logger.error(f"Error sending to specific dashboard: {e}")
            self.dashboard_connections.discard(websocket)
    
    async def broadcast_location_update(self, tourist_id: str, longitude: float, latitude: float, 
                                      tourist_name: str, status: str, address: str = None):
        """Broadcast location update to all dashboard clients"""
        message = WebSocketMessage(
            type="location_update",
            data={
                "tourist_id": tourist_id,
                "tourist_name": tourist_name,
                "longitude": longitude,
                "latitude": latitude,
                "status": status,
                "address": address,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        await self.send_to_dashboard(message)
        await self.send_to_admin(message)
    
    async def broadcast_alert(self, alert_data: Dict):
        """Broadcast new alert to all dashboard and admin clients"""
        message = WebSocketMessage(
            type="new_alert",
            data=alert_data
        )
        
        await self.send_to_dashboard(message)
        await self.send_to_admin(message)
    
    async def broadcast_status_change(self, tourist_id: str, tourist_name: str, 
                                    old_status: str, new_status: str, reason: str = None):
        """Broadcast tourist status change"""
        message = WebSocketMessage(
            type="status_change",
            data={
                "tourist_id": tourist_id,
                "tourist_name": tourist_name,
                "old_status": old_status,
                "new_status": new_status,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        await self.send_to_dashboard(message)
        await self.send_to_admin(message)
    
    async def broadcast_alert_resolution(self, alert_data: Dict):
        """Broadcast alert resolution"""
        message = WebSocketMessage(
            type="alert_resolved",
            data=alert_data
        )
        
        await self.send_to_dashboard(message)
        await self.send_to_admin(message)
    
    async def send_emergency_broadcast(self, emergency_data: Dict):
        """Send emergency broadcast to all connected clients"""
        message = WebSocketMessage(
            type="emergency",
            data=emergency_data
        )
        
        # Send to all client types
        await self.send_to_dashboard(message)
        await self.send_to_admin(message)
        
        # Also try to send to location trackers (for emergency notifications)
        for tourist_id, connection in self.location_connections.items():
            try:
                message_json = json.dumps(message.dict(), default=str)
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending emergency to tourist {tourist_id}: {e}")
    
    def get_connection_stats(self) -> Dict[str, int]:
        """Get connection statistics"""
        return {
            "dashboard_connections": len(self.dashboard_connections),
            "location_connections": len(self.location_connections),
            "admin_connections": len(self.admin_connections),
            "total_connections": len(self.dashboard_connections) + len(self.location_connections) + len(self.admin_connections)
        }

# Global connection manager instance
manager = ConnectionManager()

async def handle_location_websocket(websocket: WebSocket, tourist_id: str):
    """Handle location tracking WebSocket connection"""
    await manager.connect_location_tracker(websocket, tourist_id)
    
    try:
        while True:
            # Receive location data from tourist's mobile app
            data = await websocket.receive_text()
            location_data = json.loads(data)
            
            # Validate and process location data
            try:
                location_update = LocationWebSocketData(**location_data)
                
                # Process location update
                try:
                    from .services.location_service import LocationService
                    from .models import LocationUpdate
                except ImportError:
                    from services.location_service import LocationService
                    from models import LocationUpdate
                
                location_update_model = LocationUpdate(
                    tourist_id=location_update.tourist_id,
                    longitude=location_update.longitude,
                    latitude=location_update.latitude
                )
                
                success = await LocationService.update_location(location_update_model)
                
                if success:
                    # Get tourist details for broadcasting
                    try:
                        from .services.tourist_service import TouristService
                    except ImportError:
                        from services.tourist_service import TouristService
                    tourist = await TouristService.get_tourist_by_id(tourist_id)
                    
                    if tourist:
                        # Broadcast to dashboard
                        await manager.broadcast_location_update(
                            tourist_id=tourist_id,
                            longitude=location_update.longitude,
                            latitude=location_update.latitude,
                            tourist_name=tourist.full_name,
                            status=tourist.status.value
                        )
                
            except Exception as e:
                logger.error(f"Error processing location data: {e}")
                await websocket.send_text(json.dumps({"error": "Invalid location data"}))
    
    except WebSocketDisconnect:
        manager.disconnect_location_tracker(tourist_id)
    except Exception as e:
        logger.error(f"WebSocket error for tourist {tourist_id}: {e}")
        manager.disconnect_location_tracker(tourist_id)

async def handle_dashboard_websocket(websocket: WebSocket):
    """Handle dashboard WebSocket connection"""
    await manager.connect_dashboard(websocket)
    
    try:
        while True:
            # Keep connection alive and handle any dashboard requests
            data = await websocket.receive_text()
            
            # Handle dashboard commands
            try:
                command = json.loads(data)
                
                if command.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif command.get("type") == "request_status":
                    # Send current system status
                    try:
                        from .services.analytics_service import AnalyticsService
                    except ImportError:
                        from services.analytics_service import AnalyticsService
                    kpis = await AnalyticsService.get_dashboard_kpis()
                    
                    message = WebSocketMessage(
                        type="system_status",
                        data=kpis.dict()
                    )
                    
                    await manager.send_to_specific_dashboard(websocket, message)
                
            except json.JSONDecodeError:
                logger.error("Invalid JSON received from dashboard")
    
    except WebSocketDisconnect:
        manager.disconnect_dashboard(websocket)
    except Exception as e:
        logger.error(f"Dashboard WebSocket error: {e}")
        manager.disconnect_dashboard(websocket)