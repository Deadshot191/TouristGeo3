import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

try:
    from .services.anomaly_service import AnomalyDetectionService
except ImportError:
    from services.anomaly_service import AnomalyDetectionService

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manages background tasks for the tourism safety system"""
    
    def __init__(self):
        self.anomaly_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    async def start_background_tasks(self):
        """Start all background tasks"""
        if self.is_running:
            logger.warning("Background tasks are already running")
            return
        
        logger.info("Starting background tasks...")
        
        try:
            # Start anomaly detection service
            self.anomaly_task = asyncio.create_task(
                AnomalyDetectionService.run_background_anomaly_detection()
            )
            
            self.is_running = True
            logger.info("Background tasks started successfully")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
            await self.stop_background_tasks()
    
    async def stop_background_tasks(self):
        """Stop all background tasks"""
        logger.info("Stopping background tasks...")
        
        self.is_running = False
        
        # Stop anomaly detection task
        if self.anomaly_task and not self.anomaly_task.done():
            self.anomaly_task.cancel()
            try:
                await self.anomaly_task
            except asyncio.CancelledError:
                logger.info("Anomaly detection task cancelled")
        
        logger.info("Background tasks stopped")
    
    def get_task_status(self):
        """Get status of background tasks"""
        return {
            "is_running": self.is_running,
            "anomaly_detection": {
                "running": self.anomaly_task is not None and not self.anomaly_task.done(),
                "done": self.anomaly_task.done() if self.anomaly_task else False,
                "cancelled": self.anomaly_task.cancelled() if self.anomaly_task else False
            }
        }

# Global task manager instance
task_manager = BackgroundTaskManager()

@asynccontextmanager
async def lifespan(app):
    """Application lifespan manager for background tasks"""
    # Startup
    logger.info("Application startup - starting background tasks")
    await task_manager.start_background_tasks()
    
    try:
        yield
    finally:
        # Shutdown
        logger.info("Application shutdown - stopping background tasks")
        await task_manager.stop_background_tasks()