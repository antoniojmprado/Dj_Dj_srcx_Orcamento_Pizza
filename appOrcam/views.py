from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from appOEE.models import MaquinaFinancas, ParametroFinanceiro, Maquina, Horas_turno, Turnos_dia
from appOrcam.forms import OrcamentoForm
# Ajuste o nome do model de parâmetros
from .models import Chapa, Custo_tinta, Imposto, Orcamento, MaquinaFinancasOEE
from decimal import Decimal
from django.db import connection
from django.db.models import Sum
from .models import MemoriaCalculoDinamica

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
    return render(request, 'appOrcam/templates/home.html')


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
            'custo': custo_orcado
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
            # Montamos o dicionário do passo com informações claras
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

    agregacao_ativos = MaquinaFinancas.objects.filter(valor_reposicao__isnull=False).aggregate(total=Sum('valor_reposicao'))
    total_ativos = agregacao_ativos['total'] or Decimal('0.00')

    # 2. Busca os dados da View do MySQL
    maquinas_custos = MemoriaCalculoDinamica.objects.all()
    config_financeira = ParametroFinanceiro.objects.first()
    horas = Horas_turno.objects.first()
    turnos = Turnos_dia.objects.first()
    
    p = ParametroFinanceiro.objects.first()

    # Cálculos Individuais baseados na sua planilha e na lógica da VIEW
    custo_folha = (p.quantidade_pessoas * p.salario_medio) * \
                  (1 + (p.encargos_trabalhistas_pct / 100)) * \
                  (1 + (p.beneficios_pct / 100))

    custo_aluguel = (p.aluguel_iptu_total * p.percentual_empresa_estudo) / 100

    # Depreciação Total (conforme a lógica que você preferiu)
    depreciacao_total = total_ativos * ((p.depreciacao_mensal / 100) / 12)

    # Soma de todos os componentes
    custo_fixo_calculado = custo_folha + custo_aluguel + \
        p.prestacoes_investimentos + \
        p.manutencoes_mensais + \
        p.servicos_terceirizados_mensal + \
        depreciacao_total
        
    custo_fixo_calculado = custo_fixo_calculado * (1 + (p.outros_custos_fixos_pct / 100))

    # 3. O PULO DO GATO: Criar a lista formatada com o cálculo da porcentagem
    dados_formatados = []
    for m in maquinas_custos:
        dados_formatados.append({
            'nome_maquina': m.nome_maquina,
            'valor_reposicao': m.valor_reposicao,
            'depreciacao_maquina': m.depreciacao_maquina,  # Novo campo vindo da VIEW
            # Multiplica por 100 aqui
            'participacao_pct': (m.participacao_real or 0) * 100,
            'custo_absorvido': (m.participacao_real or 0) * (m.custo_fixo_total_ref or 0),
            'custo_minuto_real': m.custo_minuto_real,
            # Adicionado para o cabeçalho não quebrar
            'custo_fixo_total_ref': m.custo_fixo_total_ref
        })

    context = {
        'maquinas': dados_formatados,  # Enviamos a lista processada
        'financeiro': config_financeira,
        'horas': horas,
        'turnos': turnos,
        'total_impostos': total_impostos,
        'total_ativos': total_ativos,
        'demonstrativo': {
            'folha': custo_folha,
            'aluguel': custo_aluguel,
            'prestacoes': p.prestacoes_investimentos,
            'manutencoes': p.manutencoes_mensais,
            'terceiros': p.servicos_terceirizados_mensal,
            'depreciacao': depreciacao_total,
            'total_geral': custo_fixo_calculado,
        }
    }
    return render(request, 'appOrcam/memoria_calculo.html', context)




def orcamento_pdf_view(request, pk):
    orcamento = get_object_or_404(Orcamento, pk=pk)
    # Pegamos apenas os impostos que de fato compõem o cálculo
    impostos_ativos = Imposto.objects.filter(ativo_no_calculo=True)

    context = {
        'orcamento': orcamento,
        'impostos_ativos': impostos_ativos,
    }
    return render(request, 'appOrcam/orcamento_pdf.html', context)
