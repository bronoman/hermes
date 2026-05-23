# Overview
This project is for new skills for [HERMES Agent](https://hermes-agent.nousresearch.com/).

## Skills
At the moment, the following skills are available here:
- Bitcoin
- Coingecko
- Nostr
- OpenHAB
Roadmap:
- Amazon.de product research & shopping
- Ebay.de product research & shopping
- yFinance - under evaluation

### Bitcoin Skill
[Bitcoin](https://bitcoin.org) skill - allows HERMES Agent to connect to the free [mempool.space](https://mempool.space/) API and retrieve Bitcoin blockchain data related to:
- bitcoin addresses
- blocks
- fees
- mining
- Lightning Network (LN) stats

#### Installation
```
hermes skills install bronoman/hermes-skills/bitcoin
```

### CoinGecko Skill
[CoinGecko](https://www.coingecko.com/en/coins/bitcoin) skill - allows HERMES Agent to retrieve cryptocurrency price data & related content using the CoinGecko APIs.
#### Installation
```
hermes skills install bronoman/hermes-skills/coingecko
```

### Nostr Skill
[Nostr](https://en.wikipedia.org/wiki/Nostr) skill - allows HERMES Agent to connect to Nostr relay/nodes and retrieve and publish notes/content to Nostr.
#### Installation
```
hermes skills install bronoman/hermes-skills/nostr
```

### openHAB Skill
[openHAB](https://www.openhab.org) skill - allows HERMES Agent to connect to a local openHAB smart home server, check its status, retrieve information (e.g. heat pump is running) and also switch items available in openHAB (e.g. turn on light in room x).
#### Installation
```
hermes skills install bronoman/hermes-skills/openhab
```
## Toolsets
In preparation - see README.md file in toolsets folder


## Additional Information
For details, please see the respective README.md and /references/DESCRIPTION.md files.

PRs welcome.
