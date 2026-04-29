#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orbit · Tienda Perfecta — Lanzador público (ngrok)
Expone la app Streamlit a internet con URL pública permanente.
"""

import os
import sys
import json
import subprocess
import time

BASE = os.path.dirname(os.path.abspath(__file__))
CFG  = os.path.join(BASE, "config_app.json")
TOKEN_FILE = os.path.join(BASE, ".ngrok_token")

# ── Leer token ngrok ────────────────────────────────────────────────────────
def get_token():
    # 1) Desde archivo .ngrok_token
    if os.path.exists(TOKEN_FILE):
        token = open(TOKEN_FILE, encoding="utf-8").read().strip()
        if token:
            return token
    # 2) Desde config_app.json
    if os.path.exists(CFG):
        cfg = json.load(open(CFG, encoding="utf-8"))
        token = cfg.get("ngrok_token", "")
        if token:
            return token
    return None

# ── Leer dominio estático opcional ─────────────────────────────────────────
def get_domain():
    if os.path.exists(CFG):
        cfg = json.load(open(CFG, encoding="utf-8"))
        return cfg.get("ngrok_domain", "")
    return ""

def main():
    print("=" * 52)
    print("  ORBIT · TIENDA PERFECTA — ACCESO PÚBLICO")
    print("=" * 52)

    # ── Verificar token ─────────────────────────────────────────────────────
    token = get_token()
    if not token:
        print()
        print("  ⚠️  TOKEN DE NGROK NO CONFIGURADO")
        print()
        print("  Seguí estos pasos UNA SOLA VEZ:")
        print()
        print("  1. Andá a https://dashboard.ngrok.com/signup")
        print("     (registrarte es gratis)")
        print()
        print("  2. Copiá tu Authtoken desde:")
        print("     https://dashboard.ngrok.com/get-started/your-authtoken")
        print()
        print("  3. Pegalo acá:")
        token = input("  Token ngrok: ").strip()
        if not token:
            print("  Token vacío. Saliendo.")
            sys.exit(1)
        # Guardar para la próxima vez
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(token)
        print("  ✅ Token guardado en .ngrok_token")

    # ── Configurar ngrok ────────────────────────────────────────────────────
    try:
        from pyngrok import ngrok, conf
        conf.get_default().auth_token = token
    except Exception as e:
        print(f"  Error importando pyngrok: {e}")
        print("  Ejecutá: pip install pyngrok")
        sys.exit(1)

    # ── Lanzar Streamlit en background ─────────────────────────────────────
    print()
    print("  Iniciando Streamlit...")
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run",
        os.path.join(BASE, "app_orbit_tp.py"),
        "--server.port", "8501",
        "--server.address", "127.0.0.1",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--theme.base", "dark",
        "--theme.primaryColor", "#6EC531",
        "--theme.backgroundColor", "#0A0A0A",
        "--theme.secondaryBackgroundColor", "#111111",
        "--theme.textColor", "#FFFFFF",
    ]
    streamlit_proc = subprocess.Popen(
        streamlit_cmd, cwd=BASE,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(3)  # Esperar que Streamlit levante

    # ── Abrir túnel ngrok ───────────────────────────────────────────────────
    domain = get_domain()
    try:
        if domain:
            tunnel = ngrok.connect(8501, bind_tls=True, hostname=domain)
        else:
            tunnel = ngrok.connect(8501, bind_tls=True)
        url = tunnel.public_url
    except Exception as e:
        print(f"  Error abriendo túnel ngrok: {e}")
        print("  Verificá que el token sea válido.")
        streamlit_proc.terminate()
        sys.exit(1)

    # ── Mostrar URL ─────────────────────────────────────────────────────────
    print()
    print("  ┌─────────────────────────────────────────────┐")
    print(f"  │  🌐  URL PÚBLICA: {url:<27}│")
    print("  │                                             │")
    print("  │  Compartí este link con tu equipo.          │")
    print("  │  Funciona desde cualquier dispositivo       │")
    print("  │  con internet — sin instalar nada.          │")
    print("  └─────────────────────────────────────────────┘")
    print()

    # ── Guardar URL en archivo para referencia ──────────────────────────────
    url_file = os.path.join(BASE, "url_publica.txt")
    with open(url_file, "w", encoding="utf-8") as f:
        f.write(f"URL pública Orbit TP: {url}\n")
        f.write(f"Generada: {time.strftime('%d/%m/%Y %H:%M')}\n")

    print("  Presioná Ctrl+C o cerrá esta ventana para detener.")
    print()

    try:
        streamlit_proc.wait()
    except KeyboardInterrupt:
        print()
        print("  Cerrando...")
        ngrok.kill()
        streamlit_proc.terminate()

if __name__ == "__main__":
    main()
