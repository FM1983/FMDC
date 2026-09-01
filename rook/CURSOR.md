# Building Rook in Cursor — the working brief

`SPEC.md` (same folder) is the operative contract — v2.0, sixteen provenance-backed
requirements P1–P16. This file is what you hand Cursor: a kickoff prompt, and a rules
file to drop into the build repo so every Cursor session stays inside the contract.

## 0. Repo setup (one-time, manual)

1. Create a **private** repo `FM1983/rook`.
2. Copy into its root: `SPEC.md`, and the rules block below saved as `.cursor/rules/rook.mdc`
   (Cursor picks up `.cursor/rules/*.mdc` automatically; legacy `.cursorrules` also works).
3. Open the repo in Cursor and paste the kickoff prompt.

## 1. Kickoff prompt (paste into Cursor)

> Read SPEC.md in full before writing anything. Build Phase 0 · Steel exactly as
> specified in §8: a pnpm monorepo — `apps/mobile` (Expo, custom dev client,
> TypeScript), `apps/server` (Fastify, argonaut :8791, SQLite + Drizzle),
> `apps/web` (Next.js companion), `packages/shared` (zod schemas, shared types).
> Wire tailnet-only serving, Tailscale identity, `/api/health`, and a direct-APNs
> hello-world push (node-apn, token .p8, generic payload). Stop at the Phase 0
> gate and show me how to run it: a push arrives with the app closed, the tap
> opens the app, `/api/health` over tailnet shows my identity. Do not start
> Phase 1 until the gate passes on a real phone.

Then drive phase by phase: each of the six phases in SPEC.md §8 ends with a runnable
gate — make Cursor demonstrate the gate before moving on. "Looks good" is not a test.

## 2. Rules — save as `.cursor/rules/rook.mdc` in FM1983/rook

```
---
description: Rook — Citadel command app. Non-negotiable build rules.
alwaysApply: true
---

- SPEC.md is the contract. Every feature must trace to a requirement P1–P16;
  anything that serves none of them gets cut, not built.
- Monorepo: apps/mobile (Expo RN, custom dev client), apps/server (Fastify,
  SQLite + Drizzle, append-only events), apps/web (Next.js), packages/shared
  (zod schemas — one brain, two runtimes). TypeScript everywhere, strict.
- Tailnet-only. No public exposure, no Funnel, no cloud hosts. The server binds
  loopback + tailscale serve. Never add a third-party transit for anything.
- Push is direct APNs via node-apn with a .p8 token. Payloads are GENERIC —
  counts and labels only, never matter names, never privileged content.
- Secrets: nothing in the repo, ever. Keys live in the server keychain/env on
  argonaut. The OpenRouter key is provided out-of-band and never written to
  Dropbox or the phone.
- LLM gateway: deterministic router, two tiers (OpenRouter conversation tier /
  Anthropic grunt tier). Privileged-flagged matters MUST NOT reach OpenRouter —
  enforce in the router by matter flag and keep the CI canary test green.
  Every call is priced into _ROOK/ledger/llm.jsonl.
- The assistant acts only through the allow-listed tools (query_items, get_item,
  add_amendment, stage_dispatch, draft_card, defer_item, tick_option-with-confirm).
  Enforce the list server-side. It may stage; it may NEVER release or send.
- Rook stages, humans release: release is a first-class event with actor,
  timestamp, ROK token, proof pointer. Events are append-only — supersede,
  never overwrite; every state change stores the five proof fields
  (timestamp / actor / transition / proof / verifier).
- Click-through everywhere (P16): any UI string naming a folder, file, document,
  email thread or calendar entry must render as a live link — Dropbox deep link,
  tailnet-streamed preview, 8787 mailbox excerpt, or iOS Calendar. The importer
  resolves every path it ingests into a context_ref automatically; an
  unresolvable path renders flagged, never silent. No dead references.
- Offline-first mobile: expo-sqlite mirror + action queue with sync_state,
  lossless replay on reconnect. No privileged bodies cached on-device — refs
  and streamed previews only; purge on lock.
- Dropbox stays canonical during the 30-day parallel run; Rook writes markdown
  + JSONL under GODS-EYE/_ROOK/ that any machine can read with cat.
- Design tokens are literal input, not guidelines: bone #F3EFE6, ink #211F19,
  Citadel green #727C60 (the only accent), rust #8A4B38 (criticals only).
  Archivo with tabular numerals for UI; Fraunces for the wordmark alone.
  44-point touch targets; dark mode is first-class.
- Phase gates in SPEC.md §8 are the test plan. Do not start phase N+1 until
  gate N passes on a real device.
```

## 3. What argonaut needs before Phase 0

- Apple Developer account for `capital.citadel` (APNs .p8 + TestFlight) — the
  one open item that blocks day one.
- Tailscale up (already true), Node 22, pnpm, and read/write on the local
  Dropbox team folder (already true for the sweeps).
