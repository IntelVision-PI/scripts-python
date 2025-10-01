import psutil as ps
import pandas as pd
import datetime as dt
import time

verificaIndice = 0
csv_file = "dados_maquina.csv"

while True:
    user = "servidor6.KLj9UH97BIJ"

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
    packages_recv_usage = ps.net_io_counters().packets_recv
    timestamp = dt.datetime.now().replace(microsecond=0)

    active_processes = len(processos_objs)

    processos_info = []
    for proc in processos_objs:
        try:
            cpu_p = proc.cpu_percent(None)
            mem_mb = proc.memory_info().rss / (1024 * 1024)
            processos_info.append({
                'pid': proc.pid,
                'name': proc.name(),
                'cpu': round(cpu_p, 2),
                'mem': round(mem_mb, 2)
            })
        except (ps.NoSuchProcess, ps.AccessDenied, ps.ZombieProcess):
            pass

    processos_ordenados = sorted(processos_info, key=lambda p: p['cpu'], reverse=True)

    top5 = processos_ordenados[:5]
    while len(top5) < 5:
        top5.append({'pid': None, 'name': None, 'cpu': 0.0, 'mem': 0.0})

    print(f'Usuário: {user}')
    print(f'Uso da CPU: {round(cpu_usage,2)}% | CPUs lógicas: {cpu_count}')
    print(f'Uso da RAM: {round(ram_usage,2)}% | Uso do disco: {round(disk_usage,2)}%')
    print(f'Processos ativos: {active_processes} | Timestamp: {timestamp}')
    print(f'Bytes recebidos: {bytes_recv_usage} | Pacotes recebidos: {packages_recv_usage}')
    print('-' * 40)
    print("Top 5 processos por CPU:")
    for i, p in enumerate(top5, 1):
        print(f"{i}) PID={p['pid']} | Nome={p['name']} | CPU={p['cpu']}%")
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
        "package_recv": [packages_recv_usage]
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
