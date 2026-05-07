import argparse
import os
from datetime import date

import pyspark.sql.functions as F

from .init import *
from .watermark_delta import write_watermark_delta, load_watermark_delta
from .lib import write_to_dw, get_DF_from_source
from .log import write_log

PIPELINE_NAME = "fato_desospitalizacao_acuracia_alta"
PK_NATURAL = ["nr_atendimento"]
SCHEMA_FINAL = None

# Indicador 13 - Acuracia na possivel data da alta
QUERY = """
WITH atendimento_base AS (
    SELECT
        ap.nr_atendimento,
        ap.cd_pessoa_fisica,
        ap.cd_medico_resp                      AS cd_medico,
        apu.cd_setor_atendimento               AS cd_setor,
        ap.dt_entrada,
        ap.dt_alta,
        ap.dt_saida_real,
        coalesce(ap.dt_saida_real, ap.dt_alta) AS dt_alta_real
    FROM
        tasy.atendimento_paciente   ap
        LEFT JOIN tasy.atend_paciente_unidade apu ON apu.nr_seq_interno = tasy.obter_atepacu_paciente(ap.nr_atendimento, 'A')
    WHERE
        ap.dt_cancelamento IS NULL
        AND coalesce(ap.dt_saida_real, ap.dt_alta) IS NOT NULL
), previsao_candidata AS (
    SELECT
        ab.nr_atendimento,
        apa.nr_sequencia,
        apa.dt_previsto_alta,
        coalesce(apa.dt_liberacao, apa.dt_registro) AS dt_evento_previsao,
        CASE
            WHEN coalesce(apa.dt_liberacao, apa.dt_registro) <= ab.dt_alta_real THEN
                1
            ELSE
                0
        END                                         AS fl_previsao_antes_alta
    FROM
             atendimento_base ab
        JOIN tasy.atend_previsao_alta apa ON apa.nr_atendimento = ab.nr_atendimento
    WHERE
        apa.dt_previsto_alta IS NOT NULL
), previsao_escolhida AS (
    SELECT
        pc.nr_atendimento,
        pc.dt_previsto_alta,
        pc.dt_evento_previsao,
        pc.fl_previsao_antes_alta,
        ROW_NUMBER()
        OVER(PARTITION BY pc.nr_atendimento
             ORDER BY
                 CASE
                     WHEN pc.fl_previsao_antes_alta = 1 THEN
                         0
                     ELSE
                         1
                 END, pc.dt_evento_previsao DESC, pc.nr_sequencia DESC
        ) AS rn
    FROM
        previsao_candidata pc
), base_final AS (
    SELECT
        ab.nr_atendimento,
        ab.cd_pessoa_fisica,
        ab.cd_medico,
        ab.cd_setor,
        pf.nm_pessoa_fisica                                 AS paciente,
        ab.dt_entrada,
        ab.dt_alta,
        ab.dt_saida_real,
        pe.dt_previsto_alta                                 AS dt_prevista_alta,
        pe.dt_evento_previsao,
        ab.dt_alta_real,
        trunc(ab.dt_alta_real) - trunc(pe.dt_previsto_alta) AS qt_dif_dias_previsto_real,
        CASE
            WHEN trunc(ab.dt_alta_real) = trunc(pe.dt_previsto_alta) THEN
                1
            ELSE
                0
        END                                                 AS fl_acerto_exato,
        CASE
            WHEN trunc(ab.dt_alta_real) - trunc(pe.dt_previsto_alta) BETWEEN - 1 AND 1 THEN
                1
            ELSE
                0
        END                                                 AS fl_acerto_tolerancia
    FROM
             atendimento_base ab
        JOIN previsao_escolhida pe ON pe.nr_atendimento = ab.nr_atendimento
                                      AND pe.rn = 1
        LEFT JOIN tasy.pessoa_fisica pf ON pf.cd_pessoa_fisica = ab.cd_pessoa_fisica
)
SELECT
    bf.nr_atendimento,
    bf.cd_pessoa_fisica AS cd_paciente,
    bf.cd_medico,
    bf.cd_setor,
    bf.paciente,
    bf.dt_entrada,
    bf.dt_alta,
    bf.dt_saida_real,
    bf.dt_prevista_alta,
    bf.dt_evento_previsao,
    bf.dt_alta_real,
    bf.qt_dif_dias_previsto_real,
    bf.fl_acerto_exato,
    bf.fl_acerto_tolerancia,
    CASE
        WHEN bf.fl_acerto_tolerancia = 1 THEN
            100
        ELSE
            0
    END                 AS indicador_percentual_acuracia
FROM
    base_final bf
ORDER BY
    bf.nr_atendimento
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
