from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.agent.graph import app as agent_app
from langchain_core.messages import HumanMessage
import json
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager
from src.services.health_monitor import health_monitor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start Health Monitor
    await health_monitor.start()
    yield
    # Shutdown: Stop Health Monitor
    await health_monitor.stop()

app = FastAPI(title="Forgery Agent API", lifespan=lifespan)

from src.api.routers import workspaces
app.include_router(workspaces.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Connection Manager ---
class ConnectionManager:
    def __init__(self):
        # Map client_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected via WebSocket.")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected.")

    async def broadcast_event(self, event_type: str, data: dict):
        """Broadcasts an event to all connected clients."""
        payload = json.dumps({"type": event_type, "data": data})
        for client_id, connection in list(self.active_connections.items()):
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.error(f"Failed to send to {client_id}: {e}")
                self.disconnect(client_id)

manager = ConnectionManager()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.websocket("/ws/events/{client_id}")
async def event_socket_endpoint(websocket: WebSocket, client_id: str):
    """
    Dedicated endpoint for system-wide events: logs, graph updates, health ticks.
    """
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive, listen for ping/pong if active
            # For now, we just wait. Client usually listens.
            data = await websocket.receive_text()
            # Optional: Handle client-side control messages here
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Event socket error: {e}")
        manager.disconnect(client_id)

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_input = message_data.get("message")
            
            if not user_input:
                continue
                
            logger.info(f"Received message: {user_input}")
            
            # Broadcast log event
            await manager.broadcast_event("log", {"level": "INFO", "message": f"User Input: {user_input}"})
            
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "reflection_score": 0.0,
                "retry_count": 0
            }
            
            # Initialize Langfuse Handler
            from langfuse.callback import CallbackHandler
            langfuse_handler = CallbackHandler()

            # Stream events from the graph
            async for output in agent_app.astream(initial_state, config={"callbacks": [langfuse_handler]}):
                for node_name, node_state in output.items():
                    # Send update to chat client
                    response = {
                        "type": "update",
                        "node": node_name,
                        "data": str(node_state)
                    }
                    await websocket.send_text(json.dumps(response))
                    
                    # Also broadcast graph_update to event stream for visualization
                    await manager.broadcast_event("graph_update", {
                        "node": node_name,
                        "status": "completed" # granularity can be improved with custom callbacks
                    })
            
            # Send completion message
            await websocket.send_text(json.dumps({"type": "complete"}))
            
    except WebSocketDisconnect:
        logger.info("Chat Client disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
        await websocket.close()
