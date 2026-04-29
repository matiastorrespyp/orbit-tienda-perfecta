#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import pandas as pd

def detect_encoding(path: str) -> str:
    # prueba rápida con bytes y fallback
    with open(path, "rb") as f:
        raw = f.read(200000)
    # heurística simple: si parece utf-8, ok; sino cp1252
    try:
        raw.decode("utf-8")
        return "utf-8"
    except Exception:
        return "cp1252"

def norm_col(c: str) -> str:
    c = str(c).strip()
    c = re.sub(r"\s+", " ", c)
    return c

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Ruta a ventas.csv")
    ap.add_argument("--out", dest="out", required=True, help="Ruta a venta_limpia.csv")
    args = ap.parse_args()

    inp = args.inp
    out = args.out

    if not os.path.exists(inp):
        raise FileNotFoundError(inp)

    enc = detect_encoding(inp)

    # engine python + sep=None detecta ; o , automáticamente
    df = pd.read_csv(inp, encoding=enc, sep=None, engine="python")

    # normalizar encabezados (NO cambia datos)
    df.columns = [norm_col(c) for c in df.columns]

    # si “localidad” viene en minúscula, la subimos a “Localidad”
    if "Localidad" not in df.columns and "localidad" in df.columns:
        df = df.rename(columns={"localidad": "Localidad"})

    # guardar limpio
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")

    print(f"OK -> {out}")

if __name__ == "__main__":
    main()