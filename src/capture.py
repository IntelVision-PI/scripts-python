import psutil as ps, pandas as pd, datetime as dt, time

verificaIndice = 0

while True:

    user = "servidor1.GUIF8SK4U2"
    cpu_usage = ps.cpu_percent()
    cpu_count = ps.cpu_count()
    ram_usage = ps.virtual_memory().percent
    disk_usage = ps.disk_usage('/').percent
    bytes_recv_usage = ps.net_io_counters().bytes_recv
    packages_recv_usage = ps.net_io_counters().packets_recv
    bytes_sent_usage = ps.net_io_counters().bytes_sent
    packages_sent_usage = ps.net_io_counters().packets_sent
    active_processes = 0
    timestamp = dt.datetime.now()

    for proc in ps.process_iter(['name']):
        active_processes += 1

    cpu_usage = round(cpu_usage, 2)
    ram_usage = round(ram_usage, 2)
    disk_usage = round(disk_usage, 2)
    bytes_recv_usage = round(bytes_recv_usage, 2)
    timestamp = dt.datetime.now().replace(microsecond=0)

    print(f'Usuário: {user}')
    print(f'Uso da CPU: {cpu_usage}%')
    print(f'Número de CPUs lógicas no sistema {cpu_count}')
    print(f'Uso da RAM: {ram_usage}%')
    print(f'Uso do disco: {disk_usage}%')
    print(f'Quantidade de processos em execução no momento: {active_processes}')
    print(f'Timestamp: {timestamp}')
    print(f'Bytes recebidos pela rede: {bytes_recv_usage}')
    print(f'Pacotes recebidos pela rede: {packages_recv_usage}')
    print(f'Bytes enviados pela rede: {bytes_sent_usage}')
    print(f'Pacotes enviados pela rede: {packages_sent_usage}')
    print('*'*30)

    dados = {
        "user": [user],
        "timestamp": [timestamp],
        "cpu": [cpu_usage],
        "cpu_count": [cpu_count],
        "ram": [ram_usage],
        "disco": [disk_usage],
        "qtd_processos": [active_processes],
        "bytes_recv": [bytes_recv_usage],
        "package_recv": [packages_recv_usage],
        "bytes_sent": [bytes_sent_usage],
        "package_sent": [packages_sent_usage]
    }

    df = pd.DataFrame(dados)

    if(verificaIndice == 0):
        df.to_csv("dados_maquina.csv", mode='a', encoding="utf-8", sep =';', index=False)
        verificaIndice += 1
    else:
        df.to_csv("dados_maquina.csv", mode='a', encoding="utf-8", sep =';', header=False, index=False)

    time.sleep(10)