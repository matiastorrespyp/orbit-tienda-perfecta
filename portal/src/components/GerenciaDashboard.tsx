import { useState } from 'react';
import { Home, Users, Target, FileText, LogOut, RefreshCw, Settings, Search, Bell, ChevronDown, ChevronRight, ArrowUp, ArrowDown, Check, MapPin, Menu, X } from 'lucide-react';
import type { Cliente, Foco, PdfEntry, ObjetivoResumen, FacturacionComparativa } from '../lib/data';

interface Props {
  clientes:    Cliente[];
  focos:       Foco[];
  pdfs:        PdfEntry[];
  vendorNames: Record<string, string>;
  objetivos?:  ObjetivoResumen[];
  facturacion?: FacturacionComparativa[];
}

type Section = 'resumen' | 'clientes' | 'foco' | 'reportes';

function pctBand(p: number) {
  if (p >= 80) return { label: 'TP',          color: '#6EC531' };
  if (p >= 60) return { label: 'Oportunidad', color: '#F0C000' };
  if (p >= 30) return { label: 'Recuperar',   color: '#E87A00' };
  return             { label: 'Crítico',       color: '#E84B4B' };
}

function PctBar({ pct, color }: { pct: number; color: string }) {
  return (
    <div style={{ position: 'relative', width: '100%', background: '#1A1D1A', borderRadius: 99, height: 6, overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, width: `${Math.min(pct, 100)}%`, background: `linear-gradient(90deg, ${color}, ${color}DD)`, borderRadius: 99, transition: 'width .8s cubic-bezier(.2,.8,.2,1)' }}/>
      <div style={{ position: 'absolute', top: -2, bottom: -2, left: '80%', width: 1.5, background: 'rgba(255,255,255,0.3)' }}/>
    </div>
  );
}

function MiniRing({ pct, color, size = 52 }: { pct: number; color: string; size?: number }) {
  const thickness = 5, r = size / 2 - thickness / 2 - 1;
  const c = 2 * Math.PI * r, v = Math.min(Math.max(pct, 0), 100);
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1F231F" strokeWidth={thickness}/>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={thickness}
              strokeLinecap="round" strokeDasharray={`${(v/100)*c} ${c}`}
              transform={`rotate(-90 ${size/2} ${size/2})`}/>
      <text x={size/2} y={size/2+4} textAnchor="middle"
            style={{ fontSize: 12, fontWeight: 600, fill: 'var(--text)', fontFamily: 'Geist Mono, monospace' }}>
        {Math.round(pct)}
      </text>
    </svg>
  );
}

function DonutOportunidad({ n }: { n: number }) {
  const size = 180, thickness = 22, r = size/2 - thickness/2 - 2;
  const c = 2 * Math.PI * r;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1A1D1A" strokeWidth={thickness}/>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#F0C000" strokeWidth={thickness}
              strokeDasharray={`${c * 0.72} ${c * 0.28}`}
              transform={`rotate(-90 ${size/2} ${size/2})`} strokeLinecap="butt"/>
      <text x={size/2} y={size/2-6} textAnchor="middle"
            style={{ fontSize: 30, fontWeight: 600, fill: 'var(--text)', fontFamily: 'Geist Mono, monospace' }}>
        {n}
      </text>
      <text x={size/2} y={size/2+16} textAnchor="middle"
            style={{ fontSize: 10, fill: 'var(--text-3)', letterSpacing: 1.5 }}>
        CLIENTES
      </text>
    </svg>
  );
}

function KPIBig({ label, value, hint, trend, trendUp = true, accent }:
  { label: string; value: string; hint?: string; trend?: string; trendUp?: boolean; accent?: string }) {
  return (
    <div className="kpi-card" style={{ flex: 1, padding: 20, border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', position: 'relative', overflow: 'hidden', minWidth: 0 }}>
      {accent && <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: accent }}/>}
      <div style={{ fontSize: 11, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 500, marginBottom: 12 }}>{label}</div>
      <div className="mono" style={{ fontSize: 30, fontWeight: 500, letterSpacing: -0.4, lineHeight: 1, marginBottom: 8 }}>{value}</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 12 }}>
        {trend && (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 3, color: trendUp ? 'var(--green)' : 'var(--red)' }}>
            {trendUp ? <ArrowUp size={11} strokeWidth={2.4}/> : <ArrowDown size={11} strokeWidth={2.4}/>}
            <span className="mono">{trend}</span>
          </span>
        )}
        {hint && <span style={{ color: 'var(--text-3)' }}>{hint}</span>}
      </div>
    </div>
  );
}

export default function GerenciaDashboard({ clientes, focos, pdfs, vendorNames, objetivos = [], facturacion = [] }: Props) {
  const [active,      setActive]      = useState<Section>('resumen');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [search,      setSearch]      = useState('');

  const latestCliente = clientes.length > 0
    ? clientes.reduce((max, c) => String(c.Fecha) > String(max.Fecha) ? c : max, clientes[0])
    : null;

  const fecha = latestCliente?.Fecha ?? '-';
  const dia   = latestCliente?.Dia   ?? '-';
  const totalC = clientes.length;
  const avgPct = totalC > 0 ? clientes.reduce((s, c) => s + c.PortafolioPct, 0) / totalC : 0;
  const conTP    = clientes.filter(c => c.TP_Sistema === 'SI').length;
  const urgentes = clientes.filter(c => c.Faltan80 <= 2 && c.Faltan80 > 0).length;

  const vendors = [...new Set(clientes.map(c => c.VendedorNombre))].sort();
  const byVendor = vendors.map(v => {
    const rows = clientes.filter(c => c.VendedorNombre === v);
    const id   = rows[0]?.VendedorID ?? '';
    const avg  = rows.reduce((s, c) => s + c.PortafolioPct, 0) / rows.length;
    const tp   = rows.filter(c => c.TP_Sistema === 'SI').length;
    const urg  = rows.filter(c => c.Faltan80 <= 2 && c.Faltan80 > 0).length;
    const topF = focos.find(f => f.Scope === 'vendedor' && f.VendedorNombre === v && f.Rank === 1);
    const pdf  = pdfs.find(p => p.VendedorID === id && p.TipoPDF === 'vendedor');
    return { v, id, count: rows.length, avg, tp, urg, topF, pdf };
  }).sort((a, b) => b.urg - a.urg);

  const topSkus = focos.filter(f => f.Scope === 'general').sort((a, b) => a.Rank - b.Rank);
  const pdfGerencial = pdfs.find(p => p.TipoPDF === 'gerencia');

  const filteredClientes = search.trim()
    ? clientes.filter(c =>
        c.RazonSocial.toLowerCase().includes(search.toLowerCase()) ||
        c.VendedorNombre.toLowerCase().includes(search.toLowerCase()) ||
        c.Localidad.toLowerCase().includes(search.toLowerCase()))
    : clientes;

  const clientesSorted = [...filteredClientes].sort((a, b) => a.Faltan80 - b.Faltan80);

  const navItems: { k: Section; label: string; Icon: typeof Home }[] = [
    { k: 'resumen',   label: 'Resumen',          Icon: Home    },
    { k: 'clientes',  label: 'Clientes zona',    Icon: Users   },
    { k: 'foco',      label: 'Productos foco',   Icon: Target  },
    { k: 'reportes',  label: 'Reportes y PDFs',  Icon: FileText},
  ];

  const sectionTitle: Record<Section, string> = {
    resumen:  'Resumen ejecutivo',
    clientes: 'Clientes zona oportunidad',
    foco:     'Productos foco',
    reportes: 'Reportes y PDFs',
  };

  const SidebarContent = () => (
    <>
      {/* Brand */}
      <div style={{ padding: '20px 18px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
        <img src="/assets/orbit-mark.png" alt="" className="orbit-mark"
             style={{ width: 40, height: 40, flexShrink: 0, filter: 'drop-shadow(0 0 12px rgba(110,197,49,0.35))', transition: 'transform .9s cubic-bezier(.2,.8,.2,1), filter .3s' }}/>
        <img src="/assets/orbit-wordmark.png" alt="Orbit · Tienda Perfecta"
             style={{ height: 28, width: 'auto', flexShrink: 0, filter: 'invert(1) brightness(1.1)' }}/>
        <div style={{ width: 1, height: 26, background: 'var(--line)', marginLeft: 2 }}/>
        <img src="/assets/pyp-mark.png" alt="P&P" className="pyp-mark"
             style={{ height: 26, width: 'auto', flexShrink: 0, filter: 'drop-shadow(0 0 8px rgba(56,110,255,0.45)) brightness(1.15) saturate(1.2)', transition: 'transform .35s, filter .3s' }}/>
      </div>

      {/* User card */}
      <div style={{ margin: '0 14px 14px', padding: '10px 12px', border: '1px solid var(--line)', borderRadius: 9, background: 'var(--surface)', display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ width: 28, height: 28, borderRadius: 6, background: '#222722', display: 'grid', placeItems: 'center', color: 'var(--green)', fontWeight: 600, fontSize: 12 }}>MT</div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 12, fontWeight: 500 }}>Matías Torres</div>
          <div style={{ fontSize: 10.5, color: 'var(--text-3)' }}>Gerencia comercial</div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ padding: '0 10px', display: 'flex', flexDirection: 'column', gap: 1 }}>
        <div style={{ fontSize: 10, color: 'var(--text-4)', letterSpacing: 1.6, textTransform: 'uppercase', padding: '8px 10px 6px' }}>Operación</div>
        {navItems.map(({ k, label, Icon }) => {
          const isActive = active === k;
          return (
            <button key={k} onClick={() => { setActive(k); setSidebarOpen(false); }}
                    className={isActive ? '' : 'nav-btn'} style={{
              display: 'flex', alignItems: 'center', gap: 11, padding: '9px 10px',
              border: 'none', background: isActive ? 'var(--surface-2)' : 'transparent',
              color: isActive ? 'var(--text)' : 'var(--text-2)', borderRadius: 7,
              cursor: 'pointer', textAlign: 'left', fontSize: 13, fontFamily: 'inherit',
              fontWeight: 500, position: 'relative', width: '100%',
            }}>
              {isActive && <span style={{ position: 'absolute', left: -10, top: 8, bottom: 8, width: 2, background: 'var(--green)', borderRadius: 2 }}/>}
              <Icon size={15} color={isActive ? 'var(--green)' : 'currentColor'} />
              <span style={{ flex: 1 }}>{label}</span>
              {k === 'clientes' && (
                <span className="mono" style={{ fontSize: 10, color: 'var(--text-3)', background: 'var(--surface-3)', padding: '1px 6px', borderRadius: 99 }}>
                  {totalC}
                </span>
              )}
              {k === 'foco' && urgentes > 0 && (
                <span style={{ width: 6, height: 6, borderRadius: 99, background: 'var(--yellow)', boxShadow: '0 0 8px rgba(240,192,0,0.6)' }}/>
              )}
            </button>
          );
        })}
      </nav>

      <div style={{ flex: 1 }}/>

      {/* Sync status */}
      <div style={{ margin: '12px 14px', padding: 14, border: '1px solid var(--line)', borderRadius: 9, background: 'linear-gradient(140deg, rgba(110,197,49,0.08), transparent 60%)' }}>
        <div style={{ fontSize: 10.5, color: 'var(--green)', letterSpacing: 1.4, textTransform: 'uppercase', fontWeight: 600, marginBottom: 6 }}>Datos CSV</div>
        <div style={{ fontSize: 11.5, color: 'var(--text-2)', lineHeight: 1.45 }}>
          Zona {dia} · {fecha}<br/>
          <span style={{ color: 'var(--text-3)', fontSize: 10.5 }}>{totalC} clientes en zona 60-79%</span>
        </div>
      </div>

      {/* Footer actions */}
      <div style={{ padding: '10px 14px 16px', display: 'flex', gap: 6, borderTop: '1px solid var(--line)' }}>
        <button className="icon-btn" style={{ width: 30, height: 30, borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', color: 'var(--text-2)', cursor: 'pointer', display: 'grid', placeItems: 'center' }}
                onClick={() => window.location.reload()}>
          <RefreshCw size={14}/>
        </button>
        <div style={{ flex: 1 }}/>
        <a href="/api/logout" style={{ textDecoration: 'none' }}>
          <button className="icon-btn" style={{ width: 30, height: 30, borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', color: 'var(--text-3)', cursor: 'pointer', display: 'grid', placeItems: 'center' }}>
            <LogOut size={14}/>
          </button>
        </a>
      </div>
    </>
  );

  return (
    <div style={{ display: 'flex', minHeight: '100vh', position: 'relative', zIndex: 1 }}>
      {/* Mobile overlay */}
      <div className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`} onClick={() => setSidebarOpen(false)}/>

      {/* Sidebar */}
      <aside className={`sidebar-fixed ${sidebarOpen ? 'open' : ''}`} style={{
        width: 232, height: '100vh', position: 'sticky', top: 0,
        borderRight: '1px solid var(--line)', background: 'var(--bg-1)',
        display: 'flex', flexDirection: 'column', zIndex: 5, flexShrink: 0,
      }}>
        <SidebarContent/>
      </aside>

      <main style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
        {/* TopBar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '18px 28px', borderBottom: '1px solid var(--line)', background: 'rgba(10,11,10,0.85)', backdropFilter: 'blur(8px)', position: 'sticky', top: 0, zIndex: 4, flexShrink: 0 }}>
          <button className="hamburger icon-btn" onClick={() => setSidebarOpen(s => !s)}
                  style={{ display: 'none', width: 30, height: 30, borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', color: 'var(--text-2)', cursor: 'pointer', placeItems: 'center' }}>
            {sidebarOpen ? <X size={14}/> : <Menu size={14}/>}
          </button>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-3)', fontSize: 11.5, letterSpacing: 0.6, marginBottom: 2 }}>
              <span>Orbit</span><ChevronRight size={11}/><span>{sectionTitle[active]}</span>
            </div>
            <h1 style={{ margin: 0, fontSize: 20, fontWeight: 600, letterSpacing: -0.3 }}>{sectionTitle[active]}</h1>
          </div>
          <div style={{ flex: 1 }}/>
          <div className="search-shell" style={{ display: 'flex', alignItems: 'center', gap: 8, background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: 8, padding: '7px 12px', minWidth: 240 }}>
            <Search size={14} color="var(--text-3)"/>
            <input placeholder="Buscar cliente, vendedor, SKU…" value={search} onChange={e => setSearch(e.target.value)}
                   style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none', color: 'var(--text)', fontSize: 13, fontFamily: 'inherit' }}/>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 11px', border: '1px solid var(--line)', borderRadius: 99, fontSize: 12 }}>
            <span className="live-dot" style={{ width: 6, height: 6, borderRadius: 99, background: 'var(--green)' }}/>
            <span style={{ color: 'var(--text-2)' }}>Zona</span>
            <span className="mono" style={{ fontWeight: 500 }}>{dia} · {fecha}</span>
          </div>
          {pdfGerencial && (
            <a href={`/api/pdf?ruta=${encodeURIComponent(pdfGerencial.RutaPDF_Relativa)}`} target="_blank" rel="noreferrer"
               style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '7px 14px', background: 'var(--green)', color: '#0A0B0A', borderRadius: 8, fontSize: 12, fontWeight: 700, textDecoration: 'none', letterSpacing: 0.5 }}>
              <FileText size={13}/> PDF
            </a>
          )}
        </div>

        {/* Content */}
        <div style={{ flex: 1, padding: '24px 28px 48px', overflow: 'auto' }}>

          {/* â”€â”€ RESUMEN â”€â”€ */}
          {active === 'resumen' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              {/* KPIs */}
              <div className="kpi-grid-4" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
                <KPIBig label="Clientes zona oportunidad" value={String(totalC)} hint="60-79% portafolio" accent="var(--yellow)"/>
                <KPIBig label="Portafolio promedio" value={`${avgPct.toFixed(1)}%`} hint="zona 60-79%"/>
                <KPIBig label="Inscriptos TP" value={String(conTP)} hint="tienen TP activo en sistema" accent="var(--green)" trendUp/>
                <KPIBig label="Urgentes hoy" value={String(urgentes)} hint="a 1-2 SKUs del TP" trend={urgentes > 0 ? '⚡ prioridad' : undefined} trendUp={false} accent="var(--orange)"/>
              </div>

              {/* Objetivos TP del mes */}
              {(() => {
                const gen      = objetivos.find(o => o.Scope === 'general');
                const vends    = objetivos.filter(o => o.Scope === 'vendedor');
                const taxRows  = objetivos.filter(o => o.Scope === 'taxonomia');
                if (!gen) return null;
                const cc = (p: number) => p >= 80 ? 'var(--green)' : p >= 50 ? 'var(--yellow)' : 'var(--orange)';
                return (
                  <div style={{ border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', overflow: 'hidden' }}>
                    <div style={{ padding: '18px 22px 14px', borderBottom: '1px solid var(--line)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div>
                        <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.5, textTransform: 'uppercase', fontWeight: 600, marginBottom: 4 }}>Mes actual</div>
                        <div style={{ fontSize: 16, fontWeight: 600 }}>Objetivos TP</div>
                        <div style={{ fontSize: 10.5, color: 'var(--text-4)', marginTop: 4 }}>Datos objetivos al {gen.Fecha}</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <MiniRing pct={gen.CumplimientoPct} color={cc(gen.CumplimientoPct)} size={56}/>
                        <div>
                          <div className="mono" style={{ fontSize: 22, fontWeight: 600, color: cc(gen.CumplimientoPct) }}>{gen.CumplimientoPct.toFixed(1)}%</div>
                          <div style={{ fontSize: 10.5, color: 'var(--text-3)' }}>cumplimiento general</div>
                        </div>
                      </div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', borderBottom: '1px solid var(--line)' }}>
                      {([
                        { label: 'Objetivo',  value: gen.Objetivo.toFixed(0)  },
                        { label: 'Acumulado', value: String(gen.Acumulado)    },
                        { label: 'Real hoy',  value: String(gen.RealDia)      },
                        { label: 'Faltante',  value: gen.Faltante.toFixed(0)  },
                      ] as {label:string;value:string}[]).map((item, i) => (
                        <div key={i} style={{ padding: '14px 22px', borderRight: i < 3 ? '1px solid var(--line)' : 'none' }}>
                          <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 600, marginBottom: 6 }}>{item.label}</div>
                          <div className="mono" style={{ fontSize: 20, fontWeight: 500 }}>{item.value}</div>
                        </div>
                      ))}
                    </div>
                    {taxRows.length > 0 && (
                      <>
                        <div style={{ display: 'grid', gridTemplateColumns: '60px 90px 80px 80px 80px 90px', gap: 8, padding: '8px 22px', fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 600, borderBottom: '1px solid var(--line)' }}>
                          <div>Tax.</div><div style={{ textAlign:'right' }}>Objetivo</div><div style={{ textAlign:'right' }}>Acum.</div><div style={{ textAlign:'right' }}>Real día</div><div style={{ textAlign:'right' }}>Faltan</div><div style={{ textAlign:'right' }}>Cumpl. %</div>
                        </div>
                        {taxRows.map(t => (
                          <div key={t.VendedorNombre} className="row-hover" style={{ display: 'grid', gridTemplateColumns: '60px 90px 80px 80px 80px 90px', gap: 8, padding: '10px 22px', alignItems: 'center', borderBottom: '1px solid var(--line)', fontSize: 12.5 }}>
                            <div style={{ fontWeight: 600 }}>{t.VendedorNombre}</div>
                            <div className="mono" style={{ textAlign:'right', color: 'var(--text-2)' }}>{t.Objetivo.toFixed(0)}</div>
                            <div className="mono" style={{ textAlign:'right', color: 'var(--text-2)' }}>{t.Acumulado}</div>
                            <div className="mono" style={{ textAlign:'right', color: 'var(--text-2)' }}>{t.RealDia}</div>
                            <div className="mono" style={{ textAlign:'right', color: 'var(--text-2)' }}>{t.Faltante.toFixed(0)}</div>
                            <div className="mono" style={{ textAlign:'right', fontWeight: 600, color: cc(t.CumplimientoPct) }}>{t.CumplimientoPct.toFixed(1)}%</div>
                          </div>
                        ))}
                      </>
                    )}
                    {vends.length > 0 && (
                      <>
                        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 90px 80px 80px 80px 90px', gap: 8, padding: '8px 22px', fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 600, borderBottom: '1px solid var(--line)' }}>
                          <div>Vendedor</div><div style={{ textAlign:'right' }}>Objetivo</div><div style={{ textAlign:'right' }}>Acum.</div><div style={{ textAlign:'right' }}>Real día</div><div style={{ textAlign:'right' }}>Faltan</div><div style={{ textAlign:'right' }}>Cumpl. %</div>
                        </div>
                        {vends.map(v => (
                          <div key={v.VendedorID} className="row-hover" style={{ display: 'grid', gridTemplateColumns: '1.2fr 90px 80px 80px 80px 90px', gap: 8, padding: '10px 22px', alignItems: 'center', borderBottom: '1px solid var(--line)', fontSize: 12.5 }}>
                            <div style={{ fontWeight: 500 }}>{v.VendedorNombre}</div>
                            <div className="mono" style={{ textAlign:'right', color: 'var(--text-2)' }}>{v.Objetivo.toFixed(0)}</div>
                            <div className="mono" style={{ textAlign:'right', color: 'var(--text-2)' }}>{v.Acumulado}</div>
                            <div className="mono" style={{ textAlign:'right', color: 'var(--text-2)' }}>{v.RealDia}</div>
                            <div className="mono" style={{ textAlign:'right', color: 'var(--text-2)' }}>{v.Faltante.toFixed(0)}</div>
                            <div className="mono" style={{ textAlign:'right', fontWeight: 600, color: cc(v.CumplimientoPct) }}>{v.CumplimientoPct.toFixed(1)}%</div>
                          </div>
                        ))}
                      </>
                    )}
                  </div>
                );
              })()}

              {/* Alertas */}
              {urgentes > 0 && (
                <div style={{ padding: '14px 18px', background: 'rgba(232,122,0,0.08)', border: '1px solid rgba(232,122,0,0.25)', borderRadius: 10 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--orange)', marginBottom: 6 }}>
                    ⚡ {urgentes} cliente{urgentes > 1 ? 's' : ''} a 1-2 SKUs del TP — cerrar hoy
                  </div>
                  {topSkus[0] && (
                    <div style={{ fontSize: 11.5, color: 'var(--text-2)' }}>
                      SKU #1 del día: <strong style={{ color: 'var(--text)' }}>{topSkus[0].Articulo}</strong> — necesario en {topSkus[0].CantClientes} clientes
                    </div>
                  )}
                </div>
              )}

              {/* Facturación TP vs No TP */}
              {(() => {
                const gen = facturacion.find(f => f.Scope === 'general');
                if (!gen) return null;
                const fmt = (n: number) =>
                  n >= 1_000_000 ? `$${(n/1_000_000).toFixed(1)}M`
                  : n >= 1_000   ? `$${(n/1_000).toFixed(0)}k`
                  : `$${n.toFixed(0)}`;
                const fmtKg = (n: number) =>
                  n >= 1_000 ? `${(n/1_000).toFixed(1)}t` : `${n.toFixed(0)} kg`;
                const difColor = (d: number) => d >= 0 ? 'var(--green)' : 'var(--red, #E84B4B)';
                const difSign  = (d: number) => d >= 0 ? `+${d.toFixed(1)}%` : `${d.toFixed(1)}%`;
                return (
                  <div style={{ border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', overflow: 'hidden' }}>
                    <div style={{ padding: '18px 22px 14px', borderBottom: '1px solid var(--line)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div>
                        <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.5, textTransform: 'uppercase', fontWeight: 600, marginBottom: 4 }}>
                          {gen.PeriodoDesde} → {gen.PeriodoHasta} · {gen.CriterioFecha}
                        </div>
                        <div style={{ fontSize: 16, fontWeight: 600 }}>Facturación TP vs No TP</div>
                      </div>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <span style={{ padding: '4px 10px', borderRadius: 99, background: 'rgba(110,197,49,0.12)', border: '1px solid var(--green-line)', fontSize: 11, color: 'var(--green)', fontWeight: 600 }}>
                          TP: {gen.ClientesTP} clientes
                        </span>
                        <span style={{ padding: '4px 10px', borderRadius: 99, background: 'rgba(255,255,255,0.04)', border: '1px solid var(--line)', fontSize: 11, color: 'var(--text-3)', fontWeight: 600 }}>
                          No TP: {gen.ClientesNoTP} clientes
                        </span>
                      </div>
                    </div>
                    {/* Métricas principales */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', borderBottom: '1px solid var(--line)' }}>
                      {([
                        { label: 'Fact. TP',    value: fmt(gen.FacturacionTP),    sub: `prom ${fmt(gen.PromedioFacturacionTP)}`, color: 'var(--green)' },
                        { label: 'Fact. No TP', value: fmt(gen.FacturacionNoTP),  sub: `prom ${fmt(gen.PromedioFacturacionNoTP)}`, color: 'var(--text)' },
                        { label: 'Kilos TP',    value: fmtKg(gen.KilosTP),        sub: `prom ${fmtKg(gen.PromedioKilosTP)}`, color: 'var(--green)' },
                        { label: 'Kilos No TP', value: fmtKg(gen.KilosNoTP),      sub: `prom ${fmtKg(gen.PromedioKilosNoTP)}`, color: 'var(--text)' },
                      ] as {label:string;value:string;sub:string;color:string}[]).map((item, i) => (
                        <div key={i} style={{ padding: '16px 22px', borderRight: i < 3 ? '1px solid var(--line)' : 'none' }}>
                          <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 600, marginBottom: 6 }}>{item.label}</div>
                          <div className="mono" style={{ fontSize: 22, fontWeight: 500, color: item.color, marginBottom: 4 }}>{item.value}</div>
                          <div style={{ fontSize: 10.5, color: 'var(--text-4)' }}>{item.sub}</div>
                        </div>
                      ))}
                    </div>
                    {/* Diferencias */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: '1px solid var(--line)' }}>
                      <div style={{ padding: '12px 22px', borderRight: '1px solid var(--line)', display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 600 }}>Dif. Facturación</div>
                        <div className="mono" style={{ fontSize: 18, fontWeight: 600, color: difColor(gen.DiferenciaFacturacionPct) }}>{difSign(gen.DiferenciaFacturacionPct)}</div>
                        <div style={{ fontSize: 10.5, color: 'var(--text-4)' }}>TP vs No TP</div>
                      </div>
                      <div style={{ padding: '12px 22px', display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 600 }}>Dif. Kilos</div>
                        <div className="mono" style={{ fontSize: 18, fontWeight: 600, color: difColor(gen.DiferenciaKilosPct) }}>{difSign(gen.DiferenciaKilosPct)}</div>
                        <div style={{ fontSize: 10.5, color: 'var(--text-4)' }}>TP vs No TP</div>
                      </div>
                    </div>
                    {/* Tabla por vendedor */}
                    {facturacion.filter(f => f.Scope === 'vendedor').length > 0 && (
                      <>
                        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 100px 100px 100px 100px 90px 90px', gap: 8, padding: '8px 22px', fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 600, borderBottom: '1px solid var(--line)' }}>
                          <div>Vendedor</div><div style={{ textAlign:'right' }}>Fact. TP</div><div style={{ textAlign:'right' }}>Fact. No TP</div><div style={{ textAlign:'right' }}>Kg TP</div><div style={{ textAlign:'right' }}>Kg No TP</div><div style={{ textAlign:'right' }}>Dif. Fact.</div><div style={{ textAlign:'right' }}>Dif. Kg</div>
                        </div>
                        {facturacion.filter(f => f.Scope === 'vendedor').map(v => (
                          <div key={v.VendedorID} className="row-hover" style={{ display: 'grid', gridTemplateColumns: '1.2fr 100px 100px 100px 100px 90px 90px', gap: 8, padding: '10px 22px', alignItems: 'center', borderBottom: '1px solid var(--line)', fontSize: 12.5 }}>
                            <div style={{ fontWeight: 500 }}>{v.VendedorNombre}</div>
                            <div className="mono" style={{ textAlign:'right', color: 'var(--green)' }}>{fmt(v.FacturacionTP)}</div>
                            <div className="mono" style={{ textAlign:'right', color: 'var(--text-2)' }}>{fmt(v.FacturacionNoTP)}</div>
                            <div className="mono" style={{ textAlign:'right', color: 'var(--green)' }}>{fmtKg(v.KilosTP)}</div>
                            <div className="mono" style={{ textAlign:'right', color: 'var(--text-2)' }}>{fmtKg(v.KilosNoTP)}</div>
                            <div className="mono" style={{ textAlign:'right', fontWeight: 600, color: difColor(v.DiferenciaFacturacionPct) }}>{difSign(v.DiferenciaFacturacionPct)}</div>
                            <div className="mono" style={{ textAlign:'right', fontWeight: 600, color: difColor(v.DiferenciaKilosPct) }}>{difSign(v.DiferenciaKilosPct)}</div>
                          </div>
                        ))}
                      </>
                    )}
                  </div>
                );
              })()}

              {/* Tabla vendedores + Donut */}
              <div className="vendor-grid" style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 16 }}>
                {/* Tabla vendedores */}
                <div style={{ border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', padding: 0, overflow: 'hidden' }}>
                  <div style={{ padding: '18px 22px 14px', borderBottom: '1px solid var(--line)' }}>
                    <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.5, textTransform: 'uppercase', fontWeight: 600, marginBottom: 4 }}>Performance zona</div>
                    <div style={{ fontSize: 16, fontWeight: 600 }}>Por vendedor</div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '36px 1.2fr 90px 100px 80px 60px 48px', gap: 8, padding: '8px 22px', fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 600 }}>
                    <div>#</div><div>Vendedor</div><div>Portafolio</div><div style={{ textAlign:'center', whiteSpace:'normal', lineHeight:1.3 }}>Clientes posibilidad</div>
                    <div style={{ textAlign:'center', whiteSpace:'normal', lineHeight:1.3 }}>TP activos</div><div style={{ textAlign:'center' }}>Urg.</div><div></div>
                  </div>
                  {byVendor.map((v, i) => {
                    const color = v.avg >= 75 ? '#6EC531' : v.avg >= 65 ? '#F0C000' : '#E87A00';
                    return (
                      <div key={v.v} className="row-hover" style={{ display: 'grid', gridTemplateColumns: '36px 1.2fr 90px 100px 80px 60px 48px', gap: 8, padding: '12px 22px', alignItems: 'center', borderBottom: '1px solid var(--line)' }}>
                        <div className="mono" style={{ fontSize: 11, color: 'var(--text-3)' }}>{String(i+1).padStart(2,'0')}</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{ width: 28, height: 28, borderRadius: 7, background: `${color}20`, border: `1px solid ${color}40`, color, display: 'grid', placeItems: 'center', fontSize: 10, fontWeight: 700 }}>
                            {v.v.slice(0,2)}
                          </div>
                          <a href={`/vendedor?id=${v.id}`} style={{ fontSize: 13, fontWeight: 500, color: 'var(--text)', textDecoration: 'none' }} onMouseEnter={e => (e.currentTarget.style.color='var(--green)')} onMouseLeave={e => (e.currentTarget.style.color='var(--text)')}>
                            {v.v}
                          </a>
                        </div>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                            <span className="mono" style={{ fontSize: 12, fontWeight: 500, color }}>{v.avg.toFixed(1)}%</span>
                            <span style={{ fontSize: 10, color: 'var(--text-4)' }}>meta 80</span>
                          </div>
                          <PctBar pct={v.avg} color={color}/>
                        </div>
                        <div className="mono" style={{ textAlign:'center', fontSize: 13 }}>{v.count}</div>
                        <div style={{ textAlign:'center' }}>
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 3, color: 'var(--green)', fontSize: 11, fontWeight: 600 }}>
                            <Check size={11} strokeWidth={2.6}/> {v.tp}
                          </span>
                        </div>
                        <div style={{ textAlign:'center' }}>
                          {v.urg > 0
                            ? <span style={{ background: 'rgba(232,122,0,0.15)', color: 'var(--orange)', borderRadius: 4, padding: '2px 7px', fontSize: 11, fontWeight: 600 }}>⚡{v.urg}</span>
                            : <span style={{ color: 'var(--text-4)', fontSize: 11 }}>—</span>}
                        </div>
                        <div>
                          {v.pdf && <a href={`/api/pdf?ruta=${encodeURIComponent(v.pdf.RutaPDF_Relativa)}`} target="_blank" rel="noreferrer"
                               style={{ fontSize: 11, color: 'var(--green)', textDecoration: 'none', fontWeight: 600 }}>↓ PDF</a>}
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Donut zona oportunidad */}
                <div style={{ border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', padding: 20 }}>
                  <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.5, textTransform: 'uppercase', fontWeight: 600, marginBottom: 4 }}>Estado portafolio</div>
                  <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 14 }}>Distribución clientes</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 18 }}>
                    <DonutOportunidad n={totalC}/>
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 10 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{ width: 8, height: 8, borderRadius: 2, background: '#F0C000', boxShadow: '0 0 8px rgba(240,192,0,0.6)', flexShrink: 0 }}/>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12.5, marginBottom: 2 }}>
                            <span>Oportunidad</span><span className="mono" style={{ color: 'var(--text-2)' }}>{totalC}</span>
                          </div>
                          <div style={{ fontSize: 10.5, color: 'var(--text-3)' }}>60–79% portafolio</div>
                        </div>
                      </div>
                      <div style={{ padding: '10px 12px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--line)', borderRadius: 8 }}>
                        <div style={{ fontSize: 10.5, color: 'var(--text-4)', lineHeight: 1.5 }}>
                          Solo se exportan clientes en zona oportunidad.<br/>
                          Otras bandas: sin dato disponible.
                        </div>
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-3)' }}>
                        <strong style={{ color: 'var(--green)' }}>{conTP}</strong> con TP activo · <strong style={{ color: 'var(--orange)' }}>{urgentes}</strong> urgentes
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Top SKUs preview */}
              <div style={{ border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', padding: 0, overflow: 'hidden' }}>
                <div style={{ padding: '18px 22px 12px', borderBottom: '1px solid var(--line)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.5, textTransform: 'uppercase', fontWeight: 600, marginBottom: 4 }}>Top SKUs por penetración</div>
                    <div style={{ fontSize: 16, fontWeight: 600 }}>Productos foco del día</div>
                  </div>
                  <button onClick={() => setActive('foco')} style={{ fontSize: 11, color: 'var(--green)', background: 'none', border: '1px solid var(--green-line)', borderRadius: 6, padding: '4px 10px', cursor: 'pointer', fontFamily: 'inherit' }}>Ver todos →</button>
                </div>
                <div style={{ padding: '12px 22px 18px', display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {topSkus.slice(0, 5).map(p => {
                    const max = topSkus[0]?.CantClientes || 1;
                    const isTop = p.Rank <= 3;
                    return (
                      <div key={p.Rank} className="foco-row" style={{ display: 'grid', gridTemplateColumns: '28px 1fr 60px', gap: 10, alignItems: 'center', padding: '6px 0' }}>
                        <span className="mono" style={{ fontSize: 11, fontWeight: 500, color: isTop ? 'var(--green)' : 'var(--text-3)' }}>{String(p.Rank).padStart(2,'0')}</span>
                        <div>
                          <div style={{ fontSize: 12.5, marginBottom: 4 }}>{p.Articulo}</div>
                          <div className="foco-bar" style={{ height: 5, background: '#1A1D1A', borderRadius: 99, overflow: 'hidden' }}>
                            <div style={{ width: `${(p.CantClientes/max)*100}%`, height: '100%', background: isTop ? 'linear-gradient(90deg, var(--green), #4A8A1C)' : '#3A4A30' }}/>
                          </div>
                        </div>
                        <div className="mono" style={{ textAlign: 'right', fontSize: 12, color: 'var(--text-2)' }}>
                          {p.CantClientes} <span style={{ color: 'var(--text-4)' }}>cli</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* â”€â”€ CLIENTES â”€â”€ */}
          {active === 'clientes' && (
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-3)', marginBottom: 16 }}>
                {filteredClientes.length} cliente{filteredClientes.length !== 1 ? 's' : ''} {search ? `que coinciden con "${search}"` : 'en zona oportunidad 60-79%'} · ordenados por urgencia (menos SKUs faltantes primero)
              </div>
              <div className="table-scroll" style={{ border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', overflow: 'hidden' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr 0.9fr 110px 70px 60px', gap: 10, padding: '10px 22px', borderBottom: '1px solid var(--line)', fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 600, minWidth: 700 }}>
                  <div>Cliente</div><div>Vendedor</div><div>Localidad</div><div>Portafolio</div><div style={{ textAlign:'center' }}>Faltan 80</div><div style={{ textAlign:'center' }}>TP</div>
                </div>
                {clientesSorted.map((c, i) => {
                  const band = pctBand(c.PortafolioPct);
                  return (
                    <div key={i} className="row-hover" style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr 0.9fr 110px 70px 60px', gap: 10, padding: '11px 22px', alignItems: 'start', borderBottom: '1px solid var(--line)', fontSize: 12.5, minWidth: 700 }}>
                      <div style={{ minWidth: 0 }}>
                        <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontWeight: 500 }}>{c.RazonSocial}</div>
                        {c.Faltan80 <= 2 && c.Faltan80 > 0 && <div style={{ fontSize: 10, color: 'var(--orange)', marginTop: 2 }}>⚡ A {c.Faltan80} SKU{c.Faltan80>1?'s':''} del TP</div>}
                        {c.SKUsFaltan100 && (
                          <div style={{ marginTop: 5 }}>
                            <div style={{ fontSize: 10, color: 'var(--text-4)', marginBottom: 4, letterSpacing: 0.5 }}>Opciones no compradas:</div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                              {(() => {
                                const prio = new Set(c.SKUsFaltan80 ? c.SKUsFaltan80.split('|').map(s => s.trim()) : []);
                                return c.SKUsFaltan100.split('|').map((sku, idx) => {
                                  const s = sku.trim();
                                  const isPrio = prio.has(s);
                                  return (
                                    <span key={idx} style={{
                                      fontSize: 10,
                                      background: isPrio ? 'rgba(110,197,49,0.10)' : 'rgba(255,255,255,0.05)',
                                      border: `1px solid ${isPrio ? 'rgba(110,197,49,0.45)' : 'var(--line)'}`,
                                      borderRadius: 4,
                                      padding: '1px 6px',
                                      color: isPrio ? 'var(--green)' : 'var(--text-3)',
                                      whiteSpace: 'nowrap',
                                    }}>
                                      {s}
                                    </span>
                                  );
                                });
                              })()}
                            </div>
                          </div>
                        )}
                      </div>
                      <div style={{ color: 'var(--text-2)' }}>
                        <a href={`/vendedor?id=${c.VendedorID}`} style={{ color: 'var(--text-2)', textDecoration: 'none' }}
                           onMouseEnter={e => (e.currentTarget.style.color='var(--green)')} onMouseLeave={e => (e.currentTarget.style.color='var(--text-2)')}>
                          {c.VendedorNombre}
                        </a>
                      </div>
                      <div style={{ color: 'var(--text-2)', fontSize: 12, display: 'flex', alignItems: 'center', gap: 4 }}>
                        <MapPin size={10} color="var(--text-4)"/>{c.Localidad}
                      </div>
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                          <span className="mono" style={{ fontSize: 12, fontWeight: 500, color: band.color }}>{c.PortafolioPct.toFixed(0)}%</span>
                        </div>
                        <PctBar pct={c.PortafolioPct} color={band.color}/>
                      </div>
                      <div className="mono" style={{ textAlign:'center', color: c.Faltan80 === 0 ? 'var(--text-4)' : 'var(--text-2)', fontSize: 13 }}>
                        {c.Faltan80 === 0 ? '—' : c.Faltan80}
                      </div>
                      <div style={{ textAlign:'center' }}>
                        {c.TP_Sistema === 'SI'
                          ? <span style={{ display:'inline-flex', alignItems:'center', gap:3, color:'var(--green)', fontSize:11, fontWeight:600 }}><Check size={11} strokeWidth={2.6}/> SI</span>
                          : <span style={{ color: 'var(--text-4)', fontSize: 11 }}>—</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* â”€â”€ FOCO â”€â”€ */}
          {active === 'foco' && (
            <div style={{ border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', padding: 0, overflow: 'hidden' }}>
              <div style={{ padding: '18px 22px 14px', borderBottom: '1px solid var(--line)' }}>
                <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.5, textTransform: 'uppercase', fontWeight: 600, marginBottom: 4 }}>Ranking 1-10 · zona {dia}</div>
                <div style={{ fontSize: 16, fontWeight: 600 }}>SKUs con mayor penetración requerida</div>
              </div>
              <div style={{ padding: '16px 22px', display: 'flex', flexDirection: 'column', gap: 8 }}>
                {topSkus.map(p => {
                  const max = topSkus[0]?.CantClientes || 1;
                  const isTop = p.Rank <= 3;
                  return (
                    <div key={p.Rank} className="foco-row" style={{ display: 'grid', gridTemplateColumns: '36px 1fr 80px', gap: 14, alignItems: 'center', padding: '8px 0' }}>
                      <span className="mono" style={{ fontSize: 14, fontWeight: 600, color: isTop ? 'var(--green)' : 'var(--text-3)' }}>{String(p.Rank).padStart(2,'0')}</span>
                      <div>
                        <div style={{ fontSize: 13.5, fontWeight: isTop ? 600 : 400, marginBottom: 6 }}>{p.Articulo}</div>
                        <div className="foco-bar" style={{ height: 6, background: '#1A1D1A', borderRadius: 99, overflow: 'hidden' }}>
                          <div style={{ width: `${(p.CantClientes/max)*100}%`, height: '100%', background: isTop ? 'linear-gradient(90deg, var(--green), #4A8A1C)' : '#3A4A30', transition: 'width .8s' }}/>
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div className="mono" style={{ fontSize: 18, fontWeight: 500, color: isTop ? 'var(--green)' : 'var(--text)' }}>{p.CantClientes}</div>
                        <div style={{ fontSize: 10.5, color: 'var(--text-4)' }}>clientes</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* â”€â”€ REPORTES â”€â”€ */}
          {active === 'reportes' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div style={{ fontSize: 11, color: 'var(--text-3)' }}>{pdfs.length} archivos PDF generados para zona {dia} · {fecha}</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {pdfs.map((p, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '14px 20px', border: '1px solid var(--line)', borderRadius: 10, background: 'var(--surface)' }}>
                    <FileText size={18} color={p.TipoPDF === 'gerencia' ? 'var(--green)' : 'var(--text-3)'}/>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 500, fontSize: 13 }}>{p.ArchivoPDF}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 2 }}>
                        {p.TipoPDF === 'gerencia' ? 'Resumen gerencial' : `Vendedor: ${p.VendedorNombre}`} · Zona {p.Zona} · {p.GeneradoEn}
                      </div>
                    </div>
                    <a href={`/api/pdf?ruta=${encodeURIComponent(p.RutaPDF_Relativa)}`} target="_blank" rel="noreferrer"
                       style={{ padding: '7px 16px', background: 'var(--green)', color: '#0A0B0A', borderRadius: 7, fontSize: 12, fontWeight: 700, textDecoration: 'none', letterSpacing: 0.5, flexShrink: 0 }}>
                      Abrir PDF
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 28px', borderTop: '1px solid var(--line)', fontSize: 11, color: 'var(--text-4)', flexShrink: 0 }}>
          <span>Orbit © 2026 · Plataforma propietaria de Torres Matías.</span>
          <span className="mono" style={{ fontSize: 10 }}>Zona {dia} · {fecha} · {totalC} clientes</span>
        </div>
      </main>
    </div>
  );
}


