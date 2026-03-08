from django.shortcuts import render, get_object_or_404
from .models import Orcamento

# =========================
# HOME - PÁGINA INICIAL
# =========================
def home(request):
    return render(request, 'home.html')


# =========================
# IMPRIMIR ORÇAMENTO
# =========================
def imprimir_orcamento(request, pk):
    # Busca o orçamento pelo ID ou dá erro 404 se não existir
    orcamento = get_object_or_404(Orcamento, pk=pk)

    # Passamos o objeto para o template
    return render(request, 'orcamento_pdf.html', {'orcamento': orcamento})
