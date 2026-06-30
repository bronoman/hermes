# Hermes Agent Skills Repository

Production-ready skills for [HERMES Agent](https://hermes-agent.nousresearch.com/) — add cryptocurrencies, IoT smart homes, decentralized social networks, FTP deployments, and more.

## 🎯 Available Skills

### 💰 Financial & Crypto

#### Bitcoin Skill
Query Bitcoin blockchain data via [mempool.space](https://mempool.space/) API.
- Bitcoin addresses, blocks, fees, mining stats
- Lightning Network (LN) statistics
- UTXO lookup, transaction history, mempool analysis

**Installation:**
```bash
hermes skills install bronoman/hermes/bitcoin
```

**Quick Start:**
```bash
hermes bitcoin --address 1A1z7agoat3dLrUquqjqM5yuPYzjRWLRd
```

---

#### CoinGecko Skill
Cryptocurrency price data & market intelligence via [CoinGecko](https://www.coingecko.com/en) APIs.
- Live price feeds (USD, EUR, GBP, and 100+ fiat currencies)
- Market cap, volume, 24h changes
- DEX aggregator data, NFT market data
- Historical price trends

**Installation:**
```bash
hermes skills install bronoman/hermes/coingecko
```

**Quick Start:**
```bash
hermes coingecko --coin bitcoin --vs-currency usd
```

---

### 🏠 Smart Home & IoT

#### openHAB Skill
Control & monitor local smart home infrastructure via [openHAB](https://www.openhab.org/).
- Read device status (thermostats, lights, locks, sensors)
- Send commands (turn on/off, dim, set temperature)
- Query automation rules, item metadata
- Real-time event subscriptions

**Installation:**
```bash
hermes skills install bronoman/hermes/openhab
```

**Quick Start:**
```bash
hermes openhab --host 192.168.255.255:8080 --action status
hermes openhab --item "LivingRoom_Light" --command ON
```

---

### 📡 Decentralized Social

#### Nostr Skill
Publish & retrieve content from [Nostr](https://en.wikipedia.org/wiki/Nostr) relays (decentralized social protocol).
- Read notes from relays
- Publish notes (signed with your private key)
- Metadata queries, relay management
- Cross-relay note aggregation

**Installation:**
```bash
hermes skills install bronoman/hermes/nostr
```

**Quick Start:**
```bash
hermes nostr --relay relay.primal.net --action read --limit 10
hermes nostr --relay relay.damus.io --action publish --content "Hello Nostr!"
```

---

### 📁 File Transfer & Deployment

#### FTP Skill ⭐ NEW
Production-ready FTP client for automated deployments, backups, and file management.
- Upload/download files with binary-safe transfers
- Sync directories with smart skip (identical file detection)
- Recursive backups with timestamp preservation
- Full directory listing, rename, delete, chmod operations
- Comprehensive error handling, timeouts, retry logic

**Installation:**
```bash
hermes skills install bronoman/hermes/ftp
```

**Setup:**
Add FTP credentials to `~/.hermes/.env`:
```bash
FTP_HOST=ftp.example.com
FTP_USER=username
FTP_PASS=password
FTP_PORT=21
FTP_PASSIVE=true
FTP_TIMEOUT=30
```

**Quick Start:**
```bash
# Test connection
hermes ftp --command test

# Upload file
hermes ftp --command upload --local ./pitch.html --remote /public_html/

# Sync directory (smart skip on identical files)
hermes ftp --command sync-upload --local ./dist --remote /public_html/

# Backup entire remote directory
hermes ftp --command backup --remote /documents --local ~/backups/docs/

# List remote directory
hermes ftp --command list --path /
```

**Features:**
- ✅ Binary-safe transfers (safe for all file types)
- ✅ Passive mode (default, recommended for NAT/firewalls)
- ✅ Configurable timeouts & retry logic
- ✅ JSON output (scriptable, CI/CD-friendly)
- ✅ Recursive sync with skip on identical files
- ✅ Full CRUD on remote files (delete, rename, chmod, mkdir)

**Use Cases:**
- 🚀 Website deployments (upload build artifacts)
- 📦 Backup automation (scheduled backups via cron)
- 🤖 CI/CD integration (upload test results, logs)
- 📄 Report submission (automated report uploads)
- 🔄 Mirroring (sync between servers)

See [FTP Skill Documentation](./ftp/SKILL.md) for complete reference.

---

## 🛣️ Roadmap

### In Evaluation
- yFinance (stock market data)
- SFTP (secure file transfer)
- Google Calendar (OAuth2 integration)
- Notion Sync (bi-directional database sync)

### Planned
- Amazon.de product research & shopping
- eBay.de product research & shopping
- Email (IMAP/SMTP with Hermes)
- Telegram bot integration

---

## 📚 Skill Structure

Each skill directory contains:
```
skill-name/
├── SKILL.md              # Complete documentation (API, examples, troubleshooting)
├── README.md             # Quick start guide
├── LICENSE               # MIT license
├── scripts/
│   └── <skill-name>.py   # Main CLI script
├── examples/             # Real-world usage examples
│   ├── deploy.sh
│   ├── backup.sh
│   └── ...
└── references/
    └── api-reference.md  # Optional: detailed API docs
```

---

## 🚀 Installation

### Option 1: Install Individual Skill
```bash
hermes skills install bronoman/hermes/ftp
hermes skills install bronoman/hermes/bitcoin
```

### Option 2: Clone Entire Repository
```bash
git clone https://github.com/bronoman/hermes.git ~/.hermes/skills/community
```

### Option 3: Manual Copy
```bash
mkdir -p ~/.hermes/skills/productivity/ftp
cp -r ftp/* ~/.hermes/skills/productivity/ftp/
```

Verify installation:
```bash
hermes skills list | grep ftp
```

---

## 🔧 Configuration

All skills use environment variables for credentials. Add to `~/.hermes/.env`:

```bash
# FTP
FTP_HOST=ftp.example.com
FTP_USER=username
FTP_PASS=password

# Bitcoin / CoinGecko
# (No auth required — uses free public APIs)

# openHAB
OPENHAB_HOST=192.168.255.255:8080
OPENHAB_USERNAME=username
OPENHAB_PASSWORD=password

# Nostr
NOSTR_RELAYS=relay.primal.net,relay.damus.io
NOSTR_NSEC=nsec1...  # Your Nostr private key
```

Credentials are **local-only** — never uploaded to cloud or shared with third parties.

---

## 📖 Usage Examples

### Deploy Website via FTP
```bash
# Backup current version
hermes ftp --command backup --remote /public_html --local ~/backups/site-backup-$(date +%Y%m%d)/

# Upload new build
hermes ftp --command sync-upload --local ./dist --remote /public_html/
```

### Query Bitcoin Blockchain
```bash
hermes bitcoin --address 1A1z7agoat3dLrUquqjqM5yuPYzjRWLRd --include-mempool
```

### Monitor Smart Home
```bash
hermes openhab --item "Thermostat_Temperature" --action get
```

### Publish to Nostr
```bash
hermes nostr --relay relay.primal.net --action publish --content "Just pushed v1.0 to production!"
```

---

## 🤝 Contributing

PRs welcome! Please include:

1. **Documentation** (SKILL.md with API reference, examples, troubleshooting)
2. **Tests** (test scripts that verify functionality)
3. **Examples** (real-world usage patterns in `examples/`)
4. **LICENSE** (MIT or compatible)

### Adding a New Skill

Create a directory with this structure:
```
my-skill/
├── SKILL.md              # Complete documentation
├── README.md             # Quick start
├── LICENSE               # MIT
├── scripts/my-skill.py   # Implementation
└── examples/             # Usage examples
```

Then submit a PR!

---

## 📝 License

All skills in this repository are licensed under the **MIT License** — see individual LICENSE files.

---

## 🔗 Links

- **Hermes Agent Docs:** https://hermes-agent.nousresearch.com/docs
- **Bitcoin (mempool.space):** https://mempool.space/api
- **CoinGecko API:** https://www.coingecko.com/en/api/documentation
- **openHAB API:** https://www.openhab.org/docs/configuration/restdocs/
- **Nostr Protocol:** https://github.com/nostr-protocol/nostr

---

## 📧 Support

- **Issues:** https://github.com/bronoman/hermes/issues
- **Discussions:** https://github.com/bronoman/hermes/discussions
- **Hermes Forum:** https://hermes-agent.nousresearch.com/community

---

**Last Updated:** 2026-06-30 | **Maintained by:** @bronoman
