
import os
import math
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from appFrete.models import FreteEdne
from appOEE.models import ParametroFinanceiro, Maquina, Horas_turno, Turnos_dia
from appOrcam.forms import OrcamentoForm
from appOrcam.models import MaquinaFinancasOEE
from .models import Chapa, Custo_tinta, EncargosTrabalhistas, Imposto, Orcamento, LeadOrcamento, ComissaoVenda
from decimal import Decimal
from django.db import connection
from django.db.models import Sum
from .models import MemoriaCalculoDinamica
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db import transaction

from appFrete.services_frete import calcular_melhor_frete_interno


#print(f"SISTEMA LENDO DE: {os.path.abspath(__file__)}")

# =============================
# LISTAR PRODUTOS-CHAPAS-PADRÃO
# ============================= 

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


def simulador_orcamento(request):

    # 1. Verifica se no final do link tem o aviso "?origem=paq"
    origem = request.GET.get('origem')

    if origem == 'packmetric':
        # Veio do PaqMetric: usa o layout verdadeiro sem a navbar fake
        # (Substitua 'base.html' pelo nome do arquivo base real do PaqMetric)
        base_escolhido = 'base_orcam.html' 
    else:
        # Veio do caminho normal de fora: usa a navbar fake
        base_escolhido = 'appOrcam/base_crm.html'

    # Traz as opções direto do banco para popular os <select> do HTML
    chapas = Chapa.objects.all()
    # CORREÇÃO: Usando os campos reais do seu modelo Maquina
    maquinas_imp = Maquina.objects.filter(impressora=True) 
    maquinas_crt = Maquina.objects.filter(corte=True)

    # Busca o vendedor ativo no banco
    comissao_bd = ComissaoVenda.objects.filter(ativo=True).first()
    
    # Se achar, usa o valor do banco. Se por algum motivo não achar, usa 5.0
    perc_comissao_inicial = comissao_bd.percentual_comissao if comissao_bd else 5.0

    # Busca o layout base do banco   
    contexto = {
        'chapas': chapas,
        'maquinas_imp': maquinas_imp,
        'maquinas_crt': maquinas_crt,
        'perc_comissao_inicial': perc_comissao_inicial,
        'layout_base': base_escolhido,
    }
    return render(request, 'appOrcam/simulador_orcamento.html', contexto)


def api_simulador_dinamico(request):
    # 1. Capturas da URL (agora pegando o ID da Chapa)
    chapa_id = request.GET.get('chapa')
    qtd = float(request.GET.get('qtd', 1000))
    preco_papel = float(request.GET.get('papel', 4.50))
    preco_tinta = float(request.GET.get('tinta', 0.20))
    # Captura a margem enviada pelo slider (se vier vazia, assume 0.0)
    margem_raw = request.GET.get('margem')
    margem = float(margem_raw) if margem_raw else 0.0
    imp_id = request.GET.get('imp')
    crt_id = request.GET.get('crt')

    # Captura as unidades por chapa enviadas (padrão 1 se não vier nada)
    unidades_por_chapa = int(request.GET.get('unidades_chapa', 1))
    # 1. Captura o valor vindo do GET (com segurança)
    unidades_chapa_str = request.GET.get('unidades_chapa', '1')
    
    print(f"Debug: unidades_chapa_str capt = {unidades_chapa_str}, unidades_por_chapa = {unidades_por_chapa}")
    try:
        unidades_chapa_val = int(unidades_chapa_str)
        if unidades_chapa_val < 1:
            unidades_chapa_val = 1
    except ValueError:
        unidades_chapa_val = 1

    try:
        with transaction.atomic():
            # 2. Busca a Chapa Exata e ajusta o preço temporário
            chapa_obj = Chapa.objects.get(id=int(chapa_id))
            chapa_obj.custo_m2 = Decimal(str(preco_papel))
            chapa_obj.save() # Fica salvo apenas na transação "fantasma"

            # 3. Busca as Máquinas
            maq_imp = Maquina.objects.get(id=int(imp_id)) if imp_id else None
            maq_crt = Maquina.objects.get(id=int(crt_id)) if crt_id else None

            # Ajusta tinta globalmente na transação
            from .models import Custo_tinta
            tinta_param = Custo_tinta.objects.first()
            if tinta_param:
                tinta_param.custo_tinta_unitario = Decimal(str(preco_tinta))
                tinta_param.save()

            # 4. A MÁGICA: Cria o orçamento dinâmico do zero
            orc = Orcamento(
                cliente="Simulação Interna (Sócio)",
                produto_nome=chapa_obj.nome, # Puxa direto da tabela chapa!
                quantidade=int(qtd),
                chapa_projeto=chapa_obj,
                chapa_utilizada=chapa_obj,
                maquina_impressao=maq_imp,
                maquina_corte=maq_crt,
                margem_real=Decimal(str(margem)),
                custo_frete_unitario=Decimal('0.00') # Frete zerado conforme combinamos
            )

            # Atribui ao objeto com o nome exato do campo na sua Model
            orc.unidades_chapa = unidades_por_chapa
                   

            # Força o frete como zero para a simulação
            orc.custo_frete_unitario = Decimal('0.00')

            
            # 5. Salva e aciona toda a engenharia de cálculo!
            orc.save()

            # 5. Coleta os resultados processados (Bypass do erro de Decimal vs Float)
            custo_total = float(orc.custo_industrial_e_frete_sem_margem)
            qtd_float = float(orc.quantidade)

            # 1. Captura o percentual que veio do JavaScript
            comissao_str = request.GET.get('comissao', '0')
            percentual_comissao = Decimal(comissao_str.replace(',', '.')) # Garante que vira Decimal

            # Define o total de chapas com a regra da Wonder vs Padrão
            chapas_papelao = (orc.quantidade * 2 / orc.unidades_chapa) if orc.unidades_chapa > 1 else orc.quantidade
            quantidade_corte =  2 / orc.unidades_chapa if orc.unidades_chapa > 1 else 1

            custo_papelao_total = float(orc.custo_papelao_unitario) * chapas_papelao
            custo_tinta_total = float(orc.custo_tinta_unitario) * orc.quantidade

            # Aplica a matemática financeira
            custo_materia_prima =  (float(orc.custo_papelao_unitario) * chapas_papelao) + (float(orc.custo_tinta_unitario) * orc.quantidade)
            custo_maquinas = float(orc.custo_impressao/orc.unidades_chapa + orc.custo_corte * quantidade_corte + orc.custo_seladora) * orc.quantidade
            custo_fabricacao = float(custo_materia_prima) + custo_maquinas
            valor_comissao = Decimal(orc.preco_final_sem_nota) * (percentual_comissao / Decimal('100.0'))
            prolabore_socio = float(orc.prolabore_socio)
            lucro_real_empresa = Decimal(orc.preco_final_sem_nota) - Decimal(custo_fabricacao) - Decimal(prolabore_socio) - valor_comissao 

            porc_materia_prima = (Decimal(custo_materia_prima) / Decimal(custo_fabricacao)) * Decimal('100.0') if custo_fabricacao > 0 else Decimal('0.00')
            porc_maquinas = (Decimal(custo_maquinas) / Decimal(custo_fabricacao)) * Decimal('100.0') if custo_fabricacao> 0 else Decimal('0.00')
            porc_custo_fabricacao = (Decimal(custo_fabricacao) / Decimal(custo_fabricacao)) * Decimal('100.0') if custo_fabricacao> 0 else Decimal('0.00')
            porc_custo_papelao_total = (Decimal(custo_papelao_total) / Decimal(custo_fabricacao)) * Decimal('100.0') if custo_fabricacao> 0 else Decimal('0.00')
            porc_custo_tinta_total = (Decimal(custo_tinta_total) / Decimal(custo_fabricacao)) * Decimal('100.0') if custo_fabricacao> 0 else Decimal('0.00')

            porc_lucro_real = (Decimal(lucro_real_empresa) / Decimal(orc.preco_final_sem_nota)) * Decimal('100.0') if orc.preco_final_sem_nota > 0 else Decimal('0.00')

            print(f"Debug: custo_materia_prima={custo_materia_prima}, custo_maquinas={custo_maquinas}, custo_fabricacao={custo_fabricacao}, valor_comissao={valor_comissao}, prolabore_socio={prolabore_socio}, lucro_real_empresa={lucro_real_empresa}, porc_lucro_real={porc_lucro_real}")

            resultados = {
                'status': 'success',
                'preco_s_nf': float(orc.preco_final_sem_nota),
                'preco_c_nf': float(orc.preco_final_com_nota),
                'r_un_s_nf': float(orc.preco_final_sem_nota / orc.quantidade),
                'r_un_c_nf': float(orc.preco_final_com_nota / orc.quantidade),
                'impostos_pct': float(orc.aliquota_imposto_aplicada),
                
                # Detalhamento para o Tooltip / Cards
                'custo_materia_prima': custo_materia_prima,
                'custo_papelao_total': custo_papelao_total,
                'custo_tinta_total': custo_tinta_total,

                'custo_maquinas': custo_maquinas,
                'custo_fabricacao': custo_fabricacao,

                'chapas_papelao': chapas_papelao,

                'margem_percentual': float(orc.margem_real),
                'prolabore_socio': prolabore_socio,
                'percentual_comissao': float(percentual_comissao),
                'valor_comissao': valor_comissao,
                'lucro_real_empresa': lucro_real_empresa,
                'porc_lucro_real': porc_lucro_real,
                'porc_materia_prima': porc_materia_prima,
                'porc_maquinas': porc_maquinas,
                'porc_custo_fabricacao': porc_custo_fabricacao,
                'porc_custo_papelao_total': porc_custo_papelao_total,
                'porc_custo_tinta_total': porc_custo_tinta_total
            }
            # 6. Desfaz tudo sem sujar o banco
            transaction.set_rollback(True)

            return JsonResponse(resultados)

    except Exception as e:
        import traceback
        print(traceback.format_exc()) # Imprime o erro no console do VS Code
        return JsonResponse({'erro': str(e)}, status=500)

    
def pagina_inicial_demo(request):
    return render(request, 'appOrcam/demo_senhor_caixa.html')


def tela_vermelha_demo(request):
    return render(request, 'appOrcam/formulario_vermelho.html')


def calcular_orcamento(request):
    if request.method == 'GET':
        # Puxa os produtos do banco (Filtrando apenas os ativos, se tiver esse campo, ou todos)
        produtos = Chapa.objects.all().order_by('nome')
        return render(request, 'appOrcam/orcamento_cliente.html', {'produtos': produtos})

    if request.method == "POST":
        # 1. Captura os dados básicos (Ajustado para o novo HTML)
        cliente_nome = request.POST.get('cliente') 
        contato = request.POST.get('contato', 'Não informado')
        telefone = request.POST.get('telefone', 'Não informado')
        cep_cliente = request.POST.get('cep')

        # Captura e limpa o CEP (tira traços, pontos ou espaços acidentais)
        cep_limpo = ''.join(filter(str.isdigit, cep_cliente))
        
        # Endereço
        logradouro = request.POST.get('logradouro', '')
        numero = request.POST.get('numero', '')
        complemento = request.POST.get('complemento', '')
        bairro = request.POST.get('bairro', '')
        cidade = request.POST.get('cidade', '')
        uf = request.POST.get('uf', '')

        # 2. Captura a lista de produtos marcados nos checkboxes
        produtos_selecionados = request.POST.getlist('produtos_selecionados')

        # 3. Trava de segurança atualizada
        if not cliente_nome or not cep_limpo or not produtos_selecionados:
            return HttpResponse("Por favor, preencha o Cliente, o CEP e selecione pelo menos um Produto.")

        if len(cep_limpo) != 8:
            return HttpResponse(f"Ops! O CEP informado ({cep_limpo}) é inválido. Por favor, digite um CEP com 8 números.")
            
        try:
            # Máquinas base
            maq_impressao = Maquina.objects.get(id=7)
            maq_corte = Maquina.objects.get(id=10)

            # Variáveis de consolidação do carrinho
            orcamentos_gerados = []
            peso_total_carrinho = 0
            valor_nf_carrinho = 0
            qt_pacotes_carrinho = 0
            volume_total_cm3 = 0
            total_unidades_carrinho = 0
            total_produtos_sem_frete = 0

            # 1. LOOP DE CUSTOS INDUSTRIAIS (Cálculo Puro)
            for prod_id in produtos_selecionados:
                quantidade = request.POST.get(f'quantidade_{prod_id}')
                if not quantidade or int(quantidade) <= 0:
                    continue
                    
                quantidade = int(quantidade)
                chapa = Chapa.objects.get(id=prod_id)

                # Salva o orçamento com FRETE ZERADO para blindar o markup (Igual ao Excel)
                orcamento = Orcamento(
                    cliente=cliente_nome,
                    produto_nome=chapa.nome,
                    quantidade=quantidade,
                    unidades_chapa=chapa.unidades_chapa,
                    maquina_impressao=maq_impressao,
                    maquina_corte=maq_corte,
                    chapa_projeto=chapa,
                    chapa_utilizada=chapa,
                    margem_real=Decimal('15.00'),
                    custo_frete_unitario=Decimal('0.00')
                )
                orcamento.save() 
                
                # Captura o valor puro de fábrica
                valor_item_puro = float(orcamento.preco_final_sem_nota)

                # Acumula os dados físicos para o caminhão
                qt_pacotes = math.ceil(quantidade / int(chapa.unidades_pacote))
                peso_item = qt_pacotes * float(chapa.peso_pacote)
                
                peso_total_carrinho += peso_item
                valor_nf_carrinho += valor_item_puro
                qt_pacotes_carrinho += qt_pacotes
                total_unidades_carrinho += quantidade
                total_produtos_sem_frete += valor_item_puro
                
                # Acumula o volume cúbico em cm³
                comp = float(chapa.comprim_pacote_cm)
                larg = float(chapa.largura_pacote_cm)
                alt = float(chapa.altura_pacote_cm)
                volume_total_cm3 += (comp * larg * alt * qt_pacotes)

                # Guarda o extrato para exibição
                orcamentos_gerados.append({
                    'nome': orcamento.produto_nome,
                    'quantidade': quantidade,
                    'unitario_caixa': valor_item_puro / quantidade,
                    'subtotal': valor_item_puro,
                    'qt_pacotes': qt_pacotes,
                    'peso_carga': peso_item,
                })

            if not orcamentos_gerados:
                return HttpResponse("Por favor, informe a quantidade válida para os produtos selecionados.")

            # 2. MOTOR LOGÍSTICO (Consulta Única)
            prazo_dias_final = 0
            custo_total_frete = 0

            if qt_pacotes_carrinho > 0:
                volume_pacote_medio_cm3 = volume_total_cm3 / qt_pacotes_carrinho
                aresta_media = volume_pacote_medio_cm3 ** (1/3) # Raiz cúbica
                unid_pacote_media = total_unidades_carrinho / qt_pacotes_carrinho
                
                melhor_frete_unitario, prazo_dias_final = calcular_melhor_frete_interno(
                    cep_destino=cep_cliente,
                    valor_nf=valor_nf_carrinho,
                    peso_informado=peso_total_carrinho,
                    comp=aresta_media,
                    larg=aresta_media,
                    alt=aresta_media,
                    qt_pacotes=qt_pacotes_carrinho,
                    unid_pacote=unid_pacote_media
                )
                
                custo_total_frete = melhor_frete_unitario * total_unidades_carrinho

            # 3. FECHAMENTO FINANCEIRO
            total_geral_pedido = total_produtos_sem_frete + custo_total_frete

            def formata_br(valor, casas=2):
                if valor is None: return "0,00"
                formatado = f"{float(valor):,.{casas}f}"
                return formatado.replace(',', 'X').replace('.', ',').replace('X', '.')

            # ==========================================
            # CAPTURA SILENCIOSA DO LEAD (CRM)
            # ==========================================
            try:
                resumo_texto = "<p class='mb-2'><strong>📦 ITENS DO PEDIDO:</strong></p><ul style='list-style-type: none; padding-left: 0;'>"
                for item in orcamentos_gerados:
                    resumo_texto += "<li style='margin-bottom: 12px; border-bottom: 1px solid rgba(150, 150, 150, 0.3); padding-bottom: 8px;'>"
                    resumo_texto += f"  <strong>{item['nome']}</strong><br>"
                    resumo_texto += f"  <span style='font-size: 0.9em;'>Qtd: {formata_br(item['quantidade'], 0)} un. | Unitário: R$ {formata_br(item['unitario_caixa'], 2)}</span><br>"
                    resumo_texto += f"  <strong style='color: #28a745;'>Subtotal: R$ {formata_br(item['subtotal'], 2)}</strong>"
                    resumo_texto += "</li>"
                resumo_texto += "</ul>"
                
                resumo_texto += "<p class='mt-4 mb-2'><strong>🚚 LOGÍSTICA:</strong></p><ul style='list-style-type: none; padding-left: 0;'>"
                resumo_texto += f"<li>Frete Total: <strong>R$ {formata_br(custo_total_frete)}</strong></li>"
                resumo_texto += f"<li>CEP Destino: {cep_cliente}</li>"
                resumo_texto += f"<li>Prazo Estimado: <strong>{int(prazo_dias_final)} dias úteis</strong></li>"
                resumo_texto += "</ul>"

                LeadOrcamento.objects.create(
                    empresa=cliente_nome,
                    nome_contato=contato,
                    telefone=telefone,
                    cep=cep_cliente,
                    cidade=cidade,
                    uf=uf,
                    resumo_pedido=resumo_texto,
                    valor_cotado=total_geral_pedido
                )
            except Exception as e_lead:
                print(f"Erro ao salvar o Lead: {e_lead}")

            endereco_completo = f"{logradouro}, {numero}"
            if complemento:
                endereco_completo += f" - {complemento}"
            endereco_completo += f" - {bairro}, {cidade}/{uf}"

            # --- PREPARAÇÃO DO WHATSAPP DETALHADO ---
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            if len(telefone_limpo) > 0 and len(telefone_limpo) <= 11:
                telefone_limpo = f"55{telefone_limpo}"

            texto_whatsapp = f"*Orçamento Múltiplo Concluído!* 🎉%0A"
            texto_whatsapp += f"Olá, {contato} da empresa {cliente_nome}! Seus itens foram processados.%0A"
            texto_whatsapp += f"📱 Seu telefone de contato: {telefone}%0A%0A"
            
            texto_whatsapp += f"*Itens do Pedido*%0A"
            for item in orcamentos_gerados:
                texto_whatsapp += f"📦 *{item['nome']}*%0A"
                texto_whatsapp += f"🔢 Quantidade: {formata_br(item['quantidade'], 0)} unidades%0A"
                texto_whatsapp += f"📦 Volumes: {int(item['qt_pacotes'])} pacotes (Peso: {formata_br(item['peso_carga'])} kg)%0A"
                texto_whatsapp += f"🏷️ Valor Unitário (Caixa): R$ {formata_br(item['unitario_caixa'], 2)}%0A"
                texto_whatsapp += f"💰 Subtotal (Produtos): R$ {formata_br(item['subtotal'], 2)}%0A%0A"

            texto_whatsapp += f"*Logística e Entrega*%0A"
            texto_whatsapp += f"📍 Endereço: {endereco_completo}%0A"
            texto_whatsapp += f"📍 CEP: {cep_cliente}%0A"
            texto_whatsapp += f"🚚 Custo Total de Frete: R$ {formata_br(custo_total_frete)}%0A"
            texto_whatsapp += f"⏱️ Prazo Estimado: {int(prazo_dias_final)} dias úteis a partir da colocação do pedido.%0A%0A"
            texto_whatsapp += f"✅ *Total Geral do Pedido: R$ {formata_br(total_geral_pedido)}*"
            # --- FIM DA PREPARAÇÃO DO WHATSAPP ---

            # =========================================================================
            # A MÁGICA ACONTECE AQUI: Em vez de HttpResponse gigante, usamos o render!
            # =========================================================================
            contexto = {
                'cliente_nome': cliente_nome,
                'contato': contato,
                'telefone': telefone,
                'orcamentos_gerados': orcamentos_gerados, # Passamos a lista inteira para o template fazer o loop!
                'endereco_completo': endereco_completo,
                'cep_cliente': cep_cliente,
                'custo_total_frete': formata_br(custo_total_frete),
                'prazo_dias_final': int(prazo_dias_final),
                'total_geral_pedido': formata_br(total_geral_pedido),
                'telefone_limpo': telefone_limpo,
                'texto_whatsapp': texto_whatsapp,
            }

            return render(request, 'appOrcam/resultado_orcamento.html', contexto)
        
        except Chapa.DoesNotExist:
            return HttpResponse(f"Ops, {cliente_nome}. Um dos produtos selecionados não existe no banco de dados.")
        except Maquina.DoesNotExist:
            return HttpResponse("Erro interno: As máquinas de impressão (ID 7) ou corte (ID 10) não foram encontradas no banco.")
        except Exception as e:
            return HttpResponse(f"Ocorreu um erro inesperado durante o cálculo: {str(e)}")

    return render(request, 'appOrcam/orcamento_cliente.html')


def consulta_cep_local(request, cep_digitado):
    # Aplica a mesma regra de limpeza que você já usa no cálculo de frete
    cep_limpo = ''.join(filter(str.isdigit, str(cep_digitado)))
    cep_busca = cep_limpo.lstrip('0') if len(cep_limpo) == 8 else cep_limpo
    
    destino = FreteEdne.objects.filter(cep=cep_busca).first()
    
    if destino:
        dados = {
            'erro': False,
            'logradouro': destino.logradouro if destino.logradouro not in ["", "NaN"] else "",
            'bairro': destino.bairro if destino.bairro not in ["", "NaN"] else "",
            'localidade': destino.municipio,
            'uf': destino.uf
        }
    else:
        dados = {'erro': True}
        
    return JsonResponse(dados)

# ==============================================
# PAINEL DA EQUIPE DE VENDAS (LINHA DE PRODUÇÃO)
# ==============================================

# A trava mágica: se não estiver logado, joga para a tela do admin
@login_required(login_url='/admin/login/') 
def painel_fila_vendas(request):
    # Conta quantos leads estão aguardando na fila geral
    leads_na_fila = LeadOrcamento.objects.filter(status='NOVO').count()
    
    # KPIs do Vendedor Logado
    meus_andamento = LeadOrcamento.objects.filter(vendedor_responsavel=request.user.username, status='EM_ATENDIMENTO').count()
    meus_ganhos = LeadOrcamento.objects.filter(vendedor_responsavel=request.user.username, status='GANHO').count()
    meus_perdidos = LeadOrcamento.objects.filter(vendedor_responsavel=request.user.username, status='PERDIDO').count()
    
    return render(request, 'appOrcam/painel_vendas.html', {
        'leads_na_fila': leads_na_fila,
        'vendedor_nome': request.user.username,
        'meus_andamento': meus_andamento,
        'meus_ganhos': meus_ganhos,
        'meus_perdidos': meus_perdidos,
    })


@login_required(login_url='/admin/login/')
def puxar_proximo_lead(request):
    if request.method == 'POST':
        # Pega o chassi do lead mais antigo (o order_by('criado_em') garante o FIFO)
        proximo_lead = LeadOrcamento.objects.filter(status='NOVO').order_by('criado_em').first()
        
        if proximo_lead:
            # Assumiu! Muda o status e carimba o nome do vendedor logado
            proximo_lead.status = 'EM_ATENDIMENTO'
            proximo_lead.vendedor_responsavel = request.user.username #request.user.username sabe quem está clicando no botão
            proximo_lead.save()
            
            # Redireciona para a tela com os dados do cliente e o botão do WhatsApp
            return redirect('detalhe_atendimento', lead_id=proximo_lead.id)
            
    # Se a fila estiver vazia ou se alguém tentar acessar via GET, volta pro painel
    return redirect('painel_fila_vendas')


@login_required(login_url='/admin/login/')
def detalhe_atendimento(request, lead_id):
    # Só deixa ver o lead se for o vendedor responsável por ele
    lead = get_object_or_404(LeadOrcamento, id=lead_id, vendedor_responsavel=request.user.username)
    return render(request, 'appOrcam/detalhe_atendimento.html', {'lead': lead})


@login_required(login_url='/admin/login/')
def meus_atendimentos(request):
    # Busca TODOS os leads do vendedor (Atendimento, Ganhos e Perdidos)
    meus_leads = LeadOrcamento.objects.filter(
        vendedor_responsavel=request.user.username
    ).exclude(status='NOVO').order_by('-atualizado_em')
    
    return render(request, 'appOrcam/meus_atendimentos.html', {'meus_leads': meus_leads})

    

@login_required(login_url='/admin/login/')
def atualizar_status_lead(request, lead_id, novo_status):
    # Proteção 1: Garante que o status seja apenas os permitidos
    if novo_status not in ['GANHO', 'PERDIDO']:
        return redirect('meus_atendimentos')
        
    # Proteção 2: Busca o lead e garante que só o dono dele pode alterar o status
    lead = get_object_or_404(LeadOrcamento, id=lead_id, vendedor_responsavel=request.user.username)
    
    # Atualiza e salva
    lead.status = novo_status
    lead.save()
    
    # Joga de volta para a carteira
    return redirect('meus_atendimentos')


def sair_sistema(request):
    logout(request)
    # Após deslogar, joga a pessoa de volta para a capa do site (demo)
    return redirect('/orcam/')