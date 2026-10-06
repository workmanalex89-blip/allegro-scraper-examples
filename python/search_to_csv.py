"""Search Allegro and write the results to a CSV.

    pip install apify-client
    export APIFY_TOKEN=...
    python search_to_csv.py "powerbank 20000mah" 100

One record is one Allegro offer. Money is PLN exactly as the page shows it;
a field Allegro does not show is null, never a zero.
"""

import csv
import os
import sys

from apify_client import ApifyClient

ACTOR = "marzi.ai/allegro-scraper"
COLUMNS = [
    "offerId", "title", "brand", "price", "priceWithDelivery", "currency",
    "sellerName", "sellerSuperSeller", "rating", "ratingCount",
    "recentBuyers", "offersCount", "buyBox", "url",
]


def main() -> None:
    phrase = sys.argv[1] if len(sys.argv) > 1 else "powerbank 20000mah"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor(ACTOR).call(
        run_input={
            "mode": "SEARCH",
            "searchQuery": phrase,
            "maxProducts": limit,
            "sort": "popularity",
            # listing cards are enough for a price sweep; leave the heavy
            # fields off and the run stays at one page per ~60 records
            "includeParameters": False,
            "includeImages": False,
            "includeDescription": False,
        },
        # the Actor stops by itself when this cap is reached
        max_total_charge_usd=1.0,
    )

    out = "allegro-%s.csv" % phrase.replace(" ", "-")
    rows = 0
    with open(out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            writer.writerow(item)
            rows += 1

    print("%d records -> %s" % (rows, out))
    summary = client.key_value_store(run["defaultKeyValueStoreId"]).get_record("RUN_SUMMARY")
    if summary:
        value = summary["value"]
        print("pages read: %s, skipped: %s" % (value.get("pagesRead"), value.get("invalid")))


if __name__ == "__main__":
    main()
