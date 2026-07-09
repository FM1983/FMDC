# FMDC Games

## F-117A Stealth Fighter — Night Strike 🛩️ (`/f117a/`)

A one-file, mobile-first retro tribute to the classic early-90s stealth flight sims.
Original code and art — software flat-shaded 3D on HTML5 Canvas, no dependencies, installable PWA.

👉 **Play:** <https://fm1983.github.io/FMDC/f117a/> (best on a phone in landscape; Add to Home Screen for fullscreen) — or open `f117a/index.html` locally.

- **Cockpit flight sim** with pitch ladder, heading tape, speed/altitude boxes, radar altimeter and stall/pull-up warnings.
- **Stealth gameplay:** an EMV bar shows your radar visibility (bay doors, gear, altitude and bank all matter). Thread the gaps between SAM/radar rings on the tactical MAP, or fly low to shrink them.
- **Air defenses:** EW radars, SAM sites with guided missiles, MiG combat air patrols. Break locks with hard turns, terrain masking and chaff/flares.
- **Weapons:** laser-guided bombs against ground targets (with a release envelope and bay-door tradeoff) and AIM-9s for MiGs.
- **Full sortie loop:** take off, ingress via waypoints, destroy the primary, egress, land back home (manual or AUTOLAND).
- **5 scripted missions** (desert, gulf, delta, arctic, capital) + endless generated deep strikes, career score, ranks and mission unlocks saved in `localStorage`.
- **Touch-first controls:** virtual stick, throttle slider, and buttons for FIRE / TGT / WPN / BAY / countermeasures / gear / map / time-compression / autoland — plus full keyboard support on desktop.

## Scorched Mobile 💥 (`/index.html`)

A one-file, mobile-first rebuild of the classic DOS artillery game **Scorched Earth**.
Pure HTML5 Canvas + JavaScript — no build step, no dependencies, works offline as an installable PWA.

👉 **Play:** open `index.html` in any modern browser (best on a phone).

## Features

- **Turn-based artillery duels** for 2–4 tanks on procedurally generated, fully destructible terrain.
- **Touch-first controls** — drag from your tank to aim (distance = power), or use the angle/power sliders and nudge buttons.
- **Wind** that pushes shots — read the arrow before you fire.
- **Trajectory preview** so you can plan your arc.
- **6 weapons:** Standard (∞), Big Shot, Nuke, Roller, MIRV (4-way split) and Digger.
- **Smart CPU opponents** that solve firing solutions by simulation (0–N of them; set them all to CPU for a watch-mode demo).
- **Falling damage / collapsing terrain**, explosions, screen shake and particle FX.
- **Match scoreboard** across rounds, multiple terrain types and HP presets.
- **Installable & offline** via web manifest + service worker. Add to Home Screen for a fullscreen app.

## Controls

| Action | How |
| --- | --- |
| Aim | Drag from your tank, or use the **Angle** / **Power** sliders & ± buttons |
| Switch weapon | Tap the weapon button (cycles through ones with ammo) |
| Fire | Tap **FIRE** (or Space on desktop) |
| Desktop keys | Arrows = aim, Space = fire, Tab = next weapon |

## Tech

Everything lives in `index.html` (game engine, physics, AI, rendering, UI).
`sw.js` + `manifest.webmanifest` + `icon.svg` make it an offline-capable PWA.

Run locally with any static server, e.g.:

```sh
python3 -m http.server 8000
# then open http://localhost:8000 on your phone (same Wi-Fi) or desktop
```
