#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orbit · Tienda Perfecta — Sync Excel → Google Sheets
Sube STATUS_CLIENTE, OBJ_VENDEDOR y OBJ_TAXONOMIA del Excel de control
a pestañas de Google Sheets para que la app en la nube pueda leerlas.
Se ejecuta después del motor principal.
"""

import json
import sys
import pandas as pd
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE = Path(__file__).resolve().parent
CFG_PATH  = BASE / "google_sync_config.json"
XLSX_PATH = BASE / "output" / "Control_TP_Portafolio_PyP.xlsx"

SHEET_MAP = {
    "STATUS_CLIENTE": "STATUS_CLIENTE",
    "OBJ_VENDEDOR":   "OBJ_VENDEDOR",
    "OBJ_TAXONOMIA":  "OBJ_TAXONOMIA",
}

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_credentials(cfg: dict) -> Credentials:
    token_path = Path(cfg["oauth_token_json"])
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Guardar token renovado
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def upload_sheet(service, spreadsheet_id: str, tab_name: str, df: pd.DataFrame):
    """Borra y vuelve a escribir una pestaña completa."""
    df_clean = df.fillna("").astype(str)
    values = [df_clean.columns.tolist()] + df_clean.values.tolist()

    # Asegurar que la pestaña existe (ignorar error si ya existe)
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [{"addSheet": {"properties": {"title": tab_name}}}]}
        ).execute()
    except Exception:
        pass  # Ya existe, OK

    # Limpiar
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f"'{tab_name}'!A:ZZ"
    ).execute()

    # Escribir
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"'{tab_name}'!A1",
        valueInputOption="RAW",
        body={"values": values}
    ).execute()

    print(f"  OK  {tab_name:<22} - {len(df)} filas")


def main():
    print()
    print("=" * 48)
    print("  Orbit - Sync Excel -> Google Sheets")
    print("=" * 48)

    if not CFG_PATH.exists():
        print("  ⚠️  google_sync_config.json no encontrado.")
        sys.exit(0)

    if not XLSX_PATH.exists():
        print(f"  ⚠️  No encontré {XLSX_PATH}")
        sys.exit(1)

    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    spreadsheet_id = cfg["spreadsheet_id"]

    print("  Autenticando con Google...")
    creds   = get_credentials(cfg)
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    print("  Leyendo Excel local...")
    xl = pd.ExcelFile(XLSX_PATH)

    print("  Subiendo pestañas...")
    for excel_tab, gsheet_tab in SHEET_MAP.items():
        df = xl.parse(excel_tab)
        upload_sheet(service, spreadsheet_id, gsheet_tab, df)

    print()
    print("  Datos de la app actualizados en Google Sheets.")
    print("  La app en la nube ya tiene los datos de hoy.")
    print()


if __name__ == "__main__":
    main()
