#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]

CSV_TO_SHEET = {
    "pdf_index.csv": "pdf_index",
    "clientes_oportunidad.csv": "clientes_oportunidad",
    "foco_productos.csv": "foco_productos",
}

# CSVs que se escriben desde A1 (sin fórmula de ID en columna A)
CSV_TO_SHEET_FULL = {
    "tp_objetivos_resumen.csv": "tp_objetivos_resumen",
}


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_google_credentials(cfg: dict):
    auth_mode = str(cfg.get("auth_mode", "")).strip().lower()

    if auth_mode == "oauth_user":
        client_path = Path(cfg["oauth_client_secrets_json"])
        token_path = Path(cfg.get("oauth_token_json") or (script_dir() / "google_oauth_token.json"))

        creds = None
        if token_path.exists():
            creds = UserCredentials.from_authorized_user_file(str(token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(client_path), SCOPES)
                creds = flow.run_local_server(port=0)
            ensure_parent(token_path)
            with open(token_path, "w", encoding="utf-8") as token:
                token.write(creds.to_json())
        return creds

    if "service_account_json" not in cfg:
        raise ValueError(
            "Falta auth_mode='oauth_user' o falta service_account_json en el config."
        )

    sa_path = Path(cfg["service_account_json"])
    return ServiceAccountCredentials.from_service_account_file(str(sa_path), scopes=SCOPES)


def get_services(creds):
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    return sheets, drive


def read_csv_rows(path: Path) -> List[List[str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return [row for row in csv.reader(f)]


def clear_sheet_data_keep_id_formula(sheets_service, spreadsheet_id: str, sheet_name: str) -> None:
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!B:ZZ",
        body={},
    ).execute()


def write_csv_to_sheet_full(sheets_service, spreadsheet_id: str, sheet_name: str, csv_path: Path) -> None:
    """Full overwrite desde A1, sin preservar columna A (para hojas sin fórmula de ID).
    Crea la hoja si no existe."""
    rows = read_csv_rows(csv_path)
    meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    existing = {s["properties"]["title"] for s in meta["sheets"]}
    if sheet_name not in existing:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [{"addSheet": {"properties": {"title": sheet_name}}}]},
        ).execute()
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=sheet_name,
        body={},
    ).execute()
    if not rows:
        return
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()


def write_csv_to_sheet(sheets_service, spreadsheet_id: str, sheet_name: str, csv_path: Path) -> None:
    rows = read_csv_rows(csv_path)
    clear_sheet_data_keep_id_formula(sheets_service, spreadsheet_id, sheet_name)
    if not rows:
        return
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!B1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()


def list_children_by_name(drive_service, parent_id: str, name: str, mime_type: Optional[str] = None):
    safe_name = name.replace("'", r"\'")
    q = f"'{parent_id}' in parents and name = '{safe_name}' and trashed = false"
    if mime_type:
        q += f" and mimeType = '{mime_type}'"
    resp = drive_service.files().list(
        q=q,
        spaces="drive",
        fields="files(id,name,mimeType)",
        pageSize=10,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = resp.get("files", [])
    return files[0] if files else None


def ensure_drive_folder(drive_service, parent_id: str, folder_name: str) -> str:
    mime = "application/vnd.google-apps.folder"
    existing = list_children_by_name(drive_service, parent_id, folder_name, mime)
    if existing:
        return existing["id"]
    created = drive_service.files().create(
        body={"name": folder_name, "mimeType": mime, "parents": [parent_id]},
        fields="id",
        supportsAllDrives=True,
    ).execute()
    return created["id"]


def upload_or_update_file(drive_service, parent_id: str, local_path: Path) -> str:
    existing = list_children_by_name(drive_service, parent_id, local_path.name)
    media = MediaFileUpload(str(local_path), resumable=False)
    if existing:
        drive_service.files().update(
            fileId=existing["id"],
            media_body=media,
            supportsAllDrives=True,
        ).execute()
        return existing["id"]
    created = drive_service.files().create(
        body={"name": local_path.name, "parents": [parent_id]},
        media_body=media,
        fields="id",
        supportsAllDrives=True,
    ).execute()
    return created["id"]


def sync_pdf_tree(drive_service, local_dir: Path, drive_folder_id: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not local_dir.exists():
        return out

    for root, _, files in os.walk(local_dir):
        root_path = Path(root)
        rel = root_path.relative_to(local_dir)
        current_parent = drive_folder_id
        if rel.parts:
            for part in rel.parts:
                current_parent = ensure_drive_folder(drive_service, current_parent, part)

        for name in files:
            if not name.lower().endswith(".pdf"):
                continue
            local_path = root_path / name
            file_id = upload_or_update_file(drive_service, current_parent, local_path)
            rel_path = "/".join(rel.parts + (name,)) if rel.parts else name
            out[rel_path] = file_id
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = load_json(Path(args.config))

    base_dir = script_dir()
    csv_dir = Path(cfg.get("csv_dir") or (base_dir / "output" / "APPSHEET"))
    pdf_ger_dir = Path(cfg.get("pdf_gerencial_dir") or (base_dir / "output" / "PDF_GERENCIAL"))
    pdf_vend_dir = Path(cfg.get("pdf_vendedores_dir") or (base_dir / "output" / "PDF_VENDEDORES"))

    print("=== TP_PYP SYNC GOOGLE ===")
    print(f"CSV dir: {csv_dir}")
    print(f"PDF gerencial dir: {pdf_ger_dir}")
    print(f"PDF vendedores dir: {pdf_vend_dir}")

    creds = get_google_credentials(cfg)
    sheets_service, drive_service = get_services(creds)

    spreadsheet_id = cfg["spreadsheet_id"]

    for csv_name, sheet_name in CSV_TO_SHEET.items():
        csv_path = csv_dir / csv_name
        if not csv_path.exists():
            raise FileNotFoundError(f"No existe {csv_path}")
        write_csv_to_sheet(sheets_service, spreadsheet_id, sheet_name, csv_path)

    for csv_name, sheet_name in CSV_TO_SHEET_FULL.items():
        csv_path = csv_dir / csv_name
        if csv_path.exists():
            write_csv_to_sheet_full(sheets_service, spreadsheet_id, sheet_name, csv_path)
            print(f"  {sheet_name}: subido desde A1")
        else:
            print(f"  AVISO: {csv_name} no encontrado, saltando.")

    print("OK: Google Sheets actualizado")

    ger_map = sync_pdf_tree(drive_service, pdf_ger_dir, cfg["drive_pdf_gerencial_folder_id"])
    vend_map = sync_pdf_tree(drive_service, pdf_vend_dir, cfg["drive_pdf_vendedores_folder_id"])

    print(f"- PDFs gerenciales sincronizados: {len(ger_map)}")
    print(f"- PDFs vendedores sincronizados: {len(vend_map)}")
    print("SYNC OK")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:")
        print(str(e))
        raise
