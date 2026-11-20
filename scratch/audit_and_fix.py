import os
import sys
import json
from pathlib import Path

BASE = Path(r"c:\Users\Administrator\Desktop\PeakCut")
sys.path.insert(0, str(BASE))

from studio import jobs, render, config

users_dir = BASE / "data" / "users"
print("Scanning jobs in", users_dir)

modified_jobs = 0
clips_to_fix = []

for root, dirs, files in os.walk(users_dir):
    if "job.json" in files:
        job_file = Path(root) / "job.json"
        try:
            with open(job_file, "r", encoding="utf-8") as f:
                job = json.load(f)
        except Exception as e:
            print(f"Error loading {job_file}: {e}")
            continue

        changed = False
        for c in job.get("clips", []):
            cid = c.get("id")
            v_shift = c.get("v_shift")
            status = c.get("status")
            hook = c.get("hook", "")
            
            # Print any interesting clip
            if v_shift not in (None, 0.0) or "JASON" in hook or "CAN'T PLAY" in hook:
                print(f"[{job.get('id')}] Clip {cid}: hook='{hook[:30]}' v_shift={v_shift} status={status} ver={c.get('version')}")

            if v_shift not in (None, 0.0):
                c["v_shift"] = 0.0
                changed = True
                clips_to_fix.append((job, c))

        if changed:
            with open(job_file, "w", encoding="utf-8") as f:
                json.dump(job, f, indent=1)
            modified_jobs += 1

print(f"Total modified jobs: {modified_jobs}")
print(f"Total clips with non-zero v_shift: {len(clips_to_fix)}")

