"""Campaigns marketplace and trending live streams.

Brands and Whop creators pay clippers per view for posting short-form clips.
Provides full campaign guidelines, content requirements, platform payout rates,
and Whop submission guides.
"""

from __future__ import annotations
import json
from pathlib import Path
from . import config, ctx, creators

CATALOG: list[dict] = [
    {
        "id": "kai-cenat-gta6",
        "title": "Kai Cenat - $10,000 GTA 6 Pool Campaign",
        "brand": "Clipped & Sniped",
        "verified": True,
        "prize_pool": 10000,
        "budget_left": 10000,
        "rate_per_1k": 2.0,
        "badge": "• New Campaign",
        "pool_badge": "$10k prize pool",
        "banner_bg": "linear-gradient(135deg, #1e1338 0%, #3b1b6e 50%, #571649 100%)",
        "banner_text": "KAI CENAT",
        "banner_sub": "GTA MARATHON $10,000",
        "platforms": ["tiktok", "youtube", "instagram", "twitter"],
        "category": "Gaming & Streams",
        "streamer": "Kai Cenat",
        "streamer_channel": "https://www.twitch.tv/kaicenat",
        "streamer_vods_url": "https://www.youtube.com/@KaiCenat/videos",
        "video_url": "https://www.youtube.com/watch?v=q1jR850CE_o",
        "video_title": "Robbing Every Bank In GTA 6 Free Roam! (Kai Cenat Live)",
        "tags": "#GTA6 #KaiCenat #ClippedAndSniped #WhopRewards",
        "hook_text": "KAI CENAT GTA 6 MARATHON",
        "whop_url": "https://whop.com/hub/creators",
        "ends_in": "14 days",
        "min_views": 1000,
        "rates": {
            "TikTok": "$2.50 / 1k views",
            "YouTube Shorts": "$2.00 / 1k views",
            "Instagram Reels": "$1.50 / 1k views",
            "X / Twitter": "$1.00 / 1k views",
        },
        "content_rules": [
            "Clip funny reactions, crazy fails, rage moments, and high-energy GTA 6 gameplay from Kai Cenat's streams.",
            "Video must be formatted in 9:16 vertical (1080x1920) with animated subtitles.",
            "Must feature a strong hook in the opening 3 seconds.",
            "Source footage must be from Kai Cenat's official Twitch streams or YouTube VODs.",
        ],
        "prohibited": [
            "No reposting existing TikToks or other clippers' watermarked edits.",
            "No raw stream footage without captions or facecam zoom.",
            "No fake, bot, or purchased view engagement (Whop automated fraud scanner disqualifies fake views).",
            "No copyrighted music that triggers platform mute.",
        ],
        "geo_rules": "Tier 1 views (United States, United Kingdom, Canada, Australia) count at 100% payout rate. Minimum 1,000 verified organic views required for payout.",
        "submission_guide": [
            "1. Generate your clips using ShineCut's clipping engine.",
            "2. Post your video to TikTok, YouTube Shorts, or Instagram Reels.",
            "3. Ensure the description contains #GTA6 #KaiCenat and tags @KaiCenat.",
            "4. Wait 24 to 48 hours for the video to gain organic views.",
            "5. Copy your published video link and submit it on the Whop Campaign portal to track views and collect payout.",
        ],
    },
    {
        "id": "kreekcraft-gta6",
        "title": "KreekCraft GTA 6 Clipping",
        "brand": "ClipLaunch",
        "verified": True,
        "prize_pool": 3600,
        "budget_left": 3600,
        "rate_per_1k": 0.50,
        "badge": "🚀 Get Paid to Clip",
        "pool_badge": "$0.50 per 1k views",
        "banner_bg": "linear-gradient(135deg, #231224 0%, #4a1934 50%, #1e1a38 100%)",
        "banner_text": "KreekCraft",
        "banner_sub": "GTA 6 Clipping",
        "platforms": ["youtube", "tiktok", "instagram"],
        "category": "Gaming & Highlights",
        "streamer": "KreekCraft",
        "streamer_channel": "https://www.youtube.com/@KreekCraft",
        "streamer_vods_url": "https://www.youtube.com/@KreekCraft/videos",
        "video_url": "https://www.youtube.com/watch?v=7h_Z9L51p2w",
        "video_title": "KreekCraft GTA 6 Stream Highlights & Reaction",
        "tags": "#KreekCraft #GTA6 #ClipLaunch #GamingHighlights",
        "hook_text": "KREEKCRAFT GTA 6 MOMENT",
        "whop_url": "https://whop.com",
        "ends_in": "21 days",
        "min_views": 500,
        "rates": {
            "YouTube Shorts": "$0.50 / 1k views",
            "TikTok": "$0.50 / 1k views",
            "Instagram Reels": "$0.50 / 1k views",
        },
        "content_rules": [
            "Clip high-energy gameplay highlights, unexpected glitches, and funny moments from KreekCraft's videos.",
            "Video length must be between 15 and 60 seconds.",
            "Clear vertical 9:16 layout with readable captions.",
        ],
        "prohibited": [
            "No re-uploading full unedited video segments.",
            "No misleading clickbait titles unrelated to the clip.",
        ],
        "geo_rules": "Global views accepted. All organic platforms qualify.",
        "submission_guide": [
            "1. Create captioned shorts from KreekCraft streams or uploads.",
            "2. Publish to your channel with #KreekCraft #GTA6.",
            "3. Submit link via the Whop / ClipLaunch dashboard.",
            "4. Earnings automatically calculated and released weekly.",
        ],
    },
    {
        "id": "the-trading-floor",
        "title": "The Trading Floor Whop Rewards",
        "brand": "The Trading Floor",
        "verified": True,
        "prize_pool": 10000,
        "budget_left": 8500,
        "rate_per_1k": 3.00,
        "badge": "Highest Payout",
        "pool_badge": "$3.00 / 1k views",
        "banner_bg": "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)",
        "banner_text": "TRADING FLOOR",
        "banner_sub": "Whop Content Bounty",
        "platforms": ["tiktok", "youtube", "instagram"],
        "category": "Finance & Trading",
        "streamer": "The Trading Floor",
        "streamer_channel": "https://www.youtube.com/@TheTradingFloor",
        "video_url": "https://www.youtube.com/watch?v=1bZ_C24k1aU",
        "video_title": "The Trading Floor - Live Market Session & Strategy",
        "tags": "#Trading #WhopTrading #StockMarket #TheTradingFloor",
        "hook_text": "HOW HE MADE 10K TODAY",
        "whop_url": "https://whop.com",
        "ends_in": "24 days",
        "min_views": 1000,
        "rates": {
            "TikTok": "$3.00 / 1k views",
            "YouTube Shorts": "$2.50 / 1k views",
            "Instagram Reels": "$2.00 / 1k views",
        },
        "content_rules": [
            "Clip trade analysis, profit/loss reactions, risk management psychology, and live trading moments.",
            "Must include educational value or suspenseful trade executions.",
            "Clean captions and bold hook text required.",
        ],
        "prohibited": [
            "No financial advice disclaimers violation (always include educational disclaimer).",
            "No fabricated or edited fake account screenshots.",
        ],
        "geo_rules": "Tier 1 views (US, UK, CA, AU) qualify for top tier CPM.",
        "submission_guide": [
            "1. Cut trading stream moments with ShineCut.",
            "2. Post with #Trading #WhopTrading.",
            "3. Submit published video URL on Whop Rewards.",
            "4. Payouts processed every Monday via Stripe or PayPal.",
        ],
    },
    {
        "id": "jason-pool-9000",
        "title": "$9,000 Jason Pool Campaign",
        "brand": "Reach",
        "verified": True,
        "prize_pool": 9000,
        "budget_left": 9000,
        "rate_per_1k": 2.50,
        "badge": "• New Campaign",
        "pool_badge": "$9k prize pool",
        "banner_bg": "linear-gradient(135deg, #0e2a47 0%, #005f9e 50%, #48cae4 100%)",
        "banner_text": "JASON THEWEEN",
        "banner_sub": "$9,000 Prize Pool",
        "platforms": ["instagram", "tiktok", "twitter", "youtube"],
        "category": "IRL & Comedy",
        "streamer": "JasonTheween",
        "streamer_channel": "https://www.twitch.tv/jasontheween",
        "video_url": "https://www.youtube.com/watch?v=mZ7W4X6y1wY",
        "video_title": "JasonTheween GTA 6 Stream Moments & Chaos",
        "tags": "#JasonTheween #ReachCampaign #GTA6 #FaZe",
        "hook_text": "JASON THEWEEN FUNNIEST MOMENT",
        "whop_url": "https://whop.com",
        "ends_in": "18 days",
        "min_views": 1000,
        "rates": {
            "TikTok": "$2.50 / 1k views",
            "YouTube Shorts": "$2.00 / 1k views",
            "Instagram Reels": "$1.50 / 1k views",
        },
        "content_rules": [
            "Clip hilarious stream interactions, awkward dates, Discord calls, and gaming fails.",
            "Focus on high-energy streamer facial expressions and chat reactions.",
        ],
        "prohibited": [
            "No clips violating Twitch or platform community guidelines.",
        ],
        "geo_rules": "US and international organic views accepted.",
        "submission_guide": [
            "1. Clip live stream spikes or funny moments.",
            "2. Post with #JasonTheween #ReachCampaign.",
            "3. Submit link on Whop dashboard for automated verification.",
        ],
    },
    {
        "id": "reach-gta6-37500",
        "title": "REACH GTA 6 Campaign ($37,500+)",
        "brand": "Reach",
        "verified": True,
        "prize_pool": 15000,
        "budget_left": 13000,
        "rate_per_1k": 1.50,
        "badge": "• New Campaign",
        "pool_badge": "$15k prize pool",
        "banner_bg": "linear-gradient(135deg, #2b0c3d 0%, #6a0dad 50%, #d81159 100%)",
        "banner_text": "REACH GTA 6",
        "banner_sub": "CAMPAIGNS $37,500+",
        "platforms": ["instagram", "tiktok", "twitter", "youtube"],
        "category": "Gaming & Trailer",
        "streamer": "GTA 6 Streamers",
        "streamer_channel": "",
        "video_url": "https://www.youtube.com/watch?v=QdBZY2fkU-0",
        "video_title": "GTA 6 Official Gameplay Breakdown & Secrets",
        "tags": "#ReachGTA6 #GamingClips #GTA6 #RockstarGames",
        "hook_text": "GTA 6 UNREAL MOMENT",
        "whop_url": "https://whop.com",
        "ends_in": "25 days",
        "min_views": 2000,
        "rates": {
            "TikTok": "$1.50 / 1k views",
            "YouTube Shorts": "$1.50 / 1k views",
            "Instagram Reels": "$1.00 / 1k views",
        },
        "content_rules": [
            "GTA 6 breakdowns, trailer Easter eggs, map analysis, and gameplay leaks discussion.",
            "Vertical 9:16 layout with fast pacing.",
        ],
        "prohibited": ["No copyrighted full unedited trailer re-uploads."],
        "geo_rules": "All organic views qualify.",
        "submission_guide": [
            "1. Generate short-form content discussing GTA 6.",
            "2. Tag with #ReachGTA6 and post.",
            "3. Submit link on Whop.",
        ],
    },
    {
        "id": "faze-tournament-8500",
        "title": "$8,500 FaZe Tournament Clip Campaign",
        "brand": "Clippade",
        "verified": False,
        "prize_pool": 8500,
        "budget_left": 7800,
        "rate_per_1k": 2.00,
        "badge": "$2 per 1k views",
        "pool_badge": "$2 per 1k views",
        "banner_bg": "linear-gradient(135deg, #1a1a1a 0%, #8b0000 50%, #c41e3a 100%)",
        "banner_text": "FAZE CLAN",
        "banner_sub": "$8,500 Tournament",
        "platforms": ["instagram", "tiktok", "twitter", "youtube"],
        "category": "Esports & Tournaments",
        "streamer": "FaZe Clan",
        "streamer_channel": "https://www.twitch.tv/faze",
        "video_url": "https://www.youtube.com/watch?v=kXYiU_JCYtU",
        "video_title": "FaZe Clan Tournament Final Match & Clutch Moments",
        "tags": "#FaZe #FaZeUp #Clippade #EsportsClips",
        "hook_text": "FAZE TOURNAMENT MOMENT",
        "whop_url": "https://whop.com",
        "ends_in": "10 days",
        "min_views": 1000,
        "rates": {
            "TikTok": "$2.00 / 1k views",
            "YouTube Shorts": "$2.00 / 1k views",
            "Instagram Reels": "$1.50 / 1k views",
        },
        "content_rules": [
            "FaZe Clan tournament streams, insane clutches, sniper trickshots, and high-stakes matches.",
            "Clip must highlight the winning reaction or intense match point.",
        ],
        "prohibited": ["No low-resolution or off-screen screen recordings."],
        "geo_rules": "All organic global views qualify.",
        "submission_guide": [
            "1. Clip live FaZe matches using ShineCut.",
            "2. Post with #FaZe #FaZeUp.",
            "3. Submit on Whop / Clippade dashboard.",
        ],
    },
]

TRENDING_STREAMS: list[dict] = [
    {
        "channel": "ludwig",
        "name": "Ludwig",
        "platform": "twitch",
        "avatar": "https://static-cdn.jtvnw.net/jtv_user_pictures/104a32ec-3d92-4299-8cfb-6f81a1795c6f-profile_image-300x300.png",
        "title": "DAY 2 NON-LETHAL GTA VI RUN [DROPS ON] !discord",
        "game": "Grand Theft Auto VI",
        "viewers": 4110,
        "live": True,
        "verified": True,
    },
    {
        "channel": "kaicenat",
        "name": "Kai Cenat",
        "platform": "twitch",
        "avatar": "https://static-cdn.jtvnw.net/jtv_user_pictures/5be023b1-2dd4-4fa9-b88e-670dc951d8d1-profile_image-300x300.png",
        "title": "GTA 6 MARATHON DAY 1 | SPECIAL GUEST",
        "game": "Grand Theft Auto VI",
        "viewers": 84250,
        "live": True,
        "verified": True,
    },
    {
        "channel": "caseoh_",
        "name": "CaseOh",
        "platform": "twitch",
        "avatar": "https://static-cdn.jtvnw.net/jtv_user_pictures/8b049d53-a550-48e0-a7d1-e63d41f391a0-profile_image-300x300.png",
        "title": "SCARIEST GAMES ON STEAM",
        "game": "Horror Games",
        "viewers": 51200,
        "live": True,
        "verified": True,
    },
    {
        "channel": "jynxzi",
        "name": "Jynxzi",
        "platform": "twitch",
        "avatar": "https://static-cdn.jtvnw.net/jtv_user_pictures/d0ef5585-cdfa-47cb-a50e-5d15ca3ff8be-profile_image-300x300.png",
        "title": "1V1 TOURNAMENT FOR $10,000",
        "game": "Tom Clancy's Rainbow Six Siege",
        "viewers": 43900,
        "live": True,
        "verified": True,
    },
    {
        "channel": "xqc",
        "name": "xQc",
        "platform": "twitch",
        "avatar": "https://static-cdn.jtvnw.net/jtv_user_pictures/xqc-profile_image-92d06b720f04e1ab-300x300.jpeg",
        "title": "DAILY GAMING / TIKTOK REACTS",
        "game": "Just Chatting",
        "viewers": 36700,
        "live": True,
        "verified": True,
        "embed": "xqc",
        "url": "https://www.twitch.tv/xqc",
        "channel_url": "https://www.twitch.tv/xqc",
    },
    {
        "channel": "ai39lbFr410",
        "name": "TheBurntPeanut",
        "platform": "youtube",
        "avatar": "https://yt3.ggpht.com/QZZBJTwyc5uzqJIqN-2Ppx7MtQ9mA4pBCogun2twJr-vtlXXFQg0lHu3kNnkNXQO-H-ZumFBnA=s68-c-k-c0x00ffffff-no-rj",
        "title": "🔴LIVE | GTA 6 | DAY 5",
        "game": "Grand Theft Auto VI",
        "viewers": 58500,
        "live": True,
        "verified": True,
        "embed": "ai39lbFr410",
        "url": "https://www.youtube.com/watch?v=ai39lbFr410",
        "channel_url": "https://www.youtube.com/@TheBurntPeanut",
    },
    {
        "channel": "8PM0veeBXEM",
        "name": "Typical Gamer",
        "platform": "youtube",
        "avatar": "https://i.ytimg.com/vi/8PM0veeBXEM/hqdefault.jpg",
        "title": "🔴 LIVE! - PLAYING GTA 6 RIGHT NOW!",
        "game": "Grand Theft Auto VI",
        "viewers": 16500,
        "live": True,
        "verified": True,
        "embed": "8PM0veeBXEM",
        "url": "https://www.youtube.com/watch?v=8PM0veeBXEM",
        "channel_url": "https://www.youtube.com/@typicalgamer",
    },
]


def _user_file() -> Path:
    return config.user_dir(ctx.uid()) / "campaigns.json"


def _read_user() -> dict:
    f = _user_file()
    if f.is_file():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"enrolled": []}


def _save_user(data: dict):
    f = _user_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(data, indent=2), encoding="utf-8")


def list_campaigns() -> dict:
    """Returns the campaigns catalog with user enrollment status."""
    user_data = _read_user()
    enrolled_ids = {e.get("campaign_id"): e for e in user_data.get("enrolled", [])}
    catalog_out = []
    for c in CATALOG:
        item = dict(c)
        if c["id"] in enrolled_ids:
            item["enrolled"] = True
            item["enrolled_info"] = enrolled_ids[c["id"]]
        else:
            item["enrolled"] = False
        catalog_out.append(item)
    return {
        "catalog": catalog_out,
        "enrolled": user_data.get("enrolled", []),
    }


def get_campaign(camp_id: str) -> dict | None:
    return next((c for c in CATALOG if c["id"] == camp_id), None)


def enroll(campaign_id: str, creator_id: str) -> dict:
    camp = get_campaign(campaign_id)
    if not camp:
        raise KeyError(f"No such campaign: {campaign_id}")

    c = creators.get(creator_id) if creator_id else None
    if c:
        update_data = {
            "rate_per_1k": float(camp.get("rate_per_1k") or 0.0),
            "post_footer": camp.get("tags") or "",
        }
        if camp.get("hook_text") and not c.get("hook_text"):
            update_data["hook_text"] = camp["hook_text"]
        creators.update(creator_id, update_data)

    user_data = _read_user()
    enrolled = [e for e in user_data.get("enrolled", []) if e.get("campaign_id") != campaign_id]
    entry = {
        "campaign_id": campaign_id,
        "creator_id": creator_id or "",
        "creator_name": c["name"] if c else "",
        "campaign_title": camp["title"],
        "rate_per_1k": camp["rate_per_1k"],
        "views": 0,
        "earnings": 0.0,
        "clips_count": 0,
        "whop_url": camp.get("whop_url", "https://whop.com"),
        "tags": camp.get("tags", ""),
        "rules": camp.get("content_rules", []),
        "submission_guide": camp.get("submission_guide", []),
    }
    enrolled.append(entry)
    user_data["enrolled"] = enrolled
    _save_user(user_data)
    ctx.bump()
    return entry


def unenroll(campaign_id: str) -> bool:
    user_data = _read_user()
    enrolled = [e for e in user_data.get("enrolled", []) if e.get("campaign_id") != campaign_id]
    user_data["enrolled"] = enrolled
    _save_user(user_data)
    ctx.bump()
    return True


_yt_cache: list[dict] = []
_yt_cache_time: float = 0.0

_tw_cache: list[dict] = []
_tw_cache_time: float = 0.0


def _parse_viewers(txt) -> int:
    if not txt:
        return 0
    import re
    t = str(txt).replace(",", "").replace("watching", "").replace("viewers", "").replace("concurrent", "").strip()
    m = re.search(r"([\d.]+)\s*([KMBkmb])?", t)
    if not m:
        return 0
    val = float(m.group(1))
    unit = (m.group(2) or "").upper()
    if unit == "K":
        return int(val * 1000)
    if unit == "M":
        return int(val * 1000000)
    return int(val)


def fetch_popular_youtube(limit: int = 15) -> list[dict]:
    """Scrapes currently live, popular YouTube streams directly without API keys."""
    global _yt_cache, _yt_cache_time
    import time, re, urllib.request
    now = time.time()
    if _yt_cache and now - _yt_cache_time < 90:
        return list(_yt_cache)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "SOCS=CAESEwgDEgk2OTc3OTM3MjAaAmVuIAEaBgiA_LyaBg; CONSENT=YES+",
    }
    streams = []
    urls = ["https://www.youtube.com/gaming/live", "https://www.youtube.com/live"]
    for u in urls:
        try:
            req = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req, timeout=6) as resp:
                html = resp.read().decode("utf-8", "ignore")
            m = re.search(r"var ytInitialData\s*=\s*({.+?});</script>", html)
            if not m:
                continue
            data = json.loads(m.group(1))

            def find_renderers(obj):
                res = []
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if k in ("videoRenderer", "gridVideoRenderer", "compactVideoRenderer"):
                            res.append(v)
                        else:
                            res.extend(find_renderers(v))
                elif isinstance(obj, list):
                    for item in obj:
                        res.extend(find_renderers(item))
                return res

            for r in find_renderers(data):
                badges = [b.get("metadataBadgeRenderer", {}).get("label") for b in r.get("badges", [])]
                v_text = (r.get("viewCountText") or {}).get("runs", [{}])[0].get("text") or (r.get("viewCountText") or {}).get("simpleText") or ""
                is_live = any(b == "LIVE" for b in badges) or "watching" in str(v_text).lower()
                if not is_live:
                    continue
                vid = r.get("videoId")
                if not vid or len(vid) != 11:
                    continue
                title = (r.get("title") or {}).get("runs", [{}])[0].get("text") or (r.get("title") or {}).get("simpleText") or "Live Stream"
                byline = r.get("shortBylineText") or r.get("ownerText") or {}
                runs = byline.get("runs", [{}])
                name = runs[0].get("text") or "YouTube Creator"
                ch_path = runs[0].get("navigationEndpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get("url") or f"/watch?v={vid}"
                channel_url = "https://www.youtube.com" + ch_path
                viewers = _parse_viewers(v_text)

                thumbs = r.get("channelThumbnail", {}).get("thumbnails", []) or r.get("thumbnail", {}).get("thumbnails", [])
                avatar = thumbs[-1].get("url") if thumbs else f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"

                streams.append({
                    "channel": vid,
                    "name": name,
                    "platform": "youtube",
                    "avatar": avatar,
                    "title": title,
                    "game": "YouTube Live",
                    "viewers": viewers,
                    "live": True,
                    "verified": True,
                    "embed": vid,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "channel_url": channel_url,
                })
        except Exception:
            pass

    seen = set()
    unique = []
    for s in streams:
        if s["channel"] not in seen:
            seen.add(s["channel"])
            unique.append(s)

    unique.sort(key=lambda s: s["viewers"], reverse=True)
    if unique:
        _yt_cache = unique[:limit]
        _yt_cache_time = now
    return list(_yt_cache)


def fetch_popular_twitch(limit: int = 15) -> list[dict]:
    """Fetches top live streams from Twitch via public client."""
    global _tw_cache, _tw_cache_time
    import time
    now = time.time()
    if _tw_cache and now - _tw_cache_time < 90:
        return list(_tw_cache)

    try:
        import httpx
        _TWITCH_WEB = "kimne78kx3ncx6brgo4mv6wki5h1ko"
        ua = {"User-Agent": "Mozilla/5.0"}
        q = "query { streams(first: 15) { edges { node { id title viewersCount broadcaster { login displayName profileImageURL(width: 300) } game { name } } } } }"
        r = httpx.post("https://gql.twitch.tv/gql", json={"query": q}, headers={"Client-ID": _TWITCH_WEB, **ua}, timeout=6)
        data = r.json()
        edges = data.get("data", {}).get("streams", {}).get("edges", [])
        streams = []
        for e in edges:
            n = e.get("node") or {}
            b = n.get("broadcaster") or {}
            g = n.get("game") or {}
            login = b.get("login") or ""
            if not login:
                continue
            streams.append({
                "channel": login,
                "name": b.get("displayName") or login,
                "platform": "twitch",
                "avatar": b.get("profileImageURL") or "",
                "title": n.get("title") or "",
                "game": g.get("name") or "Gaming",
                "viewers": n.get("viewersCount") or 0,
                "live": True,
                "verified": True,
                "embed": login,
                "url": f"https://www.twitch.tv/{login}",
                "channel_url": f"https://www.twitch.tv/{login}",
            })
        if streams:
            _tw_cache = streams[:limit]
            _tw_cache_time = now
    except Exception:
        pass
    return list(_tw_cache)


def get_trending(platform: str = "") -> list[dict]:
    import os
    plat = (platform or "").lower().strip()
    if os.environ.get("PEAKCUT_TESTING") == "1" or "_test" in os.environ.get("PEAKCUT_DATA", ""):
        if plat == "youtube":
            return [s for s in TRENDING_STREAMS if s.get("platform") == "youtube"]
        if plat == "twitch":
            return [s for s in TRENDING_STREAMS if s.get("platform") == "twitch"]
        return TRENDING_STREAMS

    yt = fetch_popular_youtube()
    tw = fetch_popular_twitch()
    if not yt:
        yt = [s for s in TRENDING_STREAMS if s.get("platform") == "youtube"]
    if not tw:
        tw = [s for s in TRENDING_STREAMS if s.get("platform") == "twitch"]

    if plat == "youtube":
        return yt
    if plat == "twitch":
        return tw

    combined = []
    max_len = max(len(yt), len(tw))
    for i in range(max_len):
        if i < len(yt):
            combined.append(yt[i])
        if i < len(tw):
            combined.append(tw[i])
    return combined[:20] if combined else TRENDING_STREAMS
