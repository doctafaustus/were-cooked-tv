"""Build a new timeline from a cut list: videos/<name>/cut.json.

    py -3.10 resolve/build_cut.py crispy-cranberry-chicken [--name "Some other timeline name"]

The new timeline is a duplicate of the source timeline (same format and tracks), emptied and
refilled from cut.json. The source timeline is only read, never changed. Refuses to run if a
timeline with the new name already exists.

cut.json: { "clips": [ {
    "src":   "video1:4"      track + index (time order) of an item on the SOURCE timeline,
    "track": "video1"        where it goes on the new timeline (video1..N / audio1..N),
    "start": 7.458, "end": 8.417     new position, seconds,
    "offset": 0.0            optional: seconds further into the source clip than the source item starts,
    "props": {"FlipX": true} optional: transform overrides (the source item's transform is copied first),
    "media": "name.wav"      optional: use this media-pool clip instead of the source item's media
  }, ... ] }
The source item's LUT (node 1) and transform carry over. The video's voice goes on resolve.voiceTrack.
"""
import json
import math
import os
import sys

from resolve_common import F, connect, load, pool_clips, sorted_items, timeline, timelines

PK = ["ZoomX", "ZoomY", "Pan", "Tilt", "RotationAngle", "FlipX", "FlipY", "CropLeft", "CropRight", "CropTop", "CropBottom"]


def main():
    args = sys.argv[1:]
    name_override = None
    if "--name" in args:
        i = args.index("--name"); name_override = args[i + 1]; del args[i:i + 2]
    cfg = load(args[0] if args else "crispy-cranberry-chicken")
    cut = json.load(open(os.path.join(cfg["dir"], "cut.json"), encoding="utf-8"))
    r, pm, p = connect(cfg)
    mp = p.GetMediaPool()
    new_name = name_override or cfg["resolve"]["timeline"]
    if new_name in timelines(p):
        sys.exit(f'timeline "{new_name}" already exists; delete it in Resolve or pass --name')
    src_t = timeline(p, cfg["resolve"]["sourceTimeline"])

    cache = {}
    def source(ref):
        if ref not in cache:
            kind_track, idx = ref.split(":")
            kind, track = kind_track.rstrip("0123456789"), int(kind_track[len(kind_track.rstrip("0123456789")):])
            it = sorted_items(src_t, kind, track)[int(idx)]
            g = it.GetNodeGraph() if kind == "video" else None
            cache[ref] = dict(mp=it.GetMediaPoolItem(), lo=it.GetLeftOffset(), kind=kind,
                              props={k: it.GetProperty(k) for k in PK} if kind == "video" else {},
                              lut=(g.GetLUT(1) if g and g.GetNumNodes() else ""))
        return cache[ref]
    pool = {c.GetName(): c for c in pool_clips(mp)}

    t = src_t.DuplicateTimeline(new_name)
    if not t:
        sys.exit("couldn't duplicate the source timeline")
    p.SetCurrentTimeline(t)
    st = t.GetStartFrame()
    for kind in ("video", "audio"):
        for tr in range(1, t.GetTrackCount(kind) + 1):
            its = t.GetItemListInTrack(kind, tr) or []
            if its:
                t.DeleteClips(its, False)
    for tr in range(1, t.GetTrackCount("audio") + 1):
        t.SetTrackEnable("audio", tr, True)

    def put(m, sf, n, track, rec, want, mtype):
        got = None
        for _ in range(6):
            it = mp.AppendToTimeline([{"mediaPoolItem": m, "startFrame": sf, "endFrame": sf + n,
                                       "trackIndex": track, "recordFrame": st + rec, "mediaType": mtype}])[0]
            got = it.GetEnd() - st
            if got == want:
                return it
            t.DeleteClips([it], False)
            n += 1 if got < want else -1
        sys.exit(f"couldn't get {m.GetName()} to {want - rec} frames (got {got - rec})")

    placed = 0
    for c in cut["clips"]:
        s = source(c["src"])
        kind = c["track"].rstrip("0123456789"); track = int(c["track"][len(kind):])
        m = pool[c["media"]] if c.get("media") else s["mp"]
        a, b = F(c["start"]), F(c["end"])
        if m.GetClipProperty("Frames") == "1":                       # a still: length comes from mark in/out
            m.SetMarkInOut(0, b - a)
            it = mp.AppendToTimeline([{"mediaPoolItem": m, "startFrame": 0, "endFrame": b - a, "trackIndex": track,
                                       "recordFrame": st + a, "mediaType": 1}])[0]
            m.ClearMarkInOut()
        else:
            fps = float(m.GetClipProperty("FPS") or 24)
            sf = round((s["lo"] / 24 + c.get("offset", 0.0)) * fps)
            it = put(m, sf, math.ceil((b - a) * fps / 24), track, a, b, 1 if kind == "video" else 2)
        for k, v in {**s["props"], **c.get("props", {})}.items():
            if v is not None:
                it.SetProperty(k, v)
        if kind == "video" and s["lut"]:
            it.GetNodeGraph().SetLUT(1, s["lut"])
        placed += 1

    voice = next((v for v in pool.values() if os.path.normcase(v.GetClipProperty("File Path") or "") ==
                  os.path.normcase(cfg["voicePath"])), None) or mp.ImportMedia([cfg["voicePath"]])[0]
    mp.AppendToTimeline([{"mediaPoolItem": voice, "trackIndex": cfg["resolve"]["voiceTrack"],
                          "recordFrame": st, "mediaType": 2}])
    print(f'built "{new_name}": {placed} clips + voice, {(t.GetEndFrame() - st) / 24:.2f} s')
    pm.SaveProject()


if __name__ == "__main__":
    main()
