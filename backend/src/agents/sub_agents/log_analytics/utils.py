"""Utility functions for log analysis agent"""
from typing import Dict, List
import re
from collections import Counter


def extract_error_patterns(logs: List[Dict]) -> Dict:
    """
    Extract common error patterns from logs.
    
    Args:
        logs: List of log entries
        
    Returns:
        Dictionary with error patterns and counts
    """
    error_patterns = {
        'authentication_failure': 0,
        'connection_timeout': 0,
        'permission_denied': 0,
        'service_unavailable': 0,
        'database_error': 0,
        'unknown_user': 0,
        'failed_login': 0,
        'alert_exit': 0,
        'other_errors': 0
    }
    
    for log in logs:
        line = log.get('line', '').lower()
        
        if 'authentication failure' in line or 'auth' in line and 'fail' in line:
            error_patterns['authentication_failure'] += 1
        elif 'timeout' in line or 'timed out' in line:
            error_patterns['connection_timeout'] += 1
        elif 'permission denied' in line or 'denied' in line:
            error_patterns['permission_denied'] += 1
        elif 'unavailable' in line or 'down' in line:
            error_patterns['service_unavailable'] += 1
        elif 'database' in line and ('error' in line or 'fail' in line):
            error_patterns['database_error'] += 1
        elif 'user unknown' in line or 'unknown user' in line:
            error_patterns['unknown_user'] += 1
        elif 'failed' in line and ('login' in line or 'logon' in line):
            error_patterns['failed_login'] += 1
        elif 'alert' in line and 'exit' in line:
            error_patterns['alert_exit'] += 1
        elif 'error' in line or 'fail' in line or 'critical' in line:
            error_patterns['other_errors'] += 1
    
    return {k: v for k, v in error_patterns.items() if v > 0}


def calculate_anomaly_score(logs: List[Dict], error_patterns: Dict) -> float:
    """
    Calculate anomaly score based on error patterns.
    
    Args:
        logs: List of log entries
        error_patterns: Dictionary of error patterns and counts
        
    Returns:
        Anomaly score (0-100)
    """
    if not logs:
        return 0.0
    
    total_logs = len(logs)
    total_errors = sum(error_patterns.values())
    
    # Calculate error rate
    error_rate = (total_errors / total_logs) * 100 if total_logs > 0 else 0
    
    # Weight certain critical errors higher
    critical_errors = (
        error_patterns.get('authentication_failure', 0) +
        error_patterns.get('database_error', 0) +
        error_patterns.get('service_unavailable', 0)
    )
    
    critical_rate = (critical_errors / total_logs) * 100 if total_logs > 0 else 0
    
    # Anomaly score: weighted combination
    anomaly_score = min(100, (error_rate * 0.6) + (critical_rate * 0.4))
    
    return round(anomaly_score, 2)


def extract_ip_addresses(logs: List[Dict]) -> List[str]:
    """
    Extract unique IP addresses from logs.
    
    Args:
        logs: List of log entries
        
    Returns:
        List of unique IP addresses
    """
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ips = []
    
    for log in logs:
        line = log.get('line', '')
        matches = re.findall(ip_pattern, line)
        ips.extend(matches)
    
    return list(set(ips))


def get_top_error_sources(logs: List[Dict], top_n: int = 5) -> List[tuple]:
    """
    Get top error sources (IPs or hostnames).
    
    Args:
        logs: List of log entries
        top_n: Number of top sources to return
        
    Returns:
        List of tuples (source, count)
    """
    sources = []
    
    for log in logs:
        line = log.get('line', '')
        # Extract IP addresses
        ip_pattern = r'rhost=([^\s]+)'
        match = re.search(ip_pattern, line)
        if match:
            sources.append(match.group(1))
    
    source_counts = Counter(sources)
    return source_counts.most_common(top_n)
