"""Bake a video's mouth track: videos/<name>/{voice.mp3, script.txt, words.json} -> lipsync.js

    python tools/bake_visemes.py crispy-cranberry-chicken

The script words are lined up with Whisper's word timings (words.json, from whisper_words.py),
spelled out into rough mouth shapes, blended over time, and the jaw is scaled by the real
loudness so it opens wider on stressed syllables. Digits Whisper writes ("$40", "10") are mapped
to spoken words with "whisperNumbers" in video.js.
"""
import json, os, re, subprocess, sys, difflib
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.ndimage import gaussian_filter1d

from chub_config import load

CFG = load(sys.argv[1] if len(sys.argv) > 1 else "crispy-cranberry-chicken")
AUDIO = CFG["voicePath"]
WORDS = os.path.join(CFG["dir"], "words.json")
OUT = os.path.join(CFG["dir"], "lipsync.js")
SCRIPT = open(os.path.join(CFG["dir"], "script.txt"), encoding="utf-8").read().strip()
FPS = 100

# ---------- loudness (same voice band + dB scale as the live analyser) ----------
sr = 44100
raw = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '2', '-i', AUDIO, '-ac', '1', '-ar', str(sr),
                      '-f', 'f32le', '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.float32).astype(np.float64)
x = sosfilt(butter(2, [180, 3800], btype='band', fs=sr, output='sos'), x)
N = int(len(x) / sr * FPS) + 1
hop, win = sr // FPS, 1024
loud = np.zeros(N)
for f in range(N):
    seg = x[max(0, f * hop - win // 2): f * hop + win // 2]
    if len(seg):
        loud[f] = np.clip((20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-6) + 52) / 34, 0, 1)

# ---------- align script words to whisper timings ----------
norm = lambda w: re.sub(r"[^a-z']", "", w.lower())
script = [t for t in re.findall(r"[A-Za-z']+", SCRIPT.replace('-', ' '))]
NUM = {k.lower(): v for k, v in CFG.get('whisperNumbers', {}).items()}
wh = []
for s, e, w in json.load(open(WORDS, encoding='utf-8')):
    k = w.lower().strip('.,?!')
    parts = NUM.get(k) or [p for p in re.findall(r"[a-z']+", k)] or [k]
    step = (e - s) / len(parts)
    for i, p in enumerate(parts):
        wh.append([s + i * step, s + (i + 1) * step, p])
A, B = [norm(w) for w in script], [norm(w[2]) for w in wh]
timed = [None] * len(script)
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
    if tag == 'equal':
        for k in range(i2 - i1):
            timed[i1 + k] = (wh[j1 + k][0], wh[j1 + k][1])
    elif tag == 'replace':
        s, e = wh[j1][0], wh[j2 - 1][1]
        lens = [max(2, len(A[i])) for i in range(i1, i2)]
        tot, acc = sum(lens), s
        for k, i in enumerate(range(i1, i2)):
            d = (e - s) * lens[k] / tot
            timed[i] = (acc, acc + d); acc += d
# script words whisper dropped: squeeze them in between their neighbours
for i in range(len(timed)):
    if timed[i] is None:
        j = i
        while j < len(timed) and timed[j] is None: j += 1
        s = timed[i - 1][1] if i > 0 else 0.0
        e = timed[j][0] if j < len(timed) else s + 0.3 * (j - i)
        if e - s < 0.08 * (j - i):
            e = s + 0.08 * (j - i)
        for k in range(i, j):
            timed[k] = (s + (e - s) * (k - i) / (j - i), s + (e - s) * (k - i + 1) / (j - i))

# ---------- spelling -> mouth-shape units ----------
#            open  wide  round teeth tongue
V = {'REST': (0.00, 0.50, 0.00, 0.00, 0.00), 'MBP': (0.00, 0.45, 0.05, 0.00, 0.00),
     'FV':   (0.12, 0.55, 0.00, 1.00, 0.00), 'SS':  (0.16, 0.72, 0.00, 1.00, 0.00),
     'SH':   (0.24, 0.45, 0.60, 0.90, 0.00), 'TH':  (0.25, 0.60, 0.00, 0.60, 0.90),
     'L':    (0.40, 0.60, 0.00, 0.30, 1.00), 'KG':  (0.38, 0.55, 0.00, 0.20, 0.20),
     'R':    (0.30, 0.40, 0.55, 0.20, 0.00), 'AA':  (1.00, 0.65, 0.00, 0.15, 0.50),
     'UH':   (0.60, 0.55, 0.10, 0.10, 0.40), 'EH':  (0.65, 0.80, 0.00, 0.35, 0.25),
     'IH':   (0.45, 0.85, 0.00, 0.45, 0.15), 'EE':  (0.32, 1.00, 0.00, 0.75, 0.00),
     'OH':   (0.75, 0.30, 0.85, 0.00, 0.20), 'OO':  (0.40, 0.15, 1.00, 0.00, 0.00)}
MULTI = [('tch', ['SH']), ('sh', ['SH']), ('ch', ['SH']), ('th', ['TH']), ('ph', ['FV']), ('wh', ['OO']),
         ('ck', ['KG']), ('ng', ['KG']), ('qu', ['KG', 'OO']), ('oo', ['OO']), ('ee', ['EE']), ('ea', ['EE']),
         ('ie', ['EE']), ('ue', ['OO']), ('ui', ['OO']), ('ai', ['EH']), ('ay', ['EH']), ('oa', ['OH']),
         ('ou', ['OH']), ('ow', ['OH']), ('oi', ['OH', 'EE']), ('oy', ['OH', 'EE']), ('au', ['OH']), ('aw', ['OH']),
         ('er', ['R']), ('ur', ['R']), ('ir', ['R']), ('ar', ['AA', 'R']), ('or', ['OH', 'R'])]
ONE = {'a': 'AA', 'e': 'EH', 'i': 'IH', 'o': 'OH', 'u': 'UH', 'y': 'EE', 'm': 'MBP', 'b': 'MBP', 'p': 'MBP',
       'f': 'FV', 'v': 'FV', 's': 'SS', 'z': 'SS', 'c': 'SS', 'x': 'SS', 't': 'SS', 'd': 'SS', 'n': 'SS',
       'j': 'SH', 'l': 'L', 'r': 'R', 'w': 'OO', 'k': 'KG', 'g': 'KG', 'q': 'KG', 'h': 'KG'}
VOWELS = {'AA', 'UH', 'EH', 'IH', 'EE', 'OH', 'OO'}

def units(word):
    w = norm(word).replace("'", "")
    if len(w) > 2 and w.endswith('e') and w[-2] not in 'aeiouy':
        w = w[:-1]                                     # silent final e
    out, i = [], 0
    while i < len(w):
        for g, vs in MULTI:
            if w.startswith(g, i):
                out += vs; i += len(g); break
        else:
            if w[i] in ONE: out.append(ONE[w[i]])
            i += 1
    return out or ['UH']

# ---------- target track ----------
T = np.tile(np.array(V['REST']), (N, 1))
inword = np.zeros(N, bool)
closed = np.zeros(N)
for w, (s, e) in zip(script, timed):
    us = units(w)
    wt = np.array([2.2 if u in VOWELS else 1.2 if u == 'R' else 0.9 if u == 'MBP' else 1.0 for u in us])
    edges = s + (e - s) * np.concatenate([[0], np.cumsum(wt) / wt.sum()])
    for k, u in enumerate(us):
        a, b = int(edges[k] * FPS), max(int(edges[k] * FPS) + 1, int(edges[k + 1] * FPS))
        T[a:b] = V[u]
        inword[a:b] = True
        if u == 'MBP': closed[a:b] = 1
last_end = timed[-1][1]

# the laugh / anything after the script: an open "ha" shape that follows loudness
tail = np.arange(N) >= int(last_end * FPS) + 5
T[tail] = V['AA']

# coarticulation: soften the steps, then lead the audio slightly (mouths move before sound)
S = gaussian_filter1d(T, sigma=2.2, axis=0)
lead = 3
S = np.vstack([S[lead:], np.repeat(S[-1:], lead, 0)])
L = gaussian_filter1d(loud, 1.0)
L = np.concatenate([L[lead:], np.repeat(L[-1:], lead)])
iw = np.concatenate([inword[lead:], np.repeat(inword[-1:], lead)]) | tail
iw = gaussian_filter1d(iw.astype(float), 2.0)

# loudness drives the jaw (so it always moves when he's audible); the spelled-out shape
# scales it, and m/b/p squeeze it shut
C = gaussian_filter1d(closed, 1.5)
C = np.concatenate([C[lead:], np.repeat(C[-1:], lead)])
Lp = np.clip(L * 1.25, 0, 1) ** 0.85
jaw = Lp * (0.45 + 0.75 * S[:, 0]) * (1 - 0.75 * np.clip(C * 1.5, 0, 1))
jaw = np.where(tail, Lp * 0.9, jaw)
# talk, don't flap: never quite fully open, keep a sliver open inside words (only m/b/p and real
# pauses close it), and round off the syllable edges
inw = np.clip(iw * 1.4, 0, 1) * (1 - np.clip(C * 1.5, 0, 1))
jaw = np.maximum(np.minimum(0.8 * jaw, 0.82), 0.14 * inw * np.clip(L * 4, 0, 1))
jaw = gaussian_filter1d(jaw, 1.2)
q = lambda a: [int(round(v)) for v in np.clip(a, 0, 1) * 99]
out = {'fps': FPS, 'duration': round(len(x) / sr, 3), 'data': q(loud),
       'open': q(jaw), 'wide': q(S[:, 1]), 'round': q(S[:, 2]), 'teeth': q(S[:, 3] * np.clip(iw * 1.4 + Lp, 0, 1)),
       'tongue': q(S[:, 4] * np.clip(jaw * 2, 0, 1))}
open(OUT, 'w').write("// mouth track for " + os.path.basename(AUDIO) + ", 100 frames/s, values 0-99. Made by tools/bake_visemes.py.\n"
                     "// data = loudness (meter); open/wide/round/teeth/tongue = baked mouth shapes.\n"
                     "window.CHUB_LIPSYNC = " + json.dumps(out, separators=(',', ':')) + ";\n")
print('frames', N, 'words', len(script), 'last word ends', round(last_end, 2), '->', OUT)
for w, t in list(zip(script, timed))[:6] + list(zip(script, timed))[-4:]:
    print(w, [round(v, 2) for v in t], units(w))
