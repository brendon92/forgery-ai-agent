import os
import requests
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
        Fetch recent traces from Langfuse API.
        """
        print(f"Fetching last {limit} traces from Langfuse...")
        
        auth = (config.LANGFUSE_PUBLIC_KEY, config.LANGFUSE_SECRET_KEY)
        url = f"{config.LANGFUSE_HOST}/api/public/traces?limit={limit}"
        
        try:
            response = requests.get(url, auth=auth, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                print(f"Successfully fetched {len(data)} traces.")
                return data
            else:
                print(f"Failed to fetch traces: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error fetching traces: {e}")
            return []

collector = DataCollector()
