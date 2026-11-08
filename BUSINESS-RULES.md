# BUSINESS-RULES · Órbita

> Regras que o sistema **deve** respeitar. Mudar qualquer uma exige decisão explícita do Cristiano.
> Origem dos porquês: `CONTEXT_ORBITA 1.md` e `CONTEXT_ORBITA 2.md`.

## Dados e segurança
- R1 · Dados namespaced por consultor: `consultores/{uid}/...`. Regra Firestore: só `auth.uid == uid` lê/escreve.
- R2 · Firestore em `southamerica-east1` (dado no Brasil). Projeto `orbita-b2b55`, separado do NIT.
- R3 · Interface nunca fala com o banco direto: só pelas funções `repoLoadAll`, `saveConsultor`, `saveCliente`, `saveOrdemDoc`, `deleteOrdemDoc`.
- R4 · Persistência offline ligada (visita com sinal ruim grava e sincroniza depois).

## LGPD
- R5 · Consentimento LGPD obrigatório para salvar a OS, com carimbo por OS.
- R6 · Consultor = Controlador; plataforma = Operador.
- R7 · Telefone, endereço, CPF e valores do cliente **não** vão na OS (vai ao laboratório). Valores só no recibo.
- R8 · Prazo **não** é impresso pelo consultor — é do laboratório.

## Receita
- R9 · Faixas: esférico/cilíndrico até 30 dioptrias (passo 0,25); eixo 0–180°; adição positiva (aviso acima de +4,00).
- R10 · Notação BR na saída: vírgula, eixo com °, "plano"/"Sem correção" quando vazio.
- R11 · Cilíndrico vazio começa com sinal **−**; o operador troca com um toque.
- R12 · OE = OD copia valores, mas o operador **sempre confere e confirma**.

## Entrada de dados (UX)
- R13 · Número clínico → modal-teclado; escolha → toque (chips/lista); texto → teclado nativo.
- R14 · Receita: teclado de calculadora com vírgula automática (padrão Pix: dígitos entram pela direita; − 0 2 5 = −0,25; tecla 00 para inteiros). Só quartos: não avança fora de ,00 ,25 ,50 ,75. Primeira tecla em campo recém-aberto substitui o valor. O outro olho fica visível para conferência. Medições: passo ±0,5 mm.
- R14a · Eixo só existe com cilíndrico ≠ 0; sem cilíndrico, o eixo não é editado nem salvo.
- R14b · Exibição na tela com vírgula; armazenamento com ponto (formato numérico).
- R15 · Barra de ação some durante a digitação (`body.typing`).
- R16 · Inimigo nº 1 é o atrito: se for mais lento que a caneta, o consultor volta ao papel.

## OS e documentos
- R17 · OS e recibo saem como **PDF** (html2pdf). **Não** voltar a `window.print()` — quebra no iOS.
- R18 · OS em paisagem meia-folha; recibo em retrato.
- R19 · Sem fundos cinza; rótulos em preto sólido; só barras pretas do status e do "Uso do laboratório".
- R20 · Numeração sequencial por consultor (`OS-000047`).
- R21 · Emitente em Ajustes = dados da **ótica** (nome e CNPJ), nunca dado pessoal.

## Armações (catálogo)
- R22 · Ref sequencial `ORB-0001`, nunca reaproveitada enquanto existir; é o nome do arquivo da foto e o id no banco.
- R23 · Obrigatórios no cadastro: modelo, formato e medidas da haste (lente, ponte, haste). Sem preço.
- R24 · Tamanho: largura total ≤129 mm = P · 130–139 = M · ≥140 = G. Sem largura total, estimar 2×lente + ponte + 8 mm e mostrar "(estimada)".
- R25 · Teto de armações cadastradas (padrão 200, ajustável em Ajustes). No teto, não cadastra; vendida ou fora de linha sai do cadastro e do catálogo.
- R26 · Até 3 fotos por armação: frente, lado, rosto. Fotos fora do Firebase (Drive → script → GitHub) até decisão do piloto.

