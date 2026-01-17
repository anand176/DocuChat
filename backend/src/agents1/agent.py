"""Root log monitoring agent configuration"""
import google.genai.types as genai_types
from src.agents1 import prompt
from src.agents1.sub_agents import (
    log_retrieve_agent,
    log_analysis_agent,
    solution_agent,
)
from src.core.config import config
from google.adk.agents import Agent
from google.adk.planners import PlanReActPlanner
from google.adk.tools.agent_tool import AgentTool

log_monitoring_agent = Agent(
    name="log_monitoring_agent",
    model=config.agents.get_model_for_agent("log_monitoring_agent"),
    description="AI agent for comprehensive log monitoring, anomaly detection, and solution generation. Coordinates specialized sub-agents to fetch logs, analyze patterns, and provide actionable solutions.",
    planner=PlanReActPlanner(),
    instruction=prompt.INSTRUCTION,
    tools=[
        AgentTool(agent=log_retrieve_agent, skip_summarization=False),
        AgentTool(agent=log_analysis_agent, skip_summarization=False),
        AgentTool(agent=solution_agent, skip_summarization=False),
    ],
    generate_content_config=genai_types.GenerateContentConfig(
        temperature=0.2,
        http_options=genai_types.HttpOptions(
            retry_options=genai_types.HttpRetryOptions(
                initial_delay=1.0, attempts=2, max_delay=5.0
            )
        ),
    ),
)
