# HANDOFF · Órbita

> Ponto de retomada. Ler **antes** de mexer no código.
> Histórico e porquês: `CONTEXT_ORBITA 1.md` e `CONTEXT_ORBITA 2.md`. Regras fixas: `BUSINESS-RULES.md`.

**Atualizado:** 08/11/2026
**Estado:** produção de teste, uso solo. Ainda **não** usado em atendimento real.
**Stack:** `index.html` único · JS puro, sem build · Firebase compat 11 (Auth Google + Firestore, projeto `orbita-b2b55`, `southamerica-east1`) · html2pdf (OS/recibo) · GitHub Pages.

---

## 1. Entregue nesta sessão — UX da receita

| Antes | Agora |
|---|---|
| Teclado só aceitava inteiro; quartos só por ±0,25 repetido (−2,75 = sinal → 2 → +0,25 ×3) | Atalhos diretos `,00 ,25 ,50 ,75` |
| Sinal num botão "± sinal" pequeno | Sinal primeiro, em destaque: **− Negativo / + Positivo** |
| Confirmar OD fechava o modal; reabrir para OE | **"Confirmar OD e seguir para OE"** abre o OE no esférico |
| OE igual ao OD digitado de novo | Botão **"OE = OD"** no topo do OE (copia, operador confere) |
| Cilíndrico vazio começava em + | Cilíndrico vazio começa em **−** (mais comum) |

Ajuste visual: alturas de `.mbig`, `.steps` e `.pad` reduzidas para o teclado caber inteiro no celular (afeta também o modal de medições — mesma família visual, intencional).
Testado em navegador headless 390×844: −2,75 OD → OE = OD → salvo correto; cil −1,25 correto. **Falta teste no iPhone real.**

Fecha o fio aberto "Encadeamento OD→OE" do CONTEXT 2 (§8, item 2).

### 1.1 Teclado de dioptrias refeito — "digite como se lê" (08/11/2026) — só UX

⚠️ Em 08/11 o arquivo chegou ao repositório como `index (29).html`; o GitHub Pages serve `index.html`, que **continuava antigo**. Usar sempre o nome `index.html` e apagar as cópias `(1)`/`(29)`.

Histórico: 1ª revisão (sinal em botões, atalhos de quarto, ±0,25) ficou confusa; 2ª (calculadora com vírgula) aprovada na ideia, com pedido de **vírgula automática**. Estado atual:

- **Vírgula automática, padrão Pix:** os dígitos entram pela direita. `−` `0` `2` `5` → **−0,25** · `2 7 5` → 2,75 · `1 0 0 0` → 10,00.
- Tecla **00** para valores inteiros: `−` `2` `00` → −2,00. Máximo 4 dígitos (99,99).
- Layout 4×4: `1 2 3 ⌫` · `4 5 6 −` · `7 8 9 +` · `00 0 [Próximo ›]`. "limpar" fica no visor.
- Só quartos: se o valor não terminar em 00/25/50/75, o campo não deixa avançar (visor âmbar + aviso). Durante a digitação não bloqueia (0,12 é passo intermediário de 1,25).
- **Olho já preenchido à mostra:** faixa tracejada no topo com os 4 valores do outro olho, para conferência visual enquanto preenche.
- Campo recém-aberto: a primeira tecla substitui o valor. Esférico sem sinal = positivo. Cilíndrico já começa em −. Adição sempre +.
- Eixo: só dígitos, até 180; "n/a" e pulado sem cilíndrico; cil limpo apaga o eixo.
- "Próximo ›" percorre os campos; no último vira "Concluir". Confirmar OD só segue para o OE se o OE estiver vazio, levando a adição.
- Notebook: mesmos dígitos, Enter = próximo, ⌫, Delete = limpar, ←/→/Tab, Esc.
- Armazenamento inalterado (`"-0.25"`); tela com vírgula.

Testado em navegador headless (12 cenários, 0 erros). **Falta teste no iPhone real.**

## 2. Próximos passos (ordem)

1. **Testar a aba Armações no iPhone** (cadastro, foto com nome da ref, lista, teto).
2. **Fotos reais** (≈5) → calibrar o script **e** piloto comparativo: script × Cloudinary × @imgly no iPhone (§3.2).
3. **Catálogo público** (página do cliente) lendo as armações + fotos do GitHub (§3).
4. **Receita por foto** (§4).

Receita (teclado) já testada e aprovada no iPhone em 08/11/2026.

## 3. Catálogo de armações — cadastro entregue, página pública a fazer

Página pública mobile-first para o cliente ver e escolher armações antes da prova em domicílio.
Mockup aprovado (estética + UX) em 07/11/2026: catálogo, detalhe, seleção para provar e versão computador (canvas "Órbita — Catálogo de armações" no Claude).

- **Gostei:** sem login; contador anônimo → métrica de preferência e reposição.
- **Reservar para provar:** nome + WhatsApp, máx. 5 armações, validade 72 h, envio da lista pelo WhatsApp.
- **Status por armação:** disponível · em prova · indisponível (acinzentada no fim + "avise-me").
- **Medidas:** lente/ponte/haste (gravadas na haste, ex. 52□18-140) + largura total → P/M/G e filtro "cabe no meu rosto".
- **Dados (proposta):** `armacoes/{ref}`, `reservas/{id}`, perfil do cliente. Leitura pública só de `armacoes`; escrita só pelo consultor; expiração de reserva e contadores no servidor.
- **Script de fotos PRONTO (08/11/2026):** `ferramentas/fotos/padronizar.py` — IA rembg `isnet-general-use` (remove fundo e sombra), endireita até 15°, centraliza, fundo `#EFEEEB` + sombra de contato, WebP 1600/800/400 + PNG recortado, `relatorio.csv` e `contato.jpg`. Testado em 7 fotos sintéticas difíceis (`gerar_testes.py`): 7/7 OK. Ponto fraco: armação cristal mantém a lente acinzentada → fotografar em fundo cinza claro. **Falta calibrar com as 5 fotos reais.**
- **Fotos — decisão 08/11/2026:** Firebase Storage **não** é gratuito para o bucket novo (`*.firebasestorage.app` exige plano Blaze; no Spark dá erro 402/403). Decidido: **Drive como depósito das brutas + GitHub como vitrine** (pasta do repositório servida pelo Pages), custo zero, via PR. Fluxo: foto sai do celular com o nome da ref → Drive/Arquivos → script (Cristiano ou Claude) → PR com as WebP → merge → no ar.
- **Integração com a OS:** campo "Armação" (hoje texto livre) passa a puxar do catálogo.
- **Pagamento: fora do MVP.** Handoff de segurança: nunca guardar cartão; checkout hospedado (Mercado Pago / Pix); confirmação só por webhook validado no servidor.

### 3.1 Aba Armações — entregue em 08/11/2026 (PR feat/cadastro-armacoes)
- 5ª aba **Armações** na barra de baixo.
- **Lista:** contador `n/teto`, filtros por status com contagem, busca (modelo, ref, cor, formato), status trocável na própria linha, ações foto · editar · excluir. Selo de foto: sem foto · aguardando tratamento · n fotos.
- **Cadastro rápido:** ref automática sequencial `ORB-0001…` (`counters.armacao`, pula refs já usadas); modelo; formato em chips; medidas da haste com pulo automático (2/2/3 dígitos); largura total opcional; **tamanho P/M/G calculado** (≤129 P · 130–139 M · ≥140 G; sem largura total, estima 2×lente + ponte + 8 mm); material e cor em chips + "outra cor"; status; quantidade. **Sem preço** (decisão do Cristiano).
- **Foto sem servidor:** depois de salvar, tela com a ref grande (para etiqueta) e 3 vistas (frente · lado · rosto). A câmera abre e o arquivo sai como `ORB-0042.jpg` / `ORB-0042_lado.jpg` pela folha de compartilhar (Arquivos/Drive) ou download. Marca a vista como `pendente` até o tratamento.
- **Status da foto (fix 08/11/2026):** `""` sem foto · `"pendente"` foto bruta tirada · `"ok"` foto tratada no ar. O app verifica sozinho: ao abrir a lista, testa `catalogo/fotos/{REF}/{vista}_400.webp`; se a foto existe no site, troca "aguardando tratamento" por "no catálogo" e mostra miniatura. Tela da foto explica que "aguardando" é normal.
- **Publicar fotos tratadas:** rodar `ferramentas/fotos/padronizar.py` e copiar as pastas de saída (`ORB-xxxx/…webp`) para `catalogo/fotos/` num PR. Após o merge, o status muda sozinho.
- **Teto:** padrão 200 (Ajustes → Numeração). Aviso a 90%; no teto, "Nova armação" bloqueia.
- **Dados:** `consultores/{uid}/armacoes/{ref}` via `saveArmacao` / `deleteArmacao`. Regra do Firestore atual (`consultores/{uid}/{document=**}`) já cobre — nada a mudar no console.
- Testado em headless 390×844 e 1280×900 com Firebase simulado que grava/relê e rejeita `undefined`: cadastro, validação, pulo de campo, tamanho, edição, status, filtro, busca, teto, exclusão, foto com nome da ref — 0 erros. **Falta teste no iPhone real** (câmera + folha de compartilhar).

### 3.2 Piloto de fotos (quando houver 5 fotos reais)
**1ª foto real (08/11/2026, ORB-0001, metal fino preto, frente + lado):** script OK nas duas — fundo, sombra e cenário bagunçado (lado) removidos; endireitou −1,8°. Publicada em `catalogo/fotos/ORB-0001/`. Achados: (1) foto noturna com luz de lâmpada gera **grão** que vira "pontilhado" dentro da lente transparente → fotografar de dia, perto da janela; (2) remover tudo que tem cor de fundo limpa a lente mas **apaga armação cristal** (testado e revertido) — manter regra atual; (3) adesivo de demonstração da lente ("MEMORY TITANIUM") aparece, é real. Só WebP vai para o repositório (sem PNG nem foto bruta).

- **Script** (`ferramentas/fotos`, rembg): testado 7/7 em sintéticas.
- **Cloudinary (grátis, sem cartão):** remoção de fundo na nuvem custa 75 transformações por imagem (150 frentes ≈ 11 de 25 créditos/mês); salvar como transformação nomeada para cobrar uma vez; plano grátis suspende em vez de cobrar. Ponto fraco: upload sem servidor expõe o preset (restringir tipo/tamanho/pasta; trocar o nome se vazar).
- **@imgly/background-removal (no navegador):** código aberto (AGPL), sem cota; modelo IS-Net baixado uma vez (~40–80 MB). Risco: memória/velocidade no iPhone.
- Combinação candidata: @imgly no celular + armazenamento (GitHub ou Cloudinary só como storage). Decidir após comparar os recortes.

## 4. Receita por foto — próxima grande evolução

Preencher os campos da receita a partir de uma **foto da receita** (câmera ou imagem do WhatsApp).
- Foto → leitura (OCR/visão) → preenche OD/OE (esf, cil, eixo, adição) → **operador confere no modal** antes de confirmar. Nunca salvar direto sem conferência.
- **LGPD:** receita é dado de saúde. Descartar a imagem após extrair (minimização) ou guardar só com consentimento explícito.
- Decidir: OCR no aparelho (privacidade, sem custo) × IA de visão em servidor (precisão maior, dado sai do aparelho).

## 5. Ferramenta de DP (MediaPipe) — fora deste repositório

Existe uma ferramenta de medição de DP no navegador (calibração por cartão de crédito, MediaPipe Face Landmarker, paralaxe pelo diâmetro da íris), construída em sessão separada.
**Ela não está neste repositório** nem é chamada pelo `index.html`. Localizar o arquivo, versionar aqui (ex. `ferramentas/dp.html`) e só então decidir a integração com o campo de medições.

## 6. LGPD — revisão da base legal (proposta, não aplicada)

Pesquisa de 07/11/2026. **Não é parecer jurídico** — validar com especialista antes de atender cliente real de outro consultor.

- Receita = dado de saúde = **sensível** (LGPD art. 11).
- **Base principal: obrigação legal (art. 11, II, a).** O Decreto 24.492/1934 obriga a ótica a manter livro de registro das receitas aviadas, com nome e residência do paciente e do médico. Se a lei manda registrar, registrar dispensa consentimento.
- **Base de reserva:** exercício regular de direitos em contrato (art. 11, II, d).
- **Evitar** "tutela da saúde" (art. 11, II, f): restrita a profissionais/serviços de saúde; enquadramento da ótica é incerto.
- **Proibido:** legítimo interesse para dado sensível; repassar dado de saúde para vantagem econômica (art. 11 §4º) → **Motor 2 / inteligência de demanda só com dado anonimizado**; usar receita para marketing sem consentimento.
- **Sempre obrigatório:** transparência (o que coleta, por quê, por quanto tempo), segurança, minimização.

**Proposta:** trocar o checkbox obrigatório (R5) por **aviso curto** — ex.: "Registramos sua receita por exigência legal (Decreto 24.492/34). Usamos só para confeccionar seus óculos." Consentimento específico só para extras: guardar foto da receita, lembrete de renovação, marketing.
**Ideia aberta:** Órbita como livro de registro digital → perguntar à VISA Fortaleza se aceita formato digital (hoje o livro é físico, com termo de abertura rubricado).
**Decisão pendente do Cristiano.** Até decidir, R5 segue valendo.

## 7. Fios herdados ainda abertos

Ver `CONTEXT_ORBITA 2.md` §8: scroll no notebook (⚠️ sem reabrir zoom no mobile), aviso de cache do Firestore (⚠️ não quebrar offline), QR de duplo propósito, protocolo de recebimento digital. Lembrete LGPD (§10) segue de pé.
