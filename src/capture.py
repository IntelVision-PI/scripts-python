import logging
import boto3
from botocore.exceptions import ClientError
import os
import psutil as ps
import pandas as pd
import datetime as dt
import time

csv_file = "dados_maquina.csv"
user = "servidor6.NICOLASF8SK4U2"

def upload_file(file_name, bucket):
    agora = dt.datetime.now()
    ano = agora.strftime("%Y")
    mes = agora.strftime("%m")
    dia = agora.strftime("%d")

    nome_s3 = f"dados_maquina_{ano}-{mes}-{dia}--{user}.csv"
    object_name = f"{ano}/{mes}/{dia}/{nome_s3}"

    s3_client = boto3.client('s3')

    try:
        s3_client.upload_file(file_name, bucket, object_name)
        print(f"Arquivo enviado para o S3 em: {object_name}")
    except ClientError as e:
        logging.error(e)
        return False

    return True


ultimo_dia = dt.datetime.now().day 

while True:

    agora = dt.datetime.now()
    if agora.day != ultimo_dia:
        print("⏰ Deu meia-noite! Enviando arquivo e limpando CSV...")

        upload_file(csv_file, "my-bucket-raw-sptech-nicolas")

        open(csv_file, "w").close()
        print("CSV limpo.\n")

        ultimo_dia = agora.day 


    processos_objs = []
    for proc in ps.process_iter(['pid', 'name']):
        try:
            proc.cpu_percent(interval=None)
            processos_objs.append(proc)
        except (ps.NoSuchProcess, ps.AccessDenied, ps.ZombieProcess):
            pass

    time.sleep(1)

    cpu_usage = ps.cpu_percent(interval=None)
    cpu_count = ps.cpu_count()
    ram_usage = ps.virtual_memory().percent
    disk_usage = ps.disk_usage('/').percent
    disk_size = round(ps.disk_usage('/').total / 1024**3, 2)
    bytes_recv_usage = ps.net_io_counters().bytes_recv
    packages_recv_usage = ps.net_io_counters().packets_recv
    bytes_sent_usage = ps.net_io_counters().bytes_sent
    packages_sent_usage = ps.net_io_counters().packets_sent
    
    timestamp = agora.replace(microsecond=0)
    active_processes = len(processos_objs)

    processos_info = []
    for proc in processos_objs:
        try:
            cpu_p = proc.cpu_percent(interval=None) / ps.cpu_count()
            processos_info.append({
                'name': proc.name(),
                'cpu': round(cpu_p, 2),
            })
        except:
            pass

    processos_ordenados = sorted(processos_info, key=lambda p: p['cpu'], reverse=True)
    top5 = processos_ordenados[:5]

    while len(top5) < 5:
        top5.append({'name': None, 'cpu': 0.0})

    dados = {
        "user": [user],
        "timestamp": [timestamp],
        "cpu": [round(cpu_usage, 2)],
        "cpu_count": [cpu_count],
        "ram": [round(ram_usage, 2)],
        "disco": [round(disk_usage, 2)],
        "disco_size_gb": [disk_size],
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

    if not os.path.isfile(csv_file) or os.path.getsize(csv_file) == 0:
        df.to_csv(csv_file, mode='a', encoding='utf-8', sep=';', index=False)
    else:
        df.to_csv(csv_file, mode='a', encoding='utf-8', sep=';', header=False, index=False)

    time.sleep(10)
