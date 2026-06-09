from .forms import SemanAnoForm
from django.http import HttpResponse
from django.shortcuts import render
from collections import defaultdict
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.db import connection
from appQuali.forms import ReclamacoesForm
from appQuali.forms import SemanAnoForm
from appQuali.models import ReclamacoesArquivo, Reclamacoes
from django.contrib import messages
from datetime import date, timedelta

# def home(request):
#     return render(request, 'home.html')

def home(request):
    return render(request, 'home.html')


def reclam_cliente(request):
    if request.method == "POST":
        form = ReclamacoesForm(request.POST, request.FILES)

        if form.is_valid():
            # salva a reclamação principal
            reclamacao = form.save()
            
            messages.success(request, 'Reclamação cadastrada com sucesso!')
            # return redirect('reclamacao_create')  # ou outra página

            # pega os arquivos (pode vir vazio!)
            arquivos = request.FILES.getlist('arquivos')

            # 🔹 CASO 1: não há anexos
            if not arquivos:
                ReclamacoesArquivo.objects.create(
                    reclamacoes=reclamacao
                )

            # 🔹 CASO 2: há anexos
            else:
                for arquivo in arquivos:
                    ReclamacoesArquivo.objects.create(
                        reclamacoes=reclamacao,
                        itens=arquivo
                    )

            return redirect('reclamacoes_list')

    else:
        form = ReclamacoesForm()

    return render(request, 'adiciona_reclam.html', { 'form': form })


def reclamacoes_list(request):
    sql = """
    SELECT 
        r.id AS reclam_id,
        WEEK(DATE_FORMAT(MAX(SUBSTRING(a.data_upload,1,10)), "%y/%m/%d"),1)  AS sem,
        DATE_FORMAT(MAX(SUBSTRING(a.data_upload,1,10)), "%d/%m/%y")  AS data_ocor,
        e.empresa AS fabricante,
        t.tecnologia AS tecnol,
        r.cliente AS cliente,
        r.vendedora AS vendedor,
        p.produto AS produto,
        d.tipo_defeito AS defeito,
        r.descricao AS descricao,
        r.comentarios AS coment,
        GROUP_CONCAT(a.itens ORDER BY a.itens SEPARATOR ' | ') AS anexos
    FROM qualisrcaixa.reclamacoes r
    LEFT JOIN qualisrcaixa.appquali_reclamacoesarquivo a ON a.reclamacoes_id = r.id
    LEFT JOIN qualisrcaixa.empresa e ON e.id = r.id_empresa
    LEFT JOIN qualisrcaixa.produtos p ON p.id = r.id_produto
    LEFT JOIN qualisrcaixa.tecnologia t ON t.id = r.id_tecnol
    LEFT JOIN qualisrcaixa.tipos_defeitos d ON d.id = r.id_defeito
    GROUP BY 
        r.id,
        e.empresa,
        t.tecnologia,
        r.cliente,
        p.produto,
        d.tipo_defeito,
        r.descricao,
        r.comentarios
    ORDER BY r.id DESC
    """

    with connection.cursor() as cursor:
        # (opcional) aumenta limite do GROUP_CONCAT se houver muitos anexos
        cursor.execute("SET SESSION group_concat_max_len = 1000000;")
        cursor.execute(sql)

        cols = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    lista_recl_sql = []
    for row in rows:
        r = dict(zip(cols, row))

        # transforma string concatenada em lista
        if r['anexos']:
            r['anexos'] = r['anexos'].split(' | ')
        else:
            r['anexos'] = []

        lista_recl_sql.append(r)

    context = {
        'lista_recl_sql': lista_recl_sql
    }

    return render(request, 'listar.html', context)

def defeitosPorMes(request): # CALIBRADO MINÚSCULO PARA LINUX
    sql = """
         SELECT mesAno, sum(tot) as tot , max(dia) AS dias
            FROM (
                SELECT mesAno, tot, dia
                    FROM (
                        SELECT 
                            DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%y/%b") as mesAno, COUNT(distinct a.reclamacoes_id) as tot,
                            DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%y/%m/%d") as dia
                            FROM qualisrcaixa.appquali_reclamacoesarquivo a 
                            LEFT JOIN qualisrcaixa.reclamacoes r ON r.id = a.reclamacoes_id
                            INNER JOIN qualisrcaixa.tipos_defeitos AS d ON d.id = r.id_defeito
                            GROUP BY DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%y/%b"), dia
                        ) AS X
                    ORDER BY mesAno DESC, tot DESC  
                ) AS y
            GROUP BY mesAno
            ORDER BY dias          
        """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

        mesAno = [row[0] for row in rows]
        tot = [row[1] for row in rows]
        dias = [row[2] for row in rows]

        return JsonResponse({
            "mesAno": mesAno,  
            "tot": tot,
            "dias": dias
        })

def defeitosPorTipoMaisFrequentes(request): # CALIBRADO MINÚSCULO PARA LINUX
    sql = """
        SELECT ucase(tipo_defeito) as tipoId, count(DISTINCT a.reclamacoes_id) as tot
            FROM 
            qualisrcaixa.appquali_reclamacoesarquivo a 
            LEFT JOIN qualisrcaixa.reclamacoes r ON r.id = a.reclamacoes_id
            INNER JOIN qualisrcaixa.tipos_defeitos AS d ON d.id = r.id_defeito
            WHERE a.reclamacoes_id >= 69
            GROUP BY d.tipo_defeito
        ORDER BY tot DESC
        LIMIT 7;       
        """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()
        res = {}

        for key, value in row:
            res[key] = value

        tipo_recl = list(res.keys())
        qt_reclamacoes = list(res.values())

    data_json = {'tipo_recl': tipo_recl, 'tot': qt_reclamacoes}
    return JsonResponse(data_json)

def defeitoMesEscolhido(request): # CALIBRADO MINÚSCULO PARA LINUX
    anoMes = request.GET.get('anoMes')
    
    sql = f"""
        SELECT ucase(tipo_defeito) as tipoId, COUNT(distinct a.reclamacoes_id) as tot 
        FROM qualisrcaixa.appquali_reclamacoesarquivo a 
        LEFT JOIN qualisrcaixa.reclamacoes r ON r.id = a.reclamacoes_id 
        INNER JOIN qualisrcaixa.tipos_defeitos AS d ON d.id = r.id_defeito 
        WHERE a.reclamacoes_id >= 69  
          AND DATE_FORMAT(SUBSTRING(a.data_upload,1,10), '%y/%b') = '{anoMes}' 
        GROUP BY d.tipo_defeito 
        ORDER BY tot DESC 
        LIMIT 7
    """            
        
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()
        res = {}

        for key, value in row:
            res[key] = value

        chave_tipoId = list(res.keys())
        qt_tipos = list(res.values())

    data_json = {'chave_tipoId': chave_tipoId, 'qt_tipos': qt_tipos}
    return JsonResponse(data_json)

def defeitosPorSemana(request): # CALIBRADO MINÚSCULO PARA LINUX
    sql = """
    SELECT sem_Ano, sum(totrecl) as quantidade, MAX(dia) AS dias
    FROM(
        SELECT sem_Ano, sum(tot) as totrecl, dia
            FROM(
                SELECT DATE_FORMAT(dia_mes_atual, "%y/%m/%d") as dia, tot,
                CONCAT(WEEK(dia_mes_atual, 1),"_",DATE_FORMAT(dia_mes_atual, "%m"),"/",DATE_FORMAT(dia_mes_atual, "%y")) AS sem_Ano
                    FROM(
                        SELECT dia_mes_atual,  tot
                            FROM(
                                SELECT 
                                    MAX(DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%Y/%m/%d")) as dia_mes_atual, COUNT(distinct a.reclamacoes_id) as tot
                                    FROM qualisrcaixa.appquali_reclamacoesarquivo a 
                                    LEFT JOIN qualisrcaixa.reclamacoes r ON r.id = a.reclamacoes_id
                                    INNER JOIN qualisrcaixa.tipos_defeitos AS d ON d.id = r.id_defeito
                                    WHERE a.reclamacoes_id >= 69 
                                    GROUP BY DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%Y/%m/%d")                
                                ) AS X
                            ORDER BY dia_mes_atual DESC, tot DESC 
                        ) AS Y
                ) AS Z
        GROUP BY sem_Ano, dia
        ) AS T
    GROUP BY sem_Ano
    ORDER BY dias        
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        sem_Ano = [row[0] for row in rows]
        quantidade = [row[1] for row in rows]
        dias = [row[2] for row in rows]

        return JsonResponse({
            "sem_Ano": sem_Ano,
            "quantidade": quantidade,
            "dias": dias            
        })

def selecionaMesAno(request):
    sql = """
      SELECT DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%y/%b") as anoMes, count(a.reclamacoes_id) as tot_rows
      FROM qualisrcaixa.appquali_reclamacoesarquivo a 
        LEFT JOIN qualisrcaixa.reclamacoes r ON r.id  =  a.reclamacoes_id
        INNER JOIN qualisrcaixa.tipos_defeitos AS d ON d.id = r.id_defeito
        WHERE a.reclamacoes_id >= 69 
        GROUP BY anoMes
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()  # row é uma tupla
        res = {}
        num_rows = len(row)
        # converter tupla em dicionário
        for key, value in row:  # Add the key-value pair to the dictionary
            res[key] = value

        # gera lista dia_mes a partir das chaves do dicionario res
        yearMonth = list(res.keys())
        # tipo_recl.reverse()

        # gera lista tot (qtidade reclamacoes) a partir das chaves do dicionario res
        valor_mesAno = list(res.values())
        # qt_reclamacoes.reverse()

    data_json = {'yearMonth': yearMonth, 'num_rows': num_rows}

    # retorna para home.html que chamou funcao defeitosPorTipo via fetch em customs.js
    return JsonResponse(data_json)
    

def defeitosPorMaisFrequentesMesAnterior(request):
    sql = """
        SELECT ucase(tipo_defeito) as tipoId, COUNT(distinct a.reclamacoes_id) as tot,
            MAX(DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%y/%b")) as anoMes
            FROM qualisrcaixa.appquali_reclamacoesarquivo a 
            LEFT JOIN qualisrcaixa.reclamacoes r ON r.id  =  a.reclamacoes_id 
            INNER JOIN qualisrcaixa.tipos_defeitos AS d ON d.id = r.id_defeito 
            WHERE a.reclamacoes_id >= 69
            AND
            YEAR(DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%Y/%m/%d")) = YEAR(CURDATE() - INTERVAL 1 MONTH)
            AND 
            MONTH(DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%Y/%m/%d")) = MONTH(CURDATE() - INTERVAL 1 MONTH) 
            GROUP BY d.tipo_defeito 
            ORDER BY tot DESC LIMIT 7
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()  # row é uma tupla
        #print(rows)

        resultado = [ # como trata-se de uma tupla de tuplas as quais tem 3 valores, criou-se o dicionario resultado e definiu nomes para cada uma das chaves: tipo_defeito, quantidade, anoMes
            {
                "tipo_defeito": tipoId,
                "quantidade": tot,
                "anoMes": anoMes
            }
            for tipoId, tot, anoMes in rows
        ]
        
        labels = [tipoId for tipoId, _, _ in rows]  
        # tanto faz os nomes nos colchetes. Os resultados serao os da 1as pos. nas tuplas que formaram a lista labels, nome tb criado mas poderia ser outro. Note as posicoes dos "_";

        quantidade = [tot for _, tot, _ in rows] 
        # tanto faz os nomes nos colchetes. Os resultados serao os da 2as pos. nas tuplas que formaram a lista quantidade, nome tb criado mas poderia ser outro.. Note as posicoes dos "_";

        anoMes = rows[0][2] if rows else ""
        # anoMes é o mesmo na coluna inteira, então definiu-se por pegar o da 1a linha [0] e coluna [2] que é a posição mesAno na tupla;

        return JsonResponse({
            "labels": labels,  # labels, entre aspas duplas, eh o nome que vai ser respondido para a fcao defeitosPorMaisFrequentesMesAnterior no JS
            "quantidade": quantidade,  # quantidade, entre aspas duplas, eh o nome que vai ser respondido para a fcao defeitosPorMaisFrequentesMesAnterior no JS

            "anoMes": anoMes # labels, entre aspas duplas, eh o nome que vai ser respondido para a fcao defeitosPorMaisFrequentesMesAnterior no JS
        })


def defeitosPorDiaHistorico30(request):
    sql = """
	SELECT DATE_FORMAT(dia_mes_atual, "%d/%b") as dia, tot
    FROM(
        SELECT dia_mes_atual,  tot
          FROM (
                SELECT 
                    DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%Y/%m/%d") as dia_mes_atual, COUNT(distinct a.reclamacoes_id) as tot
                    FROM qualisrcaixa.appquali_reclamacoesarquivo a 
                    LEFT JOIN qualisrcaixa.reclamacoes AS r ON r.id  =  a.reclamacoes_id
                    INNER JOIN qualisrcaixa.tipos_defeitos AS d ON d.id = r.id_defeito
                    #WHERE a.reclamacoes_id >= 69 
                    #AND DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%m/%y") = DATE_FORMAT(CURDATE(), "%m/%y")
                    GROUP BY DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%Y/%m/%d")                
                )  AS X
            ORDER BY dia_mes_atual DESC, tot DESC 
            LIMIT 30
    ) AS Y
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()  # row é uma tupla
        res = {}

        # converter tupla em dicionário
        for key, value in row:  # Add the key-value pair to the dictionary
            res[key] = value

        # gera lista dia_mes a partir das chaves do dicionario res
        dia_mes = list(res.keys())
        dia_mes.reverse()

        # gera lista tot (qtidade reclamacoes) a partir das chaves do dicionario res
        qt_reclamacoes = list(res.values())
        qt_reclamacoes.reverse()

    data_json = {'dia_mes': dia_mes, 'tot': qt_reclamacoes}

    # retorna para home.html que chamou funcao defeitosPorDiaHistorico30 via fetch em customs.js
    return JsonResponse(data_json)


def tiposDefeitosMes(request):
    sql = """
    SELECT mesAno, tipoId,  tot
    FROM
    (
        SELECT DATE_FORMAT(dia, "%y/%b") AS mesAno, tipoId,  max(tot) as tot
        FROM
        (
            SELECT MAX(DATE_FORMAT(SUBSTRING(a.itens, 22, 10), "%Y/%m/%d")) as dia, ucase(tipo_defeito) as tipoId, count(r.id_defeito) as tot
            FROM
            qualisrcaixa.appquali_reclamacoesarquivo a
            LEFT JOIN qualisrcaixa.reclamacoes r ON r.id=a.reclamacoes_id
            INNER JOIN qualisrcaixa.tipos_defeitos AS d ON d.id=r.id_defeito
            WHERE a.reclamacoes_id >= 69
            GROUP BY MONTH(DATE_FORMAT(SUBSTRING(a.itens, 22, 10), "%Y/%m/%d")), d.tipo_defeito
            ORDER BY tot DESC
        ) AS X
        GROUP BY mesAno, tipoId
        ORDER BY mesAno, tot desc
    ) Y
    WHERE mesAno = "25/Nov"
    """
    return render(request, 'tiposDefeitosMes.html')


def listaDefeitos(request):
    sql = """
    SELECT d.id, ucase(tipo_defeito) as tipoId
        FROM qualisrcaixa.tipos_defeitos as d
        ORDER BY d.tipo_defeito
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()  # row é uma tupla
        num_rows = len(rows)

        resultado = [
            {
                "num_id"   : num_id,
                "tipoId"   : tipoId,
                "num_rows" : num_rows
            }
            for num_id, tipoId in rows
        ]
        
        num_id = [num_id for num_id, _ in rows]
        # tanto faz os nomes nos colchetes. Os resultados serao os da 1as pos. nas tuplas que formaram a lista num_id, nome tb criado mas poderia ser outro. Note as posicoes dos "_";

        tipoId = [tipoId for _, tipoId in rows]
        # tanto faz os nomes nos colchetes. Os resultados serao os da 2as pos. nas tuplas que formaram a lista labels, nome tb criado mas poderia ser outro. Note as posicoes dos "_";

        return JsonResponse({
            "num_Id"   : num_id,
            "tipoId"    : tipoId,
            "num_rows"  : num_rows
        })
      
           
def tiposDefeitosPorSemana(request):
    
    defeito_escolhido = request.GET.get('defeito_escolhido')    
    
    sql = f"SELECT semAno, tot, defeito,  dias FROM (SELECT semAno, count(distinct rec) as tot, defeito, max(dia) as dias FROM (SELECT CONCAT(WEEK(DATE_FORMAT(SUBSTRING(a.data_upload,1,10), '%Y/%m/%d'),1),'_',DATE_FORMAT(SUBSTRING(a.data_upload,1,10), '%m'),'/',DATE_FORMAT(SUBSTRING(a.data_upload,1,10), '%y'))  AS semAno, DATE_FORMAT(SUBSTRING(a.data_upload,1,10), '%Y/%m/%d') AS dia,ucase(tipo_defeito) as defeito, a.reclamacoes_id as rec FROM qualisrcaixa.appquali_reclamacoesarquivo a LEFT JOIN qualisrcaixa.reclamacoes r ON r.id  =  a.reclamacoes_id INNER JOIN qualisrcaixa.tipos_defeitos AS d ON d.id = r.id_defeito WHERE d.id = '{defeito_escolhido}' ORDER BY defeito DESC ) AS X  GROUP BY semAno, defeito ORDER BY semAno) as Y ORDER BY dias "
    
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()  # row é uma tupla
        num_rows = len(rows)
        
        resultado = [
            {
                "semanAno": semAno,
                "total": tot,
                "defect": defeito,
                "num_rows":  num_rows,
                "dias": dias
            }
            for semAno, defeito, tot,  dias in rows
        ]

        semAno = [semAno for semAno, _, _,_ in rows]
        # tanto faz os nomes nos colchetes. Os resultados serao os da 1as pos. nas tuplas que formaram a lista num_id, nome tb criado mas poderia ser outro. Note as posicoes dos "_";
        
        tot = [tot for _, tot, _,_ in rows]
        # tanto faz os nomes nos colchetes. Os resultados serao os da 2as pos. nas tuplas que formaram a lista labels, nome tb criado mas poderia ser outro. Note as posicoes dos "_";
        
        dias = [dias for _,_,_, dias in rows]
        # tanto faz os nomes nos colchetes. Os resultados serao os da 2as pos. nas tuplas que formaram a lista labels, nome tb criado mas poderia ser outro. Note as posicoes dos "_";

        defeito =  rows[0][2] if rows else "" # defeito é sempre o mesmo e está na 2a coluna, por isso só peguei uma linha na coluna 1

        
        # não esquecer que a ordem dos campos dentro da query eh que defini as posicoes dos "_" ...

        return JsonResponse({
            "semAno": semAno,
            "tot": tot,
            "defeito": defeito,
            "num_rows": num_rows,
            "dias": dias
        })
       
        
def data_primeiro_registro(request):
    sql = """
		SELECT r.id,
            DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%d/%m/%Y %H:%i:%s") AS prim_reg,
            r.vendedora
            FROM qualisrcaixa.appquali_reclamacoesarquivo a
            LEFT JOIN qualisrcaixa.reclamacoes r ON r.id = a.reclamacoes_id
            where r.id IS NOT NULL
            ORDER BY r.id desc
            LIMIT 1
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchone()  # row é uma tupla

        return JsonResponse({
            "prim_reg": rows[1],
            "vendedora": rows[2]
        })

        

def data_ultimo_registro(request):
    sql = """
		SELECT r.id,
            DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%d/%m/%Y %H:%i:%s") AS ult_reg,
            r.vendedora
            FROM qualisrcaixa.appquali_reclamacoesarquivo a
            LEFT JOIN qualisrcaixa.reclamacoes r ON r.id = a.reclamacoes_id
            where r.id IS NOT NULL
            ORDER BY r.id
            LIMIT 1;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchone()  # row é uma tupla
        
        return JsonResponse({
            "ult_reg": rows[1],
            "vendedora": rows[2]
        })


def reclamacao_delete_sql(request, pk): # recebe reclamacoes_list.html o valor de id quem é assumido por pk

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM qualisrcaixa.reclamacoes WHERE id = %s",
                [pk]
            )
        return JsonResponse({
            'success': True,
            'message': 'Registro excluído com sucesso!'
        })

    return redirect('reclamacoes_list')


def grafico_defeitos(request):

    sql = """
        SELECT 
            sem_Ano,dia,
            SUM(totrecl) AS quantidade,
            tipoDefeito
        FROM (
            SELECT 
                sem_Ano,
                SUM(tot) AS totrecl,
                dia,
                tipoDefeito
            FROM (
                SELECT 
                    DATE_FORMAT(dia_mes_atual, "%y/%m/%d") AS dia,
                    tot,
                    tipoDefeito,
                    CONCAT(
                        WEEK(dia_mes_atual, 1), "_",
                        DATE_FORMAT(dia_mes_atual, "%m"), "/",
                        DATE_FORMAT(dia_mes_atual, "%y")
                    ) AS sem_Ano
                FROM (
                    SELECT 
                        MAX(DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%Y-%m-%d")) AS dia_mes_atual,
                        COUNT(DISTINCT a.reclamacoes_id) AS tot,
                        d.tipo_defeito AS tipoDefeito
                    FROM qualisrcaixa.appquali_reclamacoesarquivo a
                    LEFT JOIN qualisrcaixa.reclamacoes r ON r.id = a.reclamacoes_id
                    INNER JOIN qualisrcaixa.tipos_defeitos d ON d.id = r.id_defeito
                    WHERE a.reclamacoes_id >= 69
                    GROUP BY 
                        DATE_FORMAT(SUBSTRING(a.data_upload,1,10), "%Y-%m-%d"),
                        tipoDefeito
                ) X
            ) Y
            GROUP BY sem_Ano, tipoDefeito, dia
        ) T
        GROUP BY sem_Ano, tipoDefeito, dia
        ORDER BY  dia, sem_Ano desc
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    # rows = [(sem_Ano, quantidade, tipoDefeito), ...]

    labels = []
    totais_por_semana = {}
    detalhes = {}

    for sem_ano, dia, quantidade, tipo_defeito in rows:

        if sem_ano not in labels:
            labels.append(sem_ano)
            totais_por_semana[sem_ano] = 0
            detalhes[sem_ano] = []

        totais_por_semana[sem_ano] += int(quantidade)

        detalhes[sem_ano].append({
            "defeito": tipo_defeito,
            "quantidade": int(quantidade)
        })

    totais = [totais_por_semana[s] for s in labels]

    return JsonResponse({
        "labels": labels,
        "totais": totais,
        "detalhes": detalhes
    })
    
def maioresReclamantes(request):

    sql = """
        SELECT upper(r.cliente) as cliente, count(r.id_defeito) as tot_cliente
            FROM qualisrcaixa.reclamacoes r
            group by cliente
            ORDER by tot_cliente desc
            limit 7
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()  # row é uma tupla

        resultado = [
            {
                "cliente": cliente,
                "tot_cliente": tot_cliente
            }
            for cliente, tot_cliente in rows
        ]

        cliente = [cliente for cliente, _ in rows]
        # tanto faz os nomes nos colchetes. Os resultados serao os da 1as pos. nas tuplas que formaram a lista num_id, nome tb criado mas poderia ser outro. Note as posicoes dos "_";

        tot_cliente = [tot_cliente for _, tot_cliente in rows]
        # tanto faz os nomes nos colchetes. Os resultados serao os da 2as pos. nas tuplas que formaram a lista labels, nome tb criado mas poderia ser outro. Note as posicoes dos "_";

        # não esquecer que a ordem dos campos dentro da query eh que defini as posicoes dos "_" ...

        return JsonResponse({
            "cliente": cliente,
            "tot_cliente": tot_cliente

        })


def qt_reclamantes(request):
    sql = """
    SELECT count(distinct cliente) as tot_cliente_reclam FROM qualisrcaixa.reclamacoes
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        tot_cliente_reclam = cursor.fetchone()  # row é uma tupla

    data_json = {'tot_cliente_reclam': tot_cliente_reclam}

    return JsonResponse(data_json)


def week_modal(request):
    form = SemanAnoForm(request.POST or None)
    obj = None

    if request.method == "POST" and form.is_valid():
        obj = form.save()

    return render(
        request,
        "appQuali/partials/semanAno_modelForm.html",  # 🔹 template parcial
        {
            "form": form,
            "object": obj
        }
    )
