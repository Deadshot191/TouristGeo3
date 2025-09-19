import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
import logging

try:
    from ..models import (
        Alert, AlertCreate, AlertResponse, AlertFilters, AlertType, 
        AlertSeverity, AlertStatus, AlertLocation
    )
    from ..database import get_alerts_collection, get_tourists_collection
    from .digital_id_client import digital_id_client
except ImportError:
    from models import (
        Alert, AlertCreate, AlertResponse, AlertFilters, AlertType, 
        AlertSeverity, AlertStatus, AlertLocation
    )
    from database import get_alerts_collection, get_tourists_collection
    from services.digital_id_client import digital_id_client

logger = logging.getLogger(__name__)

class AlertService:
    
    @staticmethod
    def generate_alert_id() -> str:
        """Generate unique alert ID in PN-XXXX format"""
        # Get current timestamp and generate a short unique suffix
        timestamp = str(int(datetime.utcnow().timestamp()))[-4:]
        random_suffix = str(uuid.uuid4())[:4].upper()
        return f"PN-{timestamp}{random_suffix}"
    
    @staticmethod
    async def create_alert(alert_data: AlertCreate) -> Alert:
        """Create a new alert"""
        try:
            alerts_collection = await get_alerts_collection()
            
            # Create alert object
            alert = Alert(
                alert_id=AlertService.generate_alert_id(),
                tourist_id=ObjectId(alert_data.tourist_id),
                alert_type=alert_data.alert_type,
                severity=alert_data.severity,
                location=AlertLocation(
                    coordinates=[alert_data.longitude, alert_data.latitude],
                    address=alert_data.address
                ),
                description=alert_data.description
            )
            
            # Insert into database
            result = await alerts_collection.insert_one(alert.dict(by_alias=True))
            alert.id = result.inserted_id
            
            logger.info(f"Created alert: {alert.alert_id} for tourist {alert_data.tourist_id}")
            
            # Update tourist status if it's a critical alert
            if alert_data.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                try:
                    from .tourist_service import TouristService
                    from ..models import TouristStatus
                except ImportError:
                    from services.tourist_service import TouristService
                    from models import TouristStatus
                
                if alert_data.alert_type == AlertType.PANIC_BUTTON:
                    await TouristService.update_tourist_status(
                        alert_data.tourist_id, 
                        TouristStatus.PANIC,
                        f"Panic alert: {alert.alert_id}"
                    )
                else:
                    await TouristService.update_tourist_status(
                        alert_data.tourist_id, 
                        TouristStatus.ANOMALY,
                        f"Alert: {alert.alert_id}"
                    )
            
            # For high/critical alerts, get decrypted tourist data for notifications
            if alert_data.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                await AlertService._send_emergency_notifications(alert, alert_data.tourist_id)
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise
    
    @staticmethod
    async def _send_emergency_notifications(alert: Alert, tourist_id: str):
        """
        Send emergency notifications with decrypted tourist data
        Only called for high/critical severity alerts
        """
        try:
            # Get tourist's digital ID
            tourists_collection = await get_tourists_collection()
            tourist = await tourists_collection.find_one({"_id": ObjectId(tourist_id)})
            
            if not tourist:
                logger.error(f"Tourist not found for emergency notification: {tourist_id}")
                return
            
            digital_id = tourist.get("digital_id")
            if not digital_id:
                logger.error(f"No digital ID found for tourist: {tourist_id}")
                return
            
            # Request decrypted data from Digital ID service
            access_request = {
                "tourist_id": digital_id,
                "authority_id": "ALERT_SYSTEM",
                "authority_name": "Emergency Alert System",
                "authority_department": "Automated Emergency Response",
                "access_reason": alert.alert_type.value,
                "alert_id": alert.alert_id
            }
            
            try:
                decrypted_data = await digital_id_client.request_emergency_access(access_request)
                
                # Send notifications with full personal details
                await AlertService._send_sms_notification(alert, decrypted_data)
                await AlertService._send_push_notification(alert, decrypted_data)
                
                logger.info(f"Emergency notifications sent for alert: {alert.alert_id}")
                
            except Exception as e:
                logger.error(f"Failed to get decrypted data for emergency notification: {e}")
                # Fallback: send generic notification without personal details
                await AlertService._send_generic_notification(alert, digital_id)
                
        except Exception as e:
            logger.error(f"Error sending emergency notifications: {e}")
    
    @staticmethod
    async def _send_sms_notification(alert: Alert, decrypted_data: Dict[str, Any]):
        """Send SMS notification to emergency contacts with full details"""
        try:
            tourist_name = decrypted_data.get("full_name", "Unknown Tourist")
            emergency_contacts = decrypted_data.get("emergency_contacts", [])
            
            # Prepare SMS message with full details
            message = f"EMERGENCY ALERT: {tourist_name} ({decrypted_data.get('nationality', 'Unknown')}) "
            message += f"has triggered a {alert.alert_type.value} alert. "
            message += f"Location: {alert.location.address or 'Coordinates available'}. "
            message += f"Alert ID: {alert.alert_id}. Please contact authorities immediately."
            
            # Send to all emergency contacts
            for contact in emergency_contacts:
                contact_name = contact.get("name", "Emergency Contact")
                contact_phone = contact.get("phone")
                
                if contact_phone:
                    # Here you would integrate with SMS service (Twilio, etc.)
                    logger.info(f"SMS sent to {contact_name} at {contact_phone}: {message[:50]}...")
                    
                    # Placeholder for actual SMS integration
                    # await sms_service.send_sms(contact_phone, message)
            
        except Exception as e:
            logger.error(f"Error sending SMS notifications: {e}")
    
    @staticmethod
    async def _send_push_notification(alert: Alert, decrypted_data: Dict[str, Any]):
        """Send push notification to dashboard with full details"""
        try:
            from ..websocket_manager import manager
            
            tourist_name = decrypted_data.get("full_name", "Unknown Tourist")
            
            notification_data = {
                "type": "emergency_alert",
                "alert_id": alert.alert_id,
                "tourist_name": tourist_name,
                "tourist_nationality": decrypted_data.get("nationality"),
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "location": {
                    "coordinates": alert.location.coordinates,
                    "address": alert.location.address
                },
                "emergency_contacts": decrypted_data.get("emergency_contacts", []),
                "timestamp": alert.created_at.isoformat(),
                "description": alert.description
            }
            
            # Broadcast to dashboard clients
            await manager.broadcast_to_dashboard(notification_data)
            
            logger.info(f"Push notification sent for emergency alert: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
    
    @staticmethod
    async def _send_generic_notification(alert: Alert, digital_id: str):
        """Send generic notification without personal details (fallback)"""
        try:
            message = f"Emergency alert {alert.alert_id} triggered for tourist {digital_id}. "
            message += f"Alert type: {alert.alert_type.value}. Location data available."
            
            logger.info(f"Generic notification: {message}")
            
            # You could still send basic alert to authorities without personal data
            # This maintains system functionality even if Digital ID service is unavailable
            
        except Exception as e:
            logger.error(f"Error sending generic notification: {e}")
    
    @staticmethod
    async def create_panic_alert(tourist_id: str, longitude: float, latitude: float, address: str = None) -> Alert:
        """Create a panic button alert (highest priority)"""
        alert_data = AlertCreate(
            tourist_id=tourist_id,
            alert_type=AlertType.PANIC_BUTTON,
            severity=AlertSeverity.CRITICAL,
            longitude=longitude,
            latitude=latitude,
            address=address,
            description="Emergency panic button activated"
        )
        
        return await AlertService.create_alert(alert_data)
    
    @staticmethod
    async def create_geofence_breach_alert(tourist_id: str, longitude: float, latitude: float, 
                                         fence_name: str, risk_level: str) -> Alert:
        """Create a geo-fence breach alert"""
        severity_map = {
            "low": AlertSeverity.LOW,
            "medium": AlertSeverity.MEDIUM,
            "high": AlertSeverity.HIGH,
            "critical": AlertSeverity.CRITICAL
        }
        
        alert_data = AlertCreate(
            tourist_id=tourist_id,
            alert_type=AlertType.GEOFENCE_BREACH,
            severity=severity_map.get(risk_level, AlertSeverity.MEDIUM),
            longitude=longitude,
            latitude=latitude,
            description=f"Entered restricted area: {fence_name}"
        )
        
        return await AlertService.create_alert(alert_data)
    
    @staticmethod
    async def create_inactivity_alert(tourist_id: str, last_location: Dict[str, Any], 
                                    hours_inactive: int) -> Alert:
        """Create a prolonged inactivity alert"""
        coords = last_location["coordinates"]["coordinates"]
        
        alert_data = AlertCreate(
            tourist_id=tourist_id,
            alert_type=AlertType.PROLONGED_INACTIVITY,
            severity=AlertSeverity.MEDIUM,
            longitude=coords[0],
            latitude=coords[1],
            address=last_location.get("address"),
            description=f"No activity detected for {hours_inactive} hours"
        )
        
        return await AlertService.create_alert(alert_data)
    
    @staticmethod
    async def create_route_deviation_alert(tourist_id: str, longitude: float, latitude: float, 
                                         deviation_distance: float, address: str = None) -> Alert:
        """Create a route deviation alert"""
        alert_data = AlertCreate(
            tourist_id=tourist_id,
            alert_type=AlertType.ROUTE_DEVIATION,
            severity=AlertSeverity.MEDIUM,
            longitude=longitude,
            latitude=latitude,
            address=address,
            description=f"Route deviation detected: {deviation_distance:.2f}km from planned itinerary"
        )
        
        return await AlertService.create_alert(alert_data)
    
    @staticmethod
    async def create_prolonged_inactivity_alert(tourist_id: str, longitude: float, latitude: float, 
                                              inactivity_duration_minutes: int, address: str = None) -> Alert:
        """Create a prolonged inactivity alert"""
        alert_data = AlertCreate(
            tourist_id=tourist_id,
            alert_type=AlertType.PROLONGED_INACTIVITY,
            severity=AlertSeverity.HIGH,
            longitude=longitude,
            latitude=latitude,
            address=address,
            description=f"Prolonged inactivity: No movement detected for {inactivity_duration_minutes} minutes"
        )
        
        return await AlertService.create_alert(alert_data)
    
    @staticmethod
    async def get_alerts(filters: AlertFilters) -> List[AlertResponse]:
        """Get alerts with filters"""
        try:
            alerts_collection = await get_alerts_collection()
            tourists_collection = await get_tourists_collection()
            
            # Build query
            query = {}
            
            if filters.alert_type:
                query["alert_type"] = filters.alert_type.value
            
            if filters.status:
                query["status"] = filters.status.value
            
            if filters.severity:
                query["severity"] = filters.severity.value
            
            if filters.start_date or filters.end_date:
                date_query = {}
                if filters.start_date:
                    date_query["$gte"] = filters.start_date
                if filters.end_date:
                    date_query["$lte"] = filters.end_date
                query["created_at"] = date_query
            
            if filters.search:
                # Search in alert_id or tourist names (requires lookup)
                query["$or"] = [
                    {"alert_id": {"$regex": filters.search, "$options": "i"}},
                    {"description": {"$regex": filters.search, "$options": "i"}}
                ]
            
            # Execute query with pagination, sorted by creation time (newest first)
            cursor = alerts_collection.find(query).sort("created_at", -1).skip(filters.skip).limit(filters.limit)
            alerts_data = await cursor.to_list(length=filters.limit)
            
            # Convert to response format with tourist names
            alerts_response = []
            for alert_data in alerts_data:
                alert = Alert(**alert_data)
                
                # Get tourist name
                tourist = await tourists_collection.find_one({"_id": alert.tourist_id})
                tourist_name = tourist["full_name"] if tourist else "Unknown Tourist"
                
                alert_response = AlertResponse(
                    id=str(alert.id),
                    alert_id=alert.alert_id,
                    tourist_name=tourist_name,
                    tourist_id=str(alert.tourist_id),
                    alert_type=alert.alert_type,
                    severity=alert.severity,
                    status=alert.status,
                    location=alert.location,
                    description=alert.description,
                    timestamp=alert.created_at,
                    resolved_at=alert.resolved_at,
                    response_actions=alert.response_actions
                )
                
                alerts_response.append(alert_response)
            
            return alerts_response
            
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            raise
    
    @staticmethod
    async def get_alert_by_id(alert_id: str) -> Optional[Alert]:
        """Get alert by ID"""
        try:
            alerts_collection = await get_alerts_collection()
            alert_data = await alerts_collection.find_one({"_id": ObjectId(alert_id)})
            
            if alert_data:
                return Alert(**alert_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching alert {alert_id}: {e}")
            return None
    
    @staticmethod
    async def update_alert_status(alert_id: str, status: AlertStatus, resolved_by: str = None, 
                                resolution_notes: str = None) -> bool:
        """Update alert status"""
        try:
            alerts_collection = await get_alerts_collection()
            
            update_data = {
                "status": status.value,
                "status_updated_at": datetime.utcnow()
            }
            
            if status == AlertStatus.RESOLVED:
                update_data["resolved_at"] = datetime.utcnow()
                if resolved_by:
                    update_data["resolved_by"] = ObjectId(resolved_by)
                if resolution_notes:
                    update_data["resolution_notes"] = resolution_notes
            
            result = await alerts_collection.update_one(
                {"_id": ObjectId(alert_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated alert {alert_id} status to {status.value}")
                
                # If resolved, update tourist status back to safe
                if status == AlertStatus.RESOLVED:
                    alert = await AlertService.get_alert_by_id(alert_id)
                    if alert:
                        try:
                            from .tourist_service import TouristService
                            from ..models import TouristStatus
                        except ImportError:
                            from services.tourist_service import TouristService
                            from models import TouristStatus
                        await TouristService.update_tourist_status(
                            str(alert.tourist_id), 
                            TouristStatus.SAFE,
                            f"Alert {alert.alert_id} resolved"
                        )
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating alert status: {e}")
            return False
    
    @staticmethod
    async def add_response_action(alert_id: str, action: str, performed_by: str) -> bool:
        """Add a response action to an alert"""
        try:
            alerts_collection = await get_alerts_collection()
            
            action_entry = f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M')} - {action} (by {performed_by})"
            
            result = await alerts_collection.update_one(
                {"_id": ObjectId(alert_id)},
                {"$push": {"response_actions": action_entry}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error adding response action: {e}")
            return False
    
    @staticmethod
    async def get_active_alerts_count() -> int:
        """Get count of active alerts"""
        try:
            alerts_collection = await get_alerts_collection()
            count = await alerts_collection.count_documents({
                "status": {"$in": [AlertStatus.NEW.value, AlertStatus.IN_PROGRESS.value]}
            })
            return count
            
        except Exception as e:
            logger.error(f"Error getting active alerts count: {e}")
            return 0
    
    @staticmethod
    async def get_alerts_by_type_count(alert_type: AlertType) -> int:
        """Get count of alerts by type"""
        try:
            alerts_collection = await get_alerts_collection()
            count = await alerts_collection.count_documents({"alert_type": alert_type.value})
            return count
            
        except Exception as e:
            logger.error(f"Error getting alerts by type count: {e}")
            return 0
    
    @staticmethod
    async def get_resolved_alerts_today() -> int:
        """Get count of alerts resolved today"""
        try:
            alerts_collection = await get_alerts_collection()
            
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            count = await alerts_collection.count_documents({
                "status": AlertStatus.RESOLVED.value,
                "resolved_at": {"$gte": today_start, "$lt": today_end}
            })
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting resolved alerts count: {e}")
            return 0