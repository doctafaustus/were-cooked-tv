# Plan: sync Chef Chub to the Crispy Cranberry Chicken TikTok (temporary)

Status: **planned, not started**. Two questions are open (see the end).

Inputs:
- `ziggy.mp3`: the voiceover, 52.1 s.
- The video: `Crispy Cranberry Chicken TikTok.mp4` (in the Videos folder), 1080×1920, 24 fps, 57.6 s.
- The shot list: the DaVinci Resolve project "Crispy Cranberry Chicken - TikTok", Timeline 1, 44 shots on V1.
- The word timings: faster-whisper `small.en` on `ziggy.mp3`.

## What's wrong now

Ziggy and the video drift apart as the video goes on:

| Beat | In the video | Ziggy says it | Off by |
|---|---|---|---|
| Grocery items (chicken, beans, cranberry, lemon, garlic, shallot) | pickups at 5.38 / 6.71 / 8.04 / 9.38 / 10.71 / 12.04 s | 7.84 / 9.38 / 10.16 / 11.32 / 11.82 / 13.64 s | 1.5–2.5 s late, uneven |
| "$8.84" | tally note 13.38–15.50 s | 14.46 s | about right |
| Pantry staples | 16.96–20.12 s (receipt note from 18.33 s) | 16.14 s | about right |
| Breaking the leg quarters | 21.17 s | 19.20 s | 2 s early |
| Drumsticks into the oven | 25.38 s | 23.88 s | 1.5 s early |
| Sear thighs | 27.50 s | 25.64 s | 2 s early |
| Glaze | 31.62 s | 28.72 s | 3 s early |
| Pan sauce | ~37.8 s | 33.38 s | 4 s early |
| Beans | 41.33 s | 35.50 s | 6 s early |
| Plating | 46.38 s | 39.36 s | 7 s early |
| Outro | hero shot 52.46 s | 44.84 s | 7.6 s early |

Ziggy runs 52 s and the video runs 57.6 s, so there are about 5.6 s of room to spend on pauses.

Shot list (V1, seconds), for reference:

| Seconds | Shot |
|---|---|
| 0–2.50 | hero plates |
| 2.50–4.33 | Bangers on a Budget logo |
| 4.33–5.38 | HEB store |
| 5.38–13.38 | grocery pickups (six items, about 1.33 s each, each with a grocery note and a beep) |
| 13.38–15.50 | checkout tally note |
| 15.50–16.96 | ingredients |
| 16.96–20.12 | pantry |
| 20.12–21.17 | oven on |
| 21.17–25.38 | breaking the leg quarters |
| 25.38–27.50 | drumsticks and oven |
| 27.50–31.62 | sear |
| 31.62–36.67 | glaze |
| 36.67–41.33 | glaze and pan sauce |
| 41.33–46.38 | beans and blend |
| 46.38–52.46 | plating |
| 52.46–57.62 | hero ending |

## 1. Re-time the voice to the shots (same take, no new recording)

- Cut `ziggy.mp3` into phrase clips at natural gaps between words, using energy minima.
- Place each clip at its shot with a small lead, and fill the gaps with silence. These are the
  artificial pauses.
- Store items: put each item word on its hand pickup (same approach as the earlier human voiceover).
- Output **`ziggy-timed.wav`**, exactly 57.6 s and aligned to frame 0 of the TikTok.
- Re-run Whisper and `bake_visemes.py` on the new file so the lips match.

## 2. A cue sheet that drives the cat

- **`ziggy-cues.js`**: a time-ordered list of `{ t, visible, x, y, size, look, act }`.
- The page eases between cues during playback and recording, so every take is identical and
  tweakable one line at a time.

## 3. Placement: chest-up, and off screen when he'd cover the action

- **Framing:** head and chest, cropped by the bottom edge like a streamer cam. Bust about 45–55% of
  the frame height. Keep his face above TikTok's caption zone (bottom ~18%) and away from the
  right-hand button column.
- **Side per shot:** pull one frame per shot (44) and put him on the side away from the food and hands.
- **Entrances and exits:** pop up from the bottom edge and slide back down, never hard cuts.
- **Draft schedule:**
  - **Intro (0–5.4 s):** big, center-bottom. Pop-in wave on "forty-dollar plate", head shake on
    "Nope!".
  - **Store items and tally (5.4–15.5 s):** off screen, because the pickups and grocery notes are
    busy. *(Open question 2.)*
  - **Pantry (17–20 s):** small corner peek, ducking out when the receipt note appears at 18.33 s.
  - **Cooking (20–46 s):** chest-up, swapping sides with the action, with short off-screen breaks in
    the busiest shots.
  - **Plating (46–52 s):** off screen or a small corner peek.
  - **Outro (52.5–57.6 s):** big again. Chef's kiss on "fancy", wave on "Follow", laugh bounce at
    the end.

## 4. Less stiff: new animations

- **Always on:**
  - a bouncier idle with weight shifts and head tilts
  - eye darts, looking at the food, then back at the camera
  - occasional ear twitches
  - paw gestures on stressed words
- **On cue:**
  - pop-in hello wave
  - "Nope!" head shake
  - pointing at the food
  - proud chin-up on prices
  - happy squint on jokes
  - chef's kiss ("gorgeous", "fancy now")
  - laugh bounce
  - wave goodbye
  - duck down / pop up

## 5. What you'll get

- `ziggy-timed.wav` for the timeline.
- A 1080×1920 transparent recording of the cat that follows the cue sheet.
- Both start at frame 0 on the TikTok timeline in Resolve.

## Open questions

1. **Re-time the existing take or make a new one?** The recommendation is to cut and space the
   current `ziggy.mp3`, since it keeps the voice. The alternative is a new AI Studio read paced to
   the shots.
2. **Off screen during the store items (5.4–15.5 s)?** The recommendation is yes. The alternative
   is a small peek.
