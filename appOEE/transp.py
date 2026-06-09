from flask import Flask, render_template, request, flash, url_for
import pandas as pd
import numpy as np
import datetime
import locale
import winsound
from collections import OrderedDict
from collections import Counter

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

# importar tabelas
transp_df = pd.read_excel('tab_bases\\NOVA_Tabela_fretes_transportadoras.xlsx', 'senhor_caixa')
capitais_df = pd.read_excel('tab_bases\\estados_capitais_BR.xlsx')
cep_df = pd.read_csv("tab_bases\\EDNE_CSV.csv", sep=",")

transp_df = transp_df.rename(columns={'estado': 'cidade_uf'})
cep_df = cep_df.rename(columns={'municipio': 'cidade'})

xx = datetime.datetime.now()

agora = xx.strftime("%d/%b/%Y %H:%M")

app = Flask(__name__)

app.config['SECRET_KEY'] = 'd89719a64d369a7870a69f3994de658a'


@app.route("/")
def input_cep():
    return render_template('index.html', agora=agora)


@app.route("/destino", methods=['GET', 'POST'])
def destino_select():
    cep_destino = request.form.get('cep_destino')  # vindo de index.html

    kg_total = request.form.get('kg_total')  # vindo de index.html

    valor_total = request.form.get('valor_total')  # vindo de index.html

    destino = cep_df.loc[cep_df['cep'] == int(cep_destino)]

    # no caso de cep não encontrado do df 'destino' tem tamanho zero
    if len(destino) == 0:
        freq = 1550  # frequency is set to 500Hz
        dur = 80  # duration is set to 100 milliseconds
        winsound.Beep(freq, dur)
        flash(
            f" CEP '{cep_destino}' incorreto ou inexistente!!! Tente outra vez...")
        return render_template('index.html', agora=agora)

    # remocao de indices e DType
    destino_cep = destino['cep'].to_string(index=False, header=False)
    destino_logradouro = destino['logradouro'].to_string(index=False, header=False)
    destino_cidade = destino['cidade'].to_string(index=False, header=False)
    destino_bairro = destino['bairro'].to_string(index=False, header=False)
    destino_uf = destino['uf'].to_string(index=False, header=False)

    dic_prox_pag = {
        "cep_destino": f'{destino_cep}',
        "logradouro": f'{destino_logradouro}',
        "uf": f'{destino_uf}',
        "cidade": f'{destino_cidade}',
        "bairro": f'{destino_bairro}',
        "uf": f'{destino_uf}',
        "kg_total": kg_total,
        "valor_total": valor_total
    }

    ########## removendo duplicatas de lista #############################
    # https://awari.com.br/lista-python-remova-duplicatas-e-otimize-seu-codigo/#:~:text=Uma%20forma%20simples%20de%20remover,os%20elementos%20duplicados%20ser%C3%A3o%20removidos.
    ########## removendo duplicatas de lista #############################

    # list_produtos = list(OrderedDict.fromkeys(listar_produtos)) # removendo duplicatas

    return render_template('regiao.html', agora=agora, destino_cep=destino_cep, destino_logradouro=destino_logradouro, destino_bairro=destino_bairro,destino_cidade=destino_cidade, destino_uf=destino_uf, kg_total=kg_total, valor_total=valor_total, dic_prox_pag=dic_prox_pag)


@app.route("/calculadora", methods=['GET', 'POST'])
def calculadora():

    entradas = request.form  # vindo de regiao.html

    dados = request.form.to_dict(flat=False)  # vindo de regiao.html
    print('=a' * 100)
    print(dados)
    print(dados.keys())
    print(len(dados))
    print('a=' * 100)

    empty_keys = [k for k, v in dados.items() if not v]
    for k in empty_keys:
        del dados[k]

    vol_total = 0
    qt_caixas = 0
    total_unidades = 0
    vol_unit = []
    qt_unit = []
    multip_pacote = []

    # numero de linhas do dicionario 'dados'
    num_itens = len(dados['comprimento'])
    print(f' sou o numero de linha do dicionario {num_itens}')

    # cálculo do volume total em m3
    for i in range(num_itens):
        vol_i = float(dados['comprimento'][i]) * float(dados['largura'][i]) * \
            float(dados['altura'][i]) * float(dados['volume'][i])/1000000
        vol_unit.append(vol_i)  # forma lista dos volume m2 individuais

        # gera lista dos volume m3 individuais
        multip_pacote_i = (int(dados['unidades'][i]) * float(dados['volume'][i]))
        multip_pacote.append(multip_pacote_i)

    for numero in vol_unit:
        vol_total = vol_total + numero

    print(f' volume total agora {vol_total}')

    for multiplo in multip_pacote:
        total_unidades += multiplo
        total_unidades = int(total_unidades)

    print(f' total de unidades {total_unidades}')

    # cálculo da quantidade de volumes, leia-se pacotes ou embalagens
    for k in range(num_itens):
        qt_i = float(dados['volume'][k])
        qt_unit.append(qt_i)

    for q in qt_unit:
        qt_caixas = qt_caixas + q

    print(f' volume qt_caixas {qt_caixas}')

    nf = dados['valor_total']  # indice para valor tota

    cep_destino = dados['cep']   # indice para cidade

    cidade_selecionada = dados['cidade']  # indice para cidade

    destino_logradouro = dados['logradouro']  # indice para logradouro

    destino_bairro = dados['bairro']  # indice para bairro

    valor_total = dados['valor_total']  # indice para valor_total

    kg_total = dados['kg_total']  # indice para kg_total

    cidade_uf = entradas['uf']  # indice para uf

    print(f' sou cepdestino {cep_destino}')
    print("()" * 35)
    print(type(cep_destino[0]))

    # para encontrar os ceps da Gde SP que têm de possuir 1o digito = 0
    if len(cep_destino[0]) < 8:
        cepDestino = '0'+cep_destino[0]
    else:
        cepDestino = cep_destino[0]

    dic_prox_pag = {
        # no resultados.html estava como 'lista', por isso coloquei o indice [0]
        "cep_destino": f'{cep_destino[0]}',
        # no resultados.html estava como 'lista', por isso coloquei o indice [0]
        "logradouro": f'{destino_logradouro[0]}',
        # no resultados.html estava como 'lista', por isso coloquei o indice [0]
        "bairro": f'{destino_bairro[0]}',
        "uf": f'{cidade_uf}',
        # no resultados.html estava como 'lista', por isso coloquei o indice [0]
        "cidade": f'{cidade_selecionada[0]}',
        "kg_total": kg_total,
        "valor_total": valor_total
    }

    cidade_uf = cidade_uf.strip()

    print(f" sou a cidade UF {cidade_uf}")

    capital = capitais_df.loc[capitais_df['uf'] == f'{cidade_uf}']

    cidade_destino = capital['capital'].to_string(index=False, header=False)

    if cidade_selecionada[0] == cidade_destino:
        uf_coluna = cidade_uf+'_'+'CAPITAL'
    else:
        uf_coluna = cidade_uf+'_'+'INTERIOR'

    tab_transp = transp_df.loc[transp_df['cidade_uf'] == f'{uf_coluna}']

    print("%" * 100)
    print(tab_transp)
    
    ##### cálculo do peso cubado ##################
    
    # fator FSC
    fsc = 0

    peso_informado = entradas['kg_total']  # peso total
    valor_nf = entradas['valor_total']  # valor_nf
    
    print('@'*30)
    print(f'valor_nf {valor_nf}')
    print('@'*30)

    #### novas colunas no dataframe tab_transp que considera apenas as transportadoras necessarias
    
    tab_transp['volume_total_sem_cubar'] = vol_total # coluna volume total
    tab_transp['peso_cubado_calculado'] = vol_total * tab_transp['ANTT']  # coluna peso_cubado
    tab_transp['peso_informado'] = float(peso_informado)  # peso_informado
    tab_transp['dif_cub-informado'] = tab_transp['peso_cubado_calculado'] - tab_transp['peso_informado']

    # Comparação peso carga peso cubado https://www.youtube.com/watch?v=S4hPzAKxClo
    tab_transp['peso_cubado'] = np.where(tab_transp['dif_cub-informado'] < 0, tab_transp['peso_informado'], tab_transp['peso_cubado_calculado'])
    
    # cálculo do peso excedente
    tab_transp['peso_cubado_menos_100kg'] = tab_transp['peso_cubado'] - 100
    
    # Zerando pesos cubados < 0 correspondentes à QTD
    tab_transp['peso_excesso'] = np.where(tab_transp['peso_cubado_menos_100kg'] < 0, 0, tab_transp['peso_cubado_menos_100kg'])
    
    ################ CÁLCULOS DOS FATORES COMPONENTES DO CÁLCULO DE FRETE ################################################
    
    # Cálculo do fator "adValor_seguro"
    valor_nf = float(''.join(str(digit) for digit in nf))  # convert nf que era lista para inteiro
    tab_transp.loc[:, 'valor_nf'] = valor_nf
    
    # Coluna CEP destino 
    tab_transp.loc[:, 'CEP'] = dic_prox_pag['cep_destino']
    
    # Cálculo do valor mínimo considerado (SEMPRE) independentemente se peso de entrada for >=  ou < 100 kg
    tab_transp['val_min'] = tab_transp['100_kg']
    
    # Cálculo do fator "valor_excesso"
    tab_transp['valor_excesso'] = tab_transp['fator_excedente'] * \
        tab_transp["peso_excesso"]

    # Cálculo do "adValor_seguro"
    tab_transp.loc[:, 'adValor_seguro'] = tab_transp['ad_valor'] * valor_nf
    
    # Cálculo do adValor_minimo - desconsiderado para ficar igual ao sistema que está no ar
    # tab_transp.loc[:, 'adValor_seguro'] = np.where(tab_transp['adValor_seguro'] < tab_transp['ad_valor_min'], tab_transp['ad_valor_min'], tab_transp['adValor_seguro'])
    
    # Cálculo do frete_peso/seguro
    tab_transp.loc[:, 'fator_frete_peso'] = tab_transp['frete_peso'] * tab_transp['peso_cubado']

    # Cálculo do gris
    tab_transp.loc[:, 'gris_seguro'] = tab_transp['gris'] * valor_nf
    
    # Cálculo do gris_minimo - desconsiderado para ficar igual ao sistema que está no ar
    # tab_transp.loc[:, 'gris_seguro'] = np.where(tab_transp['gris_seguro'] < tab_transp['gris_min'], tab_transp['gris_min'], tab_transp['gris_seguro'])
    
    # Cálculo do seguro Risso
    tab_transp.loc[:, 'risso_seguro'] = tab_transp['seguro_risso'] * valor_nf
    
    # Cálculo do fator Risso
    tab_transp.loc[:, 'fator_risso'] = tab_transp['fator_risso'] *  tab_transp['peso_cubado']
    
    # Cálculo do fator pedágio  - RESOLVER QUESTÃO DO PEDÁGIO MÍNIMO
    tab_transp.loc[:, 'toll'] = tab_transp['pedagio'] * (tab_transp['peso_cubado']) / 100
    

    # Verificação do pedágio comparado ao valor mínimo aceitavel
    # Se coluna 'toll' = pedagio minimo. Se for > que pedagio calculado, então coluna pedagio = tab_transp['toll']
    tab_transp.loc[tab_transp['toll'] > tab_transp['pedagio'],'pedagio'] = tab_transp['toll']
    
    # Coluna Despacho
    tab_transp.loc[:, 'tx_Despacho'] = tab_transp['taxaEmb']

    # Coluna Suframa
    tab_transp.loc[:, 'tx_Suframa'] = tab_transp['suframa']

    # Coluna tas
    tab_transp.loc[:, 'tx_tas'] = tab_transp['tas']

    # Coluna tab_transp
    tab_transp.loc[:, 'tx_tso'] = tab_transp['tso'] * valor_nf

    # Coluna emex
    tab_transp.loc[:, 'tx_emex'] = tab_transp['emex']

    # Coluna seguro fluvial
    tab_transp.loc[:, 'tx_fluvial'] = tab_transp['seguro_fluvial'] * valor_nf

    # Coluna seguro taxAdmFin
    tab_transp.loc[:, 'tx_AdmFin'] = tab_transp['taxAdmFin']
    
    # FRETE SEM ACRÉSCIMO
    tab_transp.loc[:, 'frete_sem_acresc'] = tab_transp.loc[:, 'frete_sem_acresc'] = tab_transp['val_min'] + tab_transp['valor_excesso'] + tab_transp['adValor_seguro'] + tab_transp['fator_frete_peso'] + tab_transp['gris_seguro'] + \
        tab_transp['risso_seguro'] + tab_transp['fator_risso'] + tab_transp['toll'] + tab_transp['tx_Despacho'] + tab_transp['tx_Suframa'] + \
        tab_transp['tx_tas'] + tab_transp['tx_tso'] + tab_transp['emex'] + \
        tab_transp['tx_fluvial'] + tab_transp['tx_AdmFin']
        
    # ICMS
    tab_transp.loc[:, 'fat_icms'] = 1 -  tab_transp['icms']       

    # FRETE COM IMPOSTOS
    tab_transp.loc[:, 'frete_com_acresc'] = tab_transp['frete_sem_acresc'] / tab_transp['fat_icms']
    
    # UNIDADES
    tab_transp.loc[:, 'tot_unidades'] = total_unidades

    # FRETE COM IMPOSTOS por UNIDADE
    tab_transp.loc[:, 'frete_unidade'] = tab_transp['frete_com_acresc'] / total_unidades
    
    # ORDENA DA DATAFRAME tab_transp por 'frete_unidade' DECRESCENTE
    tab_transp = tab_transp.sort_values(by='frete_unidade', ascending=True)
    
    print(tab_transp)

    peso_cubado = tab_transp['peso_cubado'].to_list() # para pegar separadamente o valor do peso cubado
    cubado_kg = peso_cubado[0]
    
    peso_informado = tab_transp['peso_informado'].to_list() # para pegar separadamente o valor do peso_informado
    peso_informado = peso_informado[0]
    
    tx_icms = tab_transp['icms'].to_list() # para pegar separadamente o valor do peso cubado
    tx_icms = tx_icms[0] * 100
    tx_icms = '{:_.0f}'.format(tx_icms).replace('_', '.')
    
    # CRIA DICIONARIO A PARTIR DO DATAFRAME tab_transp CRIANDO UMA LISTA      
    dict_transp = tab_transp.to_dict('list')
   
    df = dict(list(dados.items())[:5]) # PEGA A PRIMEIRAS 5 COLUNAS
    
    dados_first_5 = pd.DataFrame(df)
    
    num_transp = len(tab_transp)

    tab_transp_resumo = tab_transp.drop(columns=['100_kg', '150_kg', '200_kg', 'frete_peso', 'fator_excedente', 'fator_SP_capital', 'peso_excesso','dif_cub-informado', 'seguro_risso', 'ad_valor', 'ad_valor_min', 'gris', 'gris_min','taxaEmb', 'pedagio', 'tas', 'trt', 'suframa', 'seguro_fluvial', 'fator_risso', 'estado_sigla', 'icms', 'tso', 'emex', 'taxAdmFin', 'volume_total_sem_cubar', 'peso_cubado_calculado', 'peso_cubado_menos_100kg'])
    
    # TRANSPOR TABELA
    tab_transp_resumo = tab_transp_resumo.T
    
    
    colunas_salvar_excel = ['CEP','regiao', 'transportadora', 'cidade_uf', 'ANTT', 'peso_informado',
                            'peso_cubado',  'valor_nf', 'valor_excesso','val_min', 'adValor_seguro',
                            'fator_frete_peso', 'gris_seguro', 'risso_seguro', 'toll',
                            'tx_Despacho', 'tx_Suframa', 'tx_tas', 'tx_tso', 'tx_emex',
                            'tx_fluvial', 'tx_AdmFin', 'frete_sem_acresc', 'fat_icms',
                            'frete_com_acresc', 'tot_unidades', 'frete_unidade']

    # PREPARAR DADOS PARA IMPRESSÃO
    
    # CRIA ARQUIVO PARA SALVAR EM EXCEL    
    tab_transp_resumo.to_excel(f"resultados\\Fretes calculados para_{cep_destino}.xlsx" )

    # tab_transp.columns
    print(tab_transp_resumo.columns)
    print(colunas_salvar_excel)

    return render_template('result_transps.html', uf_coluna=uf_coluna, agora=agora, num_transp=num_transp, dict_transp=dict_transp, dic_prox_pag=dic_prox_pag,  dados_first_5=dados_first_5, multip_pacote=multip_pacote,  num_itens=num_itens, qt_caixas=qt_caixas, total_unidades=total_unidades, peso_informado=peso_informado, cubado_kg=cubado_kg, vol_total=vol_total, tx_icms=tx_icms)


if __name__ == '__main__':
    app.run(debug=True)


