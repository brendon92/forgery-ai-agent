import asyncio
import logging
import psutil
from typing import Dict, Any
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from src.utils.config import config

logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self):
        self.is_running = False
        self.manager = None
        
    async def start(self, connection_manager: Any):
        self.is_running = True
        self.manager = connection_manager
        logger.info("Health Monitor started.")
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop(self):
        self.is_running = False
        logger.info("Health Monitor stopped.")

    async def _monitor_loop(self):
        while self.is_running:
            try:
                # 1. Check Neo4j
                neo4j_status = "error"
                try:
                    driver = GraphDatabase.driver(
                        config.NEO4J_URI, 
                        auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
                    )
                    driver.verify_connectivity()
                    neo4j_status = "ok"
                    driver.close()
                except Exception as e:
                    logger.error(f"Neo4j health check failed: {e}")
                    neo4j_status = "error"

                # 2. Check Qdrant
                qdrant_status = "error"
                try:
                    client = QdrantClient(
                        url=config.QDRANT_URL,
                        api_key=config.QDRANT_API_KEY,
                        timeout=5
                    )
                    client.get_collections()
                    qdrant_status = "ok"
                except Exception as e:
                    logger.error(f"Qdrant health check failed: {e}")
                    qdrant_status = "error"

                # 3. Check System
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
                
                # Broadcast 'health_tick' event if manager is available
                if self.manager:
                    await self.manager.broadcast_event("health_tick", health_data)
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
            
            await asyncio.sleep(5)  # Update every 5 seconds

health_monitor = HealthMonitor()
