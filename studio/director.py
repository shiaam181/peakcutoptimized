"""Director and layout analysis for ShineCut:
- Automatic facecam detection for gaming / stream recordings (gameplay on top, cam on bottom).
- Automatic multicam / two-person podcast detection (split-screen with host on top, guest on bottom, capturing speech & reactions).
- Smart positioning of captions and hook titles to avoid covering faces.
"""
import os
import re
import subprocess
from pathlib import Path
import cv2
import numpy as np

from . import config

W, H = config.OUT_W, config.OUT_H  # 1080, 1920
MODEL_PATH = Path(__file__).resolve().parent / "models" / "face_detection_yunet_2023mar.onnx"

_DETECTOR = None


def _get_detector(w: int, h: int):
    global _DETECTOR
    if not MODEL_PATH.is_file():
        return None
    try:
        if _DETECTOR is None:
            _DETECTOR = cv2.FaceDetectorYN.create(str(MODEL_PATH), "", (w, h), 0.6, 0.3, 5000)
        _DETECTOR.setInputSize((w, h))
        return _DETECTOR
    except Exception:
        return None


def open_video(path):
    p = str(path)
    if os.name == "nt" and os.path.isabs(p) and not p.startswith("\\\\?\\"):
        p = "\\\\?\\" + os.path.abspath(p)
    return cv2.VideoCapture(p)


def _sample_frames(video_path, start: float, duration: float, n: int = 20):
    cap = open_video(video_path)
    if not cap.isOpened():
        return []
    frames = []
    for k in range(n):
        t_sec = start + duration * (k + 0.5) / n
        cap.set(cv2.CAP_PROP_POS_MSEC, t_sec * 1000.0)
        ok, frame = cap.read()
        if ok and frame is not None:
            frames.append(frame)
    cap.release()
    return frames


def detect_faces_in_frame(frame, target_w: int = 640):
    """Detect faces in a BGR frame, returning list of (cx, cy, w, h, score) in 0..1 shares."""
    h0, w0 = frame.shape[:2]
    scale = target_w / w0
    target_h = int(h0 * scale)
    small = cv2.resize(frame, (target_w, target_h))
    det = _get_detector(target_w, target_h)
    if det is None:
        return []
    try:
        _, faces = det.detect(small)
        if faces is None:
            return []
        out = []
        for f in faces:
            x, y, bw, bh = f[0], f[1], f[2], f[3]
            score = float(f[14]) if len(f) > 14 else 0.9
            if bw >= 16 and score >= 0.55:
                cx = (x + bw / 2.0) / target_w
                cy = (y + bh / 2.0) / target_h
                w_share = bw / target_w
                h_share = bh / target_h
                out.append((cx, cy, w_share, h_share, score))
        return out
    except Exception:
        return []


def _detect_circle_cam(frames, cx_px, cy_px, fh_px, src_w, src_h):
    """Checks if the webcam overlay is a circular cutout using HoughCircles."""
    found = []
    r0, r1 = int(0.9 * fh_px), int(2.4 * fh_px)
    pad = r1 + 10
    x0, y0 = max(0, int(cx_px - pad)), max(0, int(cy_px - pad))
    x1, y1 = min(src_w, int(cx_px + pad)), min(src_h, int(cy_px + pad))
    for f in frames:
        roi = cv2.medianBlur(cv2.cvtColor(f[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY), 5)
        c = cv2.HoughCircles(roi, cv2.HOUGH_GRADIENT, dp=1.2, minDist=10 * r1, param1=120, param2=40,
                             minRadius=r0, maxRadius=r1)
        if c is not None:
            for x, y, r in c[0]:
                if np.hypot(x + x0 - cx_px, y + y0 - cy_px) < 0.6 * fh_px:
                    found.append((x + x0, y + y0, r))
                    break
    if len(found) < max(2, len(frames) // 3):
        return None
    return [float(v) for v in np.median(np.array(found), axis=0)]


def detect_facecam(video_path, duration: float, src_w: int, src_h: int):
    """Detects webcam overlay (facecam) on live streams or gameplay recordings.
    Returns {'x', 'y', 'w', 'h', 'shape': 'rect'|'circle'} in pixels, or None.
    """
    frames = _sample_frames(video_path, 0.0, duration, n=24)
    if len(frames) < 6:
        return None

    # Detect faces in all sampled frames (converted to pixel coordinates)
    per_frame = []
    for f in frames:
        det = detect_faces_in_frame(f)
        px_faces = [(d[0] * src_w, d[1] * src_h, d[3] * src_h) for d in det]
        per_frame.append(px_faces)

    tol = 0.035 * src_w
    best_c, best_hits = None, []

    for faces in per_frame:
        for c in faces:
            hits = []
            for i, fs in enumerate(per_frame):
                near = [f for f in fs if abs(f[0] - c[0]) < tol and abs(f[1] - c[1]) < tol]
                if near:
                    hits.append((i, near[0]))
            if len(hits) > len(best_hits):
                best_c, best_hits = c, hits

    if not best_c or len(best_hits) < max(4, int(0.45 * len(frames))):
        return None

    cx, cy, fh = (float(v) for v in np.median(np.array([h[1] for h in best_hits]), axis=0))

    # A webcam overlay is small and positioned towards an edge (left or right side)
    # A centered face or a face larger than 22% of screen height is a normal presenter, not a facecam
    if fh > 0.22 * src_h or (0.28 * src_w < cx < 0.72 * src_w):
        return None

    circle = _detect_circle_cam([frames[i] for i, _ in best_hits], cx, cy, fh, src_w, src_h)
    if circle:
        x, y, r = circle
        r += 4
        return {"x": int(x - r), "y": int(y - r), "w": int(2 * r), "h": int(2 * r), "shape": "circle"}

    bh = min(src_h, 3.0 * fh)
    bw = min(src_w, bh * 4.0 / 3.0)
    x = max(0, min(src_w - bw, cx - bw / 2.0))
    y = max(0, min(src_h - bh, cy - bh * 0.45))
    return {"x": int(x), "y": int(y), "w": int(bw), "h": int(bh), "shape": "rect"}


def split_box(face_cx, face_cy, face_h, src_w: int, src_h: int, x_lo: int = 0, x_hi: int = None):
    """Calculates a 9:8 vertical box around a person's face for split-screen stacked layout."""
    if x_hi is None:
        x_hi = src_w
    bh = min(src_h, max(face_h * src_h * 2.5, src_h * 0.50))
    bw = min(x_hi - x_lo, bh * W / (H / 2.0))
    bh = bw * (H / 2.0) / W
    x = min(max(face_cx * src_w - bw / 2.0, x_lo), x_hi - bw)
    y = min(max(face_cy * src_h - bh * 0.42, 0), src_h - bh)
    return int(x) // 2 * 2, int(y) // 2 * 2, int(bw) // 2 * 2, int(bh) // 2 * 2


def detect_podcast_faces(video_path, start: float, duration: float, src_w: int, src_h: int):
    """Detects if a clip is a 2-person podcast / interview shot.
    Returns {'top': (x, y, w, h), 'bottom': (x, y, w, h)} in source pixels, or None.
    """
    frames = _sample_frames(video_path, start, duration, n=12)
    if len(frames) < 4:
        return None

    cluster_left, cluster_right = [], []
    for f in frames:
        det = detect_faces_in_frame(f)
        for d in det:
            cx, cy, bw, bh, score = d
            # Must be a reasonably prominent face
            if bh >= 0.08:
                if cx < 0.48:
                    cluster_left.append((cx, cy, bh))
                elif cx > 0.52:
                    cluster_right.append((cx, cy, bh))

    # A two-person podcast has both left person and right person consistently present
    min_hits = max(2, len(frames) // 3)
    if len(cluster_left) >= min_hits and len(cluster_right) >= min_hits:
        left_med = np.median(np.array(cluster_left), axis=0)
        right_med = np.median(np.array(cluster_right), axis=0)

        mid = src_w // 2
        box_left = split_box(left_med[0], left_med[1], left_med[2], src_w, src_h, 0, mid)
        box_right = split_box(right_med[0], right_med[1], right_med[2], src_w, src_h, mid, src_w)

        # Left person on top panel, right person on bottom panel
        return {"top": box_left, "bottom": box_right, "left": box_left, "right": box_right}

    return None


def build_facecam_filter(cam: dict, src_w: int, src_h: int, fps: int = 30):
    """ffmpeg filter: gameplay on top (1150px), webcam enlarged at bottom over blurred game."""
    top_h = 1150
    bot_h = H - top_h  # 770
    gw = min(src_w, int(src_h * W / top_h) // 2 * 2)
    gx = (src_w - gw) // 2

    # Avoid duplicating facecam in the top gameplay crop if possible
    if cam["x"] < gx + gw and cam["x"] + cam["w"] > gx:
        is_right = (cam["x"] + cam["w"] / 2.0) > (src_w / 2.0)
        if is_right:
            gx = max(0, min(int(cam["x"]) - gw, gx))
        else:
            gx = min(src_w - gw, max(int(cam["x"] + cam["w"]), gx))
    gx = gx // 2 * 2

    room_w = W - 120
    room_h = bot_h - 120
    scale = min(room_w / cam["w"], room_h / cam["h"])
    cw = int(cam["w"] * scale) // 2 * 2
    ch = int(cam["h"] * scale) // 2 * 2
    cam_x = (W - cw) // 2
    cam_y = (bot_h - ch) // 2

    cam_crop = f"crop={cam['w']}:{cam['h']}:{cam['x']}:{cam['y']},scale={cw}:{ch}:flags=lanczos"

    parts = [
        f"[0:v]fps={fps},split=3[fc_g][fc_b][fc_c]",
        f"[fc_g]crop={gw}:{src_h}:{gx}:0,scale={W}:{top_h}:flags=lanczos,setsar=1[fc_top]",
        f"[fc_b]scale={W}:{bot_h}:force_original_aspect_ratio=increase,crop={W}:{bot_h},"
        f"boxblur=30:3,eq=brightness=-0.14[fc_bg]",
        f"[fc_c]{cam_crop},setsar=1[fc_cam]",
        f"[fc_bg][fc_cam]overlay={cam_x}:{cam_y}[fc_bot]",
        f"[fc_top][fc_bot]vstack=inputs=2,setsar=1[v0];"
    ]
    return "".join(parts), top_h + 15, 180  # cap_y (at seam), hook_y (top of gameplay)


def build_split_filter(top_box, bot_box, src_w: int, src_h: int, fps: int = 30):
    """ffmpeg filter: podcast multicam split-screen (top panel 1080x960, bottom panel 1080x960)."""
    tx, ty, tw, th = top_box
    bx, by, bw, bh = bot_box
    half = H // 2  # 960

    parts = [
        f"[0:v]fps={fps},split=2[sp_t][sp_b]",
        f"[sp_t]crop={tw}:{th}:{tx}:{ty},scale={W}:{half}:flags=lanczos,setsar=1[sp_top]",
        f"[sp_b]crop={bw}:{bh}:{bx}:{by},scale={W}:{half}:flags=lanczos,setsar=1[sp_bot]",
        f"[sp_top][sp_bot]vstack=inputs=2,setsar=1[v0];"
    ]
    return "".join(parts), half + 10, 180  # cap_y (at center seam), hook_y (top)
