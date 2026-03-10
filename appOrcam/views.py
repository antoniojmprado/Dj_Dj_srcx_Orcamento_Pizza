from pyexpat.errors import messages

from django.shortcuts import redirect, render, get_object_or_404

from appOrcam.forms import OrcamentoForm
from .models import Orcamento

# =========================
# HOME - PÁGINA INICIAL
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
            # salva o orçamento no banco de dados appOrcam\templates\home.html  appOrcam\templates\home.html
            form.save()
            
            return redirect('home')

    else:
        form = OrcamentoForm()

        return render(request, 'cotar.html', { 'form': form })