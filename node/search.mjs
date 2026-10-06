// Search Allegro from Node and print the cheapest offers.
//
//   npm install apify-client
//   APIFY_TOKEN=... node search.mjs "sluchawki bluetooth" 50

import { ApifyClient } from 'apify-client';

const ACTOR = 'marzi.ai/allegro-scraper';
const phrase = process.argv[2] ?? 'sluchawki bluetooth';
const limit = Number(process.argv[3] ?? 50);

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

const run = await client.actor(ACTOR).call(
    {
        mode: 'SEARCH',
        searchQuery: phrase,
        maxProducts: limit,
        sort: 'price_asc',
        condition: 'new',
        includeParameters: false,
        includeImages: false,
        includeDescription: false,
    },
    { maxTotalChargeUsd: 1 },
);

const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(`${items.length} records for "${phrase}"`);

for (const offer of items.slice(0, 20)) {
    const buyers = offer.recentBuyers === null ? '-' : `${offer.recentBuyers} bought/30d`;
    console.log(
        `${String(offer.price).padStart(9)} zl  ${(offer.sellerName ?? '-').padEnd(26).slice(0, 26)}  ${buyers}`,
    );
}
