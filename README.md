# were-cooked-tv

**Chef Chub** is a three.js cartoon chef cat who narrates our cooking videos as a VTuber overlay.
This README covers how his voiceover was made and how to repeat it with a new script or voice.

| File | What it is |
|---|---|
| `chef-chub-pro.html` | The cat on his own: lip sync, actions, transparent/green recording |
| `chef-chub-tiktok.html` | The same cat in a true 1080×1920 TikTok frame over the video, with Size/X/Y placement |
| `ziggy.mp3` | The current voiceover (Crispy Cranberry Chicken TikTok, ~52 s) |
| `ziggy-lipsync.js` | Baked mouth track for `ziggy.mp3` (generated, don't hand-edit) |
| `bake_visemes.py` | Builds the mouth track from the audio plus the script text |

Open either page straight from disk. No server is needed.

---

## The voiceover pipeline

```
script  ->  Google AI Studio TTS (emotion)  ->  ElevenLabs Voice Changer (character voice)
        ->  Whisper word timings  ->  bake_visemes.py  ->  ziggy-lipsync.js  ->  the page
```

### 1. Write the script to length

- Aim for **about 145 words per 57 s** of video. AI voices talk at about 150 words a minute, so
  a 210-word script runs about 80 s.
- Follow the shots in order (store run, prices, oven, sear, glaze, pan sauce, beans, plating, outro).
- Keep it cheeky but **cheerful, not snobby**. Lines like "Please." and "show-off" came out
  condescending, so we swapped them for "Nope!" and dropped "show-off".
- Write numbers the way they should be said ("Eight eighty-four", "forty-dollar").

### 2. Generate the emotional read: Google AI Studio

ElevenLabs' straight text-to-speech sounded robotic with our voice, so the *performance* comes
from Gemini TTS and ElevenLabs only swaps the *voice* afterwards.

- Go to **https://aistudio.google.com/generate-speech** and choose **Create new dialog**.
- Model: **Gemini 3.8 Flash TTS** (`gemini-3.8-flash-tts`).
- Speaker voice: **Fola** ("Clear and friendly, medium pitch"). The low-pitched **Mako** read came
  out snobbish. The tone barely matters, since step 3 replaces it; pick the voice with the best
  *attitude*.
- **Style** (the box under the Style dropdown) we used:

  > Happy, cheerful, bubbly cartoon cat chef who is genuinely excited to share a cheap, delicious
  > recipe with a friend. Warm, friendly and playful with a big smile in the voice, like a fun
  > kids' show host. Cheeky jokes are delivered with a giggle and a wink, never snobby, sarcastic
  > or condescending. Bright, upbeat energy and a quick, bouncy TikTok pace with no long pauses.
  > Excited and proud on the prices, playfully silly on the jokes, sweet and cheeky on the last line.

- Paste the script into the speech box. Expression tags work inline: type `<` to see them
  (`<laugh>`, `<cheer>`, `<breath>`, …). We ended the script with `<laugh>`.
- Click **Run**, listen, and use the download arrow on the player. The file is saved as
  `Generated Audio <date> - <time>.wav`. Our take came out at 0:52.

### 3. Turn it into the character voice: ElevenLabs Voice Changer

- **https://elevenlabs.io/app/speech-synthesis/speech-to-speech** (sidebar → *Voice Changer*).
- Upload the AI Studio `.wav` and pick the character voice. For `ziggy.mp3` we used
  **Ziggy - Cute little Australian character** from the Voice Library.
- Model: **Eleven English v2** (the Voice Changer default), with default settings.
- **Free plan:** Voice Library voices with a **lock icon** say "Available on Starter plans and
  above", so skip those. Free-plan voices we liked for him: Little Dude II, Teddy Twinkle, Jayjay,
  Stevie - The Living Cartoon, Miffy Mouse, Ziggy, Minnie.
- Download the result as an mp3.

### 4. Bake the mouth track

The page can't analyse a local mp3 live, because Chrome silences Web Audio for `file://` media. So
the mouth movement is baked ahead of time. The bake lines the known script up against Whisper's
word timings (Whisper mishears the character voice, for example "quanberry", which is why the real
script is used), spells each word into mouth shapes, blends them, and scales the jaw by the actual
loudness.

Requirements: Python 3 with `numpy`, `scipy` and `faster-whisper`, plus `ffmpeg` on PATH.

1. Copy the new mp3 into this folder (replace `ziggy.mp3`, or see *Using a different file name*).
2. Get word timings with Whisper (**faster-whisper `small.en`**, CPU, int8):

   ```bash
   python -c "
   from faster_whisper import WhisperModel; import json
   m = WhisperModel('small.en', device='cpu', compute_type='int8', cpu_threads=2)
   segs, _ = m.transcribe('ziggy.mp3', beam_size=5, word_timestamps=True)
   json.dump([[w.start, w.end, w.word.strip()] for s in segs for w in s.words], open('words.json', 'w'))
   "
   ```

3. Edit `bake_visemes.py`:
   - `SCRIPT`: paste the exact script the voice reads.
   - `NUM`: map any digits Whisper writes (e.g. `'$40'`, `'10'`, `'8e4'`) to the spoken words.
4. Bake:

   ```bash
   python bake_visemes.py ziggy.mp3 words.json ziggy-lipsync.js
   ```

   It prints the first and last few words with their timings. Check that they look sensible.
   `words.json` is a scratch file and doesn't need committing.

The track holds, at 100 frames/s: `data` (loudness, for the meter) plus `open`, `wide`, `round`,
`teeth` and `tongue` (0–99). In the page, his own "w" lip stays as the top of the mouth and only
the jaw moves. It's wider and flatter for "ee", narrower and rounder for "oo"/"oh", shut for
m/b/p, and the tongue rises on open vowels and "l"/"th".

### 5. Preview and record

- Open `chef-chub-tiktok.html` and click **Speak Ziggy**. The voice, mouth and background video
  play together. Use **Size / X / Y** to place him and the scrub bar to check moments.
- Press **H** to hide the controls, then **Record**. It records **only the cat**, on a transparent
  background at 1080×1920, starting Ziggy from 0 and stopping at the end. The recording has no
  audio.
- In DaVinci Resolve, put the `.webm` on a track above the TikTok timeline at frame 0, and the mp3 at
  frame 0 on an audio track. If the transparency doesn't come through, either record with
  **Bg: Green** and key it, or convert to ProRes 4444 with alpha (use `libvpx` instead of
  `libvpx-vp9` if Chrome recorded VP8):

  ```bash
  ffmpeg -c:v libvpx-vp9 -i chef-chub-clear.webm -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le chef-chub.mov
  ```

### Using a different file name

`ziggy.mp3` and `ziggy-lipsync.js` are referenced by name in both HTML files (search for
`ziggy`). Either keep those names for the new take, or update the `<script src>` tag and the
`new Audio("ziggy.mp3")` line in both pages.

The background video path in `chef-chub-tiktok.html` is the `src` of `<video id="bgvid">`.
