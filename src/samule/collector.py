import os
from langfuse import Langfuse
from src.utils.config import config
from typing import List, Dict, Any

class DataCollector:
    def __init__(self):
        self.langfuse = Langfuse(
            public_key=config.LANGFUSE_PUBLIC_KEY,
            secret_key=config.LANGFUSE_SECRET_KEY,
            host=config.LANGFUSE_HOST
        )

    def fetch_traces(self, limit: int = 50) -> List[Any]:
        """
        Fetch recent traces from Langfuse.
        """
        print(f"Fetching last {limit} traces from Langfuse...")
        # Note: The Langfuse Python SDK might have different methods for fetching traces
        # depending on the version. This is a generalized implementation.
        # In a real scenario, we might need to use the API directly if the SDK 
        # is primarily for ingestion.
        
        # For now, we'll assume we can use the API client or a mock
        # Since the SDK is mostly for logging, we might need to use `requests` to hit the API
        # if the SDK doesn't expose a `get_traces` method.
        
        # Let's use a direct API call pattern for robustness
        import requests
        
        auth = (config.LANGFUSE_PUBLIC_KEY, config.LANGFUSE_SECRET_KEY)
        url = f"{config.LANGFUSE_HOST}/api/public/traces?limit={limit}"
        
        try:
            response = requests.get(url, auth=auth)
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                print(f"Failed to fetch traces: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error fetching traces: {e}")
            return []

collector = DataCollector()
