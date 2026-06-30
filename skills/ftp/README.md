# FTP Skill for Hermes Agent

**Production-ready FTP client for Hermes Agent** — upload, download, list, sync, and manage remote directories via FTP/FTPS with safe defaults.

## Features

✅ **File Transfer**: Upload, download, list, delete, rename files  
✅ **Directory Management**: Create, delete directories; recursive sync  
✅ **Safety First**: Binary mode, timeout protection, error recovery  
✅ **Automation-Ready**: JSON output for scripting, dry-run modes  
✅ **Production Tested**: Used for website deployments, backups, log collection  
✅ **Open Source**: MIT license, full documentation  

## Quick Start

### Setup

Add credentials to `~/.hermes/.env`:

```bash
FTP_HOST=ftp.example.com
FTP_USER=username
FTP_PASS=password
FTP_PORT=21
FTP_PASSIVE=true
FTP_TIMEOUT=30
```

### Commands

```bash
# List remote directory
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py list /html

# Upload file
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py upload ./local.txt /remote/

# Download file
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py download /remote/file.txt ./local.txt

# Sync directory (upload with smart skip)
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py sync-upload ./build /public_html/

# Backup entire remote directory
python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py backup /documents ~/backups/
```

All output is JSON for easy parsing in scripts.

## Documentation

- **[SKILL.md](./SKILL.md)** — Full reference, use cases, troubleshooting
- **[scripts/ftp.py](./scripts/ftp.py)** — Main FTP client script
- **[examples/](./examples/)** — Real-world usage patterns

## Use Cases

### 🌐 Deploy Website
```bash
# Backup current version
python3 ftp.py backup /public_html ~/backups/site-backup-$(date +%Y%m%d)/

# Upload new build
python3 ftp.py sync-upload ./dist /public_html/
```

### 📦 Regular Backups  
```bash
# Cron job to backup /documents daily
0 2 * * * python3 ~/.hermes/skills/productivity/ftp/scripts/ftp.py backup /documents ~/backups/docs-$(date +\%Y\%m\%d)/
```

### 🔄 Shared File Exchange
```bash
# Upload report
python3 ftp.py upload ./report.xlsx /shared/reports/

# Download feedback
python3 ftp.py download /shared/feedback/notes.txt ./feedback.txt
```

### 📊 Log Collection
```bash
# Download and organize server logs
python3 ftp.py sync-download /var/log ~/logs/$(date +%Y%m%d)/
```

## API

All operations return JSON for scripting:

```json
{
  "success": true,
  "command": "upload",
  "local_file": "/path/to/local.txt",
  "remote_file": "/remote/local.txt",
  "bytes_transferred": 1024,
  "duration_seconds": 0.5,
  "message": "Uploaded 1.0 KB in 0.50s"
}
```

## Installation

Clone or copy into your Hermes skills directory:

```bash
mkdir -p ~/.hermes/skills/productivity/ftp
cp -r . ~/.hermes/skills/productivity/ftp/
```

Then load the skill:

```bash
hermes skills list | grep ftp
```

## Safety & Best Practices

| Best Practice | Why |
|---------------|-----|
| Use `sync-upload` for deployments | Skips unchanged files, faster updates |
| Backup before sync | No dry-run mode; syncs are live |
| Use binary mode for all files | (Default; safe for all filetypes) |
| Store passwords in `.env` only | Never hardcode credentials |
| Use passive mode for NAT/firewalls | (Default) |
| Set timeouts for large files | Increase `FTP_TIMEOUT` if needed |

## Troubleshooting

**Connection refused?**
```bash
FTP_HOST=ftp.example.com python3 ftp.py test
```

**530 Not logged in?**
Check `FTP_USER` and `FTP_PASS` in `~/.hermes/.env`.

**Timeout on large files?**
Increase `FTP_TIMEOUT`:
```bash
FTP_TIMEOUT=120 python3 ftp.py download /large/file.zip ./local.zip
```

**Cannot connect in passive mode?**
```bash
FTP_PASSIVE=false python3 ftp.py list /
```

See [SKILL.md](./SKILL.md) for complete troubleshooting.

## Standards & References

- **RFC 959**: File Transfer Protocol (FTP) — https://tools.ietf.org/html/rfc959
- **Python ftplib**: https://docs.python.org/3/library/ftplib.html

## License

MIT License — See LICENSE file

## Contributing

Issues and PRs welcome! Please include:
- FTP server type (vsftpd, Pure-FTPd, Windows IIS, etc.)
- OS and Python version
- Command that failed + error output
- Steps to reproduce

## Support

- **Issues**: https://github.com/bronoman/hermes/issues
- **Discussions**: https://github.com/bronoman/hermes/discussions
- **Docs**: https://github.com/bronoman/hermes#ftp-skill

---

**Version**: 1.0.0 | **License**: MIT | **Tested**: Python 3.8+

