import os
import django
import pandas as pd
import sys

# 1. Configura o caminho do projeto para o Python encontrar os apps
sys.path.append('/var/www/joinvia/Dj_Dj_srcx_Orcamento_Pizza')

# 2. Define qual é o arquivo de configurações do seu projeto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prj_orcam.settings')

# 3. Inicializa o Django
django.setup()

# 4. AGORA SIM, importa os seus modelos
from appFrete.models import FreteEdne, TransportadoraFrete, EstadoCapitalBR

def importar_edne():
    print("Iniciando carga da EDNE (isso pode levar uns 2 minutos)...")
    path = '/var/www/joinvia/Dj_Dj_srcx_Orcamento_Pizza/appFrete/tab_bases/EDNE_CSV.csv'
    # Lendo o CSV em pedaços (chunks) para não estourar a memória RAM do servidor
    chunks = pd.read_csv(path, chunksize=10000, sep=',', encoding='utf-8')
    
    for chunk in chunks:
        objetos = [
            FreteEdne(
                cep=row['cep'],
                logradouro=row.get('logradouro'),
                complemento=row.get('complemento'),
                bairro=row.get('bairro'),
                municipio=row['municipio'],
                municipio_cod_ibge=row.get('municipio_cod_ibge'),
                uf=row['uf'],
                nome=row.get('nome')
            ) for index, row in chunk.iterrows()
        ]
        FreteEdne.objects.bulk_create(objetos)
    print("✅ EDNE importada com sucesso!")
    pass



def importar_transportadoras():
    print("Importando Tabela de Transportadoras...")
    path = './appFrete/tab_bases/NOVA_Tabela_fretes_transportadoras.xlsx'
    df = pd.read_excel(path, sheet_name='senhor_caixa')
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    print("Colunas normalizadas:", df.columns.tolist())
    
    objetos = [
        TransportadoraFrete(
            regiao=row['regiao'],
            transportadora=row['transportadora'],
            estado=row['estado'],
            estado_sigla=row['estado_sigla'],
            cem_kg=row['100_kg'],
            cento_cinquenta_kg=row['150_kg'],
            duzentos_kg=row['200_kg'],
            frete_peso=row['frete_peso'],
            fator_excedente=row['fator_excedente'],
            fator_sp_capital=row['fator_sp_capital'],
            seguro_risso=row['seguro_risso'],
            ad_valor=row['ad_valor'],
            ad_valor_min=row['ad_valor_min'],
            gris=row['gris'],
            gris_min=row['gris_min'],
            taxa_emb=row['taxaemb'],
            pedagio=row['pedagio'],
            tas=row['tas'],
            trt=row['trt'],
            suframa=row['suframa'],
            seguro_fluvial=row['seguro_fluvial'],
            fator_risso=row['fator_risso'],
            icms=row['icms'],
            tso=row['tso'],
            emex=row['emex'],
            tax_adm_fin=row['taxadmfin'],
            antt=row['antt'],
            prazo=row.get('prazo',0), # Se não achar 'prazo', assume 0
        ) for index, row in df.iterrows()
    ]
    TransportadoraFrete.objects.bulk_create(objetos)
    print("✅ Transportadoras importadas!")
    pass



def importar_estados():
    print("Importando Estados e Capitais...")
    path = './appFrete/tab_bases/estados_capitais_BR.xlsx'
    df = pd.read_excel(path)
    objetos = [
        EstadoCapitalBR(
            estado=row['estado'],
            uf=row['uf'],
            capital=row['capital'],
            regiao=row['regiao']
        ) for index, row in df.iterrows()
    ]
    EstadoCapitalBR.objects.bulk_create(objetos)
    print("✅ Estados importados!")
    pass

# 4. A função que ENGLOBA tudo (a "maestra")
def executar_carga_completa():
    print("Iniciando limpeza das tabelas...")
    EstadoCapitalBR.objects.all().delete()
    TabelaFreteTransportadora.objects.all().delete()
    FreteEdne.objects.all().delete()

    # Chama as outras funções na ordem certa
    importar_estados()
    importar_transportadoras()
    importar_edne() # Deixamos o mais pesado (1.4M de linhas) por último
    print("🚀 Tudo pronto!")

if __name__ == "__main__":
    # Limpar tabelas antes de importar para evitar duplicidade
    print("Limpando tabelas antigas...")
    FreteEdne.objects.all().delete()
    TransportadoraFrete.objects.all().delete()
    EstadoCapitalBR.objects.all().delete()
    
    importar_estados()
    importar_transportadoras()
    importar_edne()
    print("\n🚀 PROCESSO CONCLUÍDO! O banco está pronto.")
