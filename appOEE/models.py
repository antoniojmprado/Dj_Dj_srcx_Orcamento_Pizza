# 1. Imports de utilitários do Django
from decimal import Decimal
from django.db import models
from django.forms import ValidationError
from django.utils import timezone  # <-- Adicione esta linha aqui!
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import connection, transaction
from django.db.models import Sum, Avg  # <-- Aqui está o segredo para o VS Code

from django.core.validators import MinValueValidator
# 2. Imports dos seus Models locais
# Nota: Certifique-se de que este arquivo NÃO é o models.py

# 3. Imports dos seus Forms


class Maquina(models.Model):
    nome = models.CharField(max_length=50, null=True, blank=True)
    corte = models.BooleanField(default=False)
    impressora = models.BooleanField(default=False)
    seladora = models.BooleanField(default=False)

    class Meta:
        db_table = 'maquina'

    def __str__(self):
        if self.nome:
            return str(self.nome)
        return self.nome

#################
# IMPACTO FINANCEIRO
###############################################


class MaquinaFinancas(models.Model):
    # Relaciona com sua Maquina já existente
    maquina = models.OneToOneField(
        'Maquina', on_delete=models.CASCADE, related_name='financas_oee')
    valor_reposicao = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    perc_ativo = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True)
    custo_minuto = models.DecimalField(
        max_digits=16, decimal_places=6, null=True, blank=True)
    horas_turno = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    turnos_dia = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    dias_sem = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    sem_mes = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)

    # Novo campo (Requer migração)
    horas_mes = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True, editable=False)
    minutos_mes = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, editable=False)

    class Meta:
        # Força o Django a usar a tabela que você já criou
        db_table = 'appoee_maquinafinancas'


def calcular_roce_dupont(request):
    # 1. CAPITAL EMPREGADO (Soma do valor das máquinas de R$ 7M + Century, etc)
    # Buscamos direto da tabela que criamos
    investimento_total = MaquinaFinancas.objects.aggregate(
        total=models.Sum('valor_reposicao')
    )['total'] or 0

    # 2. PREJUÍZO POR OCIOSIDADE (Vem da nossa View SQL)
    with connection.cursor() as cursor:
        cursor.execute("SELECT SUM(prejuizo_rs) FROM view_prejuizo_financeiro")
        prejuizo_total = cursor.fetchone()[0] or 0

    # 3. FATURAMENTO POTENCIAL (Estimativa baseada na operação)
    # Digamos que com 100% de OEE a fábrica faturaria R$ 2.000.000,00/mês
    faturamento_potencial = 2000000.00

    # 4. OEE MÉDIO (Pode vir de outra view ou query)
    # Vamos assumir o OEE do "caos" de 45% (0.45)
    oee_medio = 0.45

    # --- CÁLCULOS DUPONT ---

    # Faturamento Real é limitado pelo OEE
    faturamento_real = faturamento_potencial * oee_medio

    # Lucro Operacional Estimado (Faturamento - Custos Fixos - Prejuízo OEE)
    custos_fixos_conhecidos = 440000.00
    lucro_operacional = faturamento_real - custos_fixos_conhecidos - prejuizo_total

    # Margem Líquida (%)
    margem = (lucro_operacional / faturamento_real) * \
        100 if faturamento_real > 0 else 0

    # Giro do Ativo (Vezes)
    giro = faturamento_real / investimento_total if investimento_total > 0 else 0

    # ROCE FINAL (%)
    roce = (lucro_operacional / investimento_total) * \
        100 if investimento_total > 0 else 0

    context = {
        'investimento_total': investimento_total,
        'prejuizo_total': prejuizo_total,
        'margem': margem,
        'giro': giro,
        'roce': roce,
        'faturamento_real': faturamento_real,
    }
    return render(request, 'dashboard_roce.html', context)


class Horas_turno(models.Model):
    qt_horas_turno = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True, unique=True)

    class Meta:
        db_table = 'horas_turno'

    def __str__(self):
        return str(self.qt_horas_turno) if self.qt_horas_turno is not None else ""


class Turnos_dia(models.Model):
    qt_turnos_dia = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True, unique=True)

    class Meta:
        db_table = 'turnos_dia'

    def __str__(self):
        return str(self.qt_turnos_dia) if self.qt_turnos_dia is not None else ""


class Mes_ano(models.Model):
    mes_ano = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True, unique=True)

    class Meta:
        db_table = 'mes_ano'

    def __str__(self):
        return str(self.mes_ano) if self.mes_ano is not None else ""


class Dia_mes(models.Model):
    dia_mes = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True, unique=True)

    class Meta:
        db_table = 'dia_mes'

    def __str__(self):
        return str(self.dia_mes) if self.dia_mes is not None else ""


class Empresa(models.Model):
    nome = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'empresa'

    def __str__(self):
        return self.nome


class Tipo_parada(models.Model):
    descricao = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        db_table = 'tipo_parada'

    def __str__(self):
        return self.descricao


class Motivo(models.Model):
    tipo_parada = models.ForeignKey(
        Tipo_parada, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'motivo'

    def __str__(self):
        return self.nome


class Ocorrencia(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE)
    motivo = models.ForeignKey(Motivo, on_delete=models.CASCADE)
    tipo_parada = models.ForeignKey(Tipo_parada, on_delete=models.CASCADE)
    horas_turno = models.ForeignKey(
        Horas_turno, on_delete=models.CASCADE, null=True, blank=True)
    turnos_dia = models.ForeignKey(
        Turnos_dia, on_delete=models.CASCADE, null=True, blank=True)

    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(null=True, blank=True)

    tempo_parado = models.DurationField(null=True, blank=True)

    qualidade = models.IntegerField(
        default=100,
        db_column='qualidade',
        choices=[(i, f'{i}%') for i in range(40, 101)],
        null=True,
        blank=True
    )

    performance = models.IntegerField(
        default=100,
        db_column='performance',
        choices=[(i, f'{i}%') for i in range(40, 101)],
        null=True,
        blank=True
    )

    disponibilidade = models.IntegerField(
        default=100,
        db_column='disponibilidade'
    )

    def __str__(self):
        return f"{self.maquina} - {self.data_inicio}"

    def clean(self):
        # Primeiro, chamamos o clean da classe pai
        super().clean()

        # Validação lógica: data_fim não pode ser menor que data_inicio
        if self.data_fim and self.data_inicio:
            if self.data_fim < self.data_inicio:
                raise ValidationError({
                    'data_fim': "A data de término não pode ser anterior à data de início."
                })

    def save(self, *args, **kwargs):

        # Garante data_inicio (caso especial fora do admin)
        if not self.data_inicio:
            self.data_inicio = timezone.now()

        # Converte data_fim para timezone-aware se necessário
        if self.data_fim and timezone.is_naive(self.data_fim):
            self.data_fim = timezone.make_aware(
                self.data_fim,
                timezone.get_current_timezone()
            )

        # Calcula tempo parado automaticamente
        if self.data_fim:
            self.tempo_parado = self.data_fim - self.data_inicio
        else:
            self.tempo_parado = None

        super().save(*args, **kwargs)

    def tempo_parado_formatado(self):
        if not self.tempo_parado:
            return '-'

        # converter o timedelta para segundos totais (total_seconds()
        total_segundos = int(self.tempo_parado.total_seconds())
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        segundos = (total_segundos % 60)

        return f'{horas:02d}:{minutos:02d}:{segundos:02d}'

    def __str__(self):
        return f"{self.maquina} - {self.motivo} ({self.data_inicio.strftime('%d/%m/%Y %H:%M')})"


class ParametroFinanceiro(models.Model):
    # Preco Unitario
    preco_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, default=2.60)
    # Quantidade Vendida
    quantidade_vendida = models.IntegerField(default=1720000)

    # Faturamento (agora automatizado)
    # Nota: Removi o default fixo, pois ele será calculado
    faturamento_grupo = models.DecimalField(
        max_digits=15, decimal_places=2, editable=False)

    # ... (restante dos seus campos permanecem iguais)

    def save(self, *args, **kwargs):
        # Calcula o faturamento automaticamente
        self.faturamento_grupo = self.preco_unitario * self.quantidade_vendida
        super(ParametroFinanceiro, self).save(*args, **kwargs)

    # Faturamento e Divisão entre empresas
    faturamento_grupo = models.DecimalField(
        max_digits=15, decimal_places=2, default=4472000.00)
    percentual_empresa_estudo = models.DecimalField(
        max_digits=5, decimal_places=2, default=65.00)

    # Pessoal
    quantidade_pessoas = models.IntegerField(default=65)
    salario_medio = models.DecimalField(
        max_digits=10, decimal_places=2, default=2200.00)
    encargos_trabalhistas_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=67.00)
    beneficios_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00)

    # Outros
    outros_custos_fixos_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=1.00)
    retirada_socio_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.00)
    aluguel_iptu_total = models.DecimalField(
        max_digits=12, decimal_places=2, default=140000.00)

    # Investimentos em equipamentos
    prestacoes_investimentos = models.DecimalField(
        max_digits=15, decimal_places=2, default=300000.00)

    # depreciacao mensal (pode ser calculada a partir do valor de reposição das máquinas)
    depreciacao_mensal = models.DecimalField(
        max_digits=15, decimal_places=2, default=8.00)

    # manutencoes mensais
    manutencoes_mensais = models.DecimalField(
        max_digits=15, decimal_places=2, default=30000)

    # servicos terceirizados mensais (TI, recrutamento, limpeza, segurança, etc)
    servicos_terceirizados_mensal = models.DecimalField(
        max_digits=15, decimal_places=2, default=30000)

    # Relacao custos variaveis e faturamento real
    custo_variav_fatur_real_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.00)

    class Meta:
        verbose_name = "Parâmetro Financeiro"
        verbose_name_plural = "Parâmetros Financeiros"


class Waterfall(models.Model):
    fat_bruto = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    perda_oee = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    fat_real = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    cust_var = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    cust_fixo = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    res_contab = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    perda_disp = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    perda_perf = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    perda_quali = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    cust_inefic = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    res_econom = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    socio = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    oee_atual = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    ativos = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True)
    hr_paralis = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    minutos_mes = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'waterfall'

    def __str__(self):
        return str(self.res_econom) if self.res_econom is not None else ""
