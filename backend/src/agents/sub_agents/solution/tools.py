"""Tools for solution agent"""
from typing import Dict, List
from utils_app.logger import get_service_logger
from agents.sub_agents.solution.utils import (
    format_solution_response,
    get_solution_for_pattern
)

logger = get_service_logger("solution_agent")


def analyze_root_cause(anomalies: Dict, logs: List[Dict]) -> str:
    """
    Analyze the root cause of detected anomalies.
    
    Args:
        anomalies: Anomaly detection results from log analysis agent
        logs: Original log entries
        
    Returns:
        Root cause description
    """
    try:
        if not anomalies.get('has_anomaly'):
            return "No anomalies detected. System appears to be functioning normally."
        
        error_patterns = anomalies.get('error_patterns', {})
        top_sources = anomalies.get('top_error_sources', [])
        anomaly_score = anomalies.get('anomaly_score', 0)
        
        # Identify primary error pattern
        if error_patterns:
            primary_error = max(error_patterns.items(), key=lambda x: x[1])
            error_type, error_count = primary_error
            
            root_causes = {
                'authentication_failure': f"High volume of authentication failures ({error_count} occurrences). This indicates potential brute force attack or misconfigured authentication system.",
                'connection_timeout': f"Multiple connection timeouts detected ({error_count} occurrences). This suggests network connectivity issues or overloaded services.",
                'permission_denied': f"Permission denied errors ({error_count} occurrences). This indicates incorrect file permissions or access control configuration.",
                'service_unavailable': f"Service unavailability detected ({error_count} occurrences). This suggests service crashes or resource exhaustion.",
                'database_error': f"Database errors detected ({error_count} occurrences). This indicates database connectivity or query issues.",
                'unknown_user': f"Unknown user attempts ({error_count} occurrences). This may indicate reconnaissance activity or misconfigured user accounts.",
                'alert_exit': f"Service alert exits detected ({error_count} occurrences). This suggests configuration errors or missing dependencies."
            }
            
            root_cause = root_causes.get(error_type, f"Multiple errors of type '{error_type}' detected ({error_count} occurrences).")
            
            # Add source information if available
            if top_sources:
                top_source, source_count = top_sources[0]
                root_cause += f" Primary source: {top_source} ({source_count} occurrences)."
            
            return root_cause
        
        return f"Anomaly detected with score {anomaly_score}%, but specific error pattern is unclear. Manual investigation recommended."
        
    except Exception as e:
        logger.error(f"Error in analyze_root_cause: {e}")
        return f"Error analyzing root cause: {str(e)}"


def generate_solution(root_cause: str, anomalies: Dict) -> str:
    """
    Generate actionable solutions based on root cause analysis.
    
    Args:
        root_cause: Identified root cause
        anomalies: Anomaly detection results
        
    Returns:
        Formatted solution recommendations
    """
    try:
        error_patterns = anomalies.get('error_patterns', {})
        
        if not error_patterns:
            return "No specific solutions available. Please review logs manually for more details."
        
        # Get primary error pattern
        primary_error = max(error_patterns.items(), key=lambda x: x[1])
        error_type, error_count = primary_error
        
        # Get solutions for the primary error
        solutions = get_solution_for_pattern(error_type, error_count)
        
        # Add additional context
        additional_info = {
            'Severity': anomalies.get('severity', 'UNKNOWN'),
            'Total Errors': anomalies.get('total_errors', 0),
            'Anomaly Score': f"{anomalies.get('anomaly_score', 0)}%"
        }
        
        if anomalies.get('top_error_sources'):
            top_source, count = anomalies['top_error_sources'][0]
            additional_info['Top Error Source'] = f"{top_source} ({count} occurrences)"
        
        # Format response
        formatted_solution = format_solution_response(root_cause, solutions, additional_info)
        
        logger.info(f"Generated solution for {error_type} with {len(solutions)} recommendations")
        
        return formatted_solution
        
    except Exception as e:
        logger.error(f"Error in generate_solution: {e}")
        return f"Error generating solution: {str(e)}"


def search_similar_issues(issue_description: str) -> List[Dict]:
    """
    Search for similar past issues (placeholder for future knowledge base integration).
    
    Args:
        issue_description: Description of the current issue
        
    Returns:
        List of similar issues with solutions
    """
    # Placeholder: In future, this would query a knowledge base or incident database
    logger.info(f"Searching for similar issues: {issue_description}")
    
    return [
        {
            'title': 'Similar issue search not yet implemented',
            'description': 'This feature will be integrated with the incident knowledge base in the future.',
            'solution': 'Use the current root cause analysis and generated solutions.'
        }
    ]
