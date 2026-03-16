from .models import Orcamento
from django.utils import timezone
from datetime import timedelta


def estatisticas_orcamentos(request):

    agora = timezone.now()
    dia_da_semana = agora.weekday()  # 0=Seg, 6=Dom

   # Se hoje for Domingo (6), queremos a semana que começou há 6 dias (dia 09)
   # Se for qualquer outro dia, queremos a semana anterior de fato.
    if dia_da_semana == 6:
            inicio_semana_alvo = (agora - timedelta(days=6)
                                ).replace(hour=0, minute=0, second=0)
    else:
            inicio_semana_alvo = (
                agora - timedelta(days=dia_da_semana + 7)).replace(hour=0, minute=0, second=0)

    fim_semana_alvo = (inicio_semana_alvo + timedelta(days=5)).replace(hour=23, minute=59, second=59)

    return {
            'total_geral': Orcamento.objects.count(),
            'total_hoje': Orcamento.objects.filter(data_criacao__date=agora.date()).count(),
            'total_semana_passada': Orcamento.objects.filter(data_criacao__range=[inicio_semana_alvo, fim_semana_alvo]
            ).count(),
    }
