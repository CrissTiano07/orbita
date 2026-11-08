# CLAUDE.md · Órbita

Instruções para qualquer IA que trabalhe neste repositório. Ler antes de mudar qualquer coisa.

## Antes de mexer
1. Ler `HANDOFF.md` (estado atual e próximos passos) e `BUSINESS-RULES.md` (regras fixas).
2. Dúvida sobre o porquê de uma decisão → `CONTEXT_ORBITA 1.md` / `2.md`.
3. Conhecer o código afetado antes de propor. Mudar sem conhecer gera regressão.

## Fluxo de trabalho
- `main` é protegida: **nunca** commit direto. Cada mudança = ramo + pull request.
- Ramos: `feat/…`, `fix/…`, `docs/…`, `chore/…`.
- Commit e PR com **título e descrição em pt-BR** (padrão `tipo(área): resumo`).
- Descrição do PR diz: o que muda, impacto no site, como revisar.
- Merge é sempre do Cristiano.
- Após cada entrega: atualizar `HANDOFF.md` no mesmo PR.

## Produto
- **Usuário em primeiro lugar.** Mobile-first; computador também bem atendido.
- Inimigo nº 1 é o atrito: se for mais lento que a caneta, o consultor volta ao papel.
- Comunicação com o Cristiano: pt-BR, direta, em fragmentos curtos.

## Técnico
- `index.html` único, JS puro, sem build. Não introduzir framework nem bundler.
- Firebase compat 11 (Auth Google + Firestore). Interface fala com o banco só por `repoLoadAll`, `saveConsultor`, `saveCliente`, `saveOrdemDoc`, `deleteOrdemDoc`, `saveArmacao`, `deleteArmacao`.
- Fotos de armações não vão para o Firebase (Storage exige plano pago): Drive → `ferramentas/fotos` → GitHub.
- OS e recibo: html2pdf. **Nunca** voltar a `window.print()` (quebra no iOS).
- Receita: teclado de calculadora com vírgula automática (padrão Pix) — aprovado; não mexer sem pedido.
- Tela mostra vírgula; armazenamento usa ponto.

## Testes
- Rodar em navegador headless 390×844 com Firebase simulado **tão exigente quanto o real**.
- Teste final é sempre no iPhone real, aba anônima com `?v=N`.

## LGPD
- Receita é dado de saúde (sensível). Minimização: OS sem telefone, endereço, CPF ou valores.
- Nada de dado de cliente em log, commit, issue ou PR.
