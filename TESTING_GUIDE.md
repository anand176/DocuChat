# Testing Guide for Refactored Log Monitoring System

## Step 1: Rebuild and Start Services

The backend is currently rebuilding with the updated dependencies. Once complete:

```bash
# Start all services
docker-compose up -d

# Verify all services are running
docker-compose ps
```

Expected services:
- ✅ docuchat-backend (port 8000)
- ✅ docuchat-loki (port 3100)
- ✅ docuchat-prometheus (port 9090)
- ✅ docuchat-alloy (port 12345)
- ✅ docuchat-postgres (port 5432)

## Step 2: Verify Loki is Ready

```bash
curl http://localhost:3100/ready
```

Expected: `ready`

## Step 3: Check Backend Logs

```bash
docker logs docuchat-backend -f
```

Look for:
- ✅ "Application startup complete"
- ✅ "Database session service initialized"
- ✅ No import errors for `google.adk`

## Step 4: Test the Log Monitoring Endpoint

### Option A: Simple curl test (adjust auth as needed)

```bash
curl -X POST http://localhost:8000/agents/log_monitoring \
  -H "Content-Type: application/json" \
  -d '{"query": "Is there an issue in the last 1 hour?"}'
```

### Option B: Python test script

```python
import requests

response = requests.post(
    "http://localhost:8000/agents/log_monitoring",
    json={"query": "Is there an issue in the last 1 hour?"}
)

print("Status:", response.status_code)
print("Response:", response.json())
```

### Option C: Test with session continuity

```python
import requests

# First request
r1 = requests.post(
    "http://localhost:8000/agents/log_monitoring",
    json={"query": "Check logs for the last 1 hour"}
)
print("Response 1:", r1.json())
session_id = r1.json().get("session_id")

# Follow-up request (should remember context)
r2 = requests.post(
    "http://localhost:8000/agents/log_monitoring",
    json={
        "query": "What's the severity?",
        "session_id": session_id
    }
)
print("Response 2:", r2.json())
```

## Step 5: What to Look For

### Success Response
```json
{
  "status": "success",
  "response": "I analyzed the logs from the last hour and found 68 authentication failures from IP 218.188.2.4, indicating a potential brute force attack...",
  "session_id": "abc-123-def-456"
}
```

### Backend Logs (docker logs docuchat-backend)
```
INFO: Agent request: user=..., agent=log_monitoring_agent, app=log_monitoring_app
INFO: Creating runner for log_monitoring_app:log_monitoring_agent
INFO: Agent request completed: user=...
```

## Step 6: Verify Alloy is Collecting Logs

```bash
# Check Alloy logs
docker logs docuchat-alloy

# Query Loki for logs
curl -G -s "http://localhost:3100/loki/api/v1/query" \
  --data-urlencode 'query={job="system-logs"}' | jq
```

## Troubleshooting

### If you get "ModuleNotFoundError: No module named 'google.adk'"
- The rebuild should fix this
- Check: `docker logs docuchat-backend` for pip install errors

### If no logs are found
- Wait 10-15 seconds for Alloy to ingest logs
- Check: `docker logs docuchat-alloy`
- Verify: `ls -la logs/linux.log` (file exists)

### If Loki is not ready
- Check: `docker logs docuchat-loki`
- Restart: `docker-compose restart loki`

## Quick Test Commands

```bash
# Check all services
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check Loki health
curl http://localhost:3100/ready

# Check Prometheus health
curl http://localhost:9090/-/ready

# View backend logs
docker logs docuchat-backend -f

# Restart everything
docker-compose restart
```

## Expected Workflow

1. User sends query: "Is there an issue in the last 1 hour?"
2. Root agent (`log_monitoring_agent`) receives query
3. Planner decides to call `log_retrieve_agent`
4. Log retrieve agent fetches logs from Loki
5. Planner calls `log_analysis_agent` with logs
6. Analysis agent detects anomalies (if any)
7. Planner calls `solution_agent` (if anomalies found)
8. Solution agent provides root cause and solutions
9. Root agent synthesizes final response
10. User receives comprehensive answer

## Success Criteria

✅ No import errors for `google.adk`
✅ Backend starts successfully
✅ Loki is ready and receiving logs
✅ API endpoint responds with agent-generated text
✅ Session continuity works (follow-up questions remember context)
✅ Agent logs show proper delegation to sub-agents
