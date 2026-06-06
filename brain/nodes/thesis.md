# nodes/thesis — the degree

### proj:thesis · project
is: capstone "Wayfinding for transit anxiety" — an interactive prototype; the degree hinges on it.
links:
  - serves → goal:graduate
  - reviewed-by → person:mara
  - is-portfolio-for → goal:studio-job        # the prototype double-counts beyond the degree
  - overlaps → proj:client-app                # they collide on the same weeks
  - advanced-by → event:2026-05-20-thesis-draft-sent
provenance: shard:thesis-brief → corpus/work/thesis-brief.md "a working interactive prototype"
notes: core flow (route → calm "what to do now" screen) prototyped; the "live disruption" screen has no completion event yet — open work.

### goal:graduate · goal
is: finish the NAD design degree this term.
links:
  - served-by → proj:thesis
  - gated-by → fact:nad-submission
  - depends-on → person:mara
  - threatened-by → proj:client-app
provenance: corpus/self/profile.md "graduating this term is the whole point of right now"
notes: one hard gate — the thesis submission. The open advisor review is the critical path, not the unbuilt screen.

### goal:studio-job · goal
is: land a junior role at a design studio after graduating.
links:
  - needs → proj:thesis                        # the prototype is the portfolio piece
provenance: corpus/self/profile.md "the prototype is the thing I'd show in interviews"
notes: not dated/urgent yet; rides on the thesis prototype being strong.

### person:mara · person
is: thesis advisor (Mara Okafor) — reviews and signs off the capstone.
links:
  - reviews → proj:thesis
  - on-critical-path-for → goal:graduate
  - involved-in → event:2026-05-20-thesis-draft-sent
provenance: corpus/network/mara.txt; shard:mara
notes: has held the draft since 2026-05-20; no comments-received event recorded since — review is open.

### fact:nad-submission · fact
is: NAD requires the final thesis submitted by 2026-06-19, with advisor sign-off.
links:
  - gates → goal:graduate
provenance: web "NAD final-thesis submission rules 2026" (fetched 2026-06-06); corpus/work/thesis-brief.md "Submission deadline: 2026-06-19" agrees.
notes: absolute date stored — compute any days-left from today. Re-verify if older than ~3 months.

### event:2026-05-20-thesis-draft-sent · event
is: Sam sent the thesis draft to Mara for review on 2026-05-20.
links:
  - advances → proj:thesis
  - involves → person:mara
provenance: corpus/network/mara.txt "just sent you the thesis draft"
notes: opened the review cycle; no comments-received event has followed, so the review reads as still open.
