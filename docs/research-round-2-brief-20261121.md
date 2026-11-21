# Research round 2 — brief (draft, not posted)

**Prepared:** 2026-11-21 ~08:30 +07, by Torque (controller).
**Status:** DRAFT — no task has been posted to the AgentNet queue, no approval
requested yet. This brief exists so the round can launch the moment the user
says "go" (or picks niches). One decision still belongs to the user: launch
round 2, or hold.

## Why now

- The topic bank is fully exhausted. The 30-video bank (30/30 used) and all
  9 fresh week-1 topics (9/9 used) are spent: v048–v049 used the last two
  fresh topics (AI tools, budget teardown) and are in git (commit b23206a,
  2026-11-20 08:54 UTC).
- 35 scripts are waiting for production (v015–v049). Week 2 (23–29/11)
  production is covered from those — research round 2 runs in parallel and
  does not block Week 2. Production itself is still blocked on PC access
  (other_tcp), which is a separate pending decision.
- At the current pace (3 scripts per batch, ~2 batches a day when writing),
  the 35 waiting scripts cover roughly the next 10–12 production batches.
  Round 2 takes days (round 1: 100 candidates 14/11 → selection 15/11 →
  deep analysis 15/11), so starting the decision now avoids a gap later.

## Scope (same shape as round 1, V1.0 mission)

1. **Research:** ~100 candidate short vertical videos (YouTube Shorts +
   TikTok), scored, then a **selection of 30** for deep analysis + 10
   reserves. Dedupe against the round-1 selection
   (`docs/selection-30-20261115.csv`) — no video already in the 30 may
   return as a "new" candidate.
2. **Verify:** independent verification of the 100-list and the 30-selection
   before any approval is asked (same as round 1: b4413e82 pattern).
3. **Deep analysis:** 6 layers per video for the 30 (hook, format,
   retention, audio, producibility, remake note), starting with the 85+
   group — only after the selection is approved.

## Lessons from round 1 to bake into the task text

- **Facebook Reels: do not require them.** Round 1 got 0/100 Reels —
  Reels are effectively unindexed/blocked for scraping. Ask for Shorts +
  TikTok only.
- **Verify counts inside the task.** Round 1's summary said 58 known
  channels while its limitations said 56 unknown (42/100 actually unknown
  on re-check); only 22/100 had a known duration. Require the Research
  node to state, per video: URL, duration (or "unknown"), channel (or
  "unknown"), spoken language — and require Verify to recount.
- **No-camera filter up front.** Exclude real-person vlogs that cannot be
  remade faceless (round 1: #37 Hindi festival vlog, 40 pts, dropped).
  Big-production work (e.g. MrBeast) is hook/retention reference only,
  never a production template.
- **Record spoken language per video.** #77 speaks Urdu, not English;
  Whisper Base fails on Hindi — deep analysis must note language so the
  remake brief is not written against a misheard hook.
- **No reuse of others' clips/audio/images in remakes.** 15/25 of the
  deep-analysed round-1 videos reuse third-party assets; remakes must use
  own assets. Note any © watermark (round 1: #50 carries one).
- **No playback claim without watching.** Round 1 watched no video in
  full; only 6 TikTok pages were verified directly. The task must state
  what was actually watched vs. inferred from frames/metadata.

## Suggested niches (to confirm or replace)

Round 1's bank leaned humour 8 / curiosity 7 / surprise 6 / emotional 5 /
everyday 4. Round 2 should weight fresh ground over repeats of the same
30 topics: everyday science, money/budget, animals, food, "how it works",
and plot-twist POV — and explicitly exclude the 30 round-1 topics
(the 35 scripts v015–v049 already cover them).

## What the user decides

- **Go / hold** — and, if go, whether to keep the niche mix above or name
  niches. No queue post, no Chief claim, no approval step is taken here.
- This brief is the launch spec: on "go", post it as the Research task
  (project=research, API 8110, research-only queue) and a Verify task
  after submission, exactly as round 1 ran.

## Files

- Round-1 selection: `docs/selection-30-20261115.md` / `.csv`
- Round-1 deep analysis: `docs/deep-analysis-5x85-20261115.md`,
  `docs/deep-analysis-25-20261115.md`
- Production framework (8 formulas): `docs/production-framework-20261115.md`
- Latest scripts: `video_production/scripts-batch-20261116/scripts-batch-v048-v049-20261120.md`
