from typing import Optional, Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
import logging

# Set up logger
logger = logging.getLogger("agents_backend")
logger.setLevel(logging.INFO)

# Create router
router = APIRouter(prefix="/agents", tags=["Agents"])

from login.dependencies import get_current_user
from tables.auth import User

class LogMonitoringRequest(BaseModel):
    query: str
    user_id: str = "default_user"
    session_id: Optional[str] = None

@router.post("/log_monitoring")
async def log_monitoring(
    req: LogMonitoringRequest,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Comprehensive log monitoring endpoint.
    """
    logger.info(f"Log monitoring request: {req.query}")
    
    try:
        from agents.agent_runner import handle_agent_request
        from agents.agent import log_monitoring_agent
        
        # Use the agent runner with proper session management
        response, actual_session_id = await handle_agent_request(
            user_id=req.user_id,
            query=req.query,
            agent=log_monitoring_agent,
            app_name="log_monitoring_app",
            session_id=req.session_id,
        )
        
        return {
            "status": "success",
            "response": response,
            "session_id": actual_session_id
        }
        
    except Exception as e:
        logger.error(f"Error in log monitoring: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process log monitoring request: {str(e)}"
        )

