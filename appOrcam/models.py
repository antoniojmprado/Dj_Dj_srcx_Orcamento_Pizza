from django.db import models
from decimal import Decimal 
from django.core.validators import MinValueValidator
from django.forms import CharField
from appOEE.models import Maquina  # Importe o modelo correto

class Chapa(models.Model):
    nome = models.CharField(max_length=100)
    largura_cm = models.DecimalField(max_digits=7, decimal_places=2)
    comprimento_cm = models.DecimalField(max_digits=7, decimal_places=2)
    tipo_papelao = models.CharField(max_length=50, default='Onda B')
    custo_m2 = models.DecimalField(max_digits=10, decimal_places=2)
    estoque_disponivel = models.BooleanField(default=True)

    @property
    def area_m2(self):
        return (self.largura_cm * self.comprimento_cm) / 10000

    def __str__(self):
        return self.nome


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
        return self.nome or "Máquina sem nome"

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
    id = models.BigIntegerField(primary_key=True)
    maquina_id = models.BigIntegerField()
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


class ConfiguracaoRateio(models.Model): # participacao da maquina na producao total, para rateio do custo fixo do OEE
    maquina = models.OneToOneField(MaquinaOEE, on_delete=models.CASCADE)
    percentual_producao = models.DecimalField(max_digits=5, decimal_places=2, help_text="Ex: 70.00 para 70%")
    percentual_century = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentual_boca_sapo = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Adicionamos aqui os parâmetros que não existem na tabela 'maquina' original
    producao_un_hora = models.IntegerField(default=1000)
    custo_hora_operacional = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nome


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

        
class Orcamento(models.Model):
    # ... (seus campos iniciais permanecem iguais)
    cliente = models.CharField(max_length=255, db_index=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    produto_nome = models.CharField(max_length=100, default="Caixa de Pizza 35")
    quantidade = models.PositiveIntegerField()
    unidades_chapa = models.PositiveIntegerField(default=1, verbose_name="Unidades por Chapa")
    chapa_ideal = models.ForeignKey(Chapa, on_delete=models.PROTECT, related_name='ideal_set')
    chapa_utilizada = models.ForeignKey(Chapa, on_delete=models.PROTECT, related_name='real_set')
    maquina_impressao = models.ForeignKey(Maquina, on_delete=models.PROTECT, related_name='orcamentos_impressao')
    maquina_corte = models.ForeignKey(Maquina, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos_corte')

    # Campos de Custo (Decimal)
    custo_impressao = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    custo_corte = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    # Novo campo para o total de máquinas
    custo_maquinas = models.DecimalField( max_digits=10, decimal_places=4, default=0)
    custo_material_unitario = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    preco_final_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    perda_material = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    margem_real = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    custo_frete_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.30, verbose_name="Frete por Unidade")

    def save(self, *args, **kwargs):
        # 0. BUSCA PARÂMETROS GLOBAIS
        params = Custo_tinta.objects.first()
        custo_tinta_unitario = params.custo_tinta_unitario if params else Decimal(
            '0.20')

        # 1. CUSTO FRETE UNITÁRIO
        self.custo_frete_unitario = self.custo_frete_unitario if self.custo_frete_unitario > 0 else Decimal('0.30') 
        

        # 2. CUSTO DO MATERIAL (Papelão + Tinta)
        area_utilizada = Decimal(str(self.chapa_utilizada.area_m2))
        area_ideal = Decimal(str(self.chapa_ideal.area_m2))
        custo_m2_papelao = Decimal(str(self.chapa_utilizada.custo_m2))

        # custo_material_unitario = (area_utilizada * custo_m2_papelao) + custo_tinta_unitario
        # Para o custo de material unitário, consideramos o custo do papelão rateado pela quantidade de unidades por chapa (corte conjugado), ou integral se for corte simples. A tinta é adicionada integralmente por unidade, pois cada unidade leva a mesma quantidade de tinta independentemente do corte.
        # ADMITIDO QUE FUNDOS E TAMPAS SÃO DE CHAPAS DIFERENTES, ENTÃO O CUSTO DE PAPELÃO É CALCULADO PARA A CHAPA IMPRESSA MAIS UMA CHAPA NÃO IMPRESSA QUE SERÁ CORTADA PARA FAZER OS FUNDOS. SE FOR CORTE CONJUGADO (UNIDADES_CHAPA > 1), O CUSTO DE PAPELÃO É DIVIDIDO PELO NÚMERO DE UNIDADES POR CHAPA PARA OBTER O CUSTO UNITÁRIO DE PAPELÃO, CASO CONTRÁRIO, O CUSTO DE PAPELÃO É INTEGRAL PARA AQUELA UNIDADE.
        
        custo_material_unitario_parcial = ((area_utilizada * custo_m2_papelao * 2 )/self.unidades_chapa) if self.unidades_chapa > 1 else (area_utilizada * custo_m2_papelao)
        
        print(f"DEBUG: area_utilizada: {area_utilizada}, custo_m2_papelao: {custo_m2_papelao}, unidades_chapa: {self.unidades_chapa}, custo_material_unitario_parcial: {custo_material_unitario_parcial}")
        self.custo_material_unitario = custo_material_unitario_parcial + custo_tinta_unitario                

        # 3. PERDA FINANCEIRA
        if area_utilizada > area_ideal:
            self.perda_material = (area_utilizada - area_ideal) * custo_m2_papelao
        else:
            self.perda_material = Decimal('0.00')

        # 4. CUSTO DE MÁQUINAS (Cálculo OEE)
        self.custo_impressao = Decimal('0.0000')
        self.custo_corte = Decimal('0.0000')
        
        nome_maquina = self.maquina_impressao.nome if self.maquina_impressao else "N/A"
        print(f"DEBUG nome_maquina {nome_maquina} ")

        try:
            # Impressão + Seladora (ID 11)
            for m_id in [self.maquina_impressao.id, 11]: # roda todos os ids de máquinas de impressão, incluindo a seladora (ID 11)
                fin = MaquinaFinancasOEE.objects.filter(
                    maquina_id=m_id).first()
                if fin and fin.producao_nominal_hora > 0:
                    tempo_unit = Decimal('60') / Decimal(str(fin.producao_nominal_hora))
                    self.custo_impressao += tempo_unit * Decimal(str(fin.custo_minuto))   
                    print(f"DEBUG: Máquina ID {m_id} - Tempo Unitário: {tempo_unit} minutos, Custo Minuto: {fin.custo_minuto}, Custo Parcial Impressão: {self.custo_impressao}")

            # Corte
            if self.maquina_corte:
                fin_corte = MaquinaFinancasOEE.objects.filter(
                    maquina_id=self.maquina_corte.id).first()
                if fin_corte and fin_corte.producao_nominal_hora > 0:
                    tempo_corte = Decimal('60') / Decimal(str(fin_corte.producao_nominal_hora))
                    self.custo_corte = tempo_corte *  Decimal(str(fin_corte.custo_minuto))
                    print(f"DEBUG: Máquina Corte ID {self.maquina_corte.id} - Tempo Unitário: {tempo_corte} minutos, Custo Minuto: {fin_corte.custo_minuto}, Custo Parcial Corte: {self.custo_corte}")
                                    
            # Custo total de máquinas (impressão + corte) dividido por unidades por chapa, para obter o custo unitário de máquinas
            # considerando que o custo de máquina é rateado entre as unidades produzidas por chapa. A divisão só acontece se o numero de chapas for maior que 1, corte 'conjugado', caso contrário, o custo de máquina é integral para aquela unidade.
            
            # Nestes casos, a maquina de corte será utilizada 2 vezes. Uma para a tampa e outra para o fundo.
            ######### CORTE CONJUGADO  OU SIMPLES - SEMPRE MÁQUINAS WONDER 1 OU WONDER 2 ##########
            self.custo_maquinas = (self.custo_impressao / self.unidades_chapa + self.custo_corte * 2 / \
                self.unidades_chapa) if self.unidades_chapa > 1 else self.custo_impressao + self.custo_corte
            
            self.custo_impressao = self.custo_impressao / self.unidades_chapa if self.unidades_chapa > 1 else self.custo_impressao
            self.custo_corte = (self.custo_corte * 2) / self.unidades_chapa if self.unidades_chapa > 1 else self.custo_corte    
                
        except Exception as e:
            print(f"Erro máquinas: {e}")

        # 5. PREÇO FINAL COM MARGEM (Markup Inverso)
        # IMPORTANTE: Somamos todos os custos reais calculados
        custo_total_base = self.custo_material_unitario + self.custo_maquinas + self.perda_material + self.custo_frete_unitario
        print(f"DEBUG: custo_total_base: {custo_total_base}")
        margem = self.margem_real if self.margem_real >= 1 else self.margem_real * 100
        fator_margem = (Decimal('100') - Decimal(str(margem))) / Decimal('100')
        # return self.custo_total_sem_margem / (Decimal('1') - (self.margem_real/100 if self.margem_real >= 0 else self.custo_total_sem_margem))
       
        self.preco_final_unitario = custo_total_base / \
                (Decimal('1') - (self.margem_real/100 if self.margem_real >=
                 0 else self.custo_total_sem_margem))
                
        super().save(*args, **kwargs)
    '''
    Detalhe técnico: variáveis definidas dentro de um método (como papelao) não ficam disponíveis automaticamente no template HTML (PDF). O Django só enxerga o que é um campo do modelo ou um método/propriedade que ele possa chamar.

    Para que você possa usar esse valor no seu orcamento_pdf.html de forma limpa, sem precisar repetir o cálculo na View, a melhor estratégia é transformar esse cálculo em uma @property. Assim, você pode acessar {{ orcamento.custo_papelao_unitario }} diretamente no template, e o Django vai chamar a função para calcular o valor na hora. Isso mantém seu código organizado e evita duplicação de lógica.
    '''
    
    @property
    def nome_maquina_impressao(self):
        """Retorna o nome da máquina"""
        return self.maquina_impressao.nome if self.maquina_impressao else ""
    
    @property
    def nome_maquina_corte(self):
        """Retorna o nome da máquina de corte"""
        return self.maquina_corte.nome if self.maquina_corte else ""
    
    @property
    def nome_chapa_ideal(self):
        """Retorna o nome da máquina de corte"""
        return self.chapa_ideal if self.chapa_ideal else ""
    
    @property
    def nome_chapa_utilizada(self):
        """Retorna o nome da máquina de corte"""
        return self.chapa_utilizada if self.chapa_utilizada else self.chapa_ideal
    
    @property
    def total_chapas(self):
        """
        Calcula o total de chapas necessárias para produzir a quantidade desejada, considerando as unidades por
        chapas diferentes para tampas e fundos.
        Se unidades_chapa for 1 ou menos, assume-se que cada chapa é usada para uma unidade (tampa + fundo juntos).
        Se unidades_chapa for maior que 1, calcula-se o número de chapas considerando o corte conjugado, onde cada chapa pode produzir múltiplas unidades (tampas e fundos juntos ????)."""
        if self.unidades_chapa > 0 and self.unidades_chapa <= 1:  # 
            return f"{self.quantidade:,}".replace(',', '.') + " chapas (fundos e tampas)" 
        qt_chapas = (self.quantidade / self.unidades_chapa) if self.unidades_chapa > 1 else self.quantidade 
        # observacao = " Admitido que Fundos e Tampas são de chapas diferentes." if self.unidades_chapa > 1 else ""      
        return f" {qt_chapas:.0f} Tampas + " f"  {qt_chapas:.0f} Fundos - CORTE CONJUGADO: {self.unidades_chapa} unidades por chapa" if self.unidades_chapa > 1 else f"{qt_chapas:.0f} chapas (fundos + tampas)"
    
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
    def custo_total_sem_margem(self):
        """Soma de todos os custos reais (Material + Máquinas + Frete)"""
        return (self.custo_papelao_unitario +
                self.custo_tinta_padrao +
                self.perda_material +
                self.custo_maquinas +
                self.custo_frete_unitario)

    @property
    def valor_total_pedido(self):
        """Preço Final Unitário x Quantidade"""
        return self.preco_final_unitario * self.quantidade
    
    @property
    def subtotal_materiais(self):
        """Soma: Papelão + Perda + Tinta"""
        return self.custo_papelao_unitario + self.perda_material + self.custo_tinta_padrao

    @property
    def subtotal_processos(self):
        """Soma: Impressão+ Seldora + Corte """
        return self.custo_impressao + self.custo_corte

    @property
    def margem_percentual_display(self):
        """Garante que a margem apareça como 20 em vez de 0.20 no PDF"""
        return self.margem_real * 100 if self.margem_real < 1 else self.margem_real
    
    @property
    def custo_total_com_margem(self):
        """Soma de todos os custos (Materiais + Processos + Logística)"""
        return self.custo_total_sem_margem / (Decimal('1') - (self.margem_real/100 if self.margem_real >= 0 else self.custo_total_sem_margem))
    
    def resumo_composicao(self): 
        if not self.preco_final_unitario:
            return "Salve para gerar o resumo."
        
        papelao = Decimal(str(self.chapa_utilizada.area_m2)) * Decimal(str(self.chapa_utilizada.custo_m2))

        # Ajustei o cálculo da margem para ser o lucro bruto real
        lucro_bruto = self.preco_final_unitario - (papelao + Decimal('0.20') +
             self.custo_frete_unitario + self.custo_maquinas)

        return (
            f"📦 Papelão: R$ {papelao:.2f} | "
            f"🎨 Tinta: R$ 0.20 | "
            f"⚙️ Impressão: R$ {self.custo_impressao:.2f} | "
            f"✂️ Corte: R$ {self.custo_corte:.2f} | "
            f"🚚 Frete: R$ {self.custo_frete_unitario:.2f} | "
            f"💰 Margem Bruta: R$ {lucro_bruto:.2f}"
        )
    resumo_composicao.short_description = 'Detalhamento de Composição'
