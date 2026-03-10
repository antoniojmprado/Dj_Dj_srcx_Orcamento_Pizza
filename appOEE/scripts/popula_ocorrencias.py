import random
from datetime import datetime, timedelta, time
from django.utils import timezone

from appOEE.models import (
    Ocorrencia,
    Empresa,
    Maquina,
    Motivo,
    Tipo_parada,
    Horas_turno,
    Turnos_dia,
)

# =============================
# PARÂMETROS GERAIS
# =============================

DATA_INICIO = datetime(2025, 11, 1)
DATA_FIM = datetime(2025, 12, 31)

HORAS_TURNO_PADRAO = Horas_turno.objects.filter(qt_horas_turno=8.8).first()
TURNOS_DIA_PADRAO = Turnos_dia.objects.filter(qt_turnos_dia=2).first()

QUALIDADE_PADRAO = 90
PERFORMANCE_PADRAO = 85

EMPRESA_PRINCIPAL = Empresa.objects.get(id=1)

# =============================
# TIPO PARADA POR MOTIVO
# =============================

TIPO_POR_MOTIVO = {
    1: "produtiva",     # setup
    3: "programada",    # refeições
    4: "programada",    # treinamento
}

TIPO_IMPRODUTIVA = "improdutiva"

TIPOS = {
    tp.descricao: tp for tp in Tipo_parada.objects.all()
}

# =============================
# DISTRIBUIÇÃO POR MÁQUINA
# =============================

DISTRIBUICAO = {
    1: [(1, 0.15), (12, 0.10)],                  # Flexo Xintian
    2: [(9, 0.15), (2, 0.10), (13, 0.10), (11, 0.05)],  # Wonder 1
    3: [(13, 0.10), (11, 0.90)],                 # Wonder 2
    4: [(1, 0.05), (2, 0.10), (13, 0.05), (11, 0.05)],  # Century
    5: [(1, 0.05), (13, 0.05), (12, 0.05)],      # Seladora
    6: [(1, 0.05), (2, 0.05), (13, 0.05)],       # Boca de Sapo
}

# =============================
# FUNÇÕES AUXILIARES
# =============================


def daterange(start, end):
    for n in range((end - start).days + 1):
        yield start + timedelta(days=n)


def escolher_tipo_parada(motivo_id):
    descricao = TIPO_POR_MOTIVO.get(motivo_id, TIPO_IMPRODUTIVA)
    return TIPOS[descricao]


def criar_paralisacoes_dia(maquina, dia):
    """Cria pelo menos 2 paralisações no dia, somando até 24h"""

    distribuicao = DISTRIBUICAO.get(maquina.id, [])
    if not distribuicao:
        return

    total_minutos_dia = 24 * 60
    minutos_restantes = total_minutos_dia

    qt_paradas = random.randint(2, 4)
    blocos = sorted(
        random.sample(range(60, minutos_restantes), qt_paradas - 1)
    )
    blocos.append(minutos_restantes)

    inicio_base = datetime.combine(dia, time(6, 0))
    inicio_base = timezone.make_aware(inicio_base)

    ultimo_fim = inicio_base

    for minutos in blocos:
        duracao = timedelta(minutes=min(minutos, 12 * 60))
        fim = ultimo_fim + duracao

        motivo_id = random.choices(
            [m for m, _ in distribuicao],
            weights=[p for _, p in distribuicao],
            k=1
        )[0]

        motivo = Motivo.objects.get(id=motivo_id)
        tipo_parada = escolher_tipo_parada(motivo_id)

        empresa = EMPRESA_PRINCIPAL if random.random() < 0.6 else random.choice(
            Empresa.objects.exclude(id=1)
        )

        Ocorrencia.objects.create(
            data_inicio=ultimo_fim,
            data_fim=fim,
            empresa=empresa,
            maquina=maquina,
            motivo=motivo,
            tipo_parada=tipo_parada,
            horas_turno=HORAS_TURNO_PADRAO,
            turnos_dia=TURNOS_DIA_PADRAO,
            qualidade=QUALIDADE_PADRAO,
            performance=PERFORMANCE_PADRAO,
        )

        ultimo_fim = fim
        minutos_restantes -= int(duracao.total_seconds() / 60)

        if minutos_restantes <= 0:
            break

# =============================
# FUNÇÃO PRINCIPAL
# =============================


def popula():
    print("⏳ Populando ocorrências...")

    maquinas = Maquina.objects.all()

    for dia in daterange(DATA_INICIO, DATA_FIM):
        if dia.weekday() >= 5:  # pula sábado/domingo
            continue

        for maquina in maquinas:
            criar_paralisacoes_dia(maquina, dia)

    print("✅ Base de dados populada com sucesso PÔ!")
