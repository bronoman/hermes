#!/usr/bin/env python3
"""
Secure Nostr Publish Script for Hermes (nostr skill v2.0)
- Requires explicit user approval ("YES")
- Loads nsec ONLY here, never logs it
- Signs and publishes to multiple relays
- Handles bech32 checksum fix (April 2026)
"""

import os
import sys
import json
import time
import bech32
from datetime import datetime

try:
    from nostr.event import Event, EventKind
    from nostr.key import PrivateKey
    from nostr.relay_manager import RelayManager
except ImportError:
    print(json.dumps({
        "status": "error",
        "message": "Missing dependencies. Install: pip install nostr bech32 websocket-client"
    }))
    sys.exit(1)


def nsec_to_private_key(nsec):
    """
    Decode nsec (bech32) to secp256k1 private key.
    
    CRITICAL FIX (April 2026):
    Bech32 decode produces 33 bytes (32 key + 1 checksum).
    MUST trim to 32 bytes for secp256k1 library.
    
    Args:
        nsec: Private key in bech32 format (nsec1...)
    
    Returns:
        PrivateKey object ready for signing
    
    Raises:
        ValueError: If nsec format is invalid
    """
    # Bech32 decode
    hrp, data = bech32.bech32_decode(nsec)
    if hrp != "nsec":
        raise ValueError(f"Invalid nsec HRP: {hrp} (expected 'nsec')")
    
    if not data:
        raise ValueError("Invalid bech32 data")
    
    # Convert 5-bit to 8-bit bytes
    decoded = bytes(bech32.convertbits(data, 5, 8))
    
    # CRITICAL: Trim checksum byte (keep first 32 bytes only)
    private_key_bytes = decoded[:32]
    
    if len(private_key_bytes) != 32:
        raise ValueError(f"Invalid key length after trim: {len(private_key_bytes)}")
    
    # Validate and create key
    try:
        pk = PrivateKey(private_key_bytes)
        return pk
    except Exception as e:
        raise ValueError(f"Failed to create private key: {e}")


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: publish.py <draft.json>"
        }))
        sys.exit(1)

    draft_path = sys.argv[1]

    # Security checkpoint: Require explicit confirmation
    print("\n" + "="*70)
    print("⚠️  SECURITY CHECKPOINT — ABOUT TO SIGN AND PUBLISH")
    print("="*70)
    
    try:
        with open(draft_path, "r", encoding="utf-8") as f:
            draft = json.load(f)
        
        print(f"\nContent: {draft.get('content', '')[:200]}...")
        print(f"Kind: {draft.get('kind', 1)}")
        print(f"Tags: {draft.get('tags', [])}")
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"Failed to load draft: {e}"
        }))
        sys.exit(1)
    
    print("\n⚠️  This action is PERMANENT and CRYPTOGRAPHIC.")
    print("Type YES (uppercase) to proceed, or press Enter to cancel:\n")
    
    confirmation = input().strip()
    if confirmation != "YES":
        print(json.dumps({
            "status": "cancelled",
            "message": "Publish cancelled by user"
        }))
        sys.exit(0)

    # Load credentials from environment
    nsec = os.getenv("NOSTR_NSEC")
    if not nsec or not nsec.startswith("nsec1"):
        print(json.dumps({
            "status": "error",
            "message": "Missing or invalid $NOSTR_NSEC environment variable"
        }))
        sys.exit(1)

    relays_str = os.getenv("NOSTR_RELAYS", 
                          "wss://relay.damus.io,wss://nostr.wine,wss://nos.lol")
    relays = [r.strip() for r in relays_str.split(",") if r.strip()]

    try:
        # Decode nsec and create signing key
        pk = nsec_to_private_key(nsec)
        public_key_hex = pk.public_key.hex()
        public_key_npub = pk.public_key.bech32()

        # Create event
        event = Event(
            public_key=public_key_hex,
            content=draft["content"],
            kind=draft.get("kind", 1),
            tags=draft.get("tags", [])
        )

        # Sign event
        pk.sign_event(event)

        # Publish to relays
        relay_manager = RelayManager()
        for relay in relays:
            relay_manager.add_relay(relay)

        relay_manager.open_connections({"skip_all_checks": True})
        time.sleep(1)  # Connection stabilization (CRITICAL)

        relay_manager.publish_event(event)
        time.sleep(2)  # Propagation time before closing (CRITICAL)

        relay_manager.close_connections()

        # Success result
        result = {
            "status": "published",
            "message": "✅ Event published successfully",
            "event_id": event.id,
            "public_key": public_key_npub,
            "timestamp": datetime.fromtimestamp(event.created_at).isoformat(),
            "relays": relays,
            "primal_url": f"https://primal.net/e/{event.id}",
            "damus_url": f"https://damus.io/note/{event.id}",
            "verify_on_nos_lol": f"https://nostr.wine/e/{event.id}"
        }

        print("\n" + "="*70)
        print("✅ PUBLISH SUCCESS")
        print("="*70)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("="*70 + "\n")

    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }, indent=2))
        sys.exit(1)
    finally:
        try:
            relay_manager.close_connections()
        except:
            pass


if __name__ == "__main__":
    main()
