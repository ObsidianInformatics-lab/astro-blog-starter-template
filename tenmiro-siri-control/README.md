# Siri control for a Tenmiro / keepsmile (ELK-BLEDOM) LED strip

Voice control ("Hey Siri, turn the ceiling lights blue") for a Bluetooth LED
strip sold under the **Tenmiro** brand and driven by the **keepsmile** app.

## Why you can't do this with Shortcuts alone

iOS **Shortcuts cannot send raw Bluetooth Low Energy (BLE) commands**. The
only Bluetooth action in Shortcuts toggles your iPhone's radio on/off — there
is no "write to a BLE characteristic" action. The keepsmile app talks to the
strip using Apple's Core Bluetooth framework (native app code); Shortcuts has
no equivalent. The strip is also **not HomeKit-certified**, so the Home app
can't see it directly either.

So every working solution needs a small **always-on bridge** that sits near
the light, speaks BLE on its behalf, and exposes something Siri *can* trigger
(HomeKit, or a plain web request). The three options below differ only in
*what* plays that bridge role.

## What your controller is

Tenmiro/keepsmile strips are rebadged **ELK-BLEDOM / MELK / LEDBLE** BLE
controllers. Confirm yours by checking the advertised Bluetooth name with a
scanner (nRF Connect / LightBlue on the App Store, or `python bridge.py
--scan` from this folder). It'll be something like `ELK-BLEDOM`, `MELK-…`, or
`KS…`.

### Protocol reference (write to characteristic `FFF3`, service `FFF0`)

| Action          | Bytes                                    |
|-----------------|------------------------------------------|
| Power ON        | `7E 00 04 F0 00 01 FF 00 EF`             |
| Power OFF       | `7E 00 04 00 00 00 FF 00 EF`             |
| Set color RGB   | `7E 00 05 03 RR GG BB 00 EF`             |
| Brightness 0–100| `7E 00 01 XX 00 00 00 00 EF` (`XX`=0–64h)|

If `FFF3` is ignored, try the `FFE1` characteristic.

---

## Option A — Home Assistant + HomeKit Bridge (most capable)

Best native Siri experience: full color wheel, brightness, dimming, "set the
lights to 20%", grouping with other lights, automations.

**You need:** a device that runs Home Assistant **and has Bluetooth within
range of the light** (Raspberry Pi 4/5, an Intel NUC/mini-PC, etc.).

1. Install Home Assistant (HAOS or the container/supervised install).
2. Add the **elkbledom** custom component — easiest via HACS, or copy it into
   `config/custom_components/`: <https://github.com/dave-code-ruiz/elkbledom>.
3. **Settings → Devices & Services → Add Integration → ELK BLEDOM**, pick your
   strip from the discovered BLE devices. It appears as a `light` entity.
4. Add the **HomeKit Bridge** integration (Settings → Devices & Services → Add
   Integration → HomeKit Bridge) and include that light entity.
5. On your iPhone, open **Home**, tap **+ → Add Accessory**, and scan the
   pairing QR code HA shows (or enter the setup code). The strip now lives in
   the Home app.
6. Siri works automatically: *"Hey Siri, turn on the ceiling lights / make
   them red / set them to 30%."*

---

## Option B — ESP32 + ESPHome (cheap; HA can live anywhere)

Same Siri result as Option A, but a ~$5–10 ESP32 sits next to the light and
does the Bluetooth, relaying to Home Assistant over Wi-Fi. Use this when your
HA box isn't physically near the strip.

**You need:** any ESP32 dev board + a Home Assistant install (anywhere on the
network) for the HomeKit bridging step.

1. Install ESPHome (the HA add-on or the standalone CLI/dashboard).
2. Use [`esphome-tenmiro.yaml`](./esphome-tenmiro.yaml) from this folder.
   Replace the `mac_address` with your strip's address and put your Wi-Fi/API
   secrets in `secrets.yaml`.
3. Flash it to the ESP32 and place the board near the light.
4. Add the ESP32 in Home Assistant (it's auto-discovered). You get a
   `Tenmiro Ceiling Strip` light entity.
5. Expose that entity through HA's **HomeKit Bridge** (steps 4–6 of Option A).

> Note: ESPHome itself doesn't speak HomeKit — Siri still comes via Home
> Assistant's HomeKit Bridge. The ESP32's only job is the BLE link.

---

## Option C — Web-request bridge + Shortcuts (no HomeKit, most DIY)

No Home Assistant, no HomeKit. A tiny Python service exposes HTTP endpoints;
iOS Shortcuts call them with "Get Contents of URL" and you attach Siri
phrases. Quickest to stand up; gives you discrete commands (on, off, named
colors, brightness) rather than a full color wheel in the Home app.

**You need:** any always-on machine with Bluetooth near the light (Raspberry
Pi, old laptop, mini-PC).

### 1. Run the bridge

```bash
cd tenmiro-siri-control
pip install -r requirements.txt

# find your strip:
python bridge.py --scan

# run it (pin the address once you know it — more reliable than name match):
python bridge.py --address AA:BB:CC:DD:EE:FF
# default: listens on http://<this-machine-ip>:8765
```

Optional: set a shared secret so only you can trigger it:

```bash
BRIDGE_TOKEN=mysecret python bridge.py --address AA:BB:CC:DD:EE:FF
# then append ?token=mysecret to every URL below
```

Keep it running across reboots with a `systemd` service, `tmux`, `pm2`, etc.

### 2. Endpoints

| URL                                   | Effect                  |
|---------------------------------------|-------------------------|
| `http://PI_IP:8765/on`                | turn on                 |
| `http://PI_IP:8765/off`               | turn off                |
| `http://PI_IP:8765/color?rgb=ff0000`  | red (any 6 hex digits)  |
| `http://PI_IP:8765/color?r=0&g=128&b=255` | color by components |
| `http://PI_IP:8765/brightness?level=50` | brightness 0–100      |
| `http://PI_IP:8765/status`            | JSON connection state   |

### 3. Build the Shortcut

For each command:

1. Open **Shortcuts → +** (new shortcut).
2. Add action **Get Contents of URL**, set the URL (e.g.
   `http://192.168.1.50:8765/on`). Leave method as GET.
3. Name the shortcut something speakable, e.g. **"Ceiling lights on"**.
4. Run it once and grant the Local Network permission prompt.
5. Say *"Hey Siri, Ceiling lights on."* (Siri uses the shortcut's name as the
   trigger phrase; rename to taste.)

Repeat for off / each color / brightness. Tip: a shortcut can **Ask for
Input** or use a menu, so one "Set ceiling color" shortcut can prompt for a
color and build the URL dynamically.

> This works only on your home network (or via VPN/Tailscale back home). It's
> not exposed to the internet, which is what you want for a light controller.

---

## Which should I pick?

- **Want the best Siri/Home experience and have a Pi/mini-PC near the light?**
  → Option A.
- **HA lives elsewhere, or you'd rather drop a $5 chip by the strip?**
  → Option B.
- **Just want a few voice commands fast and like tinkering?**
  → Option C.

## Files in this folder

- [`bridge.py`](./bridge.py) — Option C BLE→HTTP bridge (Python, bleak+aiohttp).
- [`requirements.txt`](./requirements.txt) — Python deps for the bridge.
- [`esphome-tenmiro.yaml`](./esphome-tenmiro.yaml) — Option B ESP32 config.

## Credits / references

- ELK-BLEDOM Home Assistant integration: <https://github.com/dave-code-ruiz/elkbledom>
- Protocol reverse-engineering write-up: <https://joshspicer.com/bluetooth-low-energy-home-assistant>
- HA community thread: <https://community.home-assistant.io/t/controlling-a-bluetooth-led-strip-with-ha/286029>
