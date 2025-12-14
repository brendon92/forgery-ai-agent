from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes import agent_node, ReflectionNode, tool_node

# Instantiate class-based nodes
reflection_node = ReflectionNode()

def should_continue(state: AgentState):
    """
    Router logic based on reflection score and retry count.
    """
    score = state.get('reflection_score', 0.0)
    retries = state.get('retry_count', 0)
    
    if score >= 0.8:
        return "end"
    if retries >= 3: # Max 3 retries (total 4 attempts)
        return "end" # Or redirect to a 'failure' node
    return "reflect"

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", agent_node)
workflow.add_node("reflect", reflection_node)
workflow.add_node("tools", tool_node)

# Set entry point
workflow.set_entry_point("agent")

# Add edges
workflow.add_edge("tools", "agent")

# Conditional edges
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "end": END,
        "reflect": "reflect"
    }
)

# Loop back from reflection to agent (Refinement Loop)
# In a real implementation, we might want a specific 'refine' node that
# takes the critique and modifies the original query
workflow.add_edge("reflect", "agent")

# Compile the graph
app = workflow.compile()
