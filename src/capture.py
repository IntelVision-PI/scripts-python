import psutil as ps
import pandas as pd
import datetime as dt
import time

verificaIndice = 0
csv_file = "dados_maquina.csv"

while True:
    user = "servidor6.GUIF8SK4U2"

    processos_objs = []
    for proc in ps.process_iter(['pid', 'name']):
        try:
            proc.cpu_percent(None)  
            processos_objs.append(proc)
        except (ps.NoSuchProcess, ps.AccessDenied, ps.ZombieProcess):
            pass

    cpu_usage = ps.cpu_percent(interval=1)
    cpu_count = ps.cpu_count()
    ram_usage = ps.virtual_memory().percent
    disk_usage = ps.disk_usage('/').percent
    bytes_recv_usage = ps.net_io_counters().bytes_recv
    packages_recv_usage = ps.net_io_counters().bytes_recv
    bytes_sent_usage = ps.net_io_counters().bytes_sent
    packages_sent_usage = ps.net_io_counters().packets_sent
    
    active_processes = 0
    timestamp = dt.datetime.now()

    for proc in ps.process_iter(['name']):
        active_processes += 1

    cpu_usage = round(cpu_usage, 2)
    ram_usage = round(ram_usage, 2)
    disk_usage = round(disk_usage, 2)
    timestamp = dt.datetime.now().replace(microsecond=0)

    active_processes = len(processos_objs)

    processos_info = []
    for proc in processos_objs:
        try:
            cpu_p = proc.cpu_percent(None)
            mem_mb = proc.memory_info().rss / (1024 * 1024)
            processos_info.append({
                'name': proc.name(),
                'cpu': round(cpu_p, 2)
            })
        except (ps.NoSuchProcess, ps.AccessDenied, ps.ZombieProcess):
            pass

    processos_ordenados = sorted(processos_info, key=lambda p: p['cpu'], reverse=True)

    top5 = processos_ordenados[:5]
    while len(top5) < 5:
        top5.append({'pid': None, 'name': None, 'cpu': 0.0, 'mem': 0.0})

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

    print("Top 5 processos por CPU:")
    for i, p in enumerate(top5, 1):
        print(f"{i}) Nome={p['name']} | CPU={p['cpu']}%")
    print('*' * 50)

    dados = {
        "user": [user],
        "timestamp": [timestamp],
        "cpu": [round(cpu_usage, 2)],
        "cpu_count": [cpu_count],
        "ram": [round(ram_usage, 2)],
        "disco": [round(disk_usage, 2)],
        "qtd_processos": [active_processes],
        "bytes_recv": [bytes_recv_usage],
        "package_recv": [packages_recv_usage],
        "bytes_sent": [bytes_sent_usage],
        "package_sent": [packages_sent_usage]
    }

    for idx, p in enumerate(top5, 1):
        dados[f'proc{idx}_name'] = [p['name']]
        dados[f'proc{idx}_cpu_pct'] = [p['cpu']]

    df = pd.DataFrame(dados)

    if verificaIndice == 0:
        df.to_csv(csv_file, mode='a', encoding='utf-8', sep=';', index=False)
        verificaIndice = 1
    else:
        df.to_csv(csv_file, mode='a', encoding='utf-8', sep=';', header=False, index=False)

    time.sleep(10)