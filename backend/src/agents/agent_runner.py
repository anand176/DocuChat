"""Agent runner for log monitoring system with session management"""
import uuid
from typing import Optional

from core.config import config
from fastapi import HTTPException
from google.adk.agents import LlmAgent
from google.adk.apps import App, ResumabilityConfig
from google.adk.artifacts import FileArtifactService, InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.plugins import LoggingPlugin, ReflectAndRetryToolPlugin
from google.adk.plugins.context_filter_plugin import ContextFilterPlugin
from google.adk.plugins.multimodal_tool_results_plugin import (
    MultimodalToolResultsPlugin,
)
from google.adk.plugins.save_files_as_artifacts_plugin import SaveFilesAsArtifactsPlugin
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.genai import types
from utils_app.logger import get_service_logger

logger = get_service_logger("log_monitoring_runner")

# Configuration
_DB_URL = config.get_database_url()
_ARTIFACTS_ROOT_DIR = config.artifacts_root_dir

# Singleton services (initialized once, reused across requests)
_session_service: DatabaseSessionService | InMemorySessionService | None = None
_artifact_service: FileArtifactService | InMemoryArtifactService | None = None
_memory_service: InMemoryMemoryService | None = None

# Cache for runners (keyed by app_name:agent_name)
_runner_cache: dict[str, Runner] = {}


def get_session_service() -> DatabaseSessionService | InMemorySessionService:
    """Get or create the session service instance."""
    global _session_service
    if _session_service is None:
        if _DB_URL:
            try:
                _session_service = DatabaseSessionService(db_url=_DB_URL)
                logger.info("Database session service initialized")
            except Exception as e:
                logger.warning(f"Database session service failed: {e}, using in-memory")
                _session_service = InMemorySessionService()
        else:
            logger.info("No DATABASE_URL, using in-memory session service")
            _session_service = InMemorySessionService()
    return _session_service


def get_artifact_service() -> FileArtifactService | InMemoryArtifactService:
    """Get or create the artifact service instance."""
    global _artifact_service
    if _artifact_service is None:
        if _DB_URL:
            try:
                _artifact_service = FileArtifactService(root_dir=_ARTIFACTS_ROOT_DIR)
                logger.info("File artifact service initialized")
            except Exception as e:
                logger.warning(f"File artifact service failed: {e}, using in-memory")
                _artifact_service = InMemoryArtifactService()
        else:
            logger.info("No DATABASE_URL, using in-memory artifact service")
            _artifact_service = InMemoryArtifactService()
    return _artifact_service


def get_memory_service() -> InMemoryMemoryService:
    """Get or create the memory service instance."""
    global _memory_service
    if _memory_service is None:
        _memory_service = InMemoryMemoryService()
    return _memory_service


async def _get_or_create_session(
    app_name: str,
    user_id: str,
    session_id: Optional[str] = None,
    initial_state: Optional[dict] = None,
):
    """Get an existing session or create a new one."""
    session_service = get_session_service()

    # Try to retrieve existing session if session_id provided
    if session_id:
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        if session:
            return session

    # Create new session
    return await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id or str(uuid.uuid4()),
        state=initial_state or {},
    )


def get_runner(app_name: str, agent: LlmAgent) -> Runner:
    """Get or create a cached Runner instance for the app and agent."""
    cache_key = f"{app_name}:{agent.name}"
    if cache_key not in _runner_cache:
        logger.info(f"Creating runner for {cache_key}")
        app = App(
            name=app_name,
            root_agent=agent,
            plugins=[
                LoggingPlugin(),
                ReflectAndRetryToolPlugin(
                    max_retries=3, throw_exception_if_retry_exceeded=False
                ),
                ContextFilterPlugin(num_invocations_to_keep=15),
                SaveFilesAsArtifactsPlugin(),
                MultimodalToolResultsPlugin(),
            ],
            resumability_config=ResumabilityConfig(is_resumable=True),
        )
        _runner_cache[cache_key] = Runner(
            app=app,
            session_service=get_session_service(),
            memory_service=get_memory_service(),
            artifact_service=get_artifact_service(),
        )
    return _runner_cache[cache_key]


async def _run_agent(
    runner: Runner,
    user_id: str,
    session_id: str,
    query: str,
) -> str:
    """Execute agent query and return the final response."""
    content = types.Content(role="user", parts=[types.Part(text=query)])

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                # Concatenate all text parts
                full_text = "".join([p.text for p in event.content.parts if p.text])
                
                # Filter out technical markers and reasoning blocks
                import re
                
                # Handle /*FINAL_ANSWER*/
                full_text = full_text.replace("/*FINAL_ANSWER*/", "")
                
                # Handle /REASONING/ ... /FINAL_ANSWER/ blocks
                full_text = re.sub(r'/REASONING/.*?/FINAL_ANSWER/', '', full_text, flags=re.DOTALL)
                
                # Handle standalone /REASONING/ or /FINAL_ANSWER/ tags
                full_text = full_text.replace("/REASONING/", "").replace("/FINAL_ANSWER/", "")
                
                full_text = full_text.strip()
                
                if full_text:
                    return full_text
                    
            if event.actions and event.actions.escalate:
                return (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
            break

    return "Agent did not produce a final response."


async def handle_agent_request(
    user_id: str,
    query: str,
    agent: LlmAgent,
    app_name: str = "log_monitoring_app",
    session_id: Optional[str] = None,
) -> tuple[str, str]:
    """
    Handle an agent request with proper session management.

    Args:
        user_id: The user ID making the request
        query: The user's query text
        agent: The LLM agent to handle the request
        app_name: The application/project name for session isolation
        session_id: Optional session ID for conversation continuity.
                   If None, a new unique session is created.

    Returns:
        The agent's response text

    Raises:
        HTTPException: If user_id is not provided
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"Agent request: user={user_id}, agent={agent.name}, app={app_name}")

    session = await _get_or_create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        initial_state={},
    )

    runner = get_runner(app_name, agent)
    response = await _run_agent(runner, user_id, session.id, query)

    logger.info(f"Agent request completed: user={user_id}")
    return response, session.id
