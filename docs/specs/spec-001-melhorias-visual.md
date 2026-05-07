# SPEC-001 — Template de Especificação (Formato Perguntas)

> Baseado em boas práticas de documentação/instrução da OpenAI: clareza de objetivo, contexto explícito, saída estruturada, exemplos, critérios de validação e ciclo iterativo.

## 1) Identificação

- Nome curto da iniciativa/feature?
- Ticket relacionado (ex.: `DEV-XXX`)?
- Quem aprova esta spec?
- Data de criação e última atualização?

## 2) Problema e Objetivo

- Qual problema resolver?
- Quem sente esse problema?
- Qual resultado de negócio esperado?
- Como saber que problema foi resolvido?

## 3) Escopo

- O que está dentro do escopo?
- O que está fora do escopo?
- Quais dependências externas podem impactar entrega?

## 4) Contexto e Dados de Entrada

- Quais páginas, visuais, medidas ou tabelas impactadas?
- Quais arquivos do repositório alterar?
- Quais restrições técnicas (tema, layout, performance, acessibilidade) respeitar?
- Quais premissas assumimos como verdade?

## 5) Requisitos Funcionais (Em Perguntas)

- Que comportamento o usuário executa após mudança?
- Quais filtros/interações obrigatórios?
- Quais estados de UI existem (carregando, vazio, erro, sucesso)?
- O que acontece quando dados não atendem cenário esperado?

## 6) Requisitos Não Funcionais (Em Perguntas)

- Tempo máximo de resposta/renderização aceitável?
- Quais padrões visuais obrigatórios seguir (`thema.json`, grid, espaçamento, tipografia)?
- Critérios mínimos de legibilidade e acessibilidade?
- Limites de manutenção/simplicidade técnica a preservar?

## 7) Instruções de Implementação (Clareza Operacional)

- Quais passos de implementação, em ordem?
- Quais regras são mandatórias?
- Quais decisões registrar em trade-off?
- Quais partes configuráveis versus fixas?

## 8) Formato de Saída Esperado

- Quais artefatos finais ao término (arquivos, medidas, visuais, documentação)?
- Como apresentar resultado para validação?
- Estrutura mínima do entregável (seções, checklist, evidências)?

## 9) Exemplos (Few-shot)

- Exemplo de entrada: como pedido chega?
- Exemplo de saída boa: como deve ficar?
- Exemplo de saída ruim: o que evitar?
- Quais padrões de qualidade esses exemplos deixam explícitos?

## 10) Critérios de Aceite (Checklist Objetivo)

- Quais critérios mensuráveis definem "pronto para uso"?
- Quais verificações obrigatórias no Power BI devem passar?
- Quais validações de consistência de dados/medidas necessárias?
- Quais evidências (prints, GIFs, notas técnicas) acompanham?

## 11) Riscos, Edge Cases e Mitigações

- Quais cenários extremos quebram a solução?
- Quais riscos de regressão nos visuais atuais?
- Como mitigar cada risco antes de publicar?
- Qual plano de rollback se algo der errado?

## 12) Plano de Testes e Validação

- Quais testes funcionais executar manualmente?
- Quais cruzamentos/filtros críticos validar?
- Quais resultados esperados por teste?
- Quem valida e dá aceite final?

## 13) Plano de Rollout

- Publicação total ou gradual?
- Plano de comunicação para usuários impactados?
- Como monitorar pós-publicação?
- Prazo para revisão pós-implantação?

## 14) Iteração e Aprendizado

- O que medir após release?
- Qual feedback de usuário coletar e como?
- Quando revisitar esta spec?
- Quais melhorias mapeadas para próxima versão?

## 15) Campos para Preenchimento Rápido

Preencha em 1-3 linhas por item:

- Resumo executivo:
- Objetivo principal:
- Top 3 entregáveis:
- Top 3 riscos:
- Critério de aceite mais importante:
- Data alvo de entrega:

## Changelog

- `2026-05-06`: criação do template-base em formato de perguntas, orientado a boas práticas da OpenAI.