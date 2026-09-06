#!/usr/bin/env python3
"""Rifinisce la registrazione grezza: disegna i tocchi, taglia le attese.

    python3 scripts/add_touches.py                  # lingua it
    python3 scripts/add_touches.py --lang en --dry-run

Perché i tocchi non li disegna l'app: i gesti con sorgente `test` fanno
comparire il mirino del binding (cerchio con la croce, `handlePointerEvent` in
`flutter_test/src/binding.dart`), inguardabile in un video. Il pilota
`integration_test/promo_video_test.dart` (vedi reference/driver_template.dart) usa quindi eventi con sorgente
**device** — indistinguibili da un dito per l'app, invisibili per il binding — e
stampa i marcatori:

    VIDEO:start,<ms>                       app avviata / sequenza finita
    TOUCH:<ms>,<x>,<y>                     dove ha toccato il dito
    RING:<ms>,<cx>,<cy>,<rx>,<ry>,<sec>    area da evidenziare (per il tema)

Coordinate in **punti logici** (440 di larghezza sull'iPhone 6.9"), non pixel.

Uscite:
  <video_dir>/promo-<lang>.mov            filmato pulito, con i pallini
  <video_dir>/promo-<lang>-timeline.json  tempi e aree, per `compose_video.py`
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

def video_dir(config: str) -> Path:
    """Cartella dei filmati, letta dalla configurazione del progetto."""
    cfg_path = Path(config).resolve()
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        return cfg_path.parent / cfg.get("video_dir", "store/video")
    return Path("store/video").resolve()


VIDEO = Path("store/video")   # sostituita in main() con quella della config

# Aspetto e tempi del pallino.
RADIUS_PT = 26
LIFE = 0.70
FADE_IN = 0.08
FADE_OUT = 0.30
OPACITY = 0.62

# Quanto deve durare la mappa ferma prima che parta lo zoom sulla spiaggia.
LEAD_TO_ZOOM = 4.0

# Quanto passa, nel pilota, fra il marcatore d'inizio e la partenza dello zoom.
# Sulla carta sono 5 s (`_hold(2s)` + l'attesa di 3s), misurati sul filmato ne
# risultano 7: in mezzo ci sono la lettura delle spiagge e i fotogrammi che il
# pilota disegna aspettando. Serve solo alle registrazioni precedenti al
# marcatore `VIDEO:zoom`; da quelle nuove il momento si legge e basta.
PRE_ZOOM_FALLBACK = 7.0


def dot_png(radius_px: int, path: Path) -> None:
    """Cerchio bianco morbido con un anello appena accennato: è la convenzione
    delle registrazioni Android, si legge come un tocco e non come un cursore."""
    size = radius_px * 4
    im = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    d = ImageDraw.Draw(im)
    c = size / 2
    d.ellipse([c - radius_px, c - radius_px, c + radius_px, c + radius_px],
              fill=(255, 255, 255, 235))
    d.ellipse([c - radius_px * 1.6, c - radius_px * 1.6,
               c + radius_px * 1.6, c + radius_px * 1.6],
              outline=(255, 255, 255, 120), width=max(2, radius_px // 8))
    im.filter(ImageFilter.GaussianBlur(radius_px * 0.22)).save(path)


def markers(lang: str):
    raw = VIDEO / f"promo-{lang}-raw.mov"
    marks = VIDEO / f"promo-{lang}-touches.txt"
    start = VIDEO / f"promo-{lang}-recstart.txt"
    for f in (raw, marks, start):
        if not f.exists():
            sys.exit(f"Manca {f} — rilancia scripts/record_video.sh")

    rec = int(start.read_text().strip())
    touches, rings, app_start, app_end, zoom_at = [], [], None, None, None
    for line in marks.read_text().splitlines():
        kind, _, payload = line.partition(":")
        p = payload.split(",")
        if kind == "VIDEO" and p[0] == "start":
            app_start = (int(p[1]) - rec) / 1000
        elif kind == "VIDEO" and p[0] == "end":
            app_end = (int(p[1]) - rec) / 1000
        elif kind == "VIDEO" and p[0] == "zoom":
            zoom_at = (int(p[1]) - rec) / 1000
        elif kind == "TOUCH" and len(p) == 3:
            touches.append({"t": (int(p[0]) - rec) / 1000,
                            "x": float(p[1]), "y": float(p[2])})
        elif kind == "RING" and len(p) == 6:
            rings.append({"t": (int(p[0]) - rec) / 1000,
                          "x": float(p[1]), "y": float(p[2]),
                          "rx": float(p[3]), "ry": float(p[4]),
                          "sec": float(p[5])})
    if app_start is None or app_end is None:
        sys.exit("Marcatori VIDEO:start/end assenti: la registrazione è monca.")
    return raw, touches, rings, app_start, app_end, zoom_at


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lang", default="it")
    ap.add_argument("--config", default="store-visuals.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    global VIDEO
    VIDEO = video_dir(args.config)

    raw, touches, rings, app_start, app_end, zoom_at = markers(args.lang)
    probe = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "json", str(raw)],
        capture_output=True, text=True, check=True).stdout)["streams"][0]
    w, h = probe["width"], probe["height"]
    scale = w / 440.0  # marcatori in punti logici, filmato in pixel

    # Il montato comincia `LEAD_TO_ZOOM` secondi prima della volata sulla
    # spiaggia: prima si tagliava a partire dall'avvio dell'app e restavano dieci
    # secondi di mappa immobile.
    zoom = zoom_at if zoom_at is not None else app_start + PRE_ZOOM_FALLBACK
    cut = max(0.0, zoom - LEAD_TO_ZOOM)
    print(f"{len(touches)} tocchi, {len(rings)} aree · filmato {w}x{h} · scala {scale:.1f}x")
    print(f"zoom a {zoom:.1f}s{'' if zoom_at is not None else ' (stimato)'} · "
          f"taglio da {cut:.1f}s a {app_end:.1f}s → {app_end - cut:.1f}s di montato")

    out = VIDEO / f"promo-{args.lang}.mov"
    timeline = VIDEO / f"promo-{args.lang}-timeline.json"
    if args.dry_run:
        for t in touches:
            print(f"  tocco {t['t'] - cut:6.1f}s  ({t['x']:.0f}, {t['y']:.0f})")
        for r in rings:
            print(f"  area  {r['t'] - cut:6.1f}s  ({r['x']:.0f}, {r['y']:.0f}) "
                  f"±({r['rx']:.0f}, {r['ry']:.0f}) per {r['sec']:.0f}s")
        print("\nDRY-RUN: nessun filmato prodotto.")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        radius = round(RADIUS_PT * scale)
        dot = Path(tmp) / "dot.png"
        dot_png(radius, dot)

        cmd = ["ffmpeg", "-loglevel", "error", "-y",
               "-ss", f"{cut:.3f}", "-to", f"{app_end:.3f}", "-i", str(raw)]
        for _ in touches:
            cmd += ["-loop", "1", "-t", f"{LIFE}", "-i", str(dot)]

        chain, last = [], "0:v"
        for i, t in enumerate(touches, start=1):
            at = t["t"] - cut
            chain.append(
                f"[{i}:v]format=rgba,colorchannelmixer=aa={OPACITY},"
                f"fade=t=in:st=0:d={FADE_IN}:alpha=1,"
                f"fade=t=out:st={LIFE - FADE_OUT:.2f}:d={FADE_OUT}:alpha=1,"
                f"setpts=PTS+{at:.3f}/TB[d{i}]")
            chain.append(
                f"[{last}][d{i}]overlay="
                f"x={round(t['x'] * scale)}-overlay_w/2:"
                f"y={round(t['y'] * scale)}-overlay_h/2:"
                f"enable='between(t,{at:.3f},{at + LIFE:.3f})'[v{i}]")
            last = f"v{i}"

        cmd += ["-filter_complex", ";".join(chain), "-map", f"[{last}]",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                "-pix_fmt", "yuv420p", "-an", str(out)]
        subprocess.run(cmd, check=True)

    timeline.write_text(json.dumps({
        "video": out.name,
        "width": w,
        "height": h,
        "points_per_pixel": 1 / scale,
        "duration": round(app_end - cut, 3),
        "touches": [{"t": round(t["t"] - cut, 3), "x": t["x"], "y": t["y"]}
                    for t in touches],
        "rings": [{"t": round(r["t"] - cut, 3), "x": r["x"], "y": r["y"],
                   "rx": r["rx"], "ry": r["ry"], "sec": r["sec"]} for r in rings],
    }, indent=2, ensure_ascii=False))
    print(f"\nFatto: {out} e {timeline}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
