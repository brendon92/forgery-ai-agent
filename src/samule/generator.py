from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.utils.config import config
from typing import Dict, Any

class SyntheticGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", api_key=config.OPENAI_API_KEY)

    def generate_correction(self, failure_trace: Dict[str, Any]) -> str:
        """
        Generate a corrected response for a failed trace.
        """
        # Extract the original input and the failed output from the trace
        # This is a simplification
        original_input = "Research AI Agents" # Mock extraction
        failed_output = "AI Agents are cool." # Mock extraction
        critique = "Too simple, lacks depth." # Mock extraction
        
        prompt = f"""
        Original Input: {original_input}
        Failed Output: {failed_output}
        Critique: {critique}
        
        Task: Generate a superior response that addresses the critique and satisfies the original input.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    def create_sft_example(self, failure_trace: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a training example (Input, Output) for SFT.
        """
        correction = self.generate_correction(failure_trace)
        return {
            "input": "Research AI Agents", # Should be extracted from trace
            "output": correction
        }

generator = SyntheticGenerator()
