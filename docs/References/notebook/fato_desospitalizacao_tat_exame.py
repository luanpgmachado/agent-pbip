import argparse
import os
from datetime import date

import pyspark.sql.functions as F

from .init import *
from .watermark_delta import write_watermark_delta, load_watermark_delta
from .lib import write_to_dw, get_DF_from_source
from .log import write_log

PIPELINE_NAME = "fato_exame_prescricao"
PK_NATURAL = ["nr_prescricao"]
SCHEMA_FINAL = [
    ("NR_PRESCRICAO", "string"),
    ("CD_PROTOCOLO", "string"),
    ("NR_SEQ_PROTOCOLO", "string"),
    ("CD_ESTABELECIMENTO", "string"),
    ("NR_ATENDIMENTO", "string"),
    ("CD_MEDICO", "string"),
    ("DT_PRESCRICAO", "date"),
    ("DT_LIBERACAO", "date"),
    ("DT_LIBERACAO_MEDICO", "date"),
    ("IE_RECEM_NATO", "string"),
    ("DT_ENTRADA", "date"),
    ("CD_SETOR_PACIENTE", "string"),
    ("NM_PACIENTE", "string"),
    ("NM_PACIENTE_SEM_ACENTO", "string"),
    ("DT_NASCIMENTO", "date"),
    ("DT_MESTRUACAO", "date"),
    ("IE_SEXO", "string"),
    ("QT_PESO", "string"),
    ("NM_PESSOA_RESPONSAVEL", "string"),
    ("NR_CPF_RESP", "string"),
    ("NR_CPF", "string"),
    ("NR_TELEFONE_RESP", "string"),
    ("NR_PRONTUARIO", "string"),
    ("CD_PROCEDENCIA", "string"),
    ("DS_SENHA", "string"),
    ("NM_MEDICO", "string"),
    ("NR_CPF_MEDICO", "string"),
    ("NR_CRM", "string"),
    ("UF_CRM", "string"),
    ("CD_CONVENIO", "string"),
    ("QT_ALTURA_CM", "string"),
    ("CD_CATEGORIA", "string"),
    ("QT_DOSE", "string"),
    ("DT_ULTIMA_DOSE", "date"),
    ("CD_USUARIO_CONVENIO", "string"),
    ("DT_VALIDADE_CARTEIRA", "date"),
    ("NR_DOC_CONVENIO", "string"),
    ("IE_TIPO_GUIA", "string"),
    ("DS_CONVENIO", "string"),
    ("CD_CGC_CONV", "string"),
    ("CD_REGIONAL_CONV", "string"),
    ("DS_ENDERECO", "string"),
    ("NR_ENDERECO", "string"),
    ("DS_COMPLEMENTO", "string"),
    ("DS_BAIRRO", "string"),
    ("DS_MUNICIPIO", "string"),
    ("SG_ESTADO", "string"),
    ("NR_TELEFONE", "string"),
    ("CD_CEP", "string"),
    ("DS_SETOR_PACIENTE", "string"),
    ("CD_UNIDADE", "string"),
    ("CD_ESTABELECIMENTO_FILTRO", "string"),
    ("DS_MEDICAMENTO_USO", "string"),
    ("NM_MAE", "string"),
    ("IE_TIPO_ATENDIMENTO", "string"),
    ("COR_PELE", "string"),
    ("NM_SOCIAL", "string"),
    ("DS_CLASSIFIC_PA", "string"),
    ("CD_CID", "string"),
    ("IE_STATUS_EXECUCAO", "string"),
    ("CD_DOMINIO", "string"),
    ("DT_RESULTADO", "date"),
    ("DT_RESULTADO_IMAGEM", "date"),
    ("DT_EXAME_IMAGEM", "date"),
    ("DT_LIBERACAO_IMAGEM", "date"),
    ("DT_APROVACAO_IMAGEM", "date"),
    ("DT_COLETA_DATA", "date"),
    ("DT_RESULTADO_ER", "date"),
    ("DT_LIBERACAO_ER", "date"),
    ("DT_RESULTADO_LIBERACAO_ER", "date"),
    ("QT_RESULTADO_ER", "string"),
    ("DT_PRESCRICAO_FMT", "date"),
    ("DT_RESULTADO_PP_FMT", "date"),
    ("DT_RESULTADO_ER_FMT", "date"),
    ("DT_LIBERACAO_ER_FMT", "date"),
    ("DT_RESULTADO_LIBERACAO_ER_FMT", "date"),
    ("DT_RESULTADO_IMAGEM_FMT", "date"),
    ("DT_EXAME_IMAGEM_FMT", "date"),
    ("DT_COLETA_FMT", "date"),
    ("DT_RESULTADO_REAL", "date"),
    ("DT_RESULTADO_FMT", "date"),
    ("DT_COLETA_REAL", "date"),
    ("DT_EVENTO_FINAL", "date"),
    ("DT_EVENTO_FINAL_FMT", "date"),
    ("TAT_RESULTADO_HORAS", "double"),
    ("TAT_COLETA_HORAS", "double"),
    ("TAT_HORAS", "double"),
    ("ORIGEM_EVENTO_TAT", "string"),
    ("FL_SEM_DATA_RESULTADO_REAL", "string"),
    ("FL_USOU_FALLBACK_COLETA", "string"),
    ("TAT_HORAS_ARRED", "double"),
    ("TAT_DAY_ARRED", "double"),
]

# Indicador 02 - Tempo entre prescrição e resultado de exame

QUERY = """
WITH parametros AS (
    SELECT
        /*+ INLINE */
        365 AS qt_dias_periodo
    FROM
        dual
), prescricao_base AS (
    SELECT DISTINCT
        pp2.nr_controle_exame,
        pp2.nr_prescricao,
        pp2.nr_sequencia,
        pp2.ie_amostra,
            -- dt_resultado como DATE (sem TO_CHAR) para permitir agregacao
        pp2.dt_resultado,
        to_char(pp2.dt_resultado, 'hh24:mi:ss')                  hr_resultado,
        pp2.dt_prev_execucao,
        pm2.nr_atendimento,
        pm2.dt_mestruacao,
        pm2.dt_liberacao_medico,
        pm2.qt_peso,
        pm2.ie_recem_nato,
        pm2.dt_prescricao,
        pp2.ie_se_necessario,
        pp2.nm_usuario,
        pp2.dt_atualizacao,
        pp2.ds_horarios,
        pp2.cd_protocolo,
        pp2.nr_seq_protocolo,
        pm2.cd_estabelecimento,
        pp2.ds_observacao_coleta,
        pp2.cd_setor_atendimento,
        pp2.ds_dado_clinico,
        pm2.dt_liberacao,
        pp2.ie_suspenso,
        pp2.ie_executar_leito,
        pp2.qt_procedimento,
        pp2.cd_material_exame,
        pp2.nr_seq_proc_interno,
        pp2.ie_urgencia,
        pp2.nr_seq_exame,
        pm2.cd_medico,
        pm2.cd_pessoa_fisica,
        pp2.cd_procedimento,
        pp2.ds_material_especial,
        pp2.ds_observacao,
        pm2.qt_altura_cm,
        pm2.cd_recem_nato,
        pp2.ie_origem_proced,
        pp2.ie_status_execucao,
        lp2.ie_envia_vl_proced_ws,
        upper(sa2.nm_usuario_banco)                              nm_usuario_banco,
        senha_sub.ds_senha_fila                                  ds_senha_fila,
        lp2.ie_env_senha_ws                                      ie_env_senha_ws,
        lp2.ie_env_email_ws,
        lp2.ie_env_obs_ws,
        pm2.ds_observacao                                        ds_prescr_obs,
        lp2.ie_env_cpf_resp_ws,
        decode(lp2.ie_enviar_info_cartao_nac_sus,
               'S',
               tasy.obter_dados_pf(pm2.cd_pessoa_fisica, 'CNS')) nr_cartao_nac_sus,
        decode(lp2.ie_enviar_info_cid,
               'S',
               tasy.obter_cid_pf(pm2.cd_pessoa_fisica, 'C'))     cd_cid
    FROM
             tasy.prescr_medica pm2
        INNER JOIN tasy.prescr_procedimento pp2 ON pp2.nr_prescricao = pm2.nr_prescricao
        INNER JOIN tasy.setor_atendimento   sa2 ON pp2.cd_setor_atendimento = sa2.cd_setor_atendimento
        LEFT JOIN tasy.lab_parametro       lp2 ON pm2.cd_estabelecimento = lp2.cd_estabelecimento
        OUTER APPLY (
            SELECT
                upper(substr(
                    tasy.obter_letra_verifacao_senha(nvl(psf.nr_seq_fila_senha_origem, psf.nr_seq_fila_senha)),
                    1,
                    10
                )
                      || psf.cd_senha_gerada) AS ds_senha_fila
            FROM
                     tasy.paciente_senha_fila psf
                INNER JOIN tasy.atendimento_paciente ap2 ON ap2.nr_seq_pac_senha_fila = psf.nr_sequencia
            WHERE
                    ap2.nr_atendimento = pm2.nr_atendimento
                AND lp2.ie_env_senha_ws = 'S'
        ) senha_sub
    WHERE
        pp2.dt_integracao IS NULL
        AND ( pp2.cd_motivo_baixa = 0
              OR pp2.ie_status_execucao IN ( '30', '40' ) )
        AND nvl(pp2.ie_suspenso, 'N') = 'N'
        AND ( nvl(pm2.dt_liberacao_medico, pm2.dt_liberacao) > sysdate - nvl(lp2.qt_dias_int_webs, 3)
              OR pp2.ie_status_execucao IN ( '30', '40' ) )
        AND pm2.dt_prescricao > sysdate - (
            SELECT
                qt_dias_periodo
            FROM
                parametros
        )
        AND ( pp2.nr_seq_exame IS NOT NULL
              OR pp2.ie_status_execucao IN ( '30', '40' ) )
), atend_paciente_unidade_atual AS (
    SELECT
        pb.nr_atendimento,
        apu.nr_seq_interno,
        row_number()
        OVER(PARTITION BY pb.nr_atendimento
             ORDER BY nvl(apu.dt_saida_unidade, apu.dt_entrada_unidade + 9999) DESC, apu.nr_seq_interno DESC) AS rn
    FROM
            (
                SELECT DISTINCT
                    nr_atendimento
                FROM
                    prescricao_base
            ) pb
        INNER JOIN tasy.atend_paciente_unidade apu ON apu.nr_atendimento = pb.nr_atendimento
), atend_categoria_prioritaria AS (
    SELECT
        pb.nr_atendimento,
        acc.nr_seq_interno,
        row_number()
        OVER(PARTITION BY pb.nr_atendimento
             ORDER BY coalesce(acc.nr_prioridade, 0), acc.dt_inicio_vigencia DESC, acc.nr_seq_interno DESC) AS rn
    FROM
            (
                SELECT DISTINCT
                    nr_atendimento
                FROM
                    prescricao_base
            ) pb
        INNER JOIN tasy.atend_categoria_convenio acc ON acc.nr_atendimento = pb.nr_atendimento
), atendimento_chaves AS (
    SELECT DISTINCT
        pb.nr_atendimento,
        nvl(apu.nr_seq_interno, 0) AS nr_seq_interno_apu,
        nvl(acp.nr_seq_interno, 0) AS nr_seq_interno_acc
    FROM
            prescricao_base pb
        LEFT JOIN atend_paciente_unidade_atual apu ON apu.nr_atendimento = pb.nr_atendimento
                                                       AND apu.rn = 1
        LEFT JOIN atend_categoria_prioritaria acp ON acp.nr_atendimento = pb.nr_atendimento
                                                     AND acp.rn = 1
), laudo_filtrado AS (
    SELECT
        lp.nr_prescricao,
        lp.nr_seq_prescricao,
        lp.dt_exame,
        lp.dt_liberacao,
        lp.dt_aprovacao
    FROM
             tasy.laudo_paciente lp
        CROSS JOIN parametros p
    WHERE
        nvl(lp.dt_liberacao, lp.dt_aprovacao) >= trunc(sysdate) - p.qt_dias_periodo
        OR lp.dt_exame >= trunc(sysdate) - p.qt_dias_periodo
), base_dados AS (
    SELECT DISTINCT
        a.nr_prescricao,
        a.cd_protocolo,
        a.nr_seq_protocolo,
        a.nr_sequencia,
        a.cd_estabelecimento                                                                                           cd_estab_filtro
        ,
        a.cd_procedimento,
        tasy.elimina_caractere_especial(proc.ds_procedimento)                                                          ds_procedimento
        ,
        a.qt_procedimento,
        a.dt_atualizacao,
        a.nm_usuario,
        a.ds_observacao,
        a.ie_origem_proced,
        a.ie_urgencia,
        a.ds_dado_clinico,
        a.ie_suspenso,
        a.cd_setor_atendimento,
        a.nr_atendimento,
        a.cd_medico,
        a.dt_prescricao,
        a.dt_liberacao,
        a.dt_liberacao_medico,
        a.ie_recem_nato,
        to_char(ap.dt_entrada, 'dd/mm/yyyy hh24:mi:ss')                                                                dt_entrada,
        apu.cd_setor_atendimento                                                                                       cd_setor_paciente
        ,
        tasy.elimina_caractere_especial(decode(a.cd_recem_nato,
                                               NULL,
                                               tasy.obter_nome_pf(a.cd_pessoa_fisica),
                                               substr(
                                                    tasy.obter_nome_pf(a.cd_recem_nato),
                                                    1,
                                                    80
                                                )
                                               || 'RN de '
                                               || tasy.obter_nome_pf(a.cd_pessoa_fisica)))                                                                    nm_paciente
                                               ,
        tasy.elimina_acentuacao(upper(decode(a.cd_recem_nato,
                                             NULL,
                                             tasy.obter_nome_pf(a.cd_pessoa_fisica),
                                             substr(
                                                  tasy.obter_nome_pf(a.cd_recem_nato),
                                                  1,
                                                  80
                                              )
                                             || 'RN de '
                                             || tasy.obter_nome_pf(a.cd_pessoa_fisica))))                                                                   nm_paciente_sem_acento
                                             ,
        tasy.obter_dados_pf(a.cd_pessoa_fisica, 'DN')                                                                  dt_nascimento,
        to_char(a.dt_mestruacao, 'dd/mm/yyyy hh24:mi:ss')                                                              dt_mestruacao,
        tasy.obter_dados_pf(a.cd_pessoa_fisica, 'SE')                                                                  ie_sexo,
        a.qt_peso,
        substr(
            tasy.obter_nome_pessoa_fisica(ap.cd_pessoa_responsavel, NULL),
            1,
            40
        )                                                                                                              nm_pessoa_responsavel
        ,
        decode(a.ie_env_cpf_resp_ws,
               'S',
               tasy.obter_dados_pf(ap.cd_pessoa_responsavel, 'CPF'))                                                   nr_cpf_resp,
        tasy.obter_dados_pf(a.cd_pessoa_fisica, 'CPF')                                                                 nr_cpf,
        substr(
            tasy.obter_descricao_padrao('PESSOA_FISICA', 'NR_TELEFONE_CELULAR', ap.cd_pessoa_responsavel),
            1,
            20
        )                                                                                                              nr_telefone_resp
        ,
        decode(
            tasy.obter_prontuario_pf(a.cd_estabelecimento, a.cd_pessoa_fisica),
            0,
            NULL,
            tasy.obter_prontuario_pf(a.cd_estabelecimento, a.cd_pessoa_fisica)
        )                                                                                                              nr_prontuario,
        ap.cd_procedencia,
        a.ds_observacao_coleta,
        ap.ds_senha,
        tasy.obter_nome_pf(med.cd_pessoa_fisica)                                                                       nm_medico,
        tasy.obter_dados_pf(med.cd_pessoa_fisica, 'CPF')                                                               nr_cpf_medico,
        med.nr_crm,
            -- dt_resultado mantido como DATE nesta CTE (sem TO_CHAR)
        a.dt_resultado,
        a.hr_resultado,
        a.ie_status_execucao,
        med.uf_crm,
        acc.cd_convenio,
        a.qt_altura_cm,
        tasy.lab_obter_data_coleta_amostra(a.nr_prescricao, a.nr_sequencia)                                            dt_coleta_data
        ,
        to_char(
            tasy.lab_obter_data_coleta_amostra(a.nr_prescricao, a.nr_sequencia),
            'dd/mm/yyyy hh24:mi:ss'
        )                                                                                                              dt_coleta,
        acc.cd_categoria,
        tasy.lab_obter_dados_pac_med_uso(a.cd_pessoa_fisica, 'Q')                                                      qt_dose,
        tasy.lab_obter_dados_pac_med_uso(a.cd_pessoa_fisica, 'D')                                                      dt_ultima_dose
        ,
        acc.cd_usuario_convenio,
        acc.dt_validade_carteira,
        acc.nr_doc_convenio,
        acc.ie_tipo_guia,
        tasy.elimina_caractere_especial(conv.ds_convenio)                                                              ds_convenio,
        conv.cd_cgc                                                                                                    cd_cgc_conv,
        conv.cd_regional                                                                                               cd_regional_conv
        ,
        a.cd_material_exame,
        mel.ds_material_exame,
        el.cd_exame,
        el.nm_exame,
        tasy.elimina_caractere_especial(a.ds_material_especial)                                                        ds_material_especial
        ,
        nvl(a.ie_amostra, 'N')                                                                                         ie_amostra_entregue
        ,
        a.ds_horarios,
        a.nr_seq_exame,
        tasy.elimina_caractere_especial(tasy.obter_dados_compl_pf_data(a.cd_pessoa_fisica, 1, NULL, 'ds_endereco'))    ds_endereco,
        tasy.obter_dados_compl_pf_data(a.cd_pessoa_fisica, 1, NULL, 'nr_endereco')                                     nr_endereco,
        tasy.elimina_caractere_especial(tasy.obter_dados_compl_pf_data(a.cd_pessoa_fisica, 1, NULL, 'ds_complemento')) ds_complemento
        ,
        tasy.elimina_caractere_especial(tasy.obter_dados_compl_pf_data(a.cd_pessoa_fisica, 1, NULL, 'ds_bairro'))      ds_bairro,
        tasy.elimina_caractere_especial(tasy.obter_dados_compl_pf_data(a.cd_pessoa_fisica, 1, NULL, 'ds_municipio'))   ds_municipio,
        tasy.obter_dados_compl_pf_data(a.cd_pessoa_fisica, 1, NULL, 'sg_estado')                                       sg_estado,
        tasy.lab_obter_dados_pac_prescricao(a.nr_prescricao, a.cd_pessoa_fisica)                                       nr_telefone,
        tasy.obter_dados_compl_pf_data(a.cd_pessoa_fisica, 1, NULL, 'cd_cep')                                          cd_cep,
        a.dt_prev_execucao,
        sa.ds_setor_atendimento                                                                                        ds_setor_paciente
        ,
        apu.cd_unidade_basica
        || ' '
        || cd_unidade_compl                                                                                            cd_unidade,
        decode(
            nvl(a.ie_envia_vl_proced_ws, 'S'),
            'S',
            tasy.obter_preco_procedimento(ap.cd_estabelecimento, acc.cd_convenio, acc.cd_categoria, a.dt_prescricao, a.cd_procedimento
            ,
                                          a.ie_origem_proced, acc.cd_tipo_acomodacao, ap.ie_tipo_atendimento, apu.cd_setor_atendimento
                                          , a.cd_medico,
                                          NULL, acc.cd_usuario_convenio, acc.cd_plano_convenio, ap.ie_clinica, acc.cd_empresa,
                                          'P'),
            ''
        )                                                                                                              vl_procedimento
        ,
        a.ie_executar_leito,
        a.cd_recem_nato,
        substr(
            tasy.obter_nome_pf(a.cd_recem_nato),
            1,
            80
        )                                                                                                              nm_recem_nato,
        el.nr_seq_grupo,
        nvl(
            substr(
                tasy.obter_estab_integracao(a.cd_estabelecimento, 19),
                1,
                20
            ),
            a.cd_estabelecimento
        )                                                                                                              cd_estabelecimento
        ,
        a.nr_seq_proc_interno,
        substr(
            tasy.obter_proc_interno(a.nr_seq_proc_interno, 'CI'),
            1,
            20
        )                                                                                                              cd_interno_integracao
        ,
        el.cd_exame_integracao                                                                                         cd_exame_integracao
        ,
        mel.cd_material_integracao,
        a.nr_controle_exame                                                                                            nr_controle_exame
        ,
        substr(
            tasy.obter_medic_hist_saude_atend(ap.nr_atendimento),
            1,
            2000
        )                                                                                                              ds_medicamento_uso
        ,
        tasy.elimina_caractere_especial(substr(
            tasy.obter_compl_pf(a.cd_pessoa_fisica, 5, 'N'),
            1,
            255
        ))                                                                                                             nm_mae,
        ap.ie_tipo_atendimento,
        tasy.obter_dados_pf(a.cd_pessoa_fisica, 'CP')                                                                  cor_pele,
        tasy.elimina_caractere_especial(tasy.obter_dados_pf(a.cd_pessoa_fisica, 'NSOC'))                               nm_social,
        substr(
            tasy.obter_triagem_atendimento(ap.nr_atendimento, 'C'),
            1,
            255
        )                                                                                                              ds_classific_pa
        ,
        a.cd_estabelecimento                                                                                           cd_estabelecimento_filtro
        ,
        a.nm_usuario_banco                                                                                             nm_usuario_banco
        ,
        a.ds_senha_fila                                                                                                ds_senha_fila,
        decode(a.ie_env_senha_ws, 'S', ap.dt_inicio_atendimento)                                                       dt_inicio_atendimento
        ,
        decode(a.ie_env_email_ws,
               'S',
               tasy.obter_dados_compl_pf_data(a.cd_pessoa_fisica, 1, NULL, 'ds_email'))                                ds_email,
        decode(a.ie_env_obs_ws, 'S', a.ds_prescr_obs)                                                                  ds_prescr_obs,
        a.nr_cartao_nac_sus,
        a.cd_cid,
        lpac.dt_exame                                                                                                  AS dt_exame_imagem
        ,
        lpac.dt_liberacao                                                                                              AS dt_liberacao_imagem
        ,
        lpac.dt_aprovacao                                                                                              AS dt_aprovacao_imagem
        ,
        nvl(lpac.dt_liberacao, lpac.dt_aprovacao)                                                                      AS dt_resultado_imagem
        ,
        CASE
            WHEN nvl(lpac.dt_liberacao, lpac.dt_aprovacao) IS NOT NULL
                 OR a.ie_status_execucao IN ( '30', '40' ) THEN
                'IMAGEM'
            WHEN a.ie_status_execucao IN ( '10', '20' ) THEN
                'LABORATORIO'
            ELSE
                'NAO_CLASSIFICADO'
        END                                                                                                            AS cd_dominio
    FROM
             prescricao_base a
        INNER JOIN atendimento_chaves            ach ON ach.nr_atendimento = a.nr_atendimento
        INNER JOIN tasy.atend_paciente_unidade   apu ON apu.nr_seq_interno = ach.nr_seq_interno_apu
        INNER JOIN tasy.setor_atendimento        sa ON apu.cd_setor_atendimento = sa.cd_setor_atendimento
        INNER JOIN tasy.procedimento             proc ON a.cd_procedimento = proc.cd_procedimento
                                             AND a.ie_origem_proced = proc.ie_origem_proced
        INNER JOIN tasy.atend_categoria_convenio acc ON acc.nr_atendimento = a.nr_atendimento
                                                        AND acc.nr_seq_interno = ach.nr_seq_interno_acc
        INNER JOIN tasy.convenio                 conv ON acc.cd_convenio = conv.cd_convenio
        LEFT JOIN tasy.medico                   med ON a.cd_medico = med.cd_pessoa_fisica
        LEFT JOIN tasy.exame_laboratorio        el ON a.nr_seq_exame = el.nr_seq_exame
        LEFT JOIN laudo_filtrado                lpac ON lpac.nr_prescricao = a.nr_prescricao
                                         AND lpac.nr_seq_prescricao = a.nr_sequencia
        LEFT JOIN tasy.material_exame_lab       mel ON a.cd_material_exame = mel.cd_material_exame
        INNER JOIN tasy.atendimento_paciente     ap ON ap.nr_atendimento = a.nr_atendimento
    WHERE
            nvl(el.ie_anatomia_patologica, 'N') <> 'S'
        AND ( tasy.lab_valida_realiza_integracao(a.nr_prescricao, a.nr_sequencia) = 'S'
              OR nvl(lpac.dt_liberacao, lpac.dt_aprovacao) IS NOT NULL
              OR a.ie_status_execucao IN ( '30', '40' ) )
        AND ( a.dt_resultado IS NOT NULL
              OR nvl(lpac.dt_liberacao, lpac.dt_aprovacao) IS NOT NULL
              OR a.ie_status_execucao IN ( '30', '40' ) )
), resultado_consolidado AS (
    SELECT
        /*+ MATERIALIZE */
        nr_prescricao,
        MAX(cd_protocolo)              AS cd_protocolo,
        MAX(nr_seq_protocolo)          AS nr_seq_protocolo,
        MAX(cd_estabelecimento)        AS cd_estabelecimento,
        MAX(nr_atendimento)            AS nr_atendimento,
        MAX(cd_medico)                 AS cd_medico,
        MIN(dt_prescricao)             AS dt_prescricao,
        MAX(dt_liberacao)              AS dt_liberacao,
        MAX(dt_liberacao_medico)       AS dt_liberacao_medico,
        MAX(ie_recem_nato)             AS ie_recem_nato,
        MAX(dt_entrada)                AS dt_entrada,
        MAX(cd_setor_paciente)         AS cd_setor_paciente,
        MAX(nm_paciente)               AS nm_paciente,
        MAX(nm_paciente_sem_acento)    AS nm_paciente_sem_acento,
        MAX(dt_nascimento)             AS dt_nascimento,
        MAX(dt_mestruacao)             AS dt_mestruacao,
        MAX(ie_sexo)                   AS ie_sexo,
        MAX(qt_peso)                   AS qt_peso,
        MAX(nm_pessoa_responsavel)     AS nm_pessoa_responsavel,
        MAX(nr_cpf_resp)               AS nr_cpf_resp,
        MAX(nr_cpf)                    AS nr_cpf,
        MAX(nr_telefone_resp)          AS nr_telefone_resp,
        MAX(nr_prontuario)             AS nr_prontuario,
        MAX(cd_procedencia)            AS cd_procedencia,
        MAX(ds_senha)                  AS ds_senha,
        MAX(nm_medico)                 AS nm_medico,
        MAX(nr_cpf_medico)             AS nr_cpf_medico,
        MAX(nr_crm)                    AS nr_crm,
        MAX(uf_crm)                    AS uf_crm,
        MAX(cd_convenio)               AS cd_convenio,
        MAX(qt_altura_cm)              AS qt_altura_cm,
        MAX(cd_categoria)              AS cd_categoria,
        MAX(qt_dose)                   AS qt_dose,
        MAX(dt_ultima_dose)            AS dt_ultima_dose,
        MAX(cd_usuario_convenio)       AS cd_usuario_convenio,
        MAX(dt_validade_carteira)      AS dt_validade_carteira,
        MAX(nr_doc_convenio)           AS nr_doc_convenio,
        MAX(ie_tipo_guia)              AS ie_tipo_guia,
        MAX(ds_convenio)               AS ds_convenio,
        MAX(cd_cgc_conv)               AS cd_cgc_conv,
        MAX(cd_regional_conv)          AS cd_regional_conv,
        MAX(ds_endereco)               AS ds_endereco,
        MAX(nr_endereco)               AS nr_endereco,
        MAX(ds_complemento)            AS ds_complemento,
        MAX(ds_bairro)                 AS ds_bairro,
        MAX(ds_municipio)              AS ds_municipio,
        MAX(sg_estado)                 AS sg_estado,
        MAX(nr_telefone)               AS nr_telefone,
        MAX(cd_cep)                    AS cd_cep,
        MAX(ds_setor_paciente)         AS ds_setor_paciente,
        MAX(cd_unidade)                AS cd_unidade,
        MAX(cd_estabelecimento_filtro) AS cd_estabelecimento_filtro,
        MAX(ds_medicamento_uso)        AS ds_medicamento_uso,
        MAX(nm_mae)                    AS nm_mae,
        MAX(ie_tipo_atendimento)       AS ie_tipo_atendimento,
        MAX(cor_pele)                  AS cor_pele,
        MAX(nm_social)                 AS nm_social,
        MAX(ds_classific_pa)           AS ds_classific_pa,
        MAX(cd_cid)                    AS cd_cid,
        MAX(ie_status_execucao)        AS ie_status_execucao,
        CASE
            WHEN MAX(
                CASE
                    WHEN cd_dominio = 'IMAGEM' THEN
                        1
                    ELSE
                        0
                END
            ) = 1 THEN
                'IMAGEM'
            WHEN MAX(
                CASE
                    WHEN cd_dominio = 'LABORATORIO' THEN
                        1
                    ELSE
                        0
                END
            ) = 1 THEN
                'LABORATORIO'
            ELSE
                'NAO_CLASSIFICADO'
        END                            AS cd_dominio,
        MAX(dt_resultado)              AS dt_resultado,
        MAX(dt_resultado_imagem)       AS dt_resultado_imagem,
        MAX(dt_exame_imagem)           AS dt_exame_imagem,
        MAX(dt_liberacao_imagem)       AS dt_liberacao_imagem,
        MAX(dt_aprovacao_imagem)       AS dt_aprovacao_imagem,
        MAX(dt_coleta_data)            AS dt_coleta_data
    FROM
        base_dados
    GROUP BY
        nr_prescricao
), resultado_exame_por_prescricao AS (
    SELECT
        er.nr_prescricao,
        MAX(er.dt_resultado) AS dt_resultado_er,
        MAX(er.dt_liberacao) AS dt_liberacao_er,
        COUNT(*)             AS qt_resultado_er
    FROM
             tasy.exame_lab_resultado er
        INNER JOIN resultado_consolidado rc ON rc.nr_prescricao = er.nr_prescricao
        CROSS JOIN parametros            p
    WHERE
        nvl(er.dt_resultado, er.dt_liberacao) >= trunc(sysdate) - p.qt_dias_periodo
    GROUP BY
        er.nr_prescricao
), resultado_final AS (
    SELECT
        rc.*,
        er.dt_resultado_er,
        er.dt_liberacao_er,
        coalesce(er.dt_resultado_er, er.dt_liberacao_er)         AS dt_resultado_liberacao_er,
        er.qt_resultado_er,
        to_char(rc.dt_prescricao, 'dd/mm/yyyy hh24:mi:ss')       AS dt_prescricao_fmt,
        to_char(rc.dt_resultado, 'dd/mm/yyyy hh24:mi:ss')        AS dt_resultado_pp_fmt,
        to_char(er.dt_resultado_er, 'dd/mm/yyyy hh24:mi:ss')     AS dt_resultado_er_fmt,
        to_char(er.dt_liberacao_er, 'dd/mm/yyyy hh24:mi:ss')     AS dt_liberacao_er_fmt,
        to_char(
            coalesce(er.dt_resultado_er, er.dt_liberacao_er),
            'dd/mm/yyyy hh24:mi:ss'
        )                                                        AS dt_resultado_liberacao_er_fmt,
        to_char(rc.dt_resultado_imagem, 'dd/mm/yyyy hh24:mi:ss') AS dt_resultado_imagem_fmt,
        to_char(rc.dt_exame_imagem, 'dd/mm/yyyy hh24:mi:ss')     AS dt_exame_imagem_fmt,
        to_char(rc.dt_coleta_data, 'dd/mm/yyyy hh24:mi:ss')      AS dt_coleta_fmt,
        CASE
            WHEN rc.cd_dominio = 'IMAGEM'
                 AND rc.dt_resultado_imagem > rc.dt_prescricao THEN
                rc.dt_resultado_imagem
            WHEN er.dt_resultado_er > rc.dt_prescricao     THEN
                er.dt_resultado_er
            WHEN rc.dt_resultado_imagem > rc.dt_prescricao THEN
                rc.dt_resultado_imagem
        END                                                      AS dt_resultado_real,
        to_char(
            CASE
                WHEN
                    rc.cd_dominio = 'IMAGEM'
                    AND rc.dt_resultado_imagem > rc.dt_prescricao
                THEN
                    rc.dt_resultado_imagem
                WHEN er.dt_resultado_er > rc.dt_prescricao THEN
                    er.dt_resultado_er
                WHEN rc.dt_resultado_imagem > rc.dt_prescricao THEN
                    rc.dt_resultado_imagem
            END, 'dd/mm/yyyy hh24:mi:ss')                               AS dt_resultado_fmt,
        CASE
            WHEN rc.dt_coleta_data > rc.dt_prescricao THEN
                rc.dt_coleta_data
        END                                                      AS dt_coleta_real,
        CASE
            WHEN rc.cd_dominio = 'IMAGEM'
                 AND rc.dt_resultado_imagem > rc.dt_prescricao THEN
                rc.dt_resultado_imagem
            WHEN er.dt_resultado_er > rc.dt_prescricao     THEN
                er.dt_resultado_er
            WHEN rc.dt_resultado_imagem > rc.dt_prescricao THEN
                rc.dt_resultado_imagem
            WHEN rc.dt_coleta_data > rc.dt_prescricao      THEN
                rc.dt_coleta_data
        END                                                      AS dt_evento_final,
        to_char(
            CASE
                WHEN
                    rc.cd_dominio = 'IMAGEM'
                    AND rc.dt_resultado_imagem > rc.dt_prescricao
                THEN
                    rc.dt_resultado_imagem
                WHEN er.dt_resultado_er > rc.dt_prescricao THEN
                    er.dt_resultado_er
                WHEN rc.dt_resultado_imagem > rc.dt_prescricao THEN
                    rc.dt_resultado_imagem
                WHEN rc.dt_coleta_data > rc.dt_prescricao THEN
                    rc.dt_coleta_data
            END, 'dd/mm/yyyy hh24:mi:ss')                               AS dt_evento_final_fmt,
        CASE
            WHEN rc.cd_dominio = 'IMAGEM'
                 AND rc.dt_resultado_imagem > rc.dt_prescricao THEN
                ( ( rc.dt_resultado_imagem - rc.dt_prescricao ) * 24 )
            WHEN er.dt_resultado_er > rc.dt_prescricao     THEN
                ( ( er.dt_resultado_er - rc.dt_prescricao ) * 24 )
            WHEN rc.dt_resultado_imagem > rc.dt_prescricao THEN
                ( ( rc.dt_resultado_imagem - rc.dt_prescricao ) * 24 )
        END                                                      AS tat_resultado_horas,
        CASE
            WHEN rc.dt_coleta_data > rc.dt_prescricao THEN
                ( ( rc.dt_coleta_data - rc.dt_prescricao ) * 24 )
        END                                                      AS tat_coleta_horas,
        CASE
            WHEN rc.cd_dominio = 'IMAGEM'
                 AND rc.dt_resultado_imagem > rc.dt_prescricao THEN
                ( ( rc.dt_resultado_imagem - rc.dt_prescricao ) * 24 )
            WHEN er.dt_resultado_er > rc.dt_prescricao     THEN
                ( ( er.dt_resultado_er - rc.dt_prescricao ) * 24 )
            WHEN rc.dt_resultado_imagem > rc.dt_prescricao THEN
                ( ( rc.dt_resultado_imagem - rc.dt_prescricao ) * 24 )
            WHEN rc.dt_coleta_data > rc.dt_prescricao      THEN
                ( ( rc.dt_coleta_data - rc.dt_prescricao ) * 24 )
        END                                                      AS tat_horas,
        CASE
            WHEN rc.cd_dominio = 'IMAGEM'
                 AND rc.dt_resultado_imagem > rc.dt_prescricao THEN
                'RESULTADO_IMAGEM_LAUDO'
            WHEN er.dt_resultado_er > rc.dt_prescricao     THEN
                'RESULTADO_REAL_ER'
            WHEN rc.dt_resultado_imagem > rc.dt_prescricao THEN
                'RESULTADO_IMAGEM_LAUDO_FALLBACK'
            WHEN rc.dt_coleta_data > rc.dt_prescricao      THEN
                'FALLBACK_COLETA'
            ELSE
                'SEM_EVENTO_FINAL_VALIDO'
        END                                                      AS origem_evento_tat,
        CASE
            WHEN rc.cd_dominio = 'IMAGEM'
                 AND rc.dt_resultado_imagem > rc.dt_prescricao THEN
                'N'
            WHEN er.dt_resultado_er > rc.dt_prescricao     THEN
                'N'
            WHEN rc.dt_resultado_imagem > rc.dt_prescricao THEN
                'N'
            ELSE
                'S'
        END                                                      AS fl_sem_data_resultado_real
    FROM
        resultado_consolidado          rc
        LEFT JOIN resultado_exame_por_prescricao er ON er.nr_prescricao = rc.nr_prescricao
)
SELECT
    to_char(rf.nr_prescricao)             AS nr_prescricao,
    to_char(rf.cd_protocolo)              AS cd_protocolo,
    to_char(rf.nr_seq_protocolo)          AS nr_seq_protocolo,
    to_char(rf.cd_estabelecimento)        AS cd_estabelecimento,
    to_char(rf.nr_atendimento)            AS nr_atendimento,
    to_char(rf.cd_medico)                 AS cd_medico,
    rf.dt_prescricao,
    rf.dt_liberacao,
    rf.dt_liberacao_medico,
    rf.ie_recem_nato,
    rf.dt_entrada,
    to_char(rf.cd_setor_paciente)         AS cd_setor_paciente,
    rf.nm_paciente,
    rf.nm_paciente_sem_acento,
    rf.dt_nascimento,
    rf.dt_mestruacao,
    rf.ie_sexo,
    rf.qt_peso,
    rf.nm_pessoa_responsavel,
    to_char(rf.nr_cpf_resp)               AS nr_cpf_resp,
    to_char(rf.nr_cpf)                    AS nr_cpf,
    to_char(rf.nr_telefone_resp)          AS nr_telefone_resp,
    to_char(rf.nr_prontuario)             AS nr_prontuario,
    to_char(rf.cd_procedencia)            AS cd_procedencia,
    rf.ds_senha,
    rf.nm_medico,
    to_char(rf.nr_cpf_medico)             AS nr_cpf_medico,
    to_char(rf.nr_crm)                    AS nr_crm,
    rf.uf_crm,
    to_char(rf.cd_convenio)               AS cd_convenio,
    rf.qt_altura_cm,
    to_char(rf.cd_categoria)              AS cd_categoria,
    rf.qt_dose,
    rf.dt_ultima_dose,
    to_char(rf.cd_usuario_convenio)       AS cd_usuario_convenio,
    rf.dt_validade_carteira,
    to_char(rf.nr_doc_convenio)           AS nr_doc_convenio,
    rf.ie_tipo_guia,
    rf.ds_convenio,
    to_char(rf.cd_cgc_conv)               AS cd_cgc_conv,
    to_char(rf.cd_regional_conv)          AS cd_regional_conv,
    rf.ds_endereco,
    to_char(rf.nr_endereco)               AS nr_endereco,
    rf.ds_complemento,
    rf.ds_bairro,
    rf.ds_municipio,
    rf.sg_estado,
    to_char(rf.nr_telefone)               AS nr_telefone,
    to_char(rf.cd_cep)                    AS cd_cep,
    rf.ds_setor_paciente,
    to_char(rf.cd_unidade)                AS cd_unidade,
    to_char(rf.cd_estabelecimento_filtro) AS cd_estabelecimento_filtro,
    rf.ds_medicamento_uso,
    rf.nm_mae,
    rf.ie_tipo_atendimento,
    rf.cor_pele,
    rf.nm_social,
    rf.ds_classific_pa,
    to_char(rf.cd_cid)                    AS cd_cid,
    rf.ie_status_execucao,
    rf.cd_dominio,
    rf.dt_resultado,
    rf.dt_resultado_imagem,
    rf.dt_exame_imagem,
    rf.dt_liberacao_imagem,
    rf.dt_aprovacao_imagem,
    rf.dt_coleta_data,
    rf.dt_resultado_er,
    rf.dt_liberacao_er,
    rf.dt_resultado_liberacao_er,
    rf.qt_resultado_er,
    rf.dt_prescricao_fmt,
    rf.dt_resultado_pp_fmt,
    rf.dt_resultado_er_fmt,
    rf.dt_liberacao_er_fmt,
    rf.dt_resultado_liberacao_er_fmt,
    rf.dt_resultado_imagem_fmt,
    rf.dt_exame_imagem_fmt,
    rf.dt_coleta_fmt,
    rf.dt_resultado_real,
    rf.dt_resultado_fmt,
    rf.dt_coleta_real,
    rf.dt_evento_final,
    rf.dt_evento_final_fmt,
    rf.tat_resultado_horas,
    rf.tat_coleta_horas,
    rf.tat_horas,
    rf.origem_evento_tat,
    rf.fl_sem_data_resultado_real,
    CASE
        WHEN rf.origem_evento_tat = 'FALLBACK_COLETA' THEN
            'S'
        ELSE
            'N'
    END                                   AS fl_usou_fallback_coleta,
    CASE
        WHEN rf.tat_horas IS NOT NULL THEN
            round(rf.tat_horas, 1)
        ELSE
            NULL
    END                                   AS tat_horas_arred,
    CASE
        WHEN rf.tat_horas IS NOT NULL THEN
            round(rf.tat_horas / 24, 1)
        ELSE
            NULL
    END                                   AS tat_day_arred
FROM
    resultado_final rf
ORDER BY
    rf.nr_prescricao
"""


def normalize_pk(pk):
    if pk is None:
        return []
    if isinstance(pk, str):
        return [pk]
    return list(pk)


def aplica_schema(df, schema):
    source_types = {
        field.name: field.dataType.simpleString().lower()
        for field in df.schema.fields
    }

    cols = []
    for col_name, col_type in schema:
        source_type = source_types.get(col_name, "")
        col_ref = F.col(col_name)

        if col_type.lower() == "date" and "string" in source_type:
            parsed_date = F.coalesce(
                F.to_date(F.try_to_timestamp(col_ref, F.lit("dd/MM/yyyy HH:mm:ss"))),
                F.to_date(F.try_to_timestamp(col_ref, F.lit("dd/MM/yyyy"))),
                F.to_date(F.try_to_timestamp(col_ref, F.lit("yyyy-MM-dd HH:mm:ss"))),
                F.to_date(F.try_to_timestamp(col_ref, F.lit("yyyy-MM-dd"))),
            )
            cols.append(parsed_date.alias(col_name))
            continue

        cols.append(col_ref.cast(col_type).alias(col_name))

    return df.select(cols)


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
