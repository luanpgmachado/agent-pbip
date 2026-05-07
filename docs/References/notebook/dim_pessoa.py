import argparse
import os
from functools import reduce
from datetime import date, datetime
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, concat, lit, udf, first, coalesce, desc, isnull, when, sum, count, date_trunc, max, min, datediff, abs, current_date, floor

from .init import *
from .sql import read_from_sql
from .query import get_formatted_query
from .watermark_delta import write_watermark_delta, load_watermark_delta
from .lib import create_key_udf_column, read_from_dw, write_to_dw, get_DF_from_delta_file, create_key_udf_column, gera_alias_coluna, create_surrogate_key_index
from .log import write_log

import shutil

PIPELINE_NAME = 'dim_pessoa'

def run_pipeline(**kwargs):    
    arguments = kwargs.get("arguments")
    spark = kwargs.get("spark")


    if (spark is None):
        spark = create_context(arguments.name)
    
    pipeline(spark)

    return

@udf
def pessoa_descricao_sexo(s):
    if s is None:
        return "Não Informado"
    elif s == "F":
        return "Feminino"
    elif s == "M":
        return "Masculino"
    else:
        return "Indeterminado"

@udf
def pessoa_faixa_etaria(i):
    if i is None or i <= 18:
        return '0-18'
    elif i <= 49:
        return '19-49'
    elif i <= 59:
        return '50-59'
    elif i > 59:
        return '60+'

def pipeline(spark: SparkSession):

    write_log(spark, __name__, PIPELINE_NAME)
    watermark_delta_file_path = "{}/{}".format(WATERMARK_DELTA_PATH, PIPELINE_NAME)

    start_load_date = date.today()
    last_load_date = load_watermark_delta(spark, watermark_delta_file_path, PIPELINE_NAME)

    write_log(spark, __name__, "Last load date {}".format(last_load_date))

    # Remover Surrogate Folder
    sk_file_path = "{}/{}".format(SURROGATE_DELTA_PATH, PIPELINE_NAME)
    shutil.rmtree(sk_file_path, ignore_errors=True)

    # Montar o DF
    compl_pessoa_fisica_DF = \
        get_DF_from_delta_file(spark, os.path.join(LAKE_HOME, "stage_extract_compl_pessoa_fisica")) \
            .where(col("IE_TIPO_COMPLEMENTO") == 1) \
            .select( \
                col("CD_PESSOA_FISICA").alias("L_COMPL_ID_PESSOA"),
                col("CD_MUNICIPIO_IBGE"),
                col("SG_ESTADO"),
                col("DS_EMAIL")
            )

    pessoa_fisica_DF = \
        get_DF_from_delta_file(spark, os.path.join(LAKE_HOME, "stage_extract_pessoa_fisica")) \
            .select( \
                col("RecordKey"), \
                col("CD_PESSOA_FISICA").alias("ID_PESSOA"), \
                col("NM_PESSOA_FISICA").alias("NM_PESSOA"), \
                col("NR_CPF").alias("NR_CNPJ_CPF"), \
                col("DT_NASCIMENTO"), \
                col("IE_SEXO") \
            )

    pessoa_fisica_endereco_DF = pessoa_fisica_DF \
            .join(compl_pessoa_fisica_DF, on=[compl_pessoa_fisica_DF.L_COMPL_ID_PESSOA == pessoa_fisica_DF.ID_PESSOA], how='left') \
            .select( \
                col("RecordKey"), \
                col("ID_PESSOA"), \
                col("NM_PESSOA"), \
                col("NR_CNPJ_CPF"), \
                col("CD_MUNICIPIO_IBGE"), \
                col("SG_ESTADO"), \
                col("DS_EMAIL"), \
                col("DT_NASCIMENTO"), \
                col("IE_SEXO"), \
                lit("Física").alias("TP_PESSOA")
            )

    pessoa_juridica_DF = \
        get_DF_from_delta_file(spark, os.path.join(LAKE_HOME, "stage_extract_pessoa_juridica")) \
            .select( \
                col("RecordKey"),
                col("CD_CGC").alias("ID_PESSOA"),
                col("DS_RAZAO_SOCIAL").alias("NM_PESSOA"),
                col("CD_CGC").alias("NR_CNPJ_CPF"), \
                col("CD_MUNICIPIO_IBGE"), \
                col("SG_ESTADO"), \
                col("DS_EMAIL"), \
                lit(None).cast("timestamp").alias("DT_NASCIMENTO"), \
                lit("I").alias("IE_SEXO"), \
                lit("Jurídica").alias("TP_PESSOA")
            )

    dim_municipio_DF = \
        read_from_dw(spark, "dim_municipio") \
            .select( \
                col("_id").alias("L_Municipio___id"), \
                col("Municipio___Key"), \
                col("Municipio___Descricao"), \
                col("Municipio___Sigla_Estado"), \
                col("Municipio___Codigo_Descricao") \
            )

    dfs = [pessoa_fisica_endereco_DF, pessoa_juridica_DF]

    df_union = reduce(DataFrame.unionAll, dfs) \

    df = df_union \
            .withColumn("DS_SEXO", pessoa_descricao_sexo("IE_SEXO")) \
            .withColumn("Pessoa___Idade", floor(abs(datediff( current_date() , "DT_NASCIMENTO")) / lit(365))) \
            .withColumn("Pessoa___Faixa_Etaria", pessoa_faixa_etaria("Pessoa___Idade")) \
            .withColumn("Municipio___id", create_key_udf_column("CD_MUNICIPIO_IBGE")) \
            .withColumn("Pessoa___Codigo_Descricao", concat(col("ID_PESSOA"), lit("-"), col("NM_PESSOA"))) \
            .withColumnRenamed("RecordKey", "_id") \
            .withColumnRenamed("ID_PESSOA", "Pessoa___Codigo") \
            .withColumnRenamed("NM_PESSOA", "Pessoa___Nome") \
            .withColumnRenamed("NR_CNPJ_CPF", "Pessoa___CNPJ_CPF") \
            .withColumnRenamed("CD_MUNICIPIO_IBGE", "Municipio___Codigo") \
            .withColumnRenamed("DS_SEXO", "Pessoa___Sexo") \
            .withColumnRenamed("DS_EMAIL", "Pessoa___Email") \
            .withColumnRenamed("DT_NASCIMENTO", "Pessoa___Data_Nascimento") \
            .withColumnRenamed("TP_PESSOA", "Pessoa___Tipo")

    df = df \
        .join(dim_municipio_DF, on=[dim_municipio_DF.L_Municipio___id == df.Municipio___id], how='left')

    df = df \
        .select(*(_ for _ in df.columns if _ not in ['SG_ESTADO', 'IE_SEXO', 'L_Municipio___id'])) \
        .dropDuplicates(["_id"]) \
        .drop("Municipio___id")

    df = \
        create_surrogate_key_index(spark, df, table_name=PIPELINE_NAME, key_column_name="_id", column_name="Pessoa___Key")

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
