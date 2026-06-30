#!/usr/bin/env python3
"""
FTP Client for Hermes Agent — upload, download, list, sync, and manage remote directories.

Usage:
    python3 ftp.py test
    python3 ftp.py list /path
    python3 ftp.py download /remote/file.txt ./local.txt
    python3 ftp.py upload ./local.txt /remote/dir/
    python3 ftp.py mkdir /new/dir
    python3 ftp.py delete /remote/file.txt
    python3 ftp.py rename /old.txt /new.txt
    python3 ftp.py chmod /file.txt 644
    python3 ftp.py sync-upload ./local/dir /remote/dir
    python3 ftp.py sync-download /remote/dir ./local/dir
    python3 ftp.py backup /remote/dir ~/backups/
"""
import argparse
import ftplib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


class FTPClient:
    """FTP client with safe defaults and comprehensive error handling."""

    def __init__(self, host=None, user=None, password=None, port=21, passive=True, timeout=30):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.passive = passive
        self.timeout = timeout
        self.ftp = None
        self.start_time = None

    def connect(self):
        """Connect to FTP server."""
        try:
            self.ftp = ftplib.FTP(timeout=self.timeout)
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.user, self.password)
            self.ftp.set_pasv(self.passive)
            return {"success": True, "message": f"Connected to {self.host}"}
        except ftplib.all_errors as e:
            return {"success": False, "error": str(e), "http_code": getattr(e, "code", None)}

    def close(self):
        """Disconnect from FTP server."""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                self.ftp.close()

    def list_dir(self, path="/"):
        """List remote directory contents."""
        try:
            self.ftp.cwd(path)
            files = []
            self.ftp.retrlines("LIST", lambda line: self._parse_list_line(line, files))
            return {"success": True, "files": files, "directory": path, "count": len(files)}
        except ftplib.all_errors as e:
            return {"success": False, "error": str(e), "directory": path}

    def _parse_list_line(self, line, files):
        """Parse FTP LIST line into file info."""
        # Unix-style FTP LIST: permissions links owner group size month day time/year name
        parts = line.split(None, 8)
        if len(parts) < 9:
            return

        perms, owner, group, size, month, day, time_year, name = parts[0], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7], parts[8]
        is_dir = perms.startswith('d')

        file_info = {
            "name": name,
            "type": "directory" if is_dir else "file",
            "permissions": perms,
        }
        if not is_dir:
            try:
                file_info["size"] = int(size)
            except ValueError:
                file_info["size"] = 0

        files.append(file_info)

    def download(self, remote_path, local_path):
        """Download file from server."""
        self.start_time = time.time()
        try:
            # Handle directory destination
            if local_path.endswith('/') or os.path.isdir(local_path):
                local_path = os.path.join(local_path, os.path.basename(remote_path))

            # Create parent directory if needed
            os.makedirs(os.path.dirname(local_path) or '.', exist_ok=True)

            # Download
            bytes_transferred = 0
            def callback(block):
                nonlocal bytes_transferred
                bytes_transferred += len(block)

            with open(local_path, 'wb') as f:
                self.ftp.retrbinary(f'RETR {remote_path}', f.write, blocksize=8192)

            duration = time.time() - self.start_time
            return {
                "success": True,
                "command": "download",
                "remote_file": remote_path,
                "local_file": os.path.abspath(local_path),
                "bytes_transferred": bytes_transferred or os.path.getsize(local_path),
                "duration_seconds": round(duration, 2),
                "message": f"Downloaded {os.path.getsize(local_path) / 1024 / 1024:.1f} MB in {duration:.2f}s"
            }
        except FileNotFoundError:
            return {"success": False, "error": "550 File not found", "http_code": 550}
        except ftplib.all_errors as e:
            return {"success": False, "error": str(e), "remote_file": remote_path}

    def upload(self, local_path, remote_dir):
        """Upload file to server."""
        self.start_time = time.time()
        try:
            if not os.path.exists(local_path):
                return {"success": False, "error": f"Local file not found: {local_path}"}

            # Ensure remote_dir ends with /
            if not remote_dir.endswith('/'):
                remote_dir += '/'

            remote_file = remote_dir + os.path.basename(local_path)
            file_size = os.path.getsize(local_path)

            with open(local_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_file}', f, blocksize=8192)

            duration = time.time() - self.start_time
            return {
                "success": True,
                "command": "upload",
                "local_file": os.path.abspath(local_path),
                "remote_file": remote_file,
                "bytes_transferred": file_size,
                "duration_seconds": round(duration, 2),
                "message": f"Uploaded {file_size / 1024 / 1024:.1f} MB in {duration:.2f}s"
            }
        except ftplib.all_errors as e:
            return {"success": False, "error": str(e), "local_file": local_path}

    def mkdir(self, path):
        """Create remote directory."""
        try:
            self.ftp.mkd(path)
            return {"success": True, "command": "mkdir", "path": path, "message": f"Created {path}"}
        except ftplib.all_errors as e:
            return {"success": False, "error": str(e), "path": path}

    def delete(self, path):
        """Delete remote file."""
        try:
            self.ftp.delete(path)
            return {"success": True, "command": "delete", "path": path, "message": f"Deleted {path}"}
        except ftplib.all_errors as e:
            return {"success": False, "error": str(e), "path": path}

    def rename(self, old_path, new_path):
        """Rename/move remote file."""
        try:
            self.ftp.rename(old_path, new_path)
            return {"success": True, "command": "rename", "old": old_path, "new": new_path, "message": f"Renamed {old_path} → {new_path}"}
        except ftplib.all_errors as e:
            return {"success": False, "error": str(e), "old": old_path}

    def rmdir(self, path):
        """Delete remote directory."""
        try:
            self.ftp.rmd(path)
            return {"success": True, "command": "rmdir", "path": path, "message": f"Removed {path}"}
        except ftplib.all_errors as e:
            return {"success": False, "error": str(e), "path": path}

    def chmod(self, path, mode):
        """Change file permissions."""
        try:
            self.ftp.sendcmd(f'SITE CHMOD {mode} {path}')
            return {"success": True, "command": "chmod", "path": path, "mode": mode, "message": f"Changed {path} to {mode}"}
        except ftplib.all_errors as e:
            return {"success": False, "error": str(e), "path": path, "details": "Server may not support CHMOD"}

    def sync_upload(self, local_dir, remote_dir):
        """Upload directory, skipping identical files."""
        results = {"uploaded": 0, "skipped": 0, "failed": 0, "details": []}
        try:
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    local_file = os.path.join(root, file)
                    rel_path = os.path.relpath(local_file, local_dir)
                    remote_file = remote_dir.rstrip('/') + '/' + rel_path.replace('\\', '/')

                    # Create remote subdirs
                    remote_subdir = os.path.dirname(remote_file)
                    try:
                        self.ftp.cwd(remote_subdir)
                        self.ftp.cwd(remote_dir.rstrip('/'))
                    except:
                        pass  # Directory might already exist

                    # Check if file exists and is identical
                    try:
                        remote_size = self.ftp.size(remote_file)
                        local_size = os.path.getsize(local_file)
                        if remote_size == local_size:
                            results["skipped"] += 1
                            results["details"].append({"file": rel_path, "status": "skipped", "reason": "identical size"})
                            continue
                    except ftplib.all_errors:
                        pass  # File doesn't exist, will upload

                    # Upload
                    try:
                        with open(local_file, 'rb') as f:
                            self.ftp.storbinary(f'STOR {remote_file}', f, blocksize=8192)
                        results["uploaded"] += 1
                        results["details"].append({"file": rel_path, "status": "uploaded"})
                    except Exception as e:
                        results["failed"] += 1
                        results["details"].append({"file": rel_path, "status": "failed", "error": str(e)})

            return {
                "success": True,
                "command": "sync-upload",
                "local_dir": local_dir,
                "remote_dir": remote_dir,
                "uploaded": results["uploaded"],
                "skipped": results["skipped"],
                "failed": results["failed"],
                "message": f"Uploaded {results['uploaded']}, skipped {results['skipped']}, failed {results['failed']}"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "command": "sync-upload"}

    def sync_download(self, remote_dir, local_dir):
        """Download directory, skipping identical files."""
        results = {"downloaded": 0, "skipped": 0, "failed": 0}
        try:
            os.makedirs(local_dir, exist_ok=True)
            self._recursive_download(remote_dir, local_dir, results)
            return {
                "success": True,
                "command": "sync-download",
                "remote_dir": remote_dir,
                "local_dir": local_dir,
                "downloaded": results["downloaded"],
                "skipped": results["skipped"],
                "failed": results["failed"],
                "message": f"Downloaded {results['downloaded']}, skipped {results['skipped']}, failed {results['failed']}"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "command": "sync-download"}

    def _recursive_download(self, remote_dir, local_dir, results):
        """Recursively download directory tree."""
        try:
            self.ftp.cwd(remote_dir)
            lines = []
            self.ftp.retrlines("LIST", lines.append)

            for line in lines:
                parts = line.split(None, 8)
                if len(parts) < 9:
                    continue

                perms, name = parts[0], parts[8]
                is_dir = perms.startswith('d')

                remote_path = remote_dir.rstrip('/') + '/' + name
                local_path = os.path.join(local_dir, name)

                if is_dir:
                    os.makedirs(local_path, exist_ok=True)
                    self._recursive_download(remote_path, local_path, results)
                else:
                    # Check if already exists and is same size
                    if os.path.exists(local_path):
                        try:
                            remote_size = self.ftp.size(remote_path)
                            local_size = os.path.getsize(local_path)
                            if remote_size == local_size:
                                results["skipped"] += 1
                                continue
                        except:
                            pass

                    try:
                        with open(local_path, 'wb') as f:
                            self.ftp.retrbinary(f'RETR {remote_path}', f.write, blocksize=8192)
                        results["downloaded"] += 1
                    except Exception as e:
                        results["failed"] += 1

            self.ftp.cwd('/')
        except Exception as e:
            results["failed"] += 1


def _load_env():
    """Load FTP credentials from ~/.hermes/.env"""
    env_file = Path.home() / ".hermes" / ".env"
    config = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("FTP_"):
                key, val = line.split("=", 1)
                config[key.lower()] = val.strip().strip('"').strip("'")
    return config


def _output(data):
    """Print JSON output."""
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def main():
    parser = argparse.ArgumentParser(description="FTP Client for Hermes Agent")
    parser.add_argument("command", choices=[
        "test", "list", "download", "upload", "mkdir", "delete", "rename", "rmdir", "chmod",
        "sync-upload", "sync-download", "backup"
    ])
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--host", help="FTP host (overrides FTP_HOST env)")
    parser.add_argument("--user", help="FTP user (overrides FTP_USER env)")
    parser.add_argument("--pass", dest="password", help="FTP password (overrides FTP_PASS env)")
    parser.add_argument("--port", type=int, help="FTP port (default: 21)")
    parser.add_argument("--passive", action="store_true", default=True, help="Use passive mode (default)")
    parser.add_argument("--no-passive", dest="passive", action="store_false", help="Disable passive mode")
    parser.add_argument("--timeout", type=int, help="Connection timeout in seconds (default: 30)")

    args = parser.parse_args()

    # Load config
    env = _load_env()
    host = args.host or env.get("ftp_host")
    user = args.user or env.get("ftp_user")
    password = args.password or env.get("ftp_pass")
    port = args.port or int(env.get("ftp_port", 21))
    passive = args.passive and env.get("ftp_passive", "true").lower() != "false"
    timeout = args.timeout or int(env.get("ftp_timeout", 30))

    if not host or not user:
        _output({
            "success": False,
            "error": "Missing FTP credentials",
            "fix": "Add to ~/.hermes/.env: FTP_HOST=... FTP_USER=... FTP_PASS=..."
        })
        sys.exit(1)

    client = FTPClient(host, user, password, port, passive, timeout)
    result = client.connect()
    if not result["success"]:
        _output(result)
        sys.exit(1)

    try:
        if args.command == "test":
            _output({"success": True, "message": f"Connected to {host}", "ftp_server": host, "port": port})
        elif args.command == "list":
            path = args.args[0] if args.args else "/"
            result = client.list_dir(path)
            _output(result)
        elif args.command == "download":
            if len(args.args) < 2:
                _output({"success": False, "error": "Usage: ftp.py download <remote> <local>"})
                sys.exit(1)
            result = client.download(args.args[0], args.args[1])
            _output(result)
        elif args.command == "upload":
            if len(args.args) < 2:
                _output({"success": False, "error": "Usage: ftp.py upload <local> <remote>"})
                sys.exit(1)
            result = client.upload(args.args[0], args.args[1])
            _output(result)
        elif args.command == "mkdir":
            result = client.mkdir(args.args[0])
            _output(result)
        elif args.command == "delete":
            result = client.delete(args.args[0])
            _output(result)
        elif args.command == "rename":
            if len(args.args) < 2:
                _output({"success": False, "error": "Usage: ftp.py rename <old> <new>"})
                sys.exit(1)
            result = client.rename(args.args[0], args.args[1])
            _output(result)
        elif args.command == "rmdir":
            result = client.rmdir(args.args[0])
            _output(result)
        elif args.command == "chmod":
            if len(args.args) < 2:
                _output({"success": False, "error": "Usage: ftp.py chmod <path> <mode>"})
                sys.exit(1)
            result = client.chmod(args.args[0], args.args[1])
            _output(result)
        elif args.command == "sync-upload":
            if len(args.args) < 2:
                _output({"success": False, "error": "Usage: ftp.py sync-upload <local> <remote>"})
                sys.exit(1)
            result = client.sync_upload(args.args[0], args.args[1])
            _output(result)
        elif args.command == "sync-download":
            if len(args.args) < 2:
                _output({"success": False, "error": "Usage: ftp.py sync-download <remote> <local>"})
                sys.exit(1)
            result = client.sync_download(args.args[0], args.args[1])
            _output(result)
        elif args.command == "backup":
            if len(args.args) < 2:
                _output({"success": False, "error": "Usage: ftp.py backup <remote> <local>"})
                sys.exit(1)
            result = client.sync_download(args.args[0], args.args[1])
            _output(result)
    finally:
        client.close()


if __name__ == "__main__":
    main()
