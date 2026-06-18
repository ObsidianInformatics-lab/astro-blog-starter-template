#!/usr/bin/env python3
"""
Tenmiro / keepsmile (ELK-BLEDOM family) BLE -> HTTP bridge.

This is "Option C": a tiny always-on web service that speaks Bluetooth Low
Energy to the LED controller and exposes plain HTTP endpoints that iOS
Shortcuts can call via the "Get Contents of URL" action. Assign a Siri
phrase to each Shortcut and you get voice control without HomeKit.

Run it on something that stays powered on and within Bluetooth range of the
light: a Raspberry Pi, an old laptop, a mini-PC, etc.

Endpoints
---------
  GET /on
  GET /off
  GET /color?rgb=RRGGBB          hex, e.g. /color?rgb=ff0000  (red)
  GET /color?r=255&g=0&b=128     decimal components
  GET /brightness?level=50       0-100
  GET /status                    JSON: connection state

Optional shared-secret auth: set BRIDGE_TOKEN and pass ?token=... on every
request (so a random device on your LAN can't toggle your lights).

Quick start
-----------
  pip install -r requirements.txt
  # auto-discover by advertised name:
  python bridge.py --name ELK-BLEDOM
  # ...or pin the exact address once you know it (more reliable):
  python bridge.py --address AA:BB:CC:DD:EE:FF

Find the address/name with a BLE scanner app (nRF Connect / LightBlue) or:
  python bridge.py --scan
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os

from aiohttp import web
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

# ELK-BLEDOM / MELK / LEDBLE write characteristic. If your unit doesn't
# respond, scan its GATT table and try 0000ffe1-0000-1000-8000-00805f9b34fb.
WRITE_CHAR_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"

log = logging.getLogger("tenmiro-bridge")


# --- Command byte builders (the actual protocol) ---------------------------

def cmd_power(on: bool) -> bytes:
    if on:
        return bytes([0x7E, 0x00, 0x04, 0xF0, 0x00, 0x01, 0xFF, 0x00, 0xEF])
    return bytes([0x7E, 0x00, 0x04, 0x00, 0x00, 0x00, 0xFF, 0x00, 0xEF])


def cmd_color(r: int, g: int, b: int) -> bytes:
    for name, v in (("r", r), ("g", g), ("b", b)):
        if not 0 <= v <= 255:
            raise ValueError(f"{name} must be 0-255, got {v}")
    return bytes([0x7E, 0x00, 0x05, 0x03, r, g, b, 0x00, 0xEF])


def cmd_brightness(level: int) -> bytes:
    if not 0 <= level <= 100:
        raise ValueError(f"brightness must be 0-100, got {level}")
    return bytes([0x7E, 0x00, 0x01, level, 0x00, 0x00, 0x00, 0x00, 0xEF])


# --- BLE connection manager (auto-reconnect; these strips drop often) ------

class LightController:
    def __init__(self, address: str | None, name: str | None):
        self.address = address
        self.name = name
        self._client: BleakClient | None = None
        self._lock = asyncio.Lock()

    async def _resolve_address(self) -> str:
        if self.address:
            return self.address
        log.info("Scanning for a device named %r ...", self.name)
        device = await BleakScanner.find_device_by_filter(
            lambda d, _adv: bool(d.name and self.name and self.name.lower() in d.name.lower()),
            timeout=15.0,
        )
        if device is None:
            raise BleakError(f"No BLE device matching name {self.name!r} found")
        log.info("Discovered %s (%s)", device.name, device.address)
        self.address = device.address
        return device.address

    async def _ensure_connected(self) -> BleakClient:
        if self._client and self._client.is_connected:
            return self._client
        address = await self._resolve_address()
        client = BleakClient(address)
        await client.connect()
        log.info("Connected to %s", address)
        self._client = client
        return client

    async def send(self, payload: bytes) -> None:
        async with self._lock:
            last_err: Exception | None = None
            for attempt in range(1, 4):
                try:
                    client = await self._ensure_connected()
                    await client.write_gatt_char(WRITE_CHAR_UUID, payload, response=False)
                    return
                except (BleakError, OSError, asyncio.TimeoutError) as err:
                    last_err = err
                    log.warning("Write attempt %d failed: %s", attempt, err)
                    self._client = None  # force reconnect next loop
                    await asyncio.sleep(attempt)  # 1s, 2s backoff
            raise last_err if last_err else BleakError("send failed")

    @property
    def connected(self) -> bool:
        return bool(self._client and self._client.is_connected)


# --- HTTP layer ------------------------------------------------------------

def make_app(ctrl: LightController, token: str | None) -> web.Application:
    def check_auth(request: web.Request) -> None:
        if token and request.query.get("token") != token:
            raise web.HTTPUnauthorized(text="bad or missing token\n")

    async def on(request: web.Request) -> web.Response:
        check_auth(request)
        await ctrl.send(cmd_power(True))
        return web.Response(text="on\n")

    async def off(request: web.Request) -> web.Response:
        check_auth(request)
        await ctrl.send(cmd_power(False))
        return web.Response(text="off\n")

    async def color(request: web.Request) -> web.Response:
        check_auth(request)
        q = request.query
        if "rgb" in q:
            h = q["rgb"].lstrip("#")
            if len(h) != 6:
                raise web.HTTPBadRequest(text="rgb must be 6 hex digits, e.g. ff0000\n")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        else:
            try:
                r, g, b = int(q["r"]), int(q["g"]), int(q["b"])
            except (KeyError, ValueError):
                raise web.HTTPBadRequest(text="provide rgb=RRGGBB or r=&g=&b=\n")
        try:
            payload = cmd_color(r, g, b)
        except ValueError as e:
            raise web.HTTPBadRequest(text=f"{e}\n")
        await ctrl.send(payload)
        return web.Response(text=f"color {r},{g},{b}\n")

    async def brightness(request: web.Request) -> web.Response:
        check_auth(request)
        try:
            level = int(request.query["level"])
            payload = cmd_brightness(level)
        except (KeyError, ValueError) as e:
            raise web.HTTPBadRequest(text=f"provide level=0..100 ({e})\n")
        await ctrl.send(payload)
        return web.Response(text=f"brightness {level}\n")

    async def status(request: web.Request) -> web.Response:
        return web.json_response({"connected": ctrl.connected, "address": ctrl.address})

    app = web.Application()
    app.add_routes([
        web.get("/on", on),
        web.get("/off", off),
        web.get("/color", color),
        web.get("/brightness", brightness),
        web.get("/status", status),
    ])
    return app


async def run_scan() -> None:
    print("Scanning for 10s ... (look for ELK-BLEDOM / MELK / LEDBLE / KS...)")
    devices = await BleakScanner.discover(timeout=10.0)
    for d in sorted(devices, key=lambda x: x.address):
        print(f"  {d.address}   {d.name or '(no name)'}")


def main() -> None:
    p = argparse.ArgumentParser(description="Tenmiro/keepsmile BLE -> HTTP bridge")
    p.add_argument("--address", help="BLE MAC address of the controller")
    p.add_argument("--name", default="ELK-BLEDOM", help="advertised name to match if no address")
    p.add_argument("--host", default="0.0.0.0", help="HTTP bind host")
    p.add_argument("--port", type=int, default=8765, help="HTTP port")
    p.add_argument("--scan", action="store_true", help="just list nearby BLE devices and exit")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if args.scan:
        asyncio.run(run_scan())
        return

    token = os.environ.get("BRIDGE_TOKEN")
    if token:
        log.info("Auth enabled: requests must include ?token=...")

    ctrl = LightController(address=args.address, name=args.name)
    app = make_app(ctrl, token)
    log.info("Serving on http://%s:%d", args.host, args.port)
    web.run_app(app, host=args.host, port=args.port, print=None)


if __name__ == "__main__":
    main()
