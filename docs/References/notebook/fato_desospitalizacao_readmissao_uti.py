import argparse
import os
from datetime import date

import pyspark.sql.functions as F

from .init import *
from .watermark_delta import write_watermark_delta, load_watermark_delta
from .lib import write_to_dw, get_DF_from_source
from .log import write_log

PIPELINE_NAME = "fato_desospitalizacao_readmissao_uti"
PK_NATURAL = ["nr_atendimento", "dt_entrada_retorno_uti"]
SCHEMA_FINAL = None

# Indicador 15 - Taxa de readmissao UTI em 48h
# Grao da consulta:
#   - 1 linha por evento de retorno a UTI em menos de 48h
# Observacoes:
#   - A classificacao de UTI usa SETOR_ATENDIMENTO.CD_CLASSIF_SETOR = '4'.
#   - A regra exige: UTI -> setor nao UTI -> retorno UTI.
#   - Segmentos UTI com entrada e saida no mesmo instante sao descartados como
#     candidatos de origem para evitar duplicidade por movimentos tecnicos.
QUERY = """
WITH internacao_base AS (
    SELECT
        ap.nr_atendimento,
        ap.cd_estabelecimento,
        ap.cd_pessoa_fisica,
        ap.cd_medico_resp
    FROM
        tasy.atendimento_paciente ap
    WHERE
        ap.dt_cancelamento IS NULL
        AND ap.ie_tipo_atendimento = 1
), movimentos_ordenados AS (
    SELECT
        apu.nr_seq_interno,
        apu.nr_atendimento,
        apu.cd_setor_atendimento,
        sa.ds_setor_atendimento,
        sa.cd_classif_setor,
        CASE
            WHEN sa.cd_classif_setor = '4' THEN
                'S'
            ELSE
                'N'
        END                                                   AS ie_setor_uti,
        coalesce(apu.dt_entrada_real, apu.dt_entrada_unidade) AS dt_entrada_mov,
        coalesce(apu.dt_saida_unidade, apu.dt_saida_interno)  AS dt_saida_mov,
        ib.cd_estabelecimento,
        ib.cd_pessoa_fisica,
        ib.cd_medico_resp,
        ROW_NUMBER()
        OVER(PARTITION BY apu.nr_atendimento
             ORDER BY
                 coalesce(apu.dt_entrada_real, apu.dt_entrada_unidade),
                 apu.nr_seq_interno
        )                                                     AS rn_mov
    FROM
             tasy.atend_paciente_unidade apu
        JOIN internacao_base        ib ON ib.nr_atendimento = apu.nr_atendimento
        LEFT JOIN tasy.setor_atendimento sa ON sa.cd_setor_atendimento = apu.cd_setor_atendimento
    WHERE
        coalesce(apu.dt_entrada_real, apu.dt_entrada_unidade) IS NOT NULL
), seg_step1 AS (
    SELECT
        mo.*,
        CASE
            WHEN mo.ie_setor_uti = 'S' THEN
                1
            ELSE
                0
        END AS is_uti,
        LAG(
            CASE
                WHEN mo.ie_setor_uti = 'S' THEN
                    1
                ELSE
                    0
            END
        )
        OVER(PARTITION BY mo.nr_atendimento
             ORDER BY
                 mo.rn_mov
        )   AS prev_is_uti
    FROM
        movimentos_ordenados mo
), seg_mov AS (
    SELECT
        s1.*,
        1 + SUM(
            CASE
                WHEN s1.prev_is_uti = s1.is_uti THEN
                    0
                ELSE 1
            END
        )
            OVER(PARTITION BY s1.nr_atendimento
                 ORDER BY
                     s1.rn_mov
            ) AS seg_id
    FROM
        seg_step1 s1
), seg_marks AS (
    SELECT
        sm.*,
        ROW_NUMBER()
        OVER(PARTITION BY sm.nr_atendimento, sm.seg_id
             ORDER BY
                 sm.rn_mov
        ) AS rn_seg_asc,
        ROW_NUMBER()
        OVER(PARTITION BY sm.nr_atendimento, sm.seg_id
             ORDER BY
                 sm.rn_mov DESC
        ) AS rn_seg_desc
    FROM
        seg_mov sm
), seg_agg AS (
    SELECT
        nr_atendimento,
        seg_id,
        MAX(is_uti)         AS is_uti,
        MIN(dt_entrada_mov) AS seg_dt_start,
        MAX(
            CASE
                WHEN rn_seg_desc = 1 THEN
                    dt_saida_mov
            END
        )                   AS seg_dt_end_last,
        MAX(
            CASE
                WHEN rn_seg_asc = 1 THEN
                    cd_setor_atendimento
            END
        )                   AS seg_setor_entry,
        MAX(
            CASE
                WHEN rn_seg_desc = 1 THEN
                    cd_setor_atendimento
            END
        )                   AS seg_setor_exit,
        MAX(
            CASE
                WHEN rn_seg_desc = 1 THEN
                    ds_setor_atendimento
            END
        )                   AS seg_setor_exit_ds
    FROM
        seg_marks
    GROUP BY
        nr_atendimento,
        seg_id
), seg_links AS (
    SELECT
        sa.*,
        LEAD(sa.is_uti, 1)
        OVER(PARTITION BY sa.nr_atendimento
             ORDER BY
                 sa.seg_id
        ) AS next1_is_uti,
        LEAD(sa.is_uti, 2)
        OVER(PARTITION BY sa.nr_atendimento
             ORDER BY
                 sa.seg_id
        ) AS next2_is_uti,
        LEAD(sa.seg_dt_start, 2)
        OVER(PARTITION BY sa.nr_atendimento
             ORDER BY
                 sa.seg_id
        ) AS dt_entrada_retorno_uti,
        LEAD(sa.seg_setor_entry, 2)
        OVER(PARTITION BY sa.nr_atendimento
             ORDER BY
                 sa.seg_id
        ) AS cd_setor_retorno_uti
    FROM
        seg_agg sa
), eventos_retorno_uti AS (
    SELECT
        ib.nr_atendimento,
        ib.cd_estabelecimento,
        ib.cd_pessoa_fisica,
        ib.cd_medico_resp,
        sl.seg_setor_exit                                       AS cd_setor_saida_uti,
        sl.seg_setor_exit_ds                                    AS ds_setor_saida_uti,
        sl.seg_dt_end_last                                      AS dt_saida_uti,
        sl.cd_setor_retorno_uti,
        sa_retorno.ds_setor_atendimento                         AS ds_setor_retorno_uti,
        sl.dt_entrada_retorno_uti,
        ( sl.dt_entrada_retorno_uti - sl.seg_dt_end_last ) * 24 AS qt_horas_ate_retorno_uti
    FROM
             seg_links sl
        JOIN internacao_base        ib ON ib.nr_atendimento = sl.nr_atendimento
        LEFT JOIN tasy.setor_atendimento sa_retorno ON sa_retorno.cd_setor_atendimento = sl.cd_setor_retorno_uti
    WHERE
            sl.is_uti = 1
        AND sl.next1_is_uti = 0
        AND sl.next2_is_uti = 1
        AND sl.seg_dt_end_last IS NOT NULL
        AND sl.seg_dt_end_last > sl.seg_dt_start
        AND sl.dt_entrada_retorno_uti IS NOT NULL
        AND sl.dt_entrada_retorno_uti > sl.seg_dt_end_last
        AND sl.dt_entrada_retorno_uti <= sl.seg_dt_end_last + 2
), medico_especialidade_principal AS (
    SELECT
        cd_pessoa_fisica,
        cd_especialidade
    FROM
        (
            SELECT
                me.*,
                ROW_NUMBER()
                OVER(PARTITION BY me.cd_pessoa_fisica
                     ORDER BY
                         nvl(me.nr_seq_prioridade, 999999),
                         me.cd_especialidade
                ) AS rn
            FROM
                tasy.medico_especialidade me
        )
    WHERE
        rn = 1
), prescricao_ancora AS (
    SELECT
        eru.nr_atendimento,
        eru.dt_entrada_retorno_uti,
        pm.nr_prescricao,
        pm.dt_prescricao,
        pm.cd_setor_atendimento,
        coalesce(pm.cd_prescritor, pm.cd_medico) AS cd_medico,
        ROW_NUMBER()
        OVER(PARTITION BY eru.nr_atendimento,
                          eru.dt_entrada_retorno_uti
             ORDER BY
                 CASE
                     WHEN pm.cd_setor_atendimento = eru.cd_setor_retorno_uti THEN
                         0
                     ELSE
                         1
                 END,
                 CASE
                     WHEN pm.dt_prescricao >= eru.dt_entrada_retorno_uti THEN
                             0
                     ELSE
                         1
                 END,
                 abs((pm.dt_prescricao - eru.dt_entrada_retorno_uti) * 24 * 60),
                 pm.nr_prescricao DESC
        )                                        AS rn
    FROM
        eventos_retorno_uti eru
        LEFT JOIN tasy.prescr_medica  pm ON pm.nr_atendimento = eru.nr_atendimento
                                           AND pm.dt_prescricao IS NOT NULL
), base_calculo AS (
    SELECT
        eru.nr_atendimento,
        pa.nr_prescricao,
        trunc(coalesce(pa.dt_prescricao, eru.dt_entrada_retorno_uti)) AS dt_referencia,
        eru.cd_estabelecimento,
        est.nm_fantasia_estab                                         AS nm_estabelecimento,
        eru.cd_pessoa_fisica                                          AS cd_paciente,
        pf_paciente.nm_pessoa_fisica                                  AS nm_paciente,
        coalesce(pa.cd_medico, eru.cd_medico_resp)                    AS cd_medico,
        pf_medico.nm_pessoa_fisica                                    AS nm_medico,
        mep.cd_especialidade,
        em.ds_especialidade,
        eru.cd_setor_retorno_uti                                      AS cd_setor_atendimento,
        eru.ds_setor_retorno_uti                                      AS ds_setor_atendimento,
        eru.cd_setor_saida_uti,
        eru.ds_setor_saida_uti,
        eru.dt_saida_uti,
        eru.dt_entrada_retorno_uti,
        eru.qt_horas_ate_retorno_uti
    FROM
        eventos_retorno_uti            eru
        LEFT JOIN prescricao_ancora              pa ON pa.nr_atendimento = eru.nr_atendimento
                                          AND pa.dt_entrada_retorno_uti = eru.dt_entrada_retorno_uti
                                          AND pa.rn = 1
        LEFT JOIN tasy.estabelecimento           est ON est.cd_estabelecimento = eru.cd_estabelecimento
        LEFT JOIN tasy.pessoa_fisica             pf_paciente ON pf_paciente.cd_pessoa_fisica = eru.cd_pessoa_fisica
        LEFT JOIN tasy.pessoa_fisica             pf_medico ON pf_medico.cd_pessoa_fisica = coalesce(pa.cd_medico, eru.cd_medico_resp)
        LEFT JOIN medico_especialidade_principal mep ON mep.cd_pessoa_fisica = coalesce(pa.cd_medico, eru.cd_medico_resp)
        LEFT JOIN tasy.especialidade_medica      em ON em.cd_especialidade = mep.cd_especialidade
)
SELECT
    bc.nr_atendimento,
    bc.nr_prescricao,
    bc.dt_referencia,
    bc.cd_estabelecimento,
    bc.nm_estabelecimento,
    bc.cd_paciente,
    bc.nm_paciente,
    bc.cd_especialidade,
    bc.ds_especialidade,
    bc.cd_medico,
    bc.nm_medico,
    bc.cd_setor_atendimento,
    bc.ds_setor_atendimento,
    bc.cd_setor_saida_uti,
    bc.ds_setor_saida_uti,
    bc.dt_saida_uti,
    bc.dt_entrada_retorno_uti,
    bc.qt_horas_ate_retorno_uti,
    CASE
        WHEN bc.qt_horas_ate_retorno_uti < 48 THEN
            'S'
        ELSE
            'N'
    END AS ie_readmissao_uti_48h
FROM
    base_calculo bc
WHERE
    bc.qt_horas_ate_retorno_uti < 48
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
