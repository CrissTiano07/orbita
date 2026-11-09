"""Órbita · publica as fotos tratadas no site e atualiza o índice.

Copia só os WebP (sem PNG nem foto bruta) de fotos_catalogo/ para catalogo/fotos/
e reescreve catalogo/fotos/index.json — a lista que o app lê para saber quais
armações já têm foto no catálogo, venha a foto de onde vier.

Uso (na raiz do repositório):
  python ferramentas/fotos/publicar.py fotos_catalogo
  python ferramentas/fotos/publicar.py fotos_catalogo catalogo/fotos
  python ferramentas/fotos/publicar.py --so-indice          # só refaz o index.json

Depois: abrir um PR com catalogo/fotos/. No merge, o app atualiza sozinho.
"""
import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

VISTAS = ("frente", "lado", "rosto")
TAMANHOS = ("1600", "800", "400", "mini")


def copiar(origem: Path, destino: Path):
    n = 0
    for pasta in sorted(p for p in origem.iterdir() if p.is_dir()):
        for arq in pasta.glob("*.webp"):
            alvo = destino / pasta.name / arq.name
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(arq, alvo)
            n += 1
    return n


def indice(destino: Path):
    fotos = {}
    for pasta in sorted(p for p in destino.iterdir() if p.is_dir()):
        vistas = [v for v in VISTAS if (pasta / f"{v}_400.webp").exists()]
        incompletas = [v for v in vistas if not all((pasta / f"{v}_{t}.webp").exists() for t in TAMANHOS)]
        if incompletas:
            print(f"  !! {pasta.name}: faltam tamanhos em {', '.join(incompletas)} (rode o padronizar.py de novo)")
        if vistas:
            fotos[pasta.name] = vistas
    dados = {"versao": 1, "atualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"), "fotos": fotos}
    (destino / "index.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return fotos


def main():
    ap = argparse.ArgumentParser(description="Publica fotos tratadas em catalogo/fotos e atualiza o index.json.")
    ap.add_argument("origem", nargs="?", default="fotos_catalogo")
    ap.add_argument("destino", nargs="?", default="catalogo/fotos")
    ap.add_argument("--so-indice", action="store_true", help="não copia nada, só refaz o index.json")
    arg = ap.parse_args()
    destino = Path(arg.destino)
    destino.mkdir(parents=True, exist_ok=True)
    if not arg.so_indice:
        origem = Path(arg.origem)
        if not origem.is_dir():
            sys.exit(f"Pasta de origem não existe: {origem}")
        print(f"{copiar(origem, destino)} arquivo(s) copiados para {destino}/")
    fotos = indice(destino)
    print(f"index.json: {len(fotos)} armação(ões) com foto · {sum(len(v) for v in fotos.values())} vista(s)")


if __name__ == "__main__":
    main()
