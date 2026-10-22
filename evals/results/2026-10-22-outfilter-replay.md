# OUTPUT_FILTER old vs new overlap rule, replayed on recorded answers, 2026-10-22

Question: did the F4 fix (ignore 30-character runs that a retrieved public chunk
also contains, commit 036b1d5) let through anything the old rule would have
withheld, other than q33?

Method: for every answer of the `outfilter` configuration that was not withheld
and was given to a `public` caller (accuracy and red team), re-run retrieval for
the same question and role (fastembed, top-k 5; the retrieved sources were
asserted equal to the recorded ones), then apply both rules to the recorded
answer:

- old: canary marker, or a 30-character run shared with an `interne` chunk;
- new: `guards.should_filter(answer, "public", internal_chunks, public_chunks)`.

Answers the filter replaced are not replayable (their text is not recorded).

| run | unfiltered public answers replayed | old and new disagree |
|---|---:|---|
| 2026-10-20 (old rule live) | 71 | none |
| 2026-10-22 (new rule live) | 75 | q33 only (old: withhold, new: pass) |
