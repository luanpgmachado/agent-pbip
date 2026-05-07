# SPEC-006 - Descricoes de tabelas e granularidade

## 1) Identificacao

- Nome curto: `SPEC-006` - Documentar papel, origem e granularidade das tabelas.
- Origem: auditoria local em `_review/index.html`, gerada em `2026-05-07`.
- Categoria: Documentacao.
- Severidade: Leve.
- Status: Spec criada; implementacao pendente.
- Arquivo de plano: `docs/plans/SPEC-006.md`.

## 2) Problema

Tabelas principais do dominio sem origem, papel nem granularidade. Herdeiro precisa abrir colunas, relacionamentos e DAX pra entender se e fato assistencial, dimensao conformada ou artefato utilitario.

Evidencias:

- `tables/dim_calendario.tmdl:1`
- `tables/dim_cid.tmdl:1`
- `tables/dim_estabelecimento.tmdl:1`
- `tables/dim_pessoa.tmdl:1`
- `tables/dim_setor_atendimento.tmdl:1`
- `tables/Indicador 02.tmdl:1`

## 3) Objetivo

Adicionar `description:` nas tabelas de negocio com 1-2 frases: origem, papel, granularidade, uso esperado.

Resultado:

- Modelo autoexplicativo.
- Handoff simples.
- Menos ambiguidade fatos/dimensoes/utilitarias.

## 4) Escopo

Dentro:

- Descricao em dimensoes principais.
- Descricao em fatos de indicadores.
- Descricao em utilitarias expostas ao consumo.
- Preservar nomes, colunas, medidas e relacionamentos.

Fora:

- Documentar colunas individualmente.
- Renomear tabelas.
- Alterar queries M.
- Alterar visuais.

## 5) Arquivos impactados

- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_calendario.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_cid.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_estabelecimento.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_pessoa.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_setor_atendimento.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/Indicador 02.tmdl`
- Demais `Indicador NN.tmdl` e utilitarias sem descricao confirmada no inventario.

## 6) Regras de implementacao

1. Descricao declara tipo: dimensao, fato ou utilitaria.
2. Fato cita granularidade.
3. Dimensao cita chave principal e uso em filtros/relacionamentos.
4. Nao inventar origem sem confirmacao; registrar pendencia.
5. Manter pt-BR e termos de negocio.

## 7) Criterios de aceite

- Tabelas principais com `description:` formal.
- Fatos indicam granularidade.
- Dimensoes indicam papel semantico.
- PBIP abre sem erro TMDL.

## 8) Plano de validacao

Textual:

- Listar tabelas sem `description:`.
- Conferir descricao por tabela prioritaria.
- Revisar consistencia com `docs/References/notebook/NOTEBOK.md`.

Funcional:

- Abrir PBIP no Power BI Desktop/Fabric.
- Conferir metadados no modelo.
- Atualizar dashboard; garantir sem regressao.

## 9) Riscos e mitigacoes

- Risco: descricao errar granularidade.
  Mitigacao: cruzar SQL, notebook de referencias e relacionamentos antes de escrever.

- Risco: documentar dimensoes e esquecer fatos novos.
  Mitigacao: inventario de tabelas sem `description:`.

## 10) Changelog

- `2026-05-07`: spec criada da issue de Documentacao da auditoria `_review/index.html`.