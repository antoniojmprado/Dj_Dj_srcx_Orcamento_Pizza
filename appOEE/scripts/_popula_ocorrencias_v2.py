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
    Script GOLD para popular ocorrências de forma consistente,
    sem erros de timezone, FK, peso ou múltiplos objetos.
    """

    print("🔄 Iniciando população de ocorrências...")

    # =========================
    # DADOS BÁSICOS (SEGURANÇA)
    # =========================

    empresa = Empresa.objects.first()
    if not empresa:
        raise RuntimeError("Nenhuma Empresa cadastrada.")

    maquinas = list(Maquina.objects.all())
    if not maquinas:
        raise RuntimeError("Nenhuma Máquina cadastrada.")

    motivos_ids = list(Motivo.objects.values_list("id", flat=True))
    if not motivos_ids:
        raise RuntimeError("Nenhum Motivo cadastrado.")

    tipos_parada = list(Tipo_parada.objects.all())
    if not tipos_parada:
        raise RuntimeError("Nenhum Tipo_parada cadastrado.")

    horas_turno = Horas_turno.objects.first()
    if not horas_turno:
        raise RuntimeError("Nenhum Horas_turno cadastrado.")

    turnos_dia = Turnos_dia.objects.first()
    if not turnos_dia:
        raise RuntimeError("Nenhum Turnos_dia cadastrado.")

    # =========================
    # REGRAS DE DISTRIBUIÇÃO
    # =========================
    # maquina_id: [(motivo_id, peso), ...]

    MOTIVOS_MAQUINA = {
        # exemplo:
        # 1: [(1, 40), (5, 30), (6, 30)]
    }

    agora = timezone.now()

    total_registros = 0

    # =========================
    # LOOP PRINCIPAL
    # =========================

    for maquina in maquinas:

        regras = MOTIVOS_MAQUINA.get(maquina.id)

        # cria entre 5 e 10 ocorrências por máquina
        for _ in range(random.randint(5, 10)):

            # =========================
            # ESCOLHA DO MOTIVO (SAFE)
            # =========================

            if not regras:
                # fallback total
                motivo_id = random.choice(motivos_ids)

            else:
                total_peso = sum(peso for _, peso in regras)
                r = random.random() * total_peso

                acumulado = 0.0   # 🔒 SEMPRE inicializado
                motivo_id = None

                for regra, peso in regras:
                    acumulado += peso
                    if r <= acumulado:
                        motivo_id = regra
                        break

                # fallback defensivo
                if motivo_id is None:
                    motivo_id = regras[-1][0]

            motivo = Motivo.objects.get(id=motivo_id)

            tipo_parada = random.choice(tipos_parada)

            # =========================
            # DATAS COM TIMEZONE
            # =========================

            inicio = agora - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

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

    print(
        f"✅ População finalizada com sucesso: {total_registros} ocorrências criadas.")
