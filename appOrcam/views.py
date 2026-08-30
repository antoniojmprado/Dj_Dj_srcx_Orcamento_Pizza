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
#print(f"SISTEMA LENDO DE: {os.path.abspath(__file__)}")

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

# ==========================================
# LISTAR ORÇAMENTOS x ROTEIROS DE PRODUÇÃO
# ==========================================

def listar_roteiros_producao(request, pk):

    # 1. Busca o orçamento específico
    orcamento = get_object_or_404(Orcamento, pk=pk)
    divisor = Decimal(str(orcamento.unidades_chapa or '1'))
    if divisor < 1:
        divisor = Decimal('1')

    # Trava para Pizzas
    if "pizza" in orcamento.produto_nome.lower():
        divisor = Decimal('1')
        
    custo_materiais = Decimal(str(orcamento.custo_material_unitario or '0.0000'))
    custo_materiais_parcial = custo_materiais - Decimal(str(orcamento.custo_tinta_unitario or '0.0000')) 
    custo_materiais = custo_materiais_parcial + Decimal(str(orcamento.custo_tinta_unitario or '0.0000'))

    custo_perda_total = Decimal(str(orcamento.custo_perda_total or '0.0000'))
    quantidade_solicitada = Decimal(str(orcamento.quantidade))

    # 2. Busca os dados das máquinas
    fabrica = MaquinaFinancasOEE.objects.select_related('maquina').all()


 # 3. Cria o dicionário de busca com a NOVA LÓGICA BLINDADA
    dados_maquinas = {}
    for maq in fabrica:
        if not maq.producao_nominal_hora or maq.producao_nominal_hora <= 0:
            continue

        tempo_unit = Decimal('60') / Decimal(str(maq.producao_nominal_hora))
        
        # Busca na MemoriaCalculoDinamica
        cb_impr = MemoriaCalculoDinamica.objects.filter(maquina_id=maq.maquina.id).first()
        
        # BLINDAGEM: Usa custo_minuto_real apenas se for válido e maior que 0
        if cb_impr and cb_impr.custo_minuto_real and Decimal(str(cb_impr.custo_minuto_real)) > 0:
            custo_min = Decimal(str(cb_impr.custo_minuto_real))
        else:
            custo_min = Decimal(str(maq.custo_minuto or '0.0000'))

        custo_base = tempo_unit * custo_min
        capacidade_producao = Decimal(str(maq.producao_nominal_hora))
        
        custo_orcado = (custo_base * Decimal(str(maq.producao_nominal_hora))) / quantidade_solicitada
                
        if maq.maquina.impressora:
            custo_orcado = custo_orcado / divisor if divisor > 1 else custo_orcado
                    
        if "pizza" not in orcamento.produto_nome.lower() and orcamento.unidades_chapa > 1:
            multiplicador = Decimal('1')
        else:            
            multiplicador = Decimal('2') if maq.maquina.corte else Decimal('1')

        if maq.maquina.corte:
            custo_orcado = (custo_orcado * multiplicador) if divisor > 1 else custo_orcado
            
        if maq.maquina.seladora: 
            custo_orcado = custo_orcado * multiplicador if divisor > 1 and "pizza" in orcamento.produto_nome.lower() else custo_orcado
                                        
        # Nome formatado
        nome_chave = maq.maquina.nome.strip()
        
        # Declaração explícita da variável info_maquina
        info_maquina = {
            'nome_maquina': nome_chave,   
            'tempo_maquina': tempo_unit * quantidade_solicitada,
            'custo': custo_orcado,
            'capacidade_producao': capacidade_producao,
        }
        
        # Guarda a referência no dicionário
        dados_maquinas[nome_chave] = info_maquina
        
        # Apelidos/Compatibilidade para a máquina Wonder
        if "wonder" in nome_chave.lower():
            dados_maquinas["Wonder 1"] = info_maquina
            dados_maquinas["Wonder"] = info_maquina

    # 4. Roteiros ajustados
    roteiros_possiveis = {
        "1) Flexo ► Seladora": ["Flexo Xitian", "Seladora"],
        "2) Flexo ► Century ► Seladora": ["Flexo Xitian", "Century", "Seladora"],
        "3) Flexo ► Boca de Sapo ► Seladora": ["Flexo Xitian", "Boca de Sapo", "Seladora"],
        "4) Wonder 1 ► Century ► Seladora": ["Wonder 1", "Century", "Seladora"],
        "5) Wonder 1 ► Boca de Sapo ► Seladora": ["Wonder 1", "Boca de Sapo", "Seladora"],
    }
    
    # 5. Processamento Final
    listagem_final = []
    for nome_roteiro, sequencia in roteiros_possiveis.items():
        custo_acumulado = custo_materiais 
        passos = []
        tempo_operacao_total = Decimal('0.0000')

        for nome_m in sequencia:
            # Busca com fallback de segurança
            info = dados_maquinas.get(nome_m)
            
            # Se não achar exatamente, tenta achar por aproximação (ex: "Wonder" acha "Wonder 1")
            if not info:
                for chave_maq, dados_m in dados_maquinas.items():
                    if nome_m.lower() in chave_maq.lower() or chave_maq.lower() in nome_m.lower():
                        info = dados_m
                        break
            
            # Se ainda assim não achar, define padrão com custo zero
            if not info:
                info = {'custo': Decimal('0.0000'), 'tempo_maquina': Decimal('0.0000')}

            custo_maquina = info['custo']
            custo_acumulado += custo_maquina
                       
            tempo_operacao_minutos = info.get('tempo_maquina', Decimal('0.0000'))   
            tempo_operacao_total += tempo_operacao_minutos

            passos.append({
                'nome': nome_m,
                'custo': custo_maquina,
                'tempo_operacao_minutos': tempo_operacao_minutos,
            })
        
        listagem_final.append({
            'nome_roteiro': nome_roteiro,            
            'custo_materiais_parcial': custo_materiais_parcial,
            'custo_tinta_unitario': Decimal(str(orcamento.custo_tinta_unitario or '0.0000')),
            'passos': passos,
            'custo_minuto_total': custo_acumulado,
            'custo_perdas': custo_perda_total,
            'tempo_operacao_total': tempo_operacao_total
        })

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


# =========================
# SIMULAÇÕES ORÇAMENTOS
# =========================    

def simulacoes_orcamentos(request, pk):
    orcamento_base = get_object_or_404(Orcamento, pk=pk)
    
    # -------------------------------------------------------------------------
    # 1. RESGATE DE PARÂMETROS DINÂMICOS DO BANCO DE DADOS
    # -------------------------------------------------------------------------
    try:
        impostos_ativos = Imposto.objects.filter(ativo_no_calculo=True)
        total_impostos_banco = sum(float(i.aliquota) for i in impostos_ativos)
        
        icms_registro = impostos_ativos.filter(nome__icontains='icms').first()
        valor_icms = float(icms_registro.aliquota) if icms_registro else 18.0
        
        if total_impostos_banco > valor_icms:
            total_impostos_banco = total_impostos_banco - valor_icms 
            
        taxa_imposto_efetivo = total_impostos_banco / 100.0 if total_impostos_banco > 0 else 0.1065
    except Exception:
        taxa_imposto_efetivo = 0.1075
        
    with connection.cursor() as cursor:
        cursor.execute("SELECT retirada_socio_pct, margem_calc_socio_pct FROM appOEE_parametrofinanceiro LIMIT 1")
        retirada_banco = cursor.fetchone()
        pct_prolabore_socio = float(retirada_banco[0]) / 100.0 if retirada_banco and f"{retirada_banco[0]}" != "None" else 0.05
        pct_calc_socio = float(retirada_banco[1]) / 100.0 if retirada_banco and f"{retirada_banco[1]}" != "None" else 0.15

        cursor.execute("SELECT percentual_comissao FROM appOrcam_comissao_venda WHERE ativo = 1 LIMIT 1")
        comissao_banco = cursor.fetchone()
        pct_comissao_vendas = float(comissao_banco[0]) / 100.0 if comissao_banco else 0.05
    
    # -------------------------------------------------------------------------
    # 2. CAPTURA DO DIVISOR
    # -------------------------------------------------------------------------
    unidades = float(orcamento_base.unidades_chapa) if hasattr(orcamento_base, 'unidades_chapa') and orcamento_base.unidades_chapa else 1.0

    # -------------------------------------------------------------------------
    # 3. ENGENHARIA DE CUSTOS UNITÁRIOS BASEADOS NAS REGRAS REAIS DA MODEL
    # -------------------------------------------------------------------------
    chapa_vinculada = orcamento_base.chapa_utilizada
    custo_chapa_m2 = float(chapa_vinculada.custo_m2) if chapa_vinculada else 4.50
    area_total_caixa = float(orcamento_base.area_total) if hasattr(orcamento_base, 'area_total') else 0.4005
    
    # Espelhando a lógica exata de multiplicação do papelão por 2 quando unidades > 1
    if unidades > 1:
        custo_papelao_unitario = ((area_total_caixa * custo_chapa_m2) / unidades) * 2.0
    else:
        custo_papelao_unitario = area_total_caixa * custo_chapa_m2

    custo_tinta_unitario = float(orcamento_base.custo_tinta_unitario) if hasattr(orcamento_base, 'custo_tinta_unitario') else 0.20
    custo_material_unitario = custo_papelao_unitario + custo_tinta_unitario 
    
    # Custos fixos de máquina vindos da model (que já foram processados unitariamente)
    custo_imp = float(orcamento_base.custo_impressao) if hasattr(orcamento_base, 'custo_impressao') else 0.24
    custo_crt = float(orcamento_base.custo_corte) if hasattr(orcamento_base, 'custo_corte') else 0.10
    custo_sel = float(orcamento_base.custo_seladora) if hasattr(orcamento_base, 'custo_seladora') else 0.02
    custo_frete_unit = float(orcamento_base.custo_frete_unitario) if hasattr(orcamento_base, 'custo_frete_unitario') else 0.30
    
    # -------------------------------------------------------------------------
    # 4. EXECUÇÃO DA MATRIZ DE SIMULAÇÃO PROGRESSIVA
    # -------------------------------------------------------------------------
    quantidades = [500, 1000, 2000,3000, 4000, 5000, 10000]
    margens = [15, 20, 25]
    
    matriz_simulacao = []
    prolabores_fixos = {}
    
    # Ajuste na trava de referência de pró-labore para o lote base de 5.000 unidades
    # utilizando a nova engenharia de markup (Numerador + Pró-labore / Markup)
    for m in margens:
        # 1. Cálculo do custo operacional base para 5k unidades estruturado pela model
        q_ref = 5000.0
        custo_total_papel_5k = custo_papelao_unitario * q_ref
        custo_total_tinta_5k = custo_tinta_unitario * q_ref
        custo_frete_5k = custo_frete_unit * q_ref
        
        if unidades > 1:
            custo_operacional_5k = custo_total_papel_5k + custo_total_tinta_5k + (custo_imp * q_ref / unidades) + (custo_crt * q_ref * 2.0 / unidades) + (custo_sel * q_ref) + custo_frete_5k
        else:
            custo_operacional_5k = custo_total_papel_5k + custo_total_tinta_5k + (custo_imp * q_ref) + (custo_crt * q_ref) + (custo_sel * q_ref) + custo_frete_5k
            
        # 2. Divisor fixo do sócio para encontrar o pro-labore de referência
        socio_divisor = (1.0 - pct_calc_socio - pct_prolabore_socio)
        valor_base_prolabore_5k = custo_operacional_5k / socio_divisor
        prolabores_fixos[m] = valor_base_prolabore_5k * pct_prolabore_socio

        print(f' socio divisor {socio_divisor}')
        print(f' valor_base_prolabore_5k {valor_base_prolabore_5k}')
        print(f' prolabores_fixos {prolabores_fixos}')

    # Geração dos registros da matriz de simulação
    for q in quantidades:
        for m in margens:
            # Nova regra de markup do save da model: 1 - margem_decimal
            markup_divisor = (100.0 - m) / 100.0
            prolabore_lote_fixo = prolabores_fixos[25]  # Mantém a trava padrão baseada na margem de 25%
            
            custo_materiais_total = custo_material_unitario * q
            custo_logistica_total = custo_frete_unit * q
            
            # Cálculo do custo de fabricação total obedecendo as regras de unidades/chapa do save
            if unidades > 1:
                custo_fabricacao_total = (custo_imp * q / unidades) + (custo_crt * q * 2.0 / unidades) + (custo_sel * q)
            else:
                custo_fabricacao_total = (custo_imp * q) + (custo_crt * q) + (custo_sel * q)
                
            custo_operacional_total = custo_materiais_total + custo_fabricacao_total + custo_logistica_total
            
            # Aplicação exata da nova fórmula: (Custo + Prolabore) / Markup
            #### self.preco_final_sem_nota = (custo_industrial_e_frete_sem_margem_atual * (1 + margem_decimal))  + self.prolabore_socio
            # preco_sem_nf_total = (custo_operacional_total + prolabore_lote_fixo) / markup_divisor

            preco_sem_nf_total = custo_operacional_total * (1 + m/100) + prolabore_lote_fixo
            preco_com_nf_total = preco_sem_nf_total * (1.0 + taxa_imposto_efetivo)
            
            margem_lucro_total = preco_sem_nf_total * (m / 100.0)
            custo_vendas_total = preco_sem_nf_total * pct_comissao_vendas
            custo_impostos_total = preco_sem_nf_total * taxa_imposto_efetivo

            matriz_simulacao.append({
                'quantidade': q,
                'custo_materiais_total': custo_materiais_total,
                'custo_fabricacao_total': custo_fabricacao_total,
                'custo_logistica_total': custo_logistica_total,
                'custo_operacional_total': custo_operacional_total,
                'margem_percentual': m,
                'margem_lucro_total': margem_lucro_total,
                'custo_impostos_total': custo_impostos_total,
                'custo_vendas_total': custo_vendas_total,
                'prolabore_total': prolabore_lote_fixo,
                'prolabore_unit': prolabore_lote_fixo / q,
                'preco_sem_nf_total': preco_sem_nf_total,
                'preco_sem_nf_unit': preco_sem_nf_total / q,
                'preco_com_nf_total': preco_com_nf_total,
                'preco_com_nf_unit': preco_com_nf_total / q,
            })

    context = {
        'orcamento': orcamento_base,
        'simulacoes': matriz_simulacao,
    }
    return render(request, 'simulacoes_de_orçamentos.html', context)