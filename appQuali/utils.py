def capitalize_pt(texto: str) -> str:
    excecoes = {'da', 'de', 'do', 'das', 'dos', 'e'}
    palavras = texto.lower().split()

    return ' '.join(
        p if p in excecoes else p.capitalize()
        for p in palavras
    )
