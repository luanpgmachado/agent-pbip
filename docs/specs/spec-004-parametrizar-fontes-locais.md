# SPEC-004 - Parametrizar fontes locais

## 1) Identificacao

- Nome curto: `SPEC-004` - Remover dependencia de caminhos locais no refresh.
- Origem: auditoria local em `_review/index.html`, gerada em `2026-05-07`.
- Categoria: Documentacao.
- Severidade: Media.
- Status: Spec criada; implementacao pendente.
- Arquivo de plano: `docs/plans/SPEC-004.md`.

## 2) Problema

Refresh depende de caminhos absolutos de maquina/usuario: `D:\Myrepository\...`, `C:\Users\luanp\Downloads\...`, HTML em OneDrive local. Em outro computador, usuario ou ambiente de publicacao, modelo quebra.

Evidencias:

- `tables/dim_cid.tmdl:32`
- `tables/dim_estabelecimento.tmdl:33`
- `tables/dim_pessoa.tmdl:57`
- `tables/dim_setor_atendimento.tmdl:58`
- `tables/_HTML_Base.tmdl:26`

## 3) Objetivo

Substituir dependencias locais por parametros/fontes controladas. Refresh portavel e documentado.

Resultado esperado:

- Caminhos locais concentrados em parametros quando inevitaveis.
- Fontes compartilhadas preferidas para dimensoes e HTML base.
- Handoff com menor risco de refresh quebrar em ambiente diferente.

## 4) Escopo

Dentro:

- Inventariar caminhos absolutos em queries M.
- Criar parametro `CaminhoBase` ou equivalente quando fonte local necessaria.
- Avaliar migracao de dimensoes para fonte centralizada, dataset, dataflow ou repo controlado.
- Ajustar `_HTML_Base` para evitar dependencia silenciosa de caminho local.
- Documentar fontes que exigem configuracao manual.

Fora:

- Trocar banco principal.
- Alterar logica de indicadores.
- Reestruturar pipeline fora do PBIP.
- Publicar credenciais/segredos.

## 5) Arquivos impactados

- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_cid.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_estabelecimento.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_pessoa.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_setor_atendimento.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/_HTML_Base.tmdl`

## 6) Regras de implementacao

1. Nao versionar segredos/credenciais.
2. Evitar caminhos absolutos de usuario em queries finais.
3. Parametro: nome claro, tipo `Text`, instrucao de preenchimento.
4. Se `_HTML_Base` depender de arquivo local, documentar alternativa de release.
5. Preferir fonte controlada quando arquivo alimentar refresh publicado.

## 7) Criterios de aceite

- `rg "C:\\Users\\|D:\\\\"` no semantic model ativo nao encontra dependencia operacional sem justificativa.
- Parametros necessarios documentados no plano/spec.
- Refresh local funciona apos configurar parametros.
- PBIP entregavel a outro usuario com instrucoes suficientes.

## 8) Plano de validacao

Textual:

- Buscar caminhos absolutos em `definition/tables`.
- Conferir parametros M criados.
- Conferir `_HTML_Base` e dimensoes afetadas.

Funcional:

- Abrir PBIP no Power BI Desktop/Fabric.
- Configurar parametros.
- Executar refresh.
- Confirmar dashboard com HTML esperado.

## 9) Riscos e mitigacoes

- Risco: quebrar refresh ao trocar origem. Mitigacao: preservar query original em rollback antes da mudanca.
- Risco: parametro virar dependencia obscura. Mitigacao: documentar nome, exemplo e ambiente esperado.

## 10) Changelog

- `2026-05-07`: spec criada da issue de Documentacao da auditoria `_review/index.html`.