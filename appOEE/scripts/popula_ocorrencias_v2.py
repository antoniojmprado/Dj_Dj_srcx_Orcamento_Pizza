import random
from datetime import timedelta
from django.utils import timezone

from appOEE.models import (
    Empresa,
    Maquina,
    Motivo,
    Tipo_parada,
    Horas_turno,
    Turnos_dia,
    Ocorrencia
)


def popula():
    """
    Popula ocorrências de forma consistente.
    """

    print("🔄 Iniciando população de ocorrências...")

    # =========================
    # DADOS BÁSICOS
    # =========================
    empresa = Empresa.objects.first()
    if not empresa:
        raise RuntimeError("Nenhuma Empresa cadastrada.")

    maquinas = list(Maquina.objects.all())
    if not maquinas:
        raise RuntimeError("Nenhuma Máquina cadastrada.")

    motivos = list(Motivo.objects.all())
    if not motivos:
        raise RuntimeError("Nenhum Motivo cadastrado.")

    tipos_parada = list(Tipo_parada.objects.all())
    if not tipos_parada:
        raise RuntimeError("Nenhum Tipo_parada cadastrado.")

    horas_turno = Horas_turno.objects.first()
    if not horas_turno:
        raise RuntimeError("Nenhuma Horas_turno cadastrada.")

    turnos_dia = Turnos_dia.objects.first()
    if not turnos_dia:
        raise RuntimeError("Nenhum Turnos_dia cadastrado.")

    agora = timezone.now()
    total_registros = 0

    # =========================
    # LOOP PRINCIPAL
    # =========================
    for maquina in maquinas:

        # cria entre 5 e 10 ocorrências por máquina
        for _ in range(random.randint(5, 10)):

            motivo = random.choice(motivos)
            tipo_parada = random.choice(tipos_parada)

            # =========================
            # DATAS
            # =========================
            inicio = agora - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            # Garante timezone-aware
            if timezone.is_naive(inicio):
                inicio = timezone.make_aware(inicio)

            duracao_min = random.randint(5, 180)
            fim = inicio + timedelta(minutes=duracao_min)

            # =========================
            # CRIA OCORRÊNCIA
            # =========================
            Ocorrencia.objects.create(
                empresa=empresa,
                maquina=maquina,
                motivo=motivo,
                tipo_parada=tipo_parada,
                horas_turno=horas_turno,
                turnos_dia=turnos_dia,
                data_inicio=inicio,
                data_fim=fim,
                qualidade=random.randint(60, 100),
                performance=random.randint(60, 100),
            )

            total_registros += 1

    print(f"✅ População finalizada: {total_registros} ocorrências criadas.")
