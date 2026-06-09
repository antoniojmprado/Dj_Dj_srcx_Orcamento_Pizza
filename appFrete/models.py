from django.db import models

class DetalhesFrete(models.Model):
    # O Django cria o ID automaticamente
    data_hora = models.DateTimeField( auto_now_add=True, verbose_name="Data/Hora")
    cliente = models.CharField(max_length=200)
    cep_destino = models.CharField(max_length=10, db_index=True)
    cidade = models.CharField(max_length=100)
    uf_coluna = models.CharField(max_length=150,  blank=True, null=True)
    logradouro = models.CharField(max_length=255)
    bairro = models.CharField(max_length=100)
    peso_informado = models.DecimalField(max_digits=10, decimal_places=3)
    peso_cubado = models.DecimalField(max_digits=10, decimal_places=3)
    valor_nf = models.DecimalField(max_digits=12, decimal_places=2)
    total_pacotes = models.IntegerField()
    total_unidades = models.IntegerField()
    total_volume = models.DecimalField(max_digits=10, decimal_places=4)
    icms = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.cliente} - {self.data_hora.strftime('%d/%m/%Y')}"


class ItensFrete(models.Model):
    # Relacionamento com a tabela principal
    frete = models.ForeignKey(DetalhesFrete, on_delete=models.CASCADE, related_name='itens')
    comprimento = models.DecimalField(max_digits=10, decimal_places=2)
    largura = models.DecimalField(max_digits=10, decimal_places=2)
    altura = models.DecimalField(max_digits=10, decimal_places=2)
    qt_pacotes = models.IntegerField()
    qt_unidades = models.IntegerField()
    volume_item = models.DecimalField(max_digits=10, decimal_places=4)


class TabelaFreteTransportadora(models.Model):
    # Relacionamento com a tabela principal
    frete = models.ForeignKey( DetalhesFrete, on_delete=models.CASCADE, related_name='transportadoras')
    nome_transportadora = models.CharField(max_length=150)
    regiao = models.CharField(max_length=100)
    valor_frete = models.DecimalField(max_digits=12, decimal_places=2)
    frete_unidade = models.DecimalField(max_digits=12, decimal_places=2)

# Tabela de Log para Alterações (Opcional, mas recomendado)


class LogTransportadora(models.Model):
    data_alteracao = models.DateTimeField(auto_now_add=True)
    frete_id = models.IntegerField()
    transportadora_nome = models.CharField(max_length=150)
    valor_antigo = models.DecimalField(max_digits=12, decimal_places=2)
    valor_novo = models.DecimalField(max_digits=12, decimal_places=2)
    usuario = models.CharField(max_length=100)  # Se você usar sistema de login
    

# 1. Tabela EDNE (Fiel aos seus campos - 1.4M de linhas)
class FreteEdne(models.Model):
    cep = models.CharField(max_length=9, db_index=True)
    logradouro = models.CharField(max_length=255, null=True, blank=True)
    complemento = models.CharField(max_length=255, null=True, blank=True)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    municipio = models.CharField(max_length=100, db_index=True)
    municipio_cod_ibge = models.CharField(max_length=20, null=True, blank=True)
    uf = models.CharField(max_length=2, db_index=True)
    nome = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'app_frete_edne'


# 3. Tabela Estados e Capitais
class EstadoCapitalBR(models.Model):
    estado = models.CharField(max_length=50)
    uf = models.CharField(max_length=2, db_index=True)
    capital = models.CharField(max_length=100)
    regiao = models.CharField(max_length=50)    
    
    
 # Tabela vinda da Planilha (Nome alterado para evitar conflito)


class TransportadoraFrete(models.Model):
    regiao = models.CharField(max_length=50)
    transportadora = models.CharField(max_length=100, db_index=True)
    estado = models.CharField(max_length=50)
    estado_sigla = models.CharField(max_length=2, db_index=True)
    
    # Use 'verbose_name' para manter a referência ao nome da planilha sem quebrar o Python
    cem_kg = models.DecimalField("100_kg", max_digits=10, decimal_places=2, default=0)
    cento_cinquenta_kg = models.DecimalField("150_kg", max_digits=10, decimal_places=2, default=0)
    duzentos_kg = models.DecimalField("200_kg", max_digits=10, decimal_places=2, default=0)
    
    frete_peso = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fator_excedente = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fator_sp_capital = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    seguro_risso = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ad_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ad_valor_min = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gris = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gris_min = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxa_emb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pedagio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    trt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    suframa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    seguro_fluvial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fator_risso = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    icms = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tso = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    emex = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_adm_fin = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    antt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prazo = models.IntegerField(null=True, blank=True)   
    
     

#### CONCEITO related_name ####
'''
Essa é uma excelente pergunta! O conceito de relacionamento reverso realmente não é óbvio no início, mas depois que você entende, ele vira uma ferramenta poderosa no Django.

Pense no related_name como o "caminho de volta".

O Conceito
Quando você cria uma ForeignKey na tabela ItensFrete apontando para DetalhesFrete, o Django entende facilmente que cada item pertence a um frete.

Mas e se você estiver com um objeto de Frete na mão e quiser saber todos os itens que pertencem a ele? É aí que entra o related_name.

Por que isso é útil para o seu projeto?
Na sua página result_transps.html, você não vai precisar passar para o template uma lista de itens e uma lista de transportadoras separadas. Você passará apenas o objeto frete - vide os {% for ... } a seguir.

Lá no HTML, você poderá fazer isso:

→ frete.itens = itens na tabela 'ItensFrete' relacionados ao id em 'DetalhesFrete', lembrando que na tabela 'ItensFrete', o campo 'frete' é ForeignKey da tabela 'DetalhesFrete'.

{% for item in frete.itens.all %} 
   <p>{{ item.comprimento }} x {{ item.largura }}</p>
{% endfor %}

{% for transp in frete.transportadoras.all %}
   <p>{{ transp.nome_transportadora }}: R$ {{ transp.valor_frete }}</p>
{% endfor %}
'''
