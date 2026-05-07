import argparse
import os
from datetime import date

import pyspark.sql.functions as F

from .init import *
from .watermark_delta import write_watermark_delta, load_watermark_delta
from .lib import write_to_dw, get_DF_from_source
from .log import write_log

PIPELINE_NAME = "fato_desospitalizacao_permanencia_cid_setor"
PK_NATURAL = ["nr_atendimento", "nr_seq_interno", "ie_ordem"]
SCHEMA_FINAL = None

# Indicador 6 - Media e mediana do tempo de permanencia por CID e setor
# Base preservada conforme query de referencia; complemento apenas para agrupamento por Setor + CID.

QUERY = """
WITH base_setor AS (
    SELECT
        a.nr_atendimento,
        a.dt_entrada_unidade,
        ( a.cd_unidade_basica
          || ' '
          || a.cd_unidade_compl )                            cd_unidade,
        a.cd_unidade_basica,
        a.cd_unidade_compl,
        b.dt_entrada,
        substr(
            tasy.obter_nome_pf(e.cd_pessoa_fisica),
            1,
            60
        )                                                  nm_pessoa_fisica,
        a.cd_setor_atendimento,
        e.cd_pessoa_fisica,
        e.dt_nascimento,
       --e.nr_prontuario,
        TO_NUMBER(substr(
            tasy.obter_prontuario_pf(b.cd_estabelecimento, b.cd_pessoa_fisica),
            1,
            255
        ))                                                 nr_prontuario,
        a.ie_status_unidade,
        e.ie_sexo,
        substr(
            tasy.obter_nome_convenio(c.cd_convenio),
            1,
            40
        )                                                  ds_convenio,
        substr(
            tasy.obter_categoria_convenio(c.cd_convenio, c.cd_categoria),
            1,
            40
        )                                                  ds_categoria, -- dalcastagne em 04/04/2008 os 88104
        a.cd_paciente_reserva,
        substr(
            tasy.obter_nome_pf(f.cd_pessoa_fisica),
            1,
            60
        )                                                  nm_paciente_reserva,
        a.cd_convenio_reserva,
        nm_usuario_reserva,
        d.nr_crm,
        d.nm_guerra,
        a.ie_classe_acomodacao,
        a.ie_sexo_paciente,
        a.ie_sexo_fixo,
        substr(
            tasy.obter_nome_pf(e.cd_pessoa_fisica),
            1,
            60
        )                                                  ds_status_unidade,
        a.ds_observacao,
        trunc(sysdate - b.dt_entrada, 0)                   qt_dia_permanencia,
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
        substr(
            tasy.obter_valor_dominio(1267, b.ie_probabilidade_alta),
            1,
            40
        )                                                  ds_probabilidade,
        b.cd_psicologo,
        a.ds_ocupacao,
        a.nr_agrupamento,
        a.qt_peso_maximo,
        a.qt_altura_maxima,
        c.cd_convenio,
        a.qt_tempo_prev_higien,
        a.nr_seq_motivo_reserva,
        'N'                                                ie_acompanhante,
        nvl(a.nr_seq_apresent, 999)                        nr_seq_apresent,
        nvl(a.ie_radioterapia, 'N')                        ie_radioterapia,
        b.nr_atend_alta,
        nvl(a.ie_interditado_radiacao, 'N')                ie_interditado_radiacao,
        b.cd_estabelecimento,
        e.nr_seq_perfil,
        b.cd_motivo_alta_medica,
        b.cd_medico_resp,
        b.ie_carater_inter_sus,
        b.cd_medico_referido,
        b.nr_seq_local_pa,
        b.ie_paciente_isolado,
        tasy.obter_atepacu_paciente(b.nr_atendimento, 'A') nr_seq_atepacu,
        1                                                  ie_ordem
    FROM
        tasy.pessoa_fisica            e,
        tasy.pessoa_fisica            f,
        tasy.medico                   d,
        tasy.atendimento_paciente     b,
        tasy.atend_categoria_convenio c,
        tasy.unidade_atendimento      a
    WHERE
            a.nr_atendimento = b.nr_atendimento
        AND a.nr_atendimento = c.nr_atendimento
        AND c.nr_seq_interno = tasy.obter_atecaco_atendimento(a.nr_atendimento)
        AND b.cd_pessoa_fisica = e.cd_pessoa_fisica
        AND b.cd_medico_resp = d.cd_pessoa_fisica (+)
        AND a.ie_situacao = 'A'
        AND a.ie_status_unidade IN ( 'A', 'P', 'G', 'H', 'O' )
        AND a.cd_paciente_reserva = f.cd_pessoa_fisica (+)
        AND a.nr_atendimento > 0
    UNION ALL
    SELECT
        a.nr_atendimento_acomp,
        a.dt_entrada_unidade,
        ( a.cd_unidade_basica
          || ' '
          || a.cd_unidade_compl )                            cd_unidade,
        a.cd_unidade_basica,
        a.cd_unidade_compl,
        b.dt_entrada,
        substr('Acomp '
               || tasy.obter_nome_pf(e.cd_pessoa_fisica),
               1,
               40)                                         nm_pessoa_fisica,
        a.cd_setor_atendimento,
        e.cd_pessoa_fisica,
        e.dt_nascimento,
       --e.nr_prontuario,
        TO_NUMBER(substr(
            tasy.obter_prontuario_pf(b.cd_estabelecimento, b.cd_pessoa_fisica),
            1,
            255
        ))                                                 nr_prontuario,
        a.ie_status_unidade,
        e.ie_sexo,
        substr(
            tasy.obter_nome_convenio(c.cd_convenio),
            1,
            40
        )                                                  ds_convenio,
        substr(
            tasy.obter_categoria_convenio(c.cd_convenio, c.cd_categoria),
            1,
            40
        )                                                  ds_categoria, -- dalcastagne em 04/04/2008 os 88104
        a.cd_paciente_reserva,
        substr(
            tasy.obter_nome_pf(f.cd_pessoa_fisica),
            1,
            60
        )                                                  nm_paciente_reserva,
        a.cd_convenio_reserva,
        nm_usuario_reserva,
        d.nr_crm,
        d.nm_guerra,
        a.ie_classe_acomodacao,
        a.ie_sexo_paciente,
        a.ie_sexo_fixo,
        'Acomp '
        || substr(
            tasy.obter_nome_pf(e.cd_pessoa_fisica),
            1,
            60
        )                                                  ds_status_unidade,
        a.ds_observacao,
        trunc(sysdate - b.dt_entrada, 0)                   qt_dia_permanencia,
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
        substr(
            tasy.obter_valor_dominio(1267, b.ie_probabilidade_alta),
            1,
            40
        )                                                  ds_probabilidade,
        b.cd_psicologo,
        a.ds_ocupacao,
        a.nr_agrupamento,
        a.qt_peso_maximo,
        a.qt_altura_maxima,
        c.cd_convenio                                      cd_convenio,
        a.qt_tempo_prev_higien,
        a.nr_seq_motivo_reserva,
        'S'                                                ie_acompanhante,
        nvl(a.nr_seq_apresent, 999)                        nr_seq_apresent,
        nvl(a.ie_radioterapia, 'N')                        ie_radioterapia,
        b.nr_atend_alta,
        nvl(a.ie_interditado_radiacao, 'N')                ie_interditado_radiacao,
        b.cd_estabelecimento,
        e.nr_seq_perfil,
        b.cd_motivo_alta_medica,
        b.cd_medico_resp,
        b.ie_carater_inter_sus,
        b.cd_medico_referido,
        b.nr_seq_local_pa,
        b.ie_paciente_isolado,
        tasy.obter_atepacu_paciente(b.nr_atendimento, 'A') nr_seq_atepacu,
        1                                                  ie_ordem
    FROM
        tasy.pessoa_fisica            e,
        tasy.pessoa_fisica            f,
        tasy.medico                   d,
        tasy.atendimento_paciente     b,
        tasy.atend_categoria_convenio c,
        tasy.unidade_atendimento      a
    WHERE
            a.nr_atendimento_acomp = b.nr_atendimento
        AND b.cd_pessoa_fisica = e.cd_pessoa_fisica
        AND a.nr_atendimento = c.nr_atendimento
        AND c.nr_seq_interno = tasy.obter_atecaco_atendimento(a.nr_atendimento)
        AND b.cd_medico_resp = d.cd_pessoa_fisica (+)
        AND a.ie_situacao = 'A'
        AND a.ie_status_unidade = 'M'
        AND a.cd_paciente_reserva = f.cd_pessoa_fisica
        AND a.nr_atendimento > 0
    UNION ALL
    SELECT
        a.nr_atendimento_ant                               nr_atendimento,
        a.dt_entrada_unidade,
        ( a.cd_unidade_basica
          || ' '
          || a.cd_unidade_compl )                            cd_unidade,
        a.cd_unidade_basica,
        a.cd_unidade_compl,
        b.dt_entrada,
        substr(
            tasy.obter_nome_pf(e.cd_pessoa_fisica),
            1,
            60
        )                                                  nm_pessoa_fisica,
        a.cd_setor_atendimento,
        e.cd_pessoa_fisica,
        e.dt_nascimento,
       --e.nr_prontuario,
        TO_NUMBER(substr(
            tasy.obter_prontuario_pf(b.cd_estabelecimento, b.cd_pessoa_fisica),
            1,
            255
        ))                                                 nr_prontuario,
        a.ie_status_unidade,
        e.ie_sexo,
        substr(
            tasy.obter_nome_convenio(c.cd_convenio),
            1,
            40
        )                                                  ds_convenio,
        substr(
            tasy.obter_categoria_convenio(c.cd_convenio, c.cd_categoria),
            1,
            40
        )                                                  ds_categoria, -- dalcastagne em 04/04/2008 os 88104
        a.cd_paciente_reserva,
        substr(
            tasy.obter_nome_pf(f.cd_pessoa_fisica),
            1,
            60
        )                                                  nm_paciente_reserva,
        a.cd_convenio_reserva,
        nm_usuario_reserva,
        d.nr_crm,
        d.nm_guerra,
        a.ie_classe_acomodacao,
        a.ie_sexo_paciente,
        a.ie_sexo_fixo,
        substr(
            tasy.obter_nome_pf(e.cd_pessoa_fisica),
            1,
            60
        )                                                  ds_status_unidade,
        a.ds_observacao,
        trunc(sysdate - b.dt_entrada, 0)                   qt_dia_permanencia,
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
        substr(
            tasy.obter_valor_dominio(1267, b.ie_probabilidade_alta),
            1,
            40
        )                                                  ds_probabilidade,
        b.cd_psicologo,
        a.ds_ocupacao,
        a.nr_agrupamento,
        a.qt_peso_maximo,
        a.qt_altura_maxima,
        c.cd_convenio,
        a.qt_tempo_prev_higien,
        a.nr_seq_motivo_reserva,
        'N'                                                ie_acompanhante,
        nvl(a.nr_seq_apresent, 999)                        nr_seq_apresent,
        nvl(a.ie_radioterapia, 'N')                        ie_radioterapia,
        b.nr_atend_alta,
        nvl(a.ie_interditado_radiacao, 'N')                ie_interditado_radiacao,
        b.cd_estabelecimento,
        e.nr_seq_perfil,
        b.cd_motivo_alta_medica,
        b.cd_medico_resp,
        b.ie_carater_inter_sus,
        b.cd_medico_referido,
        b.nr_seq_local_pa,
        b.ie_paciente_isolado,
        tasy.obter_atepacu_paciente(b.nr_atendimento, 'A') nr_seq_atepacu,
        1                                                  ie_ordem
    FROM
        tasy.pessoa_fisica            e,
        tasy.pessoa_fisica            f,
        tasy.medico                   d,
        tasy.atendimento_paciente     b,
        tasy.atend_categoria_convenio c,
        tasy.unidade_atendimento      a,
        tasy.parametro_medico         pm
    WHERE
            a.nr_atendimento_ant = b.nr_atendimento
        AND a.nr_atendimento_ant = c.nr_atendimento
        AND c.nr_seq_interno = tasy.obter_atecaco_atendimento(a.nr_atendimento_ant)
        AND b.cd_pessoa_fisica = e.cd_pessoa_fisica
        AND b.cd_medico_resp = d.cd_pessoa_fisica (+)
        AND a.ie_situacao = 'A'
        AND a.ie_status_unidade = 'A'
        AND a.cd_paciente_reserva = f.cd_pessoa_fisica (+)
        AND a.nr_atendimento_ant > 0
        AND a.nr_atendimento_ant IS NOT NULL
        AND a.nr_atendimento IS NULL
        AND b.dt_alta IS NOT NULL
        AND pm.cd_estabelecimento = tasy.wheb_usuario_pck.get_cd_estabelecimento
        AND nvl(pm.ie_pac_proc_alta_setor, 'S') = 'S'
    UNION ALL
    SELECT
        b.nr_atendimento,
        a.dt_entrada_unidade,
        ( a.cd_unidade_basica
          || ' '
          || a.cd_unidade_compl )                            cd_unidade,
        a.cd_unidade_basica,
        a.cd_unidade_compl,
        b.dt_entrada,
        substr(
            tasy.obter_nome_pf(e.cd_pessoa_fisica),
            1,
            60
        )                                                  nm_pessoa_fisica,
        a.cd_setor_atendimento,
        e.cd_pessoa_fisica,
        e.dt_nascimento,
       --e.nr_prontuario,
        TO_NUMBER(substr(
            tasy.obter_prontuario_pf(b.cd_estabelecimento, b.cd_pessoa_fisica),
            1,
            255
        ))                                                 nr_prontuario,
        a.ie_status_unidade,
        e.ie_sexo,
        substr(
            tasy.obter_nome_convenio(c.cd_convenio),
            1,
            40
        )                                                  ds_convenio,
        substr(
            tasy.obter_categoria_convenio(c.cd_convenio, c.cd_categoria),
            1,
            40
        )                                                  ds_categoria, -- dalcastagne em 04/04/2008 os 88104
        a.cd_paciente_reserva,
        substr(
            tasy.obter_nome_pf(f.cd_pessoa_fisica),
            1,
            60
        )                                                  nm_paciente_reserva,
        a.cd_convenio_reserva,
        nm_usuario_reserva,
        d.nr_crm,
        d.nm_guerra,
        a.ie_classe_acomodacao,
        a.ie_sexo_paciente,
        a.ie_sexo_fixo,
        substr(
            tasy.obter_nome_pf(e.cd_pessoa_fisica),
            1,
            60
        )                                                  ds_status_unidade,
        a.ds_observacao,
        trunc(sysdate - b.dt_entrada, 0)                   qt_dia_permanencia,
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
        substr(
            tasy.obter_valor_dominio(1267, b.ie_probabilidade_alta),
            1,
            40
        )                                                  ds_probabilidade,
        b.cd_psicologo,
        a.ds_ocupacao,
        a.nr_agrupamento,
        a.qt_peso_maximo,
        a.qt_altura_maxima,
        c.cd_convenio,
        a.qt_tempo_prev_higien,
        a.nr_seq_motivo_reserva,
        'N'                                                ie_acompanhante,
        nvl(a.nr_seq_apresent, 999)                        nr_seq_apresent,
        nvl(a.ie_radioterapia, 'N')                        ie_radioterapia,
        b.nr_atend_alta,
        nvl(a.ie_interditado_radiacao, 'N')                ie_interditado_radiacao,
        b.cd_estabelecimento,
        e.nr_seq_perfil,
        b.cd_motivo_alta_medica,
        b.cd_medico_resp,
        b.ie_carater_inter_sus,
        b.cd_medico_referido,
        b.nr_seq_local_pa,
        b.ie_paciente_isolado,
        tasy.obter_atepacu_paciente(b.nr_atendimento, 'A') nr_seq_atepacu,
        2                                                  ie_ordem
    FROM
        tasy.pessoa_fisica            e,
        tasy.pessoa_fisica            f,
        tasy.medico                   d,
        tasy.atendimento_paciente     b,
        tasy.atendimento_paciente     y,
        tasy.atend_categoria_convenio c,
        tasy.unidade_atendimento      a,
        tasy.atend_paciente_unidade   u,
        tasy.setor_atendimento        x,
        tasy.setor_atendimento        t
    WHERE
            a.nr_atendimento = y.nr_atendimento
        AND y.nr_atendimento = b.nr_atendimento_mae
        AND a.nr_atendimento = c.nr_atendimento
        AND c.nr_seq_interno = tasy.obter_atecaco_atendimento(a.nr_atendimento)
        AND b.cd_pessoa_fisica = e.cd_pessoa_fisica
        AND b.cd_medico_resp = d.cd_pessoa_fisica (+)
        AND u.nr_atendimento = b.nr_atendimento
        AND u.nr_seq_interno = (
            SELECT
                tasy.obter_atepacu_paciente(b.nr_atendimento, 'A')
            FROM
                dual
        )
        AND t.cd_setor_atendimento = u.cd_setor_atendimento
        AND b.dt_alta_interno = TO_DATE('30/12/2999', 'DD/MM/YYYY')
        AND a.ie_situacao = 'A'
        AND a.ie_status_unidade IN ( 'P', 'G', 'H' )
        AND x.cd_setor_atendimento = a.cd_setor_atendimento
        AND x.ie_rn_mae = 'S'
        AND a.cd_paciente_reserva = f.cd_pessoa_fisica (+)
        AND t.cd_classif_setor = '9'
        AND a.nr_atendimento > 0
        AND b.dt_cancelamento IS NULL
), diagnostico_cid AS (
    SELECT
        d.nr_atendimento,
        d.cd_doenca AS cd_cid
    FROM
        (
            SELECT
                dd.nr_atendimento,
                dd.cd_doenca,
                ROW_NUMBER()
                OVER(PARTITION BY dd.nr_atendimento
                     ORDER BY
                         CASE
                             WHEN nvl(dd.ie_diag_alta, 'N') IN('S', '1') THEN
                                 0
                             WHEN nvl(dd.ie_diag_referencia, 'N') IN('S', '1') THEN
                                 1
                             ELSE
                                 2
                         END,
                         nvl(dd.dt_liberacao, dd.dt_diagnostico) DESC,
                         dd.nr_seq_interno DESC
                ) rn
            FROM
                tasy.diagnostico_doenca dd
            WHERE
                dd.dt_inativacao IS NULL
        ) d
    WHERE
        d.rn = 1
), medidas_indicadores AS (
    SELECT
        b.*,
        dc.cd_cid,
        AVG(b.qt_dia_permanencia)
        OVER(PARTITION BY b.cd_setor_atendimento, dc.cd_cid) AS media_qt_dia_permanencia_setor_cid,
        MEDIAN(b.qt_dia_permanencia)
        OVER(PARTITION BY b.cd_setor_atendimento, dc.cd_cid) AS mediana_qt_dia_permanencia_setor_cid,
        COUNT(*)
        OVER(PARTITION BY b.cd_setor_atendimento, dc.cd_cid) AS qt_registros_setor_cid
    FROM
        base_setor      b
        LEFT JOIN diagnostico_cid dc ON dc.nr_atendimento = b.nr_atendimento
)
SELECT
    nr_atendimento,
    dt_entrada_unidade,
    cd_unidade,
    cd_unidade_basica,
    cd_unidade_compl,
    dt_entrada,
    nm_pessoa_fisica,
    cd_setor_atendimento,
    cd_pessoa_fisica,
    dt_nascimento,
    nr_prontuario,
    ie_status_unidade,
    ie_sexo,
    ds_convenio,
    ds_categoria,
    cd_paciente_reserva,
    nm_paciente_reserva,
    cd_convenio_reserva,
    nm_usuario_reserva,
    nr_crm,
    nm_guerra,
    ie_classe_acomodacao,
    ie_sexo_paciente,
    ie_sexo_fixo,
    ds_status_unidade,
    ds_observacao,
    qt_dia_permanencia,
    dt_inicio_higienizacao,
    dt_higienizacao,
    nr_seq_interno,
    dt_previsto_alta,
    dt_alta_medico,
    nm_usuario_higienizacao,
    nm_usuario_fim_higienizacao,
    nr_ramal,
    ie_temporario,
    ie_tipo_reserva,
    cd_tipo_acomodacao,
    ie_probabilidade_alta,
    ds_probabilidade,
    cd_psicologo,
    ds_ocupacao,
    nr_agrupamento,
    qt_peso_maximo,
    qt_altura_maxima,
    cd_convenio,
    qt_tempo_prev_higien,
    nr_seq_motivo_reserva,
    ie_acompanhante,
    nr_seq_apresent,
    ie_radioterapia,
    nr_atend_alta,
    ie_interditado_radiacao,
    cd_estabelecimento,
    nr_seq_perfil,
    cd_motivo_alta_medica,
    cd_medico_resp,
    ie_carater_inter_sus,
    cd_medico_referido,
    nr_seq_local_pa,
    ie_paciente_isolado,
    nr_seq_atepacu,
    ie_ordem,
    cd_cid,
    media_qt_dia_permanencia_setor_cid,
    mediana_qt_dia_permanencia_setor_cid,
    qt_registros_setor_cid
FROM
    medidas_indicadores
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
