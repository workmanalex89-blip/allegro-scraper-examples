# Allegro.pl scraper — runnable examples

Working code for the **[Allegro.pl Scraper](https://apify.com/marzi.ai/allegro-scraper)**
Actor on Apify: Allegro product, price, seller, stock and sales data from
Poland's largest marketplace, in Python, Node, cURL and from an AI agent.

Every example in this repository was run against live Allegro pages before
it was committed — the output quoted below is from those runs, not from an
illustration.

| | what it does | run |
|---|---|---|
| [`python/search_to_csv.py`](python/search_to_csv.py) | search Allegro, write a CSV | `python search_to_csv.py "powerbank 20000mah" 100` |
| [`python/every_seller_by_ean.py`](python/every_seller_by_ean.py) | every seller behind one barcode, cheapest first | `python every_seller_by_ean.py 5906849413085` |
| [`python/track_prices_daily.py`](python/track_prices_daily.py) | daily price tracking in SQLite: what moved, who left, who appeared | `python track_prices_daily.py` |
| [`node/search.mjs`](node/search.mjs) | the same search from Node | `node search.mjs "sluchawki bluetooth" 50` |
| [`curl/run_and_fetch.sh`](curl/run_and_fetch.sh) | a category to CSV with no SDK at all | `./run_and_fetch.sh` |
| [`agents/README.md`](agents/README.md) | hand the Actor to Claude, ChatGPT or any MCP client | — |

## Before you start

```bash
export APIFY_TOKEN=...        # Apify Console -> Settings -> API & Integrations
pip install apify-client      # for the Python examples
npm install apify-client      # for the Node example
```

The Actor costs **$1 per 1,000 records** delivered — failed pages,
duplicates and empty runs are not charged. Apify's Free plan comes with $5
of monthly credit and the charges draw on it, so everything in this
repository can be run against real Allegro data without paying anything of
your own.

## What one record is

One record is **one Allegro offer** — one seller's listing of a product.
Ask for every seller of a barcode and you get one record per seller:

```
EAN 5906849413085 - 116 offers

    28.88 zl  Kraina_Adwentu               BUY  SS
    29.99 zl  AJDUMM                            SS
    31.99 zl  VITALLBODY_PL                     SS
       35 zl  PLAZA-SKLEP                       SS
       ...
       99 zl  Greenwaze                         SS

116 offers from 17 sellers
buy box: 28.88 zl (Kraina_Adwentu); cheapest: 28.88 zl
```

One barcode delivered 116 records here, because that EAN sits on more than
one Allegro product card and each card has its own sellers. Records are what
is billed, so a run like this costs about 12 cents - set `maxTotalChargeUsd`
and the Actor stops at your cap.

Two field meanings are worth knowing before you build on the data:

- **`recentBuyers` is people, not units.** It is Allegro's own counter of
  buyers in the last 30 days, as printed on the product card. `unitsSold`,
  when an offer page shows it, is units.
- **`buyBox` is not always the cheapest offer.** The offer Allegro shows
  first on a product card is chosen by Allegro, not by price — so
  "undercut the cheapest" and "win the buy box" are different instructions
  to give a repricer.

A field Allegro does not show comes back `null`, never `0`.

## What the Actor reads

Give it any of these and it returns the same record shape:

- an **EAN/GTIN** — resolved to the Allegro product card, then to its sellers;
- an **offer or product link** — one offer, or every offer of the card with
  `allSellers`;
- a **seller** — their whole storefront;
- a **category** or a **search phrase** — walked page by page with Allegro's
  own sort, condition and price filters.

Fields include price, price with delivery, crossed-out price, delivery cost,
condition, rating and review count, review text, the 30-day buyer counter,
offer count on the card, stock, GTIN, buy box, Super Seller, seller rating,
specifications, images and the description.

## Three things this is used for

- **Price monitoring and repricing** — the current market behind a product:
  who sells it, at what price, who holds the buy box, who is selling and who
  is parked. [`track_prices_daily.py`](python/track_prices_daily.py) is a
  working skeleton.
- **Product and catalogue research** — a category or a search as a table:
  prices, sellers, buyer counters, ratings. Match your own catalogue to
  Allegro by EAN.
- **Feeding an AI agent** — typed input and output and a spending cap per
  run, which is what an unattended agent needs.
  [`agents/README.md`](agents/README.md) has the MCP configuration.

## Links

- **The Actor:** https://apify.com/marzi.ai/allegro-scraper
- **Full documentation:** https://apify.com/marzi.ai/allegro-scraper#readme
- **The product page:** https://marzi.ai/products/allegro-scraper/
- **History, estimates and monitoring** (what this Actor deliberately leaves
  out) live in Marzi's own products: https://marzi.ai/

Issues and pull requests on these examples are welcome. Questions about the
Actor itself go to the Issues tab on its Apify Store page.
