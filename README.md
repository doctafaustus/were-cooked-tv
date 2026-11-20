# were-cooked-tv

**Chef Chub** is a three.js cartoon chef cat who narrates our cooking videos as a VTuber overlay.
The cat is shared. Each video gets its own folder with its voice, mouth track, cue sheet and cut
list, and a few scripts take it from voiceover to a finished TikTok in DaVinci Resolve.

```
chef-chub-pro.html        the cat on his own (lip sync, actions, transparent/green recording)
chef-chub-tiktok.html     the cat in a true 1080x1920 frame over the video, driven by the cue sheet
tools/                    voice -> mouth track, frame collector, overlay encoder (Python 3)
resolve/                  DaVinci Resolve scripts: build the cut, place the overlay, render, back up
videos/<name>/            one folder per video (see below)
videos/local.example.js   template for each video's machine-specific paths
```

Open a page straight from disk; no server is needed. `?video=<name>` picks the folder, with
`crispy-cranberry-chicken` as the default:
`chef-chub-tiktok.html?video=crispy-cranberry-chicken`

## A video folder

| File | What it is | Made by |
|---|---|---|
| `video.js` | title, voice file and name, fps / frame count, Resolve project and timeline names, output file names, how Whisper writes numbers | you |
| `local.js` | **this machine's paths** (background video, output folder, backup folder). Git-ignored; copy `videos/local.example.js` | you |
| `script.txt` | the exact words the voice says | you |
| `voice.mp3` | the character voiceover | AI Studio + ElevenLabs (below) |
| `words.json` | word timings | `tools/whisper_words.py` |
| `lipsync.js` | baked mouth track (loudness + open/wide/round/teeth/tongue, 100 frames/s) | `tools/bake_visemes.py` |
| `cues.js` | when he's on screen and where, glances at the dish, actions on words | you (see the comments inside) |
| `cut.json` | the shot list that rebuilds the Resolve timeline to fit the voice | you |

**Not in the repo:** rendered videos, the overlay .mov, frame folders and Resolve backups stay on
disk (see `.gitignore`), and `local.js` keeps machine paths out of this public repo.

## Requirements

- **Python 3** with `numpy`, `scipy` and `faster-whisper`, plus **ffmpeg** on PATH, for `tools/`.
- **DaVinci Resolve Studio**, running with external scripting set to Local, for `resolve/`. Resolve's
  scripting module needs a Python version it supports; here that's **Python 3.10**
  (`py -3.10 resolve/...`). Set `RESOLVE_SCRIPT_API_MODULES` if Resolve lives somewhere unusual.
- Chrome for the pages.

## New video checklist

`<v>` is the folder name, e.g. `my-new-recipe`.

1. **Folder.** Copy `videos/crispy-cranberry-chicken/` to `videos/<v>/`, keeping `video.js` and
   `local.js` and clearing the rest. Edit `video.js` (title, Resolve names, output names) and
   `local.js` (paths).
2. **Script.** Write `script.txt`: about **145 words per 57 s** (AI voices run about 150 words a
   minute), following the shots in order, cheeky but **cheerful, not snobby**, and with numbers
   spelled the way they're said ("eight eighty-four").
3. **Emotional read: Google AI Studio.** Go to https://aistudio.google.com/generate-speech and
   choose *Create new dialog*.
   - Model: **Gemini 3.8 Flash TTS** (`gemini-3.8-flash-tts`).
   - Voice: **Fola** ("clear and friendly"). The low **Mako** read came out snobbish.
   - Style we used: *Happy, cheerful, bubbly cartoon cat chef who is genuinely excited to share a
     cheap, delicious recipe with a friend. Warm, friendly and playful with a big smile in the
     voice, like a fun kids' show host. Cheeky jokes are delivered with a giggle and a wink, never
     snobby, sarcastic or condescending. Bright, upbeat energy and a quick, bouncy TikTok pace with
     no long pauses.*
   - Paste the script. Inline tags work (type `<`: `<laugh>`, `<cheer>`…).
   - Run it, then download the .wav.
4. **Character voice: ElevenLabs Voice Changer** (sidebar → *Voice Changer*).
   - Upload the AI Studio .wav and pick the voice. Ours is **Ziggy - Cute little Australian
     character** from the Voice Library.
   - Model: **Eleven English v2**, with default settings.
   - Voices with a **lock icon** need a paid plan.
   - Save the result as `videos/<v>/voice.mp3`.
5. **Mouth track.**
   ```bash
   python tools/whisper_words.py <v>     # faster-whisper small.en, CPU -> words.json
   python tools/bake_visemes.py <v>      # script + timings + loudness -> lipsync.js
   ```
   Whisper mishears the character voice; that's fine, because only its timings are used. If it
   writes digits ("$40", "10"), map them in `video.js` → `whisperNumbers`.
6. **Re-cut the video to the voice (Resolve).** Keep the voice as recorded; trim, move or drop
   shots instead. In `cut.json`, each entry points at a clip on the source timeline (`"video1:4"` =
   5th clip on V1) and gives its new start and end, plus optional `offset`, `props` (e.g.
   `{"FlipX": true}` to mirror a shot so the cat's corner is clear) or `media` (swap in another
   media-pool clip, like a quieter music bed). Then:
   ```bash
   py -3.10 resolve/backup.py <v>
   py -3.10 resolve/build_cut.py <v>                 # new timeline; the source is never touched
   py -3.10 resolve/render.py <v> background         # mp4 without the cat, for the page preview
   ```
7. **Cue sheet.** Edit `cues.js` while previewing `chef-chub-tiktok.html?video=<v>` (**Speak**
   plays voice + background; the scrub bar jumps around).
   - Prefer the **bottom-left** corner: TikTok's buttons run down the right side.
   - Hide him while notes, logos or hands are busy.
   - Have him **glance at the dish** now and then.
   - Keep the sparkle kiss to once a video.
   - Actions: `suspicious, surprised, wave, kiss, shake, shrug, proud, laugh, point, pan`.
8. **Render the cat.**
   ```bash
   python tools/frame_collector.py <v>       # leave running
   ```
   Click **Render frames** on the page. Every frame is rendered at exact timing, so it can't
   stutter the way a live screen recording can. Then:
   ```bash
   python tools/encode_overlay.py <v>        # frames -> ProRes 4444 .mov with alpha
   py -3.10 resolve/place_overlay.py <v>     # on the "Chef Chub" track at frame 0
   py -3.10 resolve/render.py <v> final      # the finished TikTok
   ```
   To redo the cat after cue changes, bump `outputNames.overlay` (e.g. `v3`), then repeat this step
   with `render.py <v> final --replace`.

## How the mouth works

The page can't analyse a local mp3 live, because Chrome silences Web Audio for `file://` media, so
the mouth is baked ahead of time. His own "w" lip stays as the top of the mouth and only the jaw
moves. It's wider and flatter for "ee", narrower and rounder for "oo"/"oh", shut for m/b/p, with a
tongue on open vowels and "l"/"th". Loudness drives how far it opens, capped so he talks instead of
flapping.

## Notes

- The voice is AI-generated (Google AI Studio → ElevenLabs). Check both services' terms for how
  you're allowed to use and share their output on your plan.
- `PLAN-ziggy-sync.md` is the planning note from the first video; safe to delete.
