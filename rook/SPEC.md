# ROOK — the Citadel board console
**Build specification v1.0 · 2 September 2026 NZT · Confidential — internal**

A mobile-first web app that replaces reading `BOARD.md` with operating it: review board items, call up their context, record decisions and amendment notes at the moment they happen, and stage instructions to machine agents and to people — with release as an explicit, logged, one-tap act. Two-way live sync with the machine fleet over the existing Dropbox + tailnet architecture. Named for the Citadel rook.

---

## 0. Why this exists (requirements with provenance)

Every requirement below is motivated by a named failure already on the record. This table is the contract; if a feature doesn't serve one of these, cut it.

| # | Incident on the record | Requirement it creates |
|---|---|---|
| P1 | `BOARD.md` at 688KB, re-ballooned after the 13 Aug split; "one file eating a third of a context window" | Items live in a **database**, not a file. Markdown becomes a *generated view*, never the store. |
| P2 | Codex audit R013: "**no stable decision object**"; confidence "What did Farhad decide?" 3/5 | A typed, versioned **Item** with append-only history is the core entity. |
| P3 | "No genuine FM decision recorded since 13 Aug (auto-replies masquerading as FM)" — later shown to be **state-lag**: decisions made, recorded late or never | Decisions are captured **on the phone at the moment of decision**, not reconstructed by a sweep afterwards. Signed by identity, not inferred from mailbox tone. |
| P4 | Terra C9: "the machine drafted the form… rang the bell twice. The decision never came. **An alert is not an action**" | Deadline items *require* a decision transition. Undecided criticals escalate: push at T-48h, T-24h, T-3h, each logged. |
| P5 | The standing failure mode: "**a completed document waiting on a release decision**" (insurer letter unreleased since 23 Aug; Connal instruction promised, never sent; s357B "four drafts of the filing email sat unsent") | A **Dispatch Review** screen: everything staged, one tap to release, release tokens logged. Staged-but-unreleased items age visibly and nag. |
| P6 | "Whether it was actually sent is NOT recorded" (s357B); "machine sends nothing; FM sends" | Release is a first-class event with actor, timestamp, token (`ROK20260902A` style), and a proof pointer to the sent artifact. |
| P7 | The 34-hour launchd outage, "root cause… not further diagnosed"; silence looked like health | A **freshness banner** on every screen: "last sweep seen N min ago." Staleness > 45 min turns the app amber and pushes once. The watchdog is independent of the thing it watches. |
| P8 | Audit: "Move Farhad from default integration layer to **explicit material-decision gate**"; "Velocity is visible. Closure is not." | The app *is* the gate. Metrics measure the interval the audit named: raised→decided→released→**verified**. |
| P9 | "Phone calls are invisible to this machine" (Connal caveat); Otter meeting: "ten of the thirteen action items are uncaptured" | **Quick capture**: 10-second voice/dictation note attaches an outcome to an item; meeting-link capture spawns staged items from a transcript. |
| P10 | Privileged matters (Duncan LitSim, Police file) and the local-only doctrine ("no cloud host holds the corpus") | **Tailnet-only. No cloud hosting.** Role-scoped visibility; privileged matters FM-only by default. |
| P11 | Five-field proof pilot mandated by the audit: *timestamp / actor / transition / proof / verifier* | The event ledger stores exactly these five fields on every state change. Rook **is** the proof pilot. |
| P12 | Google Workspace single-instrument fragility (3 Sep suspension risk) | Rook must run with Google down: Dropbox-file transport for machine instructions; Gmail used only as an optional channel for people. |

## 1. Product definition

**One sentence.** Rook turns the GODS-EYE board from a document Farhad reads into a queue Farhad clears — from a phone, in gaps between meetings, with every decision, note and dispatch landing back in the canonical record within a minute.

**Users & roles.**
- **FM (owner):** sees everything incl. privileged; the only role that can *release* dispatches and close criticals.
- **Brandon / Zach / Nicki (operators):** scoped to their lanes; can review, comment/amend, stage instructions, mark their own tasks done; cannot release on FM-gated items; privileged matters hidden unless granted per-matter.
- **Machine agents (non-human):** GODS-EYE sweeps, workstream orchestrators, Nimbalyst sessions. They write board state in and consume instruction files out. No UI login; they speak files and one ingest API.

**Explicit non-goals (v1).** Not a chat client; not a document editor; not a Gantt tool; not a replacement for the daily briefings, the Reference Library app, or the 8787 briefing room (Rook links into them). No public internet exposure. No autonomous sending — Rook *stages*; humans release. "The next phase is not more reports, more dashboards or more agents" — Rook is none of those; it is the gate.

## 2. Architecture

```
                    ┌────────────────────── tailnet (Tailscale) ─────────────────────┐
 iPhone (PWA) ──────►  rook.<tailnet>.ts.net  ──► Next.js app (argonaut, :8791)      │
 Laptop browser ────►                              │  SQLite (rook.db) + event log   │
                                                   │  SSE stream to clients          │
                                                   ▼                                 │
                                        rook-syncd (daemon, argonaut)                │
                                        │ ingest: fs.watch on local Dropbox —        │
                                        │   GODS-EYE/board.json, registers, digests, │
                                        │   agendas, run-log tail, agent ACK files   │
                                        │ egest: write canonical .md artifacts into  │
                                        │   Dropbox _ROOK/ tree (ledger, dispatches) │
                                        ▼                                            │
   Dropbox (team folder, source of truth) ◄──── sweeps / orchestrators / Nimbalyst   │
                                                on argonaut, citadel-intel, laptops  │
```

**Key decisions, made:**
1. **Host on argonaut** (it already runs the sweeps and has the team Dropbox locally synced). Bind to localhost; expose via `tailscale serve` → `https://rook.<tailnet>.ts.net` with automatic TLS. Phone access = Tailscale iOS app with on-demand VPN → the PWA is indistinguishable from a normal app. **Funnel stays off** (P10). 
2. **Dropbox remains the canonical archive; SQLite is the operating store.** The daemon ingests machine output from the local Dropbox folder (no Dropbox API, no webhooks — the folder *is* the bus, same as the rest of the fleet) and egests Rook's own record as markdown+JSONL into `Misc-Working/A-PRIORITY/GODS-EYE/_ROOK/`. Any machine, and any future audit, can read Rook's record with `cat`.
3. **Authority migrates in two stages.** Stage 1 (launch → +30 days): board.json remains authoritative; Rook mirrors it and appends its own decisions/dispatches; sweeps ingest `_ROOK/` and reconcile. Stage 2 (after a clean 30-day parallel run — the audit's own pilot standard): inversion — Rook's DB becomes the writer of record and `BOARD.md`/`board.json` become *generated* views produced by rook-syncd. Do not flip early.
4. **Identity = Tailscale.** The app reads the tailnet identity headers (`tailscale serve` passes them; fall back to `tailscale whois` on the socket). Device ↔ person map is 6 rows in config. No passwords, no OAuth, nothing to phish, works offline-first on the phone.
5. **Reuse, don't rebuild:** mailbox context comes from the existing briefing-room API on argonaut:8787 (thread excerpts by Gmail id); Telegram pings reuse the existing GODS-EYE console bot; `gmail_sa` (drafts-only) prepares people-directed emails. Rook adds no new external surface.

## 3. Data model (Drizzle/SQLite; zod-mirrored)

```ts
// The stable decision object (P2). Series ids preserved on import: R-, D-, DL-, G-.
items {
  id           text pk          // "ROK-000123"; legacy_id nullable ("D80","R45")
  kind         enum             // decision | red_flag | gate | deadline | front | instruction | note
  matter       text             // "terra", "babich", "126fs", "police", "mcleans", "ryu", "armada", "machine", ...
  lane         enum             // litigation | commercial | machine | governance | personal
  title        text
  body_md      text             // current statement of the item (superseded versions live in events)
  severity     enum             // crit | high | med | low
  status       enum             // open | decided | staged | dispatched | acknowledged | done | verified | closed | superseded
  owner        text             // person or agent slug
  due_at       datetime?
  raised_at    datetime
  source       enum             // sweep | import | human | meeting | capture
  source_ref   text?            // dropbox path#anchor, gmail id, calendar id
  privileged   bool             // FM-only unless per-matter grant
}
context_refs { id, item_id fk, type/*dropbox|gmail|calendar|url|quote*/, ref, excerpt, pinned, added_by, added_at }
amendments   { id, item_id fk, author, kind/*note|correction|question*/, body_md, created_at, sync_state }
dispatches   { id, item_id fk?, to_type/*agent|person*/, to_slug, body_md,
               channel/*inbox_file|gmail_draft|telegram|manual*/,
               state/*staged|released|acknowledged|done|verified|recalled*/,
               staged_by, staged_at, released_by?, released_at?, token?/*ROK20260902A*/,
               ack_at?, proof_ref?, verified_by?, verified_at? }
events       { id, item_id fk, ts, actor, transition, proof, verifier }   // exactly the five fields (P11)
health       { source pk /*sweep|syncd|telemetry|workspace*/, last_seen_at, status, note }
```

Rules: **events are append-only** ("supersede, never overwrite"); every status change writes an event; `body_md` edits write a `superseded-text` event carrying the prior text; deleting is `status=superseded`, never a row delete. Nightly: `rook.db` snapshot + continuous `events.jsonl` mirror into `_ROOK/ledger/` (survives the laptop, satisfies any future audit from flat files).

## 4. The two-way machine contract

**Inbound (machines → Rook), all via local Dropbox paths watched by rook-syncd:**
- `GODS-EYE/board.json` → upsert items (id-mapped via `legacy_id`), never clobbering fields Rook owns (status past `open`, amendments, dispatches).
- `GODS-EYE/03-outputs/digests/*.md`, `agendas/*.md` → attach as context to matching matters; feed the Today screen's "what the machine says" strip.
- `GODS-EYE/session-log/run-log.md` (tail) → `health.sweep.last_seen_at` (P7).
- `_ROOK/inbox-ack/**` → dispatch `acknowledged`/`done` transitions (see outbound).
- Workstream registers (`_CONTEXT.md` frontmatter, `*/_llm/outputs/CHANGELOG.md` last rows) → high-water counters on matter cards.

**Outbound (Rook → machines and people):**
- `_ROOK/decisions/2026-09-02_ROK-000123.md` — one file per decision, YAML frontmatter (id, legacy_id, actor, ts, transition, proof, verifier) + body. Sweeps and Nimbalyst sessions ingest these as **rulings**; this is how "FM ruled in Rook" reaches every workstream without any agent integrating anything new.
- `_ROOK/dispatch/<agent-slug>/ROK-D-0045.md` — instruction files per agent inbox (frontmatter: token, released_by, released_at, due, ack_required, item refs). Agent contract: on pickup write `_ROOK/inbox-ack/ROK-D-0045.ack.md` (start) and `.done.md` (completion, with proof pointer). One page of doctrine added to `Citadel-AI/MODEL-ROUTING.md` makes every existing session check its inbox at wake — no code changes to agents.
- People: dispatch renders to (a) a scoped Rook view for Brandon/Zach/Nicki, (b) optional `gmail_sa` **draft** in FM's mailbox for one-tap send, (c) optional Telegram ping via the existing bot. Rook never emails anyone directly (P6, P12).

## 5. Screens (mobile-first; six, no more)

1. **Today (default).** Freshness banner. Then a triage stack, hardest-gated first: criticals with dates ≤ 72h, then staged-unreleased (aging badge, P5), then new-since-last-visit. Card = title, matter chip, severity dot, due, one-line machine summary. **Swipe right = Decide** (opens dictation-ready note → status `decided`, event written, `_ROOK/decisions/` emitted). **Swipe left = Defer** (pick: tomorrow / next gate / date). **Long-press = Delegate** (pick person/agent → becomes staged dispatch). Three actions, one thumb.
2. **Queue.** The full D-series successor. Filter chips: matter, lane, severity, status, owner, privileged. Sort: due, age, raised. Bulk: select → defer/close/supersede (the "done — drop next sweep" items that haunted the board for a month die here in one gesture).
3. **Item.** Everything about one item: current statement; **Context** (pinned quotes, linked Dropbox docs — tap to open in Dropbox app; Gmail excerpts via 8787; the calendar entry); **History** (the event ledger, human-readable); **Amendments** (add note/correction/question — P9 voice capture lives here); **Actions**: Decide / Amend / Stage dispatch / Link context / Mark verified (requires proof ref — the verify step the audit found missing).
4. **Dispatch.** Two tabs. *Staged*: everything awaiting release, grouped by recipient, each with age badge and a **Release** button (FM only; writes token + event; fires the channel). *In flight*: released, awaiting ack/done/verify; overdue acks flagged. This screen is P5's fix and the heart of the app.
5. **Matters.** One card per front: status line, next hard date, output high-water, last-7-day activity spark, open/staged counts, link to the workstream's `_CONTEXT.md`. Replaces reading the board end-to-end to find out "where is Terra".
6. **Pulse.** Metrics (P8): decision latency (raised→decided, p50/p90), release latency (decided→released), queue burn-down chart, staged-age histogram, verified-vs-claimed ratio, sweeps/day, freshness history. The numbers the next Lightspeed volume will quote.

Plus a global **⌘K / pull-down search** (title, body, matter, legacy id) and **Quick capture** (+): dictate a thought → item or amendment, filed by matter picker; ≤ 10 seconds phone-out-to-phone-away (P3/P9).

## 6. Design system

House style, restrained for an operating surface: bone `#F3EFE6` paper (dark mode `#191713`), ink `#211F19`, **Citadel green `#727C60`** as the sole accent, rust `#8A4B38` for criticals/blown, Archivo for UI text and labels (tabular numerals for dates/amounts), Fraunces only for the wordmark "Rook." and empty-state lines. Tokens shipped as `tokens.css` and consumed literally — no reinterpretation (the RE:Arch lesson: "design token files are not 'guidelines' — they are literal input"). Density: list rows 44pt touch targets; one-hand reach for all three triage actions; no hover-dependent UI anywhere.

## 7. Stack & repo (Cursor-ready)

- **Next.js 15 (App Router) + TypeScript strict + Tailwind + shadcn/ui**; PWA via `manifest.json` + service worker (installable, offline shell, background sync for the offline queue: decisions made offline queue locally and emit on reconnect, marked `sync_state=pending` until the daemon confirms the Dropbox write).
- **Drizzle ORM + better-sqlite3**; zod schemas shared client/server; SSE (`/api/events/stream`) for live updates; no external services, no analytics, no CDN fonts (self-host Archivo/Fraunces woff2 — already in hand).
- **rook-syncd**: a separate long-running Node process (chokidar watchers + 60s reconciliation sweep + the watchdog). Runs under launchd **with** `KeepAlive`, `ThrottleInterval`, and a cross-check: the app alarms if syncd is silent, syncd alarms (Telegram) if the app is down — neither trusts the other's silence (P7).
- Repo `FM1983/rook` (private — satisfies the GitHub mandate): 

```
rook/
├─ SPEC.md                    # this document — the founding brief Cursor works from
├─ app/                       # Next.js routes: /(today|queue|item/[id]|dispatch|matters|pulse)
├─ components/                # shadcn-based; BoardCard, TriageStack, EventLedger, ReleaseButton…
├─ lib/{db,schema,zod,auth,tokens}.ts
├─ syncd/{ingest,egest,watchdog}.ts + launchd/com.citadel.rook.syncd.plist
├─ scripts/import-board.ts    # one-off BOARD.md + board.json + _MASTER-TRACKER migration
├─ tokens.css  manifest.json  drizzle/  tests/ (Playwright)
└─ README.md                  # run: npm i && npm run import && npm run dev  (one command each)
```

## 8. Security & privacy (the restricted-claims annex)

Tailnet-only; loopback bind; TLS via ts.net cert; identity from Tailscale, 6-row device map; privileged matters excluded from non-FM queries **at the query layer**, not the UI; no secrets in the repo — `gmail_sa` key stays where it lives today (never in Dropbox, per standing doctrine); event ledger immutable; `_ROOK/` inherits Dropbox team-folder ACLs (it contains rulings and dispatches — it is already the class of content the folder holds). Explicitly forbidden in v1: Funnel/public exposure, autonomous sending of anything, storing privileged LitSim/Police *documents* in rook.db (store refs, open in Dropbox), and any LLM call from inside Rook (agents do the thinking in their own sessions; Rook is deterministic).

## 9. Build plan — five phases, each with a runnable gate

RE:Arch discipline: phased gates, security before features; acceptance tests runnable, not "looks good"; each phase ends usable.

- **Phase 0 — Steel (day 1–2).** Repo, tokens, schema, migrations, Tailscale serve, identity middleware, health endpoint. ✅ *Gate:* `curl https://rook…/api/health` from the phone over tailnet returns identity + 200; non-tailnet request impossible.
- **Phase 1 — Mirror (day 2–5).** Importer + syncd ingest; Today/Queue/Item/Matters read-only; SSE; freshness banner; PWA install. ✅ *Gate:* a new red flag written by a live sweep appears on the phone < 60s; all current R/D rows present and filterable; Lighthouse PWA installable; **usable on day 5 even if nothing else ships.**
- **Phase 2 — Decide (day 5–8).** Decide/Defer/Amend + quick capture + offline queue; `_ROOK/decisions/` egest; doctrine page for sweeps to ingest rulings. ✅ *Gate:* decide an item on the phone in an offline lift, reconnect, see the `.md` in Dropbox and the next sweep's board reflect it — end-to-end < one sweep cycle. Five-field event visible for every transition.
- **Phase 3 — Dispatch (day 8–12).** Staging, Release with tokens, agent inbox/ack loop, gmail-draft + Telegram channels, Dispatch screen, aging + escalation pushes (web push). ✅ *Gate:* stage an instruction to a test agent, release it, agent acks by file, state flips on the phone; an unreleased staged item older than 48h has nagged exactly once a day; T-48/24/3 escalations fire on a synthetic critical.
- **Phase 4 — Prove (day 12–16).** Verify flow (proof-ref required), Pulse metrics, ledger mirror to Dropbox, watchdog cross-alarms, role scoping for Brandon/Zach/Nicki. ✅ *Gate:* the 30-day parallel run *starts*: metrics populated, `verified` count > 0, a deliberately-killed syncd is detected and alarmed within 10 minutes. Authority inversion (Stage 2, §2.3) is a decision Rook itself will carry as an item — decided in Rook, on the evidence of its own parallel run.

**Definition of done for v1:** FM clears real board items from the phone for a full week; ≥ 80% of that week's decisions exist in Rook *before* any sweep infers them; zero staged items silently older than 72h; the next Pulse report draws its decision-latency numbers from `/pulse` instead of grepping BOARD.md.

## 10. Open items (small, and none block Phase 0)

1. Telegram vs iOS web-push as the primary escalation channel (web push on iOS PWA is fine ≥ iOS 16.4; Telegram already exists — ship both behind one setting).
2. Whether Nicki's calendar-heavy view warrants a 7th screen (defer; Matters covers it).
3. board.json id stability — the importer must fingerprint rows (legacy id + title hash) because ids have collided before (two numbering collisions on 26 Aug are on the record).
4. Read-only "counsel view" (Claymore et al.) — explicitly out of scope v1; revisit only with a per-matter, time-boxed grant design.

*Rook: because the board should be operated with a thumb, not read like a novel.*
