#!/usr/bin/env bash
# Run the Actor and download the dataset as CSV - no SDK, just the API.
#
#   APIFY_TOKEN=... ./run_and_fetch.sh
set -euo pipefail

: "${APIFY_TOKEN:?set APIFY_TOKEN}"
ACTOR="marzi.ai~allegro-scraper"

# Start the run and wait for it to finish (waitForFinish is in seconds).
RUN=$(curl -sS -X POST \
  "https://api.apify.com/v2/acts/$ACTOR/runs?token=$APIFY_TOKEN&maxTotalChargeUsd=1&waitForFinish=300" \
  -H 'Content-Type: application/json' \
  -d '{
        "mode": "CATEGORY",
        "startUrls": [{ "url": "https://allegro.pl/kategoria/powerbanki-252023" }],
        "maxProducts": 200,
        "sort": "popularity"
      }')

DATASET=$(printf '%s' "$RUN" | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"]["defaultDatasetId"])')
STATUS=$(printf '%s' "$RUN" | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"]["status"])')
echo "run $STATUS, dataset $DATASET"

curl -sS "https://api.apify.com/v2/datasets/$DATASET/items?format=csv&token=$APIFY_TOKEN" -o allegro.csv
echo "$(($(wc -l < allegro.csv) - 1)) records -> allegro.csv"

# What the run did, and why anything was skipped:
curl -sS "https://api.apify.com/v2/actor-runs/$(printf '%s' "$RUN" | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"]["id"])')/key-value-store/records/RUN_SUMMARY?token=$APIFY_TOKEN"
