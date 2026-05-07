# SPEC-003 - Chaves explicitas nas dimensoes

## 1) Identificacao

- Nome curto: `SPEC-003` - Marcar chaves formais das dimensoes no TMDL.
- Origem: auditoria local em `_review/index.html`, gerada em `2026-05-07`.
- Categoria: Documentacao.
- Severidade: Media.
- Status: Spec criada; implementacao pendente.
- Arquivo de plano: `docs/plans/SPEC-003.md`.

## 2) Problema

Dimensoes principais sem chave formal `isKey: true` no TMDL. Semantica fraca, leitura ambigua para handoff, catalogo e manutencao.

Evidencias da auditoria:

- `tables/dim_calendario.tmdl:1`
- `tables/dim_cid.tmdl:1`
- `tables/dim_estabelecimento.tmdl:1`
- `tables/dim_pessoa.tmdl:1`
- `tables/dim_setor_atendimento.tmdl:1`

Obs: `dim_calendario[dt_data]` corrigida na `SPEC-002`; esta spec valida esse estado e aplica mesmo padrao nas demais.

## 3) Objetivo

Marcar coluna-chave de cada dimensao. Melhora semantica, lineage e manutencao.

Resultado esperado:

- Todas dimensoes com coluna-chave clara.
- Modelo mais direto para novos analistas.
- Menor risco de relacionamento futuro apontar coluna errada.

## 4) Escopo

Dentro:

- Validar `dim_calendario[dt_data]` com `isKey: true`.
- Adicionar `isKey: true` em `dim_cid[CD_CID]`.
- Adicionar `isKey: true` em `dim_estabelecimento[cd_estabelecimento]`.
- Adicionar `isKey: true` em `dim_pessoa[Pessoa___Codigo]`.
- Adicionar `isKey: true` em `dim_setor_atendimento[cd_setor_atendimento]`.
- Validar se cada chave ja tem ou deve ter `isUnique`.
- Atualizar plano com evidencias.

Fora:

- Renomear colunas.
- Alterar relacionamentos de fatos.
- Criar novas dimensoes.
- Refatorar naming geral.

## 5) Arquivos impactados

- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_calendario.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_cid.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_estabelecimento.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_pessoa.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_setor_atendimento.tmdl`

## 6) Regras de implementacao

1. Nao marcar atributo descritivo como chave.
2. Confirmar coluna usada nos relacionamentos antes de inserir `isKey: true`.
3. Manter `summarizeBy: none` em chaves textuais/codigos.
4. Duplicidade real na dimensao: nao forcar `isUnique`; registrar risco e corrigir origem antes.
5. Validar que `dim_calendario[dt_data]` permanece com `isKey: true` apos `SPEC-002`.

## 7) Criterios de aceite

- Cada dimensao com exatamente uma chave formal `isKey: true`.
- Chaves correspondem a campos em `relationships.tmdl`.
- Nenhuma medida ou visual quebra (spec nao renomeia campos).
- PBIP abre no Power BI Desktop/Fabric sem erro de modelagem.

## 8) Plano de validacao

Textual:

- Conferir `isKey: true` nos cinco arquivos de dimensao.
- Conferir `relationships.tmdl` para confirmar colunas-chave.

Funcional:

- Abrir PBIP no Power BI Desktop/Fabric.
- Atualizar modelo.
- Conferir diagram view e relacionamentos principais.

## 9) Riscos e mitigacoes

- Risco: dimensao com chave duplicada. Mitigacao: validar unicidade antes de assumir `isUnique`.
- Risco: chave errada por diferenca de naming. Mitigacao: usar `relationships.tmdl` como fonte.

## 10) Changelog

- `2026-05-07`: spec criada a partir da issue de Documentacao da auditoria `_review/index.html`.