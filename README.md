# Projeto: Monitoramento de Nginx com Alerta no Discord

## 1 Instalação da VM e pacotes necessários
No Ubuntu Server (ou VM equivalente), atualize os pacotes e instale o Nginx e o Python:

```bash
sudo apt update && sudo apt -y install nginx python3 python3-venv python3-pip curl
```

---

## 2  Configuração de diretórios e HTML
Crie o diretório do site e adicione a página HTML:

```bash
sudo mkdir -p /var/www/estudio-site
sudo nano /var/www/estudio-site/index.html
```
*(Adicione o conteúdo HTML desejado e salve.)*

No arquivo de configuração do Nginx (`/etc/nginx/sites-available/default`), defina:
```
server_name _;
root /var/www/estudio-site;
index index.html;
```

Reinicie o Nginx:
```bash
sudo systemctl restart nginx
```

---

## 3 Arquivo de variáveis de ambiente (.env)
Crie o arquivo `/etc/estudio-monitor.env`:

```bash
sudo tee /etc/estudio-monitor.env >/dev/null <<'EOF'
MON_URL="http://127.0.0.1/healthz"
MON_TIMEOUT=5
MON_RETRIES=3
DISCORD_WEBHOOK_URL="COLE_AQUI_SEU_WEBHOOK"
EOF
sudo chmod 600 /etc/estudio-monitor.env
```

---

## 4 Script Python de monitoramento
Salve o script em `/opt/estudio-nginx/monitor_nginx.py`:

```python
#!/usr/bin/env python3
import os, time, subprocess, json
from urllib.request import urlopen, Request

MON_URL = os.getenv("MON_URL", "http://127.0.0.1/healthz")
TIMEOUT = int(os.getenv("MON_TIMEOUT", "5"))
RETRIES = int(os.getenv("MON_RETRIES", "3"))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

def http_ok(url, timeout, retries):
    for _ in range(retries):
        try:
            req = Request(url, headers={"User-Agent": "estudio-monitor"})
            with urlopen(req, timeout=timeout) as r:
                if r.getcode() == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False

def is_active(service="nginx"):
    return subprocess.run(["systemctl","is-active","--quiet",service]).returncode == 0

def restart(service="nginx"):
    subprocess.run(["systemctl","restart",service], check=False)

def alert_discord(text):
    if not DISCORD_WEBHOOK_URL:
        print("discord: webhook vazio")
        return
    try:
        url = DISCORD_WEBHOOK_URL if "?" in DISCORD_WEBHOOK_URL else DISCORD_WEBHOOK_URL + "?wait=true"
        data = json.dumps({"content": text}).encode()
        req = Request(url, data=data, headers={"Content-Type":"application/json"})
        with urlopen(req, timeout=10) as r:
            print(f"discord status: {r.status}")
    except Exception as e:
        print(f"discord erro: {e}")

if not http_ok(MON_URL, TIMEOUT, RETRIES) or not is_active("nginx"):
    alert_discord("⚠️ Nginx caiu! Tentando reiniciar...")
    restart("nginx")
```

Dê permissão de execução:
```bash
sudo chmod +x /opt/estudio-nginx/monitor_nginx.py
```

---

## 5 Service e Timer do Systemd
Crie `/etc/systemd/system/estudio-monitor.service`:
```
[Unit]
Description=Monitor simples do Nginx (checa /healthz, alerta Discord e tenta restart)
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
EnvironmentFile=/etc/estudio-monitor.env
ExecStart=/usr/bin/python3 /opt/estudio-nginx/monitor_nginx.py

[Install]
WantedBy=multi-user.target
```

Crie `/etc/systemd/system/estudio-monitor.timer`:
```
[Unit]
Description=Executa o monitor do Nginx a cada 1 minuto

[Timer]
OnBootSec=30
OnUnitActiveSec=60

[Install]
WantedBy=timers.target
```

A```

---

## 6 Teste - Pare o Nginx:
```bash
sudo systemctl stop nginx
```
- Aguarde o timer rodar e verificar se:
  - O serviço é reiniciado.
  - Uma mensagem chega no Discord via webhook.

---

## 📂 Estrutura do projeto
```
/var/www/estudio-site/index.html        # Página HTML
/opt/estudio-nginx/monitor_nginx.py     # Script Python
/etc/estudio-monitor.env                # Variáveis de ambiente
/etc/systemd/system/estudio-monitor.*   # Service e Timer
```

---

