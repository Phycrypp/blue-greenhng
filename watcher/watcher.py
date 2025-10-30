import os
import time
import re
import requests
from collections import deque

LOG_FILE = "/var/log/nginx/bluegreen.log"

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
ACTIVE_POOL = os.getenv("ACTIVE_POOL", "blue")
ERROR_RATE_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", "2"))
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", "200"))
ALERT_COOLDOWN_SEC = int(os.getenv("ALERT_COOLDOWN_SEC", "300"))
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"

window = deque(maxlen=WINDOW_SIZE)
last_pool = ACTIVE_POOL
last_alert_ts = 0

line_re = re.compile(
    r'pool="(?P<pool>[^"]*)".*?release="(?P<release>[^"]*)".*?upstream_status="(?P<ustatus>[^"]*)".*?upstream_addr="(?P<uaddr>[^"]*)"'
)

def send_slack(msg: str):
    if not SLACK_WEBHOOK_URL:
        print("⚠️ No SLACK_WEBHOOK_URL configured. Skipping:", msg)
        return
    try:
        r = requests.post(SLACK_WEBHOOK_URL, json={"text": msg}, timeout=5)
        print(f"✅ Slack ({r.status_code}): {msg}")
    except Exception as e:
        print(f"❌ Slack error: {e}")

def cooldown(now: float) -> bool:
    global last_alert_ts
    if now - last_alert_ts < ALERT_COOLDOWN_SEC:
        return True
    last_alert_ts = now
    return False

def follow(path: str):
    while not os.path.exists(path):
        print(f"⏳ waiting for {path} ...")
        time.sleep(1)
    with open(path, "r") as f:
        for _ in f:
            pass
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
            yield line

def main():
    global last_pool
    print("👀 Watcher started — monitoring Nginx logs for failovers & errors...")
    print(f"→ Watching file: {LOG_FILE}")
    print(f"→ Active pool: {ACTIVE_POOL}")
    print(f"→ Error threshold: {ERROR_RATE_THRESHOLD}% over {WINDOW_SIZE} requests")

    for line in follow(LOG_FILE):
        m = line_re.search(line)
        if not m:
            continue

        pool = m.group("pool") or "unknown"
        release = m.group("release") or "unknown"
        upstream_status = (m.group("ustatus") or "").strip()
        upstream_addr = (m.group("uaddr") or "").strip()

        # record success/error
        is_error = upstream_status.startswith("5") if upstream_status else False
        window.append((is_error, pool))

        now = time.time()

        # 1️⃣ Failover alert
        if pool not in ("", "unknown") and pool != last_pool:
            if not MAINTENANCE_MODE and not cooldown(now):
                msg = (
                    f"🚨 *Failover detected*\n"
                    f"{last_pool} → {pool} | release={release} | upstream={upstream_addr or 'n/a'}"
                )
                send_slack(msg)
            last_pool = pool

        # 2️⃣ High error-rate alert
        if len(window) >= 10:
            total = len(window)
            errors = sum(1 for e, _ in window if e)
            err_pct = (errors / total) * 100
            if err_pct >= ERROR_RATE_THRESHOLD:
                if not MAINTENANCE_MODE and not cooldown(now):
                    send_slack(
                        f"⚠️ High upstream error rate {err_pct:.2f}% "
                        f"over last {total} req (threshold={ERROR_RATE_THRESHOLD}%)"
                    )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Fatal error in watcher: {e}")
