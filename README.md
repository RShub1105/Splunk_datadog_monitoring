# Splunk & Datadog Observability

A simple **Application Health Monitoring** project built with **Python Flask**, **Splunk Enterprise**, **Datadog**, and **Docker** to demonstrate basic observability, log analysis, infrastructure monitoring, dashboards, and alerts.

## 🚀 Features

* Application logging with Python
* Structured log collection
* Splunk dashboards & SPL searches
* Datadog infrastructure monitoring
* CPU, Memory & Disk metrics
* Simulated errors and slow responses
* Docker Compose deployment

## 🛠️ Tech Stack

* Python (Flask)
* Splunk Enterprise
* Datadog Agent
* Docker & Docker Compose
* Linux
* Git

## 📂 Project Structure

```text
.
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── generate_traffic.sh
├── logs/
└── README.md
```

## ▶️ Run

```bash
git clone <repository-url>
cd splunk-datadog-observability-demo

docker compose up --build
```

Application: **http://localhost:5000**

Splunk: **http://localhost:8000**

## 📊 What is Monitored?

* Application logs
* Login events
* Error events
* Slow requests
* Response time
* CPU usage
* Memory usage
* Disk usage

## 📌 Skills Demonstrated

* Observability
* Log Analysis
* Monitoring & Alerting
* Splunk (SPL, Dashboards)
* Datadog Monitoring
* Docker
* Linux
* Python

---

**Designed as a beginner-friendly Observability & SRE project for learning Splunk and Datadog.**
