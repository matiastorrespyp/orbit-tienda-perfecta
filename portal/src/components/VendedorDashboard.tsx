import { useState } from 'react';
import { Home, LogOut, RefreshCw, FileText, ChevronRight, Check, MapPin, Menu, X } from 'lucide-react';
import type { Cliente, Foco, PdfEntry, ObjetivoResumen } from '../lib/data';

interface Props {
  clientes:     Cliente[];
  focos:        Foco[];
  pdf:          PdfEntry | null;
  vendedorId:   string;
  vendedorName: string;
  objetivo?:    ObjetivoResumen | null;
}

function pctBand(p: number) {
  if (p >= 80) return { label: 'TP',          color: '#6EC531' };
  if (p >= 60) return { label: 'Oportunidad', color: '#F0C000' };
  if (p >= 30) return { label: 'Recuperar',   color: '#E87A00' };
  return             { label: 'Crítico',        color: '#E84B4B' };
}

function PctBar({ pct, color }: { pct: number; color: string }) {
  return (
    <div style={{ position: 'relative', width: '100%', background: '#1A1D1A', borderRadius: 99, height: 6, overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, width: `${Math.min(pct,100)}%`, background: `linear-gradient(90deg,${color},${color}DD)`, borderRadius: 99, transition: 'width .8s' }}/>
      <div style={{ position: 'absolute', top: -2, bottom: -2, left: '80%', width: 1.5, background: 'rgba(255,255,255,0.3)' }}/>
    </div>
  );
}

function MiniRing({ pct, color, size = 52 }: { pct: number; color: string; size?: number }) {
  const t = 5, r = size/2 - t/2 - 1, c = 2*Math.PI*r, v = Math.min(Math.max(pct,0),100);
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1F231F" strokeWidth={t}/>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={t}
              strokeLinecap="round" strokeDasharray={`${(v/100)*c} ${c}`} transform={`rotate(-90 ${size/2} ${size/2})`}/>
      <text x={size/2} y={size/2+4} textAnchor="middle"
            style={{ fontSize: 12, fontWeight: 600, fill: 'var(--text)', fontFamily: 'Geist Mono,monospace' }}>
        {Math.round(pct)}
      </text>
    </svg>
  );
}

export default function VendedorDashboard({ clientes, focos, pdf, vendedorId, vendedorName, objetivo }: Props) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const tag = vendedorName.slice(0,2).toUpperCase();
  const latestCliente = clientes.length > 0
    ? clientes.reduce((max, c) => String(c.Fecha) > String(max.Fecha) ? c : max, clientes[0])
    : null;

  const fecha = latestCliente?.Fecha ?? '-';
  const dia   = latestCliente?.Dia   ?? '-';

  const avgPct   = clientes.length > 0 ? clientes.reduce((s,c) => s + c.PortafolioPct, 0) / clientes.length : 0;
  const conTP    = clientes.filter(c => c.TP_Sistema === 'SI').length;
  const urgentes = clientes.filter(c => c.Faltan80 <= 2 && c.Faltan80 > 0);
  const sorted   = [...clientes].sort((a,b) => a.Faltan80 - b.Faltan80);
  const topSkus  = focos.filter(f => f.Scope === 'vendedor').sort((a,b) => a.Rank - b.Rank).slice(0,5);

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
        {/* Brand */}
        <div style={{ padding: '20px 18px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
          <img src="/assets/orbit-mark.png" alt="" className="orbit-mark"
               style={{ width: 40, height: 40, flexShrink: 0, filter: 'drop-shadow(0 0 12px rgba(110,197,49,0.35))', transition: 'transform .9s cubic-bezier(.2,.8,.2,1), filter .3s' }}/>
          <img src="/assets/orbit-wordmark.png" alt="Orbit"
               style={{ height: 28, width: 'auto', flexShrink: 0, filter: 'invert(1) brightness(1.1)' }}/>
        </div>

        {/* Vendedor card */}
        <div style={{ margin: '0 14px 14px', padding: '12px 14px', border: '1px solid var(--line)', borderRadius: 9, background: 'var(--surface)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <div style={{ width: 34, height: 34, borderRadius: 8, background: 'rgba(110,197,49,0.15)', border: '1px solid var(--green-line)', display: 'grid', placeItems: 'center', color: 'var(--green)', fontWeight: 700, fontSize: 13, flexShrink: 0 }}>
              {tag}
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 600 }}>{vendedorName}</div>
              <div style={{ fontSize: 10.5, color: 'var(--text-3)' }}>Preventista · Zona {dia}</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <MiniRing pct={avgPct} color={avgPct >= 75 ? '#6EC531' : '#F0C000'}/>
            <div style={{ flex: 1 }}>
              <div className="mono" style={{ fontSize: 13, fontWeight: 600, color: 'var(--text)' }}>{avgPct.toFixed(1)}%</div>
              <div style={{ fontSize: 10.5, color: 'var(--text-3)' }}>promedio portafolio</div>
              <div style={{ fontSize: 11, color: 'var(--green)', marginTop: 4 }}><Check size={11} strokeWidth={2.6} style={{ display: 'inline', verticalAlign: 'middle' }}/> {conTP} con TP</div>
            </div>
          </div>
        </div>

        <nav style={{ padding: '0 10px', flex: 1 }}>
          <button style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '9px 10px', border: 'none', background: 'var(--surface-2)', color: 'var(--text)', borderRadius: 7, width: '100%', cursor: 'pointer', textAlign: 'left', fontSize: 13, fontFamily: 'inherit', fontWeight: 500, position: 'relative' }}>
            <span style={{ position: 'absolute', left: -10, top: 8, bottom: 8, width: 2, background: 'var(--green)', borderRadius: 2 }}/>
            <Home size={15} color="var(--green)"/><span>Mi panel</span>
          </button>
        </nav>

        {/* Sync info */}
        <div style={{ margin: '12px 14px', padding: 12, border: '1px solid var(--line)', borderRadius: 9, background: 'linear-gradient(140deg,rgba(110,197,49,0.08),transparent 60%)' }}>
          <div style={{ fontSize: 10.5, color: 'var(--green)', letterSpacing: 1.4, textTransform: 'uppercase', fontWeight: 600, marginBottom: 4 }}>Mis datos</div>
          <div style={{ fontSize: 11.5, color: 'var(--text-2)' }}>
            {clientes.length} clientes hoy<br/>
            <span style={{ color: 'var(--text-3)', fontSize: 10.5 }}>Zona {dia} · {fecha}</span>
          </div>
        </div>

        <div style={{ padding: '10px 14px 16px', display: 'flex', gap: 6, borderTop: '1px solid var(--line)' }}>
          <button className="icon-btn" onClick={() => window.location.reload()}
                  style={{ width: 30, height: 30, borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', color: 'var(--text-2)', cursor: 'pointer', display: 'grid', placeItems: 'center' }}>
            <RefreshCw size={14}/>
          </button>
          <div style={{ flex: 1 }}/>
          <a href="/api/logout" style={{ textDecoration: 'none' }}>
            <button className="icon-btn" style={{ width: 30, height: 30, borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', color: 'var(--text-3)', cursor: 'pointer', display: 'grid', placeItems: 'center' }}>
              <LogOut size={14}/>
            </button>
          </a>
        </div>
      </aside>

      {/* Main */}
      <main style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
        {/* TopBar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '18px 28px', borderBottom: '1px solid var(--line)', background: 'rgba(10,11,10,0.85)', backdropFilter: 'blur(8px)', position: 'sticky', top: 0, zIndex: 4, flexShrink: 0 }}>
          <button className="hamburger icon-btn" onClick={() => setSidebarOpen(s => !s)}
                  style={{ display: 'none', width: 30, height: 30, borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', color: 'var(--text-2)', cursor: 'pointer', placeItems: 'center' }}>
            {sidebarOpen ? <X size={14}/> : <Menu size={14}/>}
          </button>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-3)', fontSize: 11.5, marginBottom: 2 }}>
              <span>Orbit</span><ChevronRight size={11}/><span>{vendedorName}</span>
            </div>
            <h1 style={{ margin: 0, fontSize: 20, fontWeight: 600, letterSpacing: -0.3 }}>Mi panel de hoy</h1>
          </div>
          <div style={{ flex: 1 }}/>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 12px', border: '1px solid var(--line)', borderRadius: 99, fontSize: 12 }}>
            <span className="live-dot" style={{ width: 6, height: 6, borderRadius: 99, background: 'var(--green)' }}/>
            <span style={{ color: 'var(--text-2)' }}>Zona</span>
            <span className="mono" style={{ fontWeight: 500 }}>{dia} · {fecha}</span>
          </div>
          {pdf && (
            <a href={`/api/pdf?ruta=${encodeURIComponent(pdf.RutaPDF_Relativa)}`} target="_blank" rel="noreferrer"
               style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '7px 14px', background: 'var(--green)', color: '#0A0B0A', borderRadius: 8, fontSize: 12, fontWeight: 700, textDecoration: 'none' }}>
              <FileText size={13}/> Mi PDF
            </a>
          )}
        </div>

        {/* Content */}
        <div style={{ flex: 1, padding: '24px 28px 48px', overflow: 'auto' }}>

          {/* KPIs */}
          <div className="kpi-grid-4" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 20 }}>
            <div className="kpi-card" style={{ padding: 20, border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: 'var(--yellow)' }}/>
              <div style={{ fontSize: 11, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 500, marginBottom: 12 }}>Mis clientes hoy</div>
              <div className="mono" style={{ fontSize: 30, fontWeight: 500, lineHeight: 1, marginBottom: 8 }}>{clientes.length}</div>
              <div style={{ fontSize: 12, color: 'var(--text-3)' }}>en zona oportunidad</div>
            </div>
            <div className="kpi-card" style={{ padding: 20, border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', position: 'relative', overflow: 'hidden' }}>
              <div style={{ fontSize: 11, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 500, marginBottom: 12 }}>Portafolio promedio</div>
              <div className="mono" style={{ fontSize: 30, fontWeight: 500, lineHeight: 1, marginBottom: 8 }}>{avgPct.toFixed(1)}%</div>
              <div style={{ fontSize: 12, color: 'var(--text-3)' }}>meta: 80%</div>
            </div>
            <div className="kpi-card" style={{ padding: 20, border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: 'var(--orange)' }}/>
              <div style={{ fontSize: 11, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 500, marginBottom: 12 }}>Urgentes hoy</div>
              <div className="mono" style={{ fontSize: 30, fontWeight: 500, lineHeight: 1, marginBottom: 8, color: urgentes.length > 0 ? 'var(--orange)' : 'var(--text)' }}>{urgentes.length}</div>
              <div style={{ fontSize: 12, color: 'var(--text-3)' }}>a 1-2 SKUs del TP</div>
            </div>
          </div>

          {/* Objetivo TP del mes */}
          {objetivo && (() => {
            const cc = (p: number) => p >= 80 ? 'var(--green)' : p >= 50 ? 'var(--yellow)' : 'var(--orange)';
            return (
              <div style={{ marginBottom: 20, border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', overflow: 'hidden' }}>
                <div style={{ padding: '14px 22px', borderBottom: '1px solid var(--line)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.5, textTransform: 'uppercase', fontWeight: 600, marginBottom: 2 }}>Mes actual</div>
                    <div style={{ fontSize: 15, fontWeight: 600 }}>Mi objetivo TP</div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <MiniRing pct={objetivo.CumplimientoPct} color={cc(objetivo.CumplimientoPct)} size={52}/>
                    <div>
                      <div className="mono" style={{ fontSize: 20, fontWeight: 600, color: cc(objetivo.CumplimientoPct) }}>{objetivo.CumplimientoPct.toFixed(1)}%</div>
                      <div style={{ fontSize: 10.5, color: 'var(--text-3)' }}>cumplimiento</div>
                    </div>
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)' }}>
                  {([
                    { label: 'Objetivo',  value: objetivo.Objetivo.toFixed(0)  },
                    { label: 'Acumulado', value: String(objetivo.Acumulado)    },
                    { label: 'Real hoy',  value: String(objetivo.RealDia)      },
                    { label: 'Faltante',  value: objetivo.Faltante.toFixed(0)  },
                  ] as {label:string;value:string}[]).map((item, i) => (
                    <div key={i} style={{ padding: '12px 16px', borderRight: i < 3 ? '1px solid var(--line)' : 'none', textAlign: 'center' }}>
                      <div style={{ fontSize: 10, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 600, marginBottom: 4 }}>{item.label}</div>
                      <div className="mono" style={{ fontSize: 18, fontWeight: 500 }}>{item.value}</div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })()}

          {/* Alertas urgentes */}
          {urgentes.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.5, textTransform: 'uppercase', fontWeight: 600, marginBottom: 10 }}>⚡ Cerrar hoy — mínimo esfuerzo, máximo impacto</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {urgentes.map((c, i) => {
                  const skus80  = c.SKUsFaltan80.split('|').map(s => s.trim()).filter(Boolean);
                  const skus100 = c.SKUsFaltan100.split('|').map(s => s.trim()).filter(Boolean);
                  return (
                    <div key={i} style={{ padding: '14px 18px', background: c.Faltan80 === 1 ? 'rgba(110,197,49,0.06)' : 'rgba(232,122,0,0.07)', border: `1px solid ${c.Faltan80===1?'var(--green-line)':'rgba(232,122,0,0.25)'}`, borderRadius: 10 }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                        <div>
                          <span style={{ fontWeight: 600, fontSize: 13 }}>{c.RazonSocial}</span>
                          <span style={{ color: 'var(--text-3)', fontSize: 11, marginLeft: 8 }}>
                            <MapPin size={10} style={{ display:'inline', verticalAlign:'middle' }}/> {c.Localidad}
                          </span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span className="mono" style={{ fontSize: 16, fontWeight: 600, color: c.Faltan80 === 1 ? 'var(--green)' : 'var(--orange)' }}>{c.PortafolioPct.toFixed(0)}%</span>
                          <span style={{ background: c.Faltan80===1?'rgba(110,197,49,0.15)':'rgba(232,122,0,0.15)', color: c.Faltan80===1?'var(--green)':'var(--orange)', borderRadius: 6, padding: '3px 10px', fontSize: 11, fontWeight: 600 }}>
                            {c.Faltan80 === 1 ? '1 SKU para TP' : `${c.Faltan80} SKUs para TP`}
                          </span>
                        </div>
                      </div>
                      {skus80.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: skus100.length > 0 ? 6 : 0 }}>
                          <span style={{ fontSize: 10.5, color: 'var(--text-3)', marginRight: 4 }}>Para 80%:</span>
                          {skus80.map((sku, j) => (
                            <span key={j} style={{ background: 'var(--surface-3)', border: '1px solid var(--line-2)', borderRadius: 5, padding: '3px 9px', fontSize: 11.5, color: 'var(--text-2)', fontWeight: 500 }}>{sku}</span>
                          ))}
                        </div>
                      )}
                      {skus100.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                          <span style={{ fontSize: 10.5, color: 'var(--text-3)', marginRight: 4 }}>Para 100%:</span>
                          {skus100.map((sku, j) => (
                            <span key={j} style={{ background: 'var(--surface-3)', border: '1px solid var(--line)', borderRadius: 5, padding: '3px 9px', fontSize: 11.5, color: 'var(--text-3)', fontWeight: 400 }}>{sku}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Todos mis clientes */}
          <div style={{ border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', overflow: 'hidden', marginBottom: 20 }}>
            <div style={{ padding: '18px 22px 14px', borderBottom: '1px solid var(--line)' }}>
              <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.5, textTransform: 'uppercase', fontWeight: 600, marginBottom: 4 }}>Zona {dia} · {fecha}</div>
              <div style={{ fontSize: 16, fontWeight: 600 }}>Todos mis clientes — por urgencia</div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1fr 100px 64px 60px', gap: 10, padding: '8px 22px', fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 600, borderBottom: '1px solid var(--line)' }}>
              <div>Cliente</div><div>Localidad</div><div>Portafolio</div><div style={{ textAlign:'center' }}>Faltan 80</div><div style={{ textAlign:'center' }}>TP</div>
            </div>
            {sorted.map((c, i) => {
              const band  = pctBand(c.PortafolioPct);
              const skus80  = c.SKUsFaltan80.split('|').map(s => s.trim()).filter(Boolean);
              const skus100 = c.SKUsFaltan100.split('|').map(s => s.trim()).filter(Boolean);
              return (
                <div key={i} style={{ borderBottom: '1px solid var(--line)' }}>
                  <div className="row-hover" style={{ display: 'grid', gridTemplateColumns: '1.8fr 1fr 100px 64px 60px', gap: 10, padding: '11px 22px', alignItems: 'center', fontSize: 12.5 }}>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontWeight: 500 }}>{c.RazonSocial}</div>
                      {c.Faltan80 <= 2 && c.Faltan80 > 0 && <div style={{ fontSize: 10, color: 'var(--orange)', marginTop: 2 }}>⚡ {c.Faltan80} SKU{c.Faltan80>1?'s':''} para TP</div>}
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
                    <div className="mono" style={{ textAlign:'center', color: c.Faltan80===0?'var(--text-4)':'var(--text-2)', fontSize: 13 }}>
                      {c.Faltan80===0?'—':c.Faltan80}
                    </div>
                    <div style={{ textAlign:'center' }}>
                      {c.TP_Sistema === 'SI'
                        ? <span style={{ display:'inline-flex', alignItems:'center', gap:3, color:'var(--green)', fontSize:11, fontWeight:600 }}><Check size={11} strokeWidth={2.6}/></span>
                        : <span style={{ color:'var(--text-4)', fontSize:11 }}>—</span>}
                    </div>
                  </div>
                  {(skus80.length > 0 || skus100.length > 0) && (
                    <div style={{ padding: '0 22px 10px', display: 'flex', flexDirection: 'column', gap: 5 }}>
                      {skus80.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, alignItems: 'center' }}>
                          <span style={{ fontSize: 10, color: 'var(--text-3)', marginRight: 2, whiteSpace: 'nowrap' }}>Para 80%:</span>
                          {skus80.map((sku, j) => (
                            <span key={j} style={{ background: 'var(--surface-3)', border: '1px solid var(--green-line)', borderRadius: 4, padding: '2px 8px', fontSize: 11, color: 'var(--green)' }}>{sku}</span>
                          ))}
                        </div>
                      )}
                      {skus100.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, alignItems: 'center' }}>
                          <span style={{ fontSize: 10, color: 'var(--text-3)', marginRight: 2, whiteSpace: 'nowrap' }}>Para 100%:</span>
                          {skus100.map((sku, j) => (
                            <span key={j} style={{ background: 'var(--surface-3)', border: '1px solid var(--line)', borderRadius: 4, padding: '2px 8px', fontSize: 11, color: 'var(--text-3)' }}>{sku}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Top SKUs */}
          {topSkus.length > 0 && (
            <div style={{ border: '1px solid var(--line)', borderRadius: 12, background: 'var(--surface)', overflow: 'hidden' }}>
              <div style={{ padding: '16px 22px 12px', borderBottom: '1px solid var(--line)' }}>
                <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 1.5, textTransform: 'uppercase', fontWeight: 600, marginBottom: 4 }}>Mis top SKUs</div>
                <div style={{ fontSize: 16, fontWeight: 600 }}>Productos foco para mi zona</div>
              </div>
              <div style={{ padding: '12px 22px', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {topSkus.map(p => {
                  const max = topSkus[0]?.CantClientes || 1;
                  return (
                    <div key={p.Rank} className="foco-row" style={{ display: 'grid', gridTemplateColumns: '28px 1fr 60px', gap: 10, alignItems: 'center', padding: '6px 0' }}>
                      <span className="mono" style={{ fontSize: 11, fontWeight: 500, color: p.Rank <= 3 ? 'var(--green)' : 'var(--text-3)' }}>{String(p.Rank).padStart(2,'0')}</span>
                      <div>
                        <div style={{ fontSize: 12.5, marginBottom: 4 }}>{p.Articulo}</div>
                        <div style={{ height: 5, background: '#1A1D1A', borderRadius: 99, overflow: 'hidden' }}>
                          <div style={{ width: `${(p.CantClientes/max)*100}%`, height: '100%', background: p.Rank <= 3 ? 'linear-gradient(90deg,var(--green),#4A8A1C)' : '#3A4A30' }}/>
                        </div>
                      </div>
                      <div className="mono" style={{ textAlign:'right', fontSize: 12, color:'var(--text-2)' }}>{p.CantClientes} <span style={{ color:'var(--text-4)' }}>cli</span></div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 28px', borderTop: '1px solid var(--line)', fontSize: 11, color: 'var(--text-4)', flexShrink: 0 }}>
          <span>Orbit © 2026 · Plataforma propietaria de Torres Matías.</span>
          <span className="mono" style={{ fontSize: 10 }}>{vendedorName} · Zona {dia} · {fecha}</span>
        </div>
      </main>
    </div>
  );
}


