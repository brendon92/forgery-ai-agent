from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from neo4j import GraphDatabase
from src.utils.config import config
import uuid

router = APIRouter(prefix="/models", tags=["models"])

def get_db_driver():
    return GraphDatabase.driver(
        config.NEO4J_URI, 
        auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    )

class Model(BaseModel):
    id: Optional[str] = None
    name: str # e.g. "gpt-4o"
    provider: str # "openai", "ollama", "anthropic"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    context_window: int = 128000

@router.get("/", response_model=List[Model])
async def list_models():
    driver = get_db_driver()
    query = "MATCH (m:Model) RETURN m"
    try:
        with driver.session() as session:
            results = session.run(query)
            models = []
            for record in results:
                node = record["m"]
                models.append(Model(
                    id=node.get("id"),
                    name=node.get("name"),
                    provider=node.get("provider"),
                    base_url=node.get("base_url"),
                    api_key=node.get("api_key"), # Be careful returning this in prod
                    context_window=node.get("context_window", 128000)
                ))
            
            # If empty, seed default models
            if not models:
                await seed_default_models()
                return await list_models() # Recurse once
                
            return models
    except Exception as e:
        print(f"Error listing models: {e}")
        return []
    finally:
        driver.close()

@router.post("/", response_model=Model)
async def create_model(model: Model):
    driver = get_db_driver()
    model_id = str(uuid.uuid4())
    model.id = model_id
    
    query = """
    CREATE (m:Model {
        id: $id,
        name: $name,
        provider: $provider,
        base_url: $base_url,
        api_key: $api_key,
        context_window: $context_window
    })
    RETURN m
    """
    
    try:
        with driver.session() as session:
            session.run(query, 
                id=model.id,
                name=model.name,
                provider=model.provider,
                base_url=model.base_url,
                api_key=model.api_key,
                context_window=model.context_window
            )
        return model
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.close()

@router.put("/{model_id}", response_model=Model)
async def update_model(model_id: str, model: Model):
    driver = get_db_driver()
    query = """
    MATCH (m:Model {id: $id})
    SET m.name = $name,
        m.provider = $provider,
        m.base_url = $base_url,
        m.api_key = $api_key,
        m.context_window = $context_window
    RETURN m
    """
    try:
        with driver.session() as session:
            result = session.run(query, 
                id=model_id,
                name=model.name,
                provider=model.provider,
                base_url=model.base_url,
                api_key=model.api_key,
                context_window=model.context_window
            ).single()
            
            if not result:
                raise HTTPException(status_code=404, detail="Model not found")
                
            return model
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.close()

@router.delete("/{model_id}")
async def delete_model(model_id: str):
    driver = get_db_driver()
    query = "MATCH (m:Model {id: $id}) DETACH DELETE m"
    try:
        with driver.session() as session:
            session.run(query, id=model_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.close()

async def seed_default_models():
    """Seeds defaults from config.MODEL_CONFIG or standard list if DB is empty."""
    defaults = [
        Model(name="gpt-4o", provider="openai", context_window=128000),
        Model(name="qwen2.5:1.5b", provider="ollama", base_url=config.OLLAMA_BASE_URL, context_window=32000),
        Model(name="llama3.2", provider="ollama", base_url=config.OLLAMA_BASE_URL, context_window=128000),
    ]
    
    for m in defaults:
        await create_model(m)
