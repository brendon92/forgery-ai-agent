import requests
import uuid
import sys
import os

# Adjust path to find src if needed, or just rely on requests to localhost
BASE_URL = "http://localhost:8000"

def test_agents_crud():
    print("Testing Agent CRUD Operations...")
    
    # 1. Create Agent
    agent_data = {
        "name": f"Test Agent {uuid.uuid4()}",
        "role": "Tester",
        "goal": "Verify persistence",
        "backstory": "Created by automated test",
        "tools": ["test_tool"],
        "enabled": True
    }
    
    print(f"Creating agent: {agent_data['name']}...")
    try:
        res = requests.post(f"{BASE_URL}/agents/", json=agent_data)
        if res.status_code != 200:
            print(f"FAILED to create agent: {res.text}")
            return False
    except Exception as e:
        print(f"Connection failed (Server up?): {e}")
        return False
        
    created_agent = res.json()
    agent_id = created_agent["id"]
    print(f"SUCCESS: Created agent {agent_id}")
    
    # 2. List Agents
    print("Listing agents...")
    res = requests.get(f"{BASE_URL}/agents/")
    agents = res.json()
    
    found = False
    for a in agents:
        if a["id"] == agent_id:
            found = True
            break
    
    if found:
        print("SUCCESS: Found created agent in list.")
    else:
        print("FAILED: Agent not found in list.")
        return False
        
    # 3. Delete Agent
    print(f"Deleting agent {agent_id}...")
    requests.delete(f"{BASE_URL}/agents/{agent_id}")
    
    # 4. Verify Deletion
    res = requests.get(f"{BASE_URL}/agents/")
    agents = res.json()
    found_after = False
    for a in agents:
        if a["id"] == agent_id:
            found_after = True
            break
            
    if not found_after:
        print("SUCCESS: Agent deleted successfully.")
    else:
        print("FAILED: Agent still exists after deletion.")
        return False
        
    print("ALL TESTS PASSED.")
    return True

if __name__ == "__main__":
    if not test_agents_crud():
        sys.exit(1)
