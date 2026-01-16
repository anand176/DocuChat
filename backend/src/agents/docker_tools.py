import docker
import os

class DockerTools:
    def __init__(self):
        """Initializes the Docker client from the environment settings."""
        try:
            self.client = docker.from_env()
        except Exception as e:
            print(f"Error connecting to Docker: {e}")
            self.client = None

    def list_containers(self, all: bool = False):
        """
        Retrieves a list of Docker containers currently on the host.
        
        Args:
            all: Whether to include stopped containers. Defaults to False.
            
        Returns:
            A list of dictionaries containing container ID, name, status, image, and ports.
        """
        if not self.client: return "Docker client not initialized."
        try:
            containers = self.client.containers.list(all=all)
            return [
                {
                    "id": c.short_id,
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else "unknown",
                    "ports": c.attrs.get('NetworkSettings', {}).get('Ports', {})
                }
                for c in containers
            ]
        except Exception as e:
            return f"Error listing containers: {str(e)}"

    def get_container_stats(self, container_name_or_id: str):
        """
        Retrieves real-time resource utilization metrics (CPU, Memory, etc.) for a specific container.
        
        Args:
            container_name_or_id: The name or ID of the container to monitor.
            
        Returns:
            Raw dictionary of stats containing cpu_stats, memory_stats, and network_stats.
        """
        if not self.client: return "Docker client not initialized."
        try:
            container = self.client.containers.get(container_name_or_id)
            stats = container.stats(stream=False)
            return stats
        except Exception as e:
            return f"Error getting stats for {container_name_or_id}: {str(e)}"

    def get_container_logs(self, container_name_or_id: str, tail_lines: int = 50):
        """
        Fetches the most recent logs from a specific Docker container to check for errors or state changes.
        
        Args:
            container_name_or_id: The name or ID of the container.
            tail_lines: How many lines from the end of the logs to retrieve. Defaults to 50.
            
        Returns:
            A string containing the container logs.
        """
        if not self.client: return "Docker client not initialized."
        try:
            container = self.client.containers.get(container_name_or_id)
            logs = container.logs(tail=tail_lines).decode('utf-8')
            return logs
        except Exception as e:
            return f"Error getting logs for {container_name_or_id}: {str(e)}"

    def inspect_container_config(self, container_name_or_id: str):
        """
        Retrieves the full configuration and low-level details of a container for security or optimization analysis.
        
        Args:
            container_name_or_id: The name or ID of the container.
            
        Returns:
            A detailed dictionary of container attributes and configuration settings.
        """
        if not self.client: return "Docker client not initialized."
        try:
            container = self.client.containers.get(container_name_or_id)
            return container.attrs
        except Exception as e:
            return f"Error inspecting container {container_name_or_id}: {str(e)}"
