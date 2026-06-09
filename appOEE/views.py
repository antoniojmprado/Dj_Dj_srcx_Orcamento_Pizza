from appOrcam.models import EncargosTrabalhistas

from .models import Waterfall
import json
from django.utils import timezone
from .models import MaquinaFinancas, ParametroFinanceiro, Ocorrencia
from django.db.models import Sum
from django.db import connection, models
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import connection, transaction
# Importação direta para evitar erro no VS Code
from django.db.models import Sum, Avg

# Importe os seus Models e Forms aqui
# Se este arquivo for o views.py, os modelos devem vir de .models
from .models import Maquina, Ocorrencia, Waterfall, MaquinaFinancas
from appOEE.forms import OcorrenciaForm

from django.db import migrations
from decimal import Decimal
from collections import defaultdict


# ================================================================================
# RECOMENDACAO GEMINI
# Para reorganizar o seu views.py e eliminar de vez o erro de Import Circular e
# os avisos do VS Code, a regra de ouro é: nunca importe modelos do próprio
# arquivo onde eles estão sendo definidos e agrupe os imports por categoria.
# ================================================================================

# =========================
# HOME - PÁGINA INICIAL
# =========================
def home(request):
    return render(request, 'home.html')


# ========================================================================================
# APRESENTAÇÃO - PÁGINAS DE PARALISAÇÕES - ROCE - PREJUÍZOS FINANCEIROS - GRAFICOS DE OEE
# ========================================================================================
def apresentacao(request):
    return render(request, 'apresentacao.html')


def resumo_paralisacoes(request):
    return render(request, 'resumo_paralisacoes.html')


def detalhe_paralisacoes(request):
    return render(request, 'detalhe_paralisacoes.html')

# =============================
# TOTAL DE DIAS  CADASTRADOS
# =============================


def total_dias_horasParadas(request):
    sql = """
        SELECT
         COUNT(DISTINCT DATE_FORMAT(appOEE_ocorrencia.data_inicio, '%Y-%m-%d')) AS tot_dias,
         round(sum(tempo_parado/3600000000),0) as total_parado
         FROM appOEE_ocorrencia;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        r = cursor.fetchone()

    return JsonResponse({
        "tot_dias": float(r[0]),
        "total_parado": float(r[1])
    })

# =========================
# CADASTROS
# =========================


def cadastra_ocorrencia(request):
    if request.method == 'POST':
        form = OcorrenciaForm(request.POST)
        if form.is_valid():
            ocorrencia = form.save()
            return redirect('detalhe_ocorrencia', pk=ocorrencia.pk)
    else:
        form = OcorrenciaForm()
    return render(request, 'entrada_dados.html', {'form': form})


def detalhe_ocorrencia(request, pk):
    ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
    return render(request, 'detalhe_ocorrencia.html', {'ocorrencia': ocorrencia})

# =========================
# LISTA DE PARALISAÇÕES
# =========================


def listar_paralis(request):
    sql = """
        SELECT
            oc.id,
            DATE_FORMAT(oc.data_inicio, "%d/%m/%Y %H:%i") AS data_inicio,
            DATE_FORMAT(oc.data_fim, "%d/%m/%Y %H:%i") AS data_fim,
            e.nome AS empresa,
            maq.nome AS maquina,
            m.nome AS motivo,
            t.descricao AS tipo_paralis,
            ROUND(oc.tempo_parado / 3600000000, 1) AS paralis_h,
            oc.qualidade,
            oc.disponibilidade
        from appOEE_ocorrencia oc
        JOIN appOEE_empresa e ON oc.empresa_id = e.id
        JOIN appOEE_maquina maq ON oc.maquina_id = maq.id
        JOIN appOEE_motivo m ON oc.motivo_id = m.id
        JOIN appOEE_tipo_parada t ON oc.tipo_parada_id = t.id
        ORDER BY oc.data_inicio DESC
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        cols = [c[0] for c in cursor.description]
        dados = [dict(zip(cols, row)) for row in cursor.fetchall()]
    return render(request, 'lista_paralisacoes.html', {'list_paral': dados})

# =========================
# OEE PARQUE DIÁRIO
# =========================


def oee_parque_diario(request):
    sql = """
        WITH base AS (
            SELECT
                DATE(oc.data_inicio) AS dia,
                SUM(ht.qt_horas_turno * td.qt_turnos_dia) AS horas_planejadas,
                SUM(oc.tempo_parado)/3600000000 AS horas_paradas,
                AVG(oc.qualidade) AS qualidade,
                AVG(oc.disponibilidade) AS performance
            from appOEE_ocorrencia oc
            JOIN appOEE_horas_turno ht ON ht.id = oc.horas_turno_id
            JOIN appOEE_turnos_dia td ON td.id = oc.turnos_dia_id
            GROUP BY DATE(oc.data_inicio)
        )
        SELECT
            dia,
            ROUND(qualidade,0),
            ROUND(performance,0),
            ROUND(CASE WHEN horas_planejadas>0 THEN ((horas_planejadas-horas_paradas)/horas_planejadas*100) ELSE 0 END,0) AS disponibilidade,
            ROUND(CASE WHEN horas_planejadas>0 THEN (qualidade/100)*(performance/100)*((horas_planejadas-horas_paradas)/horas_planejadas*100) ELSE 0 END,0) AS oee
        FROM base
        ORDER BY dia
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    return JsonResponse({
        "dia": [str(r[0]) for r in rows],
        "qualidade": [max(0, float(r[1])) for r in rows],
        "performance": [max(0, float(r[2])) for r in rows],
        "disponibilidade": [max(0, float(r[3])) for r in rows],
        "oee": [max(0, float(r[4])) for r in rows],
    })

# =========================
# OEE PARQUE ACUMULADO
# =========================


def oee_parque_acumulado(request):
    sql = """
      SELECT
            AVG(oc.qualidade),
            AVG(oc.performance),
            AVG(oc.disponibilidade),
            ROUND((AVG(oc.qualidade)/100)*(AVG(oc.performance)/100)*(AVG(oc.disponibilidade)/100)*100,1) AS oee
        from appOEE_ocorrencia oc
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        r = cursor.fetchone()

    return JsonResponse({
        "qualidade": [max(0, float(r[0]))],
        "performance": [max(0, float(r[1]))],
        "disponibilidade": [max(0, float(r[2]))],
        "oee": [r[3]],
    })


# =========================
# OEE PARQUE ACUMULADO
# =========================

def oee_global_duponthtml(request):
    sql = """
      SELECT * from view_oee_parque_dupont
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        r = cursor.fetchone()
    return JsonResponse({
        "qualidade": [max(0, float(r[0]))],
        "performance": [max(0, float(r[1]))],
        "disponibilidade": [max(0, float(r[2]))],
        "oee": [max(0, float(r[3]))],
    })


# =========================
# OEE POR MÁQUINA
# =========================

def oee_por_maquina(request):
    maquina_id = request.GET.get("maquina")

    sql_diario = """
        WITH base_diaria AS (
           SELECT
                DATE(oc.data_inicio) AS dia,
                AVG(oc.qualidade) AS qualidade,
                AVG(oc.performance) AS performance,
                AVG(oc.disponibilidade) AS disponibilidade
            from appOEE_ocorrencia oc
            JOIN appOEE_horas_turno ht ON ht.id = oc.horas_turno_id
            JOIN appOEE_turnos_dia td ON td.id = oc.turnos_dia_id
            WHERE oc.maquina_id=%s
            GROUP BY DATE(oc.data_inicio)
        )
        SELECT
            dia,
            ROUND(qualidade,0),
            ROUND(performance,0),
            ROUND(disponibilidade,0),
            ROUND((qualidade/100)*(performance/100)*(disponibilidade/100)*100,0)  AS oee
        FROM base_diaria
        ORDER BY dia ASC;
    """
    sql_acumulado = """
        WITH base_diaria AS (
            SELECT
                maq.id AS maquinaId,
                maq.nome AS maquina,
                AVG(oc.disponibilidade) AS disponibilidade,
                AVG(oc.qualidade) AS qualidade,
                AVG(oc.performance) AS performance

            from appOEE_ocorrencia oc
            JOIN appOEE_maquina maq ON maq.id = oc.maquina_id
            JOIN appOEE_horas_turno ht ON ht.id = oc.horas_turno_id
            JOIN appOEE_turnos_dia td ON td.id = oc.turnos_dia_id
           # GROUP BY maq.id, maq.nome
            WHERE oc.maquina_id = %s
        )
        SELECT
            maquina,
            maquinaId,
            ROUND(qualidade) AS qualidade,
            ROUND(performance) AS performance,
            ROUND(disponibilidade) AS disponibilidade,

            ROUND((qualidade/100)*(performance/100)*(disponibilidade/100)*100,1) AS oee
        FROM base_diaria;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_diario, [maquina_id])
        diario = cursor.fetchall()
        cursor.execute(sql_acumulado, [maquina_id])
        acum = cursor.fetchone()
    return JsonResponse({
        "dia": [str(r[0]) for r in diario],
        "qualidade": [r[1] for r in diario],
        "performance": [r[2] for r in diario],
        "disponibilidade":  [r[3] for r in diario],
        "oee": [r[4] for r in diario],
        "maquina": acum[0],
        "qualidade_acum": acum[2],
        "performance_acum": acum[3],
        "disponibilidade_acum": acum[4],
        "oee_acum": acum[5],
    })


# =========================
# OEE ACUMULADO POR MÁQUINA (TABELA)
# =========================

def oee_acum_maquina(request):
    sql = """
        DROP TABLE IF EXISTS appOEE_oee_acum_maquina;

        CREATE TABLE appOEE_oee_acum_maquina AS
        WITH base_diaria AS (
            SELECT
                maq.id AS maquinaId,
                maq.nome AS maquina,
                AVG(oc.disponibilidade) AS disponibilidade,
                AVG(oc.qualidade) AS qualidade,
                AVG(oc.performance) AS performance
            from appOEE_ocorrencia oc
            JOIN appOEE_maquina maq ON maq.id = oc.maquina_id
            JOIN appOEE_horas_turno ht ON ht.id = oc.horas_turno_id
            JOIN appOEE_turnos_dia td ON td.id = oc.turnos_dia_id
            GROUP BY maq.id, maq.nome
        )
        SELECT
            maquina,
            maquinaId,
            disponibilidade AS disponibilidade,
            qualidade AS qualidade,
            performance AS performance,
            round(((disponibilidade/100)*(qualidade/100)*(performance/100)*100),0) AS oee
        FROM base_diaria;
    """
    with connection.cursor() as cursor:
        for stmt in sql.split(';'):
            if stmt.strip():
                cursor.execute(stmt)
        transaction.commit()
    return JsonResponse({"status": "ok", "mensagem": "Tabela appOEE_oee_acum_maquina recriada com sucesso"})


# =========================
# RANKING OEE
# =========================

def ranking_oee(request):
    sql = """
        SELECT
            m.nome as maquina,
           --
			round(((avg(disponibilidade)/100) * (avg(performance)/100) * (avg(qualidade)/100))*100,0) as oee_acum
			--
        from appOEE_ocorrencia oc
        JOIN appOEE_maquina m ON m.id = oc.maquina_id
        GROUP BY maquina
        ORDER BY oee_acum DESC
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        dados = cursor.fetchall()
    labels, valores = [], []
    for nome, oee in dados:
        labels.append(nome)
        valores.append(max(0, float(oee or 0)))
    return JsonResponse({"labels": labels, "data": valores})


# =========================
# RELATÓRIO DE OCORRENCIAS
# =========================

def relatorio_ocorrencias(request):
    sql = """
        SELECT
            oc.id,
            date_format(oc.data_inicio, "%d/%m/%Y %H:%i") as data_inicio,
            date_format(oc.data_fim, "%d/%m/%Y %H:%i") as data_fim,
            e.nome as appOEE_empresa,
            maq.nome as maquina,
            m.nome as motivo,
            t.descricao as tipo_parada,
            round(oc.tempo_parado/3600000000,1) as paralis_h,
            oc.qualidade,
            oc.disponibilidade
        FROM appOEE_ocorrencia oc
			INNER JOIN appOEE_empresa e on oc.empresa_id = e.id
            INNER JOIN appOEE_motivo m on oc.motivo_id = m.id
            INNER JOIN appOEE_maquina maq on oc.maquina_id = maq.id
            INNER JOIN appOEE_tipo_parada t on oc.tipo_parada_id = t.id
        ORDER BY oc.data_inicio DESC
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

        cols = [col[0] for col in cursor.description]

        list_ocorrencias = []
        for row in rows:
            r = dict(zip(cols, row))

            list_ocorrencias.append(r)

    context = {
        'list_ocorrencias': list_ocorrencias
    }

    return render(request, 'lista_paralisacoes.html', context)


# ====================================================================
# VIEWs PARA Pagina - Paralisacoes da Producao em lista_paralisacoes.html
# ====================================================================

def paradas_maquina(request):
    sql = """
           SELECT nome,
            ROUND((sum(paradas)),0) as tot_parado
            FROM view_distrib_paradas
            GROUP BY nome
            ORDER BY tot_parado DESC
        """
    with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

    maquina, tempo = [], []
    for nome, hora in rows:
        maquina.append(nome)
        tempo.append(max(0, float(hora or 0)))

    return JsonResponse({"maquina": maquina, "tempo": tempo})


def tipo_parada(request):
        sql = """
                SELECT
                    descricao as tipo_parada,
                    ROUND(sum(paradas),0) as tot_parado
                    FROM view_distrib_paradas
                    GROUP BY tipo_parada
                    ORDER BY tot_parado DESC
                """
        with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()

        tipo, tempo = [], []
        for nome, hora in rows:
            tipo.append(nome)
            tempo.append(max(0, float(hora or 0)))

        return JsonResponse({"tipo": tipo, "tempo": tempo})


def motivo_parada(request):
        sql = """
            SELECT  motivo_nome as motivo,
                    ROUND((sum(paradas)),0) as tot_parado
                    FROM view_distrib_paradas
                    GROUP BY motivo
                    ORDER BY tot_parado DESC
            """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

        motivo, tempo = [], []
        for nome, hora in rows:
            motivo.append(nome)
            tempo.append(max(0, float(hora or 0)))

        return JsonResponse({"motivo": motivo, "tempo": tempo})


def oee_maquina(request):
    sql_oee_par = """
           SELECT nome,
                round(avg(oee),0) as oee
                FROM view_distrib_paradas
                GROUP BY nome
                ORDER BY oee DESC
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_oee_par)
        rows = cursor.fetchall()

    maquina, oee = [], []
    for nome, hora in rows:
        maquina.append(nome)
        oee.append(max(0, float(hora or 0)))

    return JsonResponse({"maquina": maquina, "oee": oee})


# =========================
# PREJUÍZOS FINANCEIROS
# =========================

def prejuizos_financeiros(request):
    with connection.cursor() as cursor:
        # Busca o prejuízo total acumulado
        cursor.execute(
            """
                SELECT * FROM view_tempo_prejuizo_total;
                """)
        total_prejuizo = cursor.fetchone()

        # Busca o prejuízo detalhado por máquina para o gráfico
        cursor.execute("SELECT * FROM view_prejuizo_quali_perform;")
        rows = cursor.fetchall()

        cols = [c[0] for c in cursor.description]

        list_preju = []
        for row in rows:
            r = dict(zip(cols, row))

            list_preju.append(r)

    return JsonResponse({'total_prejuizo': total_prejuizo, "list_preju": list_preju})


def prejuizos_custos_maquina(request):
    with connection.cursor() as cursor:
        # Busca o prejuízo total acumulado
        cursor.execute(
            """
        select 
                maquinaId AS maquinaId,
                maquina AS maq_nome, 
                custo_minuto,
                round(sum(prejuizo_perda_tempo +prejuizo_perda_performance + prejuizo_perda_qualidade), 2) AS preju_maq
            from view_prejuizo_quali_perform
            group by maquinaId, maq_nome
            order by preju_maq desc
                """)
        rows = cursor.fetchall()

        maquinaId, maq_nome, custo_minuto, preju_maq = [], [], [], []

        for a, b, c, d in rows:
            maquinaId.append(a)
            maq_nome.append(b)
            custo_minuto.append(c)
            preju_maq.append(d)

        return JsonResponse({
            "maq_nome": maq_nome,
            "custo_minuto": custo_minuto,
        })


def prejuizos_maquina(request):
    with connection.cursor() as cursor:
        # Busca o prejuízo total acumulado
        cursor.execute(
            """
        select 
                maquinaId AS maquinaId,
                maquina AS maq_nome, 
                custo_minuto,
                round(sum(prejuizo_perda_tempo +prejuizo_perda_performance + prejuizo_perda_qualidade), 2) AS preju_maq
            from view_prejuizo_quali_perform
            group by maquinaId, maq_nome
            order by preju_maq desc
                """)
        rows = cursor.fetchall()

        maquinaId, maq_nome, custo_minuto, preju_maq = [], [], [], []

        for a, b, c, d in rows:
            maquinaId.append(a)
            maq_nome.append(b)
            custo_minuto.append(c)
            preju_maq.append(d)

        return JsonResponse({
            "maq_nome": maq_nome,
            "preju_maq": preju_maq,
        })


###############################################
# DASHBOARD ROCE
###############################################
def dashboard_roce(request):
    # 1. BUSCA PARÂMETROS FINANCEIROS (Configurados no Admin)
    params = ParametroFinanceiro.objects.last()
    
    if not params:
        faturamento_alvo = 4472000.00
        custo_fixo_operacional = 73333.33
        aluguel_proporcional = 84000.00
        prolabore_socio = 0.0
        percentual_empresa_estudo = 0.0
        depreciacao_mensal = 0.0
        manutencoes_mensais = 0.0
        servicos_terceirizados_mensal = 0.0
        preco_unitario = 0.0
        quantidade_vendida = 0.0
        faturamento_grupo = 0.0
    else:
        preco_unitario = float(params.preco_unitario)
        quantidade_vendida = float(params.quantidade_vendida)
        faturamento_grupo = float(params.faturamento_grupo)

        percentual_empresa_estudo = float(params.percentual_empresa_estudo) / 100
        faturamento_alvo = float(params.faturamento_grupo) * (float(params.percentual_empresa_estudo) / 100)
        
        # enc_pct = EncargosTrabalhistas.objects.filter(ativo_no_calculo=True).aggregate(total=Sum('aliquota'))
        # encargos_trabalhistas_pct = enc_pct['total'] or Decimal('0.00')
        
        with connection.cursor() as cursor:
            cursor.execute(
            """
                SELECT sum(aliquota) as aliq 
                FROM appOrcam_encargostrabalhistas 
                where ativo_no_calculo = 1;
                            """)
            
            encargos_trabalhistas = cursor.fetchone()
            encargos_trabalhistas_pct = float(encargos_trabalhistas[0]) if encargos_trabalhistas and encargos_trabalhistas[0] is not None else 0.0

        custo_pessoal_base = params.quantidade_pessoas * float(params.salario_medio)
        encargos = 1 + (encargos_trabalhistas_pct / 100)
        beneficios = 1 + (float(params.beneficios_pct) / 100)
        
        outros = float(params.outros_custos_fixos_pct) / 100
                
        manutencoes_mensais = float(params.manutencoes_mensais)                                             
        servicos_terceirizados_mensal = float(params.servicos_terceirizados_mensal)
        
        prestacoes_investimentos = float(params.prestacoes_investimentos) 

        aluguel_proporcional = float(params.aluguel_iptu_total) * (float(params.percentual_empresa_estudo) / 100) 
         
        custo_folha = (custo_pessoal_base * encargos * beneficios)      
        prolabore_socio = (float(params.retirada_socio_pct)/100) * float(params.faturamento_grupo) * (float(params.percentual_empresa_estudo) / 100)

    # 1A. Cálculo da depreciação antiga (Que não quebrava o Python)
    with connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT 
                (SELECT SUM(valor_reposicao) as total_de_ativos FROM appOEE_maquinafinancas) *
                (SELECT depreciacao_mensal/100/12 FROM appOEE_parametrofinanceiro) AS
                tot_depreciacao;
                            """)
        tot_depreciacao = cursor.fetchone()
        tot_depreciacao_mensal = float(tot_depreciacao[0]) if tot_depreciacao and tot_depreciacao[0] is not None else 0.0

    custo_fixo_mensal_parcial = prestacoes_investimentos + aluguel_proporcional + custo_folha + \
        manutencoes_mensais + servicos_terceirizados_mensal + tot_depreciacao_mensal
        
    outros_custos_fixos_mensal = custo_fixo_mensal_parcial * outros
    
    total_custo_fixo_mensal = custo_fixo_mensal_parcial + outros_custos_fixos_mensal
    
    print(f'custo_pessoal_base: {custo_pessoal_base}', flush=True)
    print(f'custo_fixo_mensal_parcial: {custo_fixo_mensal_parcial}', flush=True)
    print(f'outros_custos_fixos_mensal: {outros_custos_fixos_mensal}', flush=True)
    print(f'total_custo_fixo_mensal: {total_custo_fixo_mensal}', flush=True)

    # 2. BUSCA CAPITAL INVESTIDO
    res_invest = MaquinaFinancas.objects.aggregate(total=Sum('valor_reposicao'))['total']
    investimento_total = float(res_invest) if res_invest else 1.0

    # 3. BUSCA OEE E PREJUÍZO DE OCIOSIDADE
    with connection.cursor() as cursor:
        cursor.execute(
            """
                select 
                    sum(prejuizo_total_oee) as prejuizo_total_oee,
                    sum(tempo_parado_min)/60 as totHoras_parado
                from
                (
                select 
                    maquina,
                    tempo_parado_min,
                    prejuizo_perda_tempo,
                    prejuizo_perda_performance,
                    prejuizo_perda_qualidade,
                    prejuizo_perda_tempo + prejuizo_perda_performance + prejuizo_perda_qualidade as prejuizo_total_oee
                from view_prejuizo_quali_perform) as x
            """)
        res_prejuizo = cursor.fetchone()
        prejuizo_ociosidade = float(res_prejuizo[0]) if res_prejuizo and res_prejuizo[0] is not None else 0.0
        hr_paralis = float(res_prejuizo[1]) if res_prejuizo and res_prejuizo[1] is not None else 0.0

        cursor.execute("""
            SELECT
                    ROUND((AVG(oc.qualidade)/100)*(AVG(oc.performance)/100)*
                    (AVG(oc.disponibilidade)/100)*100,1) AS oee from appOEE_ocorrencia oc
                       """)
        res_oee = cursor.fetchone()
        oee_medio_atual = float(res_oee[0]) if res_oee and res_oee[0] is not None else 0.0

        cursor.execute("""
            select 
                maquina,
                custo_minuto as custominuto,
                (custo_minuto * 60) as custohora,
                tempo_parado_min/60 as tempo_parado_horas,
                prejuizo_perda_tempo as pertemp,
                prejuizo_perda_performance as perpef,
                prejuizo_perda_qualidade as perqual,
                prejuizo_perda_tempo + prejuizo_perda_performance + prejuizo_perda_qualidade as preju_tot
            from view_prejuizo_quali_perform
            order by preju_tot desc
        """)
        dados_maquinas = cursor.fetchall()

        cursor.execute("""
                select 
                    concat("R$ ",FORMAT( totcustomin, 2,"de_DE" )) as totcustomin,                    
                    concat("R$ ",FORMAT((preju/NULLIF(tm, 0))*60, 2,"de_DE" )) as totcustohora,
                    concat(round(tm/60,0), " h") as tempo,                   
                    concat("R$ ", FORMAT( pt, 2,"de_DE" )) as pertemp,
                    concat("R$ ", FORMAT( pf, 2,"de_DE" )) as perperf,
                    concat("R$ ", FORMAT( pq, 2,"de_DE" )) as perqual,                    
                    concat("R$ ", FORMAT( preju, 2,"de_DE" )) as preju_tot
                    from
                    (
                    select
                          sum(custo_minuto) as totcustomin,
                          sum(tempo_parado_min) as tm,
                          sum(prejuizo_perda_tempo) as pt,
                          sum(prejuizo_perda_performance) as pf,
                          sum(prejuizo_perda_qualidade) as pq,
                          SUM(prejuizo_perda_tempo + prejuizo_perda_performance + prejuizo_perda_qualidade) as preju
                    from view_prejuizo_quali_perform
                    ) as x           
                """)
        preju_total = cursor.fetchone()

    # 3A. ATUALIZAÇÃO TRANSACIONAL DOS CUSTOS
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE appOEE_maquinafinancas
                JOIN (
                    SELECT 
                        base.maquina_id,
                        ROUND(base.horas_mes_calc, 2) AS horas_mes,
                        ROUND(base.minutos_mes_calc, 2) AS minutos_mes,
                        ROUND((%s * base.part_maq_ativos) / NULLIF(base.minutos_mes_calc, 0), 4) AS custo_minuto,
                        ROUND(base.part_maq_ativos * 100, 4) AS perc_ativo
                        FROM (
                            SELECT 
                                m.maquina_id,
                                (m.horas_turno * m.turnos_dia * m.dias_sem * m.sem_mes) AS horas_mes_calc,
                                (m.horas_turno * m.turnos_dia * m.dias_sem * m.sem_mes) * 60 AS minutos_mes_calc,
                                CAST(m.valor_reposicao AS DECIMAL(18,6)) / NULLIF(t.total_valor, 0) AS part_maq_ativos
                            FROM appOEE_maquinafinancas m
                            CROSS JOIN (
                                SELECT CAST(SUM(valor_reposicao) AS DECIMAL(18,6)) AS total_valor
                                FROM appOEE_maquinafinancas
                            ) t
                    ) base
                ) calc ON appOEE_maquinafinancas.maquina_id = calc.maquina_id
                SET
                    appOEE_maquinafinancas.horas_mes = calc.horas_mes,
                    appOEE_maquinafinancas.minutos_mes = calc.minutos_mes,
                    appOEE_maquinafinancas.custo_minuto = calc.custo_minuto,
                    appOEE_maquinafinancas.perc_ativo = calc.perc_ativo
            """, [total_custo_fixo_mensal])

            cursor.execute("""
                SELECT avg(minutos_mes) as minutos_mes FROM appOEE_maquinafinancas
                """)
            resultado = cursor.fetchone()
            minutos_mes = resultado[0] if resultado else 0.0

    # 4. CÁLCULO DO RESULTADO (DRE SIMPLIFICADA)
    oee_medio_atual = oee_medio_atual / 100.0
    faturamento_real = float(params.faturamento_grupo) * (float(params.percentual_empresa_estudo) / 100)
    oee_medio_atual = oee_medio_atual * 100

    faturamento_potencial = faturamento_real / (oee_medio_atual/100) if oee_medio_atual > 0 else faturamento_real
    prolabore_socio = float(params.faturamento_grupo) * (float(params.percentual_empresa_estudo) / 100) * (float(params.retirada_socio_pct) / 100)
    custos_variaveis = faturamento_real * float(params.custo_variav_fatur_real_pct) / 100 + prolabore_socio

    total_custo_mensal = custos_variaveis + total_custo_fixo_mensal
    lucro_operacional = faturamento_real - total_custo_mensal

    # 5. PREPARAÇÃO DA LÓGICA DO GRÁFICO (Caminho da Cascata)
    ponto_pos_cv = faturamento_real - custos_variaveis
    ponto_pos_cf = ponto_pos_cv - total_custo_fixo_mensal

    # Força os valores estáticos de ineficiência para o Waterfall não quebrar a DRE
    p_disp, p_perf, p_qual = 0.0, 0.0, 0.0

    ponto_pos_disp = ponto_pos_cf - p_disp
    ponto_pos_perf = ponto_pos_disp - p_perf
    ponto_final = ponto_pos_perf - p_qual

    # 6. MONTAGEM DOS ARRAYS PARA O TEMPLATE
    data_waterfall = [
        [0, faturamento_alvo], [faturamento_alvo, faturamento_real], [0, faturamento_real],
        [faturamento_real, ponto_pos_cv], [ponto_pos_cv, ponto_pos_cf], [0, ponto_pos_cf],
        [ponto_pos_cf, ponto_pos_disp], [ponto_pos_disp, ponto_pos_perf], [ponto_pos_perf, ponto_final],
        [0, ponto_final]
    ]

    labels_waterfall = [
        "Fat. Bruto", "Perda OEE", "Fat. Real", "Custo Var.",
        "Custo Fixo", "EBIT (Contábil)", "P. Disponib.",
        "P. Perform.", "P. Qualidade", "Impacto Econ."
    ]

    cores_waterfall = [
        '#2c3e50', '#e74c3c99', '#34495e', '#c0392b',
        '#c0392b', '#8e44ad', '#d3540099', '#d3540099',
        '#d3540099', '#000000'
    ]

    # 7. INDICADORES FINAIS (DUPONT)
    margem_operacional = (lucro_operacional / faturamento_real * 100) if faturamento_real > 0 else 0
    giro_do_ativo = faturamento_real / investimento_total
    roce = (lucro_operacional / investimento_total * 100)

    # 8. LISTA PARA WATERFALL
    dados = {
        'fat_bruto': faturamento_potencial, 'perda_oee': faturamento_potencial - faturamento_real,
        'fat_real': faturamento_real, 'cust_var': custos_variaveis, 'cust_fixo': total_custo_fixo_mensal,
        'res_contab': ponto_pos_cf, 'perda_disp': p_disp, 'perda_perf': p_perf, 'perda_quali': p_qual,
        'cust_inefic': prejuizo_ociosidade, 'res_econom': ponto_final, 'oee_atual': oee_medio_atual,
        'socio': prolabore_socio, 'ativos': investimento_total, 'hr_paralis': hr_paralis, 'minutos_mes': minutos_mes
    }

    Waterfall.objects.update_or_create(id=1, defaults=dados)

    context = {
        'faturamento_potencial': faturamento_potencial, 'faturamento_com_oee': faturamento_real,
        'custos_variaveis': custos_variaveis, 'custo_fixo': total_custo_fixo_mensal,
        'total_custo_mensal': total_custo_mensal, 'prejuizo_ociosidade': prejuizo_ociosidade,
        'oee_atual': oee_medio_atual, 'lucro_operacional': lucro_operacional,
        'data_waterfall': data_waterfall, 'labels_waterfall': labels_waterfall, 'cores_waterfall': cores_waterfall,
        'roce': roce, 'margem': margem_operacional, 'giro': giro_do_ativo, 'dados_maquinas': dados_maquinas,
        'data_atual': timezone.now(), 'preju_total': preju_total, 'investimento_total': investimento_total,
        'tot_depreciacao_mensal': tot_depreciacao_mensal, 'preco_unitario': preco_unitario,
        'quantidade_vendida': quantidade_vendida/1000 if quantidade_vendida else 0,
        'faturamento_grupo': faturamento_grupo/1000 if faturamento_grupo else 0,
        'percentual_empresa_estudo': percentual_empresa_estudo*100
    }

    context.update(dados)
    return render(request, 'dupont.html', context)


def detalhes_waterfall(request):  # DADOS PARA GRÁFICO WATERFALL
    config = Waterfall.objects.filter(id=1).first()

    if not config:
        return JsonResponse({'error': 'Dados não encontrados'}, status=404)

    faturamento_real = float(config.fat_real)
    c_var = float(config.cust_var)
    c_fixo = float(config.cust_fixo)

    c_inefic = float(config.cust_inefic)

    # Cálculos corretos
    margem_contrib = faturamento_real - c_var
    res_oper = margem_contrib - c_fixo

    custo_ineficiencia = 0 - c_inefic

    intervalos = [
        [0, faturamento_real],
        # Faturamento
        [faturamento_real, margem_contrib],
        # Custos Variáveis
        # Margem de Contribuição (subtotal)
        [0, margem_contrib],

        [margem_contrib, res_oper],
        # Custos Fixos
        # Resultado Operacional (subtotal)
        [0, res_oper],

        [0, custo_ineficiencia],                  # Ineficiência
    ]

    return JsonResponse({
        'labels': [
            'Faturamento',
            'Custos Variav.',
            'Margem Contrib.',
            'Custos Fixos',
            'Resultado Operac.',
            'Custo_Perdas_OEE',
        ],
        'valores': intervalos,
    })


# =========================
# TEMPO PARADO PARQUE DIARIO 
# =========================

def paradas_parque_diario(request):
    sql = """
        WITH base_diaria AS (
           SELECT
                DATE(oc.data_inicio) AS dia, 
                ROUND(SUM(oc.tempo_parado/3600000000)) as horas_paradas
                from appOEE_ocorrencia oc
            JOIN appOEE_horas_turno ht ON ht.id = oc.horas_turno_id
            JOIN appOEE_turnos_dia td ON td.id = oc.turnos_dia_id
            JOIN appOEE_maquina mq ON mq.id = oc.maquina_id
            #WHERE oc.maquina_id=7
            GROUP BY dia
        )
        SELECT
            dia, horas_paradas
        FROM base_diaria
        ORDER BY dia ASC;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    return JsonResponse({
        "dia": [str(r[0]) for r in rows],
        "horas_paradas": [max(0, float(r[1])) for r in rows],
    })


# ========================================
# TEMPO PARADO POR DIA POR MÁQUINA PARQUE
# ========================================

def paradas_por_dia_maquina(request):
    sql = """
        SELECT
            DATE(oc.data_inicio) AS dia,
            mq.nome,
            ROUND(SUM(oc.tempo_parado)/3600000000) AS horas_paradas
        FROM appOEE_ocorrencia oc
        JOIN appOEE_maquina mq ON mq.id = oc.maquina_id
        GROUP BY dia, nome
        ORDER BY dia ASC
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    # Organizando os dados
    dias = sorted(list(set(str(r[0]) for r in rows)))
    maquinas = sorted(list(set(r[1] for r in rows)))

    # Criar um mapa de dados: { 'NomeMaquina': { 'Data': Valor } }
    dados_map = defaultdict(lambda: defaultdict(float))
    for r in rows:
        dia_str, maq_nome, valor = str(r[0]), r[1], float(r[2])
        dados_map[maq_nome][dia_str] = max(0, valor)

    # Formata para o Chart.js
    datasets = []

    colors = ["rgba(181, 27, 104, 0.5)", "rgba(76, 209, 134, 0.8)", "rgba(255, 238, 0, 0.8)",
              "rgba(200, 99, 71, 0.5)", "rgba(255, 0, 0, 0.5)", "rgba(146, 0, 213, 0.5)"]
              # Suas cores preferidas
              
    
    for i, maq in enumerate(maquinas):
        datasets.append({
        'label': maq,
        'data': [dados_map[maq][d] for d in dias],
        'backgroundColor': colors[i % len(colors)],  # Atribui uma cor da lista
    })

    return JsonResponse({
        "labels": dias,
        "datasets": datasets,
    })

###############################################
# SIMULADOR
###############################################


def simulador(request):
    sql = """
    SELECT 
        fat_bruto, fat_real,cust_var, cust_fixo,
        res_contab, cust_inefic, oee_atual, socio,
        ativos, hr_paralis, minutos_mes
        
    FROM appOEE_waterfall;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        r = cursor.fetchone()

    context = {
        'fat_bruto': float(r[0]),
        'fat_real': float(r[1]),
        'cust_var': float(r[2]),
        'cust_fixo': float(r[3]),
        'res_contab': float(r[4]),
        'cust_inefic': float(r[5]),
        'oee_atual': float(r[6]),
        'socio': float(r[7]),
        'ativos': float(r[8]),
        'hr_paralis': float(r[9]),
        'minutos_mes': float(r[10]),
    }

    return render(request, 'simulador.html', context)

###############################################
# ORCAMENTO
###############################################
