"""Receives the cat's rendered frames from the page and saves them as PNGs.

    python tools/frame_collector.py crispy-cranberry-chicken

Then open chef-chub-tiktok.html?video=<name> and click "Render frames". Each transparent
1080x1920 frame is POSTed to http://127.0.0.1:8733/frame/NNNNN and saved as chub_NNNNN.png in
<outputDir>/<outputNames.frames> (see the video's local.js / video.js). Localhost only.
"""
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from chub_config import load, need_local

PORT = 8733


def main():
    cfg = load(sys.argv[1] if len(sys.argv) > 1 else "crispy-cranberry-chicken")
    out = os.path.join(need_local(cfg, "outputDir"), cfg["outputNames"]["frames"])
    os.makedirs(out, exist_ok=True)
    stale = [f for f in os.listdir(out) if f.startswith("chub_") and f.endswith(".png")]
    if stale:
        print(f"note: {len(stale)} frames already in {out}; they'll be overwritten frame by frame")

    class H(BaseHTTPRequestHandler):
        def _cors(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")

        def do_OPTIONS(self):
            self.send_response(204); self._cors(); self.end_headers()

        def do_POST(self):
            m = re.fullmatch(r"/frame/(\d{5})", self.path)
            data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            if not m or not data.startswith(b"\x89PNG"):
                self.send_response(400); self._cors(); self.end_headers(); return
            with open(os.path.join(out, f"chub_{m.group(1)}.png"), "wb") as f:
                f.write(data)
            n = int(m.group(1))
            if n % 120 == 0:
                print(f"  frame {n}", flush=True)
            self.send_response(200); self._cors(); self.end_headers()

        def log_message(self, *a):
            pass

    print(f"collecting frames into {out} on http://127.0.0.1:{PORT} (Ctrl+C to stop)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()


if __name__ == "__main__":
    main()
