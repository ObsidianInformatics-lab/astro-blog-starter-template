#!/usr/bin/env python3
"""Render the capability inventory into a color-coded, indexed PDF."""
from weasyprint import HTML
from datetime import date

OUT = "CAPABILITY-INVENTORY.pdf"

CSS = """
@page {
  size: A4;
  margin: 18mm 16mm 20mm 16mm;
  @bottom-center {
    content: "Capability & Access Inventory  ·  Outcome Engineers LLC";
    font-size: 8pt; color: #8a94a6;
  }
  @bottom-right { content: "Page " counter(page) " / " counter(pages);
    font-size: 8pt; color: #8a94a6; }
}
@page :first { margin: 0; }
* { box-sizing: border-box; }
body { font-family: "DejaVu Sans", "Helvetica", sans-serif; color: #1f2933;
  font-size: 10.5pt; line-height: 1.5; }

/* ---- Cover ---- */
.cover { height: 297mm; background: linear-gradient(135deg,#0f172a 0%,#1e3a5f 55%,#2563eb 100%);
  color: #fff; padding: 60mm 22mm 0 22mm; }
.cover h1 { font-size: 34pt; margin: 0 0 6mm 0; font-weight: 800; letter-spacing:-.5px; }
.cover .sub { font-size: 13pt; color: #c7d6f0; margin-bottom: 28mm; }
.cover .meta { font-size: 10.5pt; line-height: 1.9; border-left: 3px solid #60a5fa; padding-left: 6mm; }
.cover .meta b { color:#fff; } .cover .meta span { color:#aebfdc; }
.cover .badge { display:inline-block; margin-top: 30mm; padding: 3mm 6mm;
  background: rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.3);
  border-radius: 30px; font-size: 9pt; color:#dbe7ff; }

/* ---- Headings ---- */
h2 { font-size: 17pt; margin: 11mm 0 4mm 0; padding-bottom: 2mm;
  border-bottom: 2px solid #e2e8f0; color:#0f172a; }
h2 .num { color:#2563eb; font-weight:800; margin-right: 3mm; }
h3 { font-size: 12pt; margin: 6mm 0 2mm 0; color:#1e3a5f; }
p { margin: 2mm 0; }
a { color:#2563eb; text-decoration:none; }

/* ---- TOC ---- */
.toc { page-break-after: always; }
.toc h2 { border:none; }
.toc ol { list-style:none; padding:0; margin:0; counter-reset: toc; }
.toc li { counter-increment: toc; padding: 2.4mm 0; border-bottom: 1px dashed #e2e8f0;
  font-size: 11pt; display:flex; justify-content:space-between; }
.toc li::before { content: counter(toc) ".  "; color:#2563eb; font-weight:700; }
.toc a { flex:1; padding-left:2mm; }
.toc .pg { color:#94a3b8; }

/* ---- Callouts ---- */
.note { border-radius:6px; padding:3mm 4mm; margin:4mm 0; font-size:9.8pt; }
.warn { background:#fef3f2; border-left:4px solid #ef4444; }
.info { background:#eff6ff; border-left:4px solid #3b82f6; }
.ok   { background:#ecfdf5; border-left:4px solid #10b981; }

/* ---- Tables ---- */
table { width:100%; border-collapse:collapse; margin:3mm 0; font-size:9.6pt;
  page-break-inside:avoid; }
th { background:#0f172a; color:#fff; text-align:left; padding:2.2mm 3mm; font-weight:600; }
td { padding:2mm 3mm; border-bottom:1px solid #e8edf3; vertical-align:top; }
tr:nth-child(even) td { background:#f7f9fc; }
.kv td:first-child { font-weight:600; color:#334155; width:34%; }

/* ---- Category color chips ---- */
.cat { display:flex; align-items:center; gap:3mm; margin:7mm 0 1mm 0; }
.chip { width:5mm; height:5mm; border-radius:2px; }
.cat h3 { margin:0; }
.c-design{background:#8b5cf6;} .c-prod{background:#0ea5e9;} .c-sales{background:#f59e0b;}
.c-cloud{background:#10b981;} .c-fin{background:#ef4444;} .c-legal{background:#6366f1;}
.c-comm{background:#ec4899;} .c-sec{background:#111827;}
.tag { display:inline-block; padding:.5mm 2mm; border-radius:3px; font-size:8pt;
  background:#eef2ff; color:#3730a3; margin-right:1.5mm; }
.pill-ok{background:#dcfce7;color:#166534;padding:.4mm 2mm;border-radius:10px;font-size:8.5pt;font-weight:600;}
.pill-no{background:#fee2e2;color:#991b1b;padding:.4mm 2mm;border-radius:10px;font-size:8.5pt;font-weight:600;}
.pill-auth{background:#fef9c3;color:#854d0e;padding:.4mm 2mm;border-radius:10px;font-size:8.5pt;font-weight:600;}
code { background:#f1f5f9; padding:.3mm 1.5mm; border-radius:3px; font-size:9pt;
  font-family:"DejaVu Sans Mono",monospace; color:#be123c; }
.section { page-break-inside:avoid; }
"""

def chip(c, label):
    return f'<div class="cat"><span class="chip {c}"></span><h3>{label}</h3></div>'

BODY = f"""
<div class="cover">
  <h1>Capability &amp; Access Inventory</h1>
  <div class="sub">A complete map of everything installed and accessible in this session</div>
  <div class="meta">
    <span>Prepared for</span> &nbsp; <b>dstemm@outcomeengineersllc.com</b><br>
    <span>Organization</span> &nbsp; <b>Outcome Engineers LLC</b><br>
    <span>Date</span> &nbsp; <b>{date.today().isoformat()}</b><br>
    <span>Environment</span> &nbsp; <b>Claude Code on the web (remote cloud VM)</b>
  </div>
  <div class="badge">CONFIDENTIAL · Session capability snapshot</div>
</div>

<div class="toc">
  <h2>Index</h2>
  <ol>
    <li><a href="#s0">Framing &amp; scope</a><span class="pg"></span></li>
    <li><a href="#s1">Compute environment (cloud VM)</a><span class="pg"></span></li>
    <li><a href="#s2">Built-in Claude Code capabilities</a><span class="pg"></span></li>
    <li><a href="#s3">Skills (slash-commands)</a><span class="pg"></span></li>
    <li><a href="#s4">GitHub integration</a><span class="pg"></span></li>
    <li><a href="#s5">Connected MCP servers / connectors</a><span class="pg"></span></li>
    <li><a href="#s6">Live verification results</a><span class="pg"></span></li>
    <li><a href="#s7">Category cross-reference</a><span class="pg"></span></li>
    <li><a href="#s8">Caveats &amp; notes</a><span class="pg"></span></li>
  </ol>
</div>

<h2 id="s0"><span class="num">0</span>Framing &amp; scope</h2>
<div class="note warn"><b>This session is not running on your Mac.</b> It executes inside an
ephemeral <b>Ubuntu 24.04 cloud VM</b> (Claude Code on the web). "Locally" below means
<i>this container</i>; your Mac's installed apps are not visible from here. The container is
reclaimed after inactivity, so anything worth keeping is committed to git.</div>
<p>There is no distinct product literally named "Outcome Engineers dashboard." What you have is
<b>this Claude Code session plus the connectors wired into your account</b>.</p>

<h2 id="s1"><span class="num">1</span>Compute environment (this cloud VM)</h2>
<table class="kv">
<tr><td>Host OS</td><td>Ubuntu 24.04.4 LTS (Noble Numbat)</td></tr>
<tr><td>Kernel</td><td>Linux 6.18.5, x86_64</td></tr>
<tr><td>Nature</td><td>Isolated, ephemeral container — cloned fresh, reclaimed after inactivity</td></tr>
<tr><td>Outbound network</td><td>Open (verified HTTPS 200 to github.com); governed by environment network policy</td></tr>
</table>
<h3>Language runtimes installed</h3>
<table>
<tr><th>Runtime</th><th>Version</th><th>Runtime</th><th>Version</th></tr>
<tr><td>Node.js</td><td>22.22.2</td><td>Ruby</td><td>3.3.6</td></tr>
<tr><td>npm</td><td>10.9.7</td><td>Go</td><td>installed</td></tr>
<tr><td>pnpm</td><td>10.33.0</td><td>Rust / Cargo</td><td>1.94.1</td></tr>
<tr><td>yarn</td><td>1.22.22</td><td>Java</td><td>OpenJDK 21.0.10</td></tr>
<tr><td>Bun</td><td>1.3.11</td><td>PHP</td><td>8.4.19</td></tr>
<tr><td>Python</td><td>3.11.15 (+ pip 24.0)</td><td>&nbsp;</td><td>&nbsp;</td></tr>
</table>
<h3>CLI tooling installed</h3>
<p>git 2.43 &middot; curl 8.5 &middot; wget 1.21 &middot; jq 1.7 &middot; make 4.3 &middot; gcc 13.3 &middot; Docker CLI 29.3.1 &middot; LibreOffice &middot; WeasyPrint 69</p>
<h3>Not installed in this VM</h3>
<p><code>gh</code> &middot; <code>wrangler</code> (global; via <code>npx</code>) &middot; <code>docker-compose</code> &middot; <code>kubectl</code> &middot; <code>sqlite3</code> &middot; <code>deno</code></p>
<div class="note warn"><b>Docker:</b> the CLI is present but the <b>daemon is NOT running</b> in this VM —
containers cannot be built or run here. A <code>docker-compose.yml</code> authored here is meant to run on your Mac.</div>

<h2 id="s2"><span class="num">2</span>Built-in Claude Code capabilities</h2>
<table>
<tr><th>Category</th><th>Tools</th></tr>
<tr><td>File / code</td><td>Read, Write, Edit, Glob, Grep</td></tr>
<tr><td>Execution</td><td>Bash (foreground + background), Monitor (event streams)</td></tr>
<tr><td>Web</td><td>WebSearch, WebFetch</td></tr>
<tr><td>Delegation (sub-agents)</td><td>claude, general-purpose, Explore, Plan, claude-code-guide, statusline-setup</td></tr>
<tr><td>User interaction</td><td>AskUserQuestion, SendUserFile</td></tr>
<tr><td>Tool discovery</td><td>ToolSearch (loads deferred MCP tool schemas on demand)</td></tr>
</table>

<h2 id="s3"><span class="num">3</span>Skills (slash-commands) available</h2>
<p>
<span class="tag">deep-research</span><span class="tag">code-review</span><span class="tag">security-review</span>
<span class="tag">review</span><span class="tag">verify</span><span class="tag">run</span><span class="tag">init</span>
<span class="tag">simplify</span><span class="tag">update-config</span><span class="tag">session-start-hook</span>
<span class="tag">keybindings-help</span><span class="tag">fewer-permission-prompts</span><span class="tag">loop</span>
<span class="tag">claude-api</span><span class="tag">create-visual-design</span><span class="tag">html-export-readiness</span>
</p>

<h2 id="s4"><span class="num">4</span>GitHub integration</h2>
<table class="kv">
<tr><td>Tooling</td><td>GitHub MCP — full PR / issue / CI / code-search</td></tr>
<tr><td>Current repo scope</td><td><code>obsidianinformatics-lab/astro-blog-starter-template</code></td></tr>
<tr><td>Expand scope</td><td><code>list_repos</code> &rarr; <code>add_repo</code></td></tr>
<tr><td>CLI</td><td>No <code>gh</code> — all GitHub ops route through the MCP</td></tr>
</table>

<h2 id="s5"><span class="num">5</span>Connected MCP servers / connectors (~48)</h2>
<p>Wired into your account, reachable via ToolSearch. They connect/disconnect intermittently;
each exposes 2&ndash;130+ tools loaded on demand.</p>

{chip('c-design','Design / docs / media')}
<table><tr><th>Connector</th><th>Purpose</th></tr>
<tr><td>Adobe (Creative Cloud / Express / Firefly)</td><td>Image editing, vectorize, PDF/INDD, video, fonts (~82 tools)</td></tr>
<tr><td>Figma</td><td>Design&harr;code, FigJam, Code Connect</td></tr>
<tr><td>Gamma</td><td>Presentations / docs / webpages</td></tr>
<tr><td>SlidesGPT</td><td>Slide generation</td></tr>
<tr><td>Lucid</td><td>Diagrams / whiteboard</td></tr>
<tr><td>Mermaid Chart</td><td>Diagram rendering</td></tr>
<tr><td>tldraw</td><td>Canvas / diagramming</td></tr>
<tr><td>Goodnotes</td><td>Notes / markdown / SVG / diagrams</td></tr>
<tr><td>Send</td><td>HTML document authoring</td></tr>
<tr><td>HyperFrames (HeyGen)</td><td>Programmatic HTML video</td></tr>
<tr><td>Zoom for Claude</td><td>Meeting recordings / transcripts</td></tr></table>

{chip('c-prod','Productivity / workflow / signing')}
<table><tr><th>Connector</th><th>Purpose</th></tr>
<tr><td>Notion</td><td>Docs, databases, projects</td></tr>
<tr><td>Linear</td><td>Issues, projects, cycles</td></tr>
<tr><td>DocuSign</td><td>E-signature / agreements</td></tr>
<tr><td>DocuSeal</td><td>E-signature / templates</td></tr>
<tr><td>IFTTT</td><td>Automation applets</td></tr>
<tr><td>Zapier</td><td>Bridge to 9,000+ apps</td></tr>
<tr><td>Listen Labs</td><td>User-research studies</td></tr></table>

{chip('c-sales','Sales / marketing / SEO')}
<table><tr><th>Connector</th><th>Purpose</th></tr>
<tr><td>Apollo.io</td><td>Leads / CRM enrichment</td></tr>
<tr><td>Ahrefs</td><td>SEO / backlinks / traffic</td></tr>
<tr><td>Semrush</td><td>SEO / competitive intelligence</td></tr>
<tr><td>Contentsquare</td><td>Digital-experience analytics</td></tr></table>

{chip('c-cloud','Cloud / dev infrastructure')}
<table><tr><th>Connector</th><th>Purpose</th></tr>
<tr><td>Cloudflare Developer Platform</td><td>Workers, D1, R2, KV, Hyperdrive, docs</td></tr>
<tr><td>QuickNode</td><td>Blockchain RPC endpoints</td></tr>
<tr><td>Sentry</td><td>Error monitoring + Seer analysis</td></tr>
<tr><td>Hugging Face</td><td>Models / datasets / papers / spaces</td></tr></table>

{chip('c-fin','Finance / crypto / markets')}
<table><tr><th>Connector</th><th>Purpose</th></tr>
<tr><td>FMP (Financial Modeling Prep)</td><td>Equities / SEC / economics</td></tr>
<tr><td>CoinDesk</td><td>Crypto market data</td></tr>
<tr><td>Crypto.com</td><td>Exchange market data</td></tr>
<tr><td>LunarCrush</td><td>Social / crypto sentiment</td></tr>
<tr><td>Blockscout</td><td>On-chain / blockchain explorer</td></tr></table>

{chip('c-legal','Legal / civic')}
<table><tr><th>Connector</th><th>Purpose</th></tr>
<tr><td>CourtListener</td><td>Federal case law / dockets</td></tr>
<tr><td>Descrybe Legal Engine</td><td>Structured U.S. primary law</td></tr>
<tr><td>Midpage</td><td>Legal research</td></tr>
<tr><td>Courtroom5</td><td>Case intake / deadlines / guidance</td></tr>
<tr><td>Granted</td><td>U.S. grants database</td></tr></table>

{chip('c-comm','Commerce / travel / local')}
<table><tr><th>Connector</th><th>Purpose</th></tr>
<tr><td>Instacart</td><td>Grocery / products</td></tr>
<tr><td>Square</td><td>Commerce / payments API</td></tr>
<tr><td>Uber / Uber Eats</td><td>Rides / food delivery</td></tr>
<tr><td>DirectBooker / lastminute.com</td><td>Hotels / flights</td></tr>
<tr><td>GoDaddy</td><td>Domain search / availability</td></tr>
<tr><td>Coupler.io</td><td>Data-integration pipelines (400+ sources)</td></tr>
<tr><td>Felt</td><td>Collaborative mapping</td></tr>
<tr><td>Tango</td><td>Opportunity / API search</td></tr></table>

{chip('c-sec','Security / trust')}
<table><tr><th>Connector</th><th>Purpose</th></tr>
<tr><td>Malwarebytes ScamGuard</td><td>Link / email / phone reputation checks</td></tr></table>

<h2 id="s6"><span class="num">6</span>Live verification results</h2>
<p>Connectors probed live during report generation to confirm authentication &amp; reachability:</p>
<table>
<tr><th>Target</th><th>Check</th><th>Result</th></tr>
<tr><td>Local VM network</td><td>HTTPS reachability</td><td><span class="pill-ok">VERIFIED</span> github.com &rarr; 200</td></tr>
<tr><td>GitHub MCP</td><td>__GH_RESULT__</td><td>__GH_PILL__</td></tr>
<tr><td>Cloudflare Dev Platform</td><td>__CF_RESULT__</td><td>__CF_PILL__</td></tr>
<tr><td>Hugging Face</td><td>__HF_RESULT__</td><td>__HF_PILL__</td></tr>
</table>
<div class="note info">Pills: <span class="pill-ok">VERIFIED</span> reachable &amp; authenticated &middot;
<span class="pill-auth">AUTH NEEDED</span> connected but requires OAuth &middot;
<span class="pill-no">UNVERIFIED</span> not probed this run. Most other connectors are wired but
were not individually exercised; many require their own OAuth before returning live data.</div>

<h2 id="s7"><span class="num">7</span>Category cross-reference</h2>
<table>
<tr><th>Your term</th><th>Where it maps in this report</th></tr>
<tr><td>Apps / programs</td><td>Runtimes &amp; CLIs (&sect;1) + connectors (&sect;5)</td></tr>
<tr><td>Skills</td><td>&sect;3</td></tr>
<tr><td>MCPs / connectors</td><td>&sect;5</td></tr>
<tr><td>Docker connections</td><td>CLI present, daemon unavailable (&sect;1)</td></tr>
<tr><td>Web interfaces / APIs</td><td>The &sect;5 connectors are API-backed web services</td></tr>
<tr><td>Capabilities / extensions</td><td>&sect;2 built-ins + &sect;3 skills</td></tr>
<tr><td>Virtual machine</td><td>The Ubuntu container itself (&sect;1)</td></tr>
</table>

<h2 id="s8"><span class="num">8</span>Caveats &amp; notes</h2>
<div class="note ok">The earlier OSINT/security tools (nmap, nuclei, theHarvester, etc.) are <b>not</b>
installed in this VM — that Brewfile targets your Mac.</div>
<div class="note info">Several MCP connectors require <b>OAuth / authentication</b> to return live data
(e.g., Apollo, Ahrefs, Notion, DocuSign) even though they are connected.</div>
<div class="note info">MCP connectors flap (connect/disconnect) during a session; this is normal and
does not indicate lost access. The set reflects this session and can differ elsewhere.</div>
<p style="margin-top:8mm;color:#94a3b8;font-size:8.5pt;">Report generated within a Claude Code web session for record-keeping.</p>
"""

import sys
verify = {}
for arg in sys.argv[1:]:
    k, _, v = arg.partition("=")
    verify[k] = v

def fill(res_key, pill_key, default_res="Not probed", default_pill="UNVERIFIED"):
    return verify.get(res_key, default_res), verify.get(pill_key, default_pill)

def pill_html(p):
    cls = {"VERIFIED":"pill-ok","AUTH NEEDED":"pill-auth","UNVERIFIED":"pill-no"}.get(p,"pill-no")
    return f'<span class="{cls}">{p}</span>'

gh_r, gh_p = fill("GH_RESULT","GH_PILL")
cf_r, cf_p = fill("CF_RESULT","CF_PILL")
hf_r, hf_p = fill("HF_RESULT","HF_PILL")
body = (BODY.replace("__GH_RESULT__", gh_r).replace("__GH_PILL__", pill_html(gh_p))
            .replace("__CF_RESULT__", cf_r).replace("__CF_PILL__", pill_html(cf_p))
            .replace("__HF_RESULT__", hf_r).replace("__HF_PILL__", pill_html(hf_p)))

html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
HTML(string=html).write_pdf(OUT)
print("Wrote", OUT)
"""end"""
