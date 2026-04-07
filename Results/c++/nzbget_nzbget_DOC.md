# nzbget Deployment Document

## Platform

- See Prerequisites for system requirements

## Prerequisites

- Git 2.34.1
- Bash 5.0
- curl 7.68.0
- procps 3.3.16
- lsof 4.93.2

## Build Steps

```bash
# 1. Clone project
git clone https://github.com/nzbget/nzbget.git
cd nzbget

# 2. Install dependencies
# Uses built-in installer to download and set up the nzbget binary
bash linux/install-update.sh

# 3. Configure environment variables
# None required for installation and startup

# 4. Initialize (not needed)
# No initialization step required prior to installation

# 5. Start service
./nzbget -v
./nzbget -D && until pgrep -x nzbget > /dev/null; do sleep 1; done
# Service running at: http://localhost:6789

# 6. Verify deployment
# Verify the daemon is running (returns a PID)
pgrep -x nzbget

# Verify the binary reports version
./nzbget -v
# Expected output contains the string: NZBGet



```

## Test Steps


```
curl -s http://localhost:6789 | grep -qi "NZBGet" && echo "UI OK"
```
## Unexpected Issues

- `linux/install-update.sh: No such file or directory` — current directory is not the repository root. Run `cd nzbget` first.
- `Permission denied` when running installer — executing without bash or missing execute permission. Use `bash linux/install-update.sh`.
- Network error during installation (e.g., `Could not resolve host`) — no Internet connectivity or DNS issue. Ensure Internet access and retry.
- `Port 6789 is already in use` — port occupied; Web UI fails to bind. Free with `lsof -ti:6789 | xargs kill -9`.
