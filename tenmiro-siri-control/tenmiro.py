#!/usr/bin/env python3
"""
tenmiro.py - one-shot BLE control for a Tenmiro / keepsmile (ELK-BLEDOM
family) LED strip.

Built for the macOS Shortcuts "Run Shell Script" action: it connects, sends a
single command, and exits. Pair it with a Siri-triggered Shortcut and you get
voice control on a Mac with no extra hardware (the Mac's own Bluetooth talks
to the strip).

Usage:
    python3 tenmiro.py scan                 # list nearby BLE devices
    python3 tenmiro.py on
    python3 tenmiro.py off
    python3 tenmiro.py color ff0000         # 6 hex digits (red)
    python3 tenmiro.py color 0 128 255      # r g b (0-255)
    python3 tenmiro.py brightness 50        # 0-100

Target selection (env vars, so the Shortcut doesn't hard-code args):
    TENMIRO_ADDRESS=AA:BB:CC:DD:EE:FF   # pin the exact device (most reliable)
    TENMIRO_NAME=ELK-BLEDOM             # or match by advertised name

Install once:
    python3 -m pip install --user bleak

macOS note: the first run triggers a Bluetooth permission prompt for whatever
runs it (Terminal, or the Shortcuts app). Grant it under System Settings ->
Privacy & Security -> Bluetooth.
"""

from __future__ import annotations

import asyncio
import os
import sys

from bleak import BleakClient, BleakScanner

WRITE_CHAR_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"  # try FFE1 if ignored


def cmd_power(on: bool) -> bytes:
    if on:
        return bytes([0x7E, 0x00, 0x04, 0xF0, 0x00, 0x01, 0xFF, 0x00, 0xEF])
    return bytes([0x7E, 0x00, 0x04, 0x00, 0x00, 0x00, 0xFF, 0x00, 0xEF])


def cmd_color(r: int, g: int, b: int) -> bytes:
    for name, v in (("r", r), ("g", g), ("b", b)):
        if not 0 <= v <= 255:
            sys.exit(f"error: {name} must be 0-255, got {v}")
    return bytes([0x7E, 0x00, 0x05, 0x03, r, g, b, 0x00, 0xEF])


def cmd_brightness(level: int) -> bytes:
    if not 0 <= level <= 100:
        sys.exit(f"error: brightness must be 0-100, got {level}")
    return bytes([0x7E, 0x00, 0x01, level, 0x00, 0x00, 0x00, 0x00, 0xEF])


def parse_command(argv: list[str]) -> bytes:
    if not argv:
        sys.exit(__doc__)
    action = argv[0].lower()
    if action == "on":
        return cmd_power(True)
    if action == "off":
        return cmd_power(False)
    if action == "color":
        rest = argv[1:]
        if len(rest) == 1:  # hex form: ff0000
            h = rest[0].lstrip("#")
            if len(h) != 6:
                sys.exit("error: color hex must be 6 digits, e.g. ff0000")
            return cmd_color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        if len(rest) == 3:  # decimal form: r g b
            return cmd_color(int(rest[0]), int(rest[1]), int(rest[2]))
        sys.exit("error: color takes RRGGBB or three numbers r g b")
    if action == "brightness":
        if len(argv) != 2:
            sys.exit("error: brightness takes one number 0-100")
        return cmd_brightness(int(argv[1]))
    sys.exit(f"error: unknown command {action!r}")


async def resolve_address() -> str:
    addr = os.environ.get("TENMIRO_ADDRESS")
    if addr:
        return addr
    name = os.environ.get("TENMIRO_NAME", "ELK-BLEDOM")
    device = await BleakScanner.find_device_by_filter(
        lambda d, _adv: bool(d.name and name.lower() in d.name.lower()),
        timeout=15.0,
    )
    if device is None:
        sys.exit(f"error: no BLE device matching name {name!r}; set TENMIRO_ADDRESS")
    return device.address


async def run_scan() -> None:
    print("Scanning 10s (look for ELK-BLEDOM / MELK / LEDBLE / KS...)")
    for d in await BleakScanner.discover(timeout=10.0):
        print(f"  {d.address}   {d.name or '(no name)'}")


async def send(payload: bytes) -> None:
    address = await resolve_address()
    async with BleakClient(address) as client:
        await client.write_gatt_char(WRITE_CHAR_UUID, payload, response=False)


def main() -> None:
    argv = sys.argv[1:]
    if argv and argv[0].lower() == "scan":
        asyncio.run(run_scan())
        return
    payload = parse_command(argv)
    asyncio.run(send(payload))


if __name__ == "__main__":
    main()
