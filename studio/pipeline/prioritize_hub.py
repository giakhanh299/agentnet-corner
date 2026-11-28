"""Smart Hub queue prioritizer (runs every daemon tick):
1) Auto-cancel stray QUEUED muse_make_videos tasks for movies that ALREADY have a finished final render on E:.
2) Finish-closest-first for muse_make_videos: movies that ALREADY have real AI clips on disk (`clips > 0`, not yet rendered)
   are ALWAYS pinned at the very front (`created_at = 100..900`, highest clip count first!) so animators finish 1 full
   6-8 min movie completely (38/38) before spreading thin across 70+ movies.
3) Remaining muse_make_videos: Phim Ma (ep*) -> Kiếm Hiệp (kh*) -> Tập Làm Content (v0*) -> Tiền Và Đời SRT (k1_srt_*).
4) muse_draw_images: Phim Ma -> Kiếm Hiệp -> Tập Làm Content -> Tiền Và Đời SRT.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, r"D:\0.1_FACE_BOOK\macro-tool")
from vps_ssh_helper import connect_vps_ssh

STUDIO_ROOT = pathlib.Path(r"E:\MUSE_MEDIA_STUDIO")


def scan_local_progress() -> tuple[dict[str, int], set[str]]:
    clip_counts: dict[str, int] = {}
    final_done: set[str] = set()
    if not STUDIO_ROOT.exists():
        return clip_counts, final_done

    # Check both channel/<slug> and direct <slug>
    candidates: list[pathlib.Path] = []
    for ch in STUDIO_ROOT.iterdir():
        if not ch.is_dir() or ch.name.startswith("_"):
            continue
        if (ch / "episode.json").exists():
            candidates.append(ch)
        else:
            for ep in ch.iterdir():
                if ep.is_dir() and not ep.name.startswith("_"):
                    candidates.append(ep)

    # Also check rendered outputs on E: (E:\MUSE_MEDIA_STUDIO\final, _OUTPUT, final_renders, renders)
    final_mp4_stems: set[str] = set()
    for out_dir in [
        STUDIO_ROOT / "final",
        STUDIO_ROOT / "_OUTPUT",
        STUDIO_ROOT / "final_renders",
        STUDIO_ROOT / "renders",
    ]:
        if out_dir.exists():
            for f in out_dir.rglob("*.mp4"):
                final_mp4_stems.add(f.stem.lower())

    for ep in candidates:
        slug = ep.name
        mp4s = list(ep.rglob("scene_*.mp4"))
        clip_counts[slug] = len(mp4s)
        has_local_final = (
            (ep / "03_final_v2" / f"{slug}.mp4").is_file()
            or (ep / "03_final_v2" / "qc_report_v2.json").is_file()
            or any(
                f.name.startswith("final_") or f.name.startswith("phim_ma_") or f.name.startswith("kiem_hiep_")
                for f in ep.glob("*.mp4")
            )
        )
        if has_local_final or any(slug.lower() in stem for stem in final_mp4_stems):
            final_done.add(slug)

    return clip_counts, final_done


def main() -> int:
    clip_counts, final_done = scan_local_progress()
    # Only send slugs with clips > 0 or already finalized to keep payload tiny
    active_clips = {k: v for k, v in clip_counts.items() if v > 0 and k not in final_done}
    data_json = json.dumps({"active_clips": active_clips, "final_done": sorted(final_done)}, ensure_ascii=False)

    remote = f"""
import json, sqlite3

info = json.loads({data_json!r})
active_clips = info['active_clips']
final_done = set(info['final_done'])

con = sqlite3.connect('/opt/agentnet-corner/state/research.sqlite3')
rows = con.execute("SELECT id, kind, dedup, payload FROM tasks WHERE status='QUEUED'").fetchall()

def _slug_sort_key(row):
    tid, kind, dedup, pay = row
    d = dedup or ''
    # Extract slug after second '-' for musevid6-sXX_YY-<slug> so all batches of the same movie stay consecutive!
    parts = d.split('-', 2)
    slug = parts[2] if len(parts) == 3 else d
    return (slug, d, tid)

rows.sort(key=_slug_sort_key)

canceled = 0
for i, (tid, kind, dedup, pay) in enumerate(rows):
    hay = (dedup or '') + ' ' + (pay or '')
    if kind == 'muse_make_videos':
        # Auto-cancel stray queued tasks for movies that are ALREADY finalized on E:
        matched_done = next((s for s in final_done if s in hay), None)
        if matched_done:
            con.execute("UPDATE tasks SET status='CANCELED' WHERE id=?", (tid,))
            canceled += 1
            continue

        # Finish-closest-first: 4-Act movies (ep*/kh*) with real AI clips go FIRST (100..500),
        # then short channels (v0*/k1_srt_*) with real AI clips (600..900)
        matched_slug = next((s for s in active_clips if s in hay), None)
        if matched_slug is not None:
            clips = int(active_clips[matched_slug])
            is_4act = matched_slug.startswith(("ep", "kh"))
            tier_base = 100.0 if is_4act else 600.0
            base = tier_base + max(0, 40 - clips) * 10.0
            con.execute('UPDATE tasks SET created_at = ? WHERE id = ?', (base + (i * 0.001), tid))
            continue

        if 'ep' in (dedup or '') or '[ep' in pay:
            base = 1000.0
        elif 'kh' in (dedup or '') or '[kh' in pay:
            base = 1500.0
        elif 'v0' in (dedup or '') or '[v0' in pay:
            base = 2000.0
        elif 'k1_srt_' in hay:
            base = 2500.0
        else:
            base = 3000.0
        con.execute('UPDATE tasks SET created_at = ? WHERE id = ?', (base + i * 0.01, tid))
    elif kind == 'muse_draw_images':
        if 'ep' in (dedup or '') or '[ep' in pay:
            base = 5000.0
        elif 'kh' in (dedup or '') or '[kh' in pay:
            base = 5500.0
        elif 'v0' in (dedup or '') or '[v0' in pay:
            base = 6000.0
        else:
            base = 6500.0
        con.execute('UPDATE tasks SET created_at = ? WHERE id = ?', (base + i * 0.01, tid))

con.commit()
q = con.execute("SELECT kind, status, COUNT(*) FROM tasks WHERE kind IN ('muse_draw_images','muse_make_videos') GROUP BY kind, status").fetchall()
top5 = con.execute("SELECT dedup, round(created_at, 3) FROM tasks WHERE kind='muse_make_videos' AND status='QUEUED' ORDER BY created_at ASC LIMIT 6").fetchall()
print('HUB_QUEUE_NOW:', q)
print('AUTO_CANCELED_FINALIZED:', canceled)
print('TOP6_ANIMATOR:', top5)
"""

    ssh = connect_vps_ssh(timeout=20)
    try:
        inp, o, e = ssh.exec_command("python3 -")
        inp.write(remote)
        inp.flush()
        inp.channel.shutdown_write()
        print(o.read().decode("utf-8", "replace").strip())
        err = e.read().decode("utf-8", "replace").strip()
        if err:
            print("ERR:", err)
    finally:
        ssh.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
