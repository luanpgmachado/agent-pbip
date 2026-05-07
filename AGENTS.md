# Repository Guidelines

## Project Structure & Module Organization
Repo usa formato **PBIP** (texto) para Power BI.

- `Desospitalização_Projeto_2026_03_25.pbip`: manifesto do projeto.
- `powerbi\pbip\Desospitalização_Projeto_2026_03_25.Report\definition`: páginas, visuais e metadados do relatório.
- `powerbi\pbip\Desospitalização_Projeto_2026_03_25.SemanticModel\definition`: modelo semântico (TMDL), tabelas e relacionamentos.
- `powerbi\pbip\Desospitalização_Projeto_2026_03_25.SemanticModel\definition\tables/*.tmdl`: um arquivo por tabela/medidas.
- `thema.json`: tema visual.
- `docs/specs/<ESPECIFICACOES>`: documentação funcional e técnica (spec).
- `docs/References/REFERENCES.md`: indice de arquivos externos de referencia para construcao dos indicadores.
- `docs/References/notebook/NOTEBOK.md`: segundo cerebro dos notebooks de engenharia; linhagem, schema e mapa `Indicador NN` -> tabela real.
- `docs/GUIA_MEDIDAS_DASHBOARD_V2.md`: dicionario executivo de cards/medidas do dashboard V2; atualizar quando medida, card, meta ou regra visual mudar.
- `docs/DEVOPS_RESUMO_DASHBOARD_CONSTRUIDO.md`: handoff/release notes para DEVOPS; nao e fonte de verdade de modelagem.
- `PLAN.md` (indice) e `docs/plans/`: planejamento de execucao.

## Build, Test, and Development Commands
Sem pipeline build/test automatizado.

- Abrir projeto: abra `Desospitalização_Projeto_2026_03_25.pbip` no Power BI Desktop/Fabric.
- Validar mudanças: atualize e renderize no Power BI após editar `.tmdl`/`.json`.
- Buscar objetos: `rg "measure|relationship|Indicador"` (ou PowerShell equivalente).
- Linhagem de indicadores: `docs/References/notebook/NOTEBOK.md`.
- Cards/medidas Dashboard V2: `docs/GUIA_MEDIDAS_DASHBOARD_V2.md`.

## Coding Style & Naming Conventions
- Edite `.tmdl` e `.json` com indentação de 4 espaços.
- Preserve `locale` `pt-BR` em nomes e formatos.
- Prefixos de colunas: `CD_` (chave/código), `DT_` (data/hora), `NR_` (identificador), `QT_` (quantidade).
- Medidas DAX: nomes de negócio claros, ex.: `'Tempo Médio Permanência'`.
- Não renomear tabelas/campos sem alinhar impacto nos visuais.

## Testing Guidelines
- Teste funcional no Power BI: atualizar consultas; validar relacionamentos ativos/inativos; conferir filtros, cartões e visuais por seção.
- Mudanças em `relationships.tmdl`: validar ambiguidade de datas antes de publicar.
- Sem cobertura automatizada no estado atual.

## Workflow (Spec -> Plan)
Fluxo: `spec -> plan -> implementar -> validar -> arquivar`.

Regra padrão (não perguntar a cada vez): quando alteração fizer parte desse fluxo (medidas DAX/TMDL, contratos JSON, IDs de container, render), agent atualiza na mesma sessão:
  - `PLAN.md` (status 1-3 linhas por ticket)
  - `docs/plans/<TICKET>.md` (checkboxes + progresso)
- Ticket Linear presente (ex.: `DEV-225`): manter comentário de histórico com resumo e próximos passos; apontar para arquivos do repo ao invés de colar blocos grandes.

### Hábito: Um Plano Por Issue
Economizar contexto, evitar "plan sprawl":
- `docs/plans/<TICKET>.md` existe → **atualizar**, não criar novo.
- Contratos técnicos (ex.: "Contrato JSON") → **seção dentro de `docs/plans/<TICKET>.md`**, não arquivo paralelo.
- Novo arquivo em `docs/plans/` **somente** para issue diferente (`DEV-XXX` distinto) ou plano transversal (ex.: `2026-Q2.md`); sempre linkar no `PLAN.md`.

Higiene de contexto:
- `docs/specs/`: evergreen, muda pouco; registrar mudanças em `## Changelog` curto.
- `docs/References/`: origem/engenharia dos indicadores; manter `REFERENCES.md` e `notebook/NOTEBOK.md` sincronizados ao adicionar referências.
- `docs/specs/SQL_INDICADORES.md` e prompts antigos são legado: não usar como fonte de schema quando `NOTEBOK.md` tiver dado equivalente.
- `docs/GUIA_MEDIDAS_DASHBOARD_V2.md`: acompanhar specs/plans que alterem medidas, metas, flags, cards, payload ou leitura de negocio.
- Planos detalhados em `docs/plans/` (um por ticket); `PLAN.md` não vira diário longo.

### Integração Obsidian
Vault Obsidian do projeto: `PINK/`.

Repo é a fonte executável e operacional; Obsidian é camada humana para hub, decisões, reuniões, glossário, resumos de release e links.
- Não duplicar DAX, schema completo, SQL inteiro, payload JSON completo ou planos longos no Obsidian.
- Obsidian deve apontar para `AGENTS.md`, `PLAN.md`, `docs/specs/`, `docs/plans/`, `docs/References/notebook/NOTEBOK.md`, `docs/GUIA_MEDIDAS_DASHBOARD_V2.md` e `docs/specs/dashboard_tecnico_manutencao.md`.
- Se o CLI Obsidian não estiver disponível, editar Markdown diretamente em `PINK/` e manter bootstrap em `docs/obsidian-bootstrap/` como espelho inicial.

Organização de concluídos:
- Ativos ficam em `docs/specs/` e `docs/plans/`.
- Concluídos podem ir para `docs/archive/specs/` e `docs/archive/plans/` após compressão.
- `PLAN.md` mantém só linha curta com link do arquivo ativo ou arquivado.

## Commit & Pull Request Guidelines
Sem histórico Git disponível. Adotar:

- Conventional Commits: ex.: `feat(model): add Indicador 13 measures`.
- Um commit por unidade lógica (modelo, visuais, tema, documentação).
- PR incluir: objetivo, arquivos alterados, impacto esperado e evidências visuais (prints/GIF) para mudanças de frontend.
- Referenciar ticket/issue e descrever riscos de regressão em medidas DAX.

## Security & Configuration Tips
- Não versionar segredos, credenciais ou caminhos locais de fonte de dados.
- Manter fora de versionamento: `**/.pbi/localSettings.json`, `**/.pbi/cache.abf`.
