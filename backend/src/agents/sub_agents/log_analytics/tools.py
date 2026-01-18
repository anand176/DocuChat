"""Merged tools for log retrieval and analysis"""
from typing import Dict, List, Optional
import requests
from utils_app.logger import get_service_logger
from agents.sub_agents.log_analytics.utils import parse_time_range, build_loki_query
from agents.sub_agents.log_analytics.utils import (
    extract_error_patterns,
    calculate_anomaly_score,
    extract_ip_addresses,
    get_top_error_sources
)

logger = get_service_logger("log_analytics_agent")
LOKI_URL = "http://loki:3100"

def fetch_and_analyze_logs(time_range: str, pattern: Optional[str] = None) -> str:
    """
    Fetches logs from Loki and performs immediate anomaly analysis.
    
    Args:
        time_range: Natural language time range (e.g., "last 15 minutes", "last 1 hour")
        pattern: Optional keyword pattern to filter logs
        
    Returns:
        A comprehensive human-readable summary of logs and analysis.
    """
    try:
        # 1. Fetch Logs
        start_time, end_time = parse_time_range(time_range)
        logql_query = f'{{job=~".+"}} |~ "(?i){pattern}"' if pattern else build_loki_query()
        
        url = f"{LOKI_URL}/loki/api/v1/query_range"
        params = {'query': logql_query, 'start': start_time, 'end': end_time, 'limit': 1000}
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        logs = []
        if data.get('status') == 'success' and data.get('data', {}).get('result'):
            for stream in data['data']['result']:
                stream_labels = stream.get('stream', {})
                for value in stream.get('values', []):
                    logs.append({'timestamp': value[0], 'line': value[1], 'labels': stream_labels})

        if not logs:
            return f"No logs found for {time_range}" + (f" matching pattern '{pattern}'" if pattern else "")

        # 2. Analyze Logs
        error_patterns = extract_error_patterns(logs)
        anomaly_score = calculate_anomaly_score(logs, error_patterns)
        ip_addresses = extract_ip_addresses(logs)
        top_sources = get_top_error_sources(logs)
        
        severity = 'CRITICAL' if anomaly_score > 50 else 'HIGH' if anomaly_score > 30 else 'MEDIUM' if anomaly_score > 10 else 'LOW'
        
        # 3. Format Response
        summary = [
            f"### Log Analytics Report ({time_range})",
            f"- **Total Logs**: {len(logs)}",
            f"- **Anomaly Score**: {anomaly_score}%",
            f"- **Severity Level**: {severity}",
            f"- **Unique IPs**: {len(ip_addresses)}",
            "",
            "**Error Patterns Detected:**" if error_patterns else "**No common error patterns detected.**",
        ]
        
        for p, count in list(error_patterns.items())[:5]:
            summary.append(f"- {p.replace('_', ' ').title()}: {count} occurrences")
            
        if top_sources:
            summary.append("\n**Top Error Sources:**")
            for source, count in top_sources[:3]:
                summary.append(f"- {source}: {count} errors")
        
        if anomaly_score > 10:
            summary.append("\n⚠️ **Anomalies detected!** Further investigation recommended.")
        else:
            summary.append("\n✅ System appears stable.")

        return "\n".join(summary)
        
    except Exception as e:
        logger.error(f"Error in fetch_and_analyze_logs: {e}")
        return f"failed to analyze logs: {str(e)}"
