from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

try:
    from ..models import DashboardKPIs, TouristStatus, AlertStatus, SafetyScoreResponse
    from ..services.tourist_service import TouristService
    from ..services.alert_service import AlertService
    from ..database import get_tourists_collection, get_alerts_collection, get_location_history_collection
except ImportError:
    from models import DashboardKPIs, TouristStatus, AlertStatus, SafetyScoreResponse
    from services.tourist_service import TouristService
    from services.alert_service import AlertService
    from database import get_tourists_collection, get_alerts_collection, get_location_history_collection

logger = logging.getLogger(__name__)

class AnalyticsService:
    
    @staticmethod
    async def get_dashboard_kpis() -> DashboardKPIs:
        """Get dashboard KPIs"""
        try:
            # Get active tourists count
            total_active = await TouristService.get_active_tourists_count()
            
            # Get active alerts count
            active_alerts = await AlertService.get_active_alerts_count()
            
            # Get safe status count
            safe_count = await TouristService.get_tourists_by_status(TouristStatus.SAFE)
            
            # Get high risk tourists (those with safety score < 50)
            high_risk_count = await AnalyticsService.get_high_risk_tourists_count()
            
            # Get resolved alerts today
            resolved_today = await AlertService.get_resolved_alerts_today()
            
            # Get average safety score
            avg_safety_score = await AnalyticsService.get_average_safety_score()
            
            return DashboardKPIs(
                total_active_tourists=total_active,
                active_alerts=active_alerts,
                safe_status=safe_count,
                high_risk_tourists=high_risk_count,
                resolved_alerts_today=resolved_today,
                avg_safety_score=avg_safety_score
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard KPIs: {e}")
            return DashboardKPIs(
                total_active_tourists=0,
                active_alerts=0,
                safe_status=0,
                high_risk_tourists=0,
                resolved_alerts_today=0,
                avg_safety_score=0.0
            )
    
    @staticmethod
    async def get_high_risk_tourists_count() -> int:
        """Get count of high-risk tourists (safety score < 50)"""
        try:
            tourists_collection = await get_tourists_collection()
            count = await tourists_collection.count_documents({"safety_score": {"$lt": 50}})
            return count
            
        except Exception as e:
            logger.error(f"Error getting high-risk tourists count: {e}")
            return 0
    
    @staticmethod
    async def get_average_safety_score() -> float:
        """Get average safety score of all tourists"""
        try:
            tourists_collection = await get_tourists_collection()
            
            pipeline = [
                {"$group": {"_id": None, "avg_score": {"$avg": "$safety_score"}}}
            ]
            
            cursor = tourists_collection.aggregate(pipeline)
            result = await cursor.to_list(1)
            
            if result:
                return round(result[0]["avg_score"], 1)
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting average safety score: {e}")
            return 0.0
    
    @staticmethod
    async def calculate_safety_score(tourist_id: str) -> SafetyScoreResponse:
        """Calculate safety score for a tourist using AI/ML logic"""
        try:
            tourists_collection = await get_tourists_collection()
            alerts_collection = await get_alerts_collection()
            location_collection = await get_location_history_collection()
            
            from bson import ObjectId
            
            # Get tourist data
            tourist = await tourists_collection.find_one({"_id": ObjectId(tourist_id)})
            if not tourist:
                raise ValueError("Tourist not found")
            
            # Base safety score
            safety_score = 100
            risk_factors = []
            
            # Factor 1: Recent alerts (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_alerts = await alerts_collection.count_documents({
                "tourist_id": ObjectId(tourist_id),
                "created_at": {"$gte": week_ago}
            })
            
            if recent_alerts > 0:
                penalty = min(recent_alerts * 15, 40)  # Max 40 points penalty
                safety_score -= penalty
                risk_factors.append(f"Recent alerts: {recent_alerts}")
            
            # Factor 2: Current location risk (check if in high-risk geo-fence)
            latest_location = await location_collection.find_one(
                {"tourist_id": ObjectId(tourist_id)},
                sort=[("timestamp", -1)]
            )
            
            if latest_location:
                try:
                    from .geofence_service import GeofenceService
                except ImportError:
                    from geofence_service import GeofenceService
                coords = latest_location["coordinates"]["coordinates"]
                intersecting_fences = await GeofenceService.check_point_in_geofences(coords[0], coords[1])
                
                for fence in intersecting_fences:
                    if fence["risk_level"] == "high":
                        safety_score -= 20
                        risk_factors.append(f"In high-risk zone: {fence['name']}")
                    elif fence["risk_level"] == "critical":
                        safety_score -= 35
                        risk_factors.append(f"In critical zone: {fence['name']}")
            
            # Factor 3: Location update frequency (last 6 hours)
            six_hours_ago = datetime.utcnow() - timedelta(hours=6)
            recent_locations = await location_collection.count_documents({
                "tourist_id": ObjectId(tourist_id),
                "timestamp": {"$gte": six_hours_ago}
            })
            
            if recent_locations == 0:
                safety_score -= 25
                risk_factors.append("No recent location updates")
            elif recent_locations < 3:
                safety_score -= 10
                risk_factors.append("Infrequent location updates")
            
            # Factor 4: Time of day (nighttime is riskier)
            current_hour = datetime.utcnow().hour
            if 22 <= current_hour or current_hour <= 5:  # 10 PM to 5 AM
                safety_score -= 5
                risk_factors.append("Nighttime activity")
            
            # Factor 5: Tourist status
            if tourist["status"] == TouristStatus.PANIC.value:
                safety_score = min(safety_score, 25)  # Max 25 for panic status
                risk_factors.append("Panic status active")
            elif tourist["status"] == TouristStatus.ANOMALY.value:
                safety_score -= 15
                risk_factors.append("Anomaly detected")
            
            # Ensure score is between 0 and 100
            safety_score = max(0, min(100, safety_score))
            
            # Update tourist's safety score in database
            await tourists_collection.update_one(
                {"_id": ObjectId(tourist_id)},
                {"$set": {"safety_score": safety_score, "score_updated_at": datetime.utcnow()}}
            )
            
            return SafetyScoreResponse(
                tourist_id=tourist_id,
                safety_score=safety_score,
                risk_factors=risk_factors,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error calculating safety score for {tourist_id}: {e}")
            return SafetyScoreResponse(
                tourist_id=tourist_id,
                safety_score=50,  # Default safe score
                risk_factors=["Error calculating score"],
                last_updated=datetime.utcnow()
            )
    
    @staticmethod
    async def get_location_analytics(hours: int = 24) -> Dict[str, Any]:
        """Get location-based analytics"""
        try:
            location_collection = await get_location_history_collection()
            
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Most visited areas
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_time}}},
                {"$group": {
                    "_id": "$address",
                    "visit_count": {"$sum": 1},
                    "unique_tourists": {"$addToSet": "$tourist_id"}
                }},
                {"$project": {
                    "address": "$_id",
                    "visit_count": 1,
                    "unique_tourists_count": {"$size": "$unique_tourists"}
                }},
                {"$sort": {"visit_count": -1}},
                {"$limit": 10}
            ]
            
            cursor = location_collection.aggregate(pipeline)
            popular_areas = await cursor.to_list(10)
            
            # Activity by hour
            hourly_pipeline = [
                {"$match": {"timestamp": {"$gte": start_time}}},
                {"$group": {
                    "_id": {"$hour": "$timestamp"},
                    "activity_count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            cursor = location_collection.aggregate(hourly_pipeline)
            hourly_activity = await cursor.to_list(24)
            
            return {
                "popular_areas": popular_areas,
                "hourly_activity": hourly_activity,
                "period_hours": hours
            }
            
        except Exception as e:
            logger.error(f"Error getting location analytics: {e}")
            return {"popular_areas": [], "hourly_activity": [], "period_hours": hours}
    
    @staticmethod
    async def get_alert_analytics(days: int = 7) -> Dict[str, Any]:
        """Get alert-based analytics"""
        try:
            alerts_collection = await get_alerts_collection()
            
            start_time = datetime.utcnow() - timedelta(days=days)
            
            # Alerts by type
            type_pipeline = [
                {"$match": {"created_at": {"$gte": start_time}}},
                {"$group": {
                    "_id": "$alert_type",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            
            cursor = alerts_collection.aggregate(type_pipeline)
            alerts_by_type = await cursor.to_list(None)
            
            # Alerts by severity
            severity_pipeline = [
                {"$match": {"created_at": {"$gte": start_time}}},
                {"$group": {
                    "_id": "$severity",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            
            cursor = alerts_collection.aggregate(severity_pipeline)
            alerts_by_severity = await cursor.to_list(None)
            
            # Resolution time analysis
            resolution_pipeline = [
                {"$match": {
                    "created_at": {"$gte": start_time},
                    "status": "resolved",
                    "resolved_at": {"$exists": True}
                }},
                {"$project": {
                    "resolution_time_minutes": {
                        "$divide": [
                            {"$subtract": ["$resolved_at", "$created_at"]},
                            60000  # Convert to minutes
                        ]
                    }
                }},
                {"$group": {
                    "_id": None,
                    "avg_resolution_time": {"$avg": "$resolution_time_minutes"},
                    "min_resolution_time": {"$min": "$resolution_time_minutes"},
                    "max_resolution_time": {"$max": "$resolution_time_minutes"}
                }}
            ]
            
            cursor = alerts_collection.aggregate(resolution_pipeline)
            resolution_stats = await cursor.to_list(1)
            
            return {
                "alerts_by_type": alerts_by_type,
                "alerts_by_severity": alerts_by_severity,
                "resolution_stats": resolution_stats[0] if resolution_stats else None,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting alert analytics: {e}")
            return {"alerts_by_type": [], "alerts_by_severity": [], "resolution_stats": None, "period_days": days}