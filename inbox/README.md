# inbox/ — new material waiting to be folded

Anything you drop here gets folded into `brain/` on the next "fold" and can then be archived or deleted.
Use it for the steady drip of new stuff: a meeting transcript, a decision you made, a new chat export, a
quick note to your future self.

## The Whisper contract

Whisper (or any speech-to-text tool) is just a **sensor**. Overseer ships no capture code — you point
your own tool here. Have it append lines in this format:

```
2026-06-06 14:03 | me    | decided to push devon's onboarding work to next week so the thesis gets this week
2026-06-06 14:03 | devon | fine with the timing as long as we still hit end of june
```

`YYYY-MM-DD HH:MM | speaker | text`, one utterance per line. That's the whole interface. The point of
capture is that you can't always take notes live — so it just feeds the data; folding turns it into dated
events, nodes, and edges like any other source.

A minimal wiring (if your STT prints transcript lines to stdout):

```bash
your-whisper-tool --stream | while IFS= read -r line; do
  printf '%s | me | %s\n' "$(date '+%Y-%m-%d %H:%M')" "$line" >> inbox/capture-$(date +%F).txt
done
```
