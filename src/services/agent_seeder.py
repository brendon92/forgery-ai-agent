from neo4j import GraphDatabase
import logging
from src.utils.config import config
import uuid

logger = logging.getLogger(__name__)

DEFAULT_AGENTS = [
    {
        "name": "Executive Coordinator",
        "role": "Coordinator",
        "goal": "Orchestrate complex tasks by delegating to specialized agents and ensuring final output quality.",
        "backstory": "You are the primary interface for the user. your job is to understand the request, break it down, and assign it to the correct specialist. You are responsible for the final answer.",
        "tools": []
    },
    {
        "name": "Financial Analyst",
        "role": "Analyst",
        "goal": "Analyze financial data, tax documents, and provide accurate numerical insights.",
        "backstory": "You are a seasoned CPA and financial data analyst. You are meticulous, detail-oriented, and tailored for quantitative reasoning. You never hallucinate numbers.",
        "tools": ["search_web"] # Placeholder
    },
    {
        "name": "Web Researcher",
        "role": "Researcher",
        "goal": "Gather up-to-date information from the internet to answer specific questions.",
        "backstory": "You are an expert researcher capable of using search engines and navigating web content to find the most relevant and recent information.",
        "tools": ["search_web"]
    }
]

class AgentSeeder:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )

    def seed(self):
        """
        Ensures default agents exist in the database.
        """
        with self.driver.session() as session:
            for agent in DEFAULT_AGENTS:
                session.execute_write(self._create_agent_if_not_exists, agent)
                
    def _create_agent_if_not_exists(self, tx, agent_data):
        query = """
        MERGE (a:Agent {name: $name})
        ON CREATE SET 
            a.id = $id,
            a.role = $role,
            a.goal = $goal,
            a.backstory = $backstory,
            a.tools = $tools,
            a.enabled = true,
            a.created_at = timestamp()
        RETURN a
        """
        tx.run(query, 
               name=agent_data["name"],
               id=str(uuid.uuid4()),
               role=agent_data["role"],
               goal=agent_data["goal"],
               backstory=agent_data["backstory"],
               tools=agent_data["tools"]
        )
        logger.info(f"Seeding check for agent: {agent_data['name']}")

    def close(self):
        self.driver.close()

def seed_default_agents():
    seeder = AgentSeeder()
    try:
        seeder.seed()
        logger.info("Default agents seeded successfully.")
    except Exception as e:
        logger.error(f"Failed to seed agents: {e}")
    finally:
        seeder.close()
