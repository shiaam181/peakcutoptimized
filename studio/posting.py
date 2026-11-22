"""Post queue: decides when each finished clip goes to which account, posts it, and tracks views."""
import json
import re
import secrets
import threading
import time
from pathlib import Path

from . import accounts, alerts, config, creators, ctx, jobs, live

_lock = threading.RLock()
_FILE = config.DATA_DIR / "posts.json"
try:
    _posts: list = json.loads(_FILE.read_text(encoding="utf-8")) if _FILE.exists() else []
except ValueError:
    _posts = []


def _mine() -> list:
    u = ctx.uid()
    return [p for p in _posts if p.get("user") == u]
OPEN = ("scheduled", "posting")


def _save():
    with _lock:
        tmp = _FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(_posts, indent=1), encoding="utf-8")
        tmp.replace(_FILE)


def _day(t):
    return time.strftime("%Y-%m-%d", time.localtime(t))


def _mirror(p):
    """Copy the post's state onto its clip so the clip card can show it."""
    job = jobs.get(p["job"])
    clip = next((c for c in job["clips"] if c["id"] == p["clip"]), None) if job else None
    if clip is not None:
        clip.setdefault("posts", {})[p["id"]] = {k: p.get(k) for k in ("account_name", "platform", "status", "url", "due_at", "error")}
        jobs.save(job)


def _next_slot(account_id, gap_min, cap, min_initial_delay_sec=0):
    """Earliest time that respects the gap between posts and the daily cap for this account."""
    mine = [p for p in _mine() if p["account"] == account_id and p["status"] in OPEN + ("posted",)]
    earliest = time.time() + min_initial_delay_sec
    last_post = max((p.get("posted_at") or p["due_at"] for p in mine), default=0)
    t = max(earliest, last_post + gap_min * 60)
    if cap and cap < 9000:
        for _ in range(30):
            if sum(1 for p in mine if _day(p.get("posted_at") or p["due_at"]) == _day(t)) < cap:
                break
            lt = time.localtime(t + 86400)
            t = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, 9, 0, 0, 0, 0, -1))  # 9:00 next day
    return t


def enqueue(job, clip, account_ids, now=False) -> list:
    c = creators.get(job["creator"]) or creators.DEFAULTS
    made = []
    gap_min = max(15, int(c.get("post_gap_min", 45)))
    with _lock:
        for i, aid in enumerate(account_ids):
            acc = accounts.get(aid)
            if not acc:
                continue
            if any(p["job"] == job["id"] and p["clip"] == clip["id"] and p["account"] == aid
                   and p["status"] in OPEN + ("posted",) for p in _mine()):
                continue  # never post the same clip to the same account twice
            if now:
                due = time.time()
            else:
                # Stagger across different connected accounts so all platforms are not blasted at the exact same minute.
                # Auto-posted live stream clips start with a buffer (e.g. 15 min), and each account in the set is staggered by 15 min.
                stagger_sec = i * 900
                initial_delay = 900 + stagger_sec
                due = _next_slot(aid, gap_min, c.get("daily_cap", 9999), min_initial_delay_sec=initial_delay)
            p = {"id": secrets.token_hex(8), "user": ctx.uid(), "job": job["id"], "clip": clip["id"], "creator": job["creator"],
                 "account": aid, "account_name": acc["name"], "platform": acc["platform"], "status": "scheduled",
                 "due_at": due, "created": time.time(), "title": clip.get("title") or clip.get("hook") or "Clip",
                 "score": clip.get("score", 0), "tries": 0, "url": "", "remote_id": "", "error": None, "views": None}
            _posts.append(p)
            made.append(p)
        _save()
    for p in made:
        _mirror(p)
    return made


def on_clip_ready(job, clip):
    """Called once when a clip first finishes rendering."""
    c = creators.get(job["creator"])
    if not c or not c.get("autopost"):
        return
    accs = c.get("accounts")
    if not accs:
        try:
            accs = [a["id"] for a in accounts.list_accounts()]
        except Exception:
            accs = []
    if not accs:
        return
    if clip.get("score", 0) < c.get("post_min_score", 85):
        return  # includes hand-made clips (score 0): those wait for you to press Post
    made = enqueue(job, clip, accs, now=True)
    if made:
        creators.log(c["id"], f"Queued for {len(made)} account(s): {clip.get('title') or clip.get('hook')}")


def _caption(clip, creator, platform=""):
    footer = (creator.get("post_footer") or "").strip()
    if clip.get("fixed_description") or clip.get("hashtags_in_description"):
        return "\n\n".join(x for x in (clip.get("description", ""), footer) if x)
    if platform == "youtube":
        desc = re.sub(r'#\S+', '', (clip.get("description") or "")).strip()
        desc = re.sub(r'\s{2,}', ' ', desc).strip()
        return "\n\n".join(x for x in (desc, footer) if x)
    tags = " ".join("#" + str(h).lstrip("#") for h in clip.get("hashtags", []))
    return "\n\n".join(x for x in (clip.get("description", ""), tags, footer) if x)


def _post(p):
    job = jobs.get(p["job"])
    clip = next((c for c in job["clips"] if c["id"] == p["clip"]), None) if job else None
    acc = accounts.get(p["account"])
    try:
        if not clip or clip.get("status") != "done":
            raise RuntimeError("The clip no longer exists or is not finished.")
        if not acc:
            raise RuntimeError("That account was disconnected.")
        path = Path(job["dir"]) / "clips" / clip["file"]
        creator = creators.get(job["creator"]) or dict(creators.DEFAULTS, name="clips")
        platform = acc.get("platform", "")
        title = clip.get("title") or clip.get("hook") or "Clip"
        if platform == "youtube" and "#Shorts" not in title and "#shorts" not in title:
            title = f"{title[:88]} #Shorts".strip()
        cap = _caption(clip, creator, platform)
        if acc.get("zernio_account_id") or (accounts._user_zernio_key() and not acc.get("token") and not acc.get("refresh_token")):
            if platform == "instagram":
                cap = f"{title}\n\n{cap}".strip()
            rid, url = accounts.zernio_upload(acc, path, title, cap, scheduled_for=p.get("due_at"), job_id=job["id"], tags=clip.get("hashtags", []))
        elif platform == "youtube":
            rid, url = accounts.youtube_upload(acc, path, title, cap, clip.get("hashtags", []), creator["privacy"])
        elif platform == "instagram":
            rid, url = accounts.instagram_upload(acc, path, f"{title}\n\n{cap}", job["id"])
        elif platform == "tiktok":
            rid, url = accounts.tiktok_upload(acc, path, f"{title}\n\n{cap}", creator["privacy"])
        else:
            raise RuntimeError("That kind of account is no longer supported.")
        p.update(status="posted", posted_at=time.time(), remote_id=rid, url=url, error=None)
        creators.log(p["creator"], f"Posted to {acc['name']}: {title}")
    except Exception as e:  # noqa: BLE001
        err_str = str(e)
        if "Too many failed posts detected" in err_str or "rateLimitedUntil" in err_str or "429" in err_str:
            p.update(status="scheduled", due_at=time.time() + 1800, tries=0, error="Waiting for provider cooldown")
            try:
                (accounts._dir() / "zernio_accounts.json").unlink(missing_ok=True)
            except Exception:
                pass
        elif p["tries"] < 2 and clip and acc:
            p["tries"] += 1
            p["error"] = err_str[-300:]
            p.update(status="scheduled", due_at=time.time() + 600)  # try again in 10 minutes
        else:
            p["tries"] += 1
            p["error"] = err_str[-300:]
            p["status"] = "failed"
            creators.log(p["creator"], f"Post failed on {p['account_name']}: {p['error']}")
            alerts.notify(f"post failed on {p['account_name']} ({p['title']}): {p['error'][:200]}", kind="post")
    _save()
    _mirror(p)


def _run():
    while True:
        time.sleep(15)
        due = [p for p in list(_posts) if p["status"] == "scheduled" and p["due_at"] <= time.time() and p.get("user")]
        for p in due:
            try:
                with ctx.as_user(p["user"]):
                    if accounts.settings()["paused"]:
                        continue
                    acc = accounts.get(p["account"])
                    if acc and acc.get("rate_limited_until", 0) > time.time():
                        continue
                    with _lock:
                        if p["status"] != "scheduled":
                            continue
                        p["status"] = "posting"
                    _post(p)
            except Exception:  # noqa: BLE001
                pass


def _stats_for(recent):
    for aid in {p["account"] for p in recent if p["platform"] == "youtube"}:
        acc = accounts.get(aid)
        if acc:
            views = accounts.youtube_views(acc, [p["remote_id"] for p in recent if p["account"] == aid])
            for p in recent:
                if p["account"] == aid and p["remote_id"] in views:
                    p["views"] = views[p["remote_id"]]
    for p in recent:
        acc = accounts.get(p["account"]) if p["platform"] == "instagram" else None
        if acc:
            v = accounts.instagram_views(acc, p["remote_id"])
            if v is not None:
                p["views"] = v


def _stats():
    while True:
        for uid in {p.get("user") for p in _posts if p.get("user")}:
            try:
                with ctx.as_user(uid):
                    _stats_for([p for p in _mine() if p["status"] == "posted" and time.time() - (p.get("posted_at") or p.get("due_at") or 0) < 14 * 86400])
            except Exception:  # noqa: BLE001
                pass
        _save()
        time.sleep(1800)


def cancel(pid):
    with _lock:
        p = next((p for p in _mine() if p["id"] == pid), None)
        if not p or p["status"] != "scheduled":
            raise ValueError("Only posts that are still waiting can be cancelled.")
        p["status"] = "cancelled"
        _save()
    _mirror(p)


def retry(pid):
    with _lock:
        p = next((p for p in _mine() if p["id"] == pid), None)
        if not p or p["status"] not in ("failed", "cancelled"):
            raise ValueError("Only failed or cancelled posts can be retried.")
        p.update(status="scheduled", due_at=time.time(), tries=0, error=None)
        _save()
    _mirror(p)


def overview() -> dict:
    today = _day(time.time())
    _posts = _mine()  # everything below is about the signed-in user only
    rows = []
    all_cs, all_js = creators.all_creators(), jobs.list_jobs()
    for c in all_cs:
        js = [j for j in all_js if j["creator"] == c["id"]]
        clips = [k for j in js for k in j["clips"] if k.get("status") == "done"]
        ps = [p for p in _posts if p["creator"] == c["id"]]
        views = sum(p["views"] or 0 for p in ps)
        rows.append({
            "id": c["id"], "name": c["name"],
            "state": "recording" if live.active_for(c["id"]) else "waiting" if c["auto_watch"] and c["channel"] else "idle",
            "autopost": c["autopost"] and bool(c["accounts"]),
            "clips_today": sum(1 for k in clips if _day(k.get("made_at", 0)) == today), "clips_total": len(clips),
            "posted_today": sum(1 for p in ps if p["status"] == "posted" and _day(p.get("posted_at") or p.get("due_at") or 0) == today),
            "posted_total": sum(1 for p in ps if p["status"] == "posted"),
            "queued": sum(1 for p in ps if p["status"] in OPEN), "failed": sum(1 for p in ps if p["status"] == "failed"),
            "views": views, "earnings": round(views / 1000 * c["rate_per_1k"], 2)})
    names = {c["id"]: c["name"] for c in all_cs}
    queue = sorted((p for p in _posts if p["status"] in OPEN), key=lambda p: p.get("due_at", 0))
    done = sorted((p for p in _posts if p["status"] in ("posted", "failed")), key=lambda p: -(p.get("posted_at") or p.get("due_at", 0)))[:15]
    show = [{**{k: v for k, v in p.items() if k != "user"}, "creator_name": names.get(p["creator"], "")} for p in queue + done]
    # last 14 days, oldest first, for the home graph
    days = [_day(time.time() - 86400 * i) for i in range(13, -1, -1)]
    made, posted, views = {d: 0 for d in days}, {d: 0 for d in days}, {d: 0 for d in days}
    for j in all_js:
        for k in j["clips"]:
            d = _day(k.get("made_at") or j["created"])
            if k.get("status") == "done" and d in made:
                made[d] += 1
    for p in _posts:
        if p["status"] == "posted":
            p_day = _day(p.get("posted_at") or p.get("due_at") or time.time())
            if p_day in posted:
                posted[p_day] += 1
                views[p_day] += p.get("views") or 0
    daily = [{"day": d, "clips": made[d], "posted": posted[d], "views": views[d]} for d in days]
    return {"paused": accounts.settings()["paused"], "creators": rows, "posts": show, "daily": daily,
            "alerts": alerts.configured(), "recording": len(live.active_mine())}


def digest_text() -> str:
    o = overview()
    lines = ["PeakCut daily summary"]
    for r in o["creators"]:
        lines.append(f"- {r['name']}: {r['state']}, {r['clips_today']} clips today, {r['posted_today']} posted today, "
                     f"{r['queued']} waiting, {r['failed']} failed, {r['views']} views")
    if not o["creators"]:
        lines.append("No creators set up yet.")
    if o["paused"]:
        lines.append("Posting is paused.")
    return "\n".join(lines)


def start():
    with _lock:
        for p in _posts:
            if p["status"] == "posting":  # interrupted mid-upload last time
                p.update(status="failed", error="The studio closed during this upload. Check the account, then retry.")
        _save()
    jobs.on_clip_ready.append(on_clip_ready)
    threading.Thread(target=_run, daemon=True).start()
    threading.Thread(target=_stats, daemon=True).start()
    threading.Thread(target=alerts.digest_loop, args=(digest_text,), daemon=True).start()
    threading.Thread(target=alerts.keep_awake_loop,
                     args=(lambda: bool(live.active()) or any(p["status"] in OPEN for p in _posts),), daemon=True).start()
