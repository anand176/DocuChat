"""Log Analysis Agent configuration"""
import google.genai.types as genai_types
from src.agents1.sub_agents.log_analysis import prompt, tools
from src.core.config import config
from google.adk.agents import Agent

log_analysis_agent = Agent(
    name="log_analysis_agent",
    model=config.agents.get_model_for_agent("log_analysis_agent"),
    description="The log analysis agent analyzes logs to detect anomalies and generate summaries.",
    instruction=prompt.INSTRUCTION,
    tools=[
        tools.detect_anomalies,
        tools.generate_log_summary,
        tools.classify_log_severity,
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
