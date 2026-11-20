import os
import sys
import json
import time
from pathlib import Path
import cv2

BASE = Path(r"c:\Users\Administrator\Desktop\PeakCut")
sys.path.insert(0, str(BASE))

from studio import jobs, render, config

def rerender(job_id, clip_id):
    print(f"\n--- Re-rendering {job_id} / {clip_id} ---")
    for root, dirs, files in os.walk(BASE / "data" / "users"):
        if "job.json" in files:
            p = Path(root) / "job.json"
            with open(p, "r", encoding="utf-8") as f:
                j = json.load(f)
            if j.get("id") == job_id:
                for c in j.get("clips", []):
                    if c["id"] == clip_id:
                        c["v_shift"] = 0.0
                        c["layout"] = "facecam"
                        # render directly
                        src = Path(c["src"])
                        out_dir = Path(root) / "clips"
                        off = c.get("src_offset", 0.0)
                        local = dict(c, start=c["start"] - off, end=c["end"] - off, v_shift=0.0)
                        near = [dict(w, s=w["s"] - off, e=w["e"] - off) for w in c.get("fixed_words", [])]
                        
                        out = render.render_clip(src, out_dir, clip_id, local, near, j.get("width", 1280), j.get("height", 720))
                        c.update(out)
                        c["version"] = c.get("version", 0) + 1
                        c["made_at"] = time.time()
                        
                        with open(p, "w", encoding="utf-8") as fw:
                            json.dump(j, fw, indent=1)
                        print(f"Rendered successfully: version={c['version']} file={out['file']}")
                        
                        # Verify frames
                        mp4 = out_dir / out["file"]
                        cap = cv2.VideoCapture(str(mp4))
                        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        dur = total_frames / max(1, fps)
                        print(f"MP4 properties: frames={total_frames}, fps={fps:.2f}, dur={dur:.2f}s")
                        
                        # Check frame at 2.5s and 20.0s
                        for check_sec in (2.5, 20.0):
                            if check_sec < dur:
                                cap.set(cv2.CAP_PROP_POS_MSEC, check_sec * 1000.0)
                                ok, f = cap.read()
                                if ok:
                                    print(f"Frame at {check_sec}s read ok, shape={f.shape}")
                        cap.release()
                        return

rerender("20261120-131334-3a2fa9d100", "clip001")
rerender("20261120-114947-732dff3736", "clip005")
print("\nDone re-rendering.")

