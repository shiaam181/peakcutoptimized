from pathlib import Path
import os
import sys

# Test against throwaway folder
TEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TEST_DIR))

os.environ["PEAKCUT_DATA"] = str(Path(__file__).resolve().parent / "_test_camp_data")

from studio import campaigns, config, creators, ctx

def run():
    print("Testing studio.campaigns module...")
    ctx.set_uid("u_testuser")
    
    # 1. Catalog check
    res = campaigns.list_campaigns()
    assert len(res["catalog"]) == 6, f"Expected 6 campaigns, got {len(res['catalog'])}"
    kai = next(c for c in res["catalog"] if c["id"] == "kai-cenat-gta6")
    assert kai["prize_pool"] == 10000
    assert "Kai Cenat" in kai["title"]
    print(" - Catalog list: OK (6 campaigns found)")

    # 2. Trending check
    trending = campaigns.get_trending()
    assert len(trending) >= 5
    assert trending[0]["channel"] == "ludwig"
    print(" - Trending streams: OK (Ludwig and others found)")

    # 3. Create a test creator and enroll in campaign
    cr = creators.create({"name": "Test Kai Clipper", "channel": "https://www.twitch.tv/kaicenat"})
    enrolled = campaigns.enroll("kai-cenat-gta6", cr["id"])
    assert enrolled["campaign_id"] == "kai-cenat-gta6"
    assert enrolled["creator_id"] == cr["id"]
    
    updated_cr = creators.get(cr["id"])
    assert updated_cr["rate_per_1k"] == 2.0
    assert "#GTA6" in updated_cr["post_footer"]
    print(" - Campaign enrollment & creator update: OK")

    # 4. Check list_campaigns shows enrolled
    res2 = campaigns.list_campaigns()
    kai_updated = next(c for c in res2["catalog"] if c["id"] == "kai-cenat-gta6")
    assert kai_updated["enrolled"] is True
    assert len(res2["enrolled"]) == 1
    print(" - Enrolled state tracking: OK")

    # 5. Unenroll
    campaigns.unenroll("kai-cenat-gta6")
    res3 = campaigns.list_campaigns()
    assert len(res3["enrolled"]) == 0
    print(" - Unenroll: OK")

    # Clean up test folder
    import shutil
    shutil.rmtree(os.environ["PEAKCUT_DATA"], ignore_errors=True)
    print("ALL CAMPAIGN TESTS PASSED!")

if __name__ == "__main__":
    run()
