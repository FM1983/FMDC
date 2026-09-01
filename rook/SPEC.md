# ROOK — the Citadel command app
**Build specification v2.1 · 2 September 2026 NZT · Confidential — internal · supersedes v1.0**

A **native iPhone app** — one app to rule them all — that turns the GODS-EYE board into an operable queue: review categorised items, call up context, **decide by ticking options in tabular checkbox cards (with free-text always available)**, make amendment notes, stage instructions to machine agents and to people, release with one logged tap, and **talk to the board hands-free** through a voice assistant plumbed into the group's model fleet. Two-way live sync with the machines over the existing Dropbox + tailnet architecture; **push notifications** for criticals and escalations.

v2 changes from v1: native iOS (not PWA-first) · APNs push · decision **option cards** (categorised checkbox tables + text entry) as the universal ruling pattern · a **voice chat** layer · an **LLM gateway** (v1's "no LLM inside Rook" rule is superseded, with hard data boundaries) · consolidation roadmap ("one app") · click-through links to folders, files and documents from every panel · a mandatory item brief · traffic-light priority · a coverage reconciler (nothing missed) · draft discipline (no speculative emails).

---

## 0. Why this exists (requirements with provenance)

| # | Incident on the record | Requirement it creates |
|---|---|---|
| P1 | `BOARD.md` at 688KB, re-ballooned after the 13 Aug split | Items live in a **database**; markdown is a generated view. |
| P2 | Audit R013: "**no stable decision object**" | A typed, versioned **Item** with append-only history. |
| P3 | "No genuine FM decision recorded since 13 Aug" — state-lag: decisions made, recorded late or never | Decisions captured **on the phone at the moment of decision**, signed by identity. |
| P4 | Terra C9: "an alert is not an action" | Deadline items *require* a decision transition; undecided criticals **push-escalate** at T-48h/T-24h/T-3h. |
| P5 | "A completed document waiting on a release decision" (insurer letter, Connal instruction, s357B drafts) | **Dispatch Review** screen; staged items age visibly and nag; one-tap release. |
| P6 | "Whether it was actually sent is NOT recorded" · "machine sends nothing; FM sends" | Release = first-class event: actor, timestamp, token (`ROK…`), proof pointer. Rook stages; a human releases. |
| P7 | The 34-hour launchd outage; silence looked like health | Freshness banner everywhere; independent cross-alarming watchdogs; staleness pushes once. |
| P8 | "Velocity is visible. Closure is not." | Metrics on the audited interval: raised → decided → released → **verified**. |
| P9 | "Phone calls are invisible" · 10 of 13 meeting actions lost | 10-second voice capture; meeting-link ingestion spawns staged items. |
| P10 | Privileged matters + "no cloud host holds the corpus" | Tailnet-only data plane; role scoping at the query layer; privileged = FM-only. |
| P11 | The audit's five-field proof pilot | Every state change stores timestamp / actor / transition / proof / verifier. |
| P12 | One failed payment instrument nearly took Workspace + Anthropic + Notion at once | Runs with Google down; file transport for machines; channel redundancy for pushes. |
| **P13** | **FM already rules by option paper and checkbox** — B005 was "a five-option paper for FM's ruling"; the 13 Aug burn-priorities went out as "FM checkbox, executed"; agents write options, FM ticks | **Option Cards**: categorised, tabular checkbox choices on any item, single- or multi-select, consequence column, free-text "in your own words" always present. Agents author cards as files; the app renders them natively. |
| **P14** | 8 Sep: a court appearance at 2:15pm and a 16:10 flight in one afternoon; decisions happen in cars, lifts and corridors | **Native app + push + voice.** Hands-free review and ruling; notifications that arrive without the app open; offline queue everywhere. |
| **P15** | A routing doctrine already exists and works: "the scarce resource is Claude context"; Kimi/OpenRouter routes carry confidentiality gates; "force Kimi to do the heavy lift… Don't hold back"; Opus drafts, detached | Rook's LLM layer **reuses the fleet doctrine**: an efficient OpenRouter-sourced Chinese frontier model as the conversational brain; **Opus 5 for the grunt work**, detached; privileged content never leaves the Anthropic/local boundary. |
| **P16** | The board's panels name documents the reader then has to hunt for — paths quoted in prose, "see file" with no way to open it | **Click-through everywhere.** Every folder, file, document, email thread or calendar entry a panel names is a live link — one tap opens it. No dead references anywhere in the UI. |
| **P17** | FM, 2 Sep: "the board needs to provide clear context of the matter or issue" — items surface as bare titles while context sits buried in a 688KB file or three folders away | Every item opens with a **brief**: two to four plain sentences — what the matter is, what changed, what is being asked, by when. No item renders as a title alone; a stale brief is marked stale on its face. |
| **P18** | Severity exists as a word in a column; nothing tells the thumb what to touch first | A **traffic light** on every item, derived by deterministic rules — never agent vibes. RED pushes, AMBER waits for the 07:00 summary, GREEN never pushes. Recolouring is a logged event with a reason. |
| **P19** | FM, 2 Sep: "a failure of the board to pick up key items" — and the record agrees: ten of thirteen meeting actions lost; lanes ahead of the board (OD044–OD048 with no board row); stale statements standing on lane faces | Coverage is a **testable property**: a reconciler diffs the board against lane records and raises candidate items for anything missing; a nightly grunt job stages what looks decision-shaped from the day's corpus; Pulse carries a **Caught-late** metric. A missed item is a defect with a number, not an anecdote. |
| **P20** | FM, 2 Sep: "stop drafting emails I will never send" — AI slop, often without context; OH003 rev B sat live in the Gmail drafts folder as "the live hazard"; three drafts stood against the same two people at once | **Draft discipline.** Agents never write to the Gmail drafts folder. An outbound message exists only as a Rook staged dispatch carrying provenance — item, ruling, author; the gmail_sa draft is created at release time, on the human tap. Aging staged drafts auto-supersede; orphan Gmail drafts are flagged for one-tap deletion. No draft without a ruling behind it. |

## 1. Product definition

**One sentence.** Rook is the one Citadel app: the board in your pocket — categorised queues you clear with checkboxes, context on tap, dispatches you release with a thumb, a voice you can talk to on the motorway, and notifications that find you before deadlines do.

**Roles.** FM (everything, sole releaser of FM-gated items, privileged visibility) · Brandon/Zach/Nicki (scoped lanes, can review/amend/stage/complete, per-matter privileged grants) · machine agents (no UI — files in, files out) · the assistant (a tool-using session inside the gateway; may query and stage; may **never** release, send, or see privileged matter content unless running on the privileged tier).

**One app to rule them all — consolidation roadmap.** v2 ships the board, dispatch, capture and voice. The same app then absorbs, as read surfaces: the daily briefing/digest (v2.1), matter context packs and the 8787 mailbox excerpts (v2.1), Pulse metrics (v2.0 already), agenda PDFs (v2.2), Reference-Library lookup (v2.2, links into the 4317 app). Rule: Rook *renders* other systems; it does not re-implement them. Nothing else gets built as a separate surface for FM once Rook is live.

**Click-through everywhere (P16).** Every panel — item, matter card, option card, dispatch, and voice answers — renders its references as live links, never as quoted paths. Mechanics: `context_refs` rows are tappable; a Dropbox folder or file opens in the Dropbox iOS app via a server-resolved deep link (the server maps team-folder paths to `dropbox.com` links); documents additionally offer an in-app preview streamed over the tailnet from argonaut's local Dropbox mirror — nothing stored on-device, privileged bodies streamed only to cleared roles; Gmail threads open their 8787 mailbox excerpt with an "open in Gmail" jump; calendar entries open iOS Calendar. The importer resolves every path it sees in `board.json`, digests and agent-authored cards into a ref row automatically — links come for free, not by authoring discipline. Acceptance: no panel may name a file, folder or thread without rendering it as a link; a named-but-unresolvable path renders flagged, never silent.

**Non-goals (v2).** Not a document editor; not a CRM; no public exposure; no autonomous sending; no privileged *documents* stored on-device (references + excerpts only, purge on lock); no Android (revisit later); CarPlay deferred (Siri Shortcut "Ask Rook" covers the car).

## 2. Platform decision — native iPhone

**Expo (React Native) with a custom dev client, TypeScript end-to-end.** Reasons, honestly weighed against pure SwiftUI: shared zod schemas and API types with the server (one brain, two runtimes); Cursor productivity is highest in TS; EAS builds + **TestFlight internal distribution** (no App Store review friction for a private app); native modules available where it matters (speech, push, keychain). SwiftUI would feel marginally nicer and remains a licensed future rewrite of the *shell* — the server contract below is UI-agnostic, so nothing is lost by starting in Expo.

- **Distribution:** TestFlight internal testing (FM + 3). Bundle id `capital.citadel.rook`.
- **Push:** **direct APNs from argonaut** (`node-apn`, token-based .p8 auth) — no Expo push gateway, no Firebase, no third-party transit. **Payloads are generic** ("Rook: 2 criticals await" / "Dispatch aged 48h") — never matter names, never privileged content; tapping opens the app, which pulls detail over the tailnet. Channels: critical escalations (T-48/24/3, P4), staged-item nags (P5), freshness alarms (P7), ack/verify events, morning queue summary (07:00, configurable). Redundancy: Telegram mirror via the existing bot (P12).
- **Tailnet on phone:** Tailscale iOS with on-demand VPN. Push arrives regardless of VPN state; content loads once the tunnel is up (automatic on app open).
- **Offline:** SQLite (expo-sqlite) mirror of the visible queue + full offline action queue (decisions, ticks, notes, stages) with `sync_state`, replayed on reconnect (P3).
- **Web companion:** the v1 Next.js screens survive as the laptop view — same API, no extra logic.

## 3. Decision Option Cards — the core interaction (P13)

The universal ruling pattern, everywhere an item needs a decision:

**Structure.** An `OptionCard` belongs to an item and contains **categories** (named groups, e.g. *Funding · Legal · Timing*), each holding **option rows** rendered as a table: `[☐] label · consequence/cost · (note icon)`. Card-level config: `select: single | multi | per-category`, `requires_text: bool`, `allow_custom: bool`. A **free-text field is always present** — "or in your own words" — and a per-row note lets FM qualify any tick ("yes, but capped at…"). Submitting = a `decided` event whose proof captures the exact ticks + text verbatim, and emits the ruling to `_ROOK/decisions/` with the selections as structured YAML *and* prose.

**Authoring.** Three sources: (1) **machine agents** write `_ROOK/cards/ROK-xxx.card.md` — YAML frontmatter defining categories/rows, body giving context (this is exactly the B005 five-option-paper pattern, now machine-renderable); (2) **the assistant** drafts a card from an item's context on request ("give me options on Connal") — grunt-tier model authors it, card is marked `assistant-drafted` and shows its sources; (3) **humans** compose quick cards in-app (add rows, pick category). The daily 07:00 push summarises: "6 cards await ticks."

**Tabular everywhere.** The Queue itself is categorised (matter → lane → severity) with **bulk checkbox mode**: select many, act once (defer/close/supersede) — the month-old "done, drop next sweep" rows die in one gesture.

**Seamlessness bar (acceptance, not aspiration):** open push → card rendered < 2s on tailnet; tick + submit ≤ 3 taps; offline ticks replay losslessly; every tick visible in the Dropbox ledger < 60s after reconnect.

## 3b. The brief, the light, the net, the gag (P17–P20)

**The brief (P17).** Every item carries `brief_md`: two to four sentences in plain language — what the matter is, what has changed, what is being asked, and by when — written by the authoring agent, kept current by sweeps, timestamped. The brief renders at the top of the item panel, inside push→card flows, and is what the voice assistant reads first. A brief whose timestamp trails the item's last event renders **STALE** in amber on its face. The importer refuses no item for lacking one, but an item without a brief is itself flagged — visibly — until an agent or the nightly job writes it.

**The traffic light (P18).** Priority is a derived colour, computed by rules the repo can test — never assigned by an agent's mood:
- **RED** — a decision or release is required and dated: due ≤ 72h, staged > 48h, an escalated critical, a blown gate. RED pushes.
- **AMBER** — needs a human this week: aging without movement, awaiting ack past its window, a conflicting record, a stale brief. AMBER appears in the 07:00 summary.
- **GREEN** — on track or informational. GREEN never pushes.

The light drives sort order, batching and push policy everywhere — Today, Queue, Matters, the watch face of every push. Recolouring is an event like any other: logged, with the rule that fired.

**Nothing missed (P19).** The board's failure to pick up key items is on the record, so coverage becomes machinery, not hope: (1) the **reconciler** — on every ingest, diff the board against lane `CHANGELOG`/`_CONTEXT` records and raise a **candidate item** for anything a lane records that the board lacks (the OD044–OD048 gap would have raised five candidates the same evening); (2) the **nightly net** — a grunt-tier job reads the day's digests, meeting links and mailbox excerpts against the queue and stages anything decision-shaped it cannot match to an item; (3) **coverage monitors** — every source has a freshness clock, and a source that goes quiet is itself an AMBER item; (4) **Caught-late** in Pulse — items whose raised date trails their first appearance in the record, counted and trended. Candidates are cheap to dismiss (one tick) and expensive to miss; dismissals are logged so the net learns.

**Draft discipline (P20).** The speculative-draft habit ends at the protocol layer: agents do not write to the Gmail drafts folder, ever — one doctrine page removes the permission pattern. An outbound message exists in exactly one place before sending: a Rook **staged dispatch**, carrying its provenance — the item it serves, the ruling or explicit request that motivated it, and its author. The `gmail_sa` draft is created at **release time**, on the human tap, never before. A staged draft that ages without release nags once daily, then auto-supersedes after seven days (configurable) instead of accumulating. And rook-syncd sweeps the Gmail drafts folder for **orphans** — drafts it did not create — and flags each for one-tap deletion from the phone; the OH003 class of hazard becomes a queue item instead of a landmine. Rule of the house: **no draft without a ruling behind it.**

## 4. Voice + the models (P14, P15)

**Voice chat ("Ask Rook").** Push-to-talk button on every screen + hands-free session mode + Siri Shortcut. Pipeline: **on-device STT** (iOS speech recognition) → text over the tailnet to the gateway → streamed model reply → **on-device TTS** (AVSpeechSynthesizer), sentence-chunked with barge-in. **Audio never leaves the phone**; only text transits, and only to the tier the matter allows. Voice can: read the queue ("what's critical today?"), open and summarise an item, take an amendment note, draft a dispatch or option card (staged), defer/tick with confirmation ("Tick option two on the Connal card — confirm?" → "Confirm"). Voice **cannot** release dispatches or close criticals — those stay on-glass taps (P6).

**The LLM gateway (server-side, on argonaut; keys in keychain, never in Dropbox, never on the phone):**

| Tier | Model | Used for | Boundary |
|---|---|---|---|
| **Conversation** | **Kimi K3 via OpenRouter** (`moonshotai/kimi-k3`) — the efficient Chinese frontier model the fleet already trusts as "the eyes", with confidentiality gates in standing doctrine; fallback **MiniMax M3** (1M ctx) for very long context Q&A | Voice chat, queue Q&A, item summaries, meeting-transcript triage | **Non-privileged matters only.** Receives sanitised item text + excerpts; never raw privileged docs; "nothing Kimi says is citable" — its answers cite item ids, and load-bearing claims are marked for verification. |
| **Grunt** | **Opus 5** (Anthropic API), detached jobs | Drafting dispatch bodies and option cards from raw context, nightly board synthesis, meeting-link → staged items, long adjudications | Full context allowed incl. privileged (Anthropic already processes the privileged corpus in the existing workflow). Privileged outputs render only to privileged-cleared roles. |
| **Router** | deterministic rules, not a model | privileged→Opus only · voice/chat→Kimi · >200k ctx→MiniMax · draft/author→Opus · cost ledger per call | The gateway writes a **spend ledger** (`_ROOK/ledger/llm.jsonl`: ts, tier, model, tokens, NZD) — the AI spend ledger the audit said doesn't exist, started here. |

**Assistant tool-use** (function-calling against the Rook API): `query_items`, `get_item`, `add_amendment`, `stage_dispatch`, `draft_card`, `defer_item`, `tick_option(confirm)`. Allow-listed, logged as events with `actor: assistant(model)`; anything beyond the list is refused by the server, not the prompt.

## 5. Architecture (v2)

```
 iPhone (native Rook app) ◄─APNs (generic payloads)── rook-syncd ──┐
   │ on-device STT/TTS · offline SQLite · Tailscale on-demand      │
   ▼ tailnet (no public exposure)                                  │
 rook-server (argonaut :8791) ── SQLite + append-only ledger ── SSE/WS
   │            │                                                  │
   │      llm-gateway ──► OpenRouter (Kimi K3 / MiniMax M3)        │
   │            └───────► Anthropic (Opus 5, detached)             │
   ▼                                                               ▼
 rook-syncd  ◄── fs.watch ──  Dropbox team folder  ◄── sweeps · orchestrators · people
                (board.json, digests, cards, acks | _ROOK/ decisions, dispatches, ledger)
```

Unchanged from v1: Dropbox canonical / SQLite operating; two-stage authority migration with a 30-day parallel run; Tailscale identity + six-row device map; reuse of 8787 mailbox context, the Telegram bot and `gmail_sa` drafts; events append-only with the five proof fields; `_ROOK/` file contract for agents (now plus `cards/`).

## 6. Data model — v2 additions

```ts
option_cards { id, item_id fk, title, select/*single|multi|per_category*/, requires_text, allow_custom,
               authored_by/*agent|assistant|human*/, source_ref, state/*open|submitted|superseded*/ }
option_groups{ id, card_id fk, name, sort }          // the categories
option_rows  { id, group_id fk, label, consequence, sort, selected bool, note_md?, custom bool }
card_responses{ id, card_id fk, actor, ts, selections_json, free_text_md, event_id fk }
assistant_log{ id, ts, tier, model, tool_calls_json, tokens_in, tokens_out, cost_nzd, item_refs }
devices      { id, person, apns_token, platform, last_seen, push_prefs_json }
context_refs { +deep_link_url, +kind/*folder|file|thread|event*/, +resolver_state/*resolved|flagged*/ }  // P16
items        { +brief_md, +brief_ts, +light/*red|amber|green*/ derived, +light_reason }        // P17, P18
candidates   { id, source_ref, summary, raised_by/*reconciler|nightly-net*/, state/*open|promoted|dismissed*/, dismiss_reason }  // P19
orphan_drafts{ id, gmail_draft_id, found_ts, state/*flagged|deleted|adopted*/ }                 // P20
```

## 7. Security annex (v2 deltas)

APNs payloads carry zero content beyond counts and generic labels. On-device cache excludes privileged bodies (refs only; Face ID app lock; purge on role change). Gateway keys server-side only. Privileged matters: **never** to OpenRouter, ever — enforced in the router by matter flag, tested in CI with a canary item. The assistant cannot release, send, or widen its own tool list. Voice transcripts are stored as amendments only when explicitly saved. Everything else per v1 (tailnet-only, query-layer scoping, immutable ledger, no secrets in repo).

## 8. Build plan — six phases, runnable gates (~24 days)

- **0 · Steel (d1–2)** — **enrolment check first, before any code**: `scripts/check-enrolment.ts` queries the App Store Connect API and prints PASS/FAIL on three items — Apple Developer Program membership for `capital.citadel` active; an APNs Auth Key (.p8) minted or mintable; TestFlight internal testing available. A FAIL stops with a report naming exactly what is missing and who can fix it — it is never worked around, and CI re-runs the check on every build. Then: monorepo (`apps/mobile` Expo, `apps/server`, `apps/web`, `packages/shared`), schema, tailnet serve, identity, health, APNs hello-world to FM's phone. ✅ Gate: enrolment check passes; generic push arrives with app closed; tap opens app; `/api/health` over tailnet shows identity.
- **1 · Mirror (d2–6)** — importer + ingest; native Today/Queue/Item/Matters read-only; SSE; freshness banner; offline read cache. ✅ Gate: sweep-written red flag on the phone < 60s; airplane-mode reopen still shows the queue; every path in an imported item is tappable and opens Dropbox or the tailnet preview (P16). Every imported item shows a brief and a rule-derived light; a title-only item is impossible to render (P17, P18).
- **2 · Decide (d6–11)** — **Option Cards** end-to-end (agent-authored file → native render → ticks + text → ledger + `_ROOK/decisions/`), decide/defer/amend, quick voice capture, offline action queue, bulk checkbox mode. ✅ Gate: an agent-authored card is ruled on the phone in a lift; the `.md` ruling appears in Dropbox with exact ticks; a sweep reflects it next cycle.
- **3 · Dispatch (d11–15)** — staging, tokened release, agent inbox/ack loop, gmail-draft + Telegram channels, aging nags + T-48/24/3 push escalations. ✅ Gate: test agent acks by file; state flips on the phone; a stale staged item nags exactly once daily. A gmail_sa draft cannot exist before the release tap; a planted orphan draft in the Gmail folder is flagged on the phone within one sweep (P20).
- **4 · Voice + models (d15–20)** — gateway with two tiers + router + spend ledger; push-to-talk and hands-free; assistant tools (query/summarise/note/draft/stage/tick-with-confirm); Siri Shortcut. ✅ Gate: hands-free — "what's critical, open the second one, note this, draft the dispatch" — completed without touching glass; a privileged canary item provably never reaches OpenRouter (CI test); every call priced in the ledger.
- **5 · Prove (d20–24)** — verify flow, Pulse, ledger mirror, cross-alarming watchdogs, role scoping, TestFlight to the team. ✅ Gate: 30-day parallel run starts; killed daemon alarmed < 10 min; **definition of done:** FM clears a real week from the phone, ≥80% of decisions exist in Rook before any sweep infers them, zero staged items silently >72h, and the next Pulse quotes Rook's numbers — including the first real AI spend figures and the first Caught-late count (P19).

## 9. Open items (none block Phase 0)

1. Apple Developer account for `capital.citadel` — status unknown; the Phase 0 enrolment check answers it on day one, and enrolment (if needed) starts the same day. Everything server-side proceeds regardless; only push and TestFlight wait on it.
2. Kimi K3 vs MiniMax M3 as the *default* voice brain — ship Kimi, keep the switch server-side.
3. Whether Zach/Brandon get voice in v2 or v2.1 (default: FM-only first).
4. SwiftUI shell rewrite — revisit only after the parallel run passes.

*Rook v2: tick the box, say the word, and the record keeps itself.*
