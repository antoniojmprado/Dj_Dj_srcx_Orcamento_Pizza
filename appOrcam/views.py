from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from appOrcam.forms import OrcamentoForm
from .models import Chapa, Orcamento, MaquinaFinancasOEE
from decimal import Decimal

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

    # Passamos o objeto para o template
    return render(request, 'orcamento_pdf.html', {'orcamento': orcamento})


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
    custo_materiais = Decimal(str(orcamento.custo_material_unitario or '0.0000'))
    
    # Excluímos o custo da tinta para o cálculo dos roteiros, pois ela é um custo fixo por unidade e não varia entre os roteiros.
    custo_materiais_parcial = custo_materiais - Decimal(str(orcamento.custo_tinta_unitario or '0.0000'))  
    
    # Custo material por unidade, sem a tinta
    custo_materiais_parcial = custo_materiais_parcial / orcamento.unidades_chapa if orcamento.unidades_chapa > 1 else custo_materiais_parcial
    
    custo_materiais = custo_materiais_parcial + orcamento.custo_tinta_unitario  
        
    custo_perda_total = Decimal(str(orcamento.custo_perda_total or '0.0000'))
    # custo_materiais += custo_perda_total  # Somamos o custo da perda ao
    quantidade_solicitada = Decimal(str(orcamento.quantidade))

    # 2. Busca os dados das máquinas
    fabrica = MaquinaFinancasOEE.objects.select_related('maquina').all()

    # 3. Cria o dicionário de busca com a NOVA LÓGICA
    dados_maquinas = {}
    for maq in fabrica:
        tempo_unit = Decimal('60') / Decimal(str(maq.producao_nominal_hora))
        custo_base = tempo_unit * Decimal(str(maq.custo_minuto))

        # Nota: Se a intenção é ratear o custo fixo pela quantidade, a lógica é esta:
        custo_orcado = (custo_base * Decimal(str(maq.producao_nominal_hora))) / quantidade_solicitada
        

        # Definimos uma variável segura para a divisão
        divisor = Decimal(str(orcamento.unidades_chapa or '1'))
        if divisor < 1:
            divisor = Decimal('1')
            
        # Caso do corte conjugado: o custo de impressão é o corte normal dividido pela quantidade de unidades por chapa.
        if maq.maquina.impressora == 1:
            custo_orcado = custo_orcado / divisor if divisor > 1 else custo_orcado
        
        # Caso da máquina de corte: se for corte conjugado, o custo é o mesmo do corte normal dividido pela quantidade de unidades por chapa multiplicada por 2 porque os fundos são produzidos em lote separado, mas se for corte simples, o custo é o mesmo do corte normal (sem divisão).    
        if maq.maquina.corte == 1:
            custo_orcado = ((custo_orcado / divisor) * 2) if divisor > 1 else custo_orcado
            
        # Caso da seladora: se for seladora, o custo é o mesmo do corte normal multiplicado por 2 porque os fundos são produzidos em lote separado, mas se for corte simples, o custo é o mesmo do corte normal (sem multiplicação).                
        if maq.maquina.seladora == 1:
            custo_orcado = custo_orcado * 2 if divisor > 1 else custo_orcado            
                        
               
        dados_maquinas[maq.maquina.nome] = {
            'nome_maquina': maq.maquina.nome,   
            'tempo_total': tempo_unit * quantidade_solicitada,
            'custo': custo_orcado
        }

    # 4. Roteiros (mantém sua lógica de sequências)
    roteiros_possiveis = {
        "Flexo ► Seladora": ["Flexo Xitian", "Seladora"],
        "Flexo ► Century ► Seladora": ["Flexo Xitian",  "Century", "Seladora"],
        "Flexo ► Boca de Sapo ► Seladora": ["Flexo Xitian",  "Boca de Sapo", "Seladora"],
        "Wonder 1 ► Century ► Seladora": ["Wonder 1", "Century", "Seladora"],
        "Wonder 1 ► Boca de Sapo ► Seladora": ["Wonder 1", "Boca de Sapo", "Seladora"],
    }

    # 5. Processamento Final (Corrigido)
    listagem_final = []
    for nome_roteiro, sequencia in roteiros_possiveis.items():
        custo_total = Decimal('0.0000')
        # Iniciamos o custo do roteiro já com o valor dos materiais
        custo_acumulado = custo_materiais + custo_perda_total
        passos = []

        for nome_m in sequencia:
            # Buscamos os dados da máquina. Se não achar, o custo é zero.
            # Não precisamos buscar o nome dentro do 'info', pois já temos o 'nome_m'
            info = dados_maquinas.get(nome_m, {'custo': Decimal('0.0000')})

            custo_maquina = info['custo']
            custo_acumulado += custo_maquina

            # Montamos o dicionário do passo com informações claras
            passos.append({
                'nome': nome_m,
                'custo': custo_maquina,
            })

        listagem_final.append({
            'nome_roteiro': nome_roteiro,            
            'custo_materiais': custo_materiais,
            'passos': passos,  # Lista de dicionários com nome e custo
            # Atribuímos o custo da perda apenas no último passo
            'total_geral': custo_acumulado,
            'custo_perdas': custo_perda_total if nome_m == sequencia[-1] else Decimal('0.0000')
        })

    return render(request, 'roteiros.html', {
        'roteiros': listagem_final,
        'orcamento': orcamento
    })
