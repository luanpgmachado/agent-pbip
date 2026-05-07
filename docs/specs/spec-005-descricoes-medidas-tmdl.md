# SPEC-005 - Descricoes formais nas medidas

## 1) Identificacao

- Nome curto: `SPEC-005` - Adicionar `description:` nas medidas do modelo.
- Origem: auditoria local em `_review/index.html`, gerada em `2026-05-07`.
- Categoria: Documentacao.
- Severidade: Leve.
- Status: Spec criada; implementacao pendente.
- Arquivo de plano: `docs/plans/SPEC-005.md`.

## 2) Problema

Medidas tem `///` mas sem `description:` formal no TMDL. Comentario ajuda leitor; `description:` alimenta catalogo, lineage, handoff e experiencia de consumo.

Evidencia:

- `tables/_Medidas.tmdl:6`
- `32` medidas sem `description:`.

## 3) Objetivo

Adicionar descricoes curtas, formais e de negocio nas medidas, priorizando expostas em cards, KPIs e JSONs.

Resultado:

- Medidas com significado claro no modelo semantico.
- Melhor handoff para analistas e negocio.
- Menor dependencia de leitura DAX para entender uso.

## 4) Escopo

Dentro:

- Inventariar medidas sem `description:`.
- Adicionar descricao objetiva por medida.
- Priorizar medidas executivas, operacionais, TAT, permanencia, acuracia, readmissao, UTI e JSONs.
- Preservar DAX existente.

Fora:

- Refatorar DAX.
- Renomear medidas.
- Alterar calculos.
- Criar novas medidas.

## 5) Arquivos impactados

- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/_Medidas.tmdl`

## 6) Regras de implementacao

1. Descricoes em portugues de negocio.
2. Uma frase por medida.
3. Explicar filtro/base quando muda interpretacao.
4. Nao duplicar comentario tecnico longo.
5. Nao alterar DAX, salvo formatacao minima inevitavel.

## 7) Criterios de aceite

- Todas medidas em `_Medidas.tmdl` com `description:`.
- Descricoes explicam resultado e contexto principal.
- Nenhuma expressao DAX alterada indevidamente.
- PBIP abre sem erro TMDL.

## 8) Plano de validacao

Textual:

- Contar medidas em `_Medidas.tmdl`.
- Contar `description:` associadas.
- Revisar amostra para clareza.

Funcional:

- Abrir PBIP no Power BI Desktop/Fabric.
- Conferir tooltip/metadata de medidas no modelo.
- Atualizar dashboard; verificar ausencia de regressao.

## 9) Riscos e mitigacoes

- Risco: descricao prometer regra diferente do DAX.
  Mitigacao: ler expressao antes de escrever descricao.

- Risco: alterar DAX por acidente.
  Mitigacao: comparar diff; limitar mudanca a `description:`.

## 10) Changelog

- `2026-05-07`: spec criada da issue Documentacao da auditoria `_review/index.html`.