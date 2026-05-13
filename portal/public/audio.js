// WebAudio — Dorito crunch sound effects 🌶️
// Synthesizes a crispy, brittle "snap" using filtered noise + micro-bursts

let _audioCtx = null;
function getCtx() {
  if (!_audioCtx) {
    try { _audioCtx = new (window.AudioContext || window.webkitAudioContext)(); }
    catch(e) { return null; }
  }
  if (_audioCtx.state === 'suspended') _audioCtx.resume();
  return _audioCtx;
}

// Generate a short noise buffer with selectable color
function noiseBuffer(ctx, durationSec, kind = 'white') {
  const len = Math.floor(ctx.sampleRate * durationSec);
  const buf = ctx.createBuffer(1, len, ctx.sampleRate);
  const data = buf.getChannelData(0);
  if (kind === 'pink') {
    // Paul Kellet's pink noise
    let b0=0, b1=0, b2=0, b3=0, b4=0, b5=0, b6=0;
    for (let i = 0; i < len; i++) {
      const w = Math.random() * 2 - 1;
      b0 = 0.99886 * b0 + w * 0.0555179;
      b1 = 0.99332 * b1 + w * 0.0750759;
      b2 = 0.96900 * b2 + w * 0.1538520;
      b3 = 0.86650 * b3 + w * 0.3104856;
      b4 = 0.55000 * b4 + w * 0.5329522;
      b5 = -0.7616 * b5 - w * 0.0168980;
      data[i] = (b0+b1+b2+b3+b4+b5+b6+w*0.5362) * 0.11;
      b6 = w * 0.115926;
    }
  } else {
    for (let i = 0; i < len; i++) data[i] = (Math.random() * 2 - 1);
  }
  return buf;
}

// Single crunch fragment — a short, sharp filtered-noise burst
function crunchFragment(ctx, when, vol, freqCenter, dur = 0.04) {
  const buf = noiseBuffer(ctx, dur, 'white');
  const src = ctx.createBufferSource();
  src.buffer = buf;
  src.playbackRate.value = 0.9 + Math.random() * 0.3;

  // Bandpass to give it that brittle, crispy quality
  const bp = ctx.createBiquadFilter();
  bp.type = 'bandpass';
  bp.frequency.value = freqCenter;
  bp.Q.value = 3 + Math.random() * 4;

  // Highpass to remove muddy lows
  const hp = ctx.createBiquadFilter();
  hp.type = 'highpass';
  hp.frequency.value = 800;

  // Sharp attack, fast decay (brittle snap)
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0, when);
  gain.gain.linearRampToValueAtTime(vol, when + 0.0008);
  gain.gain.exponentialRampToValueAtTime(0.0001, when + dur);

  src.connect(hp).connect(bp).connect(gain).connect(ctx.destination);
  src.start(when);
  src.stop(when + dur + 0.01);
}

// Main crunch — multiple staggered fragments simulating shattering chip pieces
function playCrunch({ vol = 0.28, intensity = 1, pitch = 1 } = {}) {
  const ctx = getCtx();
  if (!ctx) return;
  const now = ctx.currentTime;

  // Big initial snap
  crunchFragment(ctx, now,        vol * 1.0,   3200 * pitch, 0.045);
  crunchFragment(ctx, now,        vol * 0.85,  5400 * pitch, 0.035);
  crunchFragment(ctx, now + 0.004, vol * 0.7,  2200 * pitch, 0.05);

  // Crackle tail — micro-fragments
  const fragments = Math.round(3 + Math.random() * 3 * intensity);
  for (let i = 0; i < fragments; i++) {
    const t = now + 0.012 + Math.random() * 0.06 * intensity;
    const f = (1800 + Math.random() * 4500) * pitch;
    const v = vol * (0.18 + Math.random() * 0.35);
    crunchFragment(ctx, t, v, f, 0.018 + Math.random() * 0.02);
  }

  // Tiny low-end "thud" for body / mass of the chip
  const osc = ctx.createOscillator();
  osc.type = 'triangle';
  osc.frequency.setValueAtTime(220 * pitch, now);
  osc.frequency.exponentialRampToValueAtTime(80 * pitch, now + 0.04);
  const og = ctx.createGain();
  og.gain.setValueAtTime(0, now);
  og.gain.linearRampToValueAtTime(vol * 0.18, now + 0.002);
  og.gain.exponentialRampToValueAtTime(0.0001, now + 0.06);
  osc.connect(og).connect(ctx.destination);
  osc.start(now); osc.stop(now + 0.08);
}

// Lighter "release" crunch — fewer fragments, used on pointerup
function playCrunchLight({ pitch = 1 } = {}) {
  const ctx = getCtx();
  if (!ctx) return;
  const now = ctx.currentTime;
  crunchFragment(ctx, now,         0.10, 4200 * pitch, 0.022);
  crunchFragment(ctx, now + 0.006, 0.06, 2800 * pitch, 0.018);
  // 1-2 micro flecks
  for (let i = 0; i < 2; i++) {
    const t = now + 0.01 + Math.random() * 0.025;
    const f = (3000 + Math.random() * 3000) * pitch;
    crunchFragment(ctx, t, 0.05 + Math.random() * 0.04, f, 0.012);
  }
}

// Login "BIG CRUNCH" — chunky, satisfying for the launch animation
function playEnter() {
  const ctx = getCtx();
  if (!ctx) return;
  const now = ctx.currentTime;
  // First big chomp
  playCrunch({ vol: 0.4, intensity: 2.2, pitch: 0.9 });
  // Trailing crunch echo
  setTimeout(() => playCrunch({ vol: 0.28, intensity: 1.6, pitch: 1.05 }), 110);
  setTimeout(() => playCrunchLight({ pitch: 1.2 }), 240);
}

// Auto-attach to all clickable elements
function installClickSounds() {
  if (window.__clickSoundsInstalled) return;
  window.__clickSoundsInstalled = true;
  document.addEventListener('pointerdown', (e) => {
    const t = e.target.closest('button, [role="button"], .clickable, a[href], select, input[type="checkbox"], input[type="radio"]');
    if (!t) return;
    if (t.dataset.noSound) return;
    const pitch = 0.9 + Math.random() * 0.25;
    playCrunch({ vol: 0.22, intensity: 1, pitch });
  }, true);
  document.addEventListener('pointerup', (e) => {
    const t = e.target.closest('button, [role="button"], .clickable, a[href], select, input[type="checkbox"], input[type="radio"]');
    if (!t) return;
    if (t.dataset.noSound) return;
    const pitch = 1.0 + Math.random() * 0.3;
    playCrunchLight({ pitch });
  }, true);
}

// Install on first user gesture
window.addEventListener('pointerdown', () => { getCtx(); installClickSounds(); }, { once: true });
window.addEventListener('keydown', () => { getCtx(); }, { once: true });
installClickSounds();

Object.assign(window, { playCrunch, playCrunchLight, playEnter });
// Back-compat alias if anything still calls playKeyClick
window.playKeyClick = (opts = {}) => {
  if (opts.down === false) playCrunchLight({ pitch: opts.pitch || 1 });
  else playCrunch({ vol: 0.2, pitch: opts.pitch || 1 });
};
