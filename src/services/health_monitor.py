import asyncio
import logging
from typing import Dict
from src.api.server import manager

logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self):
        self.is_running = False
        
    async def start(self):
        self.is_running = True
        logger.info("Health Monitor started.")
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop(self):
        self.is_running = False
        logger.info("Health Monitor stopped.")

    async def _monitor_loop(self):
        while self.is_running:
            try:
                # 1. Check Neo4j (Mock check for now, can perform actual query)
                neo4j_status = "ok" 
                
                # 2. Check Qdrant
                qdrant_status = "ok"

                # 3. Check System
                import psutil
                cpu_usage = psutil.cpu_percent()
                memory_usage = psutil.virtual_memory().percent

                health_data = {
                    "neo4j": {"status": neo4j_status},
                    "qdrant": {"status": qdrant_status},
                    "system": {
                        "cpu": cpu_usage,
                        "memory": memory_usage
                    }
                }
                
                # Broadcast 'health_tick' event
                await manager.broadcast_event("health_tick", health_data)
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
            
            await asyncio.sleep(5)  # Update every 5 seconds

health_monitor = HealthMonitor()
