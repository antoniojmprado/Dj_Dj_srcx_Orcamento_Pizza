from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from appOEE.models import ParametroFinanceiro, Maquina, Horas_turno, Turnos_dia
from appOrcam.forms import OrcamentoForm
from appOrcam.models import MaquinaFinancasOEE
# Ajuste o nome do model de parâmetros
from .models import Chapa, Custo_tinta, EncargosTrabalhistas, Imposto, Orcamento
from decimal import Decimal
from django.db import connection
from django.db.models import Sum
from .models import MemoriaCalculoDinamica

import os
print(f"SISTEMA LENDO DE: {os.path.abspath(__file__)}")

# =========================
# LISTAR PRODUTOS-CHAPAS-PADRÃO
# ========================= 

def get_chapa_detalhes(request, chapa_id):
    try:
        chapa = Chapa.objects.get(pk=chapa_id)
        data = {
            'nome': chapa.nome,
            'unidades_chapa': chapa.unidades_chapa,
            'largura': float(chapa.largura_cm),
            'comprimento': float(chapa.comprimento_cm),
            'custo_m2': float(chapa.custo_m2),
        }
        return JsonResponse(data)
    except Chapa.DoesNotExist:
        return JsonResponse({'error': 'Chapa não encontrada'}, status=404)
# =========================
# INICIAL - PÁGINA INICIAL
# ========================= appOrcam\templates\home.html
def inicial(request):
    return render(request, 'inicial.html')
    # return render(request, 'appOrcam/templates/home.html')
    
# =========================
# HOME
# ========================= appOrcam\templates\home.html
def home(request):
    # return render(request, 'home.html')
    return render(request, 'appOrcam/templates/listar_orcamentos.html')


# =========================
# IMPRIMIR ORÇAMENTO
# =========================

def imprimir_orcamento(request, pk):
    # Busca o orçamento pelo ID ou dá erro 404 se não existir
    orcamento = get_object_or_404(Orcamento, pk=pk)
    
    impostos_ativos = Imposto.objects.filter(ativo_no_calculo=True)

    context = {
        'orcamento': orcamento,
        'impostos_ativos': impostos_ativos,
    }

    # Passamos o objeto para o template
    return render(request, 'orcamento_pdf.html', context)


# =========================
# SALVAR ORÇAMENTO
# =========================

def form_modelForm(request):
    if request.method == "POST":
        form = OrcamentoForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, 'Dados inseridos com sucesso!')
            return redirect('listar_orcamentos')
        else:
            # O POST aconteceu, mas o formulário tem erros (ex: campo vazio)
            messages.error(
                request, "Os dados não foram salvos. Verifique os campos.")
    else:
        # Se o método for GET (primeira vez entrando na página),
        # apenas criamos o formulário vazio, SEM mensagem de erro.
        form = OrcamentoForm()

    # Este render serve tanto para o erro no POST quanto para o GET inicial
    return render(request, 'cotar.html', {'form': form})

# =========================
# LISTAR ORÇAMENTOS
# =========================

def listar_orcamentos(request):
    orcamentos = Orcamento.objects.all().order_by('-data_criacao')  # Ordena por data de criação, do mais recente para o mais antigo
    return render(request, 'listar_orcamentos.html', {'orcamentos': orcamentos})


# ==========================================
# LISTAR ORÇAMENTOS x ROTEIROS DE PRODUÇÃO
# ==========================================

def listar_roteiros_producao(request, pk):

    # 1. Busca o orçamento específico para obter a quantidade  custo_perda_total
    orcamento = get_object_or_404(Orcamento, pk=pk)
    # 1. Definimos o divisor base vindo do orçamento
    divisor = Decimal(str(orcamento.unidades_chapa or '1'))
    if divisor < 1:
        divisor = Decimal('1')

    # 2. A TRAVA PARA PIZZAS (Adicione este trecho aqui)
    # Verificamos se a palavra "pizza" está no nome do produto (independente de maiúsculas)
    if "pizza" in orcamento.produto_nome.lower():
        divisor = Decimal('1')
        # Isso garante que para qualquer pizza, o rateio de máquina
        # ignore o 'unidades_chapa' e use sempre 1.
        
    custo_materiais = Decimal(str(orcamento.custo_material_unitario or '0.0000'))
    print(f'custo_materiais {custo_materiais}')    
    # Excluímos o custo da tinta para o cálculo dos roteiros, pois ela é um custo fixo por unidade e não varia entre os roteiros.
    
    custo_materiais_parcial = custo_materiais - Decimal(str(orcamento.custo_tinta_unitario or '0.0000'))  
    print(f'custo_materiais_parcial {custo_materiais_parcial}')
    
    custo_materiais = custo_materiais_parcial + Decimal(str(orcamento.custo_tinta_unitario or '0.0000'))
    print(f'custo_materiais {custo_materiais}')

    print(f'Decimal(str(orcamento.custo_tinta_unitario or "0.0000")): {Decimal(str(orcamento.custo_tinta_unitario or "0.0000"))}')
    
    custo_perda_total = Decimal(str(orcamento.custo_perda_total or '0.0000'))
    quantidade_solicitada = Decimal(str(orcamento.quantidade))

    # 2. Busca os dados das máquinas
    fabrica = MaquinaFinancasOEE.objects.select_related('maquina').all()

    # 3. Cria o dicionário de busca com a NOVA LÓGICA
    dados_maquinas = {}
    for maq in fabrica:
        tempo_unit = Decimal('60') / Decimal(str(maq.producao_nominal_hora))
        cb_impr = MemoriaCalculoDinamica.objects.filter(maquina_id=maq.maquina.id).first()
        custo_min = Decimal(str(cb_impr.custo_minuto_real)) if cb_impr else Decimal(str(maq.custo_minuto))

        custo_base = tempo_unit * custo_min
        
        capacidade_producao = Decimal(str(maq.producao_nominal_hora))  # Capacidade nominal da máquina por hora
        # Caso do custo de impressão é o custo de impressao normal dividido pela quantidade de unidades por chapa.
        # Nota: Se a intenção é ratear o custo fixo pela quantidade, a lógica é esta:
        custo_orcado = (custo_base * Decimal(str(maq.producao_nominal_hora))) / quantidade_solicitada
                
        if maq.maquina.impressora:
            custo_orcado = custo_orcado / divisor if divisor > 1 else custo_orcado
                    
        # Caso da máquina de corte: se for corte conjugado, o custo é o mesmo do corte normal dividido pela quantidade de unidades por chapa multiplicada por 2 somente SE FOR PIZZA porque, neste caso, os fundos são produzidos em lote separado, mas se for corte simples, o custo é o mesmo do corte normal (sem divisão). 
        
        if "pizza" not in orcamento.produto_nome.lower() and orcamento.unidades_chapa > 1:
            # Para Kibe, Esfiha ou outro que não seja pizza (tampa+fundo na mesma folha)
            multiplicador = Decimal('1')
        else:            
            multiplicador = Decimal('2') if maq.maquina.corte else Decimal('1')

        if maq.maquina.corte:
            custo_orcado = (custo_orcado * multiplicador) if divisor > 1 else custo_orcado
            
        # Caso da seladora: se for seladora, o custo é o mesmo do corte normal multiplicado por 2 porque os fundos são produzidos em lote separado, mas se for corte simples, o custo é o mesmo do corte normal (sem multiplicação).                
        if maq.maquina.seladora: custo_orcado = custo_orcado * multiplicador if divisor > 1 and "pizza" in orcamento.produto_nome.lower() else custo_orcado
                                       
        dados_maquinas[maq.maquina.nome] = {
            'nome_maquina': maq.maquina.nome,   
            'tempo_maquina': tempo_unit * quantidade_solicitada,
            'custo': custo_orcado,
            'capacidade_producao': capacidade_producao,
        }

    # 4. Roteiros (mantém sua lógica de sequências)
    roteiros_possiveis = {
        "1) Flexo ► Seladora": ["Flexo Xitian", "Seladora"],
        "2) Flexo ► Century ► Seladora": ["Flexo Xitian",  "Century", "Seladora"],
        "3) Flexo ► Boca de Sapo ► Seladora": ["Flexo Xitian",  "Boca de Sapo", "Seladora"],
        "4)  Wonder 1 ► Century ► Seladora": ["Wonder 1", "Century", "Seladora"],
        "5) Wonder 1 ► Boca de Sapo ► Seladora": ["Wonder 1", "Boca de Sapo", "Seladora"],
    }
    tempo_operacao_total = Decimal('0.0000')
    # 5. Processamento Final (Corrigido)
    listagem_final = []
    for nome_roteiro, sequencia in roteiros_possiveis.items():
        custo_total = Decimal('0.0000')
        custo_acumulado = custo_materiais 
        passos = []

        for nome_m in sequencia:
            # Buscamos os dados da máquina. Se não achar, o custo é zero.
            # Não precisamos buscar o nome dentro do 'info', pois já temos o 'nome_m'
            info = dados_maquinas.get(nome_m, {'custo': Decimal('0.0000')})

            custo_maquina = info['custo']
            custo_acumulado += custo_maquina
                       
            tempo_operacao_minutos = info.get('tempo_maquina', Decimal('0.0000'))   
            tempo_operacao_total += tempo_operacao_minutos
            # Montamos o dicionário do passo com informações clarasMaquinaFinancas
            passos.append({
                'nome': nome_m,
                'custo': custo_maquina,
                'tempo_operacao_minutos': tempo_operacao_minutos,
            })
       
        
        listagem_final.append({
            'nome_roteiro': nome_roteiro,            
            'custo_materiais_parcial': custo_materiais_parcial,
            'custo_tinta_unitario': Decimal(str(orcamento.custo_tinta_unitario or '0.0000')),
            'passos': passos,  # Lista de dicionários com nome e custo
            'custo_minuto_total': custo_acumulado,
            'custo_perdas': custo_perda_total if nome_m == sequencia[-1] else Decimal('0.0000'),
            'tempo_operacao_total': tempo_operacao_total
        })
        
        # Inicializa o tempo total do roteiro
        tempo_operacao_total = Decimal('0.0000')

    return render(request, 'roteiros.html', {
        'roteiros': listagem_final,
        'orcamento': orcamento
    })


def memoria_calculo_view(request):
    # 1. Agregações de impostos e ativos
    agregacao = Imposto.objects.filter(ativo_no_calculo=True).aggregate(total=Sum('aliquota'))
    total_impostos = agregacao['total'] or Decimal('0.00')

    agregacao_ativos = MaquinaFinancasOEE.objects.filter(valor_reposicao__isnull=False).aggregate(total=Sum('valor_reposicao'))
    total_ativos = agregacao_ativos['total'] or Decimal('0.00')

    # 2. Busca os dados da View do MySQL
    maquinas_custos = MemoriaCalculoDinamica.objects.all()
    
    maquinas_capacidades = MaquinaFinancasOEE.objects.all()
    
    custo_tinta = Custo_tinta.objects.first()
    custo_tinta_valor = custo_tinta.custo_tinta_unitario if custo_tinta.custo_tinta_unitario else Decimal(
        '0.00')
    
    config_financeira = ParametroFinanceiro.objects.first()
    horas = Horas_turno.objects.first()
    turnos = Turnos_dia.objects.first()
    
    # 3. Custo chapas Ondas B e E
    custo_chapa_onda_b = Chapa.objects.filter(tipo_papelao__icontains='Onda B').first()
    custo_chapa_onda_e = Chapa.objects.filter(tipo_papelao__icontains='Onda E').first()
    custo_onda_b = custo_chapa_onda_b.custo_m2 if custo_chapa_onda_b else Decimal('0.00')
    custo_onda_e = custo_chapa_onda_e.custo_m2 if custo_chapa_onda_e else Decimal('0.00')
    
    print(f'custo_onda_b: {custo_onda_b}, custo_onda_e: {custo_onda_e}')  
    
    impostos_ativos = Imposto.objects.filter(ativo_no_calculo=True)
    
    enc_pct = EncargosTrabalhistas.objects.filter(ativo_no_calculo=True).aggregate(total=Sum('aliquota'))
    encargos_trabalhistas_pct = enc_pct['total'] or Decimal('0.00')
    
    encargos_ativos = EncargosTrabalhistas.objects.filter(ativo_no_calculo=True)
    
    p = ParametroFinanceiro.objects.first()

    # Cálculos Individuais baseados na sua planilha e na lógica da VIEW
    custo_folha = (p.quantidade_pessoas * p.salario_medio) * \
                  (1 + (encargos_trabalhistas_pct / 100)) * \
                  (1 + (p.beneficios_pct / 100))

    aluguel_proporcional = (p.aluguel_iptu_total * p.percentual_empresa_estudo) / 100

    # Depreciação Total (conforme a lógica que você preferiu)
    depreciacao_total = total_ativos * ((p.depreciacao_mensal / 100) / 12)

    # Soma de todos os componentes
    custos_fixos_parcial = custo_folha + aluguel_proporcional + \
        p.prestacoes_investimentos + \
        p.manutencoes_mensais + \
        p.servicos_terceirizados_mensal + \
        depreciacao_total

    outros_custos_fixos = custos_fixos_parcial * p.outros_custos_fixos_pct / 100
    custo_fixo_calculado = custos_fixos_parcial + outros_custos_fixos
    
    pct_outros_custos_fixos = p.outros_custos_fixos_pct if p.outros_custos_fixos_pct else Decimal('0.00')

    # 3. O PULO DO GATO: Criar a lista formatada com o cálculo da porcentagem
    dados_formatados = []
    for m in zip(maquinas_custos, maquinas_capacidades):
        dados_formatados.append({
            'nome_maquina': m[0].nome_maquina,
            'valor_reposicao': m[0].valor_reposicao,
            'depreciacao_maquina': m[0].depreciacao_maquina,  # Novo campo vindo da VIEW
            # Multiplica por 100 aqui
            'participacao_pct': (m[0].participacao_real or 0) * 100,
            'custo_absorvido': (m[0].participacao_real or 0) * (m[0].custo_fixo_total_ref or 0),
            'custo_minuto_real': m[0].custo_minuto_real,
            # Adicionado para o cabeçalho não quebrar
            'custo_fixo_total_ref': m[0].custo_fixo_total_ref,
            # Novo campo vindo da tabela de máquinas
            'capacidade_producao': m[1].producao_nominal_hora if m[1].producao_nominal_hora else Decimal('0.00'),  
            'capacidade_producao_minuto': 1/(m[1].producao_nominal_hora/60) if m[1].producao_nominal_hora else Decimal('0.00'),  
            'custo_unidade': (m[0].custo_minuto_real * (1/(Decimal(str(m[1].producao_nominal_hora/60))) if m[1].producao_nominal_hora else Decimal('0.00'))) if m[0].custo_minuto_real and m[1].producao_nominal_hora else Decimal('0.00')                 ,
        })

    context = {
        'maquinas': dados_formatados,  # Enviamos a lista processada
        'financeiro': config_financeira,
        'horas': horas,
        'turnos': turnos,
        'total_impostos': total_impostos,
        'total_ativos': total_ativos,
        'impostos_ativos': impostos_ativos,
        'demonstrativo': {
            'folha': custo_folha,
            'encargos_trabalhistas_pct': encargos_trabalhistas_pct,
            'encargos_ativos': encargos_ativos,
            'aluguel': aluguel_proporcional,
            'prestacoes': p.prestacoes_investimentos,
            'manutencoes': p.manutencoes_mensais,
            'terceiros': p.servicos_terceirizados_mensal,
            'depreciacao': depreciacao_total,
            'custo_fixo_parcial': custos_fixos_parcial,
            'outros_custos_pct': outros_custos_fixos,
            'total_geral': custo_fixo_calculado,
            'pct_outros_custos_fixos': pct_outros_custos_fixos,
        },
        # Custo Chapas  Onda B e E
        'custo_onda_b': custo_onda_b,
        'custo_onda_e': custo_onda_e,
        'custo_tinta': custo_tinta_valor 
    }
    return render(request, 'appOrcam/memoria_calculo.html', context)


def orcamento_pdf(request, pk):
    orcamento = get_object_or_404(Orcamento, pk=pk)
    
    # relacao dos impostos ativos para o cálculo
    impostos_ativos = Imposto.objects.filter(ativo_no_calculo=True)
    
    # Valores padrão (caso não encontre nada ou não tenha corte)
    dados = {
        'imp_nome': 'Impressora', 'imp_capac': 0, 'imp_custo': 0,
        'cor_nome': 'N/A', 'cor_capac': 0, 'cor_custo': 0
    }

    with connection.cursor() as cursor:
        sql = """
		SELECT 
			nome_impressora,
			capac_nominal_impressora, 
			custo_impressora_minuto,
			nome_corte,
			capac_nominal_corte, 
			custo_corte_minuto,
			--
			# custos individuais por operacao e preco_final_sem_NF (soma dos custos)
			custo_impressao, custo_corte, custo_seladora, custo_total, preco_final_unitario,
			--
			# custo percentuais por maquina em relação ao preco_final_sem_NF			
				(custo_impressao/custo_total) *100 as  custo_impressao_porc,
				(custo_corte/custo_total) *100 as  custo_corte_porc,
				(custo_seladora/custo_total) *100 as  custo_seladora_porc,
                custo_total as custo_unit_sem_margem
        FROM
        (            
				SELECT 
					m_imp.nome AS nome_impressora,
					mf_imp.producao_nominal_hora AS capac_nominal_impressora,
					mf_imp.custo_minuto AS custo_impressora_minuto,
					m_cor.nome AS nome_corte,
					mf_cor.producao_nominal_hora AS capac_nominal_corte,
					mf_cor.custo_minuto AS custo_corte_minuto,
					--
					# custos individuais por operacao
						orc.custo_impressao as custo_impressao,
						orc.custo_corte as custo_corte,
						orc.custo_seladora as custo_seladora,
                        (orc.custo_corte + orc.custo_impressao + orc.custo_seladora + custo_material_unitario + custo_frete_unitario) as custo_total,
					--
					# preco_final_unitario
						orc.preco_final_sem_nota as preco_final_unitario	
				FROM appOrcam_orcamento orc
				-- Join para a Impressora
				LEFT JOIN appOEE_maquina m_imp ON orc.maquina_impressao_id = m_imp.id
				LEFT JOIN appOEE_maquinafinancas mf_imp ON m_imp.id = mf_imp.maquina_id
				-- Join para a Máquina de Corte (Validando a coluna corte = 1)
				LEFT JOIN appOEE_maquina m_cor ON orc.maquina_corte_id = m_cor.id AND m_cor.corte = 1
				LEFT JOIN appOEE_maquinafinancas mf_cor ON m_cor.id = mf_cor.maquina_id
				WHERE orc.id = %s) as x
        """
        cursor.execute(sql, [pk])
        row = cursor.fetchone()
        
        if row:
            dados.update({
                'imp_nome': row[0] or 'Impressora',
                'imp_capac': row[1] or 0,
                'imp_custo': row[2] or 0,
                'cor_nome': row[3] or 'Sem Corte',
                'cor_capac': row[4] or 0,
                'cor_custo': row[5] or 0,
                'custo_impressao': row[6] or 0,
                'custo_corte': row[7] or 0,
                'custo_seladora': row[8] or 0,
				'custo_impressao_porc': row[11] or 0,
				'custo_corte_porc': row[12] or 0,
				'custo_seladora_porc': row[13] or 0,
            })

        context = {
            'orcamento': orcamento,
            'nome_impressora': dados['imp_nome'],
            'nome_corte': dados['cor_nome'],
            'capac_impressao_nominal_hora': dados['imp_capac'],
            'custo_minuto_impressora': dados['imp_custo'],
            'capac_corte_nominal_hora': dados['cor_capac'],
            'custo_minuto_corte': dados['cor_custo'],
            # Adicione estes se o HTML pedir:
            'custo_impressao': dados['custo_impressao'],
            'custo_corte': dados['custo_corte'],
            'custo_seladora': dados['custo_seladora'],
            'custo_impressao_porc':dados['custo_impressao_porc'], 
            'custo_corte_porc': dados['custo_corte_porc'],
            'custo_seladora_porc': dados['custo_seladora_porc'],
            'impostos_ativos':impostos_ativos
        }
        
        return render(request, 'appOrcam/orcamento_pdf.html', context)