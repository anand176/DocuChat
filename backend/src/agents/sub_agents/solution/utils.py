"""Utility functions for solution agent"""
from typing import Dict, List


def format_solution_response(root_cause: str, solutions: List[str], additional_info: Dict = None) -> str:
    """
    Format the solution response in a structured way.
    
    Args:
        root_cause: Identified root cause
        solutions: List of recommended solutions
        additional_info: Additional context information
        
    Returns:
        Formatted solution string
    """
    response_parts = [
        "**Root Cause Analysis & Solutions**",
        "",
        f"**Root Cause:** {root_cause}",
        "",
        "**Recommended Solutions:**"
    ]
    
    for i, solution in enumerate(solutions, 1):
        response_parts.append(f"{i}. {solution}")
    
    if additional_info:
        response_parts.append("")
        response_parts.append("**Additional Information:**")
        for key, value in additional_info.items():
            response_parts.append(f"  - {key}: {value}")
    
    return '\n'.join(response_parts)


def get_solution_for_pattern(error_pattern: str, count: int) -> List[str]:
    """
    Get recommended solutions for specific error patterns.
    
    Args:
        error_pattern: Type of error pattern
        count: Number of occurrences
        
    Returns:
        List of solution recommendations
    """
    solutions_map = {
        'authentication_failure': [
            "Review authentication logs for brute force attack patterns",
            "Implement rate limiting on authentication endpoints",
            "Enable fail2ban or similar intrusion prevention system",
            "Review and strengthen password policies",
            "Consider implementing multi-factor authentication (MFA)"
        ],
        'connection_timeout': [
            "Check network connectivity and firewall rules",
            "Increase connection timeout values if appropriate",
            "Review server resource utilization (CPU, memory, network)",
            "Check for network congestion or bandwidth issues",
            "Verify DNS resolution is working correctly"
        ],
        'permission_denied': [
            "Review file and directory permissions",
            "Check user and group ownership",
            "Verify SELinux or AppArmor policies if enabled",
            "Review application access control lists (ACLs)",
            "Ensure service accounts have appropriate permissions"
        ],
        'service_unavailable': [
            "Check if the service is running: systemctl status <service>",
            "Review service logs for startup errors",
            "Verify service dependencies are available",
            "Check system resources (disk space, memory, CPU)",
            "Restart the service if appropriate"
        ],
        'database_error': [
            "Check database connectivity and credentials",
            "Review database logs for specific errors",
            "Verify database server is running and accessible",
            "Check for database connection pool exhaustion",
            "Review and optimize slow queries"
        ],
        'unknown_user': [
            "Verify user accounts exist in the system",
            "Check LDAP/AD integration if applicable",
            "Review user provisioning processes",
            "Implement proper user validation before authentication attempts",
            "Monitor for potential reconnaissance activities"
        ],
        'alert_exit': [
            "Review the specific service configuration",
            "Check for configuration file syntax errors",
            "Verify all required dependencies are installed",
            "Review system logs for related errors",
            "Test configuration in a non-production environment first"
        ]
    }
    
    return solutions_map.get(error_pattern, [
        "Review detailed error logs for more specific information",
        "Check system resource utilization",
        "Verify service configuration",
        "Consult service-specific documentation"
    ])
