"""Daily price tracking: run, store, and report what moved since last time.

    pip install apify-client
    export APIFY_TOKEN=...
    python track_prices_daily.py          # today's run, compared with the last one

State lives in prices.sqlite next to this file, keyed by offer id, so the
script is safe to put on a cron or on an Apify schedule. It reports three
things a repricer cares about: price moves, offers that disappeared, and
sellers that appeared.
"""

import os
import sqlite3
import time

from apify_client import ApifyClient

ACTOR = "marzi.ai/allegro-scraper"
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.sqlite")

# what to watch - any mix of EANs, product cards, offer links or a category
WATCH = {
    "mode": "AUTO",
    "gtins": ["5906849413085"],
    "allSellers": True,
    "maxProducts": 200,
}


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.execute(
        "create table if not exists offers ("
        " offerId text primary key, title text, sellerName text,"
        " price real, seenAt integer, buyBox integer)"
    )
    return conn


def main() -> None:
    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor(ACTOR).call(run_input=WATCH, max_total_charge_usd=1.0)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    now = int(time.time())

    conn = connect()
    before = {
        row[0]: row
        for row in conn.execute("select offerId, title, sellerName, price, seenAt, buyBox from offers")
    }

    moved, appeared = [], []
    for item in items:
        oid = item["offerId"]
        price = item.get("price")
        old = before.get(oid)
        if old is None:
            appeared.append(item)
        elif price is not None and old[3] is not None and abs(price - old[3]) > 0.009:
            moved.append((item, old[3]))
        conn.execute(
            "insert into offers values (?,?,?,?,?,?)"
            " on conflict(offerId) do update set price=excluded.price,"
            " seenAt=excluded.seenAt, buyBox=excluded.buyBox",
            (oid, item.get("title"), item.get("sellerName"), price, now,
             1 if item.get("buyBox") else 0),
        )

    seen = {item["offerId"] for item in items}
    gone = [row for oid, row in before.items() if oid not in seen]
    conn.commit()

    print("%d offers read" % len(items))
    for item, old in moved:
        new = item.get("price")
        arrow = "down" if new < old else "up"
        print("  %-26s %7s -> %-7s %s" % ((item.get("sellerName") or "-")[:26], old, new, arrow))
    for item in appeared:
        print("  + %-26s %7s  new offer" % ((item.get("sellerName") or "-")[:26], item.get("price")))
    for row in gone:
        print("  - %-26s %7s  gone" % ((row[2] or "-")[:26], row[3]))
    if not (moved or appeared or gone) and before:
        print("  nothing moved since the last run")


if __name__ == "__main__":
    main()
