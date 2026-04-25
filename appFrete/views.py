from django.db.models import Count  # 1. Importação necessária
import os
import pandas as pd
import numpy as np
import datetime
import locale
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

from appFrete.models import DetalhesFrete

# Configuração de localidade para o Real brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')


# @login_required
def calcular_frete_view(request, pk=None): 
    caminho_bases = os.path.join(settings.BASE_DIR, 'appFrete', 'tab_bases')
    agora = datetime.datetime.now().strftime("%d/%b/%Y %H:%M")
    
    # --- NOVO BLOCO: TRATAMENTO DE HISTÓRICO ---
    if pk:
        # Busca o frete salvo ou dá erro 404 se não existir
        frete_obj = get_object_or_404(DetalhesFrete, pk=pk)
        
        peso_cubado_bd = frete_obj.peso_cubado
        peso_informado_bd = frete_obj.peso_informado  
        total_unidades_bd = frete_obj.total_unidades  
        
        print(f' total_unidades_bd {total_unidades_bd}')
        
        # Aqui, pegamos as transportadoras salvas vinculadas a esse frete
        # Supondo que você tenha um Relacionamento (ForeignKey) no seu modelo
        
        # related_name='transportadoras' em Models.py. Com esse 'related_name' - vide Models.py, o Django busca campos
        # tanto na tabela "appfrete_detalhesfrete" como tabela "appfrete_logtransportadora" que estão relacionadas pelo 
        # foreingkey que tem o related_name = 'transportadora'. Com isso pode-se fazer a busca 'reversa' já que este é o recurso para 
        # obterem-se os dados de ambas tabelas graças ao relacionamento feito na criação do modelo. 
        
        lista_resultados = frete_obj.transportadoras.all().order_by('frete_unidade') # transportadoras related_name em "class TransportadorasFrete(models.Model)"
        
        itens_frete = frete_obj.itens.all() # itens related_name em "class ItensFrete(models.Model)"
        
        
        resultado = itens_frete.values('frete_id').annotate(num_itens=Count('id'))
        for item in resultado:
            print(f"Frete ID: {item['frete_id']}, Número de Itens: {item['num_itens']}")    
        
        qt_itens = len(itens_frete)
        range_itens = range(qt_itens)
        print(f' qt_itens {range_itens}')
        
        tot_unidades_item = []
        volume_item = []
        for item in itens_frete:
            c = int(item.comprimento)
            l = int(item.largura)
            a = int(item.altura)
            
            pc = int(item.qt_pacotes)
            un = int(item.qt_unidades)
            tot_un_indiv = pc * un
            tot_unidades_item.append(tot_un_indiv)
            
            vol_item = ((c * l * a) / 1000000) * pc
            volume_item.append(vol_item)
            
        # Cria uma única lista combinada
        dados_combinados_frete = zip(itens_frete, tot_unidades_item, volume_item)
        
        contexto = {
            'pk': pk, # Importante para o HTML saber que é histórico
            'agora': frete_obj.data_hora.strftime("%d/%b/%Y %H:%M"),
            'cep': frete_obj.cep_destino,
            'cliente': frete_obj.cliente,
            'destino_cidade': frete_obj.cidade,
            'logradouro': frete_obj.logradouro,
            'bairro': frete_obj.bairro,
            'vol_total': frete_obj.total_volume,
            'total_unidades_bd': total_unidades_bd,
            'total_pacotes': frete_obj.total_pacotes,
            'peso_cubado': frete_obj.peso_cubado,
            'valor_nf': frete_obj.valor_nf,
            'lista_resultados': lista_resultados,
            'dados_frete': dados_combinados_frete,
            'peso_cubado_bd' : peso_cubado_bd,
            'peso_informado_bd' : peso_informado_bd,
            'tot_unidades_item' : tot_unidades_item
        }
        return render(request, 'appFrete/result_transps.html', contexto)
    # --- FIM DO BLOCO DE HISTÓRICO ---

    # ETAPA 1: GET - Apenas exibe o formulário inicial (CEP, Peso, Valor)
    if request.method == 'GET':
        return render(request, 'appFrete/index.html', {'agora': agora})

    # ETAPA 2: POST - Processamento (Destino ou Cálculo Final)
    if request.method == 'POST':
        # Dados base que persistem entre as telas
        cep_destino_raw = request.POST.get(
            'cep_destino') or request.POST.get('cep')
        # para remover hífen mostrado no campo em cep em regiao.html
        cep_destino_raw = cep_destino_raw.replace('-', '')

        cliente_destino = request.POST.get('cliente')
        cliente_destino = cliente_destino.upper()

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
        bairro_destino = destino['bairro'].to_string(index=False, header=False).strip()  # Pode ser opcional

        if logradouro_destino in ["", "NaN"]:
           logradouro_destino = "..."

        if bairro_destino in ["", "NaN"]:
           bairro_destino = "..."

        # Se não enviou as dimensões ainda, manda para a tela de dimensões (regiao.html)
        print(">>> O POST CHEGOU!")
        if 'comprimento' in request.POST:
            print(">>> COMPRIMENTO ENCONTRADO!")
        else:
            print(">>> COMPRIMENTO NÃO ENCONTRADO! Voltando para regiao.html")

            dic_prox_pag = {
                "cep": f"{cep_destino_raw[:5]}-{cep_destino_raw[5:]}",
                "cliente": cliente_destino.upper(),
                "uf": destino_uf,
                "cidade": destino_cidade.upper(),
                "logradouro": logradouro_destino.upper(),
                "bairro": bairro_destino.upper(),
                "kg_total": kg_total_informado,
                "valor_total": valor_total_nf,
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
        tab_transp['peso_final'] = np.where(
            tab_transp['peso_cubado_calc'] < kg_total_informado, kg_total_informado, tab_transp['peso_cubado_calc'])

        # Pegando o peso final para exibir no template
        peso_cubado_final = tab_transp['peso_final'].iloc[0]

        # Cálculo dos Componentes (Excesso, AdVal, Gris, etc.)
        tab_transp['peso_excesso'] = np.maximum(0, tab_transp['peso_final'] - 100)
        tab_transp['valor_excesso'] = tab_transp['peso_excesso'] *tab_transp['fator_excedente']
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
        tab_transp['frete_unidade'] = tab_transp['frete_final'] /  total_unidades
        
        icms = tab_transp['icms'].iloc[0]

        # Ordenação
        tab_transp = tab_transp.sort_values(by='frete_unidade')

        # --- LIMPEZA E ALINHAMENTO ---
        # Forçamos uma coluna nova com o nome da região (ex: SP_INTERIOR)
        # Isso garante que o segundo item do zip seja TEXTO, não número.
        tab_transp['regiao_display'] = tab_transp['regiao']

        # Transformamos em dicionário
        res_dict = tab_transp.to_dict('list')

        # O ZIP MÁGICO (Siga esta ordem exata)
        lista_resultados_dict = zip(
            res_dict['transportadora'], # 1º
            res_dict['regiao_display'],  # 2º (O texto que você quer!)
            res_dict['frete_final'],    # 3º
            res_dict['frete_unidade']   # 4º
        )
        
        contexto = {
            'agora': agora,
            'cep': f"{cep_destino_raw[:5]}-{cep_destino_raw[5:]}",
            "cliente": cliente_destino,
            'destino_cidade': destino_cidade.upper(),
            'uf_coluna': uf_coluna,
            "logradouro": logradouro_destino.upper(),
            "bairro": bairro_destino.upper(),
            'vol_total': vol_total_m3,
            'total_unidades': total_unidades,
            'total_pacotes': total_pacotes,
            'peso_informado': kg_total_informado,
            'peso_cubado_final': peso_cubado_final,
            'valor_nf': valor_total_nf,
            'items': items,
            'icms': icms*100,
            'lista_resultados_dict': lista_resultados_dict 
        }

        return render(request, 'appFrete/result_transps.html', contexto)
    
def lista_fretes(request):
        # O prefetch_related traz as transportadoras de uma vez só, poupando o banco de dados
        fretes = DetalhesFrete.objects.prefetch_related('transportadoras').all().order_by('-data_hora')
        return render(request, 'appFrete/lista_fretes.html', {'fretes': fretes})
