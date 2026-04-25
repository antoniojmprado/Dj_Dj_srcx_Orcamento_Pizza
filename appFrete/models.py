from django.db import models

class DetalhesFrete(models.Model):
    # O Django cria o ID automaticamente
    data_hora = models.DateTimeField( auto_now_add=True, verbose_name="Data/Hora")
    cliente = models.CharField(max_length=200)
    cep_destino = models.CharField(max_length=9)
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


class TransportadorasFrete(models.Model):
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
