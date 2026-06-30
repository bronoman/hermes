#!/usr/bin/env python3
"""
Example: Upload a single file to FTP and log the result.
Useful for automated report submission, log uploads, etc.
"""
import subprocess
import json
import sys
from datetime import datetime

def upload_file(local_path, remote_path, description=""):
    """Upload file and log result."""
    cmd = [
        "python3", "/home/matt/.hermes/skills/productivity/ftp/scripts/ftp.py",
        "upload", local_path, remote_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "description": description,
        "local_file": local_path,
        "remote_file": remote_path,
        **data
    }
    
    print(json.dumps(log_entry, indent=2))
    
    return data.get("success", False)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 upload_example.py <local_path> <remote_path> [description]")
        sys.exit(1)
    
    local = sys.argv[1]
    remote = sys.argv[2]
    desc = sys.argv[3] if len(sys.argv) > 3 else ""
    
    success = upload_file(local, remote, desc)
    sys.exit(0 if success else 1)
