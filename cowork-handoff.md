# FMDC — Cowork Handoff

Hello Claude. You're being dropped into Jake's working directory (`~/FMDC`) to do a large piece of discovery and setup work for his stunt rigging business. Read this whole document before you do anything. Then work through it methodically. At the end, report back.

---

## Who Jake is and what FMDC does

Jake runs **FMDC** — a stunt rigging outfit that does high-line, wire work, descender rigs, fall arrest, and aerial effects for film, television, commercials, and live events. It's a small shop: Jake himself plus a rotating crew of riggers he brings on per job. The work is safety-critical — people get hung off buildings, thrown through windows, dropped from ceilings. Errors are not the kind of errors you recover from.

His world looks like this:

- **Clients** are stunt coordinators, production companies, second-unit directors, commercial producers, and occasionally live-event promoters and theme parks.
- **Jobs** run from half-day commercial gigs to multi-week feature film schedules. Each job has its own paperwork: rigging plans, load calcs, insurance certificates, COIs, permits, risk assessments, crew call sheets, gear manifests, invoices.
- **Gear** is the core asset: ropes, descenders, harnesses, pulleys, steel, soft goods, load cells, motion-control rigs. Everything has a serial number, a load rating, and an inspection history. Some of it is legally required to be inspected on a schedule.
- **Knowledge** is in Jake's head, in a pile of PDFs, in email threads with coordinators, and scattered across Drive. It needs to come out of all of those places and into one navigable system.
- **Regulation** touches everything: OSHA, union rules (IATSE), local permit offices, FAA when drones or elevated work are involved, and whatever the insurance broker demands.

Jake is not a knowledge-worker type. He's a rigger. He doesn't want a complicated system — he wants a brain outside his head that he can actually use on a job site from his phone.

---

## The mission

You have four phases. Do them in order. Don't skip ahead.

### Phase 1 — Connect to Jake's data

You need read access to Jake's Gmail and Google Drive. Do this:

1. Check whether an MCP server for Google Workspace (Gmail + Drive) is already configured: `claude mcp list`.
2. If not, install one. Pick a well-maintained Google Workspace MCP server and configure it via `claude mcp add`. Use read-only scopes where possible (`gmail.readonly`, `drive.readonly`, `drive.metadata.readonly`). Do **not** request send or modify scopes in this session — Jake hasn't authorized those.
3. Trigger the Google OAuth flow. Jake is watching the session and will click through the browser consent once. Tell him clearly what's happening before you trigger it so he knows what to expect.
4. Confirm you can list messages in his inbox and files in his Drive. Don't proceed until this is working.

If you can't get an MCP server working cleanly in a few attempts, stop and ask Jake. Don't burn the whole session on auth.

### Phase 2 — Discovery

Now actually look at the data. The goal is to understand his business, not to read everything — sample intelligently.

**From Gmail, surface:**
- Who emails him most (candidate clients and repeat collaborators)
- Recent job inquiries and how he responded (or didn't)
- Quotes he's sent in the last 12 months — amounts, scope, outcome if you can tell
- Any threads with insurance brokers, permit offices, or equipment vendors
- Unanswered inquiries still in the inbox
- His typical response patterns — how fast, how formal, what he asks for first

**From Drive, surface:**
- Existing rigging plans, load calcs, risk assessments — templates he reuses
- Insurance certificates and their expiration dates
- Any gear inventory he already keeps (spreadsheet, PDF, photos)
- Past invoices and their structure (line items, rates, terms)
- Crew contact lists
- Safety documents, SOPs, anything that looks like institutional knowledge

Keep a running set of notes in `~/FMDC/_discovery/` as you go — one markdown file per category. These are your working notes, not the final vault. Be honest in them: if something looks disorganized, say so. If you can't find something you'd expect (e.g. no gear inventory at all), note that too.

**Do not download or copy files out of Drive.** Work from metadata and content previews. Don't write anything back to Gmail or Drive in this session.

### Phase 3 — Build the Obsidian vault

Inside `~/FMDC`, build this vault structure. Every folder gets an `index.md` that explains what lives there and links to the key notes inside it. Use Obsidian wiki-link syntax (`[[Note Name]]`) for cross-references.

```
~/FMDC/
├── 00_Inbox/              ← new stuff lands here, gets triaged
├── 10_People/
│   ├── Clients/           ← one note per production company, coordinator, producer
│   └── Crew/              ← one note per rigger, with contact + specialties
├── 20_Jobs/
│   ├── Active/            ← currently running
│   ├── Pipeline/          ← quoted, not yet confirmed
│   ├── Archive/           ← completed, organized by year
│   └── _template.md       ← Job note template
├── 30_Gear/
│   ├── Inventory/         ← one note per major piece of gear
│   ├── Inspections/       ← log of inspections due and done
│   └── _template.md       ← Gear note template
├── 40_Knowledge/
│   ├── Techniques/        ← rigging techniques, rigs Jake has built before
│   ├── Regulations/       ← OSHA, IATSE, local permits, FAA
│   ├── Safety/            ← SOPs, risk assessment patterns, near-misses
│   └── Vendors/           ← gear suppliers, fabricators, specialty contacts
├── 50_Templates/
│   ├── Quote.md
│   ├── Rigging_Plan.md
│   ├── Risk_Assessment.md
│   ├── COI_Request.md
│   └── First_Response.md  ← the email he sends to a new inquiry
├── 60_Admin/
│   ├── Insurance/         ← notes on policies + expiration dates
│   ├── Business/          ← licenses, entity docs, tax notes
│   └── Rates/             ← day rates, gear rental, overtime
└── _discovery/            ← your Phase 2 working notes; leave them in place
```

Populate what you can from the discovery phase. If Jake has ten repeat clients in his inbox, create ten client notes. If you can identify five active jobs from recent Drive files, create the job notes. **Don't fabricate.** Empty is fine — a stub note that says "To be filled in" is better than made-up data. Especially for gear, insurance expirations, and anything safety-adjacent: only record what you can verify from his actual data.

Every note Jake cares about (clients, jobs, gear) should have frontmatter with consistent properties so Obsidian's Properties view and Dataview will work later. Example for a job:

```yaml
---
type: job
client: "[[Production Company Name]]"
coordinator: "[[Jane Smith]]"
status: pipeline       # pipeline | active | completed | lost
start_date: 2025-??-??
end_date:
location:
day_rate:
crew_size:
gear_needed: []
permits_needed: []
insurance_required:
---
```

Pick sensible defaults for the other note types. Keep the schemas simple — Jake will actually fill them in with his thumbs on his phone.

### Phase 4 — Intake pipeline

This is the piece Jake will actually use day one. When a new inquiry lands in his email, this is what should happen:

1. He forwards the email (or tells Claude about it) to the intake pipeline.
2. A new note gets created in `00_Inbox/` with a consistent name like `2026-04-11 — Inquiry from [Client].md`.
3. The note gets pre-filled: client name, project type guessed from the email, dates mentioned, any budget signal, scope signal, urgency signal.
4. A triage checklist sits at the top: *confirmed client identity? / dates feasible? / scope within capability? / budget in range? / insurance sufficient? / crew available?*
5. A suggested first-response draft gets written into the note, based on his existing voice as seen in his real past responses in Gmail.
6. If the inquiry turns into a quote, the note moves to `20_Jobs/Pipeline/`.

Build this as a script or set of notes + a CLAUDE.md instruction block in `~/FMDC/CLAUDE.md` that tells future Claude sessions how to run the intake. Jake's actual interaction with this should be: open a Claude session in `~/FMDC`, paste an email or forwarded text, and watch it get processed into a triaged note. No custom servers, no hosted automation. Just files and Claude.

Write `~/FMDC/CLAUDE.md` as the persistent briefing for future sessions — what this vault is, how it's organized, what the intake pipeline does, what the templates are, and what Claude should *not* do (touch gear inspection data without verification, send emails, make up clients, change insurance records, offer rigging or safety advice Jake didn't ask for).

---

## Boundaries — read carefully

- **Read-only on Gmail and Drive this session.** Do not send emails, do not create or modify Drive files, do not reply on his behalf.
- **No safety claims.** You are not qualified to design rigging, calculate loads, approve gear, or assess whether a stunt is safe. If you record information about techniques or gear, you're cataloging what Jake already knows, not inventing it. Any safety-adjacent note must make clear it reflects his existing materials, not your judgment.
- **No fabricated inventory.** If you can't confirm a piece of gear exists, don't put it in the gear folder. An empty inventory is fine and honest.
- **No fabricated clients or jobs.** Same rule.
- **Respect confidentiality.** You'll see client names, project details, possibly unreleased film titles. Those go in the vault (which lives only on Jake's machine), never in any external tool, never in a commit message, never echoed back to a third party.
- **Commit your work in small, reviewable chunks** as you build the vault. Separate commits for: MCP setup, discovery notes, vault scaffolding, intake pipeline, CLAUDE.md. Don't push anywhere — this stays local until Jake decides otherwise.
- **If you're not sure, stop and ask Jake.** He's at the keyboard.

---

## The report

When you're done, print a summary to the terminal with these sections:

1. **What I connected to** — MCP servers installed, scopes granted, what worked and what didn't.
2. **What I built** — vault structure overview, counts (clients, jobs, gear items, templates), path to the vault.
3. **How the intake pipeline works** — one paragraph, then the exact command or paste Jake uses to run it.
4. **The top 5 things I learned about FMDC.** This is the important one. Real observations pulled from his actual data, not generic business advice. Examples of the *kind* of thing that qualifies:
   - "You have 14 unanswered inquiries in your inbox older than two weeks, six of them with budget signals above $X."
   - "Your three biggest repeat clients are A, B, and C — together they account for roughly half of your identifiable job correspondence in the last year."
   - "Your insurance COI on file expires in 37 days."
   - "You've quoted [Company] four times in 18 months and haven't won a job — worth a direct conversation."
   - "There's no gear inventory anywhere in Drive — this is the biggest gap in the vault and the thing most worth fixing next."
   - Something actually surprising about how he runs the shop.
   Be specific. Cite the evidence. If a finding would be useful but you can't back it up from his data, don't include it.
5. **What I didn't do and why** — anything you skipped, couldn't access, or consciously left for Jake.
6. **Next session suggestion** — one concrete thing for the next time Jake opens Claude in this directory.

Keep the report tight. Jake will read it on his phone.

---

Begin with Phase 1. Tell Jake what you're about to do before you trigger the Google auth prompt.
