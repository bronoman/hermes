#!/usr/bin/env python3
"""
Secure Telegram → Nostr Cross-Post with Image
Skill Path: ~/.hermes/skills/social-media/nostr

Supports:
- Blossom (NIP-B7) primary upload (public & decentralized)
- Picsur fallback (local testing)
"""

import os
import sys
import json
import hashlib
import time
import requests
from datetime import datetime

def compute_sha256(file_path):
    """Compute SHA-256 hash of file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def upload_to_blossom(image_path, blossom_servers=None):
    """Upload to Blossom servers (preferred)"""
    if not blossom_servers:
        blossom_servers = [
            "https://blossom.primal.net",
            "https://cdn.nostrcheck.me",
            "https://blossom.nostr.build"
        ]

    sha256 = compute_sha256(image_path)
    filename = os.path.basename(image_path)

    for server in blossom_servers:
        url = f"{server.rstrip('/')}/upload"
        print(f"→ Trying Blossom upload to {server}...")

        try:
            with open(image_path, 'rb') as f:
                files = {'file': (filename, f)}
                response = requests.post(url, files=files, timeout=30)

            if response.status_code in (200, 201):
                blossom_url = f"{server.rstrip('/')}/{sha256}{os.path.splitext(filename)[1]}"
                print(f"✅ Blossom upload successful: {blossom_url}")
                return blossom_url, sha256
        except Exception as e:
            print(f"   Failed {server}: {e}")

    print("⚠️ All Blossom servers failed")
    return None, None

def upload_to_picsur(image_path):
    """Fallback to local Picsur"""
    host = os.getenv("PICSUR_URL", "http://localhost:3000")
    try:
        with open(image_path, 'rb') as f:
            r = requests.post(f"{host}/upload", files={'file': f}, timeout=20)
            if r.ok:
                data = r.json() if r.content else {}
                url = data.get('url') or f"{host.rstrip('/')}/i/{data.get('id', '')}"
                print(f"✅ Picsur upload successful: {url}")
                return url
    except Exception as e:
        print(f"Picsur upload failed: {e}")
    return None

def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "status": "error",
            "message": "Usage: telegram_to_nostr.py <image_path> \"Caption text\""
        }, indent=2))
        sys.exit(1)

    image_path = sys.argv[1]
    caption = sys.argv[2]

    if not os.path.exists(image_path):
        print(json.dumps({"status": "error", "message": f"Image not found: {image_path}"}))
        sys.exit(1)

    print(f"Processing: {image_path}")

    # 1. Try Blossom first (modern/decentralized)
    image_url, sha256 = upload_to_blossom(image_path)

    # 2. Fallback to Picsur (local testing)
    if not image_url:
        image_url = upload_to_picsur(image_path)

    if not image_url:
        print(json.dumps({"status": "error", "message": "All upload methods failed"}))
        sys.exit(1)

    # 3. Send to Telegram (optional)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if bot_token and chat_id:
        try:
            with open(image_path, 'rb') as photo:
                requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                    data={'chat_id': chat_id, 'caption': caption},
                    files={'photo': photo}
                )
            print("✅ Sent to Telegram")
        except Exception as e:
            print(f"Telegram warning: {e}")

    # 4. Create Nostr content
    content = f"{caption}\n\n{image_url}"

    result = {
        "status": "success",
        "message": "Ready for Nostr",
        "image_url": image_url,
        "caption": caption,
        "content_for_nostr": content,
        "timestamp": datetime.now().isoformat()
    }

    print("\n=== FINAL RESULT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Save draft for publishing
    with open("last_draft.json", "w", encoding="utf-8") as f:
        json.dump({
            "content": content,
            "kind": 1,
            "tags": [["imeta", f"url {image_url}", "m image/jpeg", f"x {sha256}" if sha256 else ""]]
        }, f, indent=2)

    print("\n💡 Next step: ./scripts/publish.py last_draft.json")

if __name__ == "__main__":
    main()
