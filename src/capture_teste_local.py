import logging
import boto3
from botocore.exceptions import ClientError
import os
import psutil as ps
import pandas as pd
import datetime as dt
import time
import subprocess
import re
import platform
import random

csv_file = "dados_maquina.csv"
user = "servidor19.LETSS05HWDF"
bucket_name = "my-bucket-raw-sptech"
contador = 0

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

def get_network_ping_hybrid(host="8.8.8.8"):
    """
    Tenta pegar latência real. 
    Se der erro (bloqueio de rede) ou retornar 0 (erro de idioma),
    gera dados simulados para não quebrar a dashboard.
    """
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        output = subprocess.check_output(['ping', param, '4', host], stderr=subprocess.STDOUT).decode('cp850', errors='ignore')
        
        times = [float(t) for t in re.findall(r"(?:time|tempo)[=<](\d+)", output)]
        
        loss_match = re.search(r"(\d+)% loss", output) or re.search(r"(\d+)% packet loss", output) or re.search(r"(\d+)% de perda", output)
        loss = int(loss_match.group(1)) if loss_match else 0
        
        if len(times) > 0:
            avg_latency = sum(times) / len(times)
            jitter = 0
            if len(times) > 1:
                diffs = [abs(times[i] - times[i-1]) for i in range(1, len(times))]
                jitter = sum(diffs) / len(diffs)
            return round(avg_latency, 2), round(jitter, 2), loss
        else:
            raise Exception("Nenhum tempo encontrado no ping")

    except Exception as e:
        sim_latency = random.uniform(15.0, 60.0)
        sim_jitter = random.uniform(1.0, 8.0)
        return round(sim_latency, 2), round(sim_jitter, 2), 0

def get_interface_speed():
    try:
        stats = ps.net_if_stats()
        for nic, info in stats.items():
            if info.isup and info.speed > 0:
                return info.speed 
        return 1000 
    except:
        return 1000

ultimo_dia = dt.datetime.now().day 
interface_speed = get_interface_speed()

print("Iniciando IntelVision Monitor...")
print(f"Modo: Hardware Real | Rede Simulada/Híbrida")

while contador < 10:
    agora = dt.datetime.now()
    
    """ if agora.day != ultimo_dia:
        print("Deu meia-noite! Enviando arquivo e limpando CSV...")
        upload_file(csv_file, bucket_name)
        open(csv_file, "w").close()
        print("CSV limpo.\n")
        ultimo_dia = agora.day  """
    processos_objs = []
    for proc in ps.process_iter(['pid', 'name']):
        try:
            proc.cpu_percent(interval=None)
            processos_objs.append(proc)
        except (ps.NoSuchProcess, ps.AccessDenied, ps.ZombieProcess):
            pass

    time.sleep(5)

    mbps_recv = random.uniform(40.0, 120.0)
    mbps_sent = random.uniform(5.0, 15.0)
    saturacao = (mbps_recv / interface_speed) * 100

    latencia, jitter, perda = get_network_ping_hybrid()

    cpu_usage = ps.cpu_percent(interval=None)
    cpu_count = ps.cpu_count()
    ram_usage = ps.virtual_memory().percent
    disk_usage = ps.disk_usage('/').percent
    disk_size = round(ps.disk_usage('/').total / 1024**3, 2)
    
    net_io = ps.net_io_counters()
    
    timestamp = agora.replace(microsecond=0)
    active_processes = len(processos_objs)

    processos_info = []
    for proc in processos_objs:
        try:
            cpu_p = proc.cpu_percent(interval=None) / ps.cpu_count()
            processos_info.append({'name': proc.name(), 'cpu': round(cpu_p, 2)})
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
        "bytes_recv": [net_io.bytes_recv],
        "package_recv": [net_io.packets_recv],
        "bytes_sent": [net_io.bytes_sent],
        "package_sent": [net_io.packets_sent],
        #(Simulados ou Híbridos para que em caso de erro simule)
        "rede_download_mbps": [round(mbps_recv, 2)],
        "rede_upload_mbps": [round(mbps_sent, 2)],
        "rede_saturacao": [round(saturacao, 2)],
        "rede_latencia": [latencia],
        "rede_jitter": [jitter],
        "rede_perda": [perda]
    }

    for idx, p in enumerate(top5, 1):
        dados[f'proc{idx}_name'] = [p['name']]
        dados[f'proc{idx}_cpu_pct'] = [p['cpu']]

    df = pd.DataFrame(dados)

    if not os.path.isfile(csv_file) or os.path.getsize(csv_file) == 0:
        df.to_csv(csv_file, mode='a', encoding='utf-8', sep=';', index=False)
    else:
        df.to_csv(csv_file, mode='a', encoding='utf-8', sep=';', header=False, index=False)
    
    print(f"[{timestamp}] Salvo.")
    contador += 1

print("Deu meia-noite! Enviando arquivo e limpando CSV...")
upload_file(csv_file, bucket_name)
open(csv_file, "w").close()
print("CSV limpo.\n")
ultimo_dia = agora.day 