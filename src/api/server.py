from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.agent.graph import app as agent_app
from langchain_core.messages import HumanMessage
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Forgery Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

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
            
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "next_step": "start",
                "reflection_score": 0.0,
                "retry_count": 0
            }
            
            # Stream events from the graph
            async for output in agent_app.astream(initial_state):
                for node_name, node_state in output.items():
                    # Send update to client
                    response = {
                        "type": "update",
                        "node": node_name,
                        "data": str(node_state) # Serialize state for now
                    }
                    await websocket.send_text(json.dumps(response))
            
            # Send completion message
            await websocket.send_text(json.dumps({"type": "complete"}))
            
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
        await websocket.close()
