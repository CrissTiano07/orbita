# Órbita

Atendimento ótico a domicílio, do celular do consultor: cadastro do cliente, receita, medições, ordem de serviço (OS) e recibo em PDF prontos para o WhatsApp.

**No ar:** https://crisstiano07.github.io/orbita/

## Stack
- `index.html` único · HTML/CSS/JS puro, sem build
- Firebase compat 11 · Auth Google + Firestore (`orbita-b2b55`, `southamerica-east1`), offline ligado
- html2pdf · OS e recibo em PDF (funciona no iOS)
- GitHub Pages · deploy automático a cada commit na `main`

## Documentação — ler antes de mexer
| Arquivo | Para quê |
|---|---|
| [`HANDOFF.md`](HANDOFF.md) | Estado atual, últimas entregas e próximos passos |
| [`BUSINESS-RULES.md`](BUSINESS-RULES.md) | Regras que o sistema deve respeitar |
| `CONTEXT_ORBITA 1.md` / `2.md` | Histórico e porquês das decisões |
| [`ferramentas/fotos/`](ferramentas/fotos/) | Script que padroniza as fotos do catálogo de armações |

## Fluxo de mudança
Ler o HANDOFF → mudar → testar no celular real (aba anônima, `?v=N`) → commit com título e descrição → atualizar o HANDOFF.

---
Desenvolvido por Cristiano · Fortaleza
