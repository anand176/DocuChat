"""Solution Agent configuration"""
import google.genai.types as genai_types
from src.agents1.sub_agents.solution import prompt, tools
from src.core.config import config
from google.adk.agents import Agent

solution_agent = Agent(
    name="solution_agent",
    model=config.agents.get_model_for_agent("solution_agent"),
    description="The solution agent analyzes root causes and provides actionable solutions for detected anomalies.",
    instruction=prompt.INSTRUCTION,
    tools=[
        tools.analyze_root_cause,
        tools.generate_solution,
        tools.search_similar_issues,
    ],
    generate_content_config=genai_types.GenerateContentConfig(
        temperature=0.3,
        http_options=genai_types.HttpOptions(
            retry_options=genai_types.HttpRetryOptions(
                initial_delay=1.0, attempts=2, max_delay=5.0
            )
        ),
    ),
)
