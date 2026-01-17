"""
Test script for log monitoring system

This script demonstrates how to use the log monitoring endpoint.
"""
import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"
LOG_MONITORING_ENDPOINT = f"{BASE_URL}/agents/log_monitoring"

def test_log_monitoring(query: str):
    """
    Test the log monitoring endpoint with a query.
    
    Args:
        query: Natural language query (e.g., "Is there an issue in the last 1 hour?")
    """
    print(f"\n{'='*80}")
    print(f"Testing Log Monitoring with query: '{query}'")
    print(f"{'='*80}\n")
    
    try:
        # Make request
        response = requests.post(
            LOG_MONITORING_ENDPOINT,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Display results
        print(f"Status: {result.get('status')}")
        print(f"Session ID: {result.get('session_id')}")
        print(f"\nAgent Response:")
        print("-" * 40)
        print(result.get('response'))
        print("-" * 40)
        
        print(f"\n{'='*80}\n")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Test cases
    test_queries = [
        "Is there an issue in the last 1 hour?",
        "Any problems in the last 2 hours?",
        "Check logs for the last 30 minutes",
    ]
    
    print("Log Monitoring System Test")
    print("="*80)
    print("\nMake sure Docker services are running:")
    print("  docker-compose up -d")
    print("\nAnd the backend server is running:")
    print("  cd backend && python -m uvicorn app:app --reload")
    print("\n")
    
    for query in test_queries:
        test_log_monitoring(query)
        input("Press Enter to continue to next test...")
