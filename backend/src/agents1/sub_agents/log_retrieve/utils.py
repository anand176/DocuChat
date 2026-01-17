"""Utility functions for log retrieve agent"""
from datetime import datetime, timedelta
from typing import Dict, Tuple
import re


def parse_time_range(time_string: str) -> Tuple[str, str]:
    """
    Convert natural language time to Loki query format.
    
    Args:
        time_string: Natural language time like "last 1 hour", "last 30 minutes", "last 2 hours"
        
    Returns:
        Tuple of (start_time, end_time) in RFC3339 format
    """
    time_string = time_string.lower().strip()
    
    # Parse patterns like "last X hour(s)", "last X minute(s)", "last X day(s)"
    patterns = [
        (r'last\s+(\d+)\s+hour[s]?', 'hours'),
        (r'last\s+(\d+)\s+minute[s]?', 'minutes'),
        (r'last\s+(\d+)\s+day[s]?', 'days'),
        (r'last\s+(\d+)\s+h', 'hours'),
        (r'last\s+(\d+)\s+m', 'minutes'),
        (r'last\s+(\d+)\s+d', 'days'),
    ]
    
    for pattern, unit in patterns:
        match = re.search(pattern, time_string)
        if match:
            value = int(match.group(1))
            end_time = datetime.utcnow()
            
            if unit == 'hours':
                start_time = end_time - timedelta(hours=value)
            elif unit == 'minutes':
                start_time = end_time - timedelta(minutes=value)
            elif unit == 'days':
                start_time = end_time - timedelta(days=value)
            
            return (
                start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            )
    
    # Default: last 1 hour
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    return (
        start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    )


def build_loki_query(filters: Dict[str, str] = None) -> str:
    """
    Build LogQL query string for Loki.
    
    Args:
        filters: Dictionary of label filters (e.g., {"job": "system-logs", "level": "error"})
        
    Returns:
        LogQL query string
    """
    if not filters:
        return '{job=~".+"}'  # Match all jobs
    
    filter_parts = []
    for key, value in filters.items():
        filter_parts.append(f'{key}="{value}"')
    
    return '{' + ', '.join(filter_parts) + '}'


def format_log_results(logs: list) -> str:
    """
    Format logs for analysis.
    
    Args:
        logs: List of log entries from Loki
        
    Returns:
        Formatted string of logs
    """
    if not logs:
        return "No logs found for the specified time range."
    
    formatted = []
    for i, log in enumerate(logs[:100], 1):  # Limit to 100 logs
        timestamp = log.get('timestamp', 'N/A')
        message = log.get('line', log.get('message', ''))
        formatted.append(f"[{i}] {timestamp}: {message}")
    
    if len(logs) > 100:
        formatted.append(f"\n... and {len(logs) - 100} more log entries")
    
    return '\n'.join(formatted)
