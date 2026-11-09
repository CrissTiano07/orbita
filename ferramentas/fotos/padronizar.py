"""Órbita · padroniza fotos de armações para o catálogo.

Pega a foto bruta do celular e entrega a foto de catálogo:
  1. corrige a rotação do iPhone (EXIF) e remove o grão de pouca luz
  2. remove o fundo e a sombra (IA: rembg, modelo isnet-general-use)
     e corrige cor/exposição usando o papel como referência neutra
  3. endireita a armação torta (frente)
  4. centraliza e põe sempre na mesma escala
  5. aplica fundo neutro + sombra de contato suave
  6. salva WebP em 3 tamanhos (1600 / 800 / 400) + miniatura justa (mini) + recorte PNG transparente
  7. gera relatorio.csv e contato.jpg (folha para conferir tudo de uma vez)

Nome do arquivo = ref da armação (o mesmo do cadastro):
  ORB-0042.jpg        → vista "frente"
  ORB-0042_lado.jpg   → vista "lado"
  ORB-0042_rosto.jpg  → vista "rosto"

Uso:
  python padronizar.py                         # fotos_brutas/ → fotos_catalogo/
  python padronizar.py entrada/ saida/ --fundo "#EFEEEB" --forcar --sem-sombra

1ª execução baixa o modelo de IA (~180 MB). Depois roda offline.
"""
import argparse
import csv
import math
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

# ---- padrões do catálogo (mudar aqui muda o catálogo inteiro) ----
LADO = 1600                 # quadrado final, px
TAMANHOS = (1600, 800, 400)  # WebP gerados
MINI = 480                  # miniatura justa para a grade do app (vista_mini.webp; nítida em tela retina)
QUALIDADE = 85
FUNDO = "#EFEEEB"           # neutro claro (mesma família do mockup aprovado)
OCUPA_LARG = {"frente": 0.78, "lado": 0.84, "rosto": 0.90}  # largura da armação / quadro
OCUPA_ALT = 0.62            # teto de altura (armações muito altas)
GIRO_MAX = 15               # graus: acima disso, não endireita (provável foto de lado)
MAX_ENTRADA = 2400          # reduz a foto bruta antes da IA (rapidez, sem perda visível)
PAPEL = 0.93                # brilho-alvo do papel depois da correção (0–1)
NITIDEZ = (0.8, 60, 2)      # UnsharpMask (raio, %, limiar) aplicado em cada tamanho final
GRAO_MIN = 1.2              # só remove grão acima deste nível (foto de dia ≈ 0,7; noturna ≈ 2)
EXTENSOES = {".jpg", ".jpeg", ".png", ".heic", ".webp"}
VISTAS = {"frente", "lado", "rosto"}

_sessao = None


def sessao_ia():
    global _sessao
    if _sessao is None:
        from rembg import new_session
        _sessao = new_session("isnet-general-use")
    return _sessao


def ler_nome(arq):
    """ORB-0042_lado.jpg → ("ORB-0042", "lado")."""
    stem = arq.stem
    if "_" in stem:
        ref, vista = stem.rsplit("_", 1)
        if vista.lower() in VISTAS:
            return ref, vista.lower()
    return stem, "frente"


def abrir(arq):
    if arq.suffix.lower() == ".heic":
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except ImportError:
            raise RuntimeError("foto .heic: instale pillow-heif ou exporte como JPG")
    img = ImageOps.exif_transpose(Image.open(arq)).convert("RGB")
    img.thumbnail((MAX_ENTRADA, MAX_ENTRADA), Image.LANCZOS)
    return tirar_grao(img)


def nivel_grao(img):
    """Estima o ruído da foto (desvio robusto do Laplaciano). Foto de dia ≈ 0,7; noturna ≈ 2."""
    import cv2
    a = np.array(img.convert("L")).astype(np.float32)
    lap = cv2.Laplacian(a, cv2.CV_32F)
    return float(np.median(np.abs(lap - np.median(lap))) * 1.4826 / math.sqrt(20))


def tirar_grao(img):
    """Remove o grão de foto com pouca luz, só quando há grão. Sem isso, o grão vira 'pontilhado'
    dentro da lente transparente depois do recorte (achado com a 1ª foto real, ORB-0001).
    Em foto limpa não mexe: suavizar à toa faz a IA tratar lente como parte da armação."""
    try:
        import cv2
    except ImportError:
        return img  # sem OpenCV, segue sem esta etapa
    g = nivel_grao(img)
    if g < GRAO_MIN:
        return img
    h = min(10, round(3 * g))
    img = Image.fromarray(cv2.fastNlMeansDenoisingColored(np.array(img), None, h, h, 7, 21))
    img.info["grao"] = g
    return img


def recortar(img):
    """Remove fundo e sombra. Devolve RGBA com alfa limpo."""
    from rembg import remove
    rgba = remove(img, session=sessao_ia())
    a = np.array(rgba.split()[-1]).astype(np.int16)
    a[a < 14] = 0                      # resíduo de fundo
    # lente transparente: a IA às vezes deixa "manchas" de fundo dentro da lente.
    # Pixel com cor de fundo e alfa incompleto = fundo → some.
    rgb = np.array(img).astype(np.int16)
    h, w = a.shape
    # fundo local estimado (mediana larga numa cópia reduzida: a armação, fina, some)
    peq = img.resize((max(1, w // 8), max(1, h // 8)), Image.BILINEAR).filter(ImageFilter.MedianFilter(15))
    cor_fundo = np.array(peq.resize((w, h), Image.BICUBIC)).astype(np.int16)
    perto = np.linalg.norm(rgb - cor_fundo, axis=2) < 20
    a[perto & (a < 230)] = 0
    rgba.putalpha(Image.fromarray(a.astype(np.uint8)))
    return rgba


def corrigir_cor(img, rgba):
    """Balanço de branco e exposição usando o próprio papel como referência (como um cartão cinza):
    o fundo que a IA descartou deveria ser neutro e claro. Tira o tom amarelado/azulado da lâmpada
    e deixa o preto da armação preto de verdade. Devolve o recorte com as cores corrigidas."""
    rgb = np.array(img).astype(np.float32) / 255
    a = np.array(rgba.split()[-1])
    fundo = a < 5
    if fundo.mean() < 0.05:  # quase sem fundo visível: não arrisca
        return rgba, None
    med = np.median(rgb[fundo], axis=0)
    alvo = float(med.mean())
    ganho = np.clip(alvo / np.maximum(med, 1e-3), 0.8, 1.25)        # neutraliza o tom
    expo = float(np.clip(PAPEL / max(alvo, 1e-3), 0.85, 1.6))         # papel vira branco-claro
    out = np.clip(rgb * ganho * expo, 0, 1)
    novo = Image.fromarray((out * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    novo.putalpha(rgba.split()[-1])
    return novo, (med * 255).round().astype(int)


def caixa(rgba, limiar=40):
    a = np.array(rgba.split()[-1]) > limiar
    ys, xs = np.where(a)
    if len(xs) == 0:
        return None
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def inclinacao(rgba):
    """Ângulo da armação de frente: liga o centro de massa da metade esquerda ao da direita."""
    a = np.array(rgba.split()[-1]).astype(np.float32) / 255
    a[a < 0.2] = 0
    ys, xs = np.nonzero(a)
    if len(xs) < 50:
        return 0.0
    w = a[ys, xs]
    meio = np.average(xs, weights=w)
    esq, dir_ = xs < meio, xs >= meio
    if esq.sum() < 20 or dir_.sum() < 20:
        return 0.0
    x1, y1 = np.average(xs[esq], weights=w[esq]), np.average(ys[esq], weights=w[esq])
    x2, y2 = np.average(xs[dir_], weights=w[dir_]), np.average(ys[dir_], weights=w[dir_])
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def compor(recorte, vista, fundo, sombra, lado=LADO, ocupa=None):
    larg, alt = recorte.size
    oc = ocupa or OCUPA_LARG[vista]
    escala = min(lado * oc / larg, lado * max(OCUPA_ALT, oc * 0.8) / alt)
    arm = recorte.resize((max(1, round(larg * escala)), max(1, round(alt * escala))), Image.LANCZOS)
    quadro = Image.new("RGBA", (lado, lado), fundo)
    x, y = (lado - arm.width) // 2, (lado - arm.height) // 2
    if sombra:
        # sombra de contato: discreta, deslocada para baixo — dá profundidade sem "sujar"
        a = np.array(arm.split()[-1]).astype(np.float32) * 0.16
        s = Image.new("RGBA", arm.size, (40, 36, 32, 0))
        s.putalpha(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(lado * 0.008)))
        quadro.alpha_composite(s, (x, y + round(lado * 0.012)))
    quadro.alpha_composite(arm, (x, y))
    return quadro.convert("RGB")


def avisos_de(img, bx):
    w, h = img.size
    x0, y0, x1, y1 = bx
    av = []
    m = 0.01
    if x0 <= w * m or y0 <= h * m or x1 >= w * (1 - m) or y1 >= h * (1 - m):
        av.append("armação encosta na borda: pode estar cortada")
    if (x1 - x0) < w * 0.25 and (x1 - x0) < h * 0.25:
        av.append("armação pequena na foto: aproxime o celular")
    return av


def processar(arq, saida, fundo, sombra):
    ref, vista = ler_nome(arq)
    t = time.time()
    img = abrir(arq)
    rec = recortar(img)
    rec, tom = corrigir_cor(img, rec)
    bx = caixa(rec)
    if bx is None:
        return ref, vista, "ERRO", "armação não encontrada", 0.0, time.time() - t, None
    av = avisos_de(img, bx)
    if img.info.get("grao"):
        av.append(f"foto com grão ({img.info['grao']:.1f}): removi; prefira luz de dia")
    rec = rec.crop(bx)
    giro = 0.0
    if vista == "frente":
        ang = inclinacao(rec)
        if 0.4 <= abs(ang) <= GIRO_MAX:
            giro = ang
            rec = rec.rotate(ang, resample=Image.BICUBIC, expand=True)
            rec = rec.crop(caixa(rec, limiar=8))
        elif abs(ang) > GIRO_MAX:
            av.append(f"muito torta ({ang:.0f}°): não endireitei")
    final = compor(rec, vista, fundo, sombra)
    pasta = saida / ref
    pasta.mkdir(parents=True, exist_ok=True)
    for tam in TAMANHOS:
        im = final if tam == LADO else final.resize((tam, tam), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(*NITIDEZ))
        im.save(pasta / f"{vista}_{tam}.webp", "WEBP", quality=QUALIDADE, method=6)
    # miniatura justa para a lista do app: armação ocupa quase todo o quadro
    mini = compor(rec, vista, fundo, sombra, lado=MINI, ocupa=0.94).filter(ImageFilter.UnsharpMask(*NITIDEZ))
    mini.save(pasta / f"{vista}_mini.webp", "WEBP", quality=QUALIDADE, method=6)
    rec.save(pasta / f"{vista}_recorte.png")
    status = "AVISO" if av else "OK"
    return ref, vista, status, "; ".join(av), giro, time.time() - t, final


def folha_contato(itens, destino, fundo):
    if not itens:
        return
    cel, cols = 360, 4
    linhas = math.ceil(len(itens) / cols)
    folha = Image.new("RGB", (cols * cel, linhas * (cel + 40)), "white")
    from PIL import ImageDraw
    d = ImageDraw.Draw(folha)
    for i, (rotulo, status, im) in enumerate(itens):
        x, y = (i % cols) * cel, (i // cols) * (cel + 40)
        folha.paste(im.resize((cel - 10, cel - 10), Image.LANCZOS), (x + 5, y + 5))
        cor = {"OK": (31, 95, 91), "AVISO": (176, 110, 0), "ERRO": (179, 38, 30)}[status]
        d.text((x + 8, y + cel), f"{rotulo}  [{status}]", fill=cor)
    folha.save(destino, quality=88)


def main():
    ap = argparse.ArgumentParser(description="Padroniza fotos de armações para o catálogo do Órbita.")
    ap.add_argument("entrada", nargs="?", default="fotos_brutas")
    ap.add_argument("saida", nargs="?", default="fotos_catalogo")
    ap.add_argument("--fundo", default=FUNDO, help="cor do fundo, ex. #EFEEEB")
    ap.add_argument("--forcar", action="store_true", help="refaz mesmo as já processadas")
    ap.add_argument("--sem-sombra", action="store_true", help="não aplica sombra de contato")
    arg = ap.parse_args()

    entrada, saida = Path(arg.entrada), Path(arg.saida)
    if not entrada.is_dir():
        sys.exit(f"Pasta de entrada não existe: {entrada}")
    saida.mkdir(parents=True, exist_ok=True)
    fotos = sorted(p for p in entrada.iterdir() if p.suffix.lower() in EXTENSOES)
    if not fotos:
        sys.exit(f"Nenhuma foto em {entrada}")

    linhas, folha = [], []
    print(f"{len(fotos)} foto(s) · fundo {arg.fundo} · saída {saida}/\n")
    for arq in fotos:
        ref, vista = ler_nome(arq)
        pronto = saida / ref / f"{vista}_{LADO}.webp"
        if pronto.exists() and pronto.stat().st_mtime > arq.stat().st_mtime and not arg.forcar:
            print(f"  =  {arq.name:24} já processada (use --forcar para refazer)")
            continue
        try:
            ref, vista, status, av, giro, seg, final = processar(arq, saida, arg.fundo, not arg.sem_sombra)
        except Exception as e:  # uma foto ruim não pode parar o lote
            ref, vista, status, av, giro, seg, final = ref, vista, "ERRO", str(e), 0.0, 0.0, None
        marca = {"OK": "ok", "AVISO": "!!", "ERRO": "XX"}[status]
        extra = f" · endireitei {giro:+.1f}°" if giro else ""
        print(f"  {marca} {arq.name:24} {status}{extra}{' · ' + av if av else ''}  ({seg:.1f}s)")
        linhas.append({"ref": ref, "vista": vista, "status": status, "avisos": av,
                       "giro_corrigido": f"{giro:.1f}", "arquivo": arq.name})
        if final is not None:
            folha.append((f"{ref} {vista}", status, final))

    if linhas:
        rel = saida / "relatorio.csv"
        novo = not rel.exists()
        with rel.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
            if novo:
                w.writeheader()
            w.writerows(linhas)
        folha_contato(folha, saida / "contato.jpg", arg.fundo)
        n = {s: sum(1 for l in linhas if l["status"] == s) for s in ("OK", "AVISO", "ERRO")}
        print(f"\nOK {n['OK']} · AVISO {n['AVISO']} · ERRO {n['ERRO']}")
        print(f"Confira tudo de uma vez em {saida / 'contato.jpg'}")


if __name__ == "__main__":
    main()
