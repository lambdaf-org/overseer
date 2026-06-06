# nodes/freelance — the paid work

### proj:client-app · project
is: freelance build — a booking web app for Devon's studio. Pays the rent.
links:
  - involves → person:devon
  - overlaps → proj:thesis
  - threatens → goal:graduate                  # it competes for the thesis weeks
  - changed-by → event:2026-06-01-client-scope-expanded
provenance: shard:devon → corpus/network/devon.txt
notes: single-slot flow done and in polish; scope grew 2026-06-01 (group bookings) into the thesis weeks.

### person:devon · person
is: freelance client (Devon Ash, "devon_ux") — runs the studio commissioning the booking app.
links:
  - involved-in → proj:client-app
  - involved-in → event:2026-06-01-client-scope-expanded
provenance: corpus/network/devon.txt; shard:devon
notes: asked for an added group-booking flow on 2026-06-01; wants it before end of June, flexible on exact timing.

### event:2026-06-01-client-scope-expanded · event
is: Devon expanded the client-app scope (added group bookings) on 2026-06-01, asking for it before end of June.
links:
  - changes → proj:client-app
  - involves → person:devon
provenance: corpus/network/devon.txt "can we also get group bookings in before end of june?"
notes: pushes client-app load into late 2026-06 — the same weeks as the 2026-06-19 thesis gate.
