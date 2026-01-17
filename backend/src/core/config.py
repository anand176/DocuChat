from typing import Any, Dict, Optional

import litellm
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

load_dotenv()
litellm.drop_params = True
litellm._turn_on_debug()


class MCPConfig(BaseModel):
    connection_timeout: int = Field(
        default=60, description="MCP connection timeout in seconds"
    )


class AgentModelConfig(BaseModel):
    """Configuration for agent models."""

    # Agent configurations with model instances
    agent_configs: Dict[str, Any] = Field(
        default_factory=lambda: {
            "ai_assistant": LiteLlm("gemini/gemini-2.5-flash"),
            "incident_manager_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "incident_resolution_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "knowledge_base_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "log_analytics_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "log_monitoring_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "communication_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "root_cause_analyzer_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "report_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "time_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "preference_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "webhook_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "code_executor_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "google_search_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "MemoryRecallAgent": LiteLlm("gemini/gemini-2.5-flash"),
            "log_analysis_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "log_retrieve_agent": LiteLlm("gemini/gemini-2.5-flash"),
            "solution_agent": LiteLlm("gemini/gemini-2.5-flash"),
        }
    )

    def get_model_for_agent(self, agent_name: str) -> Any:
        """Get the model for a specific agent, falling back to default if not specified."""
        # Use Ollama Chat to run local models if needed
        # LiteLlm(
        #     model="ollama_chat/llama3.2:3b",
        #     api_base="http://localhost:11434",
        # ),
        return self.agent_configs.get(agent_name, LiteLlm("gemini/gemini-2.5-flash"))


class Config(BaseSettings):
    app_name: str = "Incident Management API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database configuration - use Pydantic settings for environment variables
    postgres_user: Optional[str] = None  # REQUIRED: set in env
    postgres_password: Optional[str] = None  # REQUIRED: set in env
    postgres_host: Optional[str] = None  # REQUIRED: set in env
    postgres_port: int = 5432  # Default can remain (non-secret)
    postgres_db: Optional[str] = None  # REQUIRED: set in env

    # Allow direct database URL override (useful for tests)
    database_url: Optional[str] = None

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:2000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:2000",
        "http://3.95.67.240:8080",
        "http://3.95.67.240:8000",
        "http://3.95.67.240",
        "http://34.205.146.246",
        "http://incident.abilytics.com",
        "https://incident.abilytics.com",
    ]
    allowed_methods: list[str] = ["*"]
    allowed_headers: list[str] = ["*"]
    allow_credentials: bool = True

    # Authentication/JWT secrets
    secret_key: str = ""  # REQUIRED: Set in environment
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    artifacts_root_dir: str = "./artifacts"

    # MCP Configuration
    mcp: MCPConfig = Field(default_factory=MCPConfig)

    # Agent Model Configuration
    agents: AgentModelConfig = Field(default_factory=AgentModelConfig)

    def get_database_url(self) -> str:
        """Get the database URL, either from direct setting or constructed from components."""
        # If DATABASE_URL is directly provided, use it (useful for tests)
        if self.database_url:
            return self.database_url

        # Otherwise, construct PostgreSQL URL from components
        if (
            not self.postgres_user
            or not self.postgres_password
            or not self.postgres_host
            or not self.postgres_db
        ):
            raise ValueError(
                "Database configuration is incomplete. Either provide DATABASE_URL or all POSTGRES_* variables."
            )

        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra environment variables without validation errors


config = Config()
