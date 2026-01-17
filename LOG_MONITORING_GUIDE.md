# Log Monitoring System - Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ with required dependencies
- Google API key configured in `.env`

## Setup Instructions

### 1. Start Docker Services

```bash
cd Cricket-Chatbot
docker-compose up -d
```

Verify services are running:
```bash
docker-compose ps
```

You should see:
- `docuchat-loki` (port 3100)
- `docuchat-prometheus` (port 9090)
- `docuchat-alloy` (port 12345)
- `docuchat-postgres` (port 5432)
- `docuchat-backend` (port 8000)

### 2. Verify Loki is Ready

```bash
curl http://localhost:3100/ready
```

Expected response: `ready`

### 3. Verify Prometheus is Ready

```bash
curl http://localhost:9090/-/ready
```

Expected response: `Prometheus Server is Ready.`

### 4. Check Logs are Being Ingested

Wait a few seconds for Alloy to start ingesting logs, then query Loki:

```bash
curl -G -s "http://localhost:3100/loki/api/v1/query" \
  --data-urlencode 'query={job="system-logs"}' | jq
```

## Usage

### API Endpoint

**POST** `/agents/log_monitoring`

**Request Body**:
```json
{
  "query": "Is there an issue in the last 1 hour?"
}
```

### Example Queries

1. **Check last hour**:
   ```bash
   curl -X POST http://localhost:8000/agents/log_monitoring \
     -H "Content-Type: application/json" \
     -d '{"query": "Is there an issue in the last 1 hour?"}'
   ```

2. **Check last 30 minutes**:
   ```bash
   curl -X POST http://localhost:8000/agents/log_monitoring \
     -H "Content-Type: application/json" \
     -d '{"query": "Any problems in the last 30 minutes?"}'
   ```

3. **Check last 2 hours**:
   ```bash
   curl -X POST http://localhost:8000/agents/log_monitoring \
     -H "Content-Type: application/json" \
     -d '{"query": "Check logs for the last 2 hours"}'
   ```

### Using the Test Script

```bash
python test_log_monitoring.py
```

## Expected Response

```json
{
  "status": "success",
  "time_range": "last 1 hour",
  "log_count": 150,
  "has_issues": true,
  "anomaly_score": 45.5,
  "severity": "HIGH",
  "summary": "**Log Analysis Summary**\n\nTotal Logs Analyzed: 150\nAnomaly Score: 45.5%\nSeverity: HIGH\nHas Anomaly: Yes\n\n**Error Patterns Detected:**\n  - Authentication Failure: 68\n  - Unknown User: 12\n\n**Top Error Sources:**\n  - 218.188.2.4: 25 occurrences\n  - 220-135-151-1.hinet-ip.hinet.net: 15 occurrences\n\n⚠️ **Anomalies detected!** Further investigation recommended.",
  "error_patterns": {
    "authentication_failure": 68,
    "unknown_user": 12
  },
  "top_error_sources": [
    ["218.188.2.4", 25],
    ["220-135-151-1.hinet-ip.hinet.net", 15]
  ],
  "root_cause": "High volume of authentication failures (68 occurrences). This indicates potential brute force attack or misconfigured authentication system. Primary source: 218.188.2.4 (25 occurrences).",
  "solutions": "**Root Cause Analysis & Solutions**\n\n**Root Cause:** High volume of authentication failures (68 occurrences)...\n\n**Recommended Solutions:**\n1. Review authentication logs for brute force attack patterns\n2. Implement rate limiting on authentication endpoints\n3. Enable fail2ban or similar intrusion prevention system\n4. Review and strengthen password policies\n5. Consider implementing multi-factor authentication (MFA)\n\n**Additional Information:**\n  - Severity: HIGH\n  - Total Errors: 80\n  - Anomaly Score: 45.5%\n  - Top Error Source: 218.188.2.4 (25 occurrences)"
}
```

## Troubleshooting

### Loki Not Ready

```bash
docker logs docuchat-loki
```

### No Logs Found

1. Check Alloy is running:
   ```bash
   docker logs docuchat-alloy
   ```

2. Verify log file exists:
   ```bash
   ls -la logs/linux.log
   ```

3. Check Alloy configuration:
   ```bash
   cat backend/src/config/config.alloy
   ```

### Backend Errors

```bash
docker logs docuchat-backend
```

## Architecture Overview

```
User Query → API Endpoint → Log Retrieve Agent → Loki
                                    ↓
                          Log Analysis Agent
                                    ↓
                            Solution Agent
                                    ↓
                          Comprehensive Response
```

## Agent Workflow

1. **Log Retrieve Agent**:
   - Parses time range from query
   - Queries Loki for logs
   - Returns formatted log data

2. **Log Analysis Agent**:
   - Analyzes log patterns
   - Detects anomalies
   - Calculates anomaly score
   - Identifies error sources

3. **Solution Agent**:
   - Determines root cause
   - Generates actionable solutions
   - Provides context and severity

## Next Steps

- Integrate with alerting system
- Add more log sources
- Implement historical trend analysis
- Create dashboard for visualization
