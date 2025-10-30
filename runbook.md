# 🧭 Blue-Green Deployment Runbook

This document explains how to operate, monitor, and respond to alerts in the **blue-green deployment** environment.  
The system uses **Nginx logs** for visibility and a **Python watcher** to detect failovers or high error rates, sending alerts to **Slack**.

---

## 🔍 Overview

### Components
| Service | Description |
|----------|-------------|
| **nginx** | Reverse proxy and traffic router between `app_blue` and `app_green`. Logs all requests with metadata. |
| **app_blue** | The primary (active) pool by default. |
| **app_green** | The standby (backup) pool used during failover. |
| **alert_watcher** | Python service that tails Nginx logs and posts alerts to Slack when failover or error-rate thresholds are triggered. |

Logs are written to `/var/log/nginx/bluegreen.log` and monitored in real time by the watcher.

---

## ⚙️ Environment Variables

These are configured in the `.env` file or `docker-compose.yml`:

| Variable | Description | Example |
|-----------|-------------|----------|
| `SLACK_WEBHOOK_URL` | Slack webhook used for alerts. | `<SLACK_WEBHOOK_URL>` |
| `ACTIVE_POOL` | Initial active pool (`blue` or `green`). | `blue` |
| `ERROR_RATE_THRESHOLD` | % of 5xx errors to trigger alert. | `2` |
| `WINDOW_SIZE` | Number of recent requests to evaluate. | `200` |
| `ALERT_COOLDOWN_SEC` | Seconds between repeated alerts. | `300` |
| `MAINTENANCE_MODE` | Suppresses alerts if set to `true`. | `false` |

---

## 🚨 Alert Types

### 1️⃣ Failover Detected
Triggered when Nginx routes requests to a different pool than `ACTIVE_POOL`.

**Slack message example:**

