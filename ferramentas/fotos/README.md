# Órbita · Fotos do catálogo

Transforma a foto do celular na foto padronizada do catálogo de armações.

## O que faz
1. Corrige a rotação do iPhone e remove grão de foto noturna
2. Remove fundo e sombra (IA, roda no seu computador ou no Colab) e corrige cor/exposição pelo papel
3. Endireita armação torta (até 15°)
4. Centraliza, mesma escala em todas
5. Fundo neutro `#EFEEEB` + sombra de contato suave
6. Salva WebP 1600 / 800 / 400 + miniatura justa (`_mini`, 240 px) + recorte PNG transparente
7. `relatorio.csv` + `contato.jpg` para conferir tudo de uma olhada

## Como fotografar
- Fundo claro e liso (folha A3, cartolina)
- Luz difusa: perto de janela, sem sol direto; sem flash
- Celular fixo (apoio), sempre à mesma distância
- Armação de frente, hastes abertas, ocupando boa parte da foto
- **Armação cristal/transparente:** use fundo um pouco mais escuro (cinza claro) para dar contraste

## Nome do arquivo = ref do cadastro
```
ORB-0042.jpg         → frente
ORB-0042_lado.jpg    → lado
ORB-0042_rosto.jpg   → no rosto
```

## Rodar no computador
```
pip install -r requirements.txt
python padronizar.py                 # fotos_brutas/ → fotos_catalogo/
```
1ª vez baixa o modelo de IA (~180 MB). Depois roda sem internet. ~3 s por foto.

Opções: `--fundo "#EFEEEB"` · `--forcar` (refaz as já feitas) · `--sem-sombra`.
Já processadas são puladas — dá para rodar de novo a cada lote novo.

## Rodar no Colab
```
!pip -q install "rembg[cpu]" pillow numpy
# envie padronizar.py e a pasta fotos_brutas/ (ou monte o Drive)
!python padronizar.py fotos_brutas fotos_catalogo
```

## Resultado
```
fotos_catalogo/
  ORB-0042/frente_1600.webp  frente_800.webp  frente_400.webp  frente_recorte.png
  relatorio.csv   ← OK / AVISO / ERRO por foto
  contato.jpg     ← todas lado a lado para conferir
```
AVISO não trava o lote: armação encostando na borda, pequena na foto, ou torta demais.

## Publicar no catálogo
```
python ferramentas/fotos/publicar.py fotos_catalogo    # na raiz do repositório
```
Copia só os WebP para `catalogo/fotos/` e refaz `catalogo/fotos/index.json` — a lista que o app lê para marcar "no catálogo". Depois: PR → merge.

## Testar sem fotos reais
`python gerar_testes.py` cria 7 fotos sintéticas difíceis (sombra, luz desigual, torta, EXIF, cristal).
