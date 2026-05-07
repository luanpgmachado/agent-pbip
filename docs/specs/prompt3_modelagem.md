Status: contrato tecnico historico ainda valido para payload compacto. Validar contra `docs/specs/dashboard_tecnico_manutencao.md` e `_Medidas.tmdl` antes de alterar.

Refatorar `JSON Dashboard Compacto`: sair chaves crípticas (`d/e/s/m`, `gn`, etc.), emitir JSON rastreável por **tabela do modelo** e **nome de coluna**.

Contrato novo (raiz):

- `"meta"`: bloco informativo
- `"Indicador 02"`: array fato TAT
- `"Indicador 06"`: array fato Permanencia
- `"Indicador 13"`: array fato Acuracia
- `"Indicador 14"`: array fato Readmissao
- `"Indicador 15"`: array fato Retorno UTI

Criar/ajustar medidas:

1. `JSON Meta Dashboard`
   - Só bloco `"meta":{...}`
   - Campos:
     - `maxRows` (fixo `1800`)
     - `tatConclusaoCampo = "DT_EVENTO_FINAL"`
     - `totais`: objeto totais reais por tabela (`"Indicador 02"`, `"Indicador 06"`, `"Indicador 13"`, `"Indicador 14"`, `"Indicador 15"`)
     - `truncated`: objeto boolean por tabela, indica truncamento por `maxRows`

2. `JSON TAT Exames` (Indicador 02)
   - Array em `"Indicador 02"` no agregador final
   - Filtro base (exames concluidos): `DT_PRESCRICAO`, `DT_EVENTO_FINAL`, `TAT_HORAS` não nulos
   - Limite `_maxRows = 1800`
   - Só colunas do modelo (sem `COALESCE` multi-campo):
     - `DT_PRESCRICAO` (ISO `yyyy-MM-dd`)
     - `CD_ESTABELECIMENTO`
     - `CD_SETOR_PACIENTE` (grupo ranking)
     - `CD_DOMINIO` (abas: `LABORATORIO`, `IMAGEM`)
     - `CD_MEDICO`
     - `TAT_HORAS`

3. `JSON Permanencia` (Indicador 06)
   - Array em `"Indicador 06"`
   - Só colunas do modelo:
     - `DT_ENTRADA` (ISO `yyyy-MM-dd`)
     - `NR_ATENDIMENTO`
     - `NM_PESSOA_FISICA`
     - `CD_ESTABELECIMENTO`
     - `CD_SETOR_ATENDIMENTO`
     - `CD_CID`
     - `QT_DIA_PERMANENCIA`
     - `MEDIA_QT_DIA_PERMANENCIA_SETOR_CID`

4. `JSON Acuracia Alta` (Indicador 13)
   - Array em `"Indicador 13"`
   - Só colunas do modelo:
     - `DT_ALTA_REAL` (ISO `yyyy-MM-dd`)
     - `CD_SETOR`
     - `CD_MEDICO`
     - `INDICADOR_PERCENTUAL_ACURACIA`
     - `QT_DIF_DIAS_PREVISTO_REAL`

5. `JSON Readmissao` (Indicador 14)
   - Array em `"Indicador 14"`
   - Só colunas do modelo (flags `S/N`):
     - `DT_SAIDA_ORIGEM` (ISO `yyyy-MM-dd`)
     - `CD_ESTABELECIMENTO_ORIGEM`
     - `DS_SETOR_ATENDIMENTO_RETORNO`
     - `NM_MEDICO_RETORNO`
     - `IE_DENOMINADOR_7_DIAS`
     - `IE_READMISSAO_7_DIAS`
     - `IE_DENOMINADOR_30_DIAS`
     - `IE_READMISSAO_30_DIAS_TOTAL`

6. `JSON Retorno UTI` (Indicador 15)
   - Array em `"Indicador 15"`
   - Só colunas do modelo (flag `S/N`):
     - `DT_ENTRADA_RETORNO_UTI` (ISO `yyyy-MM-dd`)
     - `CD_ESTABELECIMENTO`
     - `CD_SETOR_ATENDIMENTO`
     - `CD_MEDICO`
     - `IE_READMISSAO_UTI_48H`
     - `QT_HORAS_ATE_RETORNO_UTI`

7. `JSON Dashboard Compacto`
   - Medida final: concatena `"meta"` + arrays por tabela

Regras:
- Sem mistura de significados no mesmo campo (ex.: "Grupo de exame" não alterna entre 3 colunas).
- Coluna `null/blank` → manter `null/blank` no JSON (sem fallback `"-"`/`"Outros"`).
- Derivações (ex.: `fora`, `desvio`, `% > SLA`) calcular no `dashboard_template.html` a partir das colunas base.
