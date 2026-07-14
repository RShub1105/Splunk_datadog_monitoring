# Application Health Monitoring using Splunk and Datadog

Simple observability project that runs a Python Flask application, generates useful application logs, sends those logs to Splunk, and monitors host/container metrics in Datadog.

## Architecture

```text
User
  |
Flask App
  |
+-------------------+
|                   |
Application Logs    Metrics
|                   |
Splunk              Datadog Agent
|                   |
Dashboard/Alerts    Dashboard/Alerts
```

## What This Builds

- Flask app with home, login, health, error, slow response, CPU load, and metrics endpoints
- Structured application logs in `logs/app.log`
- Docker Compose stack for Flask, Splunk Enterprise, and optional Datadog Agent
- SPL searches for errors, warnings, login events, response time, and slow requests
- Alert examples for application errors and infrastructure thresholds

## Project Structure

```text
splunk-datadog-demo/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── generate_traffic.sh
├── logs/
│   └── .gitkeep
├── screenshots/
│   └── .gitkeep
└── README.md
```

## Run Locally with Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open:

- `http://localhost:5000`
- `http://localhost:5000/login`
- `http://localhost:5000/health`
- `http://localhost:5000/error`
- `http://localhost:5000/slow`
- `http://localhost:5000/cpu`
- `http://localhost:5000/metrics`

Generate repeat traffic:

```bash
chmod +x generate_traffic.sh
./generate_traffic.sh
```

## Run with Docker Compose

Copy the environment file:

```bash
cp .env.example .env
```

Start Flask and Splunk:

```bash
docker compose up --build
```

Start Flask, Splunk, and Datadog Agent:

```bash
DD_API_KEY=your_datadog_api_key docker compose --profile datadog up --build
```

URLs:

- Flask: `http://localhost:5000`
- Splunk: `http://localhost:8000`
- Splunk username: `admin`
- Splunk password: value of `SPLUNK_PASSWORD` in `.env`

## Configure Splunk Log Monitoring

The Compose file mounts Flask logs into the Splunk container at:

```text
/var/log/flask-app/app.log
```

In Splunk:

1. Go to `Settings > Add Data`.
2. Select `Monitor`.
3. Select `Files & Directories`.
4. Enter `/var/log/flask-app/app.log`.
5. Set source type to `_json` only if you change the app to JSON logs. For the current log format, use automatic detection or a custom source type.
6. Set index to `main`.
7. Save.

## Useful SPL Queries

All logs:

```spl
index=main source="/var/log/flask-app/app.log"
```

Errors:

```spl
index=main source="/var/log/flask-app/app.log" ERROR
```

Warnings:

```spl
index=main source="/var/log/flask-app/app.log" WARNING
```

Login events:

```spl
index=main source="/var/log/flask-app/app.log" login_success
```

Slow responses:

```spl
index=main source="/var/log/flask-app/app.log" slow_response
```

Count by log level:

```spl
index=main source="/var/log/flask-app/app.log"
| rex "\s(?<log_level>INFO|WARNING|ERROR)\s"
| stats count by log_level
```

Errors over time:

```spl
index=main source="/var/log/flask-app/app.log" ERROR
| timechart count
```

Average response time by endpoint:

```spl
index=main source="/var/log/flask-app/app.log" request_completed
| rex "endpoint=(?<endpoint>\S+)"
| rex "duration_ms=(?<duration_ms>\d+)"
| stats avg(duration_ms) as avg_ms max(duration_ms) as max_ms by endpoint
| sort - avg_ms
```

HTTP status count:

```spl
index=main source="/var/log/flask-app/app.log"
| rex "status=(?<status>\d+)"
| stats count by status
```

## Splunk Dashboard Panels

Create a dashboard with these panels:

- Total logs: `index=main source="/var/log/flask-app/app.log" | stats count as total_logs`
- Errors: `index=main source="/var/log/flask-app/app.log" ERROR | stats count as errors`
- Warnings: `index=main source="/var/log/flask-app/app.log" WARNING | stats count as warnings`
- Login events: `index=main source="/var/log/flask-app/app.log" login_success | timechart count`
- Response time: use the average response time SPL query above
- Errors over time: use the errors over time SPL query above

## Splunk Alert

Example alert: more than 5 errors in 5 minutes.

Search:

```spl
index=main source="/var/log/flask-app/app.log" ERROR earliest=-5m
| stats count as error_count
| where error_count > 5
```

Recommended actions:

- Email notification
- Webhook to an incident tool
- Slack or Teams integration if available

## Datadog Setup

Create a Datadog API key and run:

```bash
DD_API_KEY=your_datadog_api_key docker compose --profile datadog up --build
```

In Datadog, create dashboard widgets for:

- CPU usage
- Memory usage
- Disk usage
- Network traffic
- Load average
- Running containers/processes

Useful monitor examples:

- CPU usage greater than `80%`
- Memory usage greater than `85%`
- Disk usage greater than `90%`
- Flask container is not running

## Generate CPU Load

```bash
curl "http://localhost:5000/cpu?limit=50000000"
```

Increase `limit` for a heavier test. Watch CPU usage rise in Datadog.

## Screenshots to Capture

Place project screenshots in `screenshots/`:

- `dashboard.png`: Splunk or Datadog dashboard
- `splunk_search.png`: SPL query results
- `alerts.png`: configured alert

## Resume Points

- Developed a Python Flask application that generates normal, warning, and error logs.
- Configured Splunk Enterprise to collect, index, search, and alert on application logs.
- Created SPL searches and dashboard panels for login events, errors, warnings, slow responses, and response time.
- Integrated Datadog Agent for CPU, memory, disk, network, load, and container monitoring.
- Simulated incidents with error, slow response, and CPU intensive endpoints.

Technologies: Python, Flask, Docker, Splunk, Datadog, Linux, Git.
