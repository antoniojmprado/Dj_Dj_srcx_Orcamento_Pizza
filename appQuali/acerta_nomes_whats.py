from django.conf import settings
import os
import re

pasta = settings.MEDIA_ROOT / 'itens'

for nome in os.listdir(pasta):
    antigo = pasta / nome

    if not antigo.is_file():
        continue

    novo = nome

    # remove hashes estranhos (ex: 8XTM5vu)
    novo = re.sub(r'_[A-Za-z0-9]{6,}', '', novo)

    # troca múltiplos pontos por underscore (menos o da extensão)
    partes = novo.split('.')
    if len(partes) > 2:
        novo = '_'.join(partes[:-1]) + '.' + partes[-1]

    # garante apenas caracteres seguros
    novo = re.sub(r'[^A-Za-z0-9_.-]', '_', novo)

    if novo != nome:
        print(f'{nome}  ->  {novo}')
        os.rename(antigo, pasta / novo)
