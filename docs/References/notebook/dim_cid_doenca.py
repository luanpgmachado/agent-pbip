import argparse
import os
from functools import reduce
from datetime import date, datetime
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, concat, lit, udf, first, coalesce, desc, isnull, when, sum, count, date_trunc, max, min

from .init import *
from .sql import read_from_sql
from .query import get_formatted_query
from .watermark_delta import write_watermark_delta, load_watermark_delta
from .lib import create_key_udf_column, write_to_dw, get_DF_from_delta_file, create_key_udf_column, gera_alias_coluna, create_surrogate_key_index
from .log import write_log

import shutil

PIPELINE_NAME = 'dim_cid_doenca'

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

    cid_doenca_DF = \
        get_DF_from_delta_file(spark, os.path.join(LAKE_HOME, "stage_extract_cid_doenca")) \
            .select( \
                col("RecordKey").alias("_id"), \
                col("CD_DOENCA_CID"), \
                col("DS_DOENCA_CID") \
            )

    df = cid_doenca_DF.select( \
        col("_id"), \
        col("CD_DOENCA_CID").alias("CID___Codigo"), \
        col("DS_DOENCA_CID").alias("CID___Descricao"), \
        concat(col("CD_DOENCA_CID"), lit(" - "), col("DS_DOENCA_CID")).alias("CID___Codigo_Descricao"), \
    )

    df = \
        create_surrogate_key_index(spark, df, table_name=PIPELINE_NAME, key_column_name="_id", column_name="CID___Key")

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
