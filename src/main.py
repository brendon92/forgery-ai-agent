import asyncio
from src.agent.graph import app
from langchain_core.messages import HumanMessage

async def main():
    print("Starting Forgery Agent...")
    
    initial_state = {
        "messages": [HumanMessage(content="Research the latest trends in AI agents.")],
        "next_step": "start",
        "reflection_score": 0.0,
        "retry_count": 0
    }
    
    # Run the graph
    async for output in app.astream(initial_state):
        for key, value in output.items():
            print(f"Node '{key}':")
            print(value)
            print("---")

if __name__ == "__main__":
    asyncio.run(main())
