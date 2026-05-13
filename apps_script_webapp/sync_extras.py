#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_extras.py — Sincroniza hojas adicionales de Google Sheets para la vista Gerencia.

Sube a Google Sheets las dos hojas que sync_tp_appsheet_drive.py no cubre:
  - tp_objetivos_resumen.csv  → hoja "tp_objetivos_resumen"
  - tp_facturacion_comparativa.csv → hoja "tp_facturacion_comparativa"

Usa las mismas credenciales y Spreadsheet ID que el sync principal.
Ejecutar después de sync_tp_appsheet_drive.py.

Uso:
  python sync_extras.py --config google_sync_config.json
"""

import argparse
import csv
import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

EXTRA_CSV_TO_SHEET = {
    "tp_objetivos_resumen.csv":       "tp_objetivos_resumen",
    "tp_facturacion_comparativa.csv": "tp_facturacion_comparativa",
}


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_credentials(cfg: dict):
    client_path = Path(cfg["oauth_client_secrets_json"])
    token_path  = Path(cfg.get("oauth_token_json") or (script_dir().parent / "credenciales" / "google-oauth-token.json"))

    creds = None
    if token_path.exists():
        creds = UserCredentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return creds


def read_csv(path: Path) -> list[list]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


def upload_sheet(service, spreadsheet_id: str, sheet_name: str, rows: list[list]):
    # Verificar o crear la hoja
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    existing = {s["properties"]["title"] for s in meta["sheets"]}

    if sheet_name not in existing:
        body = {"requests": [{"addSheet": {"properties": {"title": sheet_name}}}]}
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        print(f"  Hoja creada: {sheet_name}")

    # Limpiar y escribir
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=sheet_name
    ).execute()

    if rows:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="RAW",
            body={"values": rows}
        ).execute()
        print(f"  {sheet_name}: {len(rows)-1} filas subidas.")
    else:
        print(f"  {sheet_name}: CSV vacío, hoja limpiada.")


def main():
    parser = argparse.ArgumentParser(description="Sync extras para gerencia")
    parser.add_argument("--config", default="google_sync_config.json")
    args = parser.parse_args()

    cfg_path = script_dir().parent / args.config
    if not cfg_path.exists():
        print(f"ERROR: No se encontró {cfg_path}")
        raise SystemExit(1)

    cfg            = load_json(cfg_path)
    spreadsheet_id = cfg["spreadsheet_id"]
    appsheet_dir   = script_dir().parent / "output" / "APPSHEET"

    print("=" * 50)
    print("  SYNC EXTRAS — Gerencia")
    print("=" * 50)

    creds   = get_credentials(cfg)
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    for csv_name, sheet_name in EXTRA_CSV_TO_SHEET.items():
        csv_path = appsheet_dir / csv_name
        if not csv_path.exists():
            print(f"  AVISO: No encontré {csv_path}, saltando.")
            continue
        rows = read_csv(csv_path)
        upload_sheet(service, spreadsheet_id, sheet_name, rows)

    print()
    print("  Sync extras finalizado.")


if __name__ == "__main__":
    main()
