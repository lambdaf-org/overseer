# shards/ — compressed memory of heavy sources

A shard is what's left of a source after folding: a pointer-dense summary you can read cheaply, with
locators back into `corpus/` so a quote can always be verified against the original. You read shards;
you open the raw file only to check something.

Shards get **shorter and denser** over time, not longer — that's the compression ratchet in
`OVERSEER.md`. The raw file in `corpus/` is the truth; the shard is a disposable index over it. If a
shard and the raw file disagree, the raw file wins and you re-fold.

The shards here are the synthetic **Sam Rivera** seed — `self-profile`, `thesis-brief`, `mara`, `devon` —
each folded from the matching file in `corpus/` and carrying its locators. Replace the corpus with your
own material and re-fold, and these get replaced by shards of your sources.
