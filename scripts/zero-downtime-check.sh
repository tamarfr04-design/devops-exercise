#!/usr/bin/env bash
# Sends requests in a loop, prints status code + version, counts failures.
# Stop with Ctrl+C to see the summary.
URL="${1:-http://localhost/}"
ok=0
fail=0
trap 'echo; echo "OK: $ok  FAILED: $fail"; exit' INT

while true; do
  resp=$(curl -s --max-time 2 -w $'\n%{http_code}' "$URL")
  code=${resp##*$'\n'}
  ver=$(echo "$resp" | grep -o 'Version:</strong> [^<]*' | cut -d' ' -f2 | cut -c1-7)
  if [ "$code" = "200" ]; then ok=$((ok+1)); else fail=$((fail+1)); fi
  echo "$(date +%T) $code $ver"
  sleep 0.1
done