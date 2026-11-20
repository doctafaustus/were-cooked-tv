"""Shared helpers for the DaVinci Resolve scripts (run them while Resolve is open).

Resolve's scripting module needs a Python it supports; on this machine that's Python 3.10:
    py -3.10 resolve/build_cut.py crispy-cranberry-chicken
Set RESOLVE_SCRIPT_API_MODULES if Resolve's Modules folder is somewhere else.
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from chub_config import load, need_local  # noqa: E402  (re-exported for the scripts)

MODULES = os.environ.get("RESOLVE_SCRIPT_API_MODULES",
                         r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
sys.path.append(MODULES)

FPS = 24


def F(seconds):
    """Seconds -> timeline frames."""
    return int(round(seconds * FPS))


def connect(cfg):
    """Resolve, project manager, project; insists the video's project is the one open."""
    import DaVinciResolveScript as dvr
    r = dvr.scriptapp("Resolve")
    if r is None:
        sys.exit("can't reach DaVinci Resolve; is it running (Preferences > General > external scripting: Local)?")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    want = cfg["resolve"]["project"]
    if p is None or p.GetName() != want:
        sys.exit(f'open the project "{want}" in Resolve first (current: {p.GetName() if p else None})')
    return r, pm, p


def timelines(p):
    return {p.GetTimelineByIndex(i + 1).GetName(): p.GetTimelineByIndex(i + 1) for i in range(p.GetTimelineCount())}


def timeline(p, name):
    t = timelines(p).get(name)
    if t is None:
        sys.exit(f'no timeline called "{name}" in {p.GetName()}')
    return t


def pool_clips(mp):
    out = []
    def walk(f):
        out.extend(f.GetClipList() or [])
        for s in f.GetSubFolderList() or []:
            walk(s)
    walk(mp.GetRootFolder())
    return out


def sorted_items(t, kind, track):
    return sorted(t.GetItemListInTrack(kind, track) or [], key=lambda i: i.GetStart())


def backup(cfg, pm, p):
    """Save, then export a dated .drp to backupDir (same-day backups get b, c, d...)."""
    folder = need_local(cfg, "backupDir")
    base = os.path.join(folder, f"{p.GetName()} backup {datetime.date.today().isoformat()}")
    out = base + ".drp"
    for suffix in "bcdefghijklmnop":
        if not os.path.exists(out):
            break
        out = f"{base} {suffix}.drp"
    pm.SaveProject()
    if not pm.ExportProject(p.GetName(), out, False):
        sys.exit("backup export failed")
    print("backup:", out)
    return out


def render(p, t, out_dir, name, disable_video_tracks=()):
    """Render a timeline to <out_dir>/<name>.mp4 (H.264, 1080x1920 as the timeline is set)."""
    p.SetCurrentTimeline(t)
    was = {k: t.GetIsTrackEnabled("video", k) for k in disable_video_tracks}
    for k in disable_video_tracks:
        t.SetTrackEnable("video", k, False)
    try:
        p.SetCurrentRenderFormatAndCodec("mp4", "H264")
        p.SetRenderSettings({"SelectAllFrames": True, "TargetDir": out_dir, "CustomName": name,
                             "ExportVideo": True, "ExportAudio": True})
        job = p.AddRenderJob()
        p.StartRendering([job], False)
        import time
        while p.IsRenderingInProgress():
            time.sleep(2)
        status = p.GetRenderJobStatus(job)
        p.DeleteRenderJob(job)
    finally:
        for k, v in was.items():
            t.SetTrackEnable("video", k, v)
    print("render:", os.path.join(out_dir, name + ".mp4"), status.get("JobStatus"))
    return status
