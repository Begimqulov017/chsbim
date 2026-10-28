#!/usr/bin/env python3
"""CHSB_PRO test sayti serveri. Ishga tushirish:  python server.py  ->  http://localhost:8000
Natijalar results/<fan>.json fayllarida saqlanadi."""
import json, os, threading, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
ROOT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ROOT, "results"); os.makedirs(RES, exist_ok=True)
SUBJ = {"fizika", "matematika", "ingliz"}
lock = threading.Lock()

def path_of(s): return os.path.join(RES, s + ".json")
def load(s):
    try:
        with open(path_of(s), encoding="utf-8") as f: return json.load(f)
    except Exception: return []

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def send_json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path.startswith("/api/results/"):
            s = self.path.split("/")[-1].split("?")[0]
            return self.send_json(load(s) if s in SUBJ else [], 200 if s in SUBJ else 404)
        if self.path.startswith("/results/") or self.path.endswith(".py"): return self.send_error(403)
        super().do_GET()
    def do_POST(self):
        if self.path != "/api/result": return self.send_error(404)
        try:
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            s = d["subject"]; assert s in SUBJ
            rec = {"name": str(d["name"]).strip()[:60], "subject": s, "variant": str(d["variant"])[:10],
                   "score": round(float(d["score"]), 2), "total": float(d["total"]), "correct": int(d["correct"]),
                   "wrong": int(d["wrong"]), "skipped": int(d["skipped"]), "time": int(d["time"]),
                   "date": time.strftime("%Y-%m-%d %H:%M:%S")}
            assert rec["name"] and 0 <= rec["score"] <= rec["total"]
        except Exception: return self.send_json({"ok": False}, 400)
        with lock:
            data = load(s); data.append(rec)
            tmp = path_of(s) + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=1)
            os.replace(tmp, path_of(s))
        self.send_json({"ok": True})
    def log_message(self, *a): pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Sayt: http://localhost:{port}   (to'xtatish: Ctrl+C)")
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
