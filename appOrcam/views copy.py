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
def listar_roteiros_producao(request):
    # 1. Busca os dados atuais do banco
    fabrica = MaquinaFinancasOEE.objects.select_related('maquina').all()

    # 2. Cria o dicionário de busca (Lookup Table)
    dados_maquinas = {
        maq.maquina.nome: {
            'custo': (Decimal('60') / Decimal(str(maq.producao_nominal_hora))) * Decimal(str(maq.custo_minuto)),
            'tempo': Decimal('60') / Decimal(str(maq.producao_nominal_hora))
            
        } for maq in fabrica
    }

    # 3. Define as possibilidades de roteiro
    roteiros_possiveis = {
        "Produção Flexo_Seladora": ["Flexo Xitian", "Seladora"],
        "Produção Flexo_Century_Seladora": ["Flexo Xitian",  "Century", "Seladora"],
        "Produção Flexo_Boca_de_Sapo_Seladora": ["Flexo Xitian",  "Boca de Sapo", "Seladora"],
        "Produção Wonder 1_Century_Seladora": ["Wonder 1", "Century", "Seladora"],
        "Produção Wonder 1_Boca_de_Sapo_Seladora": ["Wonder 1", "Boca de Sapo", "Seladora"],
    }

    # 4. Monta a listagem_final processada
    listagem_final = []
    for nome_roteiro, sequencia in roteiros_possiveis.items():
        custo_total = Decimal('0.0000')
        passos = []

        for nome_m in sequencia:
            info = dados_maquinas.get(
                nome_m, {'custo': Decimal('0'), 'tempo': 0})
            custo_total += info['custo']
            passos.append({'nome': nome_m, 'custo': info['custo']})

        listagem_final.append({
            'nome': nome_roteiro,
            'passos': passos,
            'total': custo_total
        })

    # 5. O ENVIO PARA O HTML
    # O nome que você colocar na 'chave' (esquerda) é o nome que usará no HTML
    return render(request, 'roteiros.html', {'roteiros': listagem_final})
