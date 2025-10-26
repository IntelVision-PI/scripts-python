import psutil as ps
import pandas as pd
import datetime as dt
import time
import os
import boto3
from botocore.exceptions import ClientError
import logging

# antes de rodar configure o AWS CLI com 'aws configure' e mude a variavel user abaixo
verificaIndice = 0
csv_file = "dados_maquina.csv"

for i in range(3):
    user = "servidor6.NICOLASF8SK4U2"

    # Captura processos e inicializa CPU
    processos_objs = []
    for proc in ps.process_iter(['pid', 'name']):
        try:
            if "System Idle Process" not in proc.name():
                proc.cpu_percent(interval=None) 
                processos_objs.append(proc)
        except (ps.NoSuchProcess, ps.AccessDenied, ps.ZombieProcess):
            pass

    # Espera 1 segundo para medir CPU real
    time.sleep(1)

    cpu_usage = round(ps.cpu_percent(interval=None), 2)
    cpu_count = ps.cpu_count()
    ram_usage = round(ps.virtual_memory().percent, 2)
    disk_usage = round(ps.disk_usage('/').percent, 2)
    disk_size = round(ps.disk_usage('/').total / 1024**3, 2)
    bytes_recv_usage = ps.net_io_counters().bytes_recv
    packages_recv_usage = ps.net_io_counters().packets_recv
    bytes_sent_usage = ps.net_io_counters().bytes_sent
    packages_sent_usage = ps.net_io_counters().packets_sent
    active_processes = len(processos_objs)
    timestamp = dt.datetime.now().replace(microsecond=0)

    # Captura CPU% real de cada processo
    processos_info = []
    for proc in processos_objs:
        try:
            cpu_p = proc.cpu_percent(interval=None) / ps.cpu_count()
            processos_info.append({'name': proc.name(), 'cpu': round(cpu_p, 2)})
        except (ps.NoSuchProcess, ps.AccessDenied, ps.ZombieProcess):
            pass

    # Top 5 processos por CPU
    top5 = sorted(processos_info, key=lambda p: p['cpu'], reverse=True)[:5]
    while len(top5) < 5:
        top5.append({'name': None, 'cpu': 0.0})

    # Imprime informações
    print(f'Usuário: {user}')
    print(f'Uso da CPU: {cpu_usage}% | CPUs lógicas: {cpu_count}')
    print(f'Uso da RAM: {ram_usage}% | Uso do disco: {disk_usage}%')
    print(f'Processos ativos: {active_processes} | Timestamp: {timestamp}')
    print(f'Bytes recebidos: {bytes_recv_usage} | Pacotes recebidos: {packages_recv_usage}')
    print(f'Bytes enviados: {bytes_sent_usage} | Pacotes enviados: {packages_sent_usage}')
    print('-' * 40)
    print("Top 5 processos por CPU:")
    for i, p in enumerate(top5, 1):
        print(f"{i}) Nome={p['name']} | CPU={p['cpu']}%")
    print('*' * 50)

    # Salva no CSV
    dados = {
        "user": [user],
        "timestamp": [timestamp],
        "cpu": [cpu_usage],
        "cpu_count": [cpu_count],
        "ram": [ram_usage],
        "disco": [disk_usage],
        "disco_size": [disk_size],
        "qtd_processos": [active_processes],
        "bytes_recv": [bytes_recv_usage],
        "packages_recv": [packages_recv_usage],
        "bytes_sent": [bytes_sent_usage],
        "packages_sent": [packages_sent_usage],
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

def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client('s3')  

    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

# Upload do CSV para S3
upload_file(csv_file, 'raw-20251026133436-31233', 'dados_maquina.csv')
