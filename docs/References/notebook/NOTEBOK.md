# NOTEBOK - Segundo Cerebro dos Notebooks

Fonte canonica de linhagem/schema dos notebooks externos em `docs/References/notebook/`. Use antes de specs antigas. Notebooks = referencia de engenharia, nao codigo-fonte PBIP.

## Mapa Dashboard -> Notebook

| Dashboard | Notebook / `PIPELINE_NAME` | Tabela PBIP | Tema |
|---|---|---|---|
| `Indicador 02` | `fato_exame_prescricao` | `Indicador 02` | TAT prescricao -> resultado/coleta exame |
| `Indicador 06` | `fato_desospitalizacao_permanencia_cid_setor` | `Indicador 06` | Permanencia por setor + CID |
| `Indicador 12` | `fato_desospitalizacao_outliers_pendencias` | `Indicador 12` | Outliers permanencia + pendencias |
| `Indicador 13` | `fato_desospitalizacao_acuracia_alta` | `Indicador 13` | Acuracia previsao alta |
| `Indicador 14` | `fato_desospitalizacao_readmissao` | `Indicador 14` | Readmissao 7/30 dias |
| `Indicador 15` | `fato_desospitalizacao_readmissao_uti` | `Indicador 15` | Retorno UTI 48h |

## Padrao Comum

- Fatos: `get_DF_from_source(spark, QUERY)` -> `dropDuplicates(PK_NATURAL)` quando existe -> `dt_carga` -> `SCHEMA_FINAL` quando declarado -> `write_to_dw(df, output_path)`.
- Dimensoes: Delta `LAKE_HOME/stage_extract_*` -> enriquecimento -> surrogate via `create_surrogate_key_index(...)` -> DW.
- Watermark existe (`load_watermark_delta`/`write_watermark_delta`), mas fatos aqui sao cargas por consulta completa de referencia.
- `SCHEMA_FINAL = None`: schema inferido do `SELECT` final e validado contra TMDL quando tabela existe no PBIP.

## Dimensoes

| Notebook | Pipeline | Fontes | Chave/saida | Observacao PBIP |
|---|---|---|---|---|
| `dim_cid_doenca.py` | `dim_cid_doenca` | `stage_extract_cid_doenca` | `_id`, `CID___Codigo`, `CID___Descricao`, `CID___Codigo_Descricao`, `CID___Key` | PBIP usa `dim_cid`: `CD_CID`, `DS_CID`, `DS_CID_ORIGINAL`. |
| `dim_estabelecimento.py` | `dim_estabelecimento` | `stage_extract_estabelecimento`, `stage_extract_pessoa_juridica` | `_id`, `Estabelecimento___Codigo`, `Estabelecimento___CNPJ`, `Estabelecimento___Nome_Razao_Social`, `Estabelecimento___Nome_Fantasia`, `Estabelecimento___Key` | PBIP simplifica para `cd_estabelecimento`, `nm_razao_social`, `nm_estabelecimento`. |
| `dim_pessoa.py` | `dim_pessoa` | `stage_extract_compl_pessoa_fisica`, `stage_extract_pessoa_fisica`, `stage_extract_pessoa_juridica`, `dim_municipio` | `_id`, pessoa/cpf/cnpj/municipio/email/nascimento/tipo/sexo/idade/faixa, `Pessoa___Key` | PBIP reduz para `Pessoa___Codigo`, `Pessoa___Nome`, `Pessoa___Idade`, `Pessoa___Sexo`, `Pessoa___Tipo`, `Pessoa___Faixa_Etaria`. |
| `dim_setor_atendimento.py` | `dim_setor_atendimento` | `stage_extract_setor_atendimento`, `stage_extract_centro_custo`, dominio classificacao, SQL `TASY.setor_atendimento` | `_id`, setor, centro custo, classificacao, qt unidades, descricoes compostas, `Setor_Atendimento___Key` | PBIP usa nomes simples: `cd_setor_atendimento`, `ds_setor_atendimento`, `Centro_Custo___Codigo`, `cd_classif_setor`, `ds_classif_setor`. |

## Indicador 02 - `fato_desospitalizacao_tat_exame.py`

Pipeline: `fato_exame_prescricao`. Tabela PBIP: `Indicador 02`. PK: `["nr_prescricao"]`.

Fontes: `tasy.prescr_medica`, `tasy.prescr_procedimento`, `tasy.atendimento_paciente`, `tasy.atend_paciente_unidade`, `tasy.setor_atendimento`, `tasy.exame_lab_resultado`, `tasy.exame_laboratorio`, `tasy.material_exame_lab`, `tasy.laudo_paciente`, `tasy.procedimento`, `tasy.convenio`, `tasy.medico`, `tasy.lab_parametro`, `tasy.paciente_senha_fila`, `tasy.atend_categoria_convenio`.

Logica: CTEs de parametros/prescricao/laudo/resultado/consolidacao; calcula datas reais de resultado/coleta/evento final; gera `TAT_RESULTADO_HORAS`, `TAT_COLETA_HORAS`, `TAT_HORAS`, arredondamentos e flags fallback.

Schema:
- Chaves/contexto: `NR_PRESCRICAO`, `CD_PROTOCOLO`, `NR_SEQ_PROTOCOLO`, `CD_ESTABELECIMENTO`, `NR_ATENDIMENTO`, `CD_MEDICO`, `CD_CID`.
- Datas: `DT_PRESCRICAO`, `DT_LIBERACAO`, `DT_LIBERACAO_MEDICO`, `DT_ENTRADA`, `DT_NASCIMENTO`, `DT_MESTRUACAO`, `DT_ULTIMA_DOSE`, `DT_VALIDADE_CARTEIRA`, `DT_RESULTADO`, `DT_RESULTADO_IMAGEM`, `DT_EXAME_IMAGEM`, `DT_LIBERACAO_IMAGEM`, `DT_APROVACAO_IMAGEM`, `DT_COLETA_DATA`, `DT_RESULTADO_ER`, `DT_LIBERACAO_ER`, `DT_RESULTADO_LIBERACAO_ER`, `DT_EVENTO_FINAL`.
- Paciente/medico/convenio/setor/endereco: `NM_PACIENTE`, `NM_PACIENTE_SEM_ACENTO`, `IE_SEXO`, `QT_PESO`, `NM_PESSOA_RESPONSAVEL`, `NR_CPF_RESP`, `NR_CPF`, `NR_TELEFONE_RESP`, `NR_PRONTUARIO`, `NM_MAE`, `NM_SOCIAL`, `NM_MEDICO`, `NR_CPF_MEDICO`, `NR_CRM`, `UF_CRM`, `CD_CONVENIO`, `CD_CATEGORIA`, `DS_CONVENIO`, `CD_CGC_CONV`, `CD_REGIONAL_CONV`, `CD_SETOR_PACIENTE`, `DS_SETOR_PACIENTE`, `CD_UNIDADE`, `CD_ESTABELECIMENTO_FILTRO`.
- Exame/flags/metricas: `IE_RECEM_NATO`, `CD_PROCEDENCIA`, `DS_SENHA`, `QT_ALTURA_CM`, `QT_DOSE`, `DS_MEDICAMENTO_USO`, `IE_TIPO_ATENDIMENTO`, `COR_PELE`, `DS_CLASSIFIC_PA`, `IE_STATUS_EXECUCAO`, `CD_DOMINIO`, `QT_RESULTADO_ER`, `TAT_RESULTADO_HORAS`, `TAT_COLETA_HORAS`, `TAT_HORAS`, `TAT_HORAS_ARRED`, `TAT_DAY_ARRED`, `ORIGEM_EVENTO_TAT`, `FL_SEM_DATA_RESULTADO_REAL`, `FL_USOU_FALLBACK_COLETA`.

Modelagem: usar `DT_EVENTO_FINAL` como data executiva do TAT. Dashboard ja alinha card/detalhe por esse criterio.

## Indicador 06 - `fato_desospitalizacao_permanencia_cid_setor.py`

Pipeline/tabela: `fato_desospitalizacao_permanencia_cid_setor` -> `Indicador 06`. PK: `["nr_atendimento", "nr_seq_interno", "ie_ordem"]`.

Fontes: ocupacao/atendimento TASY, `tasy.pessoa_fisica`, `tasy.diagnostico_doenca`, setores, parametros auxiliares.

Logica: preserva query base de ocupacao; consolida variantes internacao/leito; CID preferencial; calcula `AVG`, `MEDIAN`, `COUNT` por `cd_setor_atendimento + cd_cid`.

Schema:
- Chaves: `NR_ATENDIMENTO`, `CD_ESTABELECIMENTO`, `CD_PESSOA_FISICA`, `CD_SETOR_ATENDIMENTO`, `CD_CID`, `NR_SEQ_INTERNO`, `IE_ORDEM`.
- Datas: `DT_ENTRADA_UNIDADE`, `DT_ENTRADA`, `DT_NASCIMENTO`, `DT_INICIO_HIGIENIZACAO`, `DT_HIGIENIZACAO`, `DT_PREVISTO_ALTA`, `DT_ALTA_MEDICO`, `dt_carga`.
- Paciente/leito/convenio: `CD_UNIDADE`, `CD_UNIDADE_BASICA`, `CD_UNIDADE_COMPL`, `NM_PESSOA_FISICA`, `NR_PRONTUARIO`, `IE_STATUS_UNIDADE`, `IE_SEXO`, `IE_SEXO_PACIENTE`, `IE_SEXO_FIXO`, `DS_STATUS_UNIDADE`, `DS_CONVENIO`, `DS_CATEGORIA`, `CD_PACIENTE_RESERVA`, `NM_PACIENTE_RESERVA`, `CD_CONVENIO_RESERVA`, `NM_USUARIO_RESERVA`, `CD_CONVENIO`.
- Medico/status: `NR_CRM`, `NM_GUERRA`, `CD_MEDICO_RESP`, `CD_MEDICO_REFERIDO`, `IE_PROBABILIDADE_ALTA`, `DS_PROBABILIDADE`, `CD_MOTIVO_ALTA_MEDICA`.
- Metricas/outros: `QT_DIA_PERMANENCIA`, `MEDIA_QT_DIA_PERMANENCIA_SETOR_CID`, `MEDIANA_QT_DIA_PERMANENCIA_SETOR_CID`, `QT_REGISTROS_SETOR_CID`, `QT_PESO_MAXIMO`, `QT_ALTURA_MAXIMA`, `QT_TEMPO_PREV_HIGIEN`, `IE_CLASSE_ACOMODACAO`, `DS_OBSERVACAO`, `NM_USUARIO_HIGIENIZACAO`, `NM_USUARIO_FIM_HIGIENIZACAO`, `NR_RAMAL`, `IE_TEMPORARIO`, `IE_TIPO_RESERVA`, `CD_TIPO_ACOMODACAO`, `CD_PSICOLOGO`, `DS_OCUPACAO`, `NR_AGRUPAMENTO`, `NR_SEQ_MOTIVO_RESERVA`, `IE_ACOMPANHANTE`, `NR_SEQ_APRESENT`, `IE_RADIOTERAPIA`, `NR_ATEND_ALTA`, `IE_INTERDITADO_RADIACAO`, `NR_SEQ_PERFIL`, `IE_CARATER_INTER_SUS`, `NR_SEQ_LOCAL_PA`, `IE_PACIENTE_ISOLADO`, `NR_SEQ_ATEPACU`.

Modelagem: medias/medianas SQL sao referencia estatica setor+CID. Para filtro dinamico, criar medida DAX e documentar diferenca.

## Indicador 12 - `fato_desospitalizacao_outliers_pendencias.py`

Pipeline/tabela: `fato_desospitalizacao_outliers_pendencias` -> `Indicador 12`. PK: `["nr_atendimento"]`.

Fontes: base similar Indicador 06, `tasy.diagnostico_doenca`, `tasy.adep_pend_v`, `tasy.setor_atendimento`.

Logica: calcula permanencia por setor+CID; media/mediana grupo; filtra outliers; ranqueia/concatena pendencias por atendimento.

Schema: `NR_ATENDIMENTO`, `NM_PACIENTE`, `DS_SETOR_ATENDIMENTO`, `CD_CID`, `QT_DIA_PERMANENCIA`, `MEDIA_SETOR_CID`, `MEDIANA_SETOR_CID`, `DIAS_ACIMA_MEDIA`, `DIAS_ACIMA_MEDIANA`, `FLAG_OUTLIER`, `QT_PENDENCIAS`, `DS_PRINCIPAIS_PENDENCIAS`, `NM_RESPONSAVEL_PENDENCIA`, `DS_AREA_PENDENCIA`, `DS_STATUS_PENDENCIA`, `dt_carga`.

Modelagem: sem `CD_ESTABELECIMENTO` e sem codigo setor final; cruzar por `NR_ATENDIMENTO`, `CD_CID`, descricao setor.

## Indicador 13 - `fato_desospitalizacao_acuracia_alta.py`

Pipeline/tabela: `fato_desospitalizacao_acuracia_alta` -> `Indicador 13`. PK: `["nr_atendimento"]`.

Fontes: `tasy.atendimento_paciente`, `tasy.atend_paciente_unidade`, `tasy.atend_previsao_alta`, `tasy.pessoa_fisica`.

Logica: atendimento com alta real; escolhe previsao mais relevante via ranking; compara `dt_prevista_alta` vs `dt_alta_real`; flags acerto exato/tolerancia +/- 1 dia; percentual 0/100.

Schema: `NR_ATENDIMENTO`, `CD_PACIENTE`, `CD_MEDICO`, `CD_SETOR`, `PACIENTE`, `DT_ENTRADA`, `DT_ALTA`, `DT_SAIDA_REAL`, `DT_PREVISTA_ALTA`, `DT_EVENTO_PREVISAO`, `DT_ALTA_REAL`, `QT_DIF_DIAS_PREVISTO_REAL`, `FL_ACERTO_EXATO`, `FL_ACERTO_TOLERANCIA`, `INDICADOR_PERCENTUAL_ACURACIA`, `dt_carga`.

Modelagem: flags DW podem vir como decimal textual. Dashboard aceita `1`, `1.0000000000`, equivalentes ja tratados.

## Indicador 14 - `fato_desospitalizacao_readmissao.py`

Pipeline/tabela: `fato_desospitalizacao_readmissao` -> `Indicador 14`. PK: `["nr_atendimento_origem"]`.

Fontes: `tasy.atendimento_paciente`, `tasy.prescr_medica`, `tasy.estabelecimento`, `tasy.motivo_alta`, `tasy.pessoa_fisica`, `tasy.medico_especialidade`, `tasy.especialidade_medica`, `tasy.setor_atendimento`.

Logica: parametros exclusao; internacao indice elegivel; primeiro retorno do paciente ate 30 dias; dias/horas ate readmissao; faixa e flags numerador/denominador.

Schema: `NR_ATENDIMENTO_ORIGEM`, `NR_ATENDIMENTO_RETORNO`, `NR_PRESCRICAO`, `DT_REFERENCIA`, `DT_COMPETENCIA_ORIGEM`, `CD_ESTABELECIMENTO_ORIGEM`, `NM_ESTABELECIMENTO_ORIGEM`, `CD_ESTABELECIMENTO_RETORNO`, `NM_ESTABELECIMENTO_RETORNO`, `CD_PACIENTE`, `NM_PACIENTE`, `CD_MOTIVO_ALTA_ORIGEM`, `DS_MOTIVO_ALTA_ORIGEM`, `IE_OBITO_ORIGEM`, `IE_TRANSFERENCIA_ADMIN_ORIGEM`, `CD_ESPECIALIDADE_RETORNO`, `DS_ESPECIALIDADE_RETORNO`, `CD_MEDICO_RETORNO`, `NM_MEDICO_RETORNO`, `CD_SETOR_ATENDIMENTO_RETORNO`, `DS_SETOR_ATENDIMENTO_RETORNO`, `DT_ENTRADA_ORIGEM`, `DT_SAIDA_ORIGEM`, `DT_ENTRADA_RETORNO`, `DT_SAIDA_BASE_RETORNO`, `QT_DIAS_ATE_READMISSAO`, `QT_HORAS_ATE_READMISSAO`, `DS_FAIXA_READMISSAO`, `IE_READMISSAO_7_DIAS`, `IE_READMISSAO_8_30_DIAS`, `IE_READMISSAO_30_DIAS_TOTAL`, `IE_DENOMINADOR_7_DIAS`, `IE_DENOMINADOR_30_DIAS`, `dt_carga`.

Modelagem: lista detalhada de readmissao real deve remover `DS_FAIXA_READMISSAO = "SEM_READMISSAO_30_DIAS"`.

## Indicador 15 - `fato_desospitalizacao_readmissao_uti.py`

Pipeline/tabela: `fato_desospitalizacao_readmissao_uti` -> `Indicador 15`. PK: `["nr_atendimento", "dt_entrada_retorno_uti"]`.

Fontes: `tasy.atend_paciente_unidade`, `tasy.atendimento_paciente`, `tasy.prescr_medica`, `tasy.estabelecimento`, `tasy.pessoa_fisica`, `tasy.medico_especialidade`, `tasy.especialidade_medica`, `tasy.setor_atendimento`.

Logica: setor UTI por `SETOR_ATENDIMENTO.CD_CLASSIF_SETOR = '4'`; ordena movimentos; exige UTI -> nao UTI -> UTI; descarta segmentos inconsistentes; calcula horas; retorna casos `< 48h`.

Schema: `NR_ATENDIMENTO`, `NR_PRESCRICAO`, `DT_REFERENCIA`, `CD_ESTABELECIMENTO`, `NM_ESTABELECIMENTO`, `CD_PACIENTE`, `NM_PACIENTE`, `CD_ESPECIALIDADE`, `DS_ESPECIALIDADE`, `CD_MEDICO`, `NM_MEDICO`, `CD_SETOR_ATENDIMENTO`, `DS_SETOR_ATENDIMENTO`, `CD_SETOR_SAIDA_UTI`, `DS_SETOR_SAIDA_UTI`, `DT_SAIDA_UTI`, `DT_ENTRADA_RETORNO_UTI`, `QT_HORAS_ATE_RETORNO_UTI`, `IE_READMISSAO_UTI_48H`, `dt_carga`.

Modelagem: tabela ja representa eventos positivos `< 48h`.
