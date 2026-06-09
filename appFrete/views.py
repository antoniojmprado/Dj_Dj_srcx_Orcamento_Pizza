
import math
import time
from urllib import request

from django.db import transaction
from django.http import HttpResponse
from .models import DetalhesFrete, TabelaFreteTransportadora, TransportadoraFrete, ItensFrete,EstadoCapitalBR, FreteEdne, LogTransportadora
from django.db.models import Count  # 1. Importação necessária
import os
import datetime
import locale
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

# Configuração de localidade para o Real brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')



def calcular_frete_view(request, pk=None): 
    tempo_inicio = time.time()
    print(f"\n>>> [DJANGO] Iniciou o cálculo do frete para o usuário {request.user}")   
    
    caminho_bases = os.path.join(settings.BASE_DIR, 'appFrete', 'tab_bases')
    agora = datetime.datetime.now().strftime("%d/%b/%Y %H:%M")
    
    # --- NOVO BLOCO: TRATAMENTO DE HISTÓRICO - DADOS QUE VÊM DO BANCO ---
    if pk:
        # Busca o frete salvo ou dá erro 404 se não existir
        frete_obj = get_object_or_404(DetalhesFrete, pk=pk)
        
        peso_cubado_bd = frete_obj.peso_cubado
        peso_informado_bd = frete_obj.peso_informado  
        total_unidades_bd = frete_obj.total_unidades
        icms = frete_obj.icms  
        
        print(f' total_unidades_bd {total_unidades_bd}')
        
        # Aqui, pegamos as transportadoras salvas vinculadas a esse frete
        # Supondo que você tenha um Relacionamento (ForeignKey) no seu modelo
        
        # related_name='transportadoras' em Models.py. Com esse 'related_name' - vide Models.py, o Django busca campos
        # tanto na tabela "appfrete_detalhesfrete" como tabela "appfrete_logtransportadora" que estão relacionadas pelo 
        # foreingkey que tem o related_name = 'transportadora'. Com isso pode-se fazer a busca 'reversa' já que este é o recurso para 
        # obterem-se os dados de ambas tabelas graças ao relacionamento feito na criação do modelo. 
        
        lista_resultados = frete_obj.transportadoras.all().order_by('frete_unidade') # transportadoras related_name em "class TabelaFreteTransportadora(models.Model)"
        
        # itens_frete = QuerySet
        itens_frete = frete_obj.itens.all() # itens related_name em "class ItensFrete(models.Model)"
        
        # agrupara numero de itens por frete_id, ou seja, contar quantos itens tem para cada frete_id. O resultado é uma lista de dicionários, onde cada dicionário tem o 'frete_id' e o 'num_itens' correspondente.            
        # O Count('id') conta o número de itens para cada frete_id, e o values('frete_id') agrupa os resultados por frete_id. O resultado é uma lista de dicionários, onde cada dicionário tem o 'frete_id' e o 'num_itens' correspondente.
        resultado = itens_frete.values('frete_id').annotate(num_itens=Count('id'))
  
        num_itens_frete = resultado[0]['num_itens'] if resultado else 0    
        
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
        
        context = {
            'pk': pk, # Importante para o HTML saber que é histórico
            'agora': frete_obj.data_hora.strftime("%d/%b/%Y %H:%M"),
            'cep': frete_obj.cep_destino,
            'cliente': frete_obj.cliente,
            'destino_cidade': frete_obj.cidade,
            'uf_coluna': frete_obj.uf_coluna,
            'logradouro': frete_obj.logradouro,
            'bairro': frete_obj.bairro,
            'vol_total': frete_obj.total_volume,
            'total_unidades_bd': total_unidades_bd,
            'total_pacotes': frete_obj.total_pacotes,
            'peso_cubado': frete_obj.peso_cubado,
            'valor_nf': frete_obj.valor_nf,
            'dados_frete': dados_combinados_frete,
            'peso_cubado_bd' : peso_cubado_bd,
            'peso_informado_bd' : peso_informado_bd,
            'tot_unidades_item' : tot_unidades_item,
            'num_itens_frete' : num_itens_frete, 
            'icms': icms,
            'res_list': lista_resultados
        }
        return render(request, 'appFrete/resultado_frete_novo.html', context)
    
    # --- FIM DO BLOCO DE HISTÓRICO  - DADOS QUE VÊM DO BANCO ---

    # ETAPA 1: GET - Apenas exibe o formulário inicial (CEP, Peso, Valor)
    if request.method == 'GET':
        return render(request, 'appFrete/index.html', {'agora': agora})

    # ETAPA 2: POST - Processamento (Destino ou Cálculo Final)
    if request.method == 'POST':
        # Dados base que persistem entre as telas
        cep_destino_raw = request.POST.get('cep_destino') or request.POST.get('cep')
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

        # Busca o destino diretamente no banco de dados (Muito mais rápido que o CSV!)
        try:
            # Limpamos o CEP para garantir que tenha apenas números
            cep_limpo = ''.join(filter(str.isdigit, str(cep_destino_raw)))
            
            # Se o CEP tem 8 dígitos e começa com 0, removemos o zero para a busca no MySQL
            cep_busca = cep_limpo.lstrip('0') if len(cep_limpo) == 8 else cep_limpo
            
            
            t_cep = time.time()
            # Buscamos no banco o primeiro registro que coincidir com o CEP
            destino = FreteEdne.objects.filter(cep=cep_busca).first()
            print(f">>> BUSCA CEP: {time.time() - t_cep:.4f}s") # Veja quanto tempo leva aqui
            
            if not destino:
                # Se não achar o CEP, você pode decidir o que fazer (ex: erro ou busca por município)
                print(f"CEP {cep_limpo} não encontrado na base EDNE.")
        
        except Exception as e:
            print(f"Erro ao buscar CEP no banco: {e}")
            destino = None

        if not destino:
            messages.error(request, f"CEP '{cep_destino_raw}' não encontrado!")
            return render(request, 'appFrete/index.html', {'agora': agora})

        if destino:
            destino_uf = destino.uf
            destino_cidade = destino.municipio
            logradouro_destino = destino.logradouro
            bairro_destino = destino.bairro
            # ... continue com sua lógica de cálculo de frete
        else:
            # Caso o CEP não exista no banco
            destino_cidade = "Não encontrada"
            destino_uf   = ""

        if logradouro_destino in ["", "NaN"]:
           logradouro_destino = "..."

        if bairro_destino in ["", "NaN"]:
           bairro_destino = "..."

        # Se não enviou as dimensões ainda, manda para a tela de dimensões (regiao.html)
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

            num_itens_calculados_frete = i + 1  # Para exibir no template
            
        print(f'num_itens_calculados_frete: {num_itens_calculados_frete} | total_unidades: {total_unidades} | vol_total_m3: {vol_total_m3:.2f} m³')
        
        # --- 3. Lógica Capital vs Interior (USANDO O BANCO) ---


        # Busca se a cidade é capital no banco
        capital_obj = EstadoCapitalBR.objects.filter(uf=destino_uf).first()
        cidade_capital = capital_obj.capital if capital_obj else ""
        
        # Define a string de busca (Ex: SP_CAPITAL ou SP_INTERIOR)
        uf_coluna = f"{destino_uf}_CAPITAL" if destino_cidade == cidade_capital else f"{destino_uf}_INTERIOR"

        # --- 4. Tabela de Transportadoras e Fórmulas (USANDO O BANCO) ---
        # Buscamos todas as transportadoras que atendem essa região
        transp_qs = TransportadoraFrete.objects.filter(estado=uf_coluna).only(
            'transportadora', 'regiao', 'antt', 'fator_excedente', 
            'ad_valor', 'gris', 'pedagio', 'frete_peso', 
            'cem_kg', 'taxa_emb', 'tas', 'icms'
        )
        
        resultados_frete = []
        # Pré-calculamos variáveis que são constantes no loop para poupar CPU
        valor_nf_float = float(valor_total_nf)
        kg_informado_float = float(kg_total_informado)

        for t in transp_qs:
            # CONVERSÃO ÚNICA: Transformamos os Decimais do banco em floats do Python
            # Isso evita que o Django tente validar o objeto Decimal em cada operação matemática
            antt = float(t.antt)
            fator_excedente = float(t.fator_excedente)
            ad_valor_taxa = float(t.ad_valor)
            gris_taxa = float(t.gris)
            pedagio_taxa = float(t.pedagio)
            frete_peso_taxa = float(t.frete_peso)
            cem_kg = float(t.cem_kg)
            taxa_emb = float(t.taxa_emb)
            tas = float(t.tas)
            icms_taxa = float(t.icms)

            # CÁLCULOS MATEMÁTICOS (Agora com floats puros, muito mais rápido)
            peso_cubado_calc = vol_total_m3 * antt
            peso_cubado_final = max(kg_informado_float, peso_cubado_calc)
            
            peso_excesso = max(0, peso_cubado_final - 100)
            valor_excesso = peso_excesso * fator_excedente
            ad_val_total = ad_valor_taxa * valor_nf_float
            gris_total = gris_taxa * valor_nf_float
            pedagio_total = math.ceil(peso_cubado_final / 100) * pedagio_taxa

            frete_net = (frete_peso_taxa * peso_cubado_final + valor_excesso + cem_kg + 
                        ad_val_total + gris_total + pedagio_total + taxa_emb + tas)

            frete_final = frete_net / (1 - icms_taxa)
            frete_unidade = frete_final / total_unidades

            resultados_frete.append({
                'transportadora': t.transportadora,
                'regiao': t.regiao,
                'frete_final': frete_final,
                'frete_unidade': frete_unidade,
            })

        # Ordenar por menor frete por unidade
        resultados_frete = sorted(resultados_frete, key=lambda x: x['frete_unidade'])
        
        context = {
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
            'num_itens_frete': num_itens_calculados_frete,
            'icms': t.icms*100,
            'res_list': resultados_frete 
        }
    
    t_save = time.time()
    # --- BLOCO DE SALVAMENTO NO BANCO DE DADOS ---
    # 1. BUSCA OTIMIZADA (Fora da transação)
    transp_qs = TransportadoraFrete.objects.filter(estado=uf_coluna).only(
        'transportadora', 'regiao', 'antt', 'fator_excedente', 
        'ad_valor', 'gris', 'pedagio', 'frete_peso', 
        'cem_kg', 'taxa_emb', 'tas', 'icms'
    )
    
    resultados_frete = []
    
    # Pré-calculamos variáveis que são constantes no loop para poupar CPU
    valor_nf_float = float(valor_total_nf)
    kg_informado_float = float(kg_total_informado)

    for t in transp_qs:
        # CONVERSÃO ÚNICA: Transformamos os Decimais do banco em floats do Python
        # Isso evita que o Django tente validar o objeto Decimal em cada operação matemática
        antt = float(t.antt)
        fator_excedente = float(t.fator_excedente)
        ad_valor_taxa = float(t.ad_valor)
        gris_taxa = float(t.gris)
        pedagio_taxa = float(t.pedagio)
        frete_peso_taxa = float(t.frete_peso)
        cem_kg = float(t.cem_kg)
        taxa_emb = float(t.taxa_emb)
        tas = float(t.tas)
        icms_taxa = float(t.icms)

        # CÁLCULOS MATEMÁTICOS (Agora com floats puros, muito mais rápido)
        peso_cubado_calc = vol_total_m3 * antt
        peso_cubado_final = max(kg_informado_float, peso_cubado_calc)
        
        peso_excesso = max(0, peso_cubado_final - 100)
        valor_excesso = peso_excesso * fator_excedente
        ad_val_total = ad_valor_taxa * valor_nf_float
        gris_total = gris_taxa * valor_nf_float
        pedagio_total = math.ceil(peso_cubado_final / 100) * pedagio_taxa

        frete_net = (frete_peso_taxa * peso_cubado_final + valor_excesso + cem_kg + 
                     ad_val_total + gris_total + pedagio_total + taxa_emb + tas)

        frete_final = frete_net / (1 - icms_taxa)
        frete_unidade = frete_final / total_unidades

        resultados_frete.append({
            'transportadora': t.transportadora,
            'regiao': t.regiao,
            'frete_final': frete_final,
            'frete_unidade': frete_unidade,
        })

    # 2. GRAVAÇÃO EM LOTE (Apenas agora abrimos o banco para escrita)
    try:
        with transaction.atomic():
            # 1. O Mestre (Usando o padrão que você tinha em 06 de maio)
            frete_master = DetalhesFrete.objects.create(
                cliente=cliente_destino,
                cep_destino=f"{cep_destino_raw[:5]}-{cep_destino_raw[5:]}",
                cidade=destino_cidade.upper(),
                uf_coluna=uf_coluna,
                logradouro=logradouro_destino.upper(),
                bairro=bairro_destino.upper(),
                total_volume=vol_total_m3,
                total_unidades=total_unidades,
                total_pacotes=total_pacotes,
                peso_informado=kg_total_informado,
                peso_cubado=peso_cubado_final,
                valor_nf=valor_total_nf,
                # Note: use o valor de ICMS que você calculou no loop ou uma variável fixa
                icms=icms_taxa * 100  # Convertendo para porcentagem para salvar no banco, se necessário
            )

            # 2. Itens (Ajuste para usar os campos corretos do seu modelo ItensFrete)
            objs_itens = [
                ItensFrete(
                    frete=frete_master,
                    comprimento=float(list_comps[i].replace(',', '.')),
                    largura=float(list_largs[i].replace(',', '.')),
                    altura=float(list_alts[i].replace(',', '.')),
                    qt_pacotes=int(list_vols[i]),
                    qt_unidades=int(list_unis[i]),
                    volume_item = (float(list_comps[i].replace(',', '.')) * 
                        float(list_largs[i].replace(',', '.')) * 
                        float(list_alts[i].replace(',', '.')) / 1000000) * float(list_vols[i])
                ) for i in range(len(list_comps))
            ]
            ItensFrete.objects.bulk_create(objs_itens)

            # 3. Transportadoras (Usando os resultados que guardamos na lista)
            objs_transp = [
                TabelaFreteTransportadora(
                    frete=frete_master,
                    nome_transportadora=item['transportadora'],
                    regiao=item['regiao'],
                    valor_frete=item['frete_final'],
                    frete_unidade=item['frete_unidade']
                ) for item in resultados_frete
            ]
            TabelaFreteTransportadora.objects.bulk_create(objs_transp, batch_size=50)
                    
    except Exception as e:
        print(f"ERRO DE SALVAMENTO DETALHADO: {e}") # Isso vai aparecer no journalctl
        import traceback
        traceback.print_exc() # Isso vai mostrar a linha exata do erro
        return HttpResponse(f"Erro técnico: {e}")
        
    tempo_fim = time.time()
    tempo_total = tempo_fim - tempo_inicio
    print(f">>> [DJANGO] Tempo gasto no servidor: {tempo_total:.4f} segundos", flush=True)
    
    return render(request, 'appFrete/resultado_frete_novo.html', context)

    # --- FIM DO SALVAMENTO ---    
                

def lista_fretes(request):
        '''
        Essa view é responsável por exibir a lista de fretes salvos, ordenados pela data de criação (do mais recente para o mais antigo).
        Ela utiliza o método prefetch_related para otimizar a consulta das transportadoras relacionadas a cada frete, 
        e o annotate para contar o número de itens relacionados a cada frete. 
        O resultado é passado para o template 'lista_fretes.html' para renderização.
        '''
    
        fretes = DetalhesFrete.objects.prefetch_related('transportadoras') \
            .annotate(num_itens=Count('itens')) \
            .all() \
            .order_by('-data_hora')
                
        return render(request, 'appFrete/lista_fretes.html', {'fretes': fretes})
