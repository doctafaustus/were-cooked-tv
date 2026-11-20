"""Word timings for a video's voice: videos/<name>/voice.mp3 -> words.json

    python tools/whisper_words.py crispy-cranberry-chicken

Uses faster-whisper `small.en` on the CPU (int8). Whisper often mishears the character voice;
that's fine: bake_visemes.py only uses the timings and lines them up with script.txt.
"""
import json
import os
import sys

from chub_config import load


def main():
    cfg = load(sys.argv[1] if len(sys.argv) > 1 else "crispy-cranberry-chicken")
    from faster_whisper import WhisperModel
    model = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=2)
    segs, _ = model.transcribe(cfg["voicePath"], beam_size=5, word_timestamps=True, vad_filter=False)
    words = [[round(w.start, 3), round(w.end, 3), w.word.strip()] for s in segs for w in s.words]
    out = os.path.join(cfg["dir"], "words.json")
    json.dump(words, open(out, "w", encoding="utf-8"))
    print(f"{len(words)} words -> {out}")
    print(" ".join(w[2] for w in words))


if __name__ == "__main__":
    main()
