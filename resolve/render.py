"""Render the video's timeline.

    py -3.10 resolve/render.py crispy-cranberry-chicken background   # no cat: the page's preview background
    py -3.10 resolve/render.py crispy-cranberry-chicken final        # with the cat: the one to post

Writes <outputDir>/<outputNames.background|final>.mp4. Refuses to overwrite: delete or rename the
old file first (or pass --replace).
"""
import os
import sys

from resolve_common import connect, load, need_local, render, timeline


def main():
    args = [a for a in sys.argv[1:] if a != "--replace"]
    replace = "--replace" in sys.argv
    if len(args) < 2 or args[1] not in ("background", "final"):
        sys.exit(__doc__)
    cfg = load(args[0])
    which = args[1]
    out_dir = need_local(cfg, "outputDir")
    name = cfg["outputNames"][which]
    target = os.path.join(out_dir, name + ".mp4")
    if os.path.exists(target):
        if not replace:
            sys.exit(f"{target} exists; pass --replace to overwrite it")
        os.remove(target)
    r, pm, p = connect(cfg)
    t = timeline(p, cfg["resolve"]["timeline"])
    overlay = cfg["resolve"].get("overlayTrackName")
    hide = [k for k in range(1, t.GetTrackCount("video") + 1) if t.GetTrackName("video", k) == overlay] \
        if which == "background" else []
    render(p, t, out_dir, name, disable_video_tracks=hide)


if __name__ == "__main__":
    main()
