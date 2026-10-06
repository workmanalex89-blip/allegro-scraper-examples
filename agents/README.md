# Let an AI agent run it

Apify's MCP server exposes any Store Actor as a tool, so an agent can run
the Allegro scraper without any glue code of yours. Three things make this
Actor safe to hand to an agent:

- **typed input and output schemas** — the agent cannot invent a field;
- **no interactive steps** — one call in, one dataset out;
- **a budget per run** — `maxTotalChargeUsd` stops the Actor at your cap,
  whatever the agent asks for.

## Claude Code

```bash
claude mcp add apify --transport http https://mcp.apify.com \
  --header "Authorization: Bearer $APIFY_TOKEN"
```

Then ask in plain words:

> Use the Apify Actor `marzi.ai/allegro-scraper` to find every Allegro
> seller of EAN 5906849413085, and tell me who holds the buy box and
> whether they are the cheapest.

## Claude Desktop / any MCP client

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

## OpenAI Responses API

```python
import os
from openai import OpenAI

client = OpenAI()
response = client.responses.create(
    model="gpt-5.5",
    input=(
        "Find every Allegro seller of EAN 5906849413085 with the Apify Actor "
        "marzi.ai/allegro-scraper (mode AUTO, gtins, allSellers true). "
        "Report the buy box price, the cheapest price and the seller count."
    ),
    tools=[{
        "type": "mcp",
        "server_label": "apify",
        "server_url": "https://mcp.apify.com",
        "authorization": os.environ["APIFY_TOKEN"],
        "require_approval": "never",
    }],
)
print(response.output_text)
```

## What to tell the agent about the data

Two field meanings decide whether an agent's conclusion is right:

- `recentBuyers` is **people who bought in the last 30 days**, as Allegro
  prints it on the product card — not units and not revenue. `unitsSold`,
  when the offer page shows it, is units.
- `buyBox` is the offer Allegro shows first on the product card. It is
  **not always the cheapest** — telling an agent to "undercut the cheapest"
  and telling it to "win the buy box" are two different instructions.

A field Allegro does not show comes back `null`, never `0`. An agent that
treats `null` as zero will report a market of free products.
