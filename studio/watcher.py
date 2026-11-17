"""Watch creator channels for new video uploads and automatically create clips."""
import logging
import re
import threading
import time
from urllib.parse import urlparse

import yt_dlp

from . import alerts, auth, config, creators, ctx, jobs, media

log = logging.getLogger("studio.watcher")


class _QuietLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    if not url:
        return ""
    m = re.search(r"(?:v=|\/embed\/|\/shorts\/|youtu\.be\/|watch\?.*v=)([0-9A-Za-z_-]{11})", str(url))
    if m:
        return m.group(1)
    m2 = re.search(r"([0-9A-Za-z_-]{11})", str(url))
    return m2.group(1) if m2 else ""


def normalize_videos_url(url: str) -> str:
    """Normalize a channel link to its uploads / videos feed URL."""
    clean = re.sub(r"[?#].*$", "", str(url or "").strip()).rstrip("/")
    if not clean:
        return ""
    if not re.match(r"^https?://", clean):
        clean = "https://" + clean
    if "youtube.com" in clean or "youtu.be" in clean:
        if not clean.endswith("/videos"):
            clean += "/videos"
    return clean


def fetch_recent_videos(channel_url: str, limit: int = 5) -> list:
    """Fetch recent video uploads from a channel without downloading."""
    vurl = normalize_videos_url(channel_url)
    if not vurl:
        return []
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlistend": limit,
        "logger": _QuietLogger(),
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(vurl, download=False)
            entries = info.get("entries") or []
            results = []
            for e in entries:
                if not e:
                    continue
                vid = str(e.get("id") or "").strip()
                title = str(e.get("title") or "").strip()
                duration = float(e.get("duration") or 0)
                if vid:
                    results.append({
                        "id": vid,
                        "title": title or f"Video {vid}",
                        "duration": duration,
                        "url": f"https://www.youtube.com/watch?v={vid}",
                    })
            return results
    except Exception as e:
        log.warning("Failed to fetch uploads for %s: %s", vurl, e)
        return []


def check_creator_uploads(cid: str, force_clip_latest: bool = False) -> list:
    """Check for new long video uploads for this creator. Enqueue clipping jobs for new videos."""
    c = creators.get(cid)
    if not c:
        return []
    # Channel URL: primary channel or youtube platform channel
    channel_url = c.get("channel") or (c.get("channels") or {}).get("youtube")
    if not channel_url:
        return []

    min_duration = int(c.get("min_upload_duration") or 300)   # default 5 minutes
    clip_count = int(c.get("auto_clip_count") or 10)         # default 10 clips

    videos = fetch_recent_videos(channel_url, limit=6)
    if not videos:
        return []

    # Filter by minimum duration to ignore YouTube Shorts and short teasers
    long_videos = [v for v in videos if v["duration"] >= min_duration or v["duration"] == 0]

    seen = set(c.get("seen_upload_ids") or [])

    # Also check existing jobs for this user so we never duplicate
    try:
        for j in jobs.all_jobs():
            vid = extract_video_id((j.get("source") or {}).get("url", ""))
            if vid:
                seen.add(vid)
    except Exception:
        pass

    # First-time seed check: don't download backlog unless forced
    has_seen = bool(c.get("seen_upload_ids"))
    if not has_seen:
        all_ids = [v["id"] for v in videos]
        if not force_clip_latest:
            creators.seed_seen_uploads(cid, all_ids)
            creators.log(cid, f"Auto-clipping armed: tracking future uploads (seeded {len(all_ids)} existing videos)")
            return []
        else:
            # Seed everything except the top video
            other_ids = [v["id"] for v in videos[1:]]
            creators.seed_seen_uploads(cid, other_ids)

    queued_jobs = []
    for v in long_videos:
        if v["id"] in seen:
            continue
        try:
            job = jobs.create(
                source={"type": "url", "url": v["url"], "name": v["title"]},
                options={"max_clips": clip_count, "quality": 1080},
                creator=c["id"],
            )
            creators.mark_seen_upload(c["id"], v["id"])
            seen.add(v["id"])
            creators.log(c["id"], f"New upload detected: '{v['title']}'. Auto-clipping {clip_count} clips.")
            alerts.notify(f"New video from {c['name']}: '{v['title']}'. Making {clip_count} clips automatically.")
            queued_jobs.append(job)
        except Exception as e:
            creators.log(c["id"], f"Failed to auto-clip upload '{v['title']}': {str(e)[-150:]}")

    return queued_jobs


def check_user_creators(uid: str):
    """Check all creators belonging to a specific user who have auto_clip_uploads enabled."""
    with ctx.as_user(uid):
        try:
            active_creators = [
                c for c in creators.all_creators()
                if c.get("auto_clip_uploads") and (c.get("channel") or (c.get("channels") or {}).get("youtube"))
            ]
        except Exception:
            return
        for c in active_creators:
            try:
                check_creator_uploads(c["id"], force_clip_latest=False)
            except Exception as e:
                log.warning("Upload check error for creator %s: %s", c.get("id"), e)


def watch_uploads_loop():
    """Background worker that periodically checks creators for new long video uploads."""
    time.sleep(25)
    while True:
        t0 = time.time()
        try:
            for uid in auth.user_ids():
                check_user_creators(uid)
        except Exception as e:
            log.warning("watch_uploads_loop error: %s", e)
        elapsed = time.time() - t0
        time.sleep(max(30, 180 - elapsed))


def start():
    """Start the upload watcher background thread."""
    threading.Thread(target=watch_uploads_loop, daemon=True, name="upload-watcher").start()
