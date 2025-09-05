import psutil as ps, pandas as pd, datetime as dt, time

verificaIndice = 0

while True:

    user = "Usuário"
    cpu_usage = ps.cpu_percent()
    cpu_count = ps.cpu_count()
    ram_usage = ps.virtual_memory().percent
    disk_usage = ps.disk_usage('/').percent
    active_processes = 0
    timestamp = dt.datetime.now()

    for proc in ps.process_iter(['name']):
        active_processes += 1

    cpu_usage = round(cpu_usage, 2)
    ram_usage = round(ram_usage, 2)
    disk_usage = round(disk_usage, 2)
    timestamp = dt.datetime.now().replace(microsecond=0)

    print(f'Usuário: {user}')
    print(f'Uso da CPU: {cpu_usage}%')
    print(f'Número de CPUs lógicas no sistema {cpu_count}')
    print(f'Uso da RAM: {ram_usage}%')
    print(f'Uso do disco: {disk_usage}%')
    print(f'Quantidade de processos em execução no momento: {active_processes}')
    print(f'Timestamp: {timestamp}')
    print('*'*30)

    dados = {
    "user": ["Guilherme"],
    "timestamp": [timestamp],
    "cpu": [cpu_usage],
    "cpu_count": [cpu_count],
    "ram": [ram_usage],
    "disco": [disk_usage],
    "qtd_processos": [active_processes]
    }

    df = pd.DataFrame(dados)

    if(verificaIndice == 0):
        df.to_csv("dados_maquina.csv", mode='a', encoding="utf-8", sep =';', index=False)
        verificaIndice += 1
    else:
        df.to_csv("dados_maquina.csv", mode='a', encoding="utf-8", sep =';', header=False, index=False)

    time.sleep(10)