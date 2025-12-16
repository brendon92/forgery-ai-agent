from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from src.utils.config import config
from neo4j import GraphDatabase
import logging

logger = logging.getLogger(__name__)

class ModelFactory:
    @staticmethod
    def get_model(model_type: str = "smart"):
        """
        Returns a Chat model instance based on the logical model type.
        Prioritizes Global Settings from Neo4j, falls back to Config.
        """
        
        # 1. Fetch Global Settings to see if there's a default override for "smart" or "fast"
        # For simplicity, we mapped "model_selection_llm_model" in Settings, which acts as the default "smart" model.
        # If model_type is 'fast' or 'reflector', we might still look up config or specific settings.
        # For now, let's implement a robust lookup.
        
        driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD))
        
        target_model_name = config.MODEL_CONFIG.get(model_type, config.MODEL_CONFIG["smart"])
        
        try:
            with driver.session() as session:
                # Get Global Settings
                settings_query = "MATCH (s:SystemSettings {id: 'global'}) RETURN s"
                result = session.run(settings_query).single()
                if result:
                    props = dict(result["s"])
                    # If the request is for the main "smart" model, use the global default
                    if model_type == "smart":
                         target_model_name = props.get("model_selection_llm_model", target_model_name)
                    
                # Now resolve the physical model details from Model Registry
                model_query = "MATCH (m:Model {name: $name}) RETURN m"
                model_result = session.run(model_query, name=target_model_name).single()
                
                if model_result:
                     m_node = model_result["m"]
                     provider = m_node.get("provider", "openai")
                     base_url = m_node.get("base_url") 
                     # api_key = m_node.get("api_key") # If stored
                     
                     if provider == "openai":
                         return ChatOpenAI(model=target_model_name, api_key=config.OPENAI_API_KEY)
                     elif provider == "ollama":
                         return ChatOllama(
                            model=target_model_name,
                            base_url=base_url or config.OLLAMA_BASE_URL,
                            temperature=0.1
                         )
        except Exception as e:
            logger.error(f"ModelFactory Error: {e}")
            # Fallback to config
            pass
        finally:
            driver.close()

        # Fallback implementation if DB fails
        if "gpt" in target_model_name:
            return ChatOpenAI(model=target_model_name, api_key=config.OPENAI_API_KEY)
        else:
            return ChatOllama(
                model=target_model_name,
                base_url=config.OLLAMA_BASE_URL,
                temperature=0.1
            )
