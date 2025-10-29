#!/bin/bash
set -euo pipefail
curl -sf http://localhost:8080/healthz >/dev/null || { echo "gateway down"; exit 1; }
curl -sf -XPOST "http://localhost:8081/chaos/start?mode=error" >/dev/null || true
pass=0; total=40
for i in $(seq 1 $total); do
  hdrs=$(curl -sI --max-time 3 http://localhost:8080/version || true)
  code=$(printf "%s" "$hdrs" | awk '/^HTTP/{print $2;exit}')
  pool=$(printf "%s" "$hdrs" | awk -F": " '/^X-App-Pool:/{print $2;exit}')
  [ "$code" = "200" ] && [ "$pool" = "green" ] && pass=$((pass+1))
  sleep 0.2
done
echo "green=${pass}/${total} ($((100*pass/total))%)"
curl -sf -XPOST "http://localhost:8081/chaos/stop" >/dev/null || true
