"""Export finished clips to a folder (such as a Google Drive synced folder) or upload via Google Drive API.

Settings saved in data/drive.json:
    folder_path: local path (e.g. G:\\My Drive\\clippedautoupload)
    enabled: True/False
    folder_id, key_file: optional Google Cloud Service Account settings for Workspace Shared Drives
"""
import base64
import json
import re
import shutil
import threading
import time
import traceback
from pathlib import Path

import httpx

from . import config, ctx, creators, jobs

_FILE = config.DATA_DIR / "drive.json"
_DEFAULT_KEY_FILE = config.DATA_DIR / "drive_key.json"
_lock = threading.Lock()
_saved = {"at": None, "data": {}}


def _clean_folder_id(val: str) -> str:
    """Extract raw folder ID from either a direct ID or a full drive link."""
    v = str(val or "").strip()
    m = re.search(r"folders/([a-zA-Z0-9_\-]+)", v)
    if m:
        return m.group(1)
    m2 = re.search(r"^[a-zA-Z0-9_\-]{15,100}$", v)
    if m2:
        return m2.group(0)
    return v


def _clean_filename(name: str) -> str:
    """Strip characters not allowed in Windows filenames."""
    clean = re.sub(r'[\/\\:*?"<>|]', "", str(name or "")).strip()
    return clean[:120] if clean else "clip"


# ---------------------------------------------------------------- settings
def _from_file() -> dict:
    try:
        at = _FILE.stat().st_mtime_ns
    except OSError:
        at = 0
    if _saved["at"] != at:
        try:
            data = json.loads(_FILE.read_text(encoding="utf-8")) if at else {}
        except (OSError, ValueError):
            data = {}
        _saved.update(at=at, data=data if isinstance(data, dict) else {})
    return _saved["data"]


def current() -> dict:
    d = _from_file()
    folder_path = d.get("folder_path")
    if folder_path is None:
        # Check default G:\My Drive\clippedautoupload
        default_p = Path(r"G:\My Drive\clippedautoupload")
        if default_p.is_dir():
            folder_path = str(default_p)
        else:
            folder_path = config.env("PEAKCUT_EXPORT_FOLDER", "").strip()

    key_file = d.get("key_file") or config.env("PEAKCUT_DRIVE_KEY_FILE", "").strip()
    if not key_file and _DEFAULT_KEY_FILE.is_file():
        key_file = str(_DEFAULT_KEY_FILE)
    folder_id = _clean_folder_id(d.get("folder_id") or config.env("PEAKCUT_DRIVE_FOLDER_ID", "").strip())
    enabled = d.get("enabled", config.env("PEAKCUT_DRIVE_ENABLED", "1") == "1")

    return {
        "folder_path": str(folder_path or "").strip(),
        "folder_id": folder_id,
        "key_file": key_file,
        "enabled": bool(enabled),
    }


def ready() -> bool:
    c = current()
    if not c["enabled"]:
        return False
    if c["folder_path"] and Path(c["folder_path"]).is_dir():
        return True
    return bool(c["folder_id"] and c["key_file"] and Path(c["key_file"]).is_file())


def _read_key_data(key_file: str = "") -> dict:
    c = current()
    target = Path(key_file) if key_file else (Path(c["key_file"]) if c["key_file"] else None)
    if not target or not target.is_file():
        raise ValueError("No service account key file found.")
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"Invalid JSON in key file: {e}")
    if not data.get("client_email") or not data.get("private_key"):
        raise ValueError("The key file is missing client_email or private_key.")
    return data


def public() -> dict:
    c = current()
    key_email = ""
    if c["key_file"] and Path(c["key_file"]).is_file():
        try:
            kd = _read_key_data(c["key_file"])
            key_email = kd.get("client_email", "")
        except Exception:
            pass
    path_ok = bool(c["folder_path"] and Path(c["folder_path"]).is_dir())
    return {
        "enabled": c["enabled"],
        "folder_path": c["folder_path"],
        "path_ok": path_ok,
        "folder_id": c["folder_id"],
        "has_key": bool(c["key_file"] and Path(c["key_file"]).is_file()),
        "key_hint": Path(c["key_file"]).name if c["key_file"] else "",
        "key_email": key_email,
        "ready": ready(),
    }


def save(folder_path: str = "", folder_id: str = "", key_file: str = "", key_json: str = "", enabled: bool = True) -> dict:
    folder_path = str(folder_path or "").strip()
    folder_id = _clean_folder_id(folder_id)
    key_file = str(key_file or "").strip()[:500]
    key_json = str(key_json or "").strip()

    if key_json:
        try:
            parsed = json.loads(key_json)
            if not isinstance(parsed, dict) or "client_email" not in parsed or "private_key" not in parsed:
                raise ValueError("JSON key must contain 'client_email' and 'private_key'.")
            _DEFAULT_KEY_FILE.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
            key_file = str(_DEFAULT_KEY_FILE)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON key: {e}")

    # Validate folder_path if provided
    if folder_path:
        p = Path(folder_path)
        try:
            p.mkdir(parents=True, exist_ok=True)
            # test write
            test_f = p / ".peakcut_test"
            test_f.write_text("ok", encoding="utf-8")
            test_f.unlink(missing_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot write to folder '{folder_path}': {e}")

    d = _from_file()
    d.update(folder_path=folder_path, folder_id=folder_id, enabled=bool(enabled))
    if key_file:
        d["key_file"] = key_file
    elif key_file == "" and "key_file" in d and not key_json:
        pass

    with _lock:
        _FILE.parent.mkdir(parents=True, exist_ok=True)
        _FILE.write_text(json.dumps(d, indent=2), encoding="utf-8")
        _saved["at"] = None

    return public()


def test_connection(folder_path: str = "") -> dict:
    c = current()
    check_path = folder_path.strip() if folder_path else c.get("folder_path")
    if check_path:
        p = Path(check_path)
        if not p.is_dir():
            raise ValueError(f"Folder '{check_path}' does not exist.")
        try:
            test_f = p / ".peakcut_test"
            test_f.write_text("ok", encoding="utf-8")
            test_f.unlink(missing_ok=True)
            return {"ok": True, "type": "folder", "name": p.name or str(p), "path": str(p.resolve())}
        except Exception as e:
            raise ValueError(f"Cannot write to '{check_path}': {e}")

    # Fall back to Google Cloud API check
    folder_id = c["folder_id"]
    if not folder_id:
        raise ValueError("Please provide a folder path or a Google Drive folder ID.")
    key_data = _read_key_data(c["key_file"])
    token = _access_token(key_data)

    r = httpx.get(
        f"https://www.googleapis.com/drive/v3/files/{folder_id}?fields=id,name,mimeType,capabilities&supportsAllDrives=true",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if r.status_code == 404:
        raise ValueError(f"Folder not found. Make sure you shared it with: {key_data.get('client_email')}")
    if r.status_code != 200:
        raise ValueError(f"Google Drive error (HTTP {r.status_code}): {r.text[:200]}")
    info = r.json()
    return {"ok": True, "type": "cloud", "name": info.get("name", "Drive Folder"), "email": key_data.get("client_email", "")}


# ---------------------------------------------------------------- Google Cloud JWT
def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _make_jwt(key_data: dict) -> str:
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
    except ImportError:
        raise RuntimeError("Install cryptography for Google Drive uploads.")

    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {
        "iss": key_data["client_email"],
        "scope": "https://www.googleapis.com/auth/drive",
        "aud": "https://oauth2.googleapis.com/token",
        "exp": now + 3600,
        "iat": now,
    }
    encoded_header = _b64url(json.dumps(header).encode("utf-8"))
    encoded_payload = _b64url(json.dumps(payload).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")

    pk = load_pem_private_key(key_data["private_key"].encode("utf-8"), password=None)
    sig = pk.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    return f"{encoded_header}.{encoded_payload}.{_b64url(sig)}"


_TOKEN_CACHE = {"token": "", "expires_at": 0}


def _access_token(key_data: dict) -> str:
    now = time.time()
    if _TOKEN_CACHE["token"] and _TOKEN_CACHE["expires_at"] > now + 60:
        return _TOKEN_CACHE["token"]

    jwt_token = _make_jwt(key_data)
    r = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": jwt_token,
        },
        timeout=15,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Google auth error ({r.status_code}): {r.text[:200]}")
    data = r.json()
    _TOKEN_CACHE["token"] = data["access_token"]
    _TOKEN_CACHE["expires_at"] = now + data.get("expires_in", 3600)
    return _TOKEN_CACHE["token"]


# ---------------------------------------------------------------- export one clip
def export_clip(job: dict, clip: dict) -> bool:
    """Copy or upload one finished clip directly into the destination folder (no subfolder)."""
    c = current()
    if not c.get("enabled"):
        return False

    job_dir = Path(job["dir"])
    clip_file = job_dir / "clips" / f"{clip['id']}.mp4"
    if not clip_file.is_file() and clip.get("file"):
        clip_file = job_dir / "clips" / clip["file"]
    if not clip_file.is_file():
        return False

    title = clip.get("title") or clip.get("hook") or clip.get("id", "clip")
    safe_name = _clean_filename(title)

    # 1. Local / Google Drive synced folder
    folder_path = c.get("folder_path")
    if folder_path:
        dest_dir = Path(folder_path)
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            target = dest_dir / f"{safe_name}.mp4"
            # Avoid same-file copy
            if target.is_file():
                try:
                    if target.samefile(clip_file):
                        return True
                except OSError:
                    pass
            shutil.copy2(clip_file, target)
            print(f"  Drive: saved {clip_file.name} -> {target.name}", flush=True)
            creators.log(job.get("creator"), f"Clip saved to Drive folder: {target.name}")
            return True
        except Exception:
            traceback.print_exc()
            print(f"  Drive: failed to copy {clip_file.name} to {dest_dir}", flush=True)

    # 2. Service account upload fallback
    if c.get("folder_id") and c.get("key_file") and Path(c["key_file"]).is_file():
        try:
            key_data = _read_key_data(c["key_file"])
            token = _access_token(key_data)
            meta = {"name": f"{safe_name}.mp4", "parents": [c["folder_id"]]}
            boundary = f"boundary_{int(time.time())}"
            data = clip_file.read_bytes()
            body = (
                f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(meta)}\r\n"
                f"--{boundary}\r\nContent-Type: video/mp4\r\n\r\n"
            ).encode("utf-8") + data + f"\r\n--{boundary}--\r\n".encode("utf-8")

            r = httpx.post(
                "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true",
                headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/related; boundary={boundary}"},
                content=body,
                timeout=60,
            )
            if r.status_code in (200, 201):
                creators.log(job.get("creator"), f"Clip uploaded to Google Drive: {safe_name}")
                return True
        except Exception:
            traceback.print_exc()

    return False


def export_all_existing() -> int:
    """Export all clips that have status == 'done' across all jobs to the folder."""
    all_j = jobs.all_jobs()
    count = 0
    for j in all_j:
        for c in j.get("clips", []):
            if c.get("status") == "done":
                if export_clip(j, c):
                    count += 1
    return count


def _on_clip_ready(job, clip):
    """Pipeline hook: runs automatically whenever a clip finishes."""
    if not ready():
        return

    def do():
        try:
            export_clip(job, clip)
        except Exception:
            traceback.print_exc()

    threading.Thread(target=do, daemon=True).start()


def start():
    jobs.on_clip_ready.append(_on_clip_ready)
