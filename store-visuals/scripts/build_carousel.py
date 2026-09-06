#!/usr/bin/env python3
"""Mockup store in stile **carosello**: le slide si leggono come un'unica scena.

    python3 scripts/build_carousel.py                          # tutto, da store-visuals.json
    python3 scripts/build_carousel.py --device ios-iphone69 --lang it
    python3 scripts/build_carousel.py --config altra-app.json

Prende le catture in `raw_dir/<device>/<lingua>/NN-<scena>.png` e scrive le
slide in `mockups_dir/<device>/<lingua>/`.

Le tre scelte che rendono lo stile riconoscibile:

1. **Le slide si compongono su un'unica tela larga** e si tagliano alla fine. È
   l'unico modo perché le bande diagonali dello sfondo proseguano da una slide
   all'altra senza scalini, e perché un telefono possa stare **a cavallo** di
   due immagini: chi scorre il carosello vede un movimento, non cartoline
   scollegate.
2. **Cornice bianca spessa, senza finto notch**: le catture contengono già la
   barra di stato vera e l'isola dinamica; disegnarne un'altra dà due tacche.
3. **Telefono e testo come blocco unico centrato** (vedi le quote qui sotto).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Le quote sotto **devono restare legate**: `EDGE` (telefono ↔ bordo) e
# `CAP_TOP`/`CAP_BOTTOM` (testo ↔ bordo) uguali fanno sì che il blocco
# telefono+testo risulti centrato nella slide. Con valori diversi il telefono
# finisce incollato a un bordo e tutto il vuoto si accumula dall'altra parte:
# misurato, 72 px sopra e 480 sotto.
CAP_TOP = 0.075
CAP_BOTTOM = 0.075
EDGE = 0.075
GAP = 0.05          # aria fra telefono e blocco di testo

PAIR_WIDTH = 0.72   # larghezza dello schermo nel telefono a cavallo (frazione slide)
PAIR_TILT = -10     # gradi
PAIR_CENTER_Y = 0.34
SOLO_WIDTH = 0.74


def load_config(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"Manca {path}: copia scripts/store-visuals.example.json e adattalo.")
    return json.loads(path.read_text(encoding="utf-8"))


def font_for(cfg: dict, size: int, weight: str = "heavy") -> ImageFont.FreeTypeFont:
    f = cfg["font"]
    return ImageFont.truetype(f["file"], size, index=f.get(weight, 0))


def background(cfg: dict, width: int, height: int, scale: float) -> Image.Image:
    """Fondo con bande diagonali che attraversano **tutto** il carosello.

    Le bande sono parallelogrammi lunghi quanto la tela: tagliando le slide,
    ognuna eredita la sua fetta e il disegno prosegue senza interruzioni.
    """
    p = cfg["palette"]
    deep, mid, light = tuple(p["deep"]), tuple(p["mid"]), tuple(p["light"])
    bg = Image.new("RGBA", (width, height), (*deep, 255))
    d = ImageDraw.Draw(bg, "RGBA")

    slant = height * 1.15          # ~41°
    band = round(760 * scale)
    x, i = -slant, 0
    while x < width + slant:
        colour = (*mid, 255) if i % 2 == 0 else (*light, 90)
        d.polygon([(x, height), (x + slant, 0),
                   (x + slant + band, 0), (x + band, height)], fill=colour)
        x += band * 2
        i += 1

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gr = round(1400 * scale)
    ImageDraw.Draw(glow).ellipse([-gr // 2, -gr, gr, gr // 3], fill=(255, 226, 160, 46))
    bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(round(180 * scale))))
    return bg


def phone(shot: Image.Image, inner_w: int, radius: int, bezel: int) -> Image.Image:
    """Cattura dentro una cornice bianca spessa, angoli molto arrotondati."""
    inner_h = round(inner_w * shot.height / shot.width)
    inner = shot.convert("RGBA").resize((inner_w, inner_h), Image.LANCZOS)
    fw, fh = inner_w + bezel * 2, inner_h + bezel * 2
    frame = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle([0, 0, fw - 1, fh - 1], radius,
                                            fill=(255, 255, 255, 255))
    mask = Image.new("L", (inner_w, inner_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, inner_w - 1, inner_h - 1],
                                           max(2, radius - bezel), fill=255)
    frame.paste(inner, (bezel, bezel), mask)
    return frame


def with_shadow(im: Image.Image, blur: int, offset: tuple[int, int], opacity: int = 120):
    """Ombra morbida: senza, la cornice bianca sembra incollata sul fondo."""
    pad = blur * 3
    canvas = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow.paste(Image.new("RGBA", im.size, (2, 26, 42, opacity)),
                 (pad + offset[0], pad + offset[1]), im.split()[3])
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(blur)))
    canvas.alpha_composite(im, (pad, pad))
    return canvas, pad


def caption_height(title: str, subtitle: str | None, scale: float) -> int:
    return (round(120 * scale) * len(title.split("\n"))
            + (round(78 * scale) if subtitle else 0))


def draw_caption(cfg, canvas, slide_x, slide_w, height, title, subtitle,
                 where, scale, align="center") -> None:
    d = ImageDraw.Draw(canvas, "RGBA")
    margin = round(104 * scale)
    f_title = font_for(cfg, round(104 * scale), "heavy")
    f_sub = font_for(cfg, round(46 * scale), "medium")
    line_h = round(120 * scale)
    foam = tuple(cfg["palette"]["foam"])

    y = (round(height * CAP_TOP) if where == "top"
         else height - caption_height(title, subtitle, scale) - round(height * CAP_BOTTOM))

    def place(w: float) -> float:
        return slide_x + margin if align == "left" else slide_x + (slide_w - w) / 2

    for line in title.split("\n"):
        w = d.textlength(line, font=f_title)
        x = place(w)
        d.text((x + 3 * scale, y + 5 * scale), line, font=f_title, fill=(2, 30, 48, 120))
        d.text((x, y), line, font=f_title, fill=(255, 255, 255))
        y += line_h

    if subtitle:
        y += round(10 * scale)
        w = d.textlength(subtitle, font=f_sub)
        d.text((place(w), y), subtitle, font=f_sub, fill=(*foam, 235))


def build(cfg: dict, root: Path, device: str, lang: str) -> int:
    spec = cfg["devices"][device]
    (W, H), radius, bezel = spec["size"], spec["radius"], spec["bezel"]
    src = root / cfg["raw_dir"] / spec.get("alias", device) / lang
    if not src.is_dir():
        print(f"  {device}/{lang}: nessuna cattura in {src}")
        return 0
    shots = {p.stem.split("-", 1)[-1]: p for p in src.glob("*.png")}
    plan = cfg["slides"][lang]

    # Media geometrica fra i due rapporti, non la sola larghezza: su tablet
    # (molto più larghi che alti rispetto a un telefono) tarare il corpo del
    # testo sulla larghezza darebbe didascalie enormi.
    scale = math.sqrt((W / 1320) * (H / 2868))
    canvas = background(cfg, W * len(plan), H, scale)

    for i, slide in enumerate(plan):
        role = slide["role"]
        if role == "pair-end":
            continue                                  # disegnato dalla slide prima
        scene = slide.get("scene")
        if scene not in shots:
            print(f"  manca la cattura «{scene}» in {src}")
            continue
        shot = Image.open(shots[scene])

        if role == "pair-start":
            # A cavallo della cucitura, inclinato e alto: sotto resta una fascia
            # libera su entrambe le slide, dove vivono le due didascalie.
            inch = phone(shot, round(W * PAIR_WIDTH), radius, bezel)
            inch = inch.rotate(PAIR_TILT, resample=Image.BICUBIC, expand=True)
            img, _ = with_shadow(inch, round(46 * scale),
                                 (round(12 * scale), round(28 * scale)))
            cx, cy = W * (i + 1), H * PAIR_CENTER_Y
            canvas.alpha_composite(img, (round(cx - img.width / 2),
                                         round(cy - img.height / 2)))
        else:
            where = slide.get("caption", "bottom")
            cap_h = caption_height(slide["title"], slide.get("subtitle"), scale)
            edge, gap = round(H * EDGE), round(H * GAP)
            if where == "top":
                band_top, band_bottom = round(H * CAP_TOP) + cap_h + gap, H - edge
            else:
                band_top = edge
                band_bottom = H - round(H * CAP_BOTTOM) - cap_h - gap
            band_h = band_bottom - band_top
            inner_w = min(round(W * SOLO_WIDTH),
                          round((band_h - bezel * 2) * shot.width / shot.height))
            img, pad = with_shadow(phone(shot, inner_w, radius, bezel),
                                   round(40 * scale), (0, round(24 * scale)))
            x = round(W * i + (W - img.width) / 2)
            y = band_top + (band_h - (img.height - pad * 2)) // 2 - pad
            canvas.alpha_composite(img, (x, y))

    for i, slide in enumerate(plan):
        draw_caption(cfg, canvas, W * i, W, H, slide["title"], slide.get("subtitle"),
                     slide.get("caption", "bottom"), scale,
                     "left" if slide["role"] == "pair-start" else "center")

    out_dir = root / cfg["mockups_dir"] / device / lang
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.glob("*.png"):
        p.unlink()
    for i, slide in enumerate(plan):
        name = slide.get("scene") or f"{plan[i - 1].get('scene')}-2"
        out = canvas.crop((W * i, 0, W * (i + 1), H)).convert("RGB")
        assert out.size == (W, H)
        out.save(out_dir / f"{i + 1:02d}-{name}.png", "PNG")
    print(f"  {device}/{lang}: {len(plan)} slide {W}x{H} in {out_dir}")
    return len(plan)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="store-visuals.json")
    ap.add_argument("--device", nargs="+")
    ap.add_argument("--lang", nargs="+")
    args = ap.parse_args(argv[1:])

    cfg_path = Path(args.config).resolve()
    cfg = load_config(cfg_path)
    root = cfg_path.parent
    devices = args.device or list(cfg["devices"])
    langs = args.lang or list(cfg["slides"])

    print("Carosello:")
    made = sum(build(cfg, root, d, lang) for d in devices for lang in langs)
    print(f"  totale: {made} slide")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
