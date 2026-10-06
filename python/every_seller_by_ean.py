"""Every Allegro seller behind one barcode, cheapest first.

    pip install apify-client
    export APIFY_TOKEN=...
    python every_seller_by_ean.py 5906849413085

The Actor resolves the EAN/GTIN to the Allegro product card, then reads that
card's offer list - one record per seller, with the buy box flagged. This is
the cheap way to ask "who else sells this and for how much": the offer list
holds ~60 offers on one page, while one offer link is one page per record.
"""

import os
import sys

from apify_client import ApifyClient

ACTOR = "marzi.ai/allegro-scraper"


def main() -> None:
    ean = sys.argv[1] if len(sys.argv) > 1 else "5906849413085"

    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor(ACTOR).call(
        run_input={
            "mode": "AUTO",
            "gtins": [ean],
            "allSellers": True,   # walk the product card's offer list
            "maxProducts": 200,
        },
        max_total_charge_usd=1.0,
    )

    offers = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    offers.sort(key=lambda o: o.get("price") or 0)

    print("EAN %s - %d offers" % (ean, len(offers)))
    for offer in offers:
        print(
            "%9s zl  %-28s %-4s %-5s  %s"
            % (
                offer.get("price"),
                (offer.get("sellerName") or "-")[:28],
                "BUY" if offer.get("buyBox") else "",
                "SS" if offer.get("sellerSuperSeller") else "",
                offer.get("stockLabel") or "",
            )
        )

    buy_box = next((o for o in offers if o.get("buyBox")), None)
    sellers = len({o.get("sellerName") for o in offers if o.get("sellerName")})
    print("\n%d offers from %d sellers" % (len(offers), sellers))
    if buy_box and offers:
        cheapest = offers[0].get("price")
        print("buy box: %s zl (%s); cheapest: %s zl" % (buy_box.get("price"), buy_box.get("sellerName"), cheapest))
        if buy_box.get("price") != cheapest:
            print("the buy box is not the cheapest offer here - so 'undercut the "
                  "cheapest' and 'win the buy box' are two different instructions")


if __name__ == "__main__":
    main()
