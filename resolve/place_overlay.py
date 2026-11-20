"""Put the cat overlay (.mov from tools/encode_overlay.py) on the top video track at frame 0.

    py -3.10 resolve/place_overlay.py crispy-cranberry-chicken

Uses the track named resolve.overlayTrackName ("Chef Chub"), adding it if needed. If an older
overlay is already there it's taken off the timeline (the old file stays on disk).
"""
import os
import sys

from resolve_common import connect, load, need_local, pool_clips, timeline


def main():
    cfg = load(sys.argv[1] if len(sys.argv) > 1 else "crispy-cranberry-chicken")
    path = os.path.join(need_local(cfg, "outputDir"), cfg["outputNames"]["overlay"])
    if not os.path.isfile(path):
        sys.exit(f"no overlay at {path}; run tools/encode_overlay.py first")
    r, pm, p = connect(cfg)
    mp = p.GetMediaPool()
    t = timeline(p, cfg["resolve"]["timeline"])
    p.SetCurrentTimeline(t)
    st = t.GetStartFrame()
    name = cfg["resolve"].get("overlayTrackName", "Overlay")
    track = next((k for k in range(1, t.GetTrackCount("video") + 1) if t.GetTrackName("video", k) == name), None)
    if track is None:
        t.AddTrack("video")
        track = t.GetTrackCount("video")
        t.SetTrackName("video", track, name)
    old = t.GetItemListInTrack("video", track) or []
    if old:
        print("taking off:", ", ".join(i.GetName() for i in old))
        t.DeleteClips(old, False)
    m = next((c for c in pool_clips(mp) if os.path.normcase(c.GetClipProperty("File Path") or "") == os.path.normcase(path)), None) \
        or mp.ImportMedia([path])[0]
    n = int(m.GetClipProperty("Frames"))
    it = mp.AppendToTimeline([{"mediaPoolItem": m, "startFrame": 0, "endFrame": n, "trackIndex": track,
                               "recordFrame": st, "mediaType": 1}])[0]
    print(f'V{track} "{name}": {it.GetName()} frames {it.GetStart() - st}-{it.GetEnd() - st} '
          f'(timeline {t.GetEndFrame() - st}), alpha {m.GetClipProperty("Alpha mode")}')
    pm.SaveProject()


if __name__ == "__main__":
    main()
