import pytest
from unittest.mock import MagicMock, patch
from src.agent.nodes import ReflectionNode
from src.agent.state import AgentState
from langchain_core.messages import AIMessage, HumanMessage

@pytest.fixture
def reflection_node():
    return ReflectionNode()

def test_reflection_node_call_success(reflection_node):
    # Mock LLM response
    mock_llm_response = AIMessage(content='{"score": 0.9, "reason": "Excellent response"}')
    
    with patch('src.agent.nodes.llm.invoke', return_value=mock_llm_response):
        state = {
            "messages": [
                HumanMessage(content="What is AI?"),
                AIMessage(content="AI stands for Artificial Intelligence.")
            ],
            "retry_count": 0
        }
        
        result = reflection_node(state)
        
        assert result["reflection_score"] == 0.9
        assert result["retry_count"] == 1

def test_reflection_node_call_json_error(reflection_node):
    # Mock invalid JSON response
    mock_llm_response = AIMessage(content='Invalid JSON output')
    
    with patch('src.agent.nodes.llm.invoke', return_value=mock_llm_response):
        state = {
            "messages": [HumanMessage(content="Test"), AIMessage(content="Response")],
            "retry_count": 0
        }
        
        result = reflection_node(state)
        
        # Should fallback to default error handling
        assert result["reflection_score"] == 0.5
        assert result["retry_count"] == 1
