import argparse
import os
from datetime import date

import pyspark.sql.functions as F

from .init import *
from .watermark_delta import write_watermark_delta, load_watermark_delta
from .lib import write_to_dw, get_DF_from_source
from .log import write_log

PIPELINE_NAME = "fato_desospitalizacao_outliers_pendencias"
PK_NATURAL = ["nr_atendimento"]
SCHEMA_FINAL = None

# Indicador 12 - Analise de outliers e maiores pendencias
# Objetivo funcional (regra 12):
#   "Analisar outlier a parte: paciente com internacao muito maior que media
#    ou mediana do hospital (referencia Setor + CID), trazendo maiores
#    pendencias para acompanhamento diario."

QUERY = """
WITH base_setor AS (
select 	a.nr_atendimento,
       	a.dt_entrada_unidade,
	(a.cd_unidade_basica || ' ' || a.cd_unidade_compl) cd_unidade,
       a.cd_unidade_basica,
	a.cd_unidade_compl,
       b.dt_entrada,
       substr(tasy.obter_nome_pf(e.cd_pessoa_fisica),1,60) nm_pessoa_fisica,
       a.cd_setor_atendimento,
       e.cd_pessoa_fisica,
       e.dt_nascimento,
       --e.nr_prontuario,
	to_number(substr(tasy.obter_prontuario_pf(b.cd_estabelecimento,b.cd_pessoa_fisica),1,255)) nr_prontuario,
       a.ie_status_unidade,
       e.ie_sexo,
       substr(tasy.obter_nome_convenio(c.cd_convenio),1,40) ds_convenio,
	substr(tasy.obter_categoria_convenio(c.cd_convenio,c.cd_categoria),1,40) ds_categoria, -- dalcastagne em 04/04/2008 os 88104
       a.cd_paciente_reserva,
       substr(tasy.obter_nome_pf(f.cd_pessoa_fisica),1,60) nm_paciente_reserva,a.cd_convenio_reserva,
	nm_usuario_reserva,
       d.nr_crm,
       d.nm_guerra,
	a.ie_classe_acomodacao,
	a.ie_sexo_paciente,
	a.ie_sexo_fixo,
	substr(tasy.obter_nome_pf(e.cd_pessoa_fisica),1,60) ds_status_unidade,
	a.ds_observacao,
	trunc(sysdate - b.dt_entrada, 0) qt_dia_permanencia,
	dt_inicio_higienizacao,
	dt_higienizacao,
	a.nr_seq_interno,
	b.dt_previsto_alta,	
	b.dt_alta_medico,
	a.nm_usuario_higienizacao,
	a.nm_usuario_fim_higienizacao,
	a.nr_ramal,
	a.ie_temporario,
	a.ie_tipo_reserva,
	a.cd_tipo_acomodacao,
	b.ie_probabilidade_alta,
	substr(tasy.obter_valor_dominio(1267,b.ie_probabilidade_alta),1,40) ds_probabilidade,
	b.cd_psicologo,
	a.ds_ocupacao,
	a.nr_agrupamento,
	a.qt_peso_maximo,         
	a.qt_altura_maxima,
	c.cd_convenio,
	a.qt_tempo_prev_higien,
	a.nr_seq_motivo_reserva,
	'N' ie_acompanhante,
	nvl(a.nr_seq_apresent,999) nr_seq_apresent,
	nvl(a.ie_radioterapia,'N') ie_radioterapia,
	b.nr_atend_alta,
	nvl(a.ie_interditado_radiacao,'N') ie_interditado_radiacao,
	b.cd_estabelecimento,
	e.nr_seq_perfil,
	b.cd_motivo_alta_medica,
	b.cd_medico_resp,
	b.IE_CARATER_INTER_SUS,
	b.cd_medico_referido,
	b.NR_SEQ_LOCAL_PA,
	b.IE_PACIENTE_ISOLADO,
	tasy.obter_atepacu_paciente(b.nr_atendimento, 'A') nr_seq_atepacu,
	1 ie_ordem
from  	tasy.pessoa_fisica e,
      	tasy.pessoa_fisica f,     
      	tasy.medico d,
      	tasy.atendimento_paciente b,
	tasy.atend_categoria_convenio c,
      	tasy.unidade_atendimento a
where	a.nr_atendimento      	= b.nr_atendimento
and	a.nr_atendimento	= c.nr_atendimento
and	c.nr_seq_interno	= tasy.obter_atecaco_atendimento(a.nr_atendimento)
and 	b.cd_pessoa_fisica    = e.cd_pessoa_fisica
and 	b.cd_medico_resp      = d.cd_pessoa_fisica (+)
and 	a.ie_situacao         = 'A'
and 	a.ie_status_unidade   in ('A','P','G','H','O')
and 	a.cd_paciente_reserva = f.cd_pessoa_fisica (+)
and	a.nr_atendimento >0
union all 
select  a.nr_atendimento_acomp,
       a.dt_entrada_unidade,
       (a.cd_unidade_basica ||' ' || a.cd_unidade_compl) cd_unidade,
       a.cd_unidade_basica,
       a.cd_unidade_compl,
      	b.dt_entrada,
       substr('Acomp ' || tasy.obter_nome_pf(e.cd_pessoa_fisica),1,40) nm_pessoa_fisica,
       a.cd_setor_atendimento,
       e.cd_pessoa_fisica,
       e.dt_nascimento,
       --e.nr_prontuario,
	to_number(substr(tasy.obter_prontuario_pf(b.cd_estabelecimento,b.cd_pessoa_fisica),1,255)) nr_prontuario,
       a.ie_status_unidade,
       e.ie_sexo,
       substr(tasy.obter_nome_convenio(c.cd_convenio),1,40) ds_convenio,
	substr(tasy.obter_categoria_convenio(c.cd_convenio,c.cd_categoria),1,40) ds_categoria, -- dalcastagne em 04/04/2008 os 88104
       a.cd_paciente_reserva,
       substr(tasy.obter_nome_pf(f.cd_pessoa_fisica),1,60) nm_paciente_reserva,
	a.cd_convenio_reserva,
	nm_usuario_reserva,
       d.nr_crm,
       d.nm_guerra,
	a.ie_classe_acomodacao,
	a.ie_sexo_paciente,
	a.ie_sexo_fixo,
	'Acomp ' || substr(tasy.obter_nome_pf(e.cd_pessoa_fisica),1,60) ds_status_unidade,
	a.ds_observacao,
	trunc(sysdate - b.dt_entrada, 0) qt_dia_permanencia,
	dt_inicio_higienizacao,
	dt_higienizacao,
	a.nr_seq_interno,
	b.dt_previsto_alta,
	b.dt_alta_medico,
	a.nm_usuario_higienizacao,
	a.nm_usuario_fim_higienizacao,
	a.nr_ramal,
	a.ie_temporario,
	a.ie_tipo_reserva,
	a.cd_tipo_acomodacao,
	b.ie_probabilidade_alta,
	substr(tasy.obter_valor_dominio(1267,b.ie_probabilidade_alta),1,40) ds_probabilidade,
	b.cd_psicologo,
	a.ds_ocupacao,
	a.nr_agrupamento,
	a.qt_peso_maximo,         
	a.qt_altura_maxima,
	c.cd_convenio cd_convenio,
	a.qt_tempo_prev_higien,
	a.nr_seq_motivo_reserva,
	'S' ie_acompanhante,
	nvl(a.nr_seq_apresent,999) nr_seq_apresent,
	nvl(a.ie_radioterapia,'N') ie_radioterapia,
	b.nr_atend_alta,
	nvl(a.ie_interditado_radiacao,'N') ie_interditado_radiacao,
	b.cd_estabelecimento,
	e.nr_seq_perfil,
	b.cd_motivo_alta_medica,
	b.cd_medico_resp,
	b.IE_CARATER_INTER_SUS,
	b.cd_medico_referido,
	b.NR_SEQ_LOCAL_PA,
	b.IE_PACIENTE_ISOLADO,
	tasy.obter_atepacu_paciente(b.nr_atendimento, 'A') nr_seq_atepacu,
	1 ie_ordem
from  	tasy.pessoa_fisica e,
      	tasy.pessoa_fisica f,     
      	tasy.medico d,
      	tasy.atendimento_paciente b,
	tasy.atend_categoria_convenio c,
      	tasy.unidade_atendimento a
where 	a.nr_atendimento_acomp= b.nr_atendimento
  and b.cd_pessoa_fisica    = e.cd_pessoa_fisica
  and	a.nr_atendimento	= c.nr_atendimento
  and	c.nr_seq_interno	= tasy.obter_atecaco_atendimento(a.nr_atendimento)
  and b.cd_medico_resp      = d.cd_pessoa_fisica(+)
  and a.ie_situacao         = 'A'
  and a.ie_status_unidade   = 'M'
  and a.cd_paciente_reserva = f.cd_pessoa_fisica
  and	a.nr_atendimento >0
union all
select 	a.nr_atendimento_ant nr_atendimento,
       	a.dt_entrada_unidade,
	(a.cd_unidade_basica || ' ' || a.cd_unidade_compl) cd_unidade,
       a.cd_unidade_basica,
	a.cd_unidade_compl,
       b.dt_entrada,
       substr(tasy.obter_nome_pf(e.cd_pessoa_fisica),1,60) nm_pessoa_fisica,
       a.cd_setor_atendimento,
       e.cd_pessoa_fisica,
       e.dt_nascimento,
       --e.nr_prontuario,
	to_number(substr(tasy.obter_prontuario_pf(b.cd_estabelecimento,b.cd_pessoa_fisica),1,255)) nr_prontuario,
       a.ie_status_unidade,
       e.ie_sexo,
       substr(tasy.obter_nome_convenio(c.cd_convenio),1,40) ds_convenio,
	substr(tasy.obter_categoria_convenio(c.cd_convenio,c.cd_categoria),1,40) ds_categoria, -- dalcastagne em 04/04/2008 os 88104
       a.cd_paciente_reserva,
       substr(tasy.obter_nome_pf(f.cd_pessoa_fisica),1,60) nm_paciente_reserva,
	a.cd_convenio_reserva,
	nm_usuario_reserva,
       d.nr_crm,
       d.nm_guerra,
	a.ie_classe_acomodacao,
	a.ie_sexo_paciente,
	a.ie_sexo_fixo,
	substr(tasy.obter_nome_pf(e.cd_pessoa_fisica),1,60) ds_status_unidade,
	a.ds_observacao,
	trunc(sysdate - b.dt_entrada, 0) qt_dia_permanencia,
	dt_inicio_higienizacao,
	dt_higienizacao,
	a.nr_seq_interno,
	b.dt_previsto_alta,	
	b.dt_alta_medico,
	a.nm_usuario_higienizacao,
	a.nm_usuario_fim_higienizacao,
	a.nr_ramal,
	a.ie_temporario,
	a.ie_tipo_reserva,
	a.cd_tipo_acomodacao,
	b.ie_probabilidade_alta,
	substr(tasy.obter_valor_dominio(1267,b.ie_probabilidade_alta),1,40) ds_probabilidade,
	b.cd_psicologo,
	a.ds_ocupacao,
	a.nr_agrupamento,
	a.qt_peso_maximo,         
	a.qt_altura_maxima,
	c.cd_convenio,
	a.qt_tempo_prev_higien,
	a.nr_seq_motivo_reserva,
	'N' ie_acompanhante,
	nvl(a.nr_seq_apresent,999) nr_seq_apresent,
	nvl(a.ie_radioterapia,'N') ie_radioterapia,
	b.nr_atend_alta,
	nvl(a.ie_interditado_radiacao,'N') ie_interditado_radiacao,
	b.cd_estabelecimento,
	e.nr_seq_perfil,
	b.cd_motivo_alta_medica,
	b.cd_medico_resp,
	b.IE_CARATER_INTER_SUS,
	b.cd_medico_referido,
	b.NR_SEQ_LOCAL_PA,
	b.IE_PACIENTE_ISOLADO,
	tasy.obter_atepacu_paciente(b.nr_atendimento, 'A') nr_seq_atepacu,
	1 ie_ordem
from  	tasy.pessoa_fisica e,
      	tasy.pessoa_fisica f,     
      	tasy.medico d,
      	tasy.atendimento_paciente b,
	tasy.atend_categoria_convenio c,
      	tasy.unidade_atendimento a,
	tasy.parametro_medico pm
where	a.nr_atendimento_ant      	= b.nr_atendimento
and	a.nr_atendimento_ant	= c.nr_atendimento
and	c.nr_seq_interno	= tasy.obter_atecaco_atendimento(a.nr_atendimento_ant)
and 	b.cd_pessoa_fisica    = e.cd_pessoa_fisica
and 	b.cd_medico_resp      = d.cd_pessoa_fisica (+)
and 	a.ie_situacao         = 'A'
and 	a.ie_status_unidade   = 'A'
and 	a.cd_paciente_reserva = f.cd_pessoa_fisica (+)
and	a.nr_atendimento_ant >0
and	a.nr_atendimento_ant is not null
and	a.nr_atendimento is null
and	b.dt_alta is not null
and	pm.cd_estabelecimento = tasy.wheb_usuario_pck.get_cd_estabelecimento
and	nvl(pm.ie_pac_proc_alta_setor,'S') = 'S'
union all
select 	b.nr_atendimento,
       	a.dt_entrada_unidade,
	(a.cd_unidade_basica || ' ' || a.cd_unidade_compl) cd_unidade,
       a.cd_unidade_basica,
	a.cd_unidade_compl,
       b.dt_entrada,
       substr(tasy.obter_nome_pf(e.cd_pessoa_fisica),1,60) nm_pessoa_fisica,
       a.cd_setor_atendimento,
       e.cd_pessoa_fisica,
       e.dt_nascimento,
       --e.nr_prontuario,
	to_number(substr(tasy.obter_prontuario_pf(b.cd_estabelecimento,b.cd_pessoa_fisica),1,255)) nr_prontuario,
       a.ie_status_unidade,
       e.ie_sexo,
       substr(tasy.obter_nome_convenio(c.cd_convenio),1,40) ds_convenio,
	substr(tasy.obter_categoria_convenio(c.cd_convenio,c.cd_categoria),1,40) ds_categoria, -- dalcastagne em 04/04/2008 os 88104
       a.cd_paciente_reserva,
       substr(tasy.obter_nome_pf(f.cd_pessoa_fisica),1,60) nm_paciente_reserva,
	a.cd_convenio_reserva,
	nm_usuario_reserva,
       d.nr_crm,
       d.nm_guerra,
	a.ie_classe_acomodacao,
	a.ie_sexo_paciente,
	a.ie_sexo_fixo,
	substr(tasy.obter_nome_pf(e.cd_pessoa_fisica),1,60) ds_status_unidade,
	a.ds_observacao,
	trunc(sysdate - b.dt_entrada, 0) qt_dia_permanencia,
	dt_inicio_higienizacao,
	dt_higienizacao,
	a.nr_seq_interno,
	b.dt_previsto_alta,	
	b.dt_alta_medico,
	a.nm_usuario_higienizacao,
	a.nm_usuario_fim_higienizacao,
	a.nr_ramal,
	a.ie_temporario,
	a.ie_tipo_reserva,
	a.cd_tipo_acomodacao,
	b.ie_probabilidade_alta,
	substr(tasy.obter_valor_dominio(1267,b.ie_probabilidade_alta),1,40) ds_probabilidade,
	b.cd_psicologo,
	a.ds_ocupacao,
	a.nr_agrupamento,
	a.qt_peso_maximo,         
	a.qt_altura_maxima,
	c.cd_convenio,
	a.qt_tempo_prev_higien,
	a.nr_seq_motivo_reserva,
	'N' ie_acompanhante,
	nvl(a.nr_seq_apresent,999) nr_seq_apresent,
	nvl(a.ie_radioterapia,'N') ie_radioterapia,
	b.nr_atend_alta,
	nvl(a.ie_interditado_radiacao,'N') ie_interditado_radiacao,
	b.cd_estabelecimento,
	e.nr_seq_perfil,
	b.cd_motivo_alta_medica,
	b.cd_medico_resp,
	b.IE_CARATER_INTER_SUS,
	b.cd_medico_referido,
	b.NR_SEQ_LOCAL_PA,
	b.IE_PACIENTE_ISOLADO,
	tasy.obter_atepacu_paciente(b.nr_atendimento, 'A') nr_seq_atepacu,
	2 ie_ordem
from  	tasy.pessoa_fisica e,
      	tasy.pessoa_fisica f,     
      	tasy.medico d,
      	tasy.atendimento_paciente b,
	tasy.atendimento_paciente y,
	tasy.atend_categoria_convenio c,
      	tasy.unidade_atendimento a,
	tasy.atend_paciente_unidade u,
	tasy.setor_atendimento x,
	tasy.setor_atendimento t
where	a.nr_atendimento      	= y.nr_atendimento
and		y.nr_atendimento		= b.nr_atendimento_mae
and		a.nr_atendimento	= c.nr_atendimento
and		c.nr_seq_interno	= tasy.obter_atecaco_atendimento(a.nr_atendimento)
and 	b.cd_pessoa_fisica    = e.cd_pessoa_fisica
and 	b.cd_medico_resp      = d.cd_pessoa_fisica (+)
and	u.nr_atendimento = b.nr_atendimento
and	u.nr_seq_interno = (select tasy.obter_atepacu_paciente(b.nr_atendimento, 'A') from dual)
and	t.cd_setor_atendimento = u.cd_setor_atendimento
and		b.dt_alta_interno     = to_date('30/12/2999', 'DD/MM/YYYY')
and 	a.ie_situacao         = 'A'
and 	a.ie_status_unidade   in ('P','G','H')
and		x.cd_setor_atendimento	= a.cd_setor_atendimento
and		x.ie_rn_mae				= 'S'
and 	a.cd_paciente_reserva = f.cd_pessoa_fisica (+)
and	t.cd_classif_setor = '9'
and	a.nr_atendimento >0
and 	b.dt_cancelamento is null 
),
diagnostico_cid AS (
    SELECT
        d.nr_atendimento,
        d.cd_doenca AS cd_cid
    FROM (
        SELECT
            dd.nr_atendimento,
            dd.cd_doenca,
            ROW_NUMBER() OVER (
                PARTITION BY dd.nr_atendimento
                ORDER BY
                    CASE
                        WHEN NVL(dd.ie_diag_alta, 'N') IN ('S', '1') THEN 0
                        WHEN NVL(dd.ie_diag_referencia, 'N') IN ('S', '1') THEN 1
                        ELSE 2
                    END,
                    NVL(dd.dt_liberacao, dd.dt_diagnostico) DESC,
                    dd.nr_seq_interno DESC
            ) rn
        FROM tasy.diagnostico_doenca dd
        WHERE dd.dt_inativacao IS NULL
    ) d
    WHERE d.rn = 1
),
indicador_6_base AS (
    SELECT
        b.nr_atendimento,
        b.nm_pessoa_fisica AS nm_paciente,
        b.cd_setor_atendimento,
        sa.ds_setor_atendimento,
        dc.cd_cid,
        b.qt_dia_permanencia,
        AVG(b.qt_dia_permanencia) OVER (
            PARTITION BY b.cd_setor_atendimento, dc.cd_cid
        ) AS media_qt_dia_permanencia_setor_cid,
        MEDIAN(b.qt_dia_permanencia) OVER (
            PARTITION BY b.cd_setor_atendimento, dc.cd_cid
        ) AS mediana_qt_dia_permanencia_setor_cid
    FROM base_setor b
    LEFT JOIN diagnostico_cid dc
        ON dc.nr_atendimento = b.nr_atendimento
    LEFT JOIN tasy.setor_atendimento sa
        ON sa.cd_setor_atendimento = b.cd_setor_atendimento
    WHERE dc.cd_cid IS NOT NULL
),
outlier_base AS (
    SELECT
        b.nr_atendimento,
        b.nm_paciente,
        b.cd_setor_atendimento,
        b.ds_setor_atendimento,
        b.cd_cid,
        b.qt_dia_permanencia,
        b.media_qt_dia_permanencia_setor_cid AS media_grupo_setor_cid,
        b.mediana_qt_dia_permanencia_setor_cid AS mediana_grupo_setor_cid,
        GREATEST(
            b.qt_dia_permanencia - b.media_qt_dia_permanencia_setor_cid,
            0
        ) AS qt_dias_acima_media,
        GREATEST(
            b.qt_dia_permanencia - b.mediana_qt_dia_permanencia_setor_cid,
            0
        ) AS qt_dias_acima_mediana,
        CASE
            WHEN b.qt_dia_permanencia > b.media_qt_dia_permanencia_setor_cid
              OR b.qt_dia_permanencia > b.mediana_qt_dia_permanencia_setor_cid
                THEN 'S'
            ELSE 'N'
        END AS ie_outlier
    FROM indicador_6_base b
),
outlier_filtrado AS (
    SELECT *
    FROM outlier_base
    WHERE ie_outlier = 'S'
),
pendencia_base AS (
    SELECT
        p.nr_atendimento,
        p.nr_prescricao,
        p.cd_setor_prescr AS cd_area_pendencia,
        sa.ds_setor_atendimento AS ds_area_pendencia,
        p.nm_prescritor AS nm_responsavel_pendencia,
        p.ds_item AS ds_pendencia,
        NVL(p.qt_pend, 1) AS qt_pendencia_item,
        CASE
            WHEN p.dt_horario IS NULL THEN 'SEM_HORARIO'
            WHEN p.dt_horario < SYSDATE THEN 'ATRASADA'
            ELSE 'NO_PRAZO'
        END AS ds_status_pendencia
    FROM tasy.adep_pend_v p
    JOIN outlier_filtrado o
        ON o.nr_atendimento = p.nr_atendimento
    LEFT JOIN tasy.setor_atendimento sa
        ON sa.cd_setor_atendimento = p.cd_setor_prescr
    WHERE NVL(p.qt_pend, 0) > 0
),
pendencia_rank AS (
    SELECT
        pb.*,
        ROW_NUMBER() OVER (
            PARTITION BY pb.nr_atendimento
            ORDER BY
                pb.qt_pendencia_item DESC,
                pb.ds_pendencia,
                pb.nr_prescricao DESC
        ) AS rn_pendencia
    FROM pendencia_base pb
),
pendencia_consolidada AS (
    SELECT
        pr.nr_atendimento,
        SUM(pr.qt_pendencia_item) AS qt_pendencias,
        LISTAGG(
            CASE
                WHEN pr.rn_pendencia <= 5 THEN
                    pr.ds_pendencia || ' (qt=' || pr.qt_pendencia_item || ')'
            END,
            ' | '
        ) WITHIN GROUP (
            ORDER BY
                pr.qt_pendencia_item DESC,
                pr.ds_pendencia
        ) AS ds_principais_pendencias,
        MAX(
            CASE
                WHEN pr.rn_pendencia = 1 THEN pr.nm_responsavel_pendencia
            END
        ) AS nm_responsavel_pendencia,
        MAX(
            CASE
                WHEN pr.rn_pendencia = 1 THEN pr.ds_area_pendencia
            END
        ) AS ds_area_pendencia,
        MAX(
            CASE
                WHEN pr.rn_pendencia = 1 THEN pr.ds_status_pendencia
            END
        ) AS ds_status_pendencia
    FROM pendencia_rank pr
    GROUP BY
        pr.nr_atendimento
)
SELECT
    o.nr_atendimento AS nr_atendimento,
    o.nm_paciente AS nm_paciente,
    o.ds_setor_atendimento AS ds_setor_atendimento,
    o.cd_cid AS cd_cid,
    o.qt_dia_permanencia,
    o.media_grupo_setor_cid AS media_setor_cid,
    o.mediana_grupo_setor_cid AS mediana_setor_cid,
    o.qt_dias_acima_media AS dias_acima_media,
    o.qt_dias_acima_mediana AS dias_acima_mediana,
    o.ie_outlier AS flag_outlier,
    NVL(pc.qt_pendencias, 0) AS qt_pendencias,
    NVL(pc.ds_principais_pendencias, 'SEM_PENDENCIA_NA_FONTE') AS ds_principais_pendencias,
    pc.nm_responsavel_pendencia AS nm_responsavel_pendencia,
    pc.ds_area_pendencia AS ds_area_pendencia,
    pc.ds_status_pendencia AS ds_status_pendencia
FROM outlier_filtrado o
LEFT JOIN pendencia_consolidada pc
    ON pc.nr_atendimento = o.nr_atendimento
ORDER BY
    GREATEST(o.qt_dias_acima_media, o.qt_dias_acima_mediana) DESC,
    NVL(pc.qt_pendencias, 0) DESC,
    o.nr_atendimento DESC
"""


def normalize_pk(pk):
    if pk is None:
        return []
    if isinstance(pk, str):
        return [pk]
    return list(pk)


def aplica_schema(df, schema):
    return df.select([
        F.col(col_name).cast(col_type).alias(col_name)
        for col_name, col_type in schema
    ])


def run_pipeline(**kwargs):
    arguments = kwargs.get("arguments")
    spark = kwargs.get("spark")

    if spark is None:
        spark = create_context(arguments.name)

    pipeline(spark)


def pipeline(spark):
    write_log(spark, __name__, PIPELINE_NAME)

    watermark_path = f"{WATERMARK_DELTA_PATH}/{PIPELINE_NAME}"
    start_load_date = date.today()
    last_load_date = load_watermark_delta(spark, watermark_path, PIPELINE_NAME)
    write_log(spark, __name__, f"Last load date {last_load_date}")

    df = get_DF_from_source(spark, QUERY)

    pk_list = normalize_pk(PK_NATURAL)
    if pk_list:
        df = df.dropDuplicates(pk_list)

    df = df.withColumn("dt_carga", F.lit(start_load_date))

    if SCHEMA_FINAL:
        df = aplica_schema(df, SCHEMA_FINAL)

    output_path = os.path.join(LAKE_HOME, PIPELINE_NAME)
    write_log(spark, __name__, output_path)
    write_to_dw(df, output_path)

    write_watermark_delta(
        spark,
        watermark_path,
        PIPELINE_NAME,
        start_load_date,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executar pipeline")
    parser.add_argument("-name", required=True, type=str)
    args = parser.parse_args()
    run_pipeline(arguments=args)
