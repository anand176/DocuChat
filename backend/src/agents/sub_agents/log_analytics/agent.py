"""Log Analytics Agent configuration"""
import google.genai.types as genai_types
from agents.sub_agents.log_analytics import prompt, tools
from core.config import config
from google.adk.agents import Agent

log_analytics_agent = Agent(
    name="log_analytics_agent",
    model=config.agents.get_model_for_agent("log_analytics_agent") or "gemini-1.5-flash",
    description="The log analytics agent fetches and analyzes logs for anomalies in a single step.",
    instruction=prompt.INSTRUCTION,
    tools=[
        tools.fetch_and_analyze_logs,
    ],
    generate_content_config=genai_types.GenerateContentConfig(
        temperature=0.1,
    ),
)
