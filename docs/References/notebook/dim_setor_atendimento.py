import argparse
import os
from functools import reduce
from datetime import date, datetime
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
import pyspark.sql.functions as F

from .init import *
from .sql import read_from_sql
from .query import get_formatted_query
from .watermark_delta import write_watermark_delta, load_watermark_delta
from .lib import create_key_udf_column, read_from_dw, write_to_dw, get_DF_from_delta_file, create_key_udf_column, gera_alias_coluna, create_surrogate_key_index
from .log import write_log

import shutil

PIPELINE_NAME = 'dim_setor_atendimento'

def run_pipeline(**kwargs):    
    arguments = kwargs.get("arguments")
    spark = kwargs.get("spark")


    if (spark is None):
        spark = create_context(arguments.name)
    
    pipeline(spark)

    return

def pipeline(spark: SparkSession):

    write_log(spark, __name__, PIPELINE_NAME)
    watermark_delta_file_path = "{}/{}".format(WATERMARK_DELTA_PATH, PIPELINE_NAME)

    start_load_date = date.today()
    last_load_date = load_watermark_delta(spark, watermark_delta_file_path, PIPELINE_NAME)

    write_log(spark, __name__, "Last load date {}".format(last_load_date))

    # Remover Surrogate Folder
    sk_file_path = "{}/{}".format(SURROGATE_DELTA_PATH, PIPELINE_NAME)
    shutil.rmtree(sk_file_path, ignore_errors=True)

    # Montar DF base da dimensao
    setor_atendimento_DF = (
        get_DF_from_delta_file(spark, os.path.join(LAKE_HOME, "stage_extract_setor_atendimento"))
        .select(
            F.col("RecordKey").alias("_id"),
            F.col("CD_SETOR_ATENDIMENTO").alias("Setor_Atendimento___Codigo"),
            F.col("DS_SETOR_ATENDIMENTO").alias("Setor_Atendimento___Descricao"),
            F.col("CD_CENTRO_CUSTO").alias("Centro_Custo___Codigo"),
            F.col("CD_CLASSIF_SETOR").alias("Classificacao_Setor___Codigo"),
        )
    )

    centro_custo_DF = (
        get_DF_from_delta_file(spark, os.path.join(LAKE_HOME, "stage_extract_centro_custo"))
        .select(
            F.col("CD_CENTRO_CUSTO"),
            F.col("DS_CENTRO_CUSTO").alias("Centro_Custo___Descricao"),
        )
    )

    classificacao_setor_DF = (
        get_DF_from_delta_file(spark, os.path.join(LAKE_HOME, "stage_extract_valor_dominio_classificacao_setor"))
        .select(
            F.col("CD_CLASSIF_SETOR"),
            F.col("DS_CLASSIF_SETOR").alias("Classificacao_Setor___Descricao"),
        )
    )

    sql_qt_unidade = """
    SELECT
        TASY.obter_qt_unidades_setor(s.cd_setor_atendimento) AS qt_unidade_setor,
        s.cd_setor_atendimento
    FROM TASY.setor_atendimento s
    WHERE s.ie_situacao = 'A'
    """

    qt_unidade_setor_DF = (
        get_DF_from_source(spark, sql_qt_unidade)
        .select(
            F.col("CD_SETOR_ATENDIMENTO").alias("Setor_Atendimento___Codigo"),
            F.col("QT_UNIDADE_SETOR").cast("decimal(10,0)").alias("Setor_Atendimento___Qt_Unidade_Setor"),
        )
    )


    df = (
        setor_atendimento_DF
            .join(centro_custo_DF, on=[centro_custo_DF.CD_CENTRO_CUSTO == setor_atendimento_DF.Centro_Custo___Codigo], how="left")
            .join(classificacao_setor_DF, on=[classificacao_setor_DF.CD_CLASSIF_SETOR == setor_atendimento_DF.Classificacao_Setor___Codigo], how="left")
            .join(qt_unidade_setor_DF, on="Setor_Atendimento___Codigo", how="inner")
    )


    df = (
        df
            .select(*(_ for _ in df.columns if _ not in ["CD_CENTRO_CUSTO", "CD_CLASSIF_SETOR"]))
            .withColumn("Setor_Atendimento___Codigo_Descricao", F.concat(F.col("Setor_Atendimento___Codigo"), F.lit("-"), F.col("Setor_Atendimento___Descricao")))
            .withColumn("Classificacao_Setor___Codigo_Descricao", F.concat(F.col("Classificacao_Setor___Codigo"), F.lit("-"), F.col("Classificacao_Setor___Descricao")))
    )


    df = create_surrogate_key_index(
        spark,
        df,
        table_name=PIPELINE_NAME,
        key_column_name="_id",
        column_name="Setor_Atendimento___Key",
    )

    pipeline_file = os.path.join(LAKE_HOME, PIPELINE_NAME)
    write_log(spark, __name__, pipeline_file)

    write_to_dw(df, pipeline_file)
    write_watermark_delta(spark, watermark_delta_file_path, PIPELINE_NAME, start_load_date)


    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Executar o pipeline')
    parser.add_argument('-name', required=True, type=str, help='Nome do contexto do pipeline')
    arguments = parser.parse_args()
    run_pipeline(arguments=arguments)
