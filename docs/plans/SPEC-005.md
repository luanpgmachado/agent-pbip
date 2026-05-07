# Plano - SPEC-005 (Descricoes formais nas medidas)

## Objetivo

Adicionar `description:` formal nas medidas do modelo sem alterar DAX.

## Checklist

- [x] Extrair issue de Documentacao da auditoria `_review/index.html`.
- [x] Criar spec operacional em `docs/specs/spec-005-descricoes-medidas-tmdl.md`.
- [ ] Inventariar medidas sem `description:`.
- [ ] Escrever descricao curta por medida.
- [ ] Aplicar descricoes em `_Medidas.tmdl`.
- [ ] Validar diff para garantir que DAX nao mudou.
- [ ] Abrir PBIP no Power BI Desktop/Fabric e validar metadados.

## Evidencias iniciais

- Issue: `32 medidas seguem sem description: formal no TMDL`.
- Severidade: Leve.
- Arquivo: `tables/_Medidas.tmdl:6`.

## Status

- Spec criada `2026-05-07`.
- Implementacao pendente.

## Proximo passo

Contar medidas. Mapear descricoes a partir do DAX real antes de editar TMDL.