import math
from .models import FreteEdne, EstadoCapitalBR, TransportadoraFrete # Ajuste os imports conforme seu appFrete

def calcular_melhor_frete_interno(cep_destino, valor_nf, peso_informado, comp, larg, alt, qt_pacotes, unid_pacote):
    """
    Motor isolado que replica a lógica real da view calcular_frete_view, 
    consultando o banco de dados (EDNE e Transportadoras) para retornar o menor frete unitário.
    """
    # 1. Matemática de Volumes
    volume_unitario = (comp * larg * alt) / 1000000.0
    volume_total_m3 = volume_unitario * qt_pacotes
    total_unidades = qt_pacotes * unid_pacote

    # 2. Busca o Destino no EDNE (Tratamento de CEP)
    cep_limpo = ''.join(filter(str.isdigit, str(cep_destino)))
    cep_busca = cep_limpo.lstrip('0') if len(cep_limpo) == 8 else cep_limpo
    
    destino = FreteEdne.objects.filter(cep=cep_busca).first()
    
    if not destino:
        print(f"CEP {cep_busca} não encontrado na base EDNE.")
        return 0.0

    # 3. Define Região (Capital vs Interior)
    capital_obj = EstadoCapitalBR.objects.filter(uf=destino.uf).first()
    cidade_capital = capital_obj.capital if capital_obj else ""
    uf_coluna = f"{destino.uf}_CAPITAL" if destino.municipio == cidade_capital else f"{destino.uf}_INTERIOR"

    # 4. Busca as Tarifas das Transportadoras
    transp_qs = TransportadoraFrete.objects.filter(estado=uf_coluna).only(
        'transportadora', 'antt', 'fator_excedente', 'ad_valor', 
        'gris', 'pedagio', 'frete_peso', 'cem_kg', 'taxa_emb', 'tas', 'icms'
    )

    melhor_frete_unidade = float('inf')

    # 5. Loop de Cálculo (Igual ao da View)
    for t in transp_qs:
        antt = float(t.antt)
        peso_cubado_calc = volume_total_m3 * antt
        
        # A sua regra de ouro do SQL: IF( volume * 300 > peso_fisico, volume * 300, peso_fisico)
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

        if frete_unidade < melhor_frete_unidade:
            melhor_frete_unidade = frete_unidade
            melhor_prazo = float(t.prazo) # <--- CAPTURA O PRAZO

            # Se não achar nada, devolve 0 para ambos
            if melhor_frete_unidade == float('inf'):
                return 0.0, 0

    return melhor_frete_unidade, melhor_prazo 