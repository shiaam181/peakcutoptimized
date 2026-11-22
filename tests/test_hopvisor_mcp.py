from pathlib import Path
import os
import sys

TEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TEST_DIR))

os.environ["PEAKCUT_DATA"] = str(Path(__file__).resolve().parent / "_test_mcp_data")

from studio import mcp_hopvisor, config, creators, ctx

def run():
    print("Testing studio.mcp_hopvisor module...")
    ctx.set_uid("u_testmcp")

    # 1. Status check
    st = mcp_hopvisor.get_status()
    assert "connected" in st
    assert "auth_url" in st
    assert "https://mcp.hopvisor.com/authorize" in st["auth_url"]
    print(" - Status & Auth URL generation: OK")

    # 2. Token setting
    res = mcp_hopvisor.set_token("test_bearer_token_123")
    assert res["connected"] is True
    st2 = mcp_hopvisor.get_status()
    assert st2["connected"] is True
    print(" - Token storage: OK")

    # 3. Search campaigns
    camps = mcp_hopvisor.search_whop_campaigns()
    assert len(camps) >= 4
    assert any("Kai Cenat" in c["title"] for c in camps)
    print(" - Whop campaigns search: OK (found live Whop campaigns)")

    # 4. Filter campaigns by query and platform
    filtered = mcp_hopvisor.search_whop_campaigns(query="trading", platform="tiktok")
    assert len(filtered) >= 1
    assert "Trading" in filtered[0]["title"]
    print(" - Query and platform filtering: OK")

    # 5. Prepare clipping
    cr = creators.create({"name": "Whop Clipper", "channel": "https://www.twitch.tv/kaicenat"})
    prep = mcp_hopvisor.prepare_whop_clipping("whop-kai-cenat-bounty", cr["id"])
    assert prep["campaign_id"] == "whop-kai-cenat-bounty"
    assert "#Whop" in prep["tags"]
    
    updated_cr = creators.get(cr["id"])
    assert updated_cr["rate_per_1k"] == 2.50
    assert "#Whop" in updated_cr["post_footer"]
    print(" - Prepare clipping & creator configuration: OK")

    # Clean up test folder
    import shutil
    shutil.rmtree(os.environ["PEAKCUT_DATA"], ignore_errors=True)
    print("ALL HOPVISOR MCP TESTS PASSED!")

if __name__ == "__main__":
    run()

