from django.db import models
from decimal import Decimal 

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
        managed = False # Isso diz ao Django para NÃO tentar criar ou alterar essa tabela, apenas ler os dados existentes.

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
        return f"Configuração: {self.maquina.nome}"


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
    cliente = models.CharField(max_length=255, db_index=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    produto_nome = models.CharField(max_length=100, default="Caixa de Pizza 35")
    quantidade = models.PositiveIntegerField()

    chapa_ideal = models.ForeignKey(Chapa, on_delete=models.PROTECT, related_name='ideal_set')
    chapa_utilizada = models.ForeignKey(Chapa, on_delete=models.PROTECT, related_name='real_set')

    maquina_impressao = models.ForeignKey(MaquinaOEE, on_delete=models.PROTECT, related_name='orcamentos_impressao')
    usou_corte_externo = models.BooleanField(default=False)
    maquina_corte = models.ForeignKey(MaquinaOEE, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos_corte')

    preco_final_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    perda_material = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    margem_real = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def calcular_custo_fixo_maquina(self):
        try:
            dados_oee = WaterfallOEE.objects.latest('id')
            total_cf = dados_oee.cust_fixo
            rateio = ConfiguracaoRateio.objects.get(maquina=self.maquina_impressao)

            # Soma os percentuais da máquina + extras (Century/Boca Sapo)
            perc_total = rateio.percentual_producao + rateio.percentual_century + rateio.percentual_boca_sapo

            return (perc_total / 100) * total_cf
        except:
            return 0
        
    custo_frete_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.30,
        verbose_name="Frete por Unidade"
    )
    

    def save(self, *args, **kwargs):
        # 1. BUSCA PARÂMETROS GLOBAIS
        # Pega o primeiro registro da tabela. Se não existir, usa 0.20 como padrão.
        params = Custo_tinta.objects.first()
        custo_tinta_unitario = params.custo_tinta_unitario if params else Decimal('0.20')
        
        param_frete = Custo_frete.objects.first()
        custo_frete_unitario = param_frete.custo_frete_unitario if param_frete else Decimal('0.30')

        # 2. CUSTO DO MATERIAL (Papelão + Tinta)
        custo_papelao_m2 = Decimal(str(self.chapa_utilizada.custo_m2))
        custo_material_unitario = self.chapa_utilizada.area_m2 * custo_papelao_m2 + custo_tinta_unitario

        # 3. CUSTO DE MÁQUINAS (Cálculo OEE)
        custo_maquinas = Decimal('0.00')
        
        # 4. PEGAMOS AS ÁREAS (certificando que são Decimais)
        area_utilizada = Decimal(str(self.chapa_utilizada.area_m2))
        area_ideal = Decimal(str(self.chapa_ideal.area_m2))
        custo_m2 = Decimal(str(self.chapa_utilizada.custo_m2))

        # 5. PERDA FINANCEIRA NA 'PROMOÇÃO DE CHAPA' (A sobra de papelão que você pagou e não usou)
        if area_utilizada > area_ideal:
            self.perda_material = (area_utilizada - area_ideal) * custo_m2
        else:
            self.perda_material = Decimal('0.00')
            
        print(f"DEBUG PERDA: Utilizada {area_utilizada} - Ideal {area_ideal} = Perda R$ {self.perda_material}")
        
        try:
            config = ConfiguracaoRateio.objects.get(maquina=self.maquina_impressao)
            velocidade = config.producao_un_hora if config.producao_un_hora > 0 else 1000
            tempo_unitario = Decimal(60) / Decimal(str(velocidade)) # tempo em minutos para produzir 1 unidade

            # Impressora e Seladora
            for m_id in [self.maquina_impressao.id, 11]:
                fin = MaquinaFinancasOEE.objects.filter(maquina_id=m_id).first()
                if fin:
                    custo_maquinas += (tempo_unitario * fin.custo_minuto)

            # Máquina de Corte Auxiliar (Century/Boca de Sapo)
            if self.maquina_corte:
                fin_corte = MaquinaFinancasOEE.objects.filter(maquina_id=self.maquina_corte.id).first()
                if fin_corte:
                    custo_maquinas += (tempo_unitario * fin_corte.custo_minuto)
        except Exception as e:
            print(f"Erro no tempo: {e}")

            # 4. PREÇO FINAL E MARGEM
        custo_total = Decimal(str(custo_material_unitario)) + custo_maquinas + custo_frete_unitario
        margem = self.margem_real if self.margem_real >= 1 else self.margem_real * 100
        fator_margem = (Decimal(100) - Decimal(str(margem))) / Decimal(100)

        if fator_margem > 0:
            self.preco_final_unitario = custo_total / fator_margem
        else:
            self.preco_final_unitario = custo_total * Decimal('1.30')

        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.cliente} - {self.produto_nome}"
    
    # Função para mostrar a composição do preço final no admin


    def resumo_composicao(self):
            if not self.preco_final_unitario:
                return "Salve o orçamento para gerar o resumo."

            # 1. Valores de custo
            papelao = Decimal(str(self.chapa_utilizada.area_m2)) * \
                            Decimal(str(self.chapa_utilizada.custo_m2))
            frete = self.custo_frete_unitario

            from appOrcam.models import Custo_tinta
            t_obj = Custo_tinta.objects.first()
            tinta = t_obj.custo_tinta_unitario if t_obj else Decimal('0.20')

            # 2. Cálculo do que sobra (Máquina + Margem)
            # Isso ajuda a ver o "peso" do lucro e da operação no preço de R$ 2,75
            outros_margem = self.preco_final_unitario - (papelao + tinta + frete)

            return (
                f"📦 Papelão: R$ {papelao:.2f} | "
                f"🎨 Tinta: R$ {tinta:.2f} | "
                f"🚚 Frete: R$ {frete:.2f} | "
                f"💰 Máquina + Margem: R$ {outros_margem:.2f}"
            )
    resumo_composicao.short_description = 'Detalhamento de Composição'
        
