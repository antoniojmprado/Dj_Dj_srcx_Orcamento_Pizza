import os
import pandas as pd
import numpy as np
import datetime
import locale
from decimal import Decimal
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

# Configuração de localidade para o Real brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')


#@login_required
def calcular_frete_view(request):
    caminho_bases = os.path.join(settings.BASE_DIR, 'appFrete', 'tab_bases')
    agora = datetime.datetime.now().strftime("%d/%b/%Y %H:%M")

    # ETAPA 1: GET - Apenas exibe o formulário inicial (CEP, Peso, Valor)
    if request.method == 'GET':
        return render(request, 'appFrete/index.html', {'agora': agora})

    # ETAPA 2: POST - Processamento (Destino ou Cálculo Final)
    if request.method == 'POST':
        # Dados base que persistem entre as telas
        cep_destino_raw = request.POST.get('cep_destino') or request.POST.get('cep')

        kg_total_raw = request.POST.get('kg_total', '0').replace(',', '.')
        valor_total_raw = request.POST.get('valor_total', '0').replace(',', '.')
        print(f'valor_total_raw: {valor_total_raw} | kg_total_raw: {kg_total_raw}')

        # Agora converte para float (que o Pandas adora)
        kg_total_informado = float(kg_total_raw)
        valor_total_nf = float(valor_total_raw)
        print(f'valor_total_nf: {valor_total_nf} | kg_total_informado: {kg_total_informado}')

        # Carregamento do EDNE para validar o destino
        cep_df = pd.read_csv(
            os.path.join(caminho_bases, 'EDNE_CSV.csv'),
            sep=",",
            low_memory=False,
            # Forçamos o CEP a ser sempre inteiro para evitar erros na busca
            dtype={'cep': int}
        )
        destino = cep_df.loc[cep_df['cep'] == int(cep_destino_raw)]

        if len(destino) == 0:
            messages.error(request, f"CEP '{cep_destino_raw}' não encontrado!")
            return render(request, 'appFrete/index.html', {'agora': agora})

        # Dados do destino
        destino_uf = destino['uf'].to_string(index=False, header=False).strip()
        destino_cidade = destino['municipio'].to_string(index=False, header=False).strip()
        logradouro_destino = destino['logradouro'].to_string(index=False, header=False).strip()  # Pode ser opcional

        # Se não enviou as dimensões ainda, manda para a tela de dimensões (regiao.html)
        if 'comprimento' not in request.POST:
            dic_prox_pag = {
                "cep": cep_destino_raw,
                "uf": destino_uf,
                "cidade": destino_cidade,
                "kg_total": kg_total_informado,
                "valor_total": valor_total_nf,
                "logradouro": logradouro_destino    
            }
            return render(request, 'appFrete/regiao.html', {'dic': dic_prox_pag, 'agora': agora})

        # --- SE CHEGOU AQUI, É O CÁLCULO FINAL (Vindo da regiao.html) ---

        # 1. Captura as listas do JavaScript
        list_comps = request.POST.getlist('comprimento')
        list_largs = request.POST.getlist('largura')
        list_alts = request.POST.getlist('altura')
        list_vols = request.POST.getlist('volume')  # Qtde pacotes
        list_unis = request.POST.getlist('unidades')  # Unidades por pacote

        # 2. Cálculo do Volume Total e Unidades Totais
        vol_total_m3 = 0
        total_unidades = 0
        total_pacotes = 0
        items = []  # Lista para armazenar as descrições de cada item para debug/logging 
        for i in range(len(list_comps)):
            # Dentro do seu loop de cálculo de volume:
            v_i = (float(list_comps[i].replace(',', '.')) * float(list_largs[i].replace(',', '.')) *
                float(list_alts[i].replace(',', '.')) / 1000000) * float(list_vols[i].replace(',', '.'))
            vol_total_m3 += v_i
            total_unidades += int(list_unis[i]) * int(list_vols[i])
            
            total_pacotes += int(list_vols[i])
            
            append_item = f"Item {i+1}: {list_comps[i]}x{list_largs[i]}x{list_alts[i]} cm -  {list_vols[i]} pacotes - Unid./Pacote: {list_unis[i]} -  Tot. Unid.: {int(list_unis[i]) * int(list_vols[i])} -  Volume Total: {v_i: .2f} m³"
            items.append(append_item)                
            
            item_i = f"Item {i+1}: {list_comps[i]}x{list_largs[i]}x{list_alts[i]} cm, Qtde: {list_vols[i]}, Unid./Pacote: {list_unis[i]}, Vol.Total: {v_i:.2f} m³"
            print(item_i)       
            
        # 3. Lógica Capital vs Interior
        capitais_df = pd.read_excel(os.path.join(caminho_bases, 'estados_capitais_BR.xlsx'))
        cidade_capital = capitais_df.loc[capitais_df['uf'] == destino_uf, 'capital'].to_string(index=False, header=False).strip()
        uf_coluna = f"{destino_uf}_CAPITAL" if destino_cidade == cidade_capital else f"{destino_uf}_INTERIOR"

        # 4. Tabela de Transportadoras e Fórmulas
        transp_df = pd.read_excel(os.path.join(caminho_bases, 'NOVA_Tabela_fretes_transportadoras.xlsx'), 'senhor_caixa')
        # Ajustado nome da coluna 'estado' conforme seu Excel
        tab_transp = transp_df.loc[transp_df['estado'] == uf_coluna].copy()

        # Cálculos de Peso Cubado (Lógica que você tinha no transp.py)
        tab_transp['peso_cubado_calc'] = vol_total_m3 * tab_transp['ANTT']
        tab_transp['peso_final'] = np.where(tab_transp['peso_cubado_calc'] < kg_total_informado, kg_total_informado, tab_transp['peso_cubado_calc'])
        
        peso_cubado_final = tab_transp['peso_final'].iloc[0]  # Pegando o peso final para exibir no template

        
        # Cálculo dos Componentes (Excesso, AdVal, Gris, etc.)
        tab_transp['peso_excesso'] = np.maximum(0, tab_transp['peso_final'] - 100)
        tab_transp['valor_excesso'] = tab_transp['peso_excesso'] * tab_transp['fator_excedente']
        tab_transp['ad_val_total'] = tab_transp['ad_valor'] * valor_total_nf
        tab_transp['gris_total'] = tab_transp['gris'] * valor_total_nf
        tab_transp['pedagio_total'] = np.ceil(tab_transp['peso_final']/100) * tab_transp['pedagio']

        # Frete Peso (Calculado sobre os 100kg iniciais ou peso total dependendo da sua regra)
        tab_transp['frete_min'] = tab_transp['100_kg']
        
        tab_transp['frete_peso_total'] = tab_transp['frete_peso'] * tab_transp['peso_final']
        

        # Soma do Frete sem Impostos
        tab_transp['frete_net'] = (
            tab_transp['frete_peso_total'] + tab_transp['valor_excesso'] + tab_transp['frete_min'] + tab_transp['ad_val_total'] +
            tab_transp['gris_total'] + tab_transp['pedagio_total'] +
            tab_transp['taxaEmb'] + tab_transp['tas']
        )

        # ICMS (Fazendo o Gross-up que você tinha)
        tab_transp['frete_final'] = tab_transp['frete_net'] / (1 - tab_transp['icms'])
        tab_transp['frete_unidade'] = tab_transp['frete_final'] / total_unidades

        # Ordenação
        tab_transp = tab_transp.sort_values(by='frete_unidade')

        # Preparação para o Template
        res_dict = tab_transp.to_dict('list')
        lista_resultados = zip(
            res_dict['transportadora'],
            res_dict['frete_final'],
            res_dict['frete_unidade'],
            res_dict['regiao'],
            res_dict['peso_final']
        )

        contexto = {
            'agora': agora,
            'cep': cep_destino_raw,
            'lista_resultados': lista_resultados,
            'destino_cidade': destino_cidade,                        
            'uf_coluna': uf_coluna,
            "logradouro": logradouro_destino,
            'vol_total': vol_total_m3,
            'total_unidades': total_unidades,
            'total_pacotes': total_pacotes,
            'peso_informado': kg_total_informado,
            'peso_cubado_final': peso_cubado_final,
            'valor_nf': valor_total_nf,                     
            'items': items  # Adicionando a lista de descrições dos itens para debug/logging
        }

        return render(request, 'appFrete/result_transps.html', contexto)
