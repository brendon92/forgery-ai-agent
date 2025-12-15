from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid

router = APIRouter(prefix="/agents", tags=["agents"])

# In-memory storage for agents (replace with DB)
agents_db: Dict[str, Dict] = {}

class AgentCreate(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str] = []
    enabled: bool = True

class AgentResponse(AgentCreate):
    id: str

@router.get("/", response_model=List[AgentResponse])
async def list_agents():
    return list(agents_db.values())

@router.post("/", response_model=AgentResponse)
async def create_agent(agent: AgentCreate):
    agent_id = str(uuid.uuid4())
    new_agent = agent.dict()
    new_agent["id"] = agent_id
    agents_db[agent_id] = new_agent
    return new_agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent: AgentCreate):
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    updated_agent = agent.dict()
    updated_agent["id"] = agent_id
    agents_db[agent_id] = updated_agent
    return updated_agent

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    del agents_db[agent_id]
    return {"status": "success"}
