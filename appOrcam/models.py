from django.db import connection, models
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.forms import CharField
from django.shortcuts import render
import appOEE
from appOEE.models import Maquina

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
    nome = models.CharField(max_length=100)
    largura_cm = models.DecimalField(max_digits=7, decimal_places=2)
    comprimento_cm = models.DecimalField(max_digits=7, decimal_places=2)
    tipo_papelao = models.CharField(max_length=50, default='Onda B')
    gramatura_kg_m2 = models.DecimalField( max_digits=7, decimal_places=2, default=0.45)
    custo_m2 = models.DecimalField(max_digits=10, decimal_places=2)
    estoque_disponivel = models.BooleanField(default=True)
    larg_apara_m = models.DecimalField(max_digits=7, decimal_places=2, default=0.01)
    preco_apara_kg = models.DecimalField(max_digits=7, decimal_places=2, default=0.8)
    medida_caixa_montada_cm = models.CharField(max_length=50, verbose_name="Medida Montada (cm)", default="0x0x0")
    unidades_chapa = models.PositiveIntegerField(default=1, verbose_name="Unidades por Chapa")
    explicacao_tecnica = models.CharField(max_length=255, blank=True, null=True)

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
        db_table = 'maquina'
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
    # A PK real da tabela é o campo 'id'
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
        db_table = 'appoee_maquinafinancas'


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
    custo_perda_total = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    custo_perda_projeto = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    custo_perda_excedente = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
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
                    nome_prod = self.produto_nome.lower()
                    if "kibe" in nome_prod:
                        self.categoria_produto_id = 3
                    elif "esfiha" in nome_prod:
                        self.categoria_produto_id = 2
                    else:
                        self.categoria_produto_id = 4

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
                
                if divisor < 1:
                    divisor = Decimal('1')
                if "pizza" in self.produto_nome.lower():
                    divisor = Decimal('1')

                # Cálculo do material unitário com rateio
                if divisor > 1:
                    self.custo_material_unitario = (area_utilizada * custo_m2_papelao) / divisor
                else:
                    self.custo_material_unitario = area_utilizada * custo_m2_papelao

                self.custo_material_unitario += self.custo_tinta_unitario

                # 2.1 CÁLCULO DINÂMICO DE PERDAS
                if self.chapa_utilizada:
                    custo_ref = Decimal(str(self.chapa_utilizada.custo_m2))
                    # ... (seus cálculos de área permanecem iguais)
                    self.area_total = Decimal(str(self.chapa_utilizada.largura_cm/100)) * Decimal(str(self.chapa_utilizada.comprimento_cm/100))
                    self.area_projeto_liquida = (Decimal(str(self.chapa_projeto.largura_cm/100)) - Decimal(str(self.chapa_projeto.larg_apara_m * 2))) * ((Decimal(str(self.chapa_projeto.comprimento_cm/100)) - Decimal(str(self.chapa_projeto.larg_apara_m * 2))))

                    self.area_perda_projeto = (Decimal(str(self.chapa_projeto.largura_cm/100)) * Decimal(str(self.chapa_projeto.larg_apara_m * 2))) + ((Decimal(str(self.chapa_projeto.comprimento_cm/100)) * Decimal(str(self.chapa_projeto.larg_apara_m * 2))))
                    
                    self.perda_area_total = self.area_total - self.area_projeto_liquida

                    self.perda_area_excedente = self.perda_area_total - self.area_perda_projeto 
                    
                    self.custo_perda_total = self.perda_area_total * custo_ref
                    
                    self.custo_perda_projeto = self.area_perda_projeto * custo_ref
                    
                    self.custo_perda_excedente = self.custo_perda_total - self.custo_perda_projeto
                            # (Mantive os campos principais para o cálculo final)

                try:
                    # --- CÁLCULO DE MÁQUINAS DINÂMICO ---
                    self.custo_impressao = Decimal('0.0000')
                    self.custo_corte = Decimal('0.0000')
                    self.custo_seladora = Decimal('0.0000')

                    # 1. IMPRESSÃO (DINÂMICA)
                    fin_impr = MaquinaFinancasOEE.objects.filter(maquina_id=self.maquina_impressao.id).first()
                    if fin_impr and fin_impr.producao_nominal_hora > 0:
                        tempo_unit = Decimal('60') / Decimal(str(fin_impr.producao_nominal_hora))

                        # Busca na View
                        cb_impr = MemoriaCalculoDinamica.objects.filter(maquina_id=self.maquina_impressao.id).first()
                        custo_min = Decimal(str(cb_impr.custo_minuto_real)) if cb_impr else 0.0

                        custo_base = tempo_unit * custo_min / divisor if divisor > 1 else tempo_unit * custo_min
                        quantidade_ajustada = Decimal(str(self.quantidade)) 
                        self.custo_impressao = custo_base * fin_impr.producao_nominal_hora / quantidade_ajustada

                    # 2. CORTE (DINÂMICA)
                    multiplicador = Decimal('2') if (self.categoria_produto_id == 1 and divisor > 1) else Decimal('1')

                    if self.maquina_corte:
                        fin_corte = MaquinaFinancasOEE.objects.filter(maquina_id=self.maquina_corte.id).first()
                        if fin_corte and fin_corte.producao_nominal_hora > 0:
                            tempo_unit = Decimal('60') / Decimal(str(fin_corte.producao_nominal_hora))

                            cb_corte = MemoriaCalculoDinamica.objects.filter(maquina_id=self.maquina_corte.id).first()
                            custo_min = Decimal(str(cb_corte.custo_minuto_real)) if cb_corte else Decimal(str(fin_corte.custo_minuto))

                            custo_base = tempo_unit * custo_min
                            self.custo_corte = (custo_base * multiplicador) * fin_corte.producao_nominal_hora / self.quantidade

                    # 3. SELADORA (DINÂMICA - ID 11)
                    fin_seladora = MaquinaFinancasOEE.objects.filter(maquina_id=11).first()
                    if fin_seladora and fin_seladora.producao_nominal_hora > 0:
                        tempo_unit = Decimal('60') / Decimal(str(fin_seladora.producao_nominal_hora))

                        cb_sela = MemoriaCalculoDinamica.objects.filter(maquina_id=11).first()
                        custo_min = Decimal(str(cb_sela.custo_minuto_real)) if cb_sela else Decimal(str(fin_seladora.custo_minuto))

                        custo_base = tempo_unit * custo_min
                        self.custo_seladora = (custo_base * multiplicador) * fin_seladora.producao_nominal_hora / self.quantidade

                    self.custo_maquinas = self.custo_impressao + self.custo_corte + self.custo_seladora

                    # 4. LOOP DA FÁBRICA (FLUXOS DE OPERAÇÃO DINÂMICOS)
                    fabrica = MaquinaFinancasOEE.objects.all()
                    maquinas_dict = {}

                    for maq in fabrica:
                        tempo_unit = Decimal('60') / Decimal(str(maq.producao_nominal_hora))

                        # Custo Dinâmico no Loop
                        cb_loop = MemoriaCalculoDinamica.objects.filter(maquina_id=maq.maquina_id).first()
                        custo_min_loop = Decimal(str(cb_loop.custo_minuto_real)) if cb_loop else Decimal(str(maq.custo_minuto))

                        custo_base = tempo_unit * custo_min_loop
                        custo_orcado = custo_base * Decimal(str(maq.producao_nominal_hora)) / self.quantidade

                        maquinas_dict[maq.maquina.nome.lower().replace(" ", "_")] = {
                            'custo': custo_orcado,
                            'tempo': tempo_unit * self.quantidade
                        }

                except Exception as e:
                    print(f"Erro máquinas: {e}")

                # 5. PREÇO FINAL
                custo_total_sem_margem = (self.custo_material_unitario +
                                        self.custo_impressao + self.custo_corte +
                                        self.custo_seladora + self.custo_frete_unitario)

                self.preco_final_unitario = custo_total_sem_margem * (Decimal('1') + (self.margem_real/100)) if self.margem_real > 0 else Decimal('0')
                
                print(f"Custo Total sem Margem: {custo_total_sem_margem}")
                print(f"Margem Real: {self.margem_real}%")
                print(f"Preço Final Unitário (sem nota): {self.preco_final_unitario}")

            # 1. Busca Impostos Ativos (Ex: 28,65%)
                from django.db.models import Sum
                total_impostos = Imposto.objects.filter(ativo_no_calculo=True).aggregate(Sum('aliquota'))['aliquota__sum'] or Decimal('0.00')
                
                self.aliquota_imposto_aplicada = total_impostos

                imposto_decimal = total_impostos / Decimal('100')

                margem_decimal = self.margem_real / Decimal('100')

                # 2. Cálculo SEM NOTA (Markup só com margem)
                denominador_sem = Decimal('1') - margem_decimal
                self.preco_final_sem_nota = custo_total_sem_margem / (denominador_sem if denominador_sem > 0 else Decimal('0.01'))

                # 3. Cálculo COM NOTA (Markup com margem + impostos)
                denominador_com = Decimal('1') - margem_decimal - imposto_decimal
                self.preco_final_com_nota = custo_total_sem_margem / (denominador_com if denominador_com > 0 else Decimal('0.01'))

                # 4. Mantém o preco_final_unitario baseado na escolha do usuário para o valor total
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
    def nome_maquina_impressao(self):
        """Retorna o nome da máquina"""
        return self.maquina_impressao.nome if self.maquina_impressao else ""

    @property
    def capac_impressao_nominal_hora(self):
        obj = MaquinaFinancasOEE.objects.get(maquina_id=self.maquina_impressao.id)
        return obj.producao_nominal_hora if obj.producao_nominal_hora else Decimal('0.20')

    @property
    def custo_minuto_impressora(self):
        cb_impr = MemoriaCalculoDinamica.objects.filter(maquina_id=self.maquina_impressao.id).first()
        return cb_impr.custo_minuto_real if cb_impr.custo_minuto_real else Decimal('0.86')

    @property
    def nome_maquina_corte(self):
        """Retorna o nome da máquina de corte"""
        return self.maquina_corte.nome if self.maquina_corte else ""

    @property
    def custo_minuto_corte(self):
        try:
            obj_maquina_corte = MemoriaCalculoDinamica.objects.get(maquina_id=self.maquina_corte.id)
            return obj_maquina_corte.custo_minuto_real if obj_maquina_corte.custo_minuto_real else Decimal('0.0')
        except:
            print("Erro: Não é possível mostrar o custo por minuto se não corte externo")

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
            # return f"{self.quantidade:,}".replace(',', '.') + " chapas (fundos e tampas)"

            qt_chapas = (self.quantidade / self.unidades_chapa) if self.unidades_chapa > 0 else self.quantidade
            # observacao = " Admitido que Fundos e Tampas são de chapas diferentes." if self.chapa_utilizada.unidades_chapa > 1 else ""
            return f" {qt_chapas:.0f} Tampas + " f"  {qt_chapas:.0f} Fundos - CORTE CONJUGADO: {self.unidades_chapa} unidades por chapa"
        else:
            qt_chapas = (
                self.quantidade / self.unidades_chapa) if self.unidades_chapa > 0 else self.quantidade
            return f"{qt_chapas:,.0f}".replace(',', '.') + " chapas(fundos + tampas)"

    @property
    def custo_papelao_unitario(self):
        """Calcula o custo base da chapa (área x custo_m2)
        considerando o número de unidades por chapa para ratear o custo do papelão entre as unidades produzidas por chapa. Se for corte conjugado (unidades_chapa > 1), o custo de papelão é dividido pelo número de unidades por chapa, caso contrário, o custo de papelão é integral para aquela unidade.
        """
        return self.custo_material_unitario - self.custo_tinta_padrao

    @property
    def custo_tinta_padrao(self):
        """Retorna o custo de tinta para o template"""
        params = Custo_tinta.objects.first()
        return params.custo_tinta_unitario if params else Decimal('0.20')

    @property
    def custo_total_fabricacao(self):
        """Soma de todos os custos reais (Material (perdas inclusas) + Máquinas"""
        return (self.custo_papelao_unitario +
                self.custo_tinta_padrao +
                self.custo_impressao +
                self.custo_corte +
                self.custo_seladora)

    @property
    def custo_total_sem_margem(self):
        """Soma de todos os custos reais (Material (perdas inclusas) + Máquinas + Frete)"""
        return (self.custo_papelao_unitario +
                self.custo_tinta_padrao +
                self.custo_impressao +
                self.custo_corte +
                self.custo_seladora +
                self.custo_frete_unitario)

    @property
    def valor_total_pedido_sem_nota(self):
        """Preço Final Unitário x Quantidade"""
        return self.preco_final_unitario * self.quantidade

    @property
    def valor_total_pedido_com_nota(self):
        """Preço Final Unitário x Quantidade"""
        return self.preco_final_com_nota * self.quantidade

    @property
    def subtotal_materiais(self):
        """Soma: Papelão + Perda + Tinta"""
        return self.custo_papelao_unitario + self.custo_tinta_padrao  # perda de papelão já está embutida no custo do papelao unitário, pois o custo do papelao é calculado considerando as perdas. Portanto, não é necessário somar a perda de papelão separadamente aqui.

    @property
    def subtotal_processos(self):
        """Soma: Impressão+ Seldora + Corte """
        return self.custo_impressao + self.custo_corte + self.custo_seladora

    @property
    def margem_percentual_display(self):
        """Garante que a margem apareça como 20 em vez de 0.20 no PDF"""
        return self.margem_real * 100 if self.margem_real < 1 else self.margem_real

    @property
    def margem_de_lucro(self):
        """Soma de todos os custos (Materiais + Processos + Logística)"""
        return self.custo_total_sem_margem / (Decimal('1') - self.margem_real/100) - self.custo_total_sem_margem if self.margem_real > 0 else Decimal('0')

    @property
    def total_impostos(self):
        """Soma de todos os custos (Materiais + Processos + Logística)"""
        return self.aliquota_imposto_aplicada if self.aliquota_imposto_aplicada > 0 else Decimal('0')

    @property
    def lucro(self):
        """margem_real x Quantidade"""
        return self.margem_de_lucro * self.quantidade

    @property
    def custo_total_com_margem(self):
        """Soma de todos os custos (Materiais + Processos + Logística)"""
        return self.custo_total_sem_margem * (Decimal('1') + (self.margem_real/100 if self.margem_real >= 0 else self.custo_total_sem_margem))

    # PORCENTAGENS SOBRE CUSTO SEM MARGEM

    @property
    # Porcentagen custo do papelao sobre o custo sem margem
    def custo_papelao_unitario_porc(self):
        params = Custo_tinta.objects.first()
        return self.custo_papelao_unitario*100/self.custo_total_sem_margem if params else Decimal('0.20')

    @property
    # Porcentagen da perda do projeto sobre o custo sem margem
    def custo_perda_projeto_porc(self):
        return (self.custo_perda_projeto + self.custo_perda_excedente) * 100/self.custo_total_sem_margem if self.custo_perda_projeto else Decimal('0.20')

    @property
    # Porcentagen custo da tinta sobre o custo sem margem
    def custo_tinta_padrao_porc(self):
        """Retorna o custo de tinta para o template"""
        params = Custo_tinta.objects.first()
        return params.custo_tinta_unitario*100/self.custo_total_sem_margem if params else Decimal('0.20')

    @property
    # Porcentagen do custo de impressao sobre o custo sem margem
    def custo_impressao_porc(self):
        return self.custo_impressao/self.custo_total_sem_margem * 100 if self.custo_impressao else Decimal('0.20')

    @property
    # Porcentagen do custo do corte e vinco sobre o custo sem margem
    def custo_corte_vinco_porc(self):
        return self.custo_corte/self.custo_total_sem_margem * 100 if self.custo_corte else Decimal('0.20')

    @property
    # Porcentagen do custo da seladora sobre o custo sem margem
    def custo_seladora_porc(self):
        return self.custo_seladora/self.custo_total_sem_margem * 100 if self.custo_seladora else Decimal('0.20')

    @property
    # Porcentagen do custo_frete_unitario sobre o custo sem margem
    def custo_frete_unitario_porc(self):
        return self.custo_frete_unitario/self.custo_total_sem_margem * 100 if self.custo_frete_unitario else Decimal('0.20')

    @property
    # Porcentagen do subtotal_proc_industriais_porc sobre o custo sem margem
    def subtotal_proc_industriais_porc(self):
        return (self.custo_impressao_porc + self.custo_corte_vinco_porc + self.custo_seladora_porc)

    @property
    # Porcentagen do subtotal_proc_industriais_porc sobre o custo sem margem
    def subtotal_materiais_insumos_porc(self):
        return (self.custo_papelao_unitario + self.custo_tinta_padrao) * 100/self.custo_total_sem_margem if self.custo_total_sem_margem else Decimal('0.20')

    @property
    # Porcentagen do subtotal_proc_industriais_porc sobre o custo sem margem
    def custo_total_sem_margem_porc(self):
        return (self.custo_total_sem_margem / self.custo_total_sem_margem) * 100

    def resumo_composicao(self):
        if not self.preco_final_unitario:
            return "Salve para gerar o resumo."

        papelao = Decimal(str(self.chapa_utilizada.area_m2)) * \
            Decimal(str(self.chapa_utilizada.custo_m2))

        # Ajustei o cálculo da margem para ser o lucro bruto real
        lucro_bruto = self.preco_final_unitario - (papelao + Decimal('0.20') +
                                                   self.custo_frete_unitario + self.custo_maquinas)

        return (
            f"📦 Papelão: R$ {papelao:.2f} | "
            f"♻️ Perda_papelão: R$ {self.custo_perda_total:.2f} | "
            f"🎨 Tinta: R$ 0.20 | "
            f"🖨️ Impressão: R$ {self.custo_impressao:.2f} | "
            f"✂️ Corte: R$ {self.custo_corte:.2f} | "
            f"🔥 Seladora: R$ {self.custo_seladora:.2f} | "
            f"🚚 Frete: R$ {self.custo_frete_unitario:.2f} | "
            f"💰 Margem Bruta: R$ {(self.custo_total_com_margem-self.custo_total_sem_margem):.2f}"
        )

    resumo_composicao.short_description = 'Detalhamento de Composição'
