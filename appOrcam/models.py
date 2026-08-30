from django.db import connection, models
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.forms import CharField
from django.shortcuts import render
import appOEE
from appOEE.models import Maquina
from django.db.models import Sum

# appOrcam/models.py

class Imposto(models.Model):
    nome = models.CharField(max_length=50)  # Ex: ICMS, PIS/COFINS, IPI
    aliquota = models.DecimalField(max_digits=5, decimal_places=2)  # Ex: 18.00
    ativo_no_calculo = models.BooleanField( default=True)  # Se entra no Markup ou não
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} - {self.aliquota}%"
    
    
class EncargosTrabalhistas(models.Model):
    nome = models.CharField(max_length=50)  # Ex: ICMS, PIS/COFINS, IPI
    aliquota = models.DecimalField(max_digits=5, decimal_places=2)  # Ex: 18.00
    ativo_no_calculo = models.BooleanField( default=True)  # Se entra no Markup ou não
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} - {self.aliquota}%"
    
    
class MemoriaCalculoDinamica(models.Model):
    maquina_id = models.BigIntegerField(primary_key=True)
    nome_maquina = models.CharField(max_length=50)
    valor_reposicao = models.DecimalField(max_digits=12, decimal_places=2)
    depreciacao_maquina = models.DecimalField(max_digits=15, decimal_places=2)
    participacao_real = models.DecimalField(max_digits=15, decimal_places=6)
    custo_fixo_total_ref = models.DecimalField(max_digits=12, decimal_places=2)
    custo_minuto_real = models.DecimalField(max_digits=16, decimal_places=4)

    class Meta:
        managed = False  # O Django ignora nas migrações de tabela
        db_table = 'view_memoria_calculo_dinamica'  # Nome da View no MySQL


class Chapa(models.Model):
    # --- CAMPOS ORIGINAIS (Com seus defaults e configurações) ---
    nome = models.CharField(max_length=100)
    largura_cm = models.DecimalField(max_digits=7, decimal_places=2)
    comprimento_cm = models.DecimalField(max_digits=7, decimal_places=2)
    tipo_papelao = models.CharField(max_length=50, default='Onda B')
    gramatura_kg_m2 = models.DecimalField(max_digits=7, decimal_places=2, default=0.45)
    custo_m2 = models.DecimalField(max_digits=10, decimal_places=2)
    estoque_disponivel = models.BooleanField(default=True)
    larg_apara_m = models.DecimalField(max_digits=7, decimal_places=2, default=0.01)
    preco_apara_kg = models.DecimalField(max_digits=7, decimal_places=2, default=0.8)
    medida_caixa_montada_cm = models.CharField(max_length=50, verbose_name="Medida Montada (cm)", default="0x0x0")
    unidades_chapa = models.PositiveIntegerField(default=1, verbose_name="Unidades por Chapa")
    explicacao_tecnica = models.CharField(max_length=255, blank=True, null=True)

    # --- NOVOS CAMPOS PARA LOGÍSTICA E INTEGRAÇÃO ---
    peso_pacote = models.DecimalField(max_digits=7, decimal_places=3, default=0.000)
    comprim_pacote_cm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    largura_pacote_cm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    altura_pacote_cm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    unidades_pacote = models.PositiveIntegerField(default=50, null=True, blank=True)
    ativo = models.BooleanField(default=True)

    # --- CÁLCULO DINÂMICO DE VOLUME ---
    @property
    def volume_pacote_m3(self):
        if self.comprim_pacote_cm and self.largura_pacote_cm and self.altura_pacote_cm:
            volume_cm3 = self.comprim_pacote_cm * self.largura_pacote_cm * self.altura_pacote_cm
            return round(volume_cm3 / 1000000, 4)
        return 0

    @property
    def area_m2(self):  # neste caso, refere-se a chapa do projeto
        return (self.largura_cm * self.comprimento_cm) / 10000

    @property
    def area_projeto_m2(self):
        return (self.largura_cm/100 - 2 * self.larg_apara_m) * (self.comprimento_cm/100 - 2 * self.larg_apara_m)

    @property
    def preco_kg_compra(self):
        return (self.custo_m2/self.gramatura_kg_m2) if self.gramatura_kg_m2 > 0 else Decimal('0.0')

    @property
    def preco_chapa_compra(self):
        return (self.custo_m2 * self.area_m2) if self.area_m2 > 0 else Decimal('0.0')

    @property
    def perda_projeto(self):
        return (self.area_m2 - self.area_projeto_m2)

    def __str__(self):
        return f"{self.nome} - chapa: {self.largura_cm} x {self.comprimento_cm} - Onda {self.tipo_papelao}"


class MaquinaOEE(models.Model):
    """
    Criada MaquinaOEE para evitar conflito durante as migracoes com a tabela 'maquina' do MySQL.
    IMPORTANTE: Mapeia apenas as colunas que REALMENTE existem na tabela 'maquina'.
    Se 'custo_hora_operacional' não existe lá, também NÃO deve estar aqui.
    """
    nome = models.CharField(max_length=50, null=True, blank=True)
    # Adicione abaixo apenas campos que você tem certeza que existem no MySQL na tabela 'maquina'
    # Se não existirem, o Django dará erro 1054.

    class Meta:
        db_table = 'appOEE_maquina'
        # Isso diz ao Django para NÃO tentar criar ou alterar essa tabela, apenas ler os dados existentes.
        managed = False

    def __str__(self):
        if self.nome:
            return str(self.nome)
        return self.nome

    # How to Fix __str__ Returned Non-String Error in Django Models
    # https://www.youtube.com/watch?v=uDli4npnUk8


class WaterfallOEE(models.Model):
    """
    Criada WaterfallOEE para evitar conflito durante as migracoes com a tabela 'waterfall' do MySQL.
    IMPORTANTE: Mapeia apenas as colunas que REALMENTE existem na tabela 'waterfall'."""
    cust_fixo = models.DecimalField(max_digits=15, decimal_places=2)
    # minutes_mes = models.IntegerField() # Descomente se existir na tabela waterfall

    class Meta:
        managed = False
        db_table = 'waterfall'


class MaquinaFinancasOEE(models.Model):
    # A PK real da tabela é o campo 'id'exit
    # id = models.BigIntegerField(primary_key=True)

    # maquina_id = models.BigIntegerField()
    maquina = models.ForeignKey(
        'appOEE.Maquina',
        on_delete=models.CASCADE,
        related_name='financas_orcamento',
        db_column='maquina_id'  # Isso resolve o conflito de nomes
    )
         
    valor_reposicao = models.DecimalField(max_digits=12, decimal_places=2)
    custo_minuto = models.DecimalField(max_digits=16, decimal_places=6)

    # Outros campos caso queira usar no futuro para conferência
    minutos_mes = models.DecimalField(max_digits=12, decimal_places=2)
    horas_mes = models.DecimalField(max_digits=7, decimal_places=2)

    # velocidade de produção nominal da máquina (unidades por hora), para cálculo do tempo unitário
    # baseei-me nos vídeos que gravei durante o tempo que estive na fábrica, mas isso pode ser ajustado conforme a realidade de cada máquina
    producao_nominal_hora = models.PositiveIntegerField(
        default=0,
        help_text="Capacidade máxima de produção (unidades/hora)"
    )

    @property
    def tempo_unitario_minutos(self):
        """Calcula quanto tempo (em minutos) cada unidade leva na máquina"""
        if self.producao_nominal_hora > 0:
            return 60 / self.producao_nominal_hora
        return 0

    class Meta:
        managed = False
        db_table = 'appOEE_maquinafinancas'


# participacao da maquina na producao total, para rateio do custo fixo do OEE
class ConfiguracaoRateio(models.Model):
    maquina = models.OneToOneField(MaquinaOEE, on_delete=models.CASCADE)
    percentual_producao = models.DecimalField( max_digits=5, decimal_places=2, help_text="Ex: 70.00 para 70%")
    percentual_century = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentual_boca_sapo = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Adicionamos aqui os parâmetros que não existem na tabela 'maquina' original
    producao_un_hora = models.IntegerField(default=1000)
    custo_hora_operacional = models.DecimalField( max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.maquina)


class Custo_tinta(models.Model):
    # Mudando o nome para ficar claro que é por UNIDADE
    custo_tinta_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.20,
        verbose_name="Custo da Tinta (R$ por unidade)"
    )

    class Meta:
        verbose_name = "Custo Tinta"


class Custo_frete(models.Model):
    # Mudando o nome para ficar claro que é por UNIDADE
    custo_frete_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.30,
        verbose_name="Custo do Frete (R$ por unidade)"
    )

    class Meta:
        verbose_name = "Custo Frete"


class CategoriaProduto(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Orcamento(models.Model):
    cliente = models.CharField(max_length=255, db_index=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    produto_nome = models.CharField( max_length=100, default="Caixa de Pizza 35")
    categoria_produto = models.ForeignKey(CategoriaProduto, on_delete=models.SET_NULL, null=True, blank=True)
    quantidade = models.PositiveIntegerField()
    unidades_chapa = models.PositiveIntegerField(default=1, verbose_name="Unidades por Chapa")
    tipo_papelao_db = models.CharField( max_length=50, null=True, blank=True, default='Onda B')
    chapa_projeto = models.ForeignKey(Chapa, on_delete=models.PROTECT, related_name='ideal_set')
    chapa_utilizada = models.ForeignKey(Chapa, on_delete=models.PROTECT, related_name='real_set')
    maquina_impressao = models.ForeignKey(Maquina, on_delete=models.PROTECT, related_name='orcamentos_impressao')
    maquina_corte = models.ForeignKey(Maquina, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos_corte')
    maquina_seladora = models.ForeignKey(Maquina, on_delete=models.SET_NULL,  null=True, blank=True, related_name='orcamentos_seladora')

    # Campos de Custo (Decimal)
    custo_tinta_unitario = models.DecimalField(max_digits=10, decimal_places=4, default=0.20)
    custo_total_tinta = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Custo Total da Tinta")
    
    custo_impressao = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    custo_corte = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    custo_seladora = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    # Novo campo para o total de máquinas
    custo_maquinas = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    custo_material_unitario = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    # Preços
    preco_final_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    margem_real = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    custo_frete_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.30, verbose_name="Frete por Unidade")

    # perdas
    area_total = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    area_projeto_liquida = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    area_perda_projeto = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    perda_area_total = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    perda_area_excedente = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    custo_papelao_total = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    custo_perda_total = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    custo_perda_projeto = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    custo_perda_excedente = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    # prolabore socio
    prolabore_socio = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # resumo_composicao.short_description = 'Detalhamento de Composição'
    # vendas com e sem nota
    # Campo para a escolha do usuário
    venda_com_nota = models.BooleanField(default=False, verbose_name="Venda com Nota Fiscal?")

    # Campos para armazenar os cálculos comparativos
    preco_final_com_nota = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    preco_final_sem_nota = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    aliquota_imposto_aplicada = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    @property
    def tipo_papelao(self):  # neste caso, refere-se a chapa do projeto
        return self.tipo_papelao

    @property
    def capac_corte_nominal_hora(self):
        if self.maquina_corte:
            fin_corte = MaquinaFinancasOEE.objects.filter(maquina_id=self.maquina_corte.id).first()
            
            if fin_corte and fin_corte.producao_nominal_hora > 0:
                return fin_corte.producao_nominal_hora if fin_corte.producao_nominal_hora else ""

    def save(self, *args, **kwargs):
        # 1. MAPEAMENTO DE CATEGORIA POR TIPO DE PAPELÃO
        if self.chapa_utilizada:
            onda = self.chapa_utilizada.tipo_papelao
            if hasattr(self, 'tipo_papelao_db'):
                self.tipo_papelao_db = onda

            if "Onda B" in onda:
                self.categoria_produto_id = 1
            elif "Onda E" in onda:
                filename_prod = self.produto_nome.lower()
                if "kibe" in filename_prod:
                    self.categoria_produto_id = 3
                elif "esfiha" in filename_prod:
                    self.categoria_produto_id = 2
                else:
                    self.categoria_produto_id = 4
                    
            quantidade_formatada = Decimal(str(self.quantidade)) if self.quantidade else Decimal('1')      

            # 0. BUSCA PARÂMETROS GLOBAIS
            params = Custo_tinta.objects.first()
            custo_tinta_unitario = params.custo_tinta_unitario if params else Decimal('0.20')
            self.custo_tinta_unitario = custo_tinta_unitario

            # 1. CUSTO FRETE UNITÁRIO
            self.custo_frete_unitario = self.custo_frete_unitario if self.custo_frete_unitario > 0 else Decimal('0.30')

            # 2. CUSTO DO MATERIAL
            area_utilizada = Decimal(str(self.chapa_utilizada.area_m2))
            custo_m2_papelao = Decimal(str(self.chapa_utilizada.custo_m2))

            # 3. DIVISOR E TRAVA PARA PIZZAS
            divisor = Decimal(str(self.unidades_chapa or '1'))
            
            quant_calc_prolabore  = 5000.0
            q_ref = Decimal(str(quant_calc_prolabore)) # para cálculo prolabore socio

            # =========================================================================
            # RETORNO AO FLUXO GLOBAL (CÓDIGO ALINHADO PARA FORA DO ELSE)
            # =========================================================================
            
            # 2.1 CÁLCULO DINÂMICO DE PERDAS
            if self.chapa_utilizada:
                custo_ref = Decimal(str(self.chapa_utilizada.custo_m2))
                
                self.area_total = Decimal(str(self.chapa_utilizada.largura_cm/100)) * Decimal(str(self.chapa_utilizada.comprimento_cm/100))
                self.area_projeto_liquida = (Decimal(str(self.chapa_projeto.largura_cm/100)) - Decimal(str(self.chapa_projeto.larg_apara_m * 2))) * ((Decimal(str(self.chapa_projeto.comprimento_cm/100)) - Decimal(str(self.chapa_projeto.larg_apara_m * 2))))
                self.area_perda_projeto = (Decimal(str(self.chapa_projeto.largura_cm/100)) * Decimal(str(self.chapa_projeto.larg_apara_m * 2))) + ((Decimal(str(self.chapa_projeto.comprimento_cm/100)) * Decimal(str(self.chapa_projeto.larg_apara_m * 2))))                
                
                self.custo_papelao_total = ((self.area_total * custo_ref * quantidade_formatada)/divisor) * 2 if divisor > 1 else (self.area_total * custo_ref * quantidade_formatada)  
                
                # --- CORRIGIDO: Removido o 'self.' para tornar variável local ---                  
                custo_papelao_total_5k = ((self.area_total * custo_ref * q_ref)/divisor) * 2 if divisor > 1 else (self.area_total * custo_ref * Decimal(str(q_ref)))  
                
                print(f'self.custo_papelao_total {self.custo_papelao_total}')
                
                self.perda_area_total = self.area_total - self.area_projeto_liquida
                self.perda_area_excedente = self.perda_area_total - self.area_perda_projeto
                
                custo_perda_unitario = self.area_perda_projeto * custo_ref
                
                custo_perda_unitario_excedente = ( self.perda_area_total - self.area_perda_projeto) * custo_ref
                                                        
                self.custo_perda_excedente = custo_perda_unitario_excedente * ((self.perda_area_excedente * custo_ref * quantidade_formatada)/divisor) * 2 if divisor > 1 else (self.area_total * custo_ref * quantidade_formatada)                    
        
                                            
                print(f'self.custo_perda_excedente {self.custo_perda_excedente}')                   
                
                self.custo_perda_total = ((custo_perda_unitario * quantidade_formatada)/divisor) * 2 if divisor > 1 else (self.area_perda_projeto * custo_perda_unitario * quantidade_formatada)  
                
                self.custo_perda_projeto = self.area_perda_projeto * custo_ref
                self.custo_perda_excedente = self.custo_perda_total - self.custo_perda_projeto                                

                self.custo_total_tinta = Decimal(str(self.custo_tinta_unitario)) * quantidade_formatada
                
                # --- CORRIGIDO: Removido o 'self.' para tornar variável local ---
                custo_total_tinta_5k = float(self.custo_tinta_unitario) * float(q_ref)
                
                self.custo_material_unitario = self.custo_papelao_total + self.custo_total_tinta 
                                                        
                print(f'self.custo_papelao_total {self.custo_papelao_total}')
                

            try:
                # --- CÁLCULO DE MÁQUINAS DINÂMICO ---
                self.custo_impressao = Decimal('0.0000')
                self.custo_corte = Decimal('0.0000')
                self.custo_seladora = Decimal('0.0000')

                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT maquina_id, fator_k FROM appOEE_maquinafinancas")
                    fatores_banco = cursor.fetchall()
                    mapa_fatores = {row[0]: float(row[1]) for row in fatores_banco if row[1] is not None}

                fator_wonder1  = Decimal(str(mapa_fatores.get(8, 0.89)))
                fator_wonder2  = Decimal(str(mapa_fatores.get(9, 0.89)))
                fator_century  = Decimal(str(mapa_fatores.get(10, 0.81)))
                fator_flexo    = Decimal(str(mapa_fatores.get(7, 1.00)))
                fator_seladora = Decimal(str(mapa_fatores.get(11, 0.09)))

                fator_impressao_medio = (fator_wonder1 + fator_wonder2) / Decimal('2.0')

                # 1. IMPRESSÃO (DINÂMICA)

                fin_impr = MaquinaFinancasOEE.objects.filter(maquina_id=self.maquina_impressao.id).first()
                if fin_impr and fin_impr.producao_nominal_hora > 0:
                    tempo_unit = Decimal('60') / Decimal(str(fin_impr.producao_nominal_hora))
                    cb_impr = MemoriaCalculoDinamica.objects.filter(maquina_id=self.maquina_impressao.id).first()
                    
                    # Fallback de custo por minuto
                    if cb_impr and cb_impr.custo_minuto_real and Decimal(str(cb_impr.custo_minuto_real)) > 0:
                        custo_min = Decimal(str(cb_impr.custo_minuto_real))
                    else:
                        custo_min = Decimal(str(fin_impr.custo_minuto or '0.0'))

                    custo_base = tempo_unit * custo_min 

                    # INICIALIZAÇÃO OBRIGATÓRIA: Evita o erro quando unidades_chapa == 1
                    divisor_calc = Decimal('1')

                    if self.maquina_impressao and self.maquina_impressao.nome.lower() == "flexo xitian" and self.categoria_produto_id == 1:
                        divisor_calc = Decimal('1')
                    elif self.unidades_chapa and self.unidades_chapa > 1:
                        divisor_calc = Decimal(str(self.unidades_chapa))

                    id_maquina_atual = self.maquina_impressao.id
                    if id_maquina_atual in [8, 9]:
                        fator_aplicado = fator_impressao_medio
                    elif id_maquina_atual == 7:
                        fator_aplicado = fator_flexo
                    else:
                        fator_aplicado = Decimal(str(mapa_fatores.get(id_maquina_atual, 1.00)))
                    
                    # Cálculo seguro com divisor_calc garantido
                    self.custo_impressao = (custo_base * fin_impr.producao_nominal_hora / (quantidade_formatada / divisor_calc)) * fator_aplicado

                    custo_impressao_5k = (custo_base * fin_impr.producao_nominal_hora / (Decimal(str(q_ref)) / divisor_calc)) * fator_aplicado if divisor_calc > 1 else (custo_base * fin_impr.producao_nominal_hora / Decimal(str(q_ref))) * fator_aplicado
                    
                    self.maquina_impressao.nome = fin_impr.maquina.nome

                    # --- CORRIGIDO: Removido o 'self.' para tornar variável local ---
                    custo_impressao_5k = (custo_base * fin_impr.producao_nominal_hora / (Decimal(str(q_ref))/divisor_calc)) * fator_aplicado  if divisor_calc > 1 else (custo_base * fin_impr.producao_nominal_hora / Decimal(str(q_ref))) * fator_aplicado
                    
                    print(f'self.custo_impressao {self.custo_impressao}')

                # 2. CORTE (DINÂMICA)
                if self.maquina_corte:
                    fin_corte = MaquinaFinancasOEE.objects.filter(maquina_id=self.maquina_corte.id).first()
                    if fin_corte and fin_corte.producao_nominal_hora > 0:
                        tempo_unit = Decimal('60') / Decimal(str(fin_corte.producao_nominal_hora))
                        cb_corte = MemoriaCalculoDinamica.objects.filter(maquina_id=self.maquina_corte.id).first()
                        custo_min = Decimal(str(cb_corte.custo_minuto_real)) if cb_corte else Decimal(str(fin_corte.custo_minuto))
                        
                        if self.unidades_chapa > 1:
                            divisor_calc = Decimal(str(self.unidades_chapa))
                            custo_base = tempo_unit * custo_min    
                            self.custo_corte = (custo_base * fin_corte.producao_nominal_hora / (quantidade_formatada * 2 / divisor_calc)) * fator_century

                            # --- CORRIGIDO: Removido o 'self.' para tornar variável local ---
                            custo_corte_5k = (custo_base * fin_corte.producao_nominal_hora / (Decimal(str(q_ref)) * 2 / divisor_calc)) * fator_century
                        else:
                            custo_base = tempo_unit * custo_min
                            self.custo_corte = (custo_base * fin_corte.producao_nominal_hora / quantidade_formatada) * fator_century  
                            
                            # --- CORRIGIDO: Removido o 'self.' para tornar variável local ---
                            custo_corte_5k = (custo_base * fin_corte.producao_nominal_hora / Decimal(str(q_ref))) * fator_century 

                # 3. SELADORA (DINÂMICA - ID 11)
                fin_seladora = MaquinaFinancasOEE.objects.filter(maquina_id=11).first()
                if fin_seladora and fin_seladora.producao_nominal_hora > 0:
                    tempo_unit = Decimal('60') / Decimal(str(fin_seladora.producao_nominal_hora))
                    cb_sela = MemoriaCalculoDinamica.objects.filter(maquina_id=11).first()
                    custo_min = Decimal(str(cb_sela.custo_minuto_real)) if cb_sela else Decimal(str(fin_seladora.custo_minuto))

                    custo_base = tempo_unit * custo_min
                    self.custo_seladora = (custo_base * fin_seladora.producao_nominal_hora / quantidade_formatada) * fator_seladora
                    
                    # --- CORRIGIDO: Removido o 'self.' para tornar variável local ---
                    custo_seladora_5k = (custo_base * fin_seladora.producao_nominal_hora / Decimal(str(q_ref))) * fator_seladora
                                    
                self.custo_maquinas = self.custo_impressao + self.custo_corte + self.custo_seladora
                
            except Exception as e:
                print(f"Erro máquinas: {e}")

            # 5. ENGENHARIA DE PREÇO FINAL COM MARKUP DIVISOR
            
            custo_total_papel = float(self.custo_papelao_total)    
            custo_total_tinta = float(self.custo_total_tinta)
            custo_imp = float(self.custo_impressao)
            custo_crt = float(self.custo_corte)
            custo_sel = float(self.custo_seladora)
            
            # --- CORRIGIDO: Agora referenciando as variáveis locais limpas ---                  
            custo_imp_5k = float(custo_impressao_5k) if 'custo_impressao_5k' in locals() else 0.0
            custo_crt_5k = float(custo_corte_5k) if 'custo_corte_5k' in locals() else 0.0
            custo_sel_5k = float(custo_seladora_5k) if 'custo_seladora_5k' in locals() else 0.0
            custo_frete_5k = float(self.custo_frete_unitario) * float(q_ref)
            
            qtd = float(self.quantidade)
            unidades = float(self.unidades_chapa)
            custo_frete = float(self.custo_frete_unitario) * qtd    
            
            # Lógica de cálculo separada por condição
            if unidades > 1:
                # --- CORRIGIDO: Variável local (sem self.) para evitar erro de Setter ---
                custo_industrial_e_frete_sem_margem_atual = custo_total_papel + custo_total_tinta + (custo_imp * qtd / unidades) + (custo_crt * qtd * 2 / unidades) + (custo_sel * qtd) + custo_frete
                                                    
                # Cenário de Referência 5k (com diluição por unidades)
                custo_industrial_e_frete_sem_margem_5k = float(custo_papelao_total_5k) + custo_total_tinta_5k + (custo_imp_5k * float(q_ref) / unidades) + (custo_crt_5k * float(q_ref) * 2 / unidades) + (custo_sel_5k * float(q_ref)) + custo_frete_5k
            else:
                # --- CORRIGIDO: Variável local (sem self.) para evitar erro de Setter ---
                custo_industrial_e_frete_sem_margem_atual = custo_total_papel + custo_total_tinta + (custo_imp * qtd) + (custo_crt * qtd) + (custo_sel * qtd) + custo_frete
                
                # Cenário de Referência 5k
                custo_industrial_e_frete_sem_margem_5k = float(custo_papelao_total_5k) + custo_total_tinta_5k + (custo_imp_5k * float(q_ref)) + (custo_crt_5k * float(q_ref)) + (custo_sel_5k * float(q_ref)) + custo_frete_5k

            with connection.cursor() as cursor:
                cursor.execute("SELECT retirada_socio_pct, margem_calc_socio_pct FROM appOEE_parametrofinanceiro LIMIT 1")
                retirada_banco = cursor.fetchone()
                pct_prolabore_socio = float(retirada_banco[0])/ 100 if retirada_banco and f"{retirada_banco[0]}" != "None" else 0.05
                pct_calc_socio = float(retirada_banco[1])/ 100 if retirada_banco and f"{retirada_banco[1]}" != "None" else 15

                margem_decimal = float(self.margem_real) / 100
                
                socio_divisor = (1 - pct_calc_socio - pct_prolabore_socio)
                
                valor_base_prolabore = custo_industrial_e_frete_sem_margem_5k / socio_divisor
                self.prolabore_socio = valor_base_prolabore * pct_prolabore_socio
                
                print(f"margem_decimal: {margem_decimal}, Preço final sem nota: {self.preco_final_sem_nota}")

                if margem_decimal > 0:
                    markup_divisor = 1 - margem_decimal
                    # --- CORRIGIDO: Utiliza a variável local comum para calcular o preço final ---
                    self.preco_final_sem_nota = (custo_industrial_e_frete_sem_margem_atual + self.prolabore_socio) / markup_divisor
                    print(f"Markup divisor aplicado: {markup_divisor}, Preço final sem nota: {self.preco_final_sem_nota}")
                else:
                    # --- CORRIGIDO: Utiliza a variável local comum caso não haja markup ---
                    self.preco_final_sem_nota = custo_industrial_e_frete_sem_margem_atual
                    print(f"Markup divisor aplicado sem markup: {markup_divisor}, Preço final sem nota: {self.preco_final_sem_nota}")

                total_impostos = Imposto.objects.filter(ativo_no_calculo=True).aggregate(Sum('aliquota'))['aliquota__sum'] or Decimal('0.00')
                self.aliquota_imposto_aplicada = total_impostos

                icms_registro = Imposto.objects.filter(ativo_no_calculo=True, nome__icontains='icms').first()
                valor_icms = icms_registro.aliquota if icms_registro else Decimal('18.0')
               
                total_impostos_calculo = total_impostos
                if total_impostos_calculo > valor_icms:
                    total_impostos_calculo = total_impostos_calculo - valor_icms
               
                imposto_decimal = total_impostos_calculo /100
                self.preco_final_com_nota = float(self.preco_final_sem_nota) * (float(1) + float(imposto_decimal)) 

                if self.venda_com_nota:
                    self.preco_final_unitario = self.preco_final_com_nota
                else:
                    self.preco_final_unitario = self.preco_final_sem_nota
               
                super().save(*args, **kwargs)


    @property
    def get_tipo_papelao(self):
        return self.tipo_papelao_db or self.chapa_utilizada.tipo_papelao

        '''
        Detalhe técnico: variáveis definidas dentro de um método (como papelao) não ficam disponíveis automaticamente no template HTML (PDF). O Django só enxerga o que é um campo do modelo ou um método/propriedade que ele possa chamar.

        Para que você possa usar esse valor no seu orcamento_pdf.html de forma limpa, sem precisar repetir o cálculo na View, a melhor estratégia é transformar esse cálculo em uma @property. Assim, você pode acessar {{ orcamento.custo_papelao_unitario }} diretamente no template, e o Django vai chamar a função para calcular o valor na hora. Isso mantém seu código organizado e evita duplicação de lógica.
        '''

    @property
    def nome_maquina_corte(self):
        """Retorna o nome da máquina de corte"""
        return self.maquina_corte.nome if self.maquina_corte else ""

    @property
    def capac_impressao_nominal_hora(self):
        # Mantenha os 4 espaços aqui também
        if self.maquina:
            obj = MaquinaFinancasOEE.objects.filter(maquina_id=self.maquina.id).first()
            return obj.producao_nominal_hora if obj and obj.producao_nominal_hora else Decimal('0.20')
        return Decimal('0.20')

    @property
    def custo_minuto_impressora(self):
        if self.maquina:
            cb_impr = MemoriaCalculoDinamica.objects.filter(maquina_id=self.maquina.id).first()
            return cb_impr.custo_minuto_real if cb_impr and cb_impr.custo_minuto_real else Decimal('0.86')
        return Decimal('0.86')

    @property
    def nome_maquina_impressao(self):
        """Retorna o nome da máquina de corte""" 
        return self.maquina_impressao.nome if self.maquina_impressao else ""

    @property
    def custo_minuto_corte(self):
    # Aqui, se você tiver um campo específico para corte, use-o, 
    # senão use self.maquina se for a mesma. 
    # Vou assumir que você tem um campo 'maquina_corte' ou similar:
        try:
            # Garanta que maquina_corte existe no seu modelo
            maquina_id = self.maquina_corte.id if hasattr(self, 'maquina_corte') and self.maquina_corte else self.maquina.id
            obj_maquina_corte = MemoriaCalculoDinamica.objects.filter(maquina_id=maquina_id).first()
            return obj_maquina_corte.custo_minuto_real if obj_maquina_corte and obj_maquina_corte.custo_minuto_real else Decimal('0.0')
        except:
            return Decimal('0.0')

    @property
    def nome_maquina_seladora(self):
        """Retorna o nome da máquina de corte"""
        return 'Seladora'

    @property
    def capac_seladora_nominal_hora(self):
        obj_seladora = MaquinaFinancasOEE.objects.get(maquina_id=11)
        return obj_seladora.producao_nominal_hora if obj_seladora.producao_nominal_hora else Decimal('5000')

    @property
    def custo_minuto_seladora(self):
        obj_seladora = MemoriaCalculoDinamica.objects.get(maquina_id=11)
        return obj_seladora.custo_minuto_real if obj_seladora.custo_minuto_real else Decimal('0.86')

    @property
    def nome_chapa_projeto(self):
        """Retorna o nome da máquina de corte"""
        return self.chapa_projeto if self.chapa_projeto else ""

    @property
    def nome_chapa_utilizada(self):
        """Retorna o nome da máquina de corte"""
        return self.chapa_utilizada if self.chapa_utilizada else self.chapa_projeto

    @property
    def gramatura_kg_m2(self):
        return self.chapa_utilizada.gramatura_kg_m2 if self.chapa_utilizada else Decimal('0.400')

    @property
    def total_chapas(self):
        """
        Calcula o total de chapas necessárias para produzir a quantidade desejada, considerando as unidades por
        chapas diferentes para tampas e fundos.
        Se unidades_chapa for 1 ou menos, assume-se que cada chapa é usada para uma unidade (tampa + fundo juntos).
        Se unidades_chapa for maior que 1, calcula-se o número de chapas considerando o corte conjugado, onde cada chapa pode produzir múltiplas unidades (tampas e fundos juntos ????)."""
        if self.unidades_chapa > 1:  #
            # return f"{quantidade_formatada:,}".replace(',', '.') + " chapas (fundos e tampas)"

            qt_chapas = (self.quantidade / self.unidades_chapa) if self.unidades_chapa > 0 else self.quantidade
            # observacao = " Admitido que Fundos e Tampas são de chapas diferentes." if self.chapa_utilizada.unidades_chapa > 1 else ""
            return f" {qt_chapas:.0f} Tampas + " f"  {qt_chapas:.0f} Fundos - CORTE CONJUGADO: {self.unidades_chapa} unidades por chapa"
        else:
            qt_chapas = (self.quantidade / self.unidades_chapa) if self.unidades_chapa > 0 else self.quantidade
            return f"{qt_chapas:,.0f}".replace(',', '.') + " chapas(fundos + tampas)"


    @property
    def custo_papelao_unitario(self):
        """Calcula o custo base da chapa (área x custo_m2)
        considerando o número de unidades por chapa para ratear o custo do papelão entre as unidades produzidas por chapa. Se for corte conjugado (unidades_chapa > 1), o custo de papelão é dividido pelo número de unidades por chapa, caso contrário, o custo de papelão é integral para aquela unidade.
        """
        return  Decimal(str(self.chapa_utilizada.area_m2)) *  Decimal(str(self.chapa_utilizada.custo_m2))             


    @property
    def custo_tinta_padrao(self):
        """Retorna o custo de tinta para o template"""
        params = Custo_tinta.objects.first()
        return params.custo_tinta_unitario if params else Decimal('0.20')

    @property
    def custo_perda_unitario(self):
        return self.area_perda_projeto *  Decimal(str(self.chapa_utilizada.custo_m2))          

    @property
    def custo_total_unitario_fabricacao(self):
        """Soma de todos os custos reais (Material (perdas inclusas) + Máquinas"""
        return (self.custo_papelao_unitario +
                self.custo_tinta_padrao +
                self.custo_impressao +
                self.custo_corte +
                self.custo_seladora)

    @property
    def custo_total_fabricacao(self):
            # Convertendo para float uma única vez para limpar o código
        custo_total_papel = float(self.custo_papelao_total)    
        custo_total_tinta = float(self.custo_total_tinta)
        custo_imp = float(self.custo_impressao)
        custo_crt = float(self.custo_corte)
        custo_sel = float(self.custo_seladora)
        qtd = float(self.quantidade)
        unidades = float(self.unidades_chapa)
        
        # Lógica de cálculo separada por condição
        if unidades > 1:
            # Seu primeiro cenário quando unidades_chapa > 1
            return custo_total_papel + custo_total_tinta + (custo_imp * qtd / unidades) + (custo_crt * qtd * 2 / unidades) + (custo_sel * qtd)
        else:
            # Seu cenário alternativo (quando unidades_chapa <= 1)
            return custo_total_papel + custo_total_tinta + (custo_imp * qtd) + (custo_crt * qtd) + (custo_sel * qtd)
        
    @property
    def custo_total_fabricacao_porc(self):
        """Soma de todos os custos reais (Material (perdas inclusas) + Máquinas"""
        return (self.custo_total_fabricacao*100/self.custo_industrial_e_frete_sem_margem) if self.custo_papelao_total else Decimal('0.20')

    @property
    def custo_unitario_total_sem_margem(self):
        return (self.custo_papelao_unitario +
                self.custo_tinta_padrao +
                self.custo_impressao +
                self.custo_corte +
                self.custo_seladora +
                self.custo_frete_unitario)

    @property
    def custo_industrial_e_frete_sem_margem(self):
            # Convertendo para float uma única vez para limpar o código
        custo_total_papel = float(self.custo_papelao_total)    
        custo_total_tinta = float(self.custo_total_tinta)
        custo_imp = float(self.custo_impressao)
        custo_crt = float(self.custo_corte)
        custo_sel = float(self.custo_seladora)
        qtd = float(self.quantidade)
        unidades = float(self.unidades_chapa)
        custo_frete = float(self.custo_frete_unitario) * qtd    
        
        # Lógica de cálculo separada por condição
        if unidades > 1:
            # Seu primeiro cenário quando unidades_chapa > 1
            return custo_total_papel + custo_total_tinta + (custo_imp * qtd / unidades) + (custo_crt * qtd * 2 / unidades) + (custo_sel * qtd) + custo_frete
        else:
            # Seu cenário alternativo (quando unidades_chapa <= 1)
            return custo_total_papel + custo_total_tinta + (custo_imp * qtd) + (custo_crt * qtd) + (custo_sel * qtd) + custo_frete


    @property
    def preco_final_sem_nota_unitario(self):
        """Preço Final Unitário x Quantidade"""
        return self.preco_final_sem_nota / self.quantidade

    @property
    def preco_final_com_nota_unitario(self):
        """Preço Final Unitário x Quantidade"""
        return self.preco_final_com_nota / self.quantidade

    @property
    def soma_unitario_materiais(self):
        """Soma: Papelão + Perda + Tinta"""
        return float(self.custo_papelao_unitario) + float(self.custo_tinta_padrao)    
        # perda de papelão já está embutida no custo do papelao unitário, pois o custo do papelao é calculado considerando as perdas. Portanto, não é necessário somar a perda de papelão separadamente aqui.


    @property
    def custo_total_materiais(self):
        """Soma: Papelão + Perda + Tinta"""
        return float(self.custo_papelao_total) + float(self.custo_total_tinta)  # Formata o resultado como moeda brasileira


    @property
    def subtotal_processos_unitario(self):
        return self.custo_impressao + self.custo_corte + self.custo_seladora


    @property
    def custo_total_impressao(self):
        return float(self.custo_impressao) * float(self.quantidade)/float(self.unidades_chapa) if self.unidades_chapa > 1 else float(self.custo_impressao) * self.quantidade

    @property
    def custo_total_corte_vinco(self):
        return float(self.custo_corte) * float(self.quantidade) * 2 /float(self.unidades_chapa) if self.unidades_chapa > 1 else float(self.custo_corte) * self.quantidade

    @property
    def custo_total_seladora(self):
        return float(self.custo_seladora) * self.quantidade
    
    
    @property
    def custo_total_processos_fabricacao(self):
        # Convertendo para float uma única vez para limpar o código
        custo_imp = float(self.custo_impressao)
        custo_crt = float(self.custo_corte)
        custo_sel = float(self.custo_seladora)
        qtd = float(self.quantidade)
        unidades = float(self.unidades_chapa)

        # Lógica de cálculo separada por condição
        if unidades > 1:
            # Seu primeiro cenário quando unidades_chapa > 1
            return (custo_imp * qtd / unidades) + (custo_crt * qtd * 2 / unidades) + (custo_sel * qtd)
        else:
            # Seu cenário alternativo (quando unidades_chapa <= 1)
            return (custo_imp * qtd) + (custo_crt * qtd) + (custo_sel * qtd)

    @property
    def margem_percentual_display(self):
        """Garante que a margem apareça como 20 em vez de 0.20 no PDF"""
        return self.margem_real * 100 if self.margem_real < 1 else self.margem_real

    @property
    def total_impostos(self):
        """Soma de todos os custos (Materiais + Processos + Logística)"""
        return self.aliquota_imposto_aplicada if self.aliquota_imposto_aplicada > 0 else Decimal('0')


    @property
    def custo_total_com_margem(self):
        """Soma de todos os custos (Materiais + Processos + Logística)"""
        return float(self.custo_industrial_e_frete_sem_margem) * (float(1) + float(self.margem_real)/100) if self.margem_real >= 0 else float(self.custo_industrial_e_frete_sem_margem)               
    
    @property
    def lucro_por_unidade(self):
        """Soma de todos os custos (Materiais + Processos + Logística)"""
        return float(self.custo_total_com_margem) * (float(self.margem_real)/100)/float(self.quantidade) if self.margem_real > 0 and self.quantidade > 0 else Decimal('0')    
    
    @property
    def lucro(self):
        """margem_real x Quantidade"""
        return float(self.custo_total_com_margem) * (float(self.margem_real)/100)

    #-------------------------------------------------
    # PORCENTAGENS SOBRE CUSTO SEM MARGEM
    #-------------------------------------------------

    @property
    # Porcentagen custo do papelao sobre o custo sem margem
    def custo_papelao_unitario_porc(self):
        params = Custo_tinta.objects.first()
        return float(self.custo_papelao_total)*100/self.custo_industrial_e_frete_sem_margem if self.custo_papelao_total else Decimal('0.20')

    @property
    # Porcentagen da perda do projeto sobre o custo sem margem
    def custo_perda_projeto_porc(self):
        return float(self.custo_perda_total)* 100/self.custo_industrial_e_frete_sem_margem if self.custo_perda_projeto else Decimal('0.20')

    @property
    # Porcentagen custo da tinta sobre o custo sem margem
    def custo_tinta_padrao_porc(self):
        return float(self.custo_total_tinta)*100/self.custo_industrial_e_frete_sem_margem if self.custo_total_tinta else Decimal('0.20')

    @property
    # Porcentagen do custo de impressao sobre o custo sem margem
    def custo_impressao_impresso(self):
        return  float(self.custo_impressao) if self.custo_impressao else Decimal('0.20')

    @property
    # Porcentagen do custo de impressao sobre o custo sem margem
    def custo_impressao_porc(self):
        return float(self.custo_total_impressao)/float(self.custo_industrial_e_frete_sem_margem) * 100 if self.custo_total_impressao else Decimal('0.20')

    @property
    # Porcentagen do custo do corte e vinco sobre o custo sem margem
    def custo_corte_porc(self):
        return float(self.custo_total_corte_vinco)/float(self.custo_industrial_e_frete_sem_margem) * 100 if self.custo_total_corte_vinco  else Decimal('0.20')

    @property
    # Porcentagen do custo da seladora sobre o custo sem margem
    def custo_seladora_porc(self):
        return float(self.custo_seladora)/float(self.custo_industrial_e_frete_sem_margem) * 100 if self.custo_seladora else Decimal('0.20')

    @property
    # Porcentagen do custo_frete_unitario sobre o custo sem margem
    def custo_frete_porc(self):
        return float(self.custo_total_frete)/float(self.custo_industrial_e_frete_sem_margem) * 100 if self.custo_frete_unitario else Decimal('0.20')

    @property
    # BUG #1 CORRIGIDO: era (qtd / unidades_chapa), agora apenas qtd
    def custo_total_frete(self):
        return float(self.custo_frete_unitario) * self.quantidade

    @property
    # Porcentagen do subtotal_proc_industriais_porc sobre o custo sem margem
    def proc_industriais_porc(self):
                # Convertendo para float uma única vez para limpar o código
        custo_imp = float(self.custo_impressao)
        custo_crt = float(self.custo_corte)
        custo_sel = float(self.custo_seladora)
        qtd = float(self.quantidade)
        unidades = float(self.unidades_chapa)

        # Lógica de cálculo separada por condição
        if unidades > 1:
            # Seu primeiro cenário quando unidades_chapa > 1
            return ((custo_imp * qtd / unidades) + (custo_crt * qtd * 2 / unidades) + (custo_sel * qtd))/self.custo_industrial_e_frete_sem_margem * 100 if self.custo_frete_unitario else Decimal('0.20')
        else:
            # Seu cenário alternativo (quando unidades_chapa <= 1)
            return ((custo_imp * qtd) + (custo_crt * qtd) + (custo_sel * qtd))/self.custo_industrial_e_frete_sem_margem * 100 if self.custo_frete_unitario else Decimal('0.20')

    @property
    # Porcentagen do subtotal_proc_industriais_porc sobre o custo sem margem
    def subtotal_materiais_insumos_porc(self):
        return float(self.custo_total_materiais)*100/self.custo_industrial_e_frete_sem_margem if self.custo_total_materiais else Decimal('0.20')

    @property
    # Porcentagen do subtotal_proc_industriais_porc sobre o custo sem margem   custo_unitario_total_sem_margem
    def custo_total_sem_margem_porc(self):
        return (float(self.custo_industrial_e_frete_sem_margem) / float(self.custo_industrial_e_frete_sem_margem)) * 100

    def resumo_composicao(self):
        if not self.preco_final_unitario:
            return "Salve para gerar o resumo."

        papelao = Decimal(str(self.chapa_utilizada.area_m2)) *  Decimal(str(self.chapa_utilizada.custo_m2))

        # Ajustei o cálculo da margem para ser o lucro bruto real
        self.lucro_bruto = self.preco_final_unitario - (papelao + Decimal('0.20') + self.custo_frete_unitario + self.custo_maquinas)

        return (
            f"📦 Papelão: R$ {papelao:.2f} | "
            f"♻️ Perda_papelão: R$ {self.custo_perda_total:.2f} | "
            f"🎨 Tinta: R$ 0.20 | "
            f"🖨️ Impressão: R$ {self.custo_impressao:.2f} | "
            f"✂️ Corte: R$ {self.custo_corte:.2f} | "
            f"🔥 Seladora: R$ {self.custo_seladora:.2f} | "
            f"🚚 Frete: R$ {self.custo_frete_unitario:.2f} | "
            f"💰 Custo_total_com_margem: R$ {(float(self.custo_total_com_margem)):.2f}"
            f"💰 Custo_industrial_e_frete_sem_margem: R$ {(float(self.custo_industrial_e_frete_sem_margem)):.2f}"
            f"💰 Margem de lucro: R$ {lucro_bruto:.2f}"
            f"💰 Preço Final (Sem Nota): R$ {(float(self.preco_final_sem_nota)):.2f}"
            f"💰 Preço Final Unitário(Sem Nota): R$ {(float(self.preco_final_sem_nota_unitario)):.2f}"
            f"💰 Preço Final (Com Nota): R$ {(float(self.preco_final_com_nota)):.2f}"
            f"💰 Preço Final Unitário(Com Nota): R$ {(float(self.preco_final_com_nota_unitario)):.2f}"
            f"💰 Prolabore Sócio: R$ {(float(self.prolabore_socio)):.2f}"
    )

    resumo_composicao.short_description = 'Detalhamento de Composição'

         
    @property
    def get_tipo_papelao(self):
        return self.tipo_papelao_db or self.chapa_utilizada.tipo_papelao

        '''
        Detalhe técnico: variáveis definidas dentro de um método (como papelao) não ficam disponíveis automaticamente no template HTML (PDF). O Django só enxerga o que é um campo do modelo ou um método/propriedade que ele possa chamar.

        Para que você possa usar esse valor no seu orcamento_pdf.html de forma limpa, sem precisar repetir o cálculo na View, a melhor estratégia é transformar esse cálculo em uma @property. Assim, você pode acessar {{ orcamento.custo_papelao_unitario }} diretamente no template, e o Django vai chamar a função para calcular o valor na hora. Isso mantém seu código organizado e evita duplicação de lógica.
        '''

    @property
    def nome_maquina_corte(self):
        """Retorna o nome da máquina de corte"""
        return self.maquina_corte.nome if self.maquina_corte else ""

    @property
    def capac_impressao_nominal_hora(self):
        # Mantenha os 4 espaços aqui também
        if self.maquina:
            obj = MaquinaFinancasOEE.objects.filter(maquina_id=self.maquina.id).first()
            return obj.producao_nominal_hora if obj and obj.producao_nominal_hora else Decimal('0.20')
        return Decimal('0.20')

    @property
    def custo_minuto_impressora(self):
        if self.maquina:
            cb_impr = MemoriaCalculoDinamica.objects.filter(maquina_id=self.maquina.id).first()
            return cb_impr.custo_minuto_real if cb_impr and cb_impr.custo_minuto_real else Decimal('0.86')
        return Decimal('0.86')

    @property
    def nome_maquina_impressao(self):
        """Retorna o nome da máquina de corte""" 
        return self.maquina_impressao.nome if self.maquina_impressao else ""

    @property
    def custo_minuto_corte(self):
    # Aqui, se você tiver um campo específico para corte, use-o, 
    # senão use self.maquina se for a mesma. 
    # Vou assumir que você tem um campo 'maquina_corte' ou similar:
        try:
            # Garanta que maquina_corte existe no seu modelo
            maquina_id = self.maquina_corte.id if hasattr(self, 'maquina_corte') and self.maquina_corte else self.maquina.id
            obj_maquina_corte = MemoriaCalculoDinamica.objects.filter(maquina_id=maquina_id).first()
            return obj_maquina_corte.custo_minuto_real if obj_maquina_corte and obj_maquina_corte.custo_minuto_real else Decimal('0.0')
        except:
            return Decimal('0.0')

    @property
    def nome_maquina_seladora(self):
        """Retorna o nome da máquina de corte"""
        return 'Seladora'

    @property
    def capac_seladora_nominal_hora(self):
        obj_seladora = MaquinaFinancasOEE.objects.get(maquina_id=11)
        return obj_seladora.producao_nominal_hora if obj_seladora.producao_nominal_hora else Decimal('5000')

    @property
    def custo_minuto_seladora(self):
        obj_seladora = MemoriaCalculoDinamica.objects.get(maquina_id=11)
        return obj_seladora.custo_minuto_real if obj_seladora.custo_minuto_real else Decimal('0.86')

    @property
    def nome_chapa_projeto(self):
        """Retorna o nome da máquina de corte"""
        return self.chapa_projeto if self.chapa_projeto else ""

    @property
    def nome_chapa_utilizada(self):
        """Retorna o nome da máquina de corte"""
        return self.chapa_utilizada if self.chapa_utilizada else self.chapa_projeto

    @property
    def gramatura_kg_m2(self):
        return self.chapa_utilizada.gramatura_kg_m2 if self.chapa_utilizada else Decimal('0.400')

    @property
    def total_chapas(self):
        """
        Calcula o total de chapas necessárias para produzir a quantidade desejada, considerando as unidades por
        chapas diferentes para tampas e fundos.
        Se unidades_chapa for 1 ou menos, assume-se que cada chapa é usada para uma unidade (tampa + fundo juntos).
        Se unidades_chapa for maior que 1, calcula-se o número de chapas considerando o corte conjugado, onde cada chapa pode produzir múltiplas unidades (tampas e fundos juntos ????)."""
        if self.unidades_chapa > 1:  #
            # return f"{quantidade_formatada:,}".replace(',', '.') + " chapas (fundos e tampas)"

            qt_chapas = (self.quantidade / self.unidades_chapa) if self.unidades_chapa > 0 else self.quantidade
            # observacao = " Admitido que Fundos e Tampas são de chapas diferentes." if self.chapa_utilizada.unidades_chapa > 1 else ""
            return f" {qt_chapas:.0f} Tampas + " f"  {qt_chapas:.0f} Fundos - CORTE CONJUGADO: {self.unidades_chapa} unidades por chapa"
        else:
            qt_chapas = (self.quantidade / self.unidades_chapa) if self.unidades_chapa > 0 else self.quantidade
            return f"{qt_chapas:,.0f}".replace(',', '.') + " chapas(fundos + tampas)"


    @property
    def custo_papelao_unitario(self):
        """Calcula o custo base da chapa (área x custo_m2)
        considerando o número de unidades por chapa para ratear o custo do papelão entre as unidades produzidas por chapa. Se for corte conjugado (unidades_chapa > 1), o custo de papelão é dividido pelo número de unidades por chapa, caso contrário, o custo de papelão é integral para aquela unidade.
        """
        return  Decimal(str(self.chapa_utilizada.area_m2)) *  Decimal(str(self.chapa_utilizada.custo_m2))             


    @property
    def custo_tinta_padrao(self):
        """Retorna o custo de tinta para o template"""
        params = Custo_tinta.objects.first()
        return params.custo_tinta_unitario if params else Decimal('0.20')

    @property
    def custo_perda_unitario(self):
        return self.area_perda_projeto *  Decimal(str(self.chapa_utilizada.custo_m2))          

    @property
    def custo_total_unitario_fabricacao(self):
        """Soma de todos os custos reais (Material (perdas inclusas) + Máquinas"""
        return (self.custo_papelao_unitario +
                self.custo_tinta_padrao +
                self.custo_impressao +
                self.custo_corte +
                self.custo_seladora)

    @property
    def custo_total_fabricacao(self):
            # Convertendo para float uma única vez para limpar o código
        custo_total_papel = float(self.custo_papelao_total)    
        custo_total_tinta = float(self.custo_total_tinta)
        custo_imp = float(self.custo_impressao)
        custo_crt = float(self.custo_corte)
        custo_sel = float(self.custo_seladora)
        qtd = float(self.quantidade)
        unidades = float(self.unidades_chapa)
        
        # Lógica de cálculo separada por condição
        if unidades > 1:
            # Seu primeiro cenário quando unidades_chapa > 1
            return custo_total_papel + custo_total_tinta + (custo_imp * qtd / unidades) + (custo_crt * qtd * 2 / unidades) + (custo_sel * qtd)
        else:
            # Seu cenário alternativo (quando unidades_chapa <= 1)
            return custo_total_papel + custo_total_tinta + (custo_imp * qtd) + (custo_crt * qtd) + (custo_sel * qtd)
        
    @property
    def custo_total_fabricacao_porc(self):
        """Soma de todos os custos reais (Material (perdas inclusas) + Máquinas"""
        return (self.custo_total_fabricacao*100/self.custo_industrial_e_frete_sem_margem) if self.custo_papelao_total else Decimal('0.20')

    @property
    def custo_unitario_total_sem_margem(self):
        return (self.custo_papelao_unitario +
                self.custo_tinta_padrao +
                self.custo_impressao +
                self.custo_corte +
                self.custo_seladora +
                self.custo_frete_unitario)

    @property
    def custo_industrial_e_frete_sem_margem(self):
            # Convertendo para float uma única vez para limpar o código
        custo_total_papel = float(self.custo_papelao_total)    
        custo_total_tinta = float(self.custo_total_tinta)
        custo_imp = float(self.custo_impressao)
        custo_crt = float(self.custo_corte)
        custo_sel = float(self.custo_seladora)
        qtd = float(self.quantidade)
        unidades = float(self.unidades_chapa)
        custo_frete = float(self.custo_frete_unitario) * qtd    
        
        # Lógica de cálculo separada por condição
        if unidades > 1:
            # Seu primeiro cenário quando unidades_chapa > 1
            return custo_total_papel + custo_total_tinta + (custo_imp * qtd / unidades) + (custo_crt * qtd * 2 / unidades) + (custo_sel * qtd) + custo_frete
        else:
            # Seu cenário alternativo (quando unidades_chapa <= 1)
            return custo_total_papel + custo_total_tinta + (custo_imp * qtd) + (custo_crt * qtd) + (custo_sel * qtd) + custo_frete


    @property
    def preco_final_sem_nota_unitario(self):
        """Preço Final Unitário x Quantidade"""
        return self.preco_final_sem_nota / self.quantidade

    @property
    def preco_final_com_nota_unitario(self):
        """Preço Final Unitário x Quantidade"""
        return self.preco_final_com_nota / self.quantidade

    @property
    def soma_unitario_materiais(self):
        """Soma: Papelão + Perda + Tinta"""
        return float(self.custo_papelao_unitario) + float(self.custo_tinta_padrao)    
        # perda de papelão já está embutida no custo do papelao unitário, pois o custo do papelao é calculado considerando as perdas. Portanto, não é necessário somar a perda de papelão separadamente aqui.


    @property
    def custo_total_materiais(self):
        """Soma: Papelão + Perda + Tinta"""
        return float(self.custo_papelao_total) + float(self.custo_total_tinta)  # Formata o resultado como moeda brasileira


    @property
    def subtotal_processos_unitario(self):
        return self.custo_impressao + self.custo_corte + self.custo_seladora


    @property
    def custo_total_impressao(self):
        return float(self.custo_impressao) * float(self.quantidade)/float(self.unidades_chapa) if self.unidades_chapa > 1 else float(self.custo_impressao) * self.quantidade

    @property
    def custo_total_corte_vinco(self):
        return float(self.custo_corte) * float(self.quantidade) * 2 /float(self.unidades_chapa) if self.unidades_chapa > 1 else float(self.custo_corte) * self.quantidade

    @property
    def custo_total_seladora(self):
        return float(self.custo_seladora) * self.quantidade
    
    
    @property
    def custo_total_processos_fabricacao(self):
        # Convertendo para float uma única vez para limpar o código
        custo_imp = float(self.custo_impressao)
        custo_crt = float(self.custo_corte)
        custo_sel = float(self.custo_seladora)
        qtd = float(self.quantidade)
        unidades = float(self.unidades_chapa)

        # Lógica de cálculo separada por condição
        if unidades > 1:
            # Seu primeiro cenário quando unidades_chapa > 1
            return (custo_imp * qtd / unidades) + (custo_crt * qtd * 2 / unidades) + (custo_sel * qtd)
        else:
            # Seu cenário alternativo (quando unidades_chapa <= 1)
            return (custo_imp * qtd) + (custo_crt * qtd) + (custo_sel * qtd)

    @property
    def margem_percentual_display(self):
        """Garante que a margem apareça como 20 em vez de 0.20 no PDF"""
        return self.margem_real * 100 if self.margem_real < 1 else self.margem_real

    @property
    def total_impostos(self):
        """Soma de todos os custos (Materiais + Processos + Logística)"""
        return self.aliquota_imposto_aplicada if self.aliquota_imposto_aplicada > 0 else Decimal('0')


    @property
    def custo_total_com_margem(self):
        """Soma de todos os custos (Materiais + Processos + Logística)"""
        return float(self.custo_industrial_e_frete_sem_margem) * (float(1) + float(self.margem_real)/100) if self.margem_real >= 0 else float(self.custo_industrial_e_frete_sem_margem)               
    
    @property
    def lucro_por_unidade(self):
        """Soma de todos os custos (Materiais + Processos + Logística)"""
        return float(self.custo_total_com_margem) * (float(self.margem_real)/100)/float(self.quantidade) if self.margem_real > 0 and self.quantidade > 0 else Decimal('0')    
    
    @property
    def lucro(self):
        """margem_real x Quantidade"""
        return float(self.custo_total_com_margem) * (float(self.margem_real)/100)

    #-------------------------------------------------
    # PORCENTAGENS SOBRE CUSTO SEM MARGEM
    #-------------------------------------------------

    @property
    # Porcentagen custo do papelao sobre o custo sem margem
    def custo_papelao_unitario_porc(self):
        params = Custo_tinta.objects.first()
        return float(self.custo_papelao_total)*100/self.custo_industrial_e_frete_sem_margem if self.custo_papelao_total else Decimal('0.20')

    @property
    # Porcentagen da perda do projeto sobre o custo sem margem
    def custo_perda_projeto_porc(self):
        return float(self.custo_perda_total)* 100/self.custo_industrial_e_frete_sem_margem if self.custo_perda_projeto else Decimal('0.20')

    @property
    # Porcentagen custo da tinta sobre o custo sem margem
    def custo_tinta_padrao_porc(self):
        return float(self.custo_total_tinta)*100/self.custo_industrial_e_frete_sem_margem if self.custo_total_tinta else Decimal('0.20')

    @property
    # Porcentagen do custo de impressao sobre o custo sem margem
    def custo_impressao_impresso(self):
        return  float(self.custo_impressao) if self.custo_impressao else Decimal('0.20')

    @property
    # Porcentagen do custo de impressao sobre o custo sem margem
    def custo_impressao_porc(self):
        return float(self.custo_total_impressao)/float(self.custo_industrial_e_frete_sem_margem) * 100 if self.custo_total_impressao else Decimal('0.20')

    @property
    # Porcentagen do custo do corte e vinco sobre o custo sem margem
    def custo_corte_porc(self):
        return float(self.custo_total_corte_vinco)/float(self.custo_industrial_e_frete_sem_margem) * 100 if self.custo_total_corte_vinco  else Decimal('0.20')

    @property
    # Porcentagen do custo da seladora sobre o custo sem margem
    def custo_seladora_porc(self):
        return float(self.custo_seladora)/float(self.custo_industrial_e_frete_sem_margem) * 100 if self.custo_seladora else Decimal('0.20')

    @property
    # Porcentagen do custo_frete_unitario sobre o custo sem margem
    def custo_frete_porc(self):
        return float(self.custo_total_frete)/float(self.custo_industrial_e_frete_sem_margem) * 100 if self.custo_frete_unitario else Decimal('0.20')

    @property
    # BUG #1 CORRIGIDO: era (qtd / unidades_chapa), agora apenas qtd
    def custo_total_frete(self):
        return float(self.custo_frete_unitario) * self.quantidade

    @property
    # Porcentagen do subtotal_proc_industriais_porc sobre o custo sem margem
    def proc_industriais_porc(self):
                # Convertendo para float uma única vez para limpar o código
        custo_imp = float(self.custo_impressao)
        custo_crt = float(self.custo_corte)
        custo_sel = float(self.custo_seladora)
        qtd = float(self.quantidade)
        unidades = float(self.unidades_chapa)

        # Lógica de cálculo separada por condição
        if unidades > 1:
            # Seu primeiro cenário quando unidades_chapa > 1
            return ((custo_imp * qtd / unidades) + (custo_crt * qtd * 2 / unidades) + (custo_sel * qtd))/self.custo_industrial_e_frete_sem_margem * 100 if self.custo_frete_unitario else Decimal('0.20')
        else:
            # Seu cenário alternativo (quando unidades_chapa <= 1)
            return ((custo_imp * qtd) + (custo_crt * qtd) + (custo_sel * qtd))/self.custo_industrial_e_frete_sem_margem * 100 if self.custo_frete_unitario else Decimal('0.20')

    @property
    # Porcentagen do subtotal_proc_industriais_porc sobre o custo sem margem
    def subtotal_materiais_insumos_porc(self):
        return float(self.custo_total_materiais)*100/self.custo_industrial_e_frete_sem_margem if self.custo_total_materiais else Decimal('0.20')

    @property
    # Porcentagen do subtotal_proc_industriais_porc sobre o custo sem margem   custo_unitario_total_sem_margem
    def custo_total_sem_margem_porc(self):
        return (float(self.custo_industrial_e_frete_sem_margem) / float(self.custo_industrial_e_frete_sem_margem)) * 100
    
    @property
    def prolaboresocio(self):
        return self.prolabore_socio if self.prolabore_socio else Decimal(200.00)

    def resumo_composicao(self):
        if not self.preco_final_unitario:
            return "Salve para gerar o resumo."

        papelao = Decimal(str(self.chapa_utilizada.area_m2)) *  Decimal(str(self.chapa_utilizada.custo_m2))

        # Ajustei o cálculo da margem para ser o lucro bruto real
        lucro_bruto = self.preco_final_unitario - (papelao + Decimal('0.20') + self.custo_frete_unitario + self.custo_maquinas)

        return (
            f"📦 Papelão: R$ {papelao:.2f} | "
            f"♻️ Perda_papelão: R$ {self.custo_perda_total:.2f} | "
            f"🎨 Tinta: R$ 0.20 | "
            f"🖨️ Impressão: R$ {self.custo_impressao:.2f} | "
            f"✂️ Corte: R$ {self.custo_corte:.2f} | "
            f"🔥 Seladora: R$ {self.custo_seladora:.2f} | "
            f"🚚 Frete: R$ {self.custo_frete_unitario:.2f} | "
            f"💰 Custo_total_com_margem: R$ {(float(self.custo_total_com_margem)):.2f}"
            f"💰 Custo_industrial_e_frete_sem_margem: R$ {(float(self.custo_industrial_e_frete_sem_margem)):.2f}"
            f"💰 Custo_total_com_margem: R$ {(float(self.custo_total_com_margem)-float(self.custo_industrial_e_frete_sem_margem)):.2f}"
            f"💰 Preço Final (Sem Nota): R$ {(float(self.preco_final_sem_nota)):.2f}"
            f"💰 Preço Final Unitário(Sem Nota): R$ {(float(self.preco_final_sem_nota_unitario)):.2f}"
            f"💰 Preço Final (Com Nota): R$ {(float(self.preco_final_com_nota)):.2f}"
            f"💰 Preço Final Unitário(Com Nota): R$ {(float(self.preco_final_com_nota_unitario)):.2f}"
            f"💰 Prolabore Sócio: R$ {(float(self.prolabore_socio)):.2f}"
    )

    resumo_composicao.short_description = 'Detalhamento de Composição'

    
class ComissaoVenda(models.Model):
    vendedor = models.CharField(max_length=100, verbose_name="Nome do Vendedor")
    percentual_comissao = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Comissão (%)")
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'appOrcam_comissao_venda'
        verbose_name = "Comissão de Venda"
        verbose_name_plural = "Comissões de Vendas"

    def __str__(self):
        return f"{self.vendedor} - {self.percentual_comissao}%"
