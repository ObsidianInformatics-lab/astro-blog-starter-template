# Capability & Access Inventory Report

**Prepared for:** dstemm@outcomeengineersllc.com (Outcome Engineers LLC)
**Date:** 2026-06-19
**Scope:** Everything installed and/or accessible within this Claude Code session
**Session environment:** Claude Code on the web (remote cloud execution)

---

## 0. Important framing

This session is **not running on your Mac**. It executes inside an **ephemeral
Ubuntu 24.04 cloud VM** (Claude Code on the web). Therefore:

- "**Locally**" below = *this container*, not your personal machine.
- Your Mac's actual installed applications are **not visible** from here.
- There is no distinct product literally named "Outcome Engineers dashboard."
  What you have is **this Claude Code session + the connectors wired into your account**.
- The container is **reclaimed after inactivity** — anything worth keeping must be
  committed and pushed to git.

---

## 1. Compute environment (this cloud VM)

| Attribute | Value |
|---|---|
| Host OS | Ubuntu 24.04.4 LTS (Noble Numbat) |
| Kernel | Linux 6.18.5, x86_64 |
| Nature | Isolated, ephemeral container — cloned fresh, reclaimed after inactivity |
| Outbound network | Open (verified HTTPS 200 to github.com); governed by environment network policy |

### Language runtimes installed
| Runtime | Version |
|---|---|
| Node.js | 22.22.2 |
| npm | 10.9.7 |
| pnpm | 10.33.0 |
| yarn | 1.22.22 |
| Bun | 1.3.11 |
| Python | 3.11.15 (+ pip 24.0) |
| Ruby | 3.3.6 |
| Go | installed |
| Rust / Cargo | 1.94.1 |
| Java | OpenJDK 21.0.10 |
| PHP | 8.4.19 |

### CLI tooling installed
git 2.43 · curl 8.5 · wget 1.21 · jq 1.7 · make 4.3 · gcc 13.3 · Docker CLI 29.3.1

### Not installed in this VM
`gh` · `wrangler` (global — available via `npx`; pinned as a project devDependency) ·
`docker-compose` (standalone) · `kubectl` · `sqlite3` · `deno`

> **Docker note:** the `docker` CLI is present, but the **daemon is NOT running**
> in this VM — containers cannot be built or run here. A `docker-compose.yml`
> authored here is meant to run on *your* Mac.

---

## 2. Built-in Claude Code capabilities

| Category | Tools |
|---|---|
| File / code | Read, Write, Edit, Glob, Grep |
| Execution | Bash (foreground + background), Monitor (event streams) |
| Web | WebSearch, WebFetch |
| Delegation (sub-agents) | `claude`, `general-purpose`, `Explore`, `Plan`, `claude-code-guide`, `statusline-setup` |
| User interaction | AskUserQuestion, SendUserFile |
| Tool discovery | ToolSearch (loads schemas for deferred MCP tools on demand) |

---

## 3. Skills (slash-commands) available

`deep-research` · `code-review` · `security-review` · `review` · `verify` ·
`run` · `init` · `simplify` · `update-config` · `session-start-hook` ·
`keybindings-help` · `fewer-permission-prompts` · `loop` · `claude-api` ·
Adobe `create-visual-design` / `html-export-readiness`

---

## 4. GitHub integration

- **GitHub MCP** — full PR / issue / CI / code-search tooling.
- **Current repo scope:** `obsidianinformatics-lab/astro-blog-starter-template`
- Additional repos can be added via `list_repos` → `add_repo`.
- No `gh` CLI — all GitHub operations route through the MCP.

---

## 5. Connected MCP servers / connectors (~48)

Wired into your account and reachable via ToolSearch. They connect/disconnect
intermittently, but all appeared this session. Each exposes anywhere from 2 to
130+ individual tools; full schemas load on demand.

### Design / docs / media
| Connector | Purpose |
|---|---|
| Adobe (Creative Cloud / Express / Firefly) | Image editing, vectorize, PDF/INDD, video, fonts (~82 tools) |
| Figma | Design↔code, FigJam, Code Connect |
| Gamma | Presentations / docs / webpages |
| SlidesGPT | Slide generation |
| Lucid | Diagrams / whiteboard |
| Mermaid Chart | Diagram rendering |
| tldraw | Canvas / diagramming |
| Goodnotes | Notes / markdown / SVG / diagrams |
| Send | HTML document authoring |
| HyperFrames (HeyGen) | Programmatic HTML video |
| Zoom for Claude | Meeting recordings / transcripts |

### Productivity / workflow / signing
| Connector | Purpose |
|---|---|
| Notion | Docs, databases, projects |
| Linear | Issues, projects, cycles |
| DocuSign | E-signature / agreements |
| DocuSeal | E-signature / templates |
| IFTTT | Automation applets |
| Zapier | Bridge to 9,000+ apps |
| Listen Labs | User-research studies |

### Sales / marketing / SEO
| Connector | Purpose |
|---|---|
| Apollo.io | Leads / CRM enrichment |
| Ahrefs | SEO / backlinks / traffic |
| Semrush | SEO / competitive intelligence |
| Contentsquare | Digital-experience analytics |

### Cloud / dev infrastructure
| Connector | Purpose |
|---|---|
| Cloudflare Developer Platform | Workers, D1, R2, KV, Hyperdrive, docs |
| QuickNode | Blockchain RPC endpoints |
| Sentry | Error monitoring + Seer analysis |
| Hugging Face | Models / datasets / papers / spaces |

### Finance / crypto / markets
| Connector | Purpose |
|---|---|
| FMP (Financial Modeling Prep) | Equities / SEC / economics |
| CoinDesk | Crypto market data |
| Crypto.com | Exchange market data |
| LunarCrush | Social / crypto sentiment |
| Blockscout | On-chain / blockchain explorer |

### Legal / civic
| Connector | Purpose |
|---|---|
| CourtListener | Federal case law / dockets |
| Descrybe Legal Engine | Structured U.S. primary law |
| Midpage | Legal research |
| Courtroom5 | Case intake / deadlines / guidance |
| Granted | U.S. grants database |

### Commerce / travel / local
| Connector | Purpose |
|---|---|
| Instacart | Grocery / products |
| Square | Commerce / payments API |
| Uber | Rides |
| Uber Eats | Food delivery |
| DirectBooker | Hotels |
| lastminute.com | Flights + hotels |
| GoDaddy | Domain search / availability |
| Coupler.io | Data-integration pipelines (400+ sources) |
| Felt | Collaborative mapping |
| Tango | Opportunity / API search |

### Security / trust
| Connector | Purpose |
|---|---|
| Malwarebytes ScamGuard | Link / email / phone reputation checks |

---

## 6. Category cross-reference

| Your term | Where it maps |
|---|---|
| Apps / programs | Runtimes & CLIs (§1) + desktop-style connectors (§5) |
| Skills | §3 |
| MCPs / connectors | §5 |
| Docker connections | CLI present, **daemon unavailable here** (§1) |
| Web interfaces / APIs | The §5 connectors are API-backed web services |
| Programs | §1 runtimes & tooling |
| Capabilities / extensions | §2 built-ins + §3 skills |
| Virtual machine | The Ubuntu container itself (§1) |

---

## 7. Caveats & notes

- The OSINT/security tools from the earlier PR (nmap, nuclei, theHarvester, etc.)
  are **not** installed in this VM — that Brewfile targets your Mac.
- Several MCP connectors require **OAuth / authentication** to return live data
  (e.g., Apollo, Ahrefs, Notion, DocuSign) even though they are connected.
- MCP connectors flap (connect/disconnect) during a session; this is normal and
  does not mean access was lost.
- Connector availability reflects this session; the set can differ in other
  sessions or environments.

---

*Report generated within a Claude Code web session for record-keeping.*
