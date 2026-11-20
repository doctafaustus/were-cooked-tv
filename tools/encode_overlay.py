"""Rendered PNG frames -> one ProRes 4444 .mov with alpha, ready for the top track in Resolve.

    python tools/encode_overlay.py crispy-cranberry-chicken

Reads <outputDir>/<outputNames.frames>/chub_%05d.png and writes <outputDir>/<outputNames.overlay>.
Refuses to overwrite an existing .mov (Resolve may be using it): bump the name in video.js instead.
"""
import os
import subprocess
import sys

from chub_config import load, need_local


def main():
    cfg = load(sys.argv[1] if len(sys.argv) > 1 else "crispy-cranberry-chicken")
    base = need_local(cfg, "outputDir")
    frames = os.path.join(base, cfg["outputNames"]["frames"])
    out = os.path.join(base, cfg["outputNames"]["overlay"])
    n = len([f for f in os.listdir(frames) if f.startswith("chub_") and f.endswith(".png")])
    want = cfg.get("frames")
    if want and n != want:
        sys.exit(f"{frames} has {n} frames, video.js expects {want}")
    if os.path.exists(out):
        sys.exit(f"{out} already exists; change outputNames.overlay in video.js (e.g. add v3)")
    subprocess.run(["ffmpeg", "-v", "error", "-threads", "2", "-framerate", str(cfg.get("fps", 24)),
                    "-i", os.path.join(frames, "chub_%05d.png"),
                    "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
                    "-alpha_bits", "16", "-vendor", "apl0", out], check=True)
    print(f"{n} frames -> {out}")


if __name__ == "__main__":
    main()
