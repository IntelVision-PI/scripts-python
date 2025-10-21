from windows_tools.installed_software import get_installed_software

import pandas as pd

verificaIndice = 0

csv_file = "lista_aplicativos.csv"

for software in get_installed_software():
    print(software['name'], software['version'], software['publisher'])
    dados = {
        "nome": [software['name']],
        "versao": [software['version']],
        "editor": [software['publisher']]
    }

    df = pd.DataFrame(dados)

    if verificaIndice == 0:
        df.to_csv(csv_file, mode='a', encoding='utf-8', sep=';', index=False)
        verificaIndice = 1
    else:
        df.to_csv(csv_file, mode='a', encoding='utf-8', sep=';', header=False, index=False)
