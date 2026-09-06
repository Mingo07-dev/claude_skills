#!/usr/bin/env python3
"""Veste il video promozionale con il tema dei caroselli.

    python3 scripts/compose_video.py                 # promo-it → promo-it-social
    python3 scripts/compose_video.py --lang en --dry-run

Prende `<video_dir>/promo-<lang>.mov` (la registrazione pulita, con i pallini
dei tocchi) e la monta dentro la stessa scena degli screenshot: fondo blu a
bande diagonali, telefono con cornice bianca, didascalie in grassetto e cerchi
sottili che pulsano sulle aree di cui parla la didascalia.

Il fondo lo disegna `build_carousel.py`: una sola definizione per carosello e
video, così se cambia la grafica cambia in un posto solo.

⚠️ **Non** è il file da caricare come App Preview: Apple vuole solo riprese
dell'app, senza cornici né grafiche aggiunte. Per l'App Store si carica
`promo-<lang>.mov`; questo serve per YouTube, Play e i social.

Uscita: `<video_dir>/promo-<lang>-social.mov`, 1080x1920.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_carousel import background, font_for, load_config  # noqa: E402

OUT_W, OUT_H = 1080, 1920
SCREEN_H = round(OUT_H * 0.72)      # altezza dello schermo dentro la cornice
BEZEL = 16
RADIUS = 62
GAP = 46                            # aria fra telefono e didascalia

# Telefono e testo si dispongono come **un blocco solo**, centrato in verticale:
# con un margine fisso in alto il blocco restava alto e sotto avanzavano
# duecento pixel di fondo vuoto. La fascia del testo è alta quanto la
# didascalia più alta, così il telefono non si sposta da una scena all'altra.

RING_FPS = 24
RING_PULSE = 1.6                    # secondi per battito

# Le didascalie e l'ordine delle scene stanno nella configurazione del progetto
# (`video.captions` e `video.scene_ends` in store-visuals.json). I **tempi** no:
# si ricavano dai tocchi registrati dal pilota, perché ogni ripresa dura un po'
# diversa (i dati arrivano quando arrivano) e i tempi fissi si sfasano — la
# didascalia di una scena compare mentre a schermo c'è ancora la precedente.


def caption_times(tl: dict, cfg: dict, lang: str) -> list[tuple[float, float, str, str]]:
    """Attacca ogni didascalia alla sua scena: da un tocco al successivo."""
    touches = tl["touches"]
    texts = cfg["video"]["captions"][lang]
    ends = cfg["video"]["scene_ends"]
    out, start = [], 0.0
    for i, (title, sub) in enumerate(texts):
        end = (touches[ends[i]]["t"] + 0.4
               if i < len(ends) and ends[i] < len(touches) else tl["duration"])
        out.append((start, max(start + 2.0, end), title, sub))
        start = end
    return out


def phone_frame(screen_w: int, screen_h: int) -> tuple[Image.Image, tuple[int, int]]:
    """Cornice bianca con il centro **trasparente**: si sovrappone al video, e i
    suoi angoli interni arrotondati coprono quelli quadrati della ripresa."""
    w, h = screen_w + BEZEL * 2, screen_h + BEZEL * 2
    frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([0, 0, w - 1, h - 1], RADIUS, fill=(255, 255, 255, 255))
    inner = Image.new("RGBA", (screen_w, screen_h), (0, 0, 0, 0))
    ImageDraw.Draw(inner).rounded_rectangle(
        [0, 0, screen_w - 1, screen_h - 1], max(2, RADIUS - BEZEL), fill=(0, 0, 0, 255))
    frame.paste((0, 0, 0, 0), (BEZEL, BEZEL), inner)
    return frame, (w, h)


def caption_png(cfg: dict, title: str, subtitle: str, width: int, path: Path) -> int:
    """Scrive il PNG della didascalia e ne restituisce l'altezza."""
    im = Image.new("RGBA", (width, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f_title = font_for(cfg, 58, "heavy")
    f_sub = font_for(cfg, 30, "medium")
    y = 0
    for line in _wrap(d, title, f_title, width - 80):
        w = d.textlength(line, font=f_title)
        d.text(((width - w) / 2 + 2, y + 3), line, font=f_title, fill=(2, 30, 48, 130))
        d.text(((width - w) / 2, y), line, font=f_title, fill=(255, 255, 255, 255))
        y += 68
    y += 6
    for line in _wrap(d, subtitle, f_sub, width - 80):
        w = d.textlength(line, font=f_sub)
        d.text(((width - w) / 2, y), line, font=f_sub,
               fill=(*tuple(cfg["palette"]["foam"]), 235))
        y += 40
    h = max(80, y + 10)
    im.crop((0, 0, width, h)).save(path)
    return h


def _wrap(d, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        probe = f"{cur} {word}".strip()
        if d.textlength(probe, font=fnt) <= max_w:
            cur = probe
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def ring_frames(rx: int, ry: int, folder: Path) -> int:
    """Cerchio sottile che **pulsa**: una sequenza corta che ffmpeg ripete."""
    n = round(RING_FPS * RING_PULSE)
    pad = 26
    w, h = (rx + pad) * 2, (ry + pad) * 2
    for i in range(n):
        phase = i / n
        # respiro: raggio e opacità salgono e scendono insieme, senza scatti
        grow = 1 + 0.06 * (1 - abs(0.5 - phase) * 2)
        alpha = round(150 + 85 * (1 - abs(0.5 - phase) * 2))
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx, cy = w / 2, h / 2
        d.ellipse([cx - rx * grow, cy - ry * grow, cx + rx * grow, cy + ry * grow],
                  outline=(255, 255, 255, alpha), width=5)
        im.filter(ImageFilter.GaussianBlur(0.6)).save(folder / f"ring_{i:03d}.png")
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lang", default="it")
    ap.add_argument("--config", default="store-visuals.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg_path = Path(args.config).resolve()
    cfg = load_config(cfg_path)
    video = cfg_path.parent / cfg.get("video_dir", "store/video")
    src = video / f"promo-{args.lang}.mov"
    tl_path = video / f"promo-{args.lang}-timeline.json"
    if not src.exists() or not tl_path.exists():
        sys.exit("Manca il filmato pulito o la sua timeline: "
                 "lancia prima scripts/add_touches.py")
    tl = json.loads(tl_path.read_text())

    screen_w = round(SCREEN_H * tl["width"] / tl["height"])
    frame_img, (fw, fh) = phone_frame(screen_w, SCREEN_H)
    screen_x = (OUT_W - screen_w) // 2
    # Dal punto logico dell'app al pixel della scena montata.
    pt = screen_w / (tl["width"] * tl["points_per_pixel"])

    times = caption_times(tl, cfg, args.lang)
    print(f"scena {OUT_W}x{OUT_H} · schermo {screen_w}x{SCREEN_H} · "
          f"{len(times)} didascalie · {len(tl['rings'])} cerchi")
    out = video / f"promo-{args.lang}-social.mov"
    if args.dry_run:
        for a, b, t, sub in times:
            print(f"  {a:6.1f}-{b:6.1f}s  {t} / {sub}")
        for r in tl["rings"]:
            print(f"  cerchio {r['t']:6.1f}s per {r['sec']}s attorno a "
                  f"({r['x']:.0f},{r['y']:.0f})")
        print("\nDRY-RUN: nessun filmato prodotto.")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        bg = background(cfg, OUT_W, OUT_H, OUT_W / 1320).convert("RGB")
        bg_path = tmpd / "bg.png"
        bg.save(bg_path)
        frame_path = tmpd / "frame.png"
        frame_img.save(frame_path)

        caps = []
        for i, (a, b, title, sub) in enumerate(times):
            p = tmpd / f"cap{i}.png"
            caps.append((a, b, p, caption_png(cfg, title, sub, OUT_W, p)))
        cap_band = max(c[3] for c in caps)
        top = (OUT_H - (fh + GAP + cap_band)) // 2
        screen_y = top + BEZEL
        cap_top = top + fh + GAP
        print(f"  blocco centrato: telefono a y={top}, testo a y={cap_top}, "
              f"fascia testo {cap_band}px")

        rings = []
        for i, r in enumerate(tl["rings"]):
            folder = tmpd / f"ring{i}"
            folder.mkdir()
            n = ring_frames(round(r["rx"] * pt), round(r["ry"] * pt), folder)
            rings.append((r, folder, n))

        cmd = ["ffmpeg", "-loglevel", "error", "-y",
               "-loop", "1", "-i", str(bg_path),          # 0 fondo
               "-i", str(src),                            # 1 ripresa
               "-loop", "1", "-i", str(frame_path)]       # 2 cornice
        idx = 3
        cap_idx, ring_idx = [], []
        for _a, _b, p, _h in caps:
            cmd += ["-loop", "1", "-i", str(p)]
            cap_idx.append(idx); idx += 1
        for r, folder, n in rings:
            cmd += ["-stream_loop", "-1", "-framerate", str(RING_FPS),
                    "-i", str(folder / "ring_%03d.png")]
            ring_idx.append(idx); idx += 1

        chain = [f"[1:v]scale={screen_w}:{SCREEN_H}[shot]",
                 f"[0:v][shot]overlay={screen_x}:{screen_y}[a0]",
                 f"[a0][2:v]overlay={screen_x - BEZEL}:{screen_y - BEZEL}[a1]"]
        last = "a1"
        for k, ((a, b, _p, ch), i) in enumerate(zip(caps, cap_idx)):
            chain.append(
                f"[{i}:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1,"
                f"fade=t=out:st={b - a - 0.5:.2f}:d=0.5:alpha=1,"
                f"setpts=PTS+{a:.3f}/TB[c{k}]")
            # Ogni didascalia sta centrata nella sua fascia: quelle su due
            # righe non spingono in basso le altre.
            chain.append(
                f"[{last}][c{k}]overlay=0:{cap_top + (cap_band - ch) // 2}:"
                f"enable='between(t,{a:.3f},{b:.3f})'[b{k}]")
            last = f"b{k}"
        for k, ((r, _f, _n), i) in enumerate(zip(rings, ring_idx)):
            x = round(screen_x + r["x"] * pt)
            y = round(screen_y + r["y"] * pt)
            chain.append(
                f"[{i}:v]format=rgba,setpts=PTS+{r['t']:.3f}/TB[r{k}]")
            chain.append(
                f"[{last}][r{k}]overlay=x={x}-overlay_w/2:y={y}-overlay_h/2:"
                f"enable='between(t,{r['t']:.3f},{r['t'] + r['sec']:.3f})'[e{k}]")
            last = f"e{k}"

        cmd += ["-filter_complex", ";".join(chain), "-map", f"[{last}]",
                "-t", f"{tl['duration']:.3f}",
                "-c:v", "libx264", "-crf", "19", "-preset", "medium",
                "-pix_fmt", "yuv420p", "-an", str(out)]
        subprocess.run(cmd, check=True)

    print(f"Fatto: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
