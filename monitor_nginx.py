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
            body = r.read().decode(errors="ignore")
            if body:
                print(f"discord body: {body[:200]}")
    except Exception as e:
        print(f"discord erro: {e}")

if __name__ == "__main__":
    if not is_active("nginx") or not http_ok(MON_URL, TIMEOUT, RETRIES):
        alert_discord("⚠️ Nginx caiu! Tentando reiniciar...")
        restart("nginx")
        time.sleep(3)
        if is_active("nginx"):
            alert_discord("✅ Nginx reiniciado com sucesso.")
        else:
            alert_discord("❌ Falha ao reiniciar o Nginx.")
