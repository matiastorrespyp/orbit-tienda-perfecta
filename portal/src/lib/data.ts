// data.ts — Fuente de datos: Google Sheets API (antes: fs.readFileSync local).
// Todas las funciones son async. Las páginas deben usar await al llamarlas.
// Cache en memoria de 5 minutos — configurado en google.ts.

import { readSheet } from './google';
import { getConfig } from './config';

// ─── Interfaces (sin cambios respecto a la versión anterior) ──────────────────

export interface Cliente {
  Fecha: string; Dia: string;
  VendedorID: string; VendedorNombre: string;
  ClienteID: string; RazonSocial: string;
  Localidad: string; Direccion: string;
  PortafolioPct: number; Faltan80: number; Faltan100: number;
  SKUsFaltan80: string; SKUsFaltan100: string;
  TP_Sistema: string; TP_Aplica: string;
}

export interface Foco {
  Fecha: string; Dia: string; Scope: string;
  VendedorID: string; VendedorNombre: string;
  Rank: number; Articulo: string; CantClientes: number;
}

export interface PdfEntry {
  Fecha: string; Dia: string; TipoPDF: string;
  VendedorID: string; VendedorNombre: string;
  ArchivoPDF: string; RutaPDF: string; RutaPDF_Relativa: string;
  Zona: string; Rol: string; Visible: string; GeneradoEn: string;
}

export interface ObjetivoResumen {
  Scope: string;
  VendedorID: string; VendedorNombre: string;
  Zona: string; Fecha: string;
  Objetivo: number; Acumulado: number;
  RealDia: number; Faltante: number;
  CumplimientoPct: number;
}

export interface FacturacionComparativa {
  PeriodoDesde: string; PeriodoHasta: string; CriterioFecha: string;
  Scope: string; VendedorID: string; VendedorNombre: string;
  ClientesTP: number; ClientesNoTP: number;
  FacturacionTP: number; FacturacionNoTP: number;
  KilosTP: number; KilosNoTP: number;
  PromedioFacturacionTP: number; PromedioFacturacionNoTP: number;
  PromedioKilosTP: number; PromedioKilosNoTP: number;
  DiferenciaFacturacionPct: number; DiferenciaKilosPct: number;
}

// ─── Funciones exportadas ─────────────────────────────────────────────────────

export async function getClientes(): Promise<Cliente[]> {
  const validIds = new Set(
    (await readSheet('pdf_index'))
      .filter(r => r.TipoPDF === 'vendedor')
      .map(r => r.VendedorID)
  );
  const cfg = getConfig();
  return (await readSheet('clientes_oportunidad'))
    .filter(r => validIds.has(r.VendedorID))
    .map(r => ({
      ...r,
      VendedorNombre: cfg.vendor_names[r.VendedorID] ?? r.VendedorNombre,
      PortafolioPct: parseFloat(r.PortafolioPct) || 0,
      Faltan80:      parseInt(r.Faltan80)         || 0,
      Faltan100:     parseInt(r.Faltan100)         || 0,
    })) as Cliente[];
}

export async function getFocos(): Promise<Foco[]> {
  const cfg = getConfig();
  return (await readSheet('foco_productos')).map(r => ({
    ...r,
    VendedorNombre: cfg.vendor_names[r.VendedorID] ?? r.VendedorNombre,
    Rank:          parseInt(r.Rank)          || 0,
    CantClientes:  parseInt(r.CantClientes)  || 0,
  })) as Foco[];
}

export async function getObjetivos(): Promise<ObjetivoResumen[]> {
  return (await readSheet('tp_objetivos_resumen')).map(r => ({
    ...r,
    Objetivo:        parseFloat(r.Objetivo)        || 0,
    Acumulado:       parseInt(r.Acumulado)          || 0,
    RealDia:         parseInt(r.RealDia)            || 0,
    Faltante:        parseFloat(r.Faltante)         || 0,
    CumplimientoPct: parseFloat(r.CumplimientoPct) || 0,
  })) as ObjetivoResumen[];
}

export async function getFacturacion(): Promise<FacturacionComparativa[]> {
  return (await readSheet('tp_facturacion_comparativa')).map(r => ({
    ...r,
    ClientesTP:               parseInt(r.ClientesTP)               || 0,
    ClientesNoTP:             parseInt(r.ClientesNoTP)             || 0,
    FacturacionTP:            parseFloat(r.FacturacionTP)          || 0,
    FacturacionNoTP:          parseFloat(r.FacturacionNoTP)        || 0,
    KilosTP:                  parseFloat(r.KilosTP)                || 0,
    KilosNoTP:                parseFloat(r.KilosNoTP)              || 0,
    PromedioFacturacionTP:    parseFloat(r.PromedioFacturacionTP)  || 0,
    PromedioFacturacionNoTP:  parseFloat(r.PromedioFacturacionNoTP)|| 0,
    PromedioKilosTP:          parseFloat(r.PromedioKilosTP)        || 0,
    PromedioKilosNoTP:        parseFloat(r.PromedioKilosNoTP)      || 0,
    DiferenciaFacturacionPct: parseFloat(r.DiferenciaFacturacionPct) || 0,
    DiferenciaKilosPct:       parseFloat(r.DiferenciaKilosPct)    || 0,
  })) as FacturacionComparativa[];
}

export async function getPdfs(): Promise<PdfEntry[]> {
  return (await readSheet('pdf_index')) as unknown as PdfEntry[];
}
