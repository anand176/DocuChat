from google.adk.agents.llm_agent import Agent
from .docker_tools import DockerTools
from src.vector_store import query_vectors
import json
import os

# Initialize tools
docker_tools = DockerTools()

# 1. Inspector Agent
# Monitors container status
inspector_agent = Agent(
    model='gemini-1.5-flash',
    name='inspector',
    description="Specialist in monitoring Docker container status, names, and states.",
    instruction="""You are the Inspector Agent. Use the list_containers tool to see which containers are currently on the host.
    Provide concise summaries of system health when asked.""",
    tools=[docker_tools.list_containers]
)

# 2. Loggy Agent
# Analyzes logs
loggy_agent = Agent(
    model='gemini-1.5-flash',
    name='loggy',
    description="Specialist in fetching and analyzing Docker container logs to find errors or warnings.",
    instruction="""You are the Loggy Agent. Use the get_container_logs tool to fetch logs for a specific container.
    Identify error patterns or crashes and report them clearly.""",
    tools=[docker_tools.get_container_logs]
)

# 3. Statman Agent
# Analyzes metrics
statman_agent = Agent(
    model='gemini-1.5-flash',
    name='statman',
    description="Specialist in analyzing real-time resource metrics like CPU and Memory usage.",
    instruction="""You are the Statman Agent. Use the get_container_stats tool to retrieve metrics.
    Explain resource consumption in simple terms (e.g., 'Using 40% of allocated memory').""",
    tools=[docker_tools.get_container_stats]
)

# 4. Sentinel Agent
# High-level anomaly detection
sentinel_agent = Agent(
    model='gemini-1.5-flash',
    name='sentinel',
    description="Specialist in detecting high-level anomalies and weird system behaviors.",
    instruction="""You are the Sentinel Agent. You look at the overall system state provided by other agents and detect anomalies.
    You do not have direct tools, but you use the information from your team to find patterns.""",
)

# 5. Mechanic Agent
# Troubleshooting and solutions
def query_knowledge_base(query: str):
    """Queries the Pinecone knowledge base for troubleshooting documents and solutions."""
    docs = query_vectors(query, top_k=3)
    return "\n\n".join([d["text"] for d in docs])

mechanic_agent = Agent(
    model='gemini-1.5-flash',
    name='mechanic',
    description="Specialist in providing solutions for system issues using technical expertise and documentation.",
    instruction="""You are the Mechanic Agent. Use the query_knowledge_base tool to find solutions in the uploaded documents.
    Combine this with output from other agents to provide step-by-step fixes.""",
    tools=[query_knowledge_base]
)

# 6. Advisor Agent
# Security and optimization
advisor_agent = Agent(
    model='gemini-1.5-flash',
    name='advisor',
    description="Specialist in security best practices and resource optimization for Docker environments.",
    instruction="""You are the Advisor Agent. Use the inspect_container_config tool to review container settings.
    Suggest improvements for security (e.g., non-root users) or efficiency.""",
    tools=[docker_tools.inspect_container_config]
)

# Root Manager Agent
# Orchestrates delegation between the specialized agents
manager_agent = Agent(
    model='gemini-1.5-flash',
    name='manager',
    description="The main entry point for Docker monitoring queries. Delegates to specialized agents.",
    instruction="""You are the Manager Agent for the Docker Monitoring system.
    You receive user queries and delegate them to the appropriate sub-agent:
    - If asked about container status or health: delegate to 'inspector'.
    - If asked for logs or errors: delegate to 'loggy'.
    - If asked for CPU/RAM or performance: delegate to 'statman'.
    - If asked for a solution or fix: delegate to 'mechanic'.
    - If asked for security or configuration reviews: delegate to 'advisor'.
    - If a complex issue is suspected: ask 'sentinel' for an anomaly report first.
    Always provide a unified, helpful response to the user.""",
    sub_agents=[
        inspector_agent, 
        loggy_agent, 
        statman_agent, 
        sentinel_agent, 
        mechanic_agent, 
        advisor_agent
    ]
)
