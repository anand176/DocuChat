"""Log Retrieve Agent configuration"""
import google.genai.types as genai_types
from src.agents1.sub_agents.log_retrieve import prompt, tools
from src.core.config import config
from google.adk.agents import Agent

log_retrieve_agent = Agent(
    name="log_retrieve_agent",
    model=config.agents.get_model_for_agent("log_retrieve_agent"),
    description="The log retrieve agent fetches logs from Loki based on time ranges and patterns.",
    instruction=prompt.INSTRUCTION,
    tools=[
        tools.fetch_logs_from_loki,
        tools.get_log_summary,
        tools.search_logs_by_pattern,
    ],
    generate_content_config=genai_types.GenerateContentConfig(
        temperature=0.1,
        http_options=genai_types.HttpOptions(
            retry_options=genai_types.HttpRetryOptions(
                initial_delay=1.0, attempts=2, max_delay=5.0
            )
        ),
    ),
)
