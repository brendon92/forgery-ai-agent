from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes import agent_node, reflection_node, tool_node, should_continue

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
workflow.add_edge("reflect", "agent") # Loop back for refinement

# Conditional edges
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "end": END,
        "reflect": "reflect"
    }
)

# Compile the graph
app = workflow.compile()
