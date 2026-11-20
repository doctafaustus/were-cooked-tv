"""Read a video folder's config: videos/<name>/video.js (committed) + local.js (this machine, git-ignored).

Both files are `window.CHUB_X = { ...JSON... };` so the browser page and these Python tools share them.
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_js_object(path):
    text = open(path, encoding="utf-8").read()
    return json.loads(text[text.index("{"): text.rindex("}") + 1])


def video_dir(arg):
    """Accept a folder path or just the video name (e.g. crispy-cranberry-chicken)."""
    d = arg if os.path.isdir(arg) else os.path.join(REPO, "videos", arg)
    if not os.path.isfile(os.path.join(d, "video.js")):
        sys.exit(f"no video.js in {d}")
    return os.path.abspath(d)


def load(arg):
    d = video_dir(arg)
    cfg = _read_js_object(os.path.join(d, "video.js"))
    local_path = os.path.join(d, "local.js")
    cfg["local"] = _read_js_object(local_path) if os.path.isfile(local_path) else {}
    cfg["dir"] = d
    cfg["voicePath"] = os.path.join(d, cfg.get("voice", "voice.mp3"))
    return cfg


def need_local(cfg, key):
    v = cfg["local"].get(key)
    if not v:
        sys.exit(f"set \"{key}\" in {os.path.join(cfg['dir'], 'local.js')} (see videos/local.example.js)")
    return v
