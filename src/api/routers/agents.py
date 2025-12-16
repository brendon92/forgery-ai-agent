from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from neo4j import GraphDatabase
from src.utils.config import config
from src.services.agent_seeder import seed_default_agents

router = APIRouter(prefix="/agents", tags=["agents"])

# Ensure default agents exist on startup (lazy init or manual trigger could be better, 
# but for now we do it on import/first usage logic if needed, 
# or simpler: just expose an endpoint or rely on main startup.
# Let's assume main.py might call seed, but we can also trigger here for safety/dev.)
# seed_default_agents() # Commented out to avoid side effects on import, better placed in startup event.

class AgentCreate(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str] = []
    enabled: bool = True

class AgentResponse(AgentCreate):
    id: str

def get_db_driver():
    return GraphDatabase.driver(
        config.NEO4J_URI, 
        auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    )

@router.post("/seed")
async def trigger_seed():
    """Manually trigger default agent seeding."""
    seed_default_agents()
    return {"status": "seeded"}

@router.get("/", response_model=List[AgentResponse])
async def list_agents():
    driver = get_db_driver()
    try:
        query = "MATCH (a:Agent) RETURN a"
        with driver.session() as session:
            result = session.run(query)
            agents = []
            for record in result:
                node = record["a"]
                agents.append(AgentResponse(
                    id=node.get("id"),
                    name=node.get("name"),
                    role=node.get("role"),
                    goal=node.get("goal"),
                    backstory=node.get("backstory"),
                    tools=node.get("tools", []),
                    enabled=node.get("enabled", True)
                ))
            return agents
    except Exception as e:
        print(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.close()

@router.post("/", response_model=AgentResponse)
async def create_agent(agent: AgentCreate):
    driver = get_db_driver()
    agent_id = str(uuid.uuid4())
    try:
        query = """
        CREATE (a:Agent {
            id: $id,
            name: $name,
            role: $role,
            goal: $goal,
            backstory: $backstory,
            tools: $tools,
            enabled: $enabled,
            created_at: timestamp()
        })
        RETURN a
        """
        with driver.session() as session:
            result = session.run(query, 
                id=agent_id, 
                name=agent.name, 
                role=agent.role, 
                goal=agent.goal, 
                backstory=agent.backstory, 
                tools=agent.tools,
                enabled=agent.enabled
            )
            # In a real app check if created
            return AgentResponse(id=agent_id, **agent.dict())
    except Exception as e:
        print(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.close()

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent: AgentCreate):
    driver = get_db_driver()
    try:
        query = """
        MATCH (a:Agent {id: $id})
        SET a.name = $name,
            a.role = $role,
            a.goal = $goal,
            a.backstory = $backstory,
            a.tools = $tools,
            a.enabled = $enabled
        RETURN a
        """
        with driver.session() as session:
            result = session.run(query,
                id=agent_id,
                name=agent.name,
                role=agent.role,
                goal=agent.goal,
                backstory=agent.backstory,
                tools=agent.tools,
                enabled=agent.enabled
            )
            if result.peek() is None:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            return AgentResponse(id=agent_id, **agent.dict())
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error updating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.close()

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    driver = get_db_driver()
    try:
        query = "MATCH (a:Agent {id: $id}) DELETE a"
        with driver.session() as session:
            session.run(query, id=agent_id)
        return {"status": "success"}
    except Exception as e:
        print(f"Error deleting agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.close()
