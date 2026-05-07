import argparse
import os
from datetime import date

import pyspark.sql.functions as F

from .init import *
from .watermark_delta import write_watermark_delta, load_watermark_delta
from .lib import write_to_dw, get_DF_from_source
from .log import write_log

PIPELINE_NAME = "fato_desospitalizacao_readmissao"
PK_NATURAL = ["nr_atendimento_origem"]
SCHEMA_FINAL = None

# Indicador 14 - Taxa de readmissao hospitalar (7 e 30 dias)
# Grao da consulta:
#   - Base detalhada: 1 linha por internacao indice elegivel (com ou sem readmissao)
#   - Suporta taxa agregada: flags de denominador (7/30 dias) + numerador

QUERY = """
WITH parametros AS (
    SELECT
        'S'            AS p_excluir_transferencia_admin,
        'S'            AS p_excluir_obito_denominador,
        trunc(sysdate) AS dt_corte_analise
    FROM
        dual
), internacao_base AS (
    SELECT
        ap.nr_atendimento,
        ap.cd_estabelecimento,
        ap.cd_pessoa_fisica,
        ap.cd_medico_resp,
        ap.cd_motivo_alta,
        ma.ds_motivo_alta,
        ma.ie_obito,
        ap.dt_entrada,
        ap.dt_alta,
        ap.dt_saida_real,
        coalesce(ap.dt_saida_real, ap.dt_alta) AS dt_saida_base,
        nvl(
            tasy.obter_se_transferencia(ap.nr_atendimento),
            'N'
        )                                      AS ie_transferencia_admin
    FROM
        tasy.atendimento_paciente ap
        LEFT JOIN tasy.motivo_alta          ma ON ma.cd_motivo_alta = ap.cd_motivo_alta
    WHERE
        ap.dt_cancelamento IS NULL
        AND ap.ie_tipo_atendimento = 1
        AND ap.dt_entrada IS NOT NULL
        AND coalesce(ap.dt_saida_real, ap.dt_alta) IS NOT NULL
        AND coalesce(ap.dt_saida_real, ap.dt_alta) >= ap.dt_entrada
), internacao_indice AS (
    SELECT
        ib.*
    FROM
             internacao_base ib
        CROSS JOIN parametros p
    WHERE
        ( p.p_excluir_transferencia_admin = 'N'
          OR ib.ie_transferencia_admin = 'N' )
        AND ( p.p_excluir_obito_denominador = 'N'
              OR nvl(ib.ie_obito, 'N') <> 'S' )
), candidatos_retorno AS (
    SELECT
        i.nr_atendimento                           AS nr_atendimento_origem,
        r.nr_atendimento                           AS nr_atendimento_retorno,
        r.cd_estabelecimento                       AS cd_estabelecimento_retorno,
        r.cd_medico_resp                           AS cd_medico_resp_retorno,
        r.dt_entrada                               AS dt_entrada_retorno,
        r.dt_saida_base                            AS dt_saida_base_retorno,
        ( r.dt_entrada - i.dt_saida_base )         AS nr_dias_ate_readmissao,
        round((r.dt_entrada - i.dt_saida_base), 4) AS qt_dias_ate_readmissao,
        ROW_NUMBER()
        OVER(PARTITION BY i.nr_atendimento
             ORDER BY
                 r.dt_entrada, r.nr_atendimento
        )                                          AS rn_retorno
    FROM
             internacao_indice i
        CROSS JOIN parametros      p
        JOIN internacao_base r ON r.cd_pessoa_fisica = i.cd_pessoa_fisica
                                  AND r.nr_atendimento <> i.nr_atendimento
                                  AND r.dt_entrada >= i.dt_saida_base
                                  AND r.dt_entrada <= i.dt_saida_base + 30
                                  AND ( p.p_excluir_transferencia_admin = 'N'
                                        OR r.ie_transferencia_admin = 'N' )
), primeiro_retorno AS (
    SELECT
        cr.nr_atendimento_origem,
        cr.nr_atendimento_retorno,
        cr.cd_estabelecimento_retorno,
        cr.cd_medico_resp_retorno,
        cr.dt_entrada_retorno,
        cr.dt_saida_base_retorno,
        cr.nr_dias_ate_readmissao,
        cr.qt_dias_ate_readmissao
    FROM
        candidatos_retorno cr
    WHERE
        cr.rn_retorno = 1
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
        pr.nr_atendimento_retorno,
        pm.nr_prescricao,
        pm.dt_prescricao,
        pm.cd_setor_atendimento,
        coalesce(pm.cd_prescritor, pm.cd_medico) AS cd_medico,
        ROW_NUMBER()
        OVER(PARTITION BY pr.nr_atendimento_retorno
             ORDER BY
                 CASE
                     WHEN pm.dt_prescricao >= pr.dt_entrada_retorno THEN
                         0
                     ELSE
                         1
                 END,
                 abs((pm.dt_prescricao - pr.dt_entrada_retorno) * 24 * 60),
                 pm.nr_prescricao DESC
        )                                        AS rn
    FROM
        primeiro_retorno   pr
        LEFT JOIN tasy.prescr_medica pm ON pm.nr_atendimento = pr.nr_atendimento_retorno
                                           AND pm.dt_prescricao IS NOT NULL
), base_detalhada AS (
    SELECT
        i.nr_atendimento                                                          AS nr_atendimento_origem,
        pr.nr_atendimento_retorno,
        pa.nr_prescricao,
        trunc(coalesce(pa.dt_prescricao, pr.dt_entrada_retorno, i.dt_saida_base)) AS dt_referencia,
        trunc(i.dt_saida_base, 'MM')                                              AS dt_competencia_origem,
        i.cd_estabelecimento                                                      AS cd_estabelecimento_origem,
        est_origem.nm_fantasia_estab                                              AS nm_estabelecimento_origem,
        pr.cd_estabelecimento_retorno,
        est_retorno.nm_fantasia_estab                                             AS nm_estabelecimento_retorno,
        i.cd_pessoa_fisica                                                        AS cd_paciente,
        pf_paciente.nm_pessoa_fisica                                              AS nm_paciente,
        i.cd_motivo_alta                                                          AS cd_motivo_alta_origem,
        i.ds_motivo_alta                                                          AS ds_motivo_alta_origem,
        nvl(i.ie_obito, 'N')                                                      AS ie_obito_origem,
        i.ie_transferencia_admin                                                  AS ie_transferencia_admin_origem,
        coalesce(pa.cd_medico, pr.cd_medico_resp_retorno)                         AS cd_medico_retorno,
        pf_medico_retorno.nm_pessoa_fisica                                        AS nm_medico_retorno,
        mep.cd_especialidade                                                      AS cd_especialidade_retorno,
        em.ds_especialidade                                                       AS ds_especialidade_retorno,
        pa.cd_setor_atendimento                                                   AS cd_setor_atendimento_retorno,
        sa.ds_setor_atendimento                                                   AS ds_setor_atendimento_retorno,
        i.dt_entrada                                                              AS dt_entrada_origem,
        i.dt_saida_base                                                           AS dt_saida_origem,
        pr.dt_entrada_retorno,
        pr.dt_saida_base_retorno,
        pr.nr_dias_ate_readmissao,
        pr.qt_dias_ate_readmissao,
        round(pr.nr_dias_ate_readmissao * 24, 2)                                  AS qt_horas_ate_readmissao,
        CASE
            WHEN i.dt_saida_base <= p.dt_corte_analise - 7 THEN
                'S'
            ELSE
                'N'
        END                                                                       AS ie_denominador_7_dias,
        CASE
            WHEN i.dt_saida_base <= p.dt_corte_analise - 30 THEN
                'S'
            ELSE
                'N'
        END                                                                       AS ie_denominador_30_dias
    FROM
             internacao_indice i
        CROSS JOIN parametros                     p
        LEFT JOIN primeiro_retorno               pr ON pr.nr_atendimento_origem = i.nr_atendimento
        LEFT JOIN prescricao_ancora              pa ON pa.nr_atendimento_retorno = pr.nr_atendimento_retorno
                                          AND pa.rn = 1
        LEFT JOIN tasy.estabelecimento           est_origem ON est_origem.cd_estabelecimento = i.cd_estabelecimento
        LEFT JOIN tasy.estabelecimento           est_retorno ON est_retorno.cd_estabelecimento = pr.cd_estabelecimento_retorno
        LEFT JOIN tasy.pessoa_fisica             pf_paciente ON pf_paciente.cd_pessoa_fisica = i.cd_pessoa_fisica
        LEFT JOIN tasy.pessoa_fisica             pf_medico_retorno ON pf_medico_retorno.cd_pessoa_fisica = coalesce(pa.cd_medico, pr.cd_medico_resp_retorno
        )
        LEFT JOIN medico_especialidade_principal mep ON mep.cd_pessoa_fisica = coalesce(pa.cd_medico, pr.cd_medico_resp_retorno)
        LEFT JOIN tasy.especialidade_medica      em ON em.cd_especialidade = mep.cd_especialidade
        LEFT JOIN tasy.setor_atendimento         sa ON sa.cd_setor_atendimento = pa.cd_setor_atendimento
)
SELECT
    bd.nr_atendimento_origem,
    bd.nr_atendimento_retorno,
    bd.nr_prescricao,
    bd.dt_referencia,
    bd.dt_competencia_origem,
    bd.cd_estabelecimento_origem,
    bd.nm_estabelecimento_origem,
    bd.cd_estabelecimento_retorno,
    bd.nm_estabelecimento_retorno,
    bd.cd_paciente,
    bd.nm_paciente,
    bd.cd_motivo_alta_origem,
    bd.ds_motivo_alta_origem,
    bd.ie_obito_origem,
    bd.ie_transferencia_admin_origem,
    bd.cd_especialidade_retorno,
    bd.ds_especialidade_retorno,
    bd.cd_medico_retorno,
    bd.nm_medico_retorno,
    bd.cd_setor_atendimento_retorno,
    bd.ds_setor_atendimento_retorno,
    bd.dt_entrada_origem,
    bd.dt_saida_origem,
    bd.dt_entrada_retorno,
    bd.dt_saida_base_retorno,
    bd.qt_dias_ate_readmissao,
    bd.qt_horas_ate_readmissao,
    CASE
        WHEN bd.nr_atendimento_retorno IS NULL THEN
            'SEM_READMISSAO_30_DIAS'
        WHEN bd.nr_dias_ate_readmissao <= 7 THEN
            'ATE_7_DIAS'
        ELSE
            'DE_8_A_30_DIAS'
    END AS ds_faixa_readmissao,
    CASE
        WHEN bd.nr_dias_ate_readmissao >= 0
             AND bd.nr_dias_ate_readmissao <= 7 THEN
            'S'
        ELSE
            'N'
    END AS ie_readmissao_7_dias,
    CASE
        WHEN bd.nr_dias_ate_readmissao > 7
             AND bd.nr_dias_ate_readmissao <= 30 THEN
            'S'
        ELSE
            'N'
    END AS ie_readmissao_8_30_dias,
    CASE
        WHEN bd.nr_dias_ate_readmissao >= 0
             AND bd.nr_dias_ate_readmissao <= 30 THEN
            'S'
        ELSE
            'N'
    END AS ie_readmissao_30_dias_total,
    bd.ie_denominador_7_dias,
    bd.ie_denominador_30_dias
FROM
    base_detalhada bd
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
