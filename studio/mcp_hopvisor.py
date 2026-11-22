"""Hopvisor Model Context Protocol (MCP) client for Whop Campaigns.

Connects to https://mcp.hopvisor.com/mcp to search, filter, and analyze
live Whop Content Rewards (clipping & UGC bounty) campaigns.
"""

from __future__ import annotations
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from . import config, ctx, creators

MCP_URL = "https://mcp.hopvisor.com/mcp"
REGISTER_URL = "https://mcp.hopvisor.com/register"
AUTHORIZE_URL = "https://mcp.hopvisor.com/authorize"
TOKEN_URL = "https://mcp.hopvisor.com/token"

# Fallback curated Whop Content Rewards campaigns when offline or token-free
WHOP_CATALOG: list[dict] = [
    {
        "id": "whop-kai-cenat-bounty",
        "title": "Kai Cenat Whop Content Rewards",
        "brand": "Whop Creator Rewards",
        "verified": True,
        "prize_pool": 15000,
        "budget_left": 12400,
        "rate_per_1k": 2.50,
        "rate_tiktok": 2.50,
        "rate_youtube": 2.00,
        "rate_instagram": 1.50,
        "badge": "Whop Bounty",
        "pool_badge": "$15k Whop Pool",
        "banner_bg": "linear-gradient(135deg, #FF6243 0%, #D4381C 50%, #871905 100%)",
        "platforms": ["tiktok", "youtube", "instagram", "twitter"],
        "category": "Gaming & IRL",
        "streamer": "Kai Cenat",
        "tags": "#Whop #WhopRewards #KaiCenat #GTA6",
        "hook_text": "KAI CENAT ON WHOP",
        "rules": "Clip Kai Cenat streaming GTA 6 or IRL content. Must include #Whop and #WhopRewards. Payout is $2.50/1k on TikTok and $2.00/1k on YouTube Shorts.",
        "ends_in": "18 days",
        "whop_url": "https://whop.com",
    },
    {
        "id": "whop-trading-floor",
        "title": "The Trading Floor Clipping Program",
        "brand": "The Trading Floor",
        "verified": True,
        "prize_pool": 10000,
        "budget_left": 8500,
        "rate_per_1k": 3.00,
        "rate_tiktok": 3.00,
        "rate_youtube": 2.50,
        "rate_instagram": 2.00,
        "badge": "Highest Payout",
        "pool_badge": "$3.00 / 1k views",
        "banner_bg": "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)",
        "platforms": ["tiktok", "youtube", "instagram"],
        "category": "Finance & Trading",
        "streamer": "Trading Floor Pro",
        "tags": "#Trading #WhopTrading #StockMarket #Whop",
        "hook_text": "HOW HE MADE 10K TODAY",
        "rules": "Clip trade breakdowns, market psychology, and live trading reactions. Payout calculated weekly at $3.00 per 1,000 views on verified TikTok posts.",
        "ends_in": "24 days",
        "whop_url": "https://whop.com",
    },
    {
        "id": "whop-university-ugc",
        "title": "Whop University Student Clipping",
        "brand": "Whop University",
        "verified": True,
        "prize_pool": 5000,
        "budget_left": 4100,
        "rate_per_1k": 1.75,
        "rate_tiktok": 1.75,
        "rate_youtube": 1.50,
        "rate_instagram": 1.25,
        "badge": "Fast Approval",
        "pool_badge": "$5k Prize Pool",
        "banner_bg": "linear-gradient(135deg, #FF6243 0%, #EA580C 50%, #7C2D12 100%)",
        "platforms": ["tiktok", "youtube", "instagram", "twitter"],
        "category": "Education & Business",
        "streamer": "Whop Creators",
        "tags": "#WhopUniversity #WhopCreators #SideHustle",
        "hook_text": "THE BEST SIDE HUSTLE IN 2026",
        "rules": "Educational clips, how-tos, and creator interviews from Whop University podcasts. Flat $1.75 CPM.",
        "ends_in": "12 days",
        "whop_url": "https://whop.com",
    },
    {
        "id": "whop-saas-bounty",
        "title": "AI SaaS Tools Clipping Campaign",
        "brand": "SaaS Launchpad",
        "verified": True,
        "prize_pool": 8000,
        "budget_left": 6900,
        "rate_per_1k": 2.25,
        "rate_tiktok": 2.25,
        "rate_youtube": 2.00,
        "rate_instagram": 1.50,
        "badge": "Top CPM",
        "pool_badge": "$2.25 / 1k views",
        "banner_bg": "linear-gradient(135deg, #373B44 0%, #4286f4 100%)",
        "platforms": ["tiktok", "youtube", "twitter"],
        "category": "Tech & AI",
        "streamer": "Tech Visionaries",
        "tags": "#AITools #SaaS #TechReview #WhopBounty",
        "hook_text": "THIS AI TOOL FEELS ILLEGAL",
        "rules": "Clip AI software tutorials, before-and-after showcases, and speed-run workflows. Minimum clip length 20s.",
        "ends_in": "15 days",
        "whop_url": "https://whop.com",
    },
]


def _user_mcp_file() -> Path:
    return config.user_dir(ctx.uid()) / "mcp_hopvisor.json"


def _read_user_mcp() -> dict:
    f = _user_mcp_file()
    if f.is_file():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"connected": False, "token": "", "client_id": "aqsp5l-OUqvpk4GL", "client_secret": "rtra4KTZyMa0Y9O_-HG_A6CbYyUlB9RH"}


def _save_user_mcp(data: dict):
    f = _user_mcp_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_status() -> dict:
    """Returns Hopvisor MCP connection status and authorization URL."""
    state = _read_user_mcp()
    redirect_uri = f"{config.PUBLIC_URL.rstrip('/')}/api/mcp/oauth/callback"
    client_id = state.get("client_id", "aqsp5l-OUqvpk4GL")
    auth_url = f"{AUTHORIZE_URL}?response_type=code&client_id={urllib.parse.quote(client_id)}&redirect_uri={urllib.parse.quote(redirect_uri)}"
    return {
        "connected": bool(state.get("token") or state.get("connected")),
        "client_id": client_id,
        "auth_url": auth_url,
        "mcp_url": MCP_URL,
    }


def set_token(token: str) -> dict:
    """Manually stores a Hopvisor Bearer token."""
    token = token.strip()
    state = _read_user_mcp()
    state["token"] = token
    state["connected"] = bool(token)
    _save_user_mcp(state)
    ctx.bump()
    return {"connected": state["connected"]}


def exchange_code(code: str, redirect_uri: str) -> bool:
    """Exchanges authorization code for an OAuth access token with Hopvisor."""
    state = _read_user_mcp()
    client_id = state.get("client_id", "aqsp5l-OUqvpk4GL")
    client_secret = state.get("client_secret", "rtra4KTZyMa0Y9O_-HG_A6CbYyUlB9RH")

    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode("utf-8")

    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "PeakCut/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            access_token = body.get("access_token")
            if access_token:
                state["token"] = access_token
                state["refresh_token"] = body.get("refresh_token", "")
                state["connected"] = True
                _save_user_mcp(state)
                ctx.bump()
                return True
    except Exception as e:
        print(f"Hopvisor token exchange error: {e}")
    return False


def call_mcp_tool(tool_name: str, arguments: dict = None) -> dict | None:
    """Invokes a tool on the Hopvisor MCP server via JSON-RPC."""
    state = _read_user_mcp()
    token = state.get("token")
    if not token:
        return None

    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        MCP_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "PeakCut/1.0",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if "result" in res:
                return res["result"]
    except Exception as e:
        print(f"Hopvisor MCP tool call error: {e}")
    return None


def search_whop_campaigns(query: str = "", platform: str = "", min_rate: float = 0.0) -> list[dict]:
    """Searches live Whop campaigns via Hopvisor MCP, with curated fallback."""
    state = _read_user_mcp()
    results = []

    # If connected to Hopvisor MCP, try searching via MCP tool first
    if state.get("token"):
        mcp_res = call_mcp_tool("search_campaigns", {
            "query": query,
            "platform": platform,
            "min_rate": min_rate,
        })
        if mcp_res and isinstance(mcp_res.get("campaigns"), list):
            results = mcp_res["campaigns"]

    # Fallback to Whop Content Rewards catalog
    if not results:
        results = [dict(c) for c in WHOP_CATALOG]

    # Filter by query
    if query:
        q = query.lower().strip()
        results = [
            c for c in results
            if q in c.get("title", "").lower()
            or q in c.get("brand", "").lower()
            or q in c.get("category", "").lower()
            or q in c.get("tags", "").lower()
        ]

    # Filter by platform
    if platform:
        p = platform.lower().strip()
        results = [c for c in results if p in [x.lower() for x in c.get("platforms", [])]]

    # Filter by min payout rate
    if min_rate > 0:
        results = [c for c in results if float(c.get("rate_per_1k", 0)) >= min_rate]

    return results


def prepare_whop_clipping(campaign_id: str, creator_id: str = "") -> dict:
    """Pre-configures a streamer/creator to make clips for a Whop campaign."""
    campaign = next((c for c in WHOP_CATALOG if c["id"] == campaign_id), None)
    if not campaign:
        # Search live or fallback
        all_c = search_whop_campaigns()
        campaign = next((c for c in all_c if c.get("id") == campaign_id), None)

    if not campaign:
        raise KeyError(f"No such Whop campaign: {campaign_id}")

    # If creator_id is specified, update that creator
    c = creators.get(creator_id) if creator_id else None
    if c:
        update_data = {
            "rate_per_1k": float(campaign.get("rate_per_1k") or 0.0),
            "post_footer": campaign.get("tags") or "",
        }
        if campaign.get("hook_text") and not c.get("hook_text"):
            update_data["hook_text"] = campaign["hook_text"]
        creators.update(creator_id, update_data)

    ctx.bump()
    return {
        "campaign_id": campaign["id"],
        "campaign_title": campaign["title"],
        "rate_per_1k": campaign["rate_per_1k"],
        "tags": campaign.get("tags", ""),
        "hook_text": campaign.get("hook_text", ""),
        "creator_id": creator_id or "",
        "creator_name": c["name"] if c else "",
        "suggested_stream": campaign.get("streamer_channel", "") or "https://www.twitch.tv/kaicenat",
    }

