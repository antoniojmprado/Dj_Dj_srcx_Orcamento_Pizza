import math
from .models import FreteEdne, EstadoCapitalBR, TransportadoraFrete # Ajuste os imports conforme seu appFrete

def calcular_melhor_frete_interno(cep_destino, valor_nf, peso_informado, comp, larg, alt, qt_pacotes, unid_pacote):
    # 1. Limpeza e Busca do CEP (Igualzinho ao seu código)
    cep_limpo = ''.join(filter(str.isdigit, str(cep_destino)))
    cep_busca = cep_limpo.lstrip('0') if len(cep_limpo) == 8 else cep_limpo
    destino = FreteEdne.objects.filter(cep=cep_busca).first()
    
    if not destino:
        return 0.0 # CEP não encontrado
        
    # 2. Capital vs Interior
    capital_obj = EstadoCapitalBR.objects.filter(uf=destino.uf).first()
    cidade_capital = capital_obj.capital if capital_obj else ""
    uf_coluna = f"{destino.uf}_CAPITAL" if destino.municipio == cidade_capital else f"{destino.uf}_INTERIOR"

    # 3. Cálculo Físico
    vol_m3 = ((comp * larg * alt) / 1000000) * qt_pacotes
    total_unidades = qt_pacotes * unid_pacote

    # 4. Motor de Transportadoras (A sua otimização com floats puros)
    transp_qs = TransportadoraFrete.objects.filter(estado=uf_coluna).only(
        'transportadora', 'antt', 'fator_excedente', 'ad_valor', 'gris', 
        'pedagio', 'frete_peso', 'cem_kg', 'taxa_emb', 'tas', 'icms'
    )
    
    menor_frete_unitario = float('inf')

    for t in transp_qs:
        peso_cubado_calc = vol_m3 * float(t.antt)
        peso_cubado_final = max(peso_informado, peso_cubado_calc)
        
        peso_excesso = max(0, peso_cubado_final - 100)
        valor_excesso = peso_excesso * float(t.fator_excedente)
        ad_val_total = float(t.ad_valor) * valor_nf
        gris_total = float(t.gris) * valor_nf
        pedagio_total = math.ceil(peso_cubado_final / 100) * float(t.pedagio)

        frete_net = (float(t.frete_peso) * peso_cubado_final + valor_excesso + float(t.cem_kg) + 
                     ad_val_total + gris_total + pedagio_total + float(t.taxa_emb) + float(t.tas))

        frete_final = frete_net / (1 - float(t.icms))
        frete_unidade = frete_final / total_unidades

        # Guarda sempre o frete mais barato
        if frete_unidade < menor_frete_unitario:
            menor_frete_unitario = frete_unidade

    return menor_frete_unitario if menor_frete_unitario != float('inf') else 0.0