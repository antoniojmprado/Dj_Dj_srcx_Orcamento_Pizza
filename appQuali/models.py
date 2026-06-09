from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timedelta




class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Empresa(models.Model):
    empresa = models.CharField(max_length=12)

    class Meta:
        managed = False
        db_table = 'empresa'


class Produtos(models.Model):
    produto = models.CharField(max_length=26)

    class Meta:
        managed = False
        db_table = 'produtos'


class Reclamacoes(models.Model):
     PRODUTOS_CHOICES = (
        (1, 'caixa de bolo'),
        (2, 'caixa de esfiha'),
        (3, 'caixa de pizza 25'),
        (4, 'caixa de pizza 30'),
        (5, 'caixa de pizza 35'),
        (6, 'caixa de pizza 40'),
        (7, 'caixa de pizza broto'),
        (8, 'caixa de vinho'),
        (9, 'fatia de pizza'),
        (10, 'maleta de vinho'),
        (11, 'sanduIche de pão por metro'),
        (12, 'embalagens especiais'),
        (13, 'embalagens de doces'),
        (14, 'caixa de torta'),
        (15, 'pizza media 18'),
        (16, 'embalagens de salgados'),
        (15, 'pizza media 18'),
        (16, 'embalagens de salgados'),
        (17, 'Tapetinho 24,5cm'),
        (18, 'Tapetinho 34,5cm'),
        (19, 'Tapetinho 39,5cm'),
    )
     
     DEFEITOS_CHOICE = (
        ( 1  , 'baixa resistência do papelão'),
        ( 2  , 'caixa avariada'),
        ( 3  , 'cheiro na embalagem'),
        ( 4  , 'desfolhamento do papelão'),
        ( 5  , 'embalagem com defeito'),
        ( 6  , 'entrega atrasada'),
        ( 7  , 'entrega incompleta'),
        ( 8  , 'impressão borrada _ tonalidade variando _ falha'),
        ( 9  , 'falta parte da tampa'),
        (10  , 'impressão fora de centro_esquadro'),
        (11  , 'lacre não cola _ fora de posição'),
        (12  , 'mistura de produtos'),
        (13  , 'rasgamento na dobra'),
        (14  , 'tampa redonda fora de medida'),
        (15  , 'trava ausente ou não encaixa'),
    )
     TECNOLOGIA_CHOICE = (
        (1, 'flexografia'),
        (2, 'OffSet'),
        (3, 'flexocromia w1'),
        (4, 'flexocromia w2'),
    )  
     
     EMPRESA_CHOICE = (
        (1, 'Senhor Caixa'),
        (2, 'Doutor Caixa'),
    )
     data_reclam = models.DateTimeField(auto_now_add=True)
     cliente = models.CharField(max_length=25)
     descricao = models.CharField(max_length=250)
     
     id_defeito = models.IntegerField(
         choices=DEFEITOS_CHOICE,
         default='impressão borrada _ tonalidade variando _ falha'
    )
     
     vendedora = models.CharField(max_length=12)
     
     id_produto = models.IntegerField(
        choices=PRODUTOS_CHOICES,
        default='caixa de pizza 35'
     )
     
     id_tecnol = models.IntegerField(
        choices=TECNOLOGIA_CHOICE,
        default='flexografia'
    )
     
     id_empresa = models.IntegerField(
        choices=EMPRESA_CHOICE,
        default='Senhor Caixa'
    )
    
     comentarios = models.CharField(max_length=193, blank=True, null=True)
     anexos = models.CharField(max_length=193, blank=True, null=True)
     data_atualiza = models.DateTimeField(auto_now=True, blank=True, null=True)

     class Meta:
        managed = False
        db_table = 'Reclamacoes'
        
     def __str__(self):
         return f" id {self.id} {self.cliente} - {self.descricao} em {self.data_reclam.strftime('%d/%m/%Y')}"

        



class Tecnologia(models.Model):
    id = models.IntegerField(primary_key=True)
    tecnologia = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'tecnologia'


class TiposDefeitos(models.Model):
    tipo_defeito = models.CharField(max_length=49)

    class Meta:
        managed = False
        db_table = 'tipos_defeitos'
        
# relacao 1 (reclamacoes) para N (reclamacoes_arquivo)
# por isso, ForeignKey em ReclamacoesArquivo apontando para Reclamacoes

class ReclamacoesArquivo(models.Model): # relacao 1 (reclamacoes) para N (reclamacoes_arquivo)
    itens = models.FileField('Arquivos / Anexos: ',
                             upload_to='itens', null=True, blank=True)
    reclamacoes = models.ForeignKey(
        Reclamacoes,
        related_name='arquivos',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reclamacoes.cliente
    
  
class SemanAno(models.Model):
    semana = models.PositiveIntegerField(
        null=False,
        blank=False,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(53)
        ],
        # Adding a helpful description
        help_text="O número da semana no ano (1-53)."
    )
    
    ano = models.PositiveIntegerField(
        null=False,
        blank=False, # Does not allow  the field to be optional in forms
        validators=[
        MinValueValidator(2025),
        MaxValueValidator(2100)
        ],
        #Adding a helpful description
        help_text="Ano de 2025 à 2100."
    )


    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    
    def clean(self):
        """
        Valida se a semana existe no ano informado
        """
        try:
            date.fromisocalendar(self.ano, self.semana, 2)
        except ValueError:
            raise ValidationError(
                f"A semana {self.semana} não existe no ano {self.ano}"
            )

    def calcular_datas(self):
        inicio = date.fromisocalendar(self.ano, self.semana, 1)
        fim = inicio + timedelta(days=6)

        self.data_inicio = inicio
        self.data_fim = fim
        
    def save(self, *args, **kwargs):

        self.full_clean()

        self.calcular_datas()

        super().save(*args, **kwargs)
        
        
