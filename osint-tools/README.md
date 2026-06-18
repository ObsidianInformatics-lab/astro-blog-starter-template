# OSINT / Security Tooling Setup (macOS)

One-shot setup for a curated set of mainstream OSINT, recon, and security tools.
Designed so you only install what you're missing — `brew bundle` skips anything
already present.

> **Authorized use only.** Point active scanning, bruteforcing, wireless, and
> exploitation tools only at systems you own or have explicit written
> permission to test. OSINT collection should respect applicable laws and ToS.

## Prerequisites

- [Homebrew](https://brew.sh) — `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for the container stacks)
- `pipx` for the Python tools — `brew install pipx && pipx ensurepath`

## 1. Homebrew tools

```bash
brew bundle --file=osint-tools/Brewfile
```

This installs CLI tools (theHarvester, amass, nuclei, ffuf, hashcat, etc.) plus
a few GUI casks (Ghidra, Cutter, OWASP ZAP). Already-installed formulae are
skipped automatically.

## 2. Python tools (pipx)

```bash
pipx install spiderfoot maigret holehe ghunt photon recon-ng \
             volatility3 sherlock-project responder
```

Each lands in its own isolated venv and on your `PATH`.

## 3. Docker platforms

```bash
# Web-UI OSINT engine
docker compose -f osint-tools/docker-compose.yml up -d spiderfoot   # http://localhost:5001

# Headless web app scanner
docker compose -f osint-tools/docker-compose.yml up -d zap          # http://localhost:8090

# One-shot WordPress scan
docker compose -f osint-tools/docker-compose.yml run --rm wpscan --url https://target.example
```

For full threat-intel platforms (**OpenCTI**, **MISP**, **TheHive + Cortex**),
use their official multi-service compose files — they need Elasticsearch/Redis/
etc. and are too heavy to inline here:

- OpenCTI: https://github.com/OpenCTI-Platform/docker
- MISP: https://github.com/MISP/misp-docker
- TheHive/Cortex: https://github.com/TheHive-Project/Docker-Templates

## What's included

| Category | Tools |
|---|---|
| Recon / OSINT | theHarvester, amass, subfinder, exiftool, SpiderFoot, Sherlock, maigret, holehe, GHunt, Photon, recon-ng |
| Network scanning | masscan, rustscan, naabu, nmap, dnsx |
| Web app testing | httpx, nuclei, katana, ffuf, gobuster, sqlmap, OWASP ZAP |
| Credentials | hashcat, john-jumbo, hydra |
| Wireless / RF | kismet, aircrack-ng |
| Forensics / RE | Ghidra, radare2, Cutter, Volatility 3, YARA, binwalk |
| Frameworks | Metasploit |

## Customizing

Comment out anything you don't want in `Brewfile`, or drop services from
`docker-compose.yml`. Re-running `brew bundle` is safe and idempotent.
