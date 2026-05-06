---
name: nostr
description: "Complete, secure Nostr integration for Hermes Agent. Read events, draft posts, publish with explicit approval, Telegram cross-posting with images via Blossom (primary) + Picsur (local fallback)."
version: 2.1.0
author: "bronoman + Hermes local integration (May 2026)"
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [nostr, social, publishing, secure, blossom, decentralized, telegram]
    category: social
    requires_tools: [terminal]
required_environment_variables:
  - name: NOSTR_NSEC
    prompt: "Your nsec private key (nsec1...)"
    help: "Dedicated key recommended. Passed only to publish scripts, never exposed in logs or prompts."
    required_for: "Signing events"
    password: true
  - name: NOSTR_RELAYS
    prompt: "Comma-separated relays"
    default: "wss://relay.damus.io,wss://nostr.wine,wss://nos.lol"
    required_for: "All operations"
optional_environment_variables:
  - name: TELEGRAM_BOT_TOKEN
    prompt: "Telegram Bot Token (or type 'N/A' to disable)"
    help: "Create via @BotFather. Optional for Telegram cross-posting."
  - name: TELEGRAM_CHAT_ID
    prompt: "Telegram Chat/Channel ID (or type 'N/A' to disable)"
    help: "Use @userinfobot to get your ID."
  - name: PICSUR_URL
    prompt: "Local Picsur URL for testing (or type 'N/A')"
    default: "http://localhost:3000"
    help: "Used as fallback when Blossom upload fails."
---

# Nostr Secure Integration (v2.1)

**Skill Path:** `~/.hermes/skills/social-media/nostr`

Complete, production-ready Nostr client for Hermes with strong security and modern media support.

---

## Features Overview

| Feature                        | Status     | Signing Required | Media Support      |
|--------------------------------|------------|------------------|---------------------|
| Read Events                    | ✅         | No               | —                  |
| Draft Posts                    | ✅         | No               | —                  |
| Publish with Approval          | ✅         | Yes              | Yes                |
| Telegram → Nostr Cross-Post    | ✅ Optional | Yes              | Yes (Image + Text) |
| Blossom Upload (NIP-B7)        | ✅ Primary | —                | Yes                |
| Picsur Local Fallback          | ✅         | —                | Yes                |

---

## Security Architecture

Private key (`NOSTR_NSEC`) **never** reaches Hermes chat or logs.  
All publish operations require explicit user confirmation (`YES`).  
Read operations require **no private key**.

---

## Core Scripts

All scripts are in:  
`~/.hermes/skills/social-media/nostr/scripts/`

- `read.py` — Read-only operations  
- `draft.py` — Create unsigned drafts  
- `publish.py` — Sign + multi-relay publish (with approval)  
- `telegram_to_nostr.py` — Telegram + Image cross-post (Blossom primary, Picsur fallback)

---

## Quick Usage

### Reading
```bash
./scripts/read.py recent
./scripts/read.py mentions
./scripts/read.py search "Hermes Agent"
```

### Drafting
```bash
./scripts/draft.py "My first Nostr post 🚀"
```

### Publishing (Requires Approval)
```bash
./scripts/draft.py "My first Nostr post 🚀" > draft.json
./scripts/publish.py draft.json
# Type YES to confirm
```

### Telegram + Image Cross-Post
```bash
./scripts/telegram_to_nostr.py /path/to/image.jpg "Caption text"
./scripts/publish.py last_draft.json
```

---

## Skill Details

This skill provides **end-to-end Nostr integration**: read recent events, draft posts, sign events, and publish to multiple relays. Built with security-first design: private keys never logged, all publications require explicit user confirmation, and events are cryptographically verifiable.

**Verified Live:** April 26, 2026 — "I Just built a secure Nostr skill for Hermes Agent..." published to Damus, Primal, and relays globally.

---

## Security Architecture

### Three Security Zones

```
┌─────────────────────────────────────────────────────────┐
│ HERMES AGENT (chat, prompts, memory)                    │
│  - Never sees nsec or private key                       │
│  - Only manages workflows, drafts, approvals            │
└─────────────┬───────────────────────────────────────────┘
              │ APPROVAL GATE (requires "YES")
              ↓
┌─────────────────────────────────────────────────────────┐
│ SANDBOX SCRIPTS (scripts/read.py, publish.py, draft.py)│
│  - Reads $NOSTR_NSEC from environment only              │
│  - Never logs or echoes private key                     │
│  - Performs all cryptographic operations                │
│  - Returns only public results (event_id, pubkey, etc)  │
└─────────────┬───────────────────────────────────────────┘
              │ WebSocket (encrypted)
              ↓
┌─────────────────────────────────────────────────────────┐
│ NOSTR RELAYS (wss://)                                   │
│  - Receive signed events                                │
│  - Verify signatures independently                      │
│  - Broadcast globally                                   │
└─────────────────────────────────────────────────────────┘
```

### Security Rules (Always Enforced)

1. **Private keys pass via environment only** — never in prompts, function args, or logs.
2. **Every publish requires user confirmation** — type "YES" to proceed.
3. **Scripts are read-only or sign-only** — no mixed operations.
4. **Event JSON shown before signing** — full transparency.
5. **All operations logged with timestamps** — for audit trails.

---

## Core Operations

### 1. Reading Events (No Key Required)

Read public Nostr events without any private key exposure.

#### List Recent Notes

```bash
~/.hermes/nostr-env/bin/python3 ~/.hermes/skills/social-media/nostr/scripts/read.py recent
```

Returns JSON with up to 20 most recent text notes (kind 1) from relays.

**Output format:**
```json
{
  "status": "success",
  "command": "recent",
  "count": 20,
  "events": [
    {
      "id": "d7c3fde6351a0aa4...",
      "pubkey": "npub1luswyznmtrj906...",
      "created_at": "2026-04-26T04:31:00+00:00",
      "kind": 1,
      "content": "I Just built a secure Nostr skill for Hermes Agent 🔥"
    },
    ...
  ]
}
```

### 2. Drafting Posts (No Key Required)

Create unsigned event JSON for review before publishing.

```bash
~/.hermes/nostr-env/bin/python3 ~/.hermes/skills/social-media/nostr/scripts/draft.py \
  "I Just built a secure Nostr skill for Hermes Agent 🔥"
```

**Output:**
```json
{
  "status": "success",
  "message": "Draft created - review and approve before publishing",
  "draft": {
    "id": "",
    "pubkey": "",
    "created_at": 1714166400,
    "kind": 1,
    "tags": [],
    "content": "I Just built a secure Nostr skill for Hermes Agent 🔥",
    "sig": ""
  },
  "instructions": "Copy this JSON, edit if needed, then run: publish.py"
}
```

**Features:**
- No signing required
- Full transparency (see exact JSON before publish)
- Can edit content, tags, kind
- Ready for approval flow

### 3. Drafting Posts using Telegram + Nostr Cross-Post with Image

Use input from Telegram (optional: with image) to create unsigned event JSON for review before publishing.

```bash
./scripts/telegram_to_nostr.py /path/to/image.jpg "My caption with image"
```

**Features:**
- No signing required
- Full transparency (see exact JSON before publish)
- Can edit content, tags, kind
- Ready for approval flow

### 4. Publishing Events (Key Required + Approval)

Sign and publish with explicit user confirmation.

```bash
~/.hermes/nostr-env/bin/python3 ~/.hermes/skills/social-media/nostr/scripts/publish.py \
  draft.json
```

**Security checkpoint:**
```
⚠️  SECURITY CHECKPOINT — ABOUT TO SIGN AND PUBLISH
======================================================================

Content: I Just built a secure Nostr skill for Hermes Agent 🔥
Kind: 1
Tags: []

⚠️  This action is PERMANENT and CRYPTOGRAPHIC.
Type YES (uppercase) to proceed, or press Enter to cancel:
```

**On approval (type "YES"):**
1. Load nsec from `$NOSTR_NSEC` environment
2. Decode nsec (bech32 → trim 33 bytes to 32)
3. Create private key and sign event
4. Broadcast to all relays in `$NOSTR_RELAYS`
5. Return event_id for verification

**Success output:**
```json
{
  "status": "published",
  "event_id": "d7c3fde6351a0aa4...",
  "public_key": "npub1luswyznmtrj906...",
  "timestamp": "2026-04-26T04:31:08+00:00",
  "relays": [
    "wss://relay.damus.io",
    "wss://nostr.wine",
    "wss://nos.lol"
  ],
  "primal_url": "https://primal.net/e/d7c3fde6351a0aa4...",
  "message": "✅ Event published successfully"
}
```

---

## Critical Discovery: The 33-Byte Checksum Issue

**Problem (April 2026):** Publishing failed with `TypeError: privkey must be composed of 32 bytes`

**Root cause:** Bech32 encoding includes a 1-byte checksum. The `bech32.bech32_decode()` function returns all 33 bytes (32 key + 1 checksum). The secp256k1 library requires exactly 32 bytes.

**Solution:** Always trim to first 32 bytes:
```python
private_key_bytes = decoded[:32]  # CRITICAL FIX
```

**Key insight:** Bech32 checksums validate the encoding; they're not cryptographic material. Always trim to the actual key size (32 bytes for secp256k1).

---

## Event Kind Reference

| Kind | Purpose | Signable | Example |
|------|---------|----------|---------|
| 0 | User metadata | Yes | `{name, about, picture, nip05}` |
| 1 | Text note | Yes | Regular posts/tweets |
| 3 | Contacts/follows | Yes | Follow list |
| 5 | Event deletion | Yes | Delete event by id |
| 7 | Reaction | Yes | ❤️ on another event |
| 10000+ | Parameterized replaceable | Yes | App state, settings |

**For Hermes:** Use **Kind 1** (TEXT_NOTE) for all public posts.

---

## Relay Selection & Redundancy

**Recommended production relays:**

| Relay | URL | Notes |
|-------|-----|-------|
| Damus | `wss://relay.damus.io` | Very stable, high uptime, active community |
| Nostr.wine | `wss://nostr.wine` | Reliable, good geo distribution |
| nos.lol | `wss://nos.lol` | Community-run, responsive, good adoption |

**Why 3+ relays?**
- Redundancy: if one relay is down, others capture the event
- Geo-distribution: faster reach globally
- Network resilience: Nostr is censorship-resistant when distributed

---

## Pitfalls & Troubleshooting

### Pitfall 1: Forgetting the 32-Byte Trim

**Symptom:** `TypeError: privkey must be composed of 32 bytes`

**Cause:** Passing all 33 bytes to `PrivateKey()`

**Fix:**
```python
private_key_bytes = decoded[:32]  # Always trim
```

### Pitfall 2: WebSocket Connection Timing

**Symptom:** `WebSocketConnectionClosedException: socket is already closed`

**Cause:** Publishing before relays connect or closing too soon

**Fix:**
```python
relay_manager.open_connections({"skip_all_checks": True})
time.sleep(1)  # ← WAIT for setup (CRITICAL)
relay_manager.publish_event(event)
time.sleep(2)  # ← WAIT for propagation (CRITICAL)
relay_manager.close_connections()
```

### Pitfall 3: Missing `public_key` in Event Constructor

**Symptom:** `TypeError: Event.__init__() missing required positional argument: 'public_key'`

**Cause:** Not passing public_key when creating event

**Fix:**
```python
event = Event(
    public_key=pk.public_key.hex(),  # ← Required
    content=content,
    kind=EventKind.TEXT_NOTE
)
```

### Pitfall 4: Invalid nsec Format

**Symptom:** `ValueError: Invalid bech32 or Unknown HRP`

**Cause:** nsec string corrupted, truncated, or has extra whitespace

**Fix:**
- Verify nsec from your Nostr client (Primal, Damus, Amethyst)
- Check for extra spaces: `nsec.strip()`
- Test decode: `bech32.bech32_decode(nsec)` should return `('nsec', data)`

### Pitfall 5: Event Not Appearing on Clients

**Symptom:** Published successfully but event doesn't show on Primal/Damus

**Causes:**
- Relay connection dropped (try again with more relays)
- Event filtered by relay (some relays have content/spam filters)
- Rate-limited by relay (publish again after 30 sec)

**Fix:**
```bash
# Verify event was published
curl -s https://primal.net/e/{event_id}

# If not there, republish to more relays
# Check alternative relay: https://nostr.wine/e/{event_id}
```

---

## Verification & Testing

### Test Read (No Key)
```bash
~/.hermes/nostr-env/bin/python3 scripts/read.py recent
# Should return JSON with events
```

### Test Draft (No Key)
```bash
~/.hermes/nostr-env/bin/python3 scripts/draft.py "Test draft"
# Should output unsigned event JSON
```

### Test Publish (With Approval)
```bash
# Create draft file
~/.hermes/nostr-env/bin/python3 scripts/draft.py "Test post" > /tmp/draft.json

# Run publish (requires manual "YES" input)
~/.hermes/nostr-env/bin/python3 scripts/publish.py /tmp/draft.json

# Type YES when prompted
# Should output success JSON with event_id
```

### Verify Published Event
1. Open: `https://primal.net/e/{event_id}` → should see post
2. Or search npub on Damus app
3. Or query relay: `websocat wss://relay.damus.io`

---

## NIP (Nostr Improvement Proposal) References

- **NIP-01:** Basic protocol spec, event formats, relay communication  
  https://github.com/nostr-protocol/nips/blob/master/01.md
  
- **NIP-10:** Conventions for "e" and "p" tags (threading, mentions)  
  https://github.com/nostr-protocol/nips/blob/master/10.md
  
- **NIP-19:** Bech32 encoding (nsec, npub, note, nevent)  
  https://github.com/nostr-protocol/nips/blob/master/19.md
  
- **NIP-42:** Relay authentication (optional feature)  
  https://github.com/nostr-protocol/nips/blob/master/42.md

---

## Environment & Credentials Checklist

- [ ] Python venv at `~/.hermes/nostr-env`
- [ ] Dependencies: `nostr`, `bech32`, `websocket-client`, `cryptography`
- [ ] `$NOSTR_NSEC` set (nsec1..., from Primal/Damus/Amethyst)
- [ ] `$NOSTR_RELAYS` set (comma-separated, default provided)
- [ ] Manual test: `~/.hermes/nostr-env/bin/python3 scripts/read.py recent`
- [ ] Manual test: `~/.hermes/nostr-env/bin/python3 scripts/draft.py "test"`
- [ ] Manual test: Create & publish a test event with approval

---

## Verified Success Record

**Published (April 26, 2026):**
```
Content: "I Just built a secure Nostr skill for Hermes Agent which runs on my local machine 🔥 - testing now!"
Event ID: d7c3fde6351a0aa4...
Public Key: npub1luswyznmtrj906ldpxkhv4ukjsutxrjka7tp4zp87s7zjhxwnets4w3ehv
Status: ✅ Live on Primal, Damus, and all major relays
Relays: wss://relay.damus.io, wss://nostr.wine, wss://nos.lol
Verification: https://primal.net/e/d7c3fde6351a0aa4...
```

---

## Version History

### v1.0
✅ Initial version using NIP-01 protocol

### v2.0
✅ Merged `media/nostr-publish` integration with bech32 checksum discovery
✅ Documented complete read/draft/publish workflows
✅ Added NIP-01 protocol details and relay query patterns
✅ Captured key discoveries (33-byte trim, timing controls)
✅ Refactored security architecture with three-zone model
✅ Expanded troubleshooting section and test checklist
✅ Added verified success record with live proof

### v2.1
✅ Added image publishing capability (Blossom + Picsur) via Telegram

---

## Author Notes

This skill represents the complete, production-ready Nostr integration for Hermes Agent. Every operation is:
- **Cryptographically verifiable** (NIP-01 compliant)
- **Audit-logged** (timestamps on all operations)
- **Secure by default** (approval gates, env var isolation)
- **Network-resilient** (multi-relay, automatic fallback)

The 33-byte checksum discovery solved a critical blocker; once identified, the fix is trivial but essential. Trust the cryptography, not the relay or third party. Read first, sign last, always ask before publish.

**Philosophy:** Nostr is social media that respects your autonomy. This skill brings that philosophy to Hermes.

PRs welcome.

## Legal Disclaimer

This Nostr skill and associated code etc. is provided for educational, experimental, and artistic purposes only.
The code is offered "as is", without any warranty of any kind. Use of this skill is entirely at your own risk.
The author is not responsible or liable for:
- Any content you publish using this skill
- Any actions, consequences, or damages resulting from its use
- Any interaction with Nostr relays, Telegram, or third-party services

This project is an expression of personal technical exploration and free speech. It does not constitute professional software, financial advice, or legal counsel.
By using this skill you agree that you are solely responsible for your own actions and compliance with all applicable laws.
