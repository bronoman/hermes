---
name: ftp
description: FTP client for Hermes Agent — connect, upload, download, list directories, sync folders. Wraps Python ftplib with safe defaults and comprehensive error handling.
version: 1.0.0
author: Hermes Community
license: MIT
category: productivity
metadata:
  hermes:
    tags: [ftp, file-transfer, remote, storage, productivity]
    homepage: https://tools.ietf.org/html/rfc959
prerequisites:
  python_modules: [ftplib]
---

# FTP Client for Hermes Agent

Production-ready FTP client for Hermes Agent — upload, download, list, sync, and manage remote directories via FTP/FTPS.

## Quick Start

### Setup: Add Credentials to `~/.hermes/.env`

```bash
FTP_HOST=ftp.example.com
FTP_USER=your_username
FTP_PASS=your_password
FTP_PORT=21
FTP_PASSIVE=true
FTP_TIMEOUT=30
```

All fields are optional except `FTP_HOST` and `FTP_USER`. Defaults:
- `FTP_PORT`: 21
- `FTP_PASSIVE`: true (recommended for NAT/firewalls)
- `FTP_TIMEOUT`: 30 seconds

### List Remote Directory

```bash
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py list /path/on/server
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py list /  # root
```

Output: JSON with file list, sizes, timestamps, and permissions.

### Download File

```bash
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py download /remote/file.txt ./local_file.txt
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py download /documents/report.pdf ~/Downloads/
```

### Upload File

```bash
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py upload ./local_file.txt /remote/path/
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py upload ~/pitch.html /public_html/
```

### Create Remote Directory

```bash
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py mkdir /new/directory
```

### Delete Remote File

```bash
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py delete /remote/file.txt
```

### Rename/Move File

```bash
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py rename /old/path/file.txt /new/path/file.txt
```

### Sync Local → Remote

```bash
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py sync-upload ./local/dir /remote/dir
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py sync-upload ./pitch.html /public_html/
```

Uploads all files from local directory to remote, skipping identical files (by size + mtime).

### Sync Remote → Local

```bash
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py sync-download /remote/dir ./local/dir
```

Downloads all files from remote directory to local, skipping identical files.

### Backup Remote Directory

```bash
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py backup /remote/path ~/backups/ftp-backup/
```

Downloads entire remote directory tree with timestamps preserved.

### Test Connection

```bash
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py test
```

Returns connection status and remote server info.

## Operations Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `test` | Test FTP connection | `ftp.py test` |
| `list` | List remote directory | `ftp.py list /html` |
| `download` | Get file from server | `ftp.py download /file.txt ./local.txt` |
| `upload` | Send file to server | `ftp.py upload ./local.txt /remote/` |
| `mkdir` | Create remote directory | `ftp.py mkdir /new/dir` |
| `delete` | Delete remote file | `ftp.py delete /file.txt` |
| `rename` | Rename/move remote file | `ftp.py rename /old.txt /new.txt` |
| `rmdir` | Delete remote directory | `ftp.py rmdir /empty/dir` |
| `chmod` | Change file permissions | `ftp.py chmod /file.txt 644` |
| `sync-upload` | Upload directory (skip identical) | `ftp.py sync-upload ./local /remote` |
| `sync-download` | Download directory (skip identical) | `ftp.py sync-download /remote ./local` |
| `backup` | Full recursive download | `ftp.py backup /remote ~/backups/` |

## Response Format

All commands return JSON:

### Success
```json
{
  "success": true,
  "command": "download",
  "remote_file": "/documents/report.pdf",
  "local_file": "./report.pdf",
  "bytes_transferred": 1048576,
  "duration_seconds": 2.3,
  "message": "Downloaded 1.0 MB in 2.30s"
}
```

### Error
```json
{
  "success": false,
  "command": "download",
  "error": "550 File not found",
  "http_code": 550,
  "details": "Remote file does not exist"
}
```

### Directory Listing
```json
{
  "success": true,
  "command": "list",
  "directory": "/html",
  "files": [
    {
      "name": "index.html",
      "type": "file",
      "size": 4096,
      "modified": "2026-06-29T10:30:00+02:00",
      "permissions": "rw-r--r--"
    },
    {
      "name": "images",
      "type": "directory",
      "permissions": "rwxr-xr-x"
    }
  ],
  "count": 2
}
```

## Authentication

### Credential Storage
- **Location:** `~/.hermes/.env`
- **Format:** `FTP_HOST`, `FTP_USER`, `FTP_PASS` (plain text, local-only)
- **Security:** File is local, never uploaded to cloud. Treat like SSH keys.

### Inline Credentials (not recommended)
```bash
FTP_HOST=ftp.example.com FTP_USER=user FTP_PASS=pass python3 ftp.py list /
```

### No Credentials Stored
If `~/.hermes/.env` is missing or incomplete, the script will prompt for connection details (interactive mode).

## Performance & Safety

### File Transfer Safety
- **Partial uploads**: Incomplete transfers are not deleted (manual cleanup recommended)
- **Overwrite protection**: Downloads will NOT overwrite existing files by default
- **Binary mode**: All transfers use binary mode (safe for all file types)

### Sync Safety
- **Dry-run**: Not implemented yet; syncs are live (consider testing with small files first)
- **Skip rules**: Identical files (same size + mtime) are skipped
- **Recursive**: `sync-upload` and `sync-download` work recursively

### Timeouts
- Default: 30 seconds per operation
- Configurable via `FTP_TIMEOUT` env var
- Long transfers may time out; use smaller files or increase timeout

## Pitfalls & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection refused | Server down or wrong host | Check `FTP_HOST` and server status |
| 530 Not logged in | Bad credentials | Verify `FTP_USER` and `FTP_PASS` |
| 550 File not found | Wrong path or filename | Use `ftp.py list /` to browse |
| Timeout during upload | Network slow or file large | Increase `FTP_TIMEOUT` |
| SSL certificate error | FTPS enabled but untrusted CA | Disable FTPS (use plain FTP) or add CA cert |
| "cannot connect in passive mode" | Firewall blocks passive FTP | Set `FTP_PASSIVE=false` (less secure) |
| Binary files corrupted | Transferred in ASCII mode | This script always uses binary; check server |

## Use Cases

### 1. Deploy Website
```bash
# Backup current version
python3 ftp.py backup /public_html ~/backups/site-$(date +%Y%m%d)/

# Upload new files
python3 ftp.py sync-upload ./build /public_html/
```

### 2. Regular Backups
```bash
# Cron job to backup /documents folder daily
0 2 * * * python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py backup /documents ~/backups/ftp-docs-$(date +\%Y\%m\%d)/
```

### 3. Shared File Exchange
```bash
# Upload report for review
python3 ftp.py upload ./quarterly-report.xlsx /shared/reports/

# Download feedback
python3 ftp.py download /shared/feedback/notes.txt ./feedback.txt
```

### 4. Log Collection
```bash
# Download all server logs
python3 ftp.py sync-download /var/log ~/logs/server-$(date +%Y%m%d)/
```

## API Reference

### `FTPClient` Class

```python
from ftp import FTPClient

client = FTPClient(
    host="ftp.example.com",
    user="username",
    password="password",
    port=21,
    passive=True,
    timeout=30
)

# List directory
files = client.list("/path")

# Upload
client.upload("local.txt", "/remote/")

# Download
client.download("/remote/file.txt", "./local.txt")

# Cleanup
client.close()
```

All methods return dicts with `success`, `message`, and operation-specific data.

## Standards & References

- **RFC 959**: File Transfer Protocol (FTP) — https://tools.ietf.org/html/rfc959
- **Python ftplib**: https://docs.python.org/3/library/ftplib.html
- **SFTP Alternative**: For secure transfers, consider SFTP (not FTP) — see `paramiko` library

## Contributing

This skill is open-source under the MIT license. Contributions welcome:

1. Fork https://github.com/bronoman/hermes
2. Add feature or fix bug
3. Test thoroughly (FTP server required)
4. Submit PR with description

### Known Limitations

- **No SFTP support** — FTP only (consider `paramiko` for SFTP)
- **No resume on partial downloads** — transfers restart from beginning
- **No tar/zip compression** — transfer raw files
- **No parallel transfers** — sequential uploads/downloads only

### Future Enhancements

- [ ] SFTP support via Paramiko
- [ ] Parallel transfers with thread pool
- [ ] Resume on partial transfers
- [ ] Dry-run mode for sync operations
- [ ] .ftpignore file support (like .gitignore)
- [ ] FTPS with certificate validation

## License

MIT License — see LICENSE file in repository.

## Support

- **Issues**: https://github.com/bronoman/hermes/issues
- **Docs**: https://github.com/bronoman/hermes#ftp-skill
- **Community**: Discussions on GitHub

---

**Last updated:** 2026-06-29 | **Version:** 1.0.0
