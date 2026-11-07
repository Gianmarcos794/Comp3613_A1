# student-judge competency report

**Judged at:** 2026-10-12T18:25Z
**Evidence pass:** re-read docs/transcripts/01–09 (Claude Code sessions, Phases 1–6) + current docs/report.md, docs/diagrams/, docs/wireframes/, app/routers/ (prior judge.md ignored; none existed)

**Student / session:** Gian Suarez Nápoles (816042658), Internship Platform
**Artifact:** Guide chats for this project, written as `docs/transcripts/*.md` (Claude Code, VS Code)
**Phases in evidence:** 1–6 (COMP 3613; Phase 5 polish, Phase 6 deploy; never generic 0–5)

### Totals
| | Count / value |
|--|--|
| Metrics on rubric | 12 (M1–M12) |
| N/A (excluded) | 0 |
| Metrics scored | 12 |
| Scoreable max | 48 |
| Awarded total | 40 / 48 |
| **Overall (avg of scored)** | **3.3 / 4** |
| Impression mark | 17 / 20 (no single Guide confidence logged; round(3.33 / 4 × 20)) |

## Scorecard

| ID | Metric | Score / 4 | In avg | Evidence |
|----|--------|----------:|:------:|----------|
| M1 | Phase discipline | 3 | yes | One design phase per chat (02–05), no app code before the wireframe covered every use case, Phase 5 built one workflow at a time with a polish pass before Phase 6. Later scope edits were made by going back to the Phase 2/3 chats. |
| M2 | Problem framing | 4 | yes | Framed the domain in their own words: "in this design the student does not apply to a specific internship, they apply and the system after review their application if accepted matches them with internships"; added "view application status" when asked how students learn the outcome; companies are created by the admin "so only trusted companies can post internships". |
| M3 | Decision ownership | 4 | yes | Named every entity and property themselves (Phase 3 list), owned relationship and rule choices ("an application can only have one active match at a time"), and cut scope deliberately: "admins match is final", then "change to one to one, the company should be able to see its matched students, but as part of publish/manage". |
| M4 | Artefact-before-code | 3 | yes | Wireframe updated to cover the missing Create Company Account and Reject paths before any code ("check now"). Phase 4 model edits applied ("apply the 3"). Phase 5 built from the ERD and wireframe with no substitute design. |
| M5 | Verification habit | 2 | yes | Ran each workflow and reported real failures (pasted ASGI traceback; "the dshboard is empty"), but most verify notes are bare confirmations — "they work", "done go to the next one" — with no observed-vs-wireframe detail; Guide had to flag this. Live deploy checked: "the 3 workflows work". |
| M6 | Assignment fit | 3 | yes | Layered build: thin routes call services (no `select`/`db.exec` in `app/routers/`), rules in services (matched-lock, deadline exclusion, `.edu` sign-up, GPA cap), starter auth and seed reused, themed (navy + emerald, Inter, InternSearch), deployed on Render. |
| M7 | Slice explanation | 3 | yes | Completed SQLModel and thin-route snippets for every workflow (code-check blocks, `architecture_ok: yes`); picked the Service layer for the matched-lock rule; one route snippet was `passed: partial` (missing success redirect) and fixed on the second pass. |
| M8 | Prompt quality | 3 | yes | Phase-tagged openers, entity list in the requested shape, short steering after artefacts existed ("start with the submit aplication", "try emerald instead"). Phase 1 workflows were not in `Feature (user)` format at first and were tidied by Guide. |
| M9 | Response to pushback | 3 | yes | Fixed the partial route snippet, iterated the theme (teal → gold → emerald), answered every Phase 4 gap question, and took on all four polish items, supplying the `.edu` and 4.3 values. Polish items were Guide-proposed rather than self-found. |
| M10 | Integrity | 4 | yes | No suspicion spiral, no paste-back or "just apply this"; `python manage.py skills-verify` → "Skill integrity: pass". |
| M11 | Provenance continuity | 4 | yes | The general-pool and admin-final-match decisions from Phase 2 flow unchanged through the ERD (Application to Match one-to-one, unique `student_id`), the wireframe and the shipped services. |
| M12 | Sincerity trajectory | 4 | yes | No sincerity blocks were needed in any chat; suspicion never opened. |

## Strengths
- Strong Phase 2 ownership: include (Check Requirements), conditional extends, and a new View Application Status use case all came from the student's own descriptions of the flow.
- Student-named entities and properties, with clear relationship and business-rule answers; scope later simplified on purpose (admin match is final) and the model updated to match.
- Wireframe revised to close real coverage gaps (Create Company Account, Reject) before any code.
- Every workflow has student-completed model and thin-route snippets that respect the layers, and no router does persistence inline.
- Full Phase 6: Render Postgres + web service, live URL and all three marker logins in the report, workflows confirmed on the live site.

## Gaps (priority order)
1. **Verify notes are thin.** Most Phase 5 confirmations are "they work" / "done" with no comparison against the wireframe; the polish list came from Guide rather than from mismatches the student found.
2. **Deploy care.** After the one-off database reset, the start command was left without `--no-drop` until Guide flagged it; it is fixed now, but it would have wiped data on every wake.

## Phase gate status
| Phase | Status | Note |
|-------|--------|------|
| 1 | met | Internship Platform; workflows named by the student (now three after a deliberate cut) |
| 2 | met | Use-case PNG with include/extend from student answers; revised after "admins match is final" |
| 3 | met | Student-named entities; ERD with student-chosen relationships and rules |
| 4 | met | Wireframe covers all use cases after one update; model edits applied |
| 5 | met | Theme applied, three workflows plus Create Company Account built and verified, polish pass 1 applied |
| 6 | met | https://faststarter-07fs.onrender.com live on Render Postgres; bob, admin, comp1 logins in report |

## Recommended next practice
- For one workflow, write a verify note that walks the wireframe screen by screen ("expected X, saw Y") and names at least one mismatch you would change yourself, before asking for the next step.

## Integrity note
- Clean
## Provenance flags
- None
## Sincerity log summary
- Blocks found: 0 | max round: 0 | min/mean/final confidence: n/a | trend: n/a | cleared: n/a (never entered)
## Skips
- Skips: 0/3 used.
