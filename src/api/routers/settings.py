from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Any
from neo4j import GraphDatabase
from src.utils.config import config

router = APIRouter(prefix="/settings", tags=["settings"])

def get_db_driver():
    return GraphDatabase.driver(
        config.NEO4J_URI, 
        auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    )

class AgentConfigModel(BaseModel):
    reflection_threshold: float = 0.7
    max_retries: int = 3
    system_prompt: str = "You are a helpful AI assistant."

class ApiKeysModel(BaseModel):
    openai_api_key: Optional[str] = None
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    qdrant_api_key: Optional[str] = None

class ModelSelectionModel(BaseModel):
    llm_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    temperature: float = 0.0

class ServiceEndpointsModel(BaseModel):
    neo4j_uri: Optional[str] = None
    qdrant_url: Optional[str] = None
    langfuse_host: Optional[str] = None

class SystemSettings(BaseModel):
    agent_config: AgentConfigModel = AgentConfigModel()
    api_keys: ApiKeysModel = ApiKeysModel()
    model_selection: ModelSelectionModel = ModelSelectionModel()
    service_endpoints: ServiceEndpointsModel = ServiceEndpointsModel()

@router.get("/", response_model=SystemSettings)
async def get_settings():
    driver = get_db_driver()
    query = "MATCH (s:SystemSettings {id: 'global'}) RETURN s"
    
    try:
        with driver.session() as session:
            result = session.run(query).single()
            if result:
                node = result["s"]
                # Neo4j stores flat properties, we need to restructure
                props = dict(node)
                
                return SystemSettings(
                    agent_config=AgentConfigModel(
                        reflection_threshold=props.get("agent_config_reflection_threshold", 0.7),
                        max_retries=props.get("agent_config_max_retries", 3),
                        system_prompt=props.get("agent_config_system_prompt", "You are a helpful AI assistant.")
                    ),
                    api_keys=ApiKeysModel(
                        openai_api_key=props.get("api_keys_openai_api_key"),
                        langfuse_public_key=props.get("api_keys_langfuse_public_key"),
                        langfuse_secret_key=props.get("api_keys_langfuse_secret_key"),
                        qdrant_api_key=props.get("api_keys_qdrant_api_key")
                    ),
                    model_selection=ModelSelectionModel(
                        llm_model=props.get("model_selection_llm_model", "gpt-4o"),
                        embedding_model=props.get("model_selection_embedding_model", "text-embedding-3-small"),
                        temperature=props.get("model_selection_temperature", 0.0)
                    ),
                    service_endpoints=ServiceEndpointsModel(
                        neo4j_uri=props.get("service_endpoints_neo4j_uri"),
                        qdrant_url=props.get("service_endpoints_qdrant_url"),
                        service_endpoints_langfuse_host=props.get("service_endpoints_langfuse_host")
                    )
                )
            else:
                return SystemSettings() # Default
                
    except Exception as e:
        print(f"Error fetching settings: {e}")
        return SystemSettings()
    finally:
        driver.close()

@router.put("/", response_model=SystemSettings)
async def update_settings(settings: SystemSettings):
    driver = get_db_driver()
    
    # Flatten for Neo4j
    props = {
        "id": "global",
        "agent_config_reflection_threshold": settings.agent_config.reflection_threshold,
        "agent_config_max_retries": settings.agent_config.max_retries,
        "agent_config_system_prompt": settings.agent_config.system_prompt,
        
        "api_keys_openai_api_key": settings.api_keys.openai_api_key,
        "api_keys_langfuse_public_key": settings.api_keys.langfuse_public_key,
        "api_keys_langfuse_secret_key": settings.api_keys.langfuse_secret_key,
        "api_keys_qdrant_api_key": settings.api_keys.qdrant_api_key,
        
        "model_selection_llm_model": settings.model_selection.llm_model,
        "model_selection_embedding_model": settings.model_selection.embedding_model,
        "model_selection_temperature": settings.model_selection.temperature,
        
        "service_endpoints_neo4j_uri": settings.service_endpoints.neo4j_uri,
        "service_endpoints_qdrant_url": settings.service_endpoints.qdrant_url,
        "service_endpoints_langfuse_host": settings.service_endpoints.langfuse_host,
    }
    
    query = """
    MERGE (s:SystemSettings {id: 'global'})
    SET s += $props
    RETURN s
    """
    
    try:
        with driver.session() as session:
            session.run(query, props=props)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.close()
