import pytest
from unittest.mock import MagicMock, patch
from src.agent.graph import app
from langchain_core.messages import HumanMessage, AIMessage

@pytest.mark.asyncio
async def test_agent_flow():
    # Mock the LLM to avoid API calls
    with patch("src.agent.nodes.llm") as mock_llm:
        # Define mock responses
        # 1. Agent generates response
        # 2. Reflector critiques (score 0.9 -> end)
        
        mock_llm.invoke.side_effect = [
            AIMessage(content="Agent Response 1"), # Agent (Pass 1)
            AIMessage(content="0.9"),            # Reflector
            AIMessage(content="Agent Response 2")  # Agent (Pass 2 - Final)
        ]
        
        initial_state = {
            "messages": [HumanMessage(content="Test Input")],
            "next_step": "start",
            "reflection_score": 0.0,
            "retry_count": 0
        }
        
        # Run the graph
        results = []
        async for output in app.astream(initial_state):
            results.append(output)
            
        # Verify flow
        # Expected sequence: agent -> reflect -> agent
        assert len(results) == 3
        assert "agent" in results[0]
        assert "reflect" in results[1]
        assert "agent" in results[2]
        
        # Verify state updates in the reflection step
        reflection_step = results[1]["reflect"]
        assert reflection_step["reflection_score"] == 0.9
