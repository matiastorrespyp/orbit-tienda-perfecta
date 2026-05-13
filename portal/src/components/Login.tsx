import { useState } from 'react';

interface Profile { id: string; label: string; sub: string; tag: string; }
interface Props { profiles: Profile[]; initialError: boolean; }

const labelStyle: React.CSSProperties = {
  display: 'block', fontSize: 10.5, color: 'var(--text-3)',
  letterSpacing: 1.5, textTransform: 'uppercase', fontWeight: 600, marginBottom: 7,
};
const inputStyle: React.CSSProperties = {
  width: '100%', background: '#101210', color: 'var(--text)',
  border: '1.5px solid var(--line)', borderRadius: 9,
  padding: '12px 44px 12px 14px', fontSize: 14, fontFamily: 'inherit',
  outline: 'none', transition: 'border-color .2s, box-shadow .2s',
};
const selectStyle: React.CSSProperties = {
  width: '100%', background: '#101210', color: 'var(--text)',
  border: '1.5px solid var(--line)', borderRadius: 9,
  padding: '12px 36px 12px 14px', fontSize: 14, fontFamily: 'inherit',
  outline: 'none', appearance: 'none', cursor: 'pointer',
};

export default function Login({ profiles, initialError }: Props) {
  const [profile,  setProfile]  = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [entering, setEntering] = useState(false);
  const [shake,    setShake]    = useState(false);
  const [error,    setError]    = useState(initialError ? 'Contraseña incorrecta' : '');
  const [role,     setRole]     = useState('');

  const selectedProfile = profiles.find(p => p.id === profile);

  const triggerShake = () => {
    setShake(true);
    setTimeout(() => setShake(false), 500);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!profile)  { setError('Seleccioná un perfil');  triggerShake(); return; }
    if (!password) { setError('Ingresá la contraseña'); triggerShake(); return; }
    setError('');
    setRole(profile === 'gerencia' ? 'gerencia' : 'vendedor');
    setEntering(true);
    if (typeof window !== 'undefined' && (window as any).playEnter) (window as any).playEnter();
    setTimeout(() => (e.target as HTMLFormElement).submit(), 900);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', position: 'relative', zIndex: 1, padding: 24 }}>
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: 'radial-gradient(60% 50% at 50% 30%, rgba(110,197,49,0.08), transparent 70%)',
      }}/>

      <div className={shake ? 'shake' : ''} style={{
        width: '100%', maxWidth: 460,
        background: 'var(--surface)', border: '1px solid var(--line)',
        borderRadius: 18, padding: '38px 38px 30px', position: 'relative',
        boxShadow: '0 30px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(110,197,49,0.04)',
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: 28 }}>
          <img src="/assets/orbit-mark.png" alt=""
               className={`login-mark ${entering ? 'entering' : ''}`}
               style={{ width: 116, height: 116, filter: 'drop-shadow(0 0 28px rgba(110,197,49,0.55))', transition: 'transform .9s cubic-bezier(.2,.8,.2,1), filter .4s' }} />
          <img src="/assets/orbit-wordmark.png" alt="Orbit · Tienda Perfecta"
               style={{ height: 38, width: 'auto', marginTop: 14, filter: 'invert(1) brightness(1.1)', opacity: entering ? 0 : 1, transition: 'opacity .35s' }} />
          <div style={{ fontSize: 10.5, color: 'var(--text-3)', letterSpacing: 2.5, textTransform: 'uppercase', marginTop: 14, fontWeight: 500 }}>
            Plataforma comercial · PyP Logística
          </div>
        </div>

        <form method="post" action="/api/login" onSubmit={handleSubmit}
              style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {/* Perfil selector */}
          <div>
            <label style={labelStyle}>Perfil</label>
            <div style={{ position: 'relative' }}>
              <select name="vendedor_id" value={profile} onChange={e => { setProfile(e.target.value); setError(''); }} style={selectStyle}>
                <option value="" disabled>Seleccioná un perfil…</option>
                {profiles.map(p => (
                  <option key={p.id} value={p.id}>{p.label}{p.sub ? ` — ${p.sub}` : ''}</option>
                ))}
              </select>
              <span style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-3)' }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9l6 6 6-6"/></svg>
              </span>
            </div>
            {selectedProfile && (
              <div style={{ marginTop: 10, padding: '8px 12px', background: 'rgba(110,197,49,0.06)', border: '1px solid var(--green-line)', borderRadius: 8, display: 'flex', alignItems: 'center', gap: 10, fontSize: 12 }}>
                <div style={{ width: 26, height: 26, borderRadius: 6, background: 'rgba(110,197,49,0.15)', color: 'var(--green)', display: 'grid', placeItems: 'center', fontWeight: 600, fontSize: 10.5, flexShrink: 0 }}>
                  {selectedProfile.tag}
                </div>
                <div>
                  <div style={{ fontWeight: 500 }}>{selectedProfile.label}</div>
                  {selectedProfile.sub && <div style={{ color: 'var(--text-3)', fontSize: 10.5 }}>{selectedProfile.sub}</div>}
                </div>
              </div>
            )}
          </div>

          {/* Hidden role field */}
          <input type="hidden" name="role" value={role} readOnly />

          {/* Contraseña */}
          <div>
            <label style={labelStyle}>Contraseña</label>
            <div style={{ position: 'relative' }}>
              <input type={showPass ? 'text' : 'password'} name="password"
                     value={password} onChange={e => { setPassword(e.target.value); setError(''); }}
                     placeholder="••••••••" style={inputStyle} />
              <button type="button" data-no-sound onClick={() => setShowPass(s => !s)}
                      style={{ position: 'absolute', right: 8, top: 8, width: 30, height: 30, border: 'none', background: 'transparent', color: 'var(--text-3)', cursor: 'pointer', display: 'grid', placeItems: 'center', fontSize: 16 }}>
                {showPass ? '◉' : '◎'}
              </button>
            </div>
          </div>

          {error && (
            <div style={{ padding: '8px 12px', background: 'rgba(232,75,75,0.08)', border: '1px solid rgba(232,75,75,0.32)', borderRadius: 8, color: 'var(--red)', fontSize: 12 }}>
              {error}
            </div>
          )}

          <button type="submit" className="login-btn" disabled={entering} style={{
            marginTop: 4, background: 'linear-gradient(135deg, #6EC531, #4A8A1C)',
            color: '#0A0B0A', fontWeight: 700, fontSize: 13, letterSpacing: 1.5,
            textTransform: 'uppercase', border: 'none', borderRadius: 10, padding: '14px',
            width: '100%', boxShadow: '0 6px 20px rgba(110,197,49,0.28)', fontFamily: 'inherit',
            opacity: entering ? 0.7 : 1,
          }}>
            {entering ? 'INICIANDO ORBIT…' : 'INGRESAR →'}
          </button>

          <div style={{ display: 'flex', justifyContent: 'flex-end', fontSize: 11, color: 'var(--text-4)', marginTop: 4 }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
              <span className="live-dot" style={{ width: 5, height: 5, borderRadius: 99, background: 'var(--green)' }}/>
              Conectado
            </span>
          </div>
        </form>

        {/* P&P partner badge */}
        <div style={{ marginTop: 26, paddingTop: 22, borderTop: '1px solid var(--line)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
          <div style={{ fontSize: 9.5, color: 'var(--text-4)', letterSpacing: 2.2, textTransform: 'uppercase', fontWeight: 600 }}>Operado por</div>
          <img src="/assets/pyp-logo.png" alt="P&P Logística"
               style={{ maxWidth: 180, height: 'auto', maxHeight: 80, filter: 'drop-shadow(0 4px 18px rgba(56,110,255,0.35)) brightness(1.18) saturate(1.15)', transition: 'transform .4s, filter .3s' }}
               onMouseEnter={e => { (e.currentTarget as HTMLImageElement).style.transform = 'scale(1.05)'; }}
               onMouseLeave={e => { (e.currentTarget as HTMLImageElement).style.transform = 'scale(1)'; }} />
        </div>
      </div>

      <div style={{ position: 'absolute', bottom: 18, left: 0, right: 0, textAlign: 'center', fontSize: 10.5, color: 'var(--text-4)', letterSpacing: 1.5 }}>
        Orbit © 2026 · Plataforma propietaria de Torres Matías.
      </div>
    </div>
  );
}
