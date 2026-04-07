SELECT
    (SELECT
        (prestacoes_investimentos +
         (aluguel_iptu_total * percentual_empresa_estudo/100) +
         ((quantidade_pessoas * salario_medio) / (encargos_trabalhistas_pct/100) * (1 + beneficios_pct/100) * (1 + outros_custos_fixos_pct/100)) +
         manutencoes_mensais +
         servicos_terceirizados_mensal)
     FROM appoee_parametrofinanceiro)
    +
    (SELECT sum(valor_reposicao) * (SELECT (depreciacao_mensal/100)/12 FROM oee_bd.appoee_parametrofinanceiro)
     FROM oee_bd.appoee_maquinafinancas
     WHERE maquina_id <> 12 AND maquina_id <> 7)
    +
    (SELECT valor_reposicao * (SELECT ((depreciacao_mensal/100)/12) * 0.10 FROM oee_bd.appoee_parametrofinanceiro)
     FROM oee_bd.appoee_maquinafinancas
     WHERE maquina_id = 7)
AS tot_custo_fixo_final;
