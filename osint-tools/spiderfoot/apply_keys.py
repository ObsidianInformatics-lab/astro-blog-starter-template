#!/usr/bin/env python3
"""Load API keys from api_keys.env into SpiderFoot's config store.

SpiderFoot's CLI (sf.py) has no flag for module API keys — it reads them from
the config DB at ~/.spiderfoot/spiderfoot.db (via SpiderFootDb.configGet at scan
start). This script reads api_keys.env, maps each variable to the corresponding
`module:option` config key, and persists it with SpiderFootDb.configSet so every
subsequent CLI scan and the web UI use the keys automatically.

Usage:
    cp api_keys.env.example api_keys.env   # then fill in your keys
    SPIDERFOOT_HOME=/tmp/spiderfoot python3 apply_keys.py
    # SPIDERFOOT_HOME defaults to /tmp/spiderfoot if unset.

Re-run any time you add or change keys. Blank values are skipped (existing
config is left untouched for those providers).
"""
import os
import sys

# Map env var name -> SpiderFoot "module:option" config key.
ENV_TO_OPT = {
    "HIBP_API_KEY": "sfp_haveibeenpwned:api_key",
    "HUNTER_API_KEY": "sfp_hunter:api_key",
    "INTELX_API_KEY": "sfp_intelx:api_key",
    "EMAILREP_API_KEY": "sfp_emailrep:api_key",
    "FULLCONTACT_API_KEY": "sfp_fullcontact:api_key",
    "DEHASHED_API_KEY": "sfp_dehashed:api_key",
    "DEHASHED_USERNAME": "sfp_dehashed:api_key_username",
    "SHODAN_API_KEY": "sfp_shodan:api_key",
    "SECURITYTRAILS_API_KEY": "sfp_securitytrails:api_key",
    "BUILTWITH_API_KEY": "sfp_builtwith:api_key",
    "ABUSEIPDB_API_KEY": "sfp_abuseipdb:api_key",
    "GREYNOISE_API_KEY": "sfp_greynoise:api_key",
}


def parse_env(path):
    """Minimal .env parser: KEY=VALUE lines, ignores comments/blanks, strips inline # comments."""
    values = {}
    with open(path) as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            # strip trailing inline comment + surrounding whitespace/quotes
            val = val.split("#", 1)[0].strip().strip("'\"")
            values[key.strip()] = val
    return values


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(here, "api_keys.env")
    if not os.path.exists(env_path):
        sys.exit(
            f"ERROR: {env_path} not found.\n"
            "Run:  cp api_keys.env.example api_keys.env   then fill in your keys."
        )

    sf_home = os.environ.get("SPIDERFOOT_HOME", "/tmp/spiderfoot")
    if sf_home not in sys.path:
        sys.path.insert(0, sf_home)
    try:
        from spiderfoot import SpiderFootDb, SpiderFootHelpers
    except ImportError:
        sys.exit(
            f"ERROR: could not import SpiderFoot from {sf_home}.\n"
            "Set SPIDERFOOT_HOME to your SpiderFoot checkout, e.g.:\n"
            "    SPIDERFOOT_HOME=/path/to/spiderfoot python3 apply_keys.py"
        )

    env = parse_env(env_path)
    opt_map = {}
    skipped = []
    for var, opt in ENV_TO_OPT.items():
        val = env.get(var, "").strip()
        if val:
            opt_map[opt] = val
        else:
            skipped.append(var)

    if not opt_map:
        sys.exit("No keys set in api_keys.env — nothing to do. Fill in at least one value.")

    db_path = f"{SpiderFootHelpers.dataPath()}/spiderfoot.db"
    dbh = SpiderFootDb({"__database": db_path}, init=True)
    dbh.configSet(opt_map)

    modules = sorted({opt.split(":", 1)[0] for opt in opt_map})
    print(f"Wrote {len(opt_map)} option(s) to {db_path}")
    print(f"Activated modules: {', '.join(modules)}")
    if skipped:
        print(f"Skipped (blank): {', '.join(skipped)}")
    print("\nDone. CLI scans (sf.py) and the web UI now use these keys.")


if __name__ == "__main__":
    main()
