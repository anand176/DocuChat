from .adk_agents import manager_agent
from google.adk.runners.runner import Runner
import asyncio

class AgentOrchestrator:
    def __init__(self):
        self.runner = Runner(manager_agent)

    async def handle_query(self, query, chat_history=None):
        """Executes the query using the ADK Runner and the Manager Agent team."""
        # ADK's Runner.run is async
        response = await self.runner.run(query)
        # Assuming the response object has a text attribute or similar
        # Based on research, the result can be accessed directly or via properties
        return str(response)

    async def handle_query_stream(self, query, chat_history=None):
        """Steams the agent's thoughts and final response using the ADK Runner."""
        # For a basic stream that returns the final result as a chunk
        response = await self.runner.run(query)
        yield str(response)
