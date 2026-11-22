"""Campaigns marketplace and trending live streams.

Brands pay clippers per view for posting short-form clips with campaign tags.
Clippers can browse active campaigns, enroll their creators, and track view payouts.
"""

from __future__ import annotations
import json
from pathlib import Path
from . import config, ctx, creators

# Verified campaigns matching the marketplace catalog
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
        "badge_color": "#3B82F6",
        "banner_text": "KAI CENAT",
        "banner_sub": "GTA MARATHON $10,000",
        "pool_badge": "$10k prize pool",
        "banner_bg": "linear-gradient(135deg, #1e1338 0%, #3b1b6e 50%, #571649 100%)",
        "avatar": "https://static-cdn.jtvnw.net/jtv_user_pictures/5be023b1-2dd4-4fa9-b88e-670dc951d8d1-profile_image-300x300.png",
        "platforms": ["instagram", "tiktok", "twitter", "youtube"],
        "streamer": "Kai Cenat",
        "streamer_channel": "https://www.twitch.tv/kaicenat",
        "tags": "#GTA6 #KaiCenat #ClippedAndSniped",
        "hook_text": "KAI CENAT'S GTA 6 MARATHON",
        "rules": "Clips must include the campaign hashtag #GTA6 and tag @KaiCenat. Payout is calculated based on cumulative organic views across Instagram Reels, TikTok, YouTube Shorts, and X.",
        "min_views": 1000,
        "ends_in": "14 days",
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
        "badge_color": "#EC4899",
        "banner_text": "KreekCraft",
        "banner_sub": "GTA 6 Clipping",
        "pool_badge": "$0.50 per 1k views",
        "banner_bg": "linear-gradient(135deg, #231224 0%, #4a1934 50%, #1e1a38 100%)",
        "avatar": "https://static-cdn.jtvnw.net/jtv_user_pictures/601170d1-6bfb-4dbe-a178-0cb934444747-profile_image-300x300.png",
        "platforms": ["instagram", "tiktok", "youtube"],
        "streamer": "KreekCraft",
        "streamer_channel": "https://www.youtube.com/@KreekCraft",
        "tags": "#KreekCraft #GTA6 #ClipLaunch",
        "hook_text": "KREEKCRAFT GTA 6 HIGHLIGHT",
        "rules": "Flat payout rate of $0.50 for every 1,000 views. Minimum clip duration 15 seconds. Submissions must be original edits with captions.",
        "min_views": 500,
        "ends_in": "21 days",
    },
    {
        "id": "dangasd3m-ruckus",
        "title": "Dangasd3m x RUCKUS | GTA 6",
        "brand": "Ruckus",
        "verified": False,
        "prize_pool": 1000,
        "budget_left": 906,
        "rate_per_1k": 2.00,
        "badge": "$2 per 1k views",
        "badge_color": "#F59E0B",
        "banner_text": "Dangasd3m x RUCKUS",
        "banner_sub": "GTA 6 Exclusive",
        "pool_badge": "$2 per 1k views",
        "banner_bg": "linear-gradient(135deg, #1b263b 0%, #314a68 50%, #526f8d 100%)",
        "avatar": "",
        "platforms": ["tiktok"],
        "streamer": "Dangasd3m",
        "streamer_channel": "",
        "tags": "#Ruckus #GTA6 #Dangasd3m",
        "hook_text": "GTA 6 GAMEPLAY HIGHLIGHT",
        "rules": "Exclusive TikTok clipping. Top performing clips receive bonus multipliers.",
        "min_views": 1000,
        "ends_in": "7 days",
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
        "badge_color": "#3B82F6",
        "banner_text": "JASON THEWEEN",
        "banner_sub": "$9,000 Prize Pool",
        "pool_badge": "$9k prize pool",
        "banner_bg": "linear-gradient(135deg, #0e2a47 0%, #005f9e 50%, #48cae4 100%)",
        "avatar": "https://static-cdn.jtvnw.net/jtv_user_pictures/1fb098d7-789a-4127-b501-1b866c1b48b5-profile_image-300x300.png",
        "platforms": ["instagram", "tiktok", "twitter", "youtube"],
        "streamer": "JasonTheween",
        "streamer_channel": "https://www.twitch.tv/jasontheween",
        "tags": "#JasonTheween #ReachCampaign #GTA6",
        "hook_text": "JASON THEWEEN REACTS",
        "rules": "All platforms accepted. Clips must be at least 20 seconds long with captions enabled.",
        "min_views": 1000,
        "ends_in": "18 days",
    },
    {
        "id": "reach-gta6-37500",
        "title": "GTA 6",
        "brand": "Reach",
        "verified": True,
        "prize_pool": 15000,
        "budget_left": 13000,
        "rate_per_1k": 1.50,
        "badge": "• New Campaign",
        "badge_color": "#3B82F6",
        "banner_text": "REACH GTA 6",
        "banner_sub": "CAMPAIGNS $37,500+",
        "pool_badge": "$15k prize pool",
        "banner_bg": "linear-gradient(135deg, #2b0c3d 0%, #6a0dad 50%, #d81159 100%)",
        "avatar": "",
        "platforms": ["instagram", "tiktok", "twitter", "youtube"],
        "streamer": "GTA 6 Streamers",
        "streamer_channel": "",
        "tags": "#ReachGTA6 #GamingClips #GTA6",
        "hook_text": "GTA 6 UNREAL MOMENT",
        "rules": "General GTA 6 clipping campaign. Payout pool distributed weekly based on verified view counts.",
        "min_views": 2000,
        "ends_in": "25 days",
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
        "badge_color": "#EF4444",
        "banner_text": "FAZE CLAN",
        "banner_sub": "$8,500 Tournament",
        "pool_badge": "$2 per 1k views",
        "banner_bg": "linear-gradient(135deg, #1a1a1a 0%, #8b0000 50%, #c41e3a 100%)",
        "avatar": "",
        "platforms": ["instagram", "tiktok", "twitter", "youtube"],
        "streamer": "FaZe Clan",
        "streamer_channel": "https://www.twitch.tv/faze",
        "tags": "#FaZe #FaZeUp #Clippade",
        "hook_text": "FAZE TOURNAMENT MOMENT",
        "rules": "FaZe Clan tournament streams and matches. Best moments and clutch plays.",
        "min_views": 1000,
        "ends_in": "10 days",
    },
]

# Trending live streams featured on Home
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
    },
    {
        "channel": "fanum",
        "name": "Fanum",
        "platform": "twitch",
        "avatar": "https://static-cdn.jtvnw.net/jtv_user_pictures/a5bb3457-3aa3-4f93-b6d4-8d4b3ff255d6-profile_image-300x300.png",
        "title": "CHILL VIBES AND GTA 6 PREVIEW",
        "game": "Grand Theft Auto VI",
        "viewers": 18400,
        "live": True,
        "verified": True,
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
    """Returns the campaigns catalog along with the current user's enrolled status."""
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


def enroll(campaign_id: str, creator_id: str) -> dict:
    """Enrolls a creator in a campaign, auto-updating their rate and tags."""
    camp = next((c for c in CATALOG if c["id"] == campaign_id), None)
    if not camp:
        raise KeyError(f"No such campaign: {campaign_id}")

    # Update creator settings if creator_id is given
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
    }
    enrolled.append(entry)
    user_data["enrolled"] = enrolled
    _save_user(user_data)
    ctx.bump()
    return entry


def unenroll(campaign_id: str) -> bool:
    """Removes a campaign enrollment for the user."""
    user_data = _read_user()
    enrolled = [e for e in user_data.get("enrolled", []) if e.get("campaign_id") != campaign_id]
    user_data["enrolled"] = enrolled
    _save_user(user_data)
    ctx.bump()
    return True


def get_trending() -> list[dict]:
    """Returns the list of trending live streams."""
    return TRENDING_STREAMS
