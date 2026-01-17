"""Tools for log analysis agent"""
from typing import Dict, List
from src.utils_app.logger import get_service_logger
from src.agents1.sub_agents.log_analysis.utils import (
    extract_error_patterns,
    calculate_anomaly_score,
    extract_ip_addresses,
    get_top_error_sources
)

logger = get_service_logger("log_analysis_agent")


def detect_anomalies(logs: List[Dict]) -> Dict:
    """
    Detect anomalies in the provided logs.
    
    Args:
        logs: List of log entries from log retrieve agent
        
    Returns:
        Dictionary with anomaly detection results
    """
    try:
        if not logs:
            return {
                'has_anomaly': False,
                'anomaly_score': 0.0,
                'message': 'No logs to analyze'
            }
        
        # Extract error patterns
        error_patterns = extract_error_patterns(logs)
        
        # Calculate anomaly score
        anomaly_score = calculate_anomaly_score(logs, error_patterns)
        
        # Determine if there's an anomaly (threshold: 10%)
        has_anomaly = anomaly_score > 10.0
        
        # Extract additional context
        ip_addresses = extract_ip_addresses(logs)
        top_sources = get_top_error_sources(logs)
        
        result = {
            'has_anomaly': has_anomaly,
            'anomaly_score': anomaly_score,
            'total_logs': len(logs),
            'error_patterns': error_patterns,
            'total_errors': sum(error_patterns.values()),
            'unique_ips': len(ip_addresses),
            'top_error_sources': top_sources,
            'severity': 'CRITICAL' if anomaly_score > 50 else 'HIGH' if anomaly_score > 30 else 'MEDIUM' if anomaly_score > 10 else 'LOW'
        }
        
        logger.info(f"Anomaly detection complete: score={anomaly_score}, has_anomaly={has_anomaly}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in detect_anomalies: {e}")
        return {
            'has_anomaly': False,
            'anomaly_score': 0.0,
            'error': str(e)
        }


def generate_log_summary(logs: List[Dict]) -> str:
    """
    Generate a concise summary of the logs.
    
    Args:
        logs: List of log entries
        
    Returns:
        Summary string
    """
    try:
        if not logs:
            return "No logs available for analysis."
        
        # Get anomaly detection results
        anomaly_result = detect_anomalies(logs)
        
        # Build summary
        summary_parts = [
            f"**Log Analysis Summary**",
            f"",
            f"Total Logs Analyzed: {anomaly_result['total_logs']}",
            f"Anomaly Score: {anomaly_result['anomaly_score']}%",
            f"Severity: {anomaly_result['severity']}",
            f"Has Anomaly: {'Yes' if anomaly_result['has_anomaly'] else 'No'}",
            f"",
        ]
        
        if anomaly_result.get('error_patterns'):
            summary_parts.append("**Error Patterns Detected:**")
            for pattern, count in anomaly_result['error_patterns'].items():
                summary_parts.append(f"  - {pattern.replace('_', ' ').title()}: {count}")
            summary_parts.append("")
        
        if anomaly_result.get('top_error_sources'):
            summary_parts.append("**Top Error Sources:**")
            for source, count in anomaly_result['top_error_sources']:
                summary_parts.append(f"  - {source}: {count} occurrences")
            summary_parts.append("")
        
        if anomaly_result['has_anomaly']:
            summary_parts.append("⚠️ **Anomalies detected!** Further investigation recommended.")
        else:
            summary_parts.append("✅ **No significant anomalies detected.** System appears healthy.")
        
        return '\n'.join(summary_parts)
        
    except Exception as e:
        logger.error(f"Error in generate_log_summary: {e}")
        return f"Error generating summary: {str(e)}"


def classify_log_severity(logs: List[Dict]) -> Dict[str, int]:
    """
    Classify logs by severity level.
    
    Args:
        logs: List of log entries
        
    Returns:
        Dictionary with severity counts
    """
    severity_counts = {
        'CRITICAL': 0,
        'ERROR': 0,
        'WARNING': 0,
        'INFO': 0,
        'DEBUG': 0
    }
    
    for log in logs:
        line = log.get('line', '').lower()
        
        if 'critical' in line or 'fatal' in line:
            severity_counts['CRITICAL'] += 1
        elif 'error' in line or 'fail' in line:
            severity_counts['ERROR'] += 1
        elif 'warning' in line or 'warn' in line or 'alert' in line:
            severity_counts['WARNING'] += 1
        elif 'debug' in line:
            severity_counts['DEBUG'] += 1
        else:
            severity_counts['INFO'] += 1
    
    return severity_counts
