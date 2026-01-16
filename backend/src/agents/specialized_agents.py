from .base_agent import BaseAgent
from .docker_tools import DockerTools
import json

class InspectorAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are the 'Inspector Agent'. Your job is to monitor the status of Docker containers.
        You can see which containers are running, their states, names, and exposed ports.
        When asked about the system status, provide a clear summary of what's up and what's down."""
        super().__init__("Inspector", system_prompt)
        self.tools = DockerTools()

    def get_status_summary(self):
        containers = self.tools.list_containers(all=True)
        return self.ask(f"Here is the current container list: {json.dumps(containers)}. Summarize the system health.")

class StatmanAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are the 'Statman Agent'. Your job is to analyze CPU, Memory, and Network metrics of containers.
        You help users understand resource consumption patterns."""
        super().__init__("Statman", system_prompt)
        self.tools = DockerTools()

    def analyze_stats(self, container_id):
        stats = self.tools.get_container_stats(container_id)
        # Simplify stats for the LLM
        refined_stats = {
            "name": stats.get("name"),
            "cpu_usage": stats.get("cpu_stats", {}).get("cpu_usage", {}).get("total_usage"),
            "memory_usage": stats.get("memory_stats", {}).get("usage"),
            "memory_limit": stats.get("memory_stats", {}).get("limit")
        }
        return self.ask(f"Analyze these stats for container {container_id}: {json.dumps(refined_stats)}")

class LoggyAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are the 'Loggy Agent'. You specialize in fetching and interpreting container logs.
        You look for errors, warnings, and unusual patterns."""
        super().__init__("Loggy", system_prompt)
        self.tools = DockerTools()

    def fetch_and_analyze_logs(self, container_id):
        logs = self.tools.get_container_logs(container_id)
        return self.ask(f"Analyze the following logs for container {container_id}: \n\n{logs}")

class SentinelAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are the 'Sentinel Agent'. You are a high-level anomaly detector.
        You receive data from other agents and determine if there is a systemic issue or anomaly.
        Focus on identifying 'weird' behavior that might not be a direct error yet."""
        super().__init__("Sentinel", system_prompt)

    def detect_anomalies(self, context_data):
        return self.ask(f"Based on this system context, are there any anomalies? Context: {json.dumps(context_data)}")

class MechanicAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are the 'Mechanic Agent'. Your job is to provide solutions.
        You use the technical details of the system and, if necessary, look into your Knowledge Base (provided context)
        to suggest fixes for container issues or deployment errors."""
        super().__init__("Mechanic", system_prompt)

    def suggest_fix(self, issue_description, kb_context=""):
        prompt = f"ISSUE: {issue_description}\n\nKNOWLEDGE BASE CONTEXT: {kb_context}\n\nProvide a step-by-step fix."
        return self.ask(prompt)

class AdvisorAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are the 'Advisor Agent'. You look for security flaws, insecure configurations, 
        and opportunities for resource optimization. You suggest best practices for Docker environments."""
        super().__init__("Advisor", system_prompt)

    def give_advice(self, container_config):
        return self.ask(f"Review this container configuration for security and optimization: {json.dumps(container_config)}")
