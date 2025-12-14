from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from src.utils.config import config

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", api_key=config.OPENAI_API_KEY)

class ResearchCrew:
    def __init__(self):
        self.researcher = Agent(
            role='Senior Researcher',
            goal='Uncover groundbreaking technologies in AI',
            backstory="""You are a veteran researcher with a knack for finding 
            hidden gems in academic papers and GitHub repositories.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        self.analyst = Agent(
            role='Reporting Analyst',
            goal='Synthesize research into a comprehensive report',
            backstory="""You are an expert at summarizing complex technical 
            topics into concise, actionable executive reports.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

    def run(self, topic: str):
        # Define Tasks
        task1 = Task(
            description=f"Conduct a comprehensive search on: {topic}. Identify key trends, players, and technologies.",
            agent=self.researcher,
            expected_output="A detailed list of findings with citations."
        )
        
        task2 = Task(
            description=f"Using the research findings, write a strategic executive summary on {topic}.",
            agent=self.analyst,
            expected_output="A markdown-formatted executive report.",
            context=[task1] # Dependency
        )
        
        # Instantiate Crew
        crew = Crew(
            agents=[self.researcher, self.analyst],
            tasks=[task1, task2],
            verbose=True,
            process=Process.sequential
        )
        
        # execution
        result = crew.kickoff()
        return result

# Example usage
# research_crew = ResearchCrew()
# report = research_crew.run("Autonomous AI Agents 2025")
