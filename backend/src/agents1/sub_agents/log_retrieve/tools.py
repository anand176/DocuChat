"""Tools for log retrieve agent"""
import requests
from typing import Dict, List, Optional
from src.utils_app.logger import get_service_logger
from src.agents1.sub_agents.log_retrieve.utils import (
    parse_time_range,
    build_loki_query,
    format_log_results
)

logger = get_service_logger("log_retrieve_agent")

LOKI_URL = "http://loki:3100"


def fetch_logs_from_loki(time_range: str, query_filter: Optional[str] = None) -> Dict:
    """
    Fetch logs from Loki based on time range and optional filters.
    
    Args:
        time_range: Natural language time range (e.g., "last 1 hour", "last 30 minutes")
        query_filter: Optional LogQL filter string
        
    Returns:
        Dictionary containing logs and metadata
    """
    try:
        # Parse time range
        start_time, end_time = parse_time_range(time_range)
        
        # Build query
        if query_filter:
            logql_query = query_filter
        else:
            logql_query = build_loki_query()
        
        # Query Loki
        url = f"{LOKI_URL}/loki/api/v1/query_range"
        params = {
            'query': logql_query,
            'start': start_time,
            'end': end_time,
            'limit': 1000  # Limit results
        }
        
        logger.info(f"Querying Loki: {logql_query} from {start_time} to {end_time}")
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract logs from response
        logs = []
        if data.get('status') == 'success' and data.get('data', {}).get('result'):
            for stream in data['data']['result']:
                stream_labels = stream.get('stream', {})
                for value in stream.get('values', []):
                    timestamp_ns, line = value
                    logs.append({
                        'timestamp': timestamp_ns,
                        'line': line,
                        'labels': stream_labels
                    })
        
        logger.info(f"Retrieved {len(logs)} log entries from Loki")
        
        return {
            'success': True,
            'logs': logs,
            'count': len(logs),
            'time_range': {'start': start_time, 'end': end_time},
            'query': logql_query
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error querying Loki: {e}")
        return {
            'success': False,
            'error': str(e),
            'logs': [],
            'count': 0
        }
    except Exception as e:
        logger.error(f"Unexpected error in fetch_logs_from_loki: {e}")
        return {
            'success': False,
            'error': str(e),
            'logs': [],
            'count': 0
        }


def get_log_summary(time_range: str) -> str:
    """
    Get a summary of logs for the specified time range.
    
    Args:
        time_range: Natural language time range
        
    Returns:
        Formatted summary string
    """
    result = fetch_logs_from_loki(time_range)
    
    if not result['success']:
        return f"Error fetching logs: {result.get('error', 'Unknown error')}"
    
    logs = result['logs']
    if not logs:
        return f"No logs found for {time_range}"
    
    # Format logs for display
    formatted_logs = format_log_results(logs)
    
    summary = f"""
Log Summary for {time_range}:
Total logs retrieved: {result['count']}
Time range: {result['time_range']['start']} to {result['time_range']['end']}

Logs:
{formatted_logs}
"""
    
    return summary


def search_logs_by_pattern(time_range: str, pattern: str) -> Dict:
    """
    Search logs containing a specific pattern.
    
    Args:
        time_range: Natural language time range
        pattern: Search pattern (e.g., "error", "authentication failure")
        
    Returns:
        Dictionary with matching logs
    """
    # Build query with pattern filter
    logql_query = f'{{job=~".+"}} |~ "(?i){pattern}"'  # Case-insensitive search
    
    result = fetch_logs_from_loki(time_range, logql_query)
    
    if result['success']:
        result['pattern'] = pattern
    
    return result
