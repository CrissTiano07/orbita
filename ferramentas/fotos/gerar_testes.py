"""Gera fotos de teste DIFÍCEIS de armações (sintéticas, sem direito autoral).

Simula o que dá errado numa foto real de celular:
fundo com textura, luz desigual (vinheta), sombra da armação, reflexo nas lentes,
armação torta e fora do centro, armação clara de baixo contraste, foto girada pelo EXIF.

Uso:  python gerar_testes.py  [pasta_saida]   (padrão: fotos_brutas/)
"""
import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 4000, 3000  # foto de celular em paisagem


def fundo(seed, tom=(238, 236, 232)):
    rng = np.random.default_rng(seed)
    base = np.ones((H, W, 3), np.float32) * np.array(tom, np.float32)
    # luz desigual: gradiente lateral + vinheta
    xx, yy = np.meshgrid(np.linspace(-1, 1, W), np.linspace(-1, 1, H))
    lado = rng.uniform(-1, 1)
    grad = 1 - 0.10 * (xx * lado + 1) / 2
    vinheta = 1 - 0.18 * (xx**2 + yy**2) / 2
    base *= (grad * vinheta)[..., None]
    # textura de papel/tecido
    ruido = rng.normal(0, 4.0, (H // 8, W // 8)).astype(np.float32)
    ruido = np.array(Image.fromarray(ruido).resize((W, H), Image.BICUBIC))
    base += ruido[..., None] + rng.normal(0, 2.0, (H, W, 1)).astype(np.float32)
    return np.clip(base, 0, 255)


def desenha_armacao(formato, cor, espessura, larg):
    """Desenha a armação numa camada RGBA (fundo transparente)."""
    lw, lh = int(larg * 0.40), int(larg * 0.26)
    ponte = int(larg * 0.12)
    cw, ch = larg + 400, lh + 400
    cam = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    lente = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d, dl = ImageDraw.Draw(cam), ImageDraw.Draw(lente)
    cx, cy = cw // 2, ch // 2
    boxes = [(cx - ponte // 2 - lw, cy - lh // 2, cx - ponte // 2, cy + lh // 2),
             (cx + ponte // 2, cy - lh // 2, cx + ponte // 2 + lw, cy + lh // 2)]
    for b in boxes:
        if formato == "redondo":
            r = min(lw, lh * 1.25) / 2
            mx, my = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
            bb = (mx - r, my - r, mx + r, my + r)
            d.ellipse(bb, outline=cor, width=espessura)
            dl.ellipse(bb, fill=(200, 215, 225, 28))
        elif formato == "gatinho":
            x0, y0, x1, y1 = boxes[0]  # desenha a esquerda; a direita é o espelho
            pts = [(x0, y0 + lh * 0.15), (x0 + lw * 0.2, y0), (x1, y0 + lh * 0.05),
                   (x1 - lw * 0.05, y1 - lh * 0.3), (x0 + lw * 0.55, y1), (x0 + lw * 0.1, y1 - lh * 0.25)]
            if b is boxes[1]:
                pts = [(cx * 2 - x, y) for x, y in pts]
            d.polygon(pts, outline=cor, width=espessura)
            dl.polygon(pts, fill=(200, 215, 225, 28))
        else:  # retangular
            d.rounded_rectangle(b, radius=int(lh * 0.18), outline=cor, width=espessura)
            dl.rounded_rectangle(b, radius=int(lh * 0.18), fill=(200, 215, 225, 28))
    # ponte e hastes (vistas de frente)
    d.arc((cx - ponte, cy - lh // 2 - ponte // 3, cx + ponte, cy - lh // 2 + ponte), 200, 340, fill=cor, width=espessura)
    y_h = cy - lh // 2 + espessura
    d.line((boxes[0][0], y_h, boxes[0][0] - 160, y_h - 20), fill=cor, width=espessura)
    d.line((boxes[1][2], y_h, boxes[1][2] + 160, y_h - 20), fill=cor, width=espessura)
    # reflexo branco nas lentes
    for b in boxes:
        dl.line((b[0] + lw * 0.25, b[1] + lh * 0.2, b[0] + lw * 0.45, b[1] + lh * 0.05), fill=(255, 255, 255, 150), width=18)
    return Image.alpha_composite(lente, cam)


CASOS = [
    # ref, formato, cor RGBA, espessura, largura px, giro°, desloc (x,y), observação
    ("ORB-0001", "retangular", (25, 25, 28, 255), 34, 2100, 4, (-300, 150), "acetato preto, torta"),
    ("ORB-0002", "redondo", (110, 75, 45, 255), 26, 1700, -6, (450, -200), "tartaruga, fora do centro"),
    ("ORB-0003", "gatinho", (110, 30, 46, 255), 30, 1900, 2, (0, 0), "vinho, sombra forte"),
    ("ORB-0004", "redondo", (165, 165, 170, 255), 9, 1600, -3, (200, 250), "metal prata fino, baixo contraste"),
    ("ORB-0005", "retangular", (200, 200, 205, 200), 24, 2000, 7, (-500, -100), "cristal translúcido, difícil"),
    ("ORB-0006", "retangular", (30, 60, 95, 255), 28, 1300, 0, (600, 300), "azul, pequena na foto"),
    ("ORB-0007", "gatinho", (40, 40, 40, 255), 30, 2000, -5, (0, 100), "preta, foto girada pelo EXIF"),
]


def main(saida="fotos_brutas"):
    out = Path(saida)
    out.mkdir(parents=True, exist_ok=True)
    random.seed(7)
    for i, (ref, fmt, cor, esp, larg, giro, (dx, dy), obs) in enumerate(CASOS):
        bg = fundo(i)
        arm = desenha_armacao(fmt, cor, esp, larg).rotate(giro, resample=Image.BICUBIC, expand=True)
        # sombra: cópia escura deslocada e borrada
        forte = 0.55 if ref == "ORB-0003" else 0.30
        a = np.array(arm.split()[-1], np.float32) / 255
        sombra = Image.fromarray((a * 255 * forte).astype(np.uint8)).filter(ImageFilter.GaussianBlur(28))
        x = W // 2 - arm.width // 2 + dx
        y = H // 2 - arm.height // 2 + dy
        canvas = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
        preto = Image.new("RGBA", sombra.size, (60, 55, 50, 255))
        preto.putalpha(sombra)
        canvas.alpha_composite(preto, (x + 45, y + 70))
        canvas.alpha_composite(arm, (x, y))
        img = canvas.convert("RGB").filter(ImageFilter.GaussianBlur(1.2))  # leve desfoque de câmera
        destino = out / f"{ref}.jpg"
        if ref == "ORB-0007":
            # salva "deitada" com EXIF Orientation=6, como o iPhone faz
            img = img.rotate(90, expand=True)
            exif = Image.Exif()
            exif[0x0112] = 6
            img.save(destino, quality=88, exif=exif)
        else:
            img.save(destino, quality=88)
        print(f"{destino.name:14} {obs}")


if __name__ == "__main__":
    main(*sys.argv[1:])
