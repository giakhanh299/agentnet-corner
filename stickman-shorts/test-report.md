# Test report — stickman-shorts (2026-11-15)

## Environment

- VPS: 4 CPU, ~8 GB RAM, no GPU; Python 3.12.3; ffmpeg/ffprobe 8.1.2.
- Manim Community Edition **0.22.1** in a dedicated venv
  (`stickman-shorts/.venv`, isolated from the video-pipeline venv).
  Deps verified: pycairo 1.29.2, manimpango 0.7.1, numpy 2.5.4.
  System libs already present: libcairo, libpango, libpangocairo
  (no apt install was needed).
- Font: Be Vietnam Pro Regular (132,948 B) + Bold (140,300 B), downloaded
  from github.com/google/fonts (ofl/bevietnampro), verified TrueType,
  installed to `~/.fonts`, confirmed by `fc-list`.

## Rig smoke test — `tests/test_rig.py`: 11/11 PASS

- SPEC frozen (MappingProxyType, assignment raises TypeError).
- Height derives from SPEC: 6.050 units
  (2×HEAD_R + NECK + TORSO + UPPER_LEG + LOWER_LEG).
- Walk pose moves the feet; walk bob in [0, 0.12].
- `place()` puts the hip at the requested point.
- `walk()` / `wave()` change the pose; wave raises right arm
  (shoulder_r = 2.29 rad).
- `lerp_pose` midpoint is the exact average.
- NFC normalize round-trips a true NFD string; `split_text` wraps ≤30 chars.

One test was fixed during the run: the first NFC test built its "NFD"
string by hand and got the decomposition wrong ("ự" is u + horn U+031B +
dot below, NOT u + circumflex). The test now builds NFD with
`unicodedata.normalize("NFD", ...)` and passes. `normalize_text()` itself
was correct all along.

## Demo render — `stickman_demo.py` (5 s, 1080x1920, 30 fps)

- Command: `.venv/bin/manim render -qm --format=mp4 stickman_demo.py StickmanScene`
- **Wall-clock: 17.2 s cold** (first render, incl. font/text caching),
  **8.6 s warm** (re-render after the wave-pose fix, Manim frame cache).
  Far below ChatGPT's 5-10 min VPS estimate for a 45 s video; a 45 s
  video at this rate should render in ~1-3 min on this VPS.
- Output: `media/videos/stickman_demo/1920p30/StickmanScene.mp4`,
  186,679 bytes. ffprobe: **h264, 1080x1920, 30/1 fps, 5.000 s**.
  (The `-qm` flag did NOT override the file-level config — the file's
  `config.pixel_width/height` wins, as intended. The folder is named
  `1920p30`, not `1080p30`.)
- Memory: no OOM; render ran while the video-#1 subagent was working
  in parallel (RAM was ~90% used system-wide at the time).

## Frames viewed (extracted with ffmpeg, inspected visually)

| t | What I saw |
|---|---|
| 0 s | Only the ground line — stickman still off-frame left (walk-in starts off-frame). Correct. |
| 1 s | Stickman mid-stride, left of centre: one leg forward, one back, arms counter-swinging. Head round, face (2 eyes + straight mouth) readable, proportions correct, limbs correct lengths. Back foot near the left edge but not clipped. |
| 2 s | Stickman at centre, feet together on the ground line, slight forward torso lean. Clean. |
| 4 s | Title card **"TÂM SỰ NGƯỜI QUE"** — all diacritics correct (Â, Ự, Ư, Ờ), Bold Be Vietnam Pro, white card + ink border, centred upper third, nothing cut off. Stickman below, smiling, right arm raised in a clear wave. |

### One real bug found and fixed (frame 4 s, first render)

The first wave pose (shoulder_r = π − 0.45) put the elbow INSIDE the
head circle, so the filled head covered the upper arm and the wave read
as a short stub/antenna above the head. Fixed by pointing the upper arm
up-OUTWARD (shoulder_r = π − 0.85, elbow_r = 0.9 + 0.5·sin(phase)) in
both `gestures.py:wave_pose()` and `poses.py:POSE_WAVE`. Re-rendered and
re-checked: the wave is now unambiguous (see frame_4s_v2.png).

## Assemble smoke test — `tools/assemble.py`

- Ran with the demo mp4 + 5 s of digital silence as voice.
- Output: 1080x1920, 30 fps, AAC audio, 5.000 s. The loudnorm filter
  graph ran without error.
- Honest limit: loudnorm measured −inf because the input was silence —
  the −16 LUFS target is verified structurally (filter runs, output is
  valid) but NOT yet verified on a real voice. Re-test with a real
  `voice.wav` before trusting the number.

## What is NOT done / still missing

- No real video has been built from this rig yet (no `videos/<date>_<slug>/`
  episode, no script.yaml, no voice). The demo is the only scene.
- `tools/assemble.py` subtitle burn-in (`--srt`) is untested end-to-end
  (no real .srt was available); the filter string is standard libass.
- Windows path is documented (README + render.bat) but NOT tested on
  the user's PC — the PC is only just being connected via SSH.
- `render_all.sh` is untested (no episodes exist yet).
- The `videos/` folder is empty; `src/assets/audio/` and `images/` are
  empty (no music/SFX library yet — that is a separate gap).
- `media/` render output is gitignored by design (regenerated); the
  `test_frames/` PNGs are inspection artefacts, not part of the repo.
