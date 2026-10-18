const NOTES = { C3: 48, E3: 52, G3: 55, C4: 60, D4: 62, E4: 64, F4: 65, G4: 67, A4: 69, B4: 71, C5: 72, D5: 74, E5: 76 };
const CHROMATIC = [
  { name: "C", midi: 0 }, { name: "C♯ / D♭", midi: 1 }, { name: "D", midi: 2 }, { name: "D♯ / E♭", midi: 3 },
  { name: "E", midi: 4 }, { name: "F", midi: 5 }, { name: "F♯ / G♭", midi: 6 }, { name: "G", midi: 7 },
  { name: "G♯ / A♭", midi: 8 }, { name: "A", midi: 9 }, { name: "A♯ / B♭", midi: 10 }, { name: "B", midi: 11 },
];
const SCORE_SCALES = [
  { id: "major", name: "Major (Ionian)", steps: [0, 2, 4, 5, 7, 9, 11, 12], degrees: [0, 1, 2, 3, 4, 5, 6, 7] },
  { id: "natural-minor", name: "Natural minor (Aeolian)", steps: [0, 2, 3, 5, 7, 8, 10, 12], degrees: [0, 1, 2, 3, 4, 5, 6, 7] },
  { id: "harmonic-minor", name: "Harmonic minor", steps: [0, 2, 3, 5, 7, 8, 11, 12], degrees: [0, 1, 2, 3, 4, 5, 6, 7] },
  { id: "melodic-minor", name: "Melodic minor", steps: [0, 2, 3, 5, 7, 9, 11, 12], degrees: [0, 1, 2, 3, 4, 5, 6, 7] },
  { id: "dorian", name: "Dorian mode", steps: [0, 2, 3, 5, 7, 9, 10, 12], degrees: [0, 1, 2, 3, 4, 5, 6, 7] },
  { id: "mixolydian", name: "Mixolydian mode", steps: [0, 2, 4, 5, 7, 9, 10, 12], degrees: [0, 1, 2, 3, 4, 5, 6, 7] },
  { id: "major-pentatonic", name: "Major pentatonic", steps: [0, 2, 4, 7, 9, 12], degrees: [0, 1, 2, 4, 5, 7] },
  { id: "minor-pentatonic", name: "Minor pentatonic", steps: [0, 3, 5, 7, 10, 12], degrees: [0, 2, 3, 4, 6, 7] },
  { id: "blues", name: "Blues scale", steps: [0, 3, 5, 6, 7, 10, 12], degrees: [0, 2, 3, 4, 4, 6, 7] },
  { id: "chromatic", name: "Chromatic scale", steps: Array.from({ length: 13 }, (_, i) => i), degrees: Array.from({ length: 13 }, (_, i) => i) },
];
const CHORDS = [
  { id: "major", name: "C major", short: "C", intervals: [0, 4, 7], notes: "C–E–G" },
  { id: "minor", name: "C minor", short: "Cm", intervals: [0, 3, 7], notes: "C–E♭–G" },
  { id: "sus2", name: "C suspended 2", short: "Csus2", intervals: [0, 2, 7], notes: "C–D–G" },
  { id: "sus4", name: "C suspended 4", short: "Csus4", intervals: [0, 5, 7], notes: "C–F–G" },
  { id: "dim", name: "C diminished", short: "Cdim", intervals: [0, 3, 6], notes: "C–E♭–G♭" },
  { id: "aug", name: "C augmented", short: "Caug", intervals: [0, 4, 8], notes: "C–E–G♯" },
];
const GUITAR_CHORDS = [
  { id: "power", name: "Power chord", intervals: [0, 7, 12], roles: ["root", "fifth", "octave"] },
  { id: "major", name: "Major", intervals: [0, 4, 7], roles: ["root", "major third", "fifth"] },
  { id: "minor", name: "Minor", intervals: [0, 3, 7], roles: ["root", "minor third", "fifth"] },
  { id: "sus2", name: "Suspended 2", intervals: [0, 2, 7], roles: ["root", "second", "fifth"] },
  { id: "sus4", name: "Suspended 4", intervals: [0, 5, 7], roles: ["root", "fourth", "fifth"] },
  { id: "dim", name: "Diminished", intervals: [0, 3, 6], roles: ["root", "minor third", "diminished fifth"] },
  { id: "aug", name: "Augmented", intervals: [0, 4, 8], roles: ["root", "major third", "augmented fifth"] },
];
const PRESETS = [
  { id: "c-major", name: "C major scale", notes: [60, 62, 64, 65, 67, 69, 71, 72] },
  { id: "g-major", name: "G major scale", notes: [67, 69, 71, 72, 74, 76, 78, 79] },
  { id: "f-major", name: "F major scale", notes: [65, 67, 69, 70, 72, 74, 76, 77] },
  { id: "a-minor", name: "A natural minor", notes: [69, 71, 72, 74, 76, 77, 79, 81] },
  { id: "c-minor", name: "C natural minor", notes: [60, 62, 63, 65, 67, 68, 70, 72] },
  { id: "c-arpeggio", name: "C major arpeggio", notes: [60, 64, 67, 72, 67, 64, 60] },
  { id: "a-arpeggio", name: "A minor arpeggio", notes: [57, 60, 64, 69, 64, 60, 57] },
  { id: "c-blues", name: "C blues lick", notes: [60, 63, 65, 66, 67, 70, 72] },
  { id: "chromatic", name: "Chromatic scale", notes: Array.from({ length: 13 }, (_, i) => 60 + i) },
  { id: "twinkle", name: "Twinkle, Twinkle", notes: [60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60] },
  { id: "ode", name: "Ode to Joy", notes: [64, 64, 65, 67, 67, 65, 64, 62, 60, 60, 62, 64, 64, 62, 62] },
];
const DRUM_PRESETS = [
  { id: "rock", name: "Basic rock", kick: [0, 8], snare: [4, 12], hat: [0, 2, 4, 6, 8, 10, 12, 14] },
  { id: "pop", name: "Pop eighths", kick: [0, 6, 8, 14], snare: [4, 12], hat: Array.from({ length: 16 }, (_, i) => i % 2 === 0 ? i : -1).filter((i) => i >= 0) },
  { id: "half", name: "Half-time", kick: [0], snare: [8], hat: [0, 4, 8, 12] },
  { id: "shuffle", name: "Shuffle feel", kick: [0, 6, 8, 14], snare: [4, 12], hat: [0, 3, 4, 7, 8, 11, 12, 15] },
  { id: "paradiddle", name: "Paradiddle sticking", kick: [], snare: [0, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15], hat: [] },
];
const TRACKS = {
  piano: { title: "Piano", intro: "Hear the notes that make a C major chord, then play them together.", notes: ["C4", "E4", "G4", "C5"], chord: ["C4", "E4", "G4"], chordName: "C major · C–E–G", voice: "piano" },
  guitar: { title: "Guitar", intro: "Compare open-chord tones and power chords. Choose any root and chord quality, inspect the notes and TAB, then play each tone or the full chord.", notes: ["C3", "E3", "G3", "C4", "E4"], chord: ["C3", "E3", "G3", "C4", "E4"], chordName: "Open C major · C–E–G–C–E", power: ["C3", "G3", "C4"], voice: "guitar" },
  drums: { title: "Drums", intro: "Hear a double-stroke roll as alternating pairs of quick strokes, plus the individual kit voices.", notes: [], voice: "drums" },
  violin: { title: "Violin", intro: "Listen to the open strings, then hear how a steady bowed note sustains and changes pitch.", notes: ["G3", "D4", "A4", "E5"], chord: ["C4", "E4", "G4"], chordName: "C major arpeggio · C–E–G", voice: "violin" },
  voice: { title: "Singing & Voice", intro: "Explore chest and head voice with gentle, short note comparisons. Stay in a comfortable range; never force a sound.", notes: ["C3", "G3", "C4", "G4", "C5"], voice: "voice" },
  theory: { title: "Music theory", intro: "Build the sound of C major: C is the root, E the major third, and G the fifth.", notes: ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"], chord: ["C4", "E4", "G4"], chordName: "C major · C–E–G", voice: "piano" },
  music: { title: "Music", intro: "Compare the same C major chord across piano and guitar timbres. Select a note or hear the full chord.", notes: ["C4", "E4", "G4"], chord: ["C4", "E4", "G4"], chordName: "C major · C–E–G", voice: "piano", compare: true },
};

function shell(root, title, intro, body) {
  root.innerHTML = `<section class="inner-page"><div class="page-head"><div><span class="pill neutral">Music &amp; Instruments</span><h1>${title}</h1><p class="muted">${intro}</p></div></div>${body}</section>`;
}

function downloadBlob(blob, name) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a"); link.href = url; link.download = name; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

function audioBufferToWav(buffer) {
  const channels = buffer.numberOfChannels; const frames = buffer.length; const bytes = 44 + frames * channels * 2;
  const out = new ArrayBuffer(bytes); const view = new DataView(out);
  const write = (offset, value) => { for (let i = 0; i < value.length; i++) view.setUint8(offset + i, value.charCodeAt(i)); };
  write(0, "RIFF"); view.setUint32(4, bytes - 8, true); write(8, "WAVE"); write(12, "fmt "); view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); view.setUint16(22, channels, true); view.setUint32(24, buffer.sampleRate, true);
  view.setUint32(28, buffer.sampleRate * channels * 2, true); view.setUint16(32, channels * 2, true); view.setUint16(34, 16, true);
  write(36, "data"); view.setUint32(40, frames * channels * 2, true);
  const data = Array.from({ length: channels }, (_, ch) => buffer.getChannelData(ch)); let offset = 44;
  for (let i = 0; i < frames; i++) for (let ch = 0; ch < channels; ch++) {
    const sample = Math.max(-1, Math.min(1, data[ch][i])); view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true); offset += 2;
  }
  return new Blob([out], { type: "audio/wav" });
}

function midiVariable(value) {
  let buffer = value & 0x7f;
  while ((value >>= 7)) buffer = (buffer << 8) | ((value & 0x7f) | 0x80);
  const bytes = [];
  while (true) { bytes.push(buffer & 255); if (buffer & 0x80) buffer >>= 8; else break; }
  return bytes;
}

function midiFile(events, bpm = 120) {
  const ordered = [];
  for (const event of events) {
    ordered.push({ tick: event.tick, bytes: [0x90 | event.channel, event.note, event.velocity ?? 90] });
    ordered.push({ tick: event.tick + (event.duration || 240), bytes: [0x80 | event.channel, event.note, 0] });
  }
  ordered.sort((a, b) => a.tick - b.tick);
  const microsPerQuarter = Math.round(60000000 / bpm);
  const body = [0, 0xff, 0x51, 3, (microsPerQuarter >>> 16) & 255, (microsPerQuarter >>> 8) & 255, microsPerQuarter & 255];
  let previous = 0;
  for (const event of ordered) { body.push(...midiVariable(event.tick - previous), ...event.bytes); previous = event.tick; }
  body.push(0, 0xff, 0x2f, 0);
  const header = [0x4d, 0x54, 0x68, 0x64, 0, 0, 0, 6, 0, 0, 0, 1, 1, 0xe0];
  const chunk = [0x4d, 0x54, 0x72, 0x6b, (body.length >>> 24) & 255, (body.length >>> 16) & 255, (body.length >>> 8) & 255, body.length & 255, ...body];
  return new Blob([new Uint8Array([...header, ...chunk])], { type: "audio/midi" });
}

function stationMarkup(track, mode) {
  const noteButtons = track.notes.map((note) => `<button class="btn glass-btn" type="button" data-play-note="${note}" aria-label="Play note ${note}">${note}<small>${note[0]}</small></button>`).join("");
  const chord = `<div class="music-audio-group"><h3>Chord examples</h3><p class="muted">Tap a chord to hear its notes together. Suspended chords replace the third; diminished chords stack two minor thirds.</p><div class="row music-audio-buttons">${CHORDS.map((item) => `<button class="btn ${item.id === "major" ? "primary" : ""}" type="button" data-chord-id="${item.id}" aria-label="Play ${item.name}">${item.short}<small>${item.notes}</small></button>`).join("")}</div></div>`;
  const power = track.voice === "guitar" ? `<div class="music-audio-group"><h3>Guitar chord builder</h3><p class="muted">Choose a root and chord quality. The notes update below; tap an individual note or play the complete chord clean or with distortion.</p><div class="music-presets"><label>Root note <select data-guitar-root>${CHROMATIC.map((n, i) => `<option value="${i}">${n.name}</option>`).join("")}</select></label><label>Chord quality <select data-guitar-quality>${GUITAR_CHORDS.map((c) => `<option value="${c.id}" ${c.id === "power" ? "selected" : ""}>${c.name}</option>`).join("")}</select></label></div><p class="music-guitar-notes" data-guitar-notes aria-live="polite"></p><div class="row music-audio-buttons"><button class="btn" type="button" data-guitar-play="acoustic">▶ Play acoustic</button><button class="btn" type="button" data-guitar-play="clean">▶ Play clean electric</button><button class="btn primary" type="button" data-guitar-play="power">▶ Play distorted</button></div><div class="music-guitar-tab" data-guitar-tab aria-label="Guitar tablature for the selected power chord"></div><p class="muted">Power chords contain the root, fifth and octave: they omit the third, so they are neither major nor minor. The tab uses standard E–A–D–G–B–E tuning.</p></div>` : "";
  const drum = track.voice === "drums" ? `<div class="music-audio-group"><h3>Drum sounds &amp; rudiment</h3><p class="muted">A double-stroke roll groups two controlled strokes on each hand: R-R, L-L. Adjust the count and tempo; the custom 16-step grid below lets you compose a groove.</p><div class="row music-audio-buttons"><button class="btn" type="button" data-drum="kick">Bass drum</button><button class="btn" type="button" data-drum="snare">Snare</button><button class="btn" type="button" data-drum="hat">Hi-hat</button></div><label class="music-control">Roll strokes <b data-roll-value>16</b><input type="range" min="4" max="32" step="4" value="16" data-roll-count></label><label class="music-control">Tempo <b data-drum-bpm-value>100</b> BPM<input type="range" min="50" max="180" value="100" data-drum-bpm></label><button class="btn primary" type="button" data-drum="roll">▶ Play double-stroke roll</button><div class="music-presets"><label>Groove preset <select data-drum-preset>${DRUM_PRESETS.map((p) => `<option value="${p.id}">${p.name}</option>`).join("")}</select></label><button class="btn small" type="button" data-apply-drum-preset>Load preset</button></div><div class="music-step-grid" aria-label="Custom one-bar drum groove">${[["kick", "Kick"], ["snare", "Snare"], ["hat", "Hi-hat"]].map(([kind, label]) => `<div class="music-step-row"><b>${label}</b>${Array.from({ length: 16 }, (_, i) => `<button type="button" class="music-step ${kind === "hat" ? "on" : ""}" data-step-kind="${kind}" data-step="${i}" aria-label="${label} step ${i + 1}" aria-pressed="${kind === "hat" ? "true" : "false"}"></button>`).join("")}</div>`).join("")}</div><button class="btn" type="button" data-play-groove>▶ Play custom groove</button></div>` : "";
  const selector = track.compare || track.voice === "guitar" ? `<label class="music-voice-label">Sound <select data-voice>${(track.voice === "guitar" ? [["acoustic", "Acoustic guitar"], ["clean", "Clean electric guitar"], ["power", "Electric power chord"]] : [["piano", "Piano"], ["acoustic", "Acoustic guitar"], ["clean", "Clean electric guitar"]]).map(([value, label]) => `<option value="${value}">${label}</option>`).join("")}</select></label>` : "";
  const tones = track.notes.length ? `<div class="music-audio-group"><h3>${track.voice === "guitar" ? "Tap a chord tone" : track.voice === "violin" ? "Open strings" : "Play a note"}</h3><div class="row music-audio-buttons">${noteButtons}</div></div>` : "";
  const vocal = track.voice === "voice" ? `<div class="music-audio-group"><h3>Chest voice vs head voice</h3><p class="muted">Chest and head voice describe different sensations and resonance strategies across the vocal range; they are not separate physical “voices.” A synthesized reference can show pitch and register, but it cannot reproduce every singer’s natural timbre.</p><div class="row music-audio-buttons"><button class="btn" type="button" data-vocal="chest">▶ Chest-register example · C3</button><button class="btn primary" type="button" data-vocal="head">▶ Head-register example · C5</button><button class="btn" type="button" data-vocal="glide">Compare gently · C3 to C5</button></div><p class="muted">Keep it light, stop if you feel pain or strain, and use a qualified voice teacher for personalized technique.</p></div>` : "";
  const sheet = track.voice === "drums" ? `<div class="music-audio-group"><h3>Read the roll</h3><div class="music-sheet-copy"><span>Count sixteenths</span><strong>1 e &amp; a 2 e &amp; a</strong><span>Hands</span><strong>R R L L R R L L</strong></div><p class="muted">Each pair is one hand’s double stroke. Keep the spacing even as you gradually raise the tempo.</p></div>` : `<div class="music-audio-group"><h3>Read and hear a C major phrase</h3><p class="muted">Treble clef: the note names sit under the staff. Middle C is on a ledger line below it.</p><div class="music-staff" role="img" aria-label="Treble staff showing C D E F G A B C"><svg viewBox="0 0 440 132" aria-hidden="true"><text x="5" y="93" class="staff-clef">𝄞</text>${[48,58,68,78,88].map((y) => `<line x1="42" y1="${y}" x2="430" y2="${y}" />`).join("")}${[60,62,64,65,67,69,71,72].map((midi, i) => { const y = [98, 93, 88, 83, 78, 73, 68, 63][i]; const x = 64 + i * 48; return `<ellipse cx="${x}" cy="${y}" rx="6" ry="4.3" transform="rotate(-18 ${x} ${y})" />${midi === 60 ? `<line x1="56" y1="98" x2="72" y2="98" />` : ""}<text x="${x}" y="124">${["C", "D", "E", "F", "G", "A", "B", "C"][i]}</text>`; }).join("")}</svg></div>${track.voice === "guitar" ? `<div class="music-guitar-phrase-tab"><b>Guitar TAB · same phrase · B string</b><div class="music-tab-row"><span>e</span><code>— — — — — — — —</code></div><div class="music-tab-row"><span>B</span><code>1 — 3 — 5 — 6 — 8 — 10 — 12 — 13</code></div><div class="music-tab-row"><span>G</span><code>— — — — — — — —</code></div><div class="music-tab-row"><span>D</span><code>— — — — — — — —</code></div><div class="music-tab-row"><span>A</span><code>— — — — — — — —</code></div><div class="music-tab-row"><span>E</span><code>— — — — — — — —</code></div><p class="muted">Numbers are fret positions; 0 would mean an open string. Read left to right with the staff above.</p></div>` : ""}<button class="btn" type="button" data-sheet-phrase>▶ Play the written phrase</button></div>`;
  const chromatic = track.voice === "drums" ? "" : `<div class="music-audio-group"><h3>Build a phrase with any note</h3><p class="muted">Choose an octave, then tap notes to add them to your phrase. Repeated notes are allowed; sharps and flats share a key.</p><label class="music-octave-label">Octave <select data-octave>${[2, 3, 4, 5, 6].map((n) => `<option value="${n}" ${n === 4 ? "selected" : ""}>${n}</option>`).join("")}</select></label><div class="music-chromatic-keys">${CHROMATIC.map((n, i) => `<button type="button" class="music-pitch ${[1, 3, 6, 8, 10].includes(i) ? "black-key" : ""}" data-pitch="${i}" aria-label="Add ${n.name} to phrase">${n.name}</button>`).join("")}</div><div class="music-presets"><label>Melody preset <select data-melody-preset>${PRESETS.map((p) => `<option value="${p.id}">${p.name}</option>`).join("")}</select></label><button class="btn small" type="button" data-load-melody>Load preset</button></div><div class="row music-phrase-controls"><button class="btn primary" type="button" data-play-phrase>▶ Play phrase</button><button class="btn" type="button" data-play-stack>Play together</button><button class="btn" type="button" data-clear-phrase>Clear</button><span class="muted" data-phrase-list aria-live="polite">No notes selected</span></div></div>`;
  return `<section class="panel clay music-room music-audio-room" data-music-station="${track.voice}">
    <div class="music-audio-intro"><div><span class="pill neutral">${mode === "practice" ? "Listen &amp; practice" : "Interactive listening"}</span><h2>${track.title} sound studio</h2><p>${track.intro}</p></div>${selector}</div>
    ${tones}${chromatic}${sheet}${chord}${power}${drum}${vocal}
    <div class="music-audio-group"><h3>Record and export</h3><p class="muted">Record your performance, then download it as WAV, MP3, or MIDI.</p><div class="row music-audio-buttons"><button class="btn primary" type="button" data-record>● Record</button><button class="btn" type="button" data-stop-record disabled>Stop &amp; prepare files</button><button class="btn" type="button" data-export="wav" disabled>Export WAV</button><button class="btn" type="button" data-export="mp3" disabled>Export MP3</button><button class="btn" type="button" data-export="midi">Export MIDI</button><span class="muted" data-record-status aria-live="polite">No recording yet</span></div></div>
    <p class="muted music-audio-status" aria-live="polite">Tap a sound to listen. Audio starts after your first tap.</p>
    <p class="muted music-audio-footnote">These are generated, offline instrument-style tones for learning pitch and note relationships; they do not require MIDI hardware.</p>
  </section>`;
}

function createAudio(root, track) {
  let audio;
  const getAudio = async () => {
    audio ||= new (window.AudioContext || window.webkitAudioContext)();
    if (!audio._musicMaster) {
      audio._musicMaster = audio.createGain();
      audio._musicStream = audio.createMediaStreamDestination();
      audio._musicMaster.connect(audio.destination);
      audio._musicMaster.connect(audio._musicStream);
    }
    if (audio.state !== "running") await audio.resume();
    return audio;
  };
  const midiHz = (midi) => 440 * (2 ** ((midi - 69) / 12));
  const envelope = (ctx, gain, start, peak, attack, decay, duration, release) => {
    gain.gain.setValueAtTime(0.0001, start);
    gain.gain.linearRampToValueAtTime(peak, start + attack);
    gain.gain.exponentialRampToValueAtTime(Math.max(0.0001, peak * decay), start + attack + Math.min(.18, duration * .45));
    gain.gain.exponentialRampToValueAtTime(.0001, start + duration + release);
  };
  const tone = (ctx, midi, start, voice, duration = .9, volume = .12) => {
    const frequency = midiHz(midi);
    const output = ctx.createGain();
    output.connect(ctx._musicMaster);
    const now = Math.max(start, ctx.currentTime);
    const isPiano = voice === "piano";
    const isViolin = voice === "violin";
    const isVocal = voice === "chest" || voice === "head";
    const peak = volume;
    envelope(ctx, output, now, peak, isViolin || isVocal ? .09 : .008, isPiano ? .2 : .56, duration, isViolin || isVocal ? .18 : .12);
    const osc = ctx.createOscillator();
    osc.type = isViolin || isVocal || voice === "power" ? "sawtooth" : isPiano ? "sine" : voice === "clean" ? "square" : "triangle";
    osc.frequency.setValueAtTime(frequency, now);
    if (isViolin) {
      const vibrato = ctx.createOscillator();
      const vibratoGain = ctx.createGain();
      vibrato.frequency.value = 5.2;
      vibratoGain.gain.value = 2.2;
      vibrato.connect(vibratoGain).connect(osc.frequency);
      vibrato.start(now + .24);
      vibrato.stop(now + duration + .1);
    }
    const filter = ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.value = isPiano ? 5200 : isViolin ? 3600 : isVocal ? (voice === "chest" ? 1250 : 2350) : voice === "clean" ? 1550 : voice === "power" ? 2100 : 2500;
    if (voice === "power") {
      const curve = new Float32Array(256);
      for (let i = 0; i < curve.length; i++) { const x = (i * 2) / (curve.length - 1) - 1; curve[i] = Math.tanh(x * 2.4); }
      const drive = ctx.createWaveShaper(); drive.curve = curve; drive.oversample = "2x";
      osc.connect(drive).connect(filter);
    } else osc.connect(filter);
    filter.connect(output);
    osc.start(now);
    osc.stop(now + duration + (isViolin ? .18 : .13));
    if (isPiano) {
      for (const [multiple, level] of [[2, .23], [3, .09]]) {
        const partial = ctx.createOscillator();
        const partialGain = ctx.createGain();
        partial.type = "sine";
        partial.frequency.value = frequency * multiple;
        partialGain.gain.value = level;
        partial.connect(partialGain).connect(output);
        partial.start(now);
        partial.stop(now + duration + .12);
      }
    }
    if (voice === "acoustic" || voice === "clean" || voice === "guitar" || voice === "power") {
      // A short filtered noise attack makes the picked string sound less like a plain oscillator.
      const length = Math.floor(ctx.sampleRate * .045);
      const buffer = ctx.createBuffer(1, length, ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < length; i++) data[i] = (Math.random() * 2 - 1) * (1 - i / length);
      const pluck = ctx.createBufferSource();
      const pluckFilter = ctx.createBiquadFilter();
      const pluckGain = ctx.createGain();
      pluck.buffer = buffer;
      pluckFilter.type = "bandpass";
      pluckFilter.frequency.value = Math.min(frequency * (voice === "power" ? 2 : 3), 3400);
      pluckFilter.Q.value = .7;
      pluckGain.gain.setValueAtTime(volume * .45, now);
      pluckGain.gain.exponentialRampToValueAtTime(.0001, now + .045);
      pluck.connect(pluckFilter).connect(pluckGain).connect(ctx._musicMaster);
      pluck.start(now);
    }
  };
  const drumHit = (ctx, kind, start, volume = .42) => {
    const now = Math.max(start, ctx.currentTime);
    if (kind === "kick") {
      const osc = ctx.createOscillator(); const gain = ctx.createGain();
      osc.type = "sine"; osc.frequency.setValueAtTime(145, now); osc.frequency.exponentialRampToValueAtTime(48, now + .13);
      gain.gain.setValueAtTime(volume, now); gain.gain.exponentialRampToValueAtTime(.0001, now + .24);
      osc.connect(gain).connect(ctx._musicMaster); osc.start(now); osc.stop(now + .25); return;
    }
    const length = Math.floor(ctx.sampleRate * (kind === "hat" ? .075 : .19));
    const buffer = ctx.createBuffer(1, length, ctx.sampleRate); const data = buffer.getChannelData(0);
    for (let i = 0; i < length; i++) data[i] = Math.random() * 2 - 1;
    const source = ctx.createBufferSource(); const filter = ctx.createBiquadFilter(); const gain = ctx.createGain();
    source.buffer = buffer; filter.type = kind === "hat" ? "highpass" : "bandpass"; filter.frequency.value = kind === "hat" ? 6800 : 1800; filter.Q.value = kind === "hat" ? .7 : .8;
    gain.gain.setValueAtTime(volume, now); gain.gain.exponentialRampToValueAtTime(.0001, now + (kind === "hat" ? .07 : .18));
    source.connect(filter).connect(gain).connect(ctx._musicMaster); source.start(now);
  };
  const setStatus = (text) => { const status = root.querySelector(".music-audio-status"); if (status) status.textContent = text; };
  const noteVoice = () => {
    const selected = root.querySelector("[data-voice]")?.value;
    return selected || track.voice;
  };
  const queued = [];
  const midiEvents = [];
  let midiCursor = 0;
  let midiBpm = 120;
  const addMidi = (notes, tick, duration = 240, channel = 0, velocity = 88) => notes.forEach((note) => midiEvents.push({ note, tick, duration, channel, velocity }));
  const noteLabel = (midi) => `${["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"][midi % 12]}${Math.floor(midi / 12) - 1}`;
  const drawGuitarChord = () => {
    const rootControl = root.querySelector("[data-guitar-root]");
    const qualityControl = root.querySelector("[data-guitar-quality]");
    if (!rootControl || !qualityControl) return;
    const rootMidi = 48 + Number(rootControl.value);
    const quality = GUITAR_CHORDS.find((item) => item.id === qualityControl.value) || GUITAR_CHORDS[0];
    const notes = quality.intervals.map((interval) => rootMidi + interval);
    const noteNames = notes.map(noteLabel);
    const noteList = root.querySelector("[data-guitar-notes]");
    noteList.innerHTML = `<b>${noteLabel(rootMidi)} ${quality.name}</b> · ${noteNames.join(" – ")}<span class="music-guitar-tone-list">${notes.map((midi, i) => `<button type="button" class="music-queue-note" data-guitar-tone="${midi}" aria-label="Play ${noteLabel(midi)}, ${quality.roles[i]}">${noteLabel(midi)} <small>${quality.roles[i]}</small></button>`).join("")}</span>`;
    const tab = root.querySelector("[data-guitar-tab]");
    if (quality.id !== "power") {
      tab.innerHTML = `<span class="muted">Power-chord TAB appears when Power chord is selected.</span>`;
      return;
    }
    const fret = rootMidi - 45; // root on the guitar's open A string (A2)
    const powerTab = [["e", "x"], ["B", "x"], ["G", fret + 2], ["D", fret + 2], ["A", fret], ["E", "x"]];
    tab.innerHTML = `<b>${noteLabel(rootMidi)}5 power-chord TAB</b>${powerTab.map(([string, position]) => `<div class="music-tab-row"><span>${string}</span><code>${position === "x" ? "— x —" : `— ${position} —`}</code></div>`).join("")}<small class="muted">Mute strings marked x; fret the three numbered strings together.</small>`;
  };
  root.querySelector("[data-guitar-root]")?.addEventListener("change", drawGuitarChord);
  root.querySelector("[data-guitar-quality]")?.addEventListener("change", drawGuitarChord);
  drawGuitarChord();
  root.querySelector("[data-guitar-notes]")?.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-guitar-tone]");
    if (!button) return;
    const midi = Number(button.dataset.guitarTone); const ctx = await getAudio();
    tone(ctx, midi, ctx.currentTime, noteVoice(), .8, .14); addMidi([midi], midiCursor); midiCursor += 240;
    setStatus(`Playing ${noteLabel(midi)} · ${noteVoice()}`);
  });
  root.querySelectorAll("[data-guitar-play]").forEach((button) => button.addEventListener("click", async () => {
    const rootMidi = 48 + Number(root.querySelector("[data-guitar-root]")?.value || 0);
    const quality = GUITAR_CHORDS.find((item) => item.id === root.querySelector("[data-guitar-quality]")?.value) || GUITAR_CHORDS[0];
    const notes = quality.intervals.map((interval) => rootMidi + interval);
    const voice = button.dataset.guitarPlay;
    const ctx = await getAudio();
    playNotes(ctx, notes, { voice, duration: 1.2 });
    setStatus(`Playing ${noteLabel(rootMidi)} ${quality.name} · ${notes.map(noteLabel).join(" – ")} · ${voice === "power" ? "distorted electric guitar" : voice === "clean" ? "clean electric guitar" : "acoustic guitar"}`);
  }));
  const drawQueue = () => {
    const list = root.querySelector("[data-phrase-list]"); if (!list) return;
    list.innerHTML = queued.length ? queued.map((midi, i) => `<button class="music-queue-note" type="button" data-remove-note="${i}" aria-label="Remove ${noteLabel(midi)}">${noteLabel(midi)} ×</button>`).join("") : "No notes selected";
  };
  const playNotes = (ctx, notes, { melody = false, voice = noteVoice(), duration = .42, tick = true } = {}) => {
    const now = ctx.currentTime + .025;
    notes.forEach((midi, i) => {
      const offset = melody ? i * duration : (track.voice === "guitar" ? i * .045 : i * .008);
      tone(ctx, midi, now + offset, voice, duration * (melody ? .92 : 2.2), .12);
      if (tick) addMidi([midi], midiCursor + i * (melody ? 240 : 0), melody ? 220 : 360);
    });
    if (tick) midiCursor += melody ? Math.max(240, notes.length * 240) : 480;
  };
  root.querySelectorAll("[data-play-note]").forEach((button) => button.addEventListener("click", async () => {
    const ctx = await getAudio(); const note = button.dataset.playNote; const voice = noteVoice();
    const midi = NOTES[note]; tone(ctx, midi, ctx.currentTime, voice === "power" ? "clean" : voice, .9, .14); addMidi([midi], midiCursor); midiCursor += 240;
    setStatus(`Playing ${note} · ${voice === "acoustic" ? "acoustic guitar" : voice === "clean" ? "clean electric guitar" : voice === "power" ? "electric guitar" : voice}`);
  }));
  root.querySelectorAll("[data-chord-id]").forEach((button) => button.addEventListener("click", async () => {
    const ctx = await getAudio(); const chord = CHORDS.find((item) => item.id === button.dataset.chordId); const guitar = track.voice === "guitar";
    const rootMidi = guitar ? 48 : 60; const notes = chord.intervals.map((interval) => rootMidi + interval);
    playNotes(ctx, notes, { voice: noteVoice(), duration: 1.1 });
    setStatus(`${chord.name}: ${chord.notes}`);
  }));
  root.querySelectorAll("[data-pitch]").forEach((button) => button.addEventListener("click", async () => {
    const ctx = await getAudio(); const pitch = Number(button.dataset.pitch); const octave = Number(root.querySelector("[data-octave]")?.value || 4);
    const midi = (octave + 1) * 12 + pitch; queued.push(midi); drawQueue();
    tone(ctx, midi, ctx.currentTime, noteVoice(), .6, .13);
    addMidi([midi], midiCursor, 220); midiCursor += 240;
    setStatus(`Added ${noteLabel(midi)} to your phrase`);
  }));
  root.querySelector("[data-phrase-list]")?.addEventListener("click", (event) => {
    const index = Number(event.target.closest("[data-remove-note]")?.dataset.removeNote);
    if (!Number.isInteger(index) || index < 0) return;
    queued.splice(index, 1); drawQueue();
  });
  root.querySelector("[data-play-phrase]")?.addEventListener("click", async () => {
    if (!queued.length) { setStatus("Add some notes to your phrase first"); return; }
    const ctx = await getAudio(); playNotes(ctx, queued, { melody: true, duration: .28 }); setStatus(`Playing ${queued.length} notes as a phrase`);
  });
  root.querySelector("[data-play-stack]")?.addEventListener("click", async () => {
    if (!queued.length) { setStatus("Add some notes to play first"); return; }
    const ctx = await getAudio(); playNotes(ctx, queued, { duration: .65 }); setStatus(`Playing ${queued.map(noteLabel).join(" + ")} together`);
  });
  root.querySelector("[data-clear-phrase]")?.addEventListener("click", () => { queued.length = 0; midiEvents.length = 0; midiCursor = 0; drawQueue(); setStatus("Phrase cleared"); });
  root.querySelector("[data-load-melody]")?.addEventListener("click", async () => {
    const preset = PRESETS.find((item) => item.id === root.querySelector("[data-melody-preset]").value);
    queued.splice(0, queued.length, ...preset.notes); drawQueue(); midiEvents.length = 0; midiCursor = 0; preset.notes.forEach((note, i) => addMidi([note], i * 240, 220)); midiCursor = preset.notes.length * 240;
    const ctx = await getAudio(); playNotes(ctx, preset.notes, { melody: true, duration: .25, tick: false }); setStatus(`Loaded and playing ${preset.name}`);
  });
  root.querySelector("[data-sheet-phrase]")?.addEventListener("click", async () => {
    const phrase = [60, 62, 64, 65, 67, 69, 71, 72]; queued.splice(0, queued.length, ...phrase); drawQueue();
    const ctx = await getAudio(); playNotes(ctx, phrase, { melody: true, duration: .31 }); setStatus("Reading and playing C–D–E–F–G–A–B–C from the treble staff");
  });
  root.querySelectorAll("[data-guitar-voice]").forEach((button) => button.addEventListener("click", async () => {
    const ctx = await getAudio(); const voice = button.dataset.guitarVoice; const notes = [48, 55, 60];
    playNotes(ctx, notes, { voice, duration: 1.25 }); setStatus(`Playing C power chord with ${voice === "power" ? "distortion" : "clean electric guitar"}`);
  }));
  root.querySelectorAll("[data-vocal]").forEach((button) => button.addEventListener("click", async () => {
    const ctx = await getAudio(); const kind = button.dataset.vocal;
    if (kind === "glide") {
      [48, 55, 60, 67, 72].forEach((midi, i) => tone(ctx, midi, ctx.currentTime + i * .38, midi < 60 ? "chest" : "head", .4, .09));
      [48, 55, 60, 67, 72].forEach((midi, i) => addMidi([midi], midiCursor + i * 180, 150)); midiCursor += 900;
      setStatus("Gentle register comparison from C3 to C5");
    } else {
      const midi = kind === "chest" ? 48 : 72; tone(ctx, midi, ctx.currentTime, kind, .9, .1); addMidi([midi], midiCursor, 360); midiCursor += 480;
      setStatus(`Playing a synthesized ${kind}-register reference at ${kind === "chest" ? "C3" : "C5"}`);
    }
  }));
  root.querySelector("[data-export='midi']")?.addEventListener("click", () => downloadBlob(midiFile(midiEvents, midiBpm), "learnmotion-composition.mid"));
  let recorder = null; let recordingChunks = []; let recordedWav = null;
  const recordStatus = (message) => { const el = root.querySelector("[data-record-status]"); if (el) el.textContent = message; };
  root.querySelector("[data-record]")?.addEventListener("click", async (event) => {
    const ctx = await getAudio();
    if (!window.MediaRecorder) { recordStatus("Recording is not supported in this browser"); return; }
    recordingChunks = []; recordedWav = null;
    const button = event.currentTarget; button.disabled = true;
    const stopButton = root.querySelector("[data-stop-record]"); if (stopButton) stopButton.disabled = false;
    root.querySelectorAll("[data-export='wav'], [data-export='mp3']").forEach((b) => { b.disabled = true; });
    recorder = new MediaRecorder(ctx._musicStream.stream);
    recorder.ondataavailable = (e) => { if (e.data.size) recordingChunks.push(e.data); };
    recorder.onstop = async () => {
      try {
        const raw = new Blob(recordingChunks, { type: recorder.mimeType || "audio/webm" });
        const decoded = await ctx.decodeAudioData(await raw.arrayBuffer()); recordedWav = audioBufferToWav(decoded);
        root.querySelectorAll("[data-export='wav'], [data-export='mp3']").forEach((b) => { b.disabled = false; });
        recordStatus("Recording ready · WAV and MP3 exports available");
      } catch { recordStatus("Could not decode this browser's recording format"); }
      if (button.isConnected) button.disabled = false;
      if (stopButton?.isConnected) stopButton.disabled = true;
    };
    recorder.start(); recordStatus("Recording · play notes, chords, or a drum groove now");
  });
  root.querySelector("[data-stop-record]")?.addEventListener("click", () => { if (recorder?.state === "recording") { recorder.stop(); recordStatus("Preparing audio file…"); } });
  root.querySelector("[data-export='wav']")?.addEventListener("click", () => recordedWav && downloadBlob(recordedWav, "learnmotion-performance.wav"));
  root.querySelector("[data-export='mp3']")?.addEventListener("click", async (event) => {
    if (!recordedWav) return;
    const button = event.currentTarget; button.disabled = true; recordStatus("Converting to MP3…");
    try {
      const bytes = new Uint8Array(await recordedWav.arrayBuffer()); let binary = "";
      for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
      const response = await fetch("/api/music/mp3", { method: "POST", headers: { "Content-Type": "application/json", "X-K8s-Playground": "1" }, body: JSON.stringify({ wav: btoa(binary) }) });
      if (!response.ok) throw new Error((await response.json()).error || "MP3 conversion is unavailable");
      downloadBlob(await response.blob(), "learnmotion-performance.mp3"); recordStatus("MP3 exported");
    } catch (error) { recordStatus(error.message || "MP3 export failed"); }
    button.disabled = false;
  });
  root.querySelectorAll("[data-step]").forEach((button) => button.addEventListener("click", () => {
    const active = button.classList.toggle("on"); button.setAttribute("aria-pressed", String(active));
  }));
  root.querySelector("[data-apply-drum-preset]")?.addEventListener("click", () => {
    const preset = DRUM_PRESETS.find((item) => item.id === root.querySelector("[data-drum-preset]").value);
    root.querySelectorAll("[data-step]").forEach((button) => {
      const active = preset[button.dataset.stepKind].includes(Number(button.dataset.step));
      button.classList.toggle("on", active); button.setAttribute("aria-pressed", String(active));
    });
    setStatus(`Loaded ${preset.name} into the 16-step groove`);
  });
  root.querySelector("[data-play-groove]")?.addEventListener("click", async () => {
    const ctx = await getAudio(); const bpm = Number(root.querySelector("[data-drum-bpm]").value); const interval = 60 / bpm / 4;
    midiBpm = bpm;
    root.querySelectorAll("[data-step].on").forEach((button) => {
      const step = Number(button.dataset.step); const kind = button.dataset.stepKind; const note = kind === "kick" ? 36 : kind === "snare" ? 38 : 42;
      drumHit(ctx, kind, ctx.currentTime + step * interval, kind === "hat" ? .14 : .32); addMidi([note], midiCursor + step * 120, 72, 9, kind === "hat" ? 55 : 88);
    });
    midiCursor += 1920;
    setStatus(`Playing your custom ${bpm} BPM drum groove`);
  });
  root.querySelector("[data-roll-count]")?.addEventListener("input", (event) => { root.querySelector("[data-roll-value]").textContent = event.target.value; });
  root.querySelector("[data-drum-bpm]")?.addEventListener("input", (event) => { root.querySelector("[data-drum-bpm-value]").textContent = event.target.value; });
  root.querySelectorAll("[data-drum]").forEach((button) => button.addEventListener("click", async () => {
    const ctx = await getAudio(); const kind = button.dataset.drum;
    if (kind === "roll") {
      const count = Number(root.querySelector("[data-roll-count]")?.value || 16); const bpm = Number(root.querySelector("[data-drum-bpm]")?.value || 100); const interval = 60 / bpm / 4;
      midiBpm = bpm;
      for (let i = 0; i < count; i++) { drumHit(ctx, "snare", ctx.currentTime + i * interval, i % 2 === 0 ? .32 : .23); addMidi([38], midiCursor + i * 60, 44, 9, i % 2 === 0 ? 92 : 66); }
      midiCursor += count * 60;
      setStatus(`Double-stroke roll · ${count} strokes at ${bpm} BPM: R-R, L-L`);
      return;
    }
    drumHit(ctx, kind, ctx.currentTime); addMidi([kind === "kick" ? 36 : kind === "snare" ? 38 : 42], midiCursor, 72, 9); midiCursor += 120;
    setStatus(`Playing ${kind === "hat" ? "hi-hat" : kind}`);
  }));
  return () => { if (audio && audio.state !== "closed") audio.close(); };
}

export function lab(root, content) {
  const subject = content.subject.id;
  const track = TRACKS[subject] || TRACKS.music;
  shell(root, `${track.title} Practice Room`, "Build a relaxed, accurate practice routine with clear sounds and a steady pulse.", `<div class="panel clay music-room music-metronome">
    <p>Set a comfortable tempo, listen to a few beats, then practice a short phrase along with the pulse.</p>
    <label for="musicTempo">Tempo: <b id="musicTempoValue">80</b> BPM</label>
    <input id="musicTempo" type="range" min="40" max="180" value="80">
    <div class="row"><button class="btn primary" id="musicStart" type="button">Start metronome</button><span class="pill neutral" id="musicBeat" aria-live="polite">Ready</span></div>
    <p class="muted">Keep your shoulders, hands, and breathing relaxed. Stop if anything feels uncomfortable.</p>
  </div>${stationMarkup(track, "practice")}`);
  const tempo = root.querySelector("#musicTempo");
  const value = root.querySelector("#musicTempoValue");
  const start = root.querySelector("#musicStart");
  const beat = root.querySelector("#musicBeat");
  let timer = null; let audio = null; let count = 0;
  const stop = () => { clearInterval(timer); timer = null; start.textContent = "Start metronome"; beat.textContent = "Paused"; };
  const tick = () => {
    count = count % 4 + 1; beat.textContent = `Beat ${count} of 4`;
    if (!audio) return;
    const osc = audio.createOscillator(); const gain = audio.createGain();
    osc.frequency.value = count === 1 ? 1100 : 750; gain.gain.setValueAtTime(.12, audio.currentTime); gain.gain.exponentialRampToValueAtTime(.001, audio.currentTime + .06);
    osc.connect(gain).connect(audio.destination); osc.start(); osc.stop(audio.currentTime + .065);
  };
  const play = () => { audio ||= new (window.AudioContext || window.webkitAudioContext)(); audio.resume(); tick(); timer = setInterval(tick, 60000 / Number(tempo.value)); start.textContent = "Stop metronome"; };
  tempo.addEventListener("input", () => { value.textContent = tempo.value; if (timer) { stop(); play(); } });
  start.addEventListener("click", () => timer ? stop() : play());
  const stopStation = createAudio(root, track);
  return () => { stop(); audio?.close(); stopStation(); };
}

export function playground(root, content) {
  const track = TRACKS[content.subject.id] || TRACKS.music;
  shell(root, `${track.title} Listening Room`, "Explore pitch, chord tones, and instrument sound by listening and tapping.", stationMarkup(track, "listen"));
  return createAudio(root, track);
}

function scoreLessonMarkup(track) {
  const keyboard = track.voice === "piano" ? `<div class="music-score-keyboard" data-score-keyboard aria-label="Piano keys from C4 through C6">${Array.from({ length: 25 }, (_, i) => `<button type="button" class="music-score-key ${[1, 3, 6, 8, 10].includes(i % 12) && i < 24 ? "black-key" : ""}" data-score-midi="${60 + i}" data-score-key="${(60 + i) % 12}" aria-label="${CHROMATIC[(60 + i) % 12].name}${Math.floor((60 + i) / 12) - 1}">${(i % 12 === 0) || i === 24 ? `C${4 + Math.floor(i / 12)}` : CHROMATIC[(60 + i) % 12].name}</button>`).join("")}</div>` : "";
  return `<details class="music-lesson-details"><summary><span><b>Hear and try it</b><small>Listen to the notes and follow them on the staff</small></span><span class="music-disclosure" aria-hidden="true">+</span></summary><section class="music-lesson-score" aria-label="Interactive music notation">
    <h3>Explore a note pattern</h3><p class="muted">Choose any tonic and scale. Read the treble staff, follow the highlighted notes, and listen as the keyboard or guitar fingering is played.</p>
    <div class="music-score-controls"><label>Starting note <select data-score-root>${CHROMATIC.map((n, i) => `<option value="${i}">${n.name}</option>`).join("")}</select></label><label>Scale <select data-score-scale>${SCORE_SCALES.map((s) => `<option value="${s.id}">${s.name}</option>`).join("")}</select></label></div>
    <h4 data-score-heading>C major</h4><div class="music-staff music-score-staff" data-score-staff role="img" aria-label="Treble staff for selected scale"></div>
    ${keyboard}
    ${track.voice === "guitar" ? `<div class="music-guitar-phrase-tab music-score-tab" data-score-tab aria-label="Six-string guitar tablature for selected scale"></div><p class="muted">Read guitar TAB from the high e string down to low E. Fret numbers line up with the notes above.</p>` : ""}
    <button class="btn primary" type="button" data-score-play>▶ Play selected scale</button><p class="muted music-score-status" data-score-status aria-live="polite">Choose a key and scale, then play it.</p>
  </section></details>`;
}

function createScoreLesson(root, track) {
  const sharpNames = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"];
  const stringTunings = [{ name: "e", midi: 64 }, { name: "B", midi: 59 }, { name: "G", midi: 55 }, { name: "D", midi: 50 }, { name: "A", midi: 45 }, { name: "E", midi: 40 }];
  let notes = [];
  let audio;
  let playbackTimers = new Set();
  const pitchName = (midi) => `${sharpNames[((midi % 12) + 12) % 12]}${Math.floor(midi / 12) - 1}`;
  const playMidi = (midi, duration = .38) => {
    const osc = audio.createOscillator(); const gain = audio.createGain();
    osc.type = track.voice === "guitar" ? "triangle" : track.voice === "violin" ? "sawtooth" : "sine";
    osc.frequency.value = 440 * (2 ** ((midi - 69) / 12));
    gain.gain.setValueAtTime(.0001, audio.currentTime); gain.gain.linearRampToValueAtTime(.13, audio.currentTime + .012);
    gain.gain.exponentialRampToValueAtTime(.0001, audio.currentTime + duration);
    osc.connect(gain).connect(audio.destination); osc.start(); osc.stop(audio.currentTime + duration + .02);
  };
  const draw = () => {
    const rootPc = Number(root.querySelector("[data-score-root]")?.value || 0);
    const scale = SCORE_SCALES.find((item) => item.id === root.querySelector("[data-score-scale]")?.value) || SCORE_SCALES[0];
    notes = scale.steps.map((step) => 60 + rootPc + step);
    const rootName = sharpNames[rootPc];
    root.querySelector("[data-score-heading]").textContent = `${rootName} ${scale.name}`;
    const rootLetter = ["C", "C", "D", "D", "E", "F", "F", "G", "G", "A", "A", "B"][rootPc];
    const letters = ["C", "D", "E", "F", "G", "A", "B"];
    const naturalPitches = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
    const rootLetterIndex = letters.indexOf(rootLetter);
    const width = Math.max(380, 102 + (notes.length - 1) * 48);
    const xFor = (i) => 66 + i * 48;
    const noteMarkup = notes.map((midi, i) => {
      const degree = scale.degrees[i];
      let letter; let staffStep; let accidental = "";
      if (scale.id === "chromatic") {
        const name = sharpNames[midi % 12]; letter = name[0];
        staffStep = 28 + letters.indexOf(letter) + (Math.floor(midi / 12) - 4) * 7;
        accidental = name.length > 1 ? "♯" : "";
      } else {
        const absoluteDegree = rootLetterIndex + degree;
        letter = letters[absoluteDegree % 7];
        staffStep = 28 + absoluteDegree;
        const expected = 60 + Math.floor(absoluteDegree / 7) * 12 + naturalPitches[letter];
        let diff = ((midi - expected + 18) % 12) - 6;
        accidental = diff === 1 ? "♯" : diff === -1 ? "♭" : "";
      }
      const y = 98 - (staffStep - 28) * 5; const x = xFor(i);
      const ledger = y >= 98 && (y - 98) % 10 === 0 || y < 48 && (48 - y) % 10 === 0 ? `<line class="score-ledger" x1="${x - 9}" y1="${y}" x2="${x + 9}" y2="${y}" />` : "";
      return `${ledger}<ellipse class="score-note" data-score-note="${i}" cx="${x}" cy="${y}" rx="7" ry="5" transform="rotate(-18 ${x} ${y})" /><text class="score-label" x="${x}" y="124">${accidental}${letter}</text>`;
    }).join("");
    root.querySelector("[data-score-staff]").innerHTML = `<svg viewBox="0 0 ${width} 134" aria-hidden="true"><text x="3" y="94" class="staff-clef">𝄞</text>${[48, 58, 68, 78, 88].map((y) => `<line class="staff-line" x1="42" y1="${y}" x2="${width - 8}" y2="${y}" />`).join("")}${noteMarkup}</svg>`;
    const keyboardEl = root.querySelector("[data-score-keyboard]");
    if (keyboardEl) keyboardEl.querySelectorAll("[data-score-midi]").forEach((key) => key.classList.toggle("in-scale", notes.includes(Number(key.dataset.scoreMidi))));
    const tab = root.querySelector("[data-score-tab]");
    if (tab) {
      let priorString = -1;
      const frets = notes.map((midi) => {
        const choices = stringTunings.map((string, index) => ({ index, fret: midi - string.midi })).filter((choice) => choice.fret >= 0 && choice.fret <= 20);
        choices.sort((a, b) => (Math.abs(a.fret - 5) + (a.index === priorString ? 2 : 0)) - (Math.abs(b.fret - 5) + (b.index === priorString ? 2 : 0)));
        const selected = choices[0] || { index: -1, fret: -1 }; priorString = selected.index;
        return selected;
      });
      tab.innerHTML = `<b>Guitar TAB · ${rootName} ${scale.name}</b>${stringTunings.map((string, row) => `<div class="music-tab-grid-row" style="--tab-note-count:${notes.length}"><span>${string.name}</span>${frets.map((fret, col) => `<code data-score-tab-note="${col}" class="${fret.index === row ? "has-fret" : ""}">${fret.index === row ? fret.fret : "·"}</code>`).join("")}</div>`).join("")}`;
    }
  };
  const stopPlayback = () => { playbackTimers.forEach((timer) => clearTimeout(timer)); playbackTimers.clear(); root.querySelectorAll(".score-note.playing, .music-score-key.playing, [data-score-tab-note].playing").forEach((el) => el.classList.remove("playing")); };
  root.querySelectorAll("[data-score-root], [data-score-scale]").forEach((control) => control.addEventListener("change", () => { stopPlayback(); draw(); }));
  root.querySelector("[data-score-keyboard]")?.addEventListener("click", async (event) => {
    const key = event.target.closest("[data-score-key]"); if (!key) return;
    const midi = Number(key.dataset.scoreMidi); audio ||= new (window.AudioContext || window.webkitAudioContext)(); await audio.resume();
    playMidi(midi, .45);
    root.querySelector("[data-score-status]").textContent = `Playing ${pitchName(midi)}`;
  });
  root.querySelector("[data-score-play]")?.addEventListener("click", async () => {
    stopPlayback(); audio ||= new (window.AudioContext || window.webkitAudioContext)(); await audio.resume();
    const keyboard = root.querySelector("[data-score-keyboard]"); const staff = root.querySelector("[data-score-staff]"); const tab = root.querySelector("[data-score-tab]");
    notes.forEach((midi, i) => {
      const at = i * 420; const timer = setTimeout(() => {
        const note = staff.querySelector(`[data-score-note="${i}"]`); note?.classList.add("playing");
        const key = [...(keyboard?.querySelectorAll("[data-score-midi]") || [])].find((el) => Number(el.dataset.scoreMidi) === midi); key?.classList.add("playing");
        tab?.querySelectorAll(`[data-score-tab-note="${i}"]`).forEach((cell) => cell.classList.add("playing"));
        playMidi(midi, .38);
        const clearTimer = setTimeout(() => { note?.classList.remove("playing"); key?.classList.remove("playing"); tab?.querySelectorAll(`[data-score-tab-note="${i}"]`).forEach((cell) => cell.classList.remove("playing")); playbackTimers.delete(clearTimer); }, 390); playbackTimers.add(clearTimer); playbackTimers.delete(timer);
      }, at); playbackTimers.add(timer);
    });
    root.querySelector("[data-score-status]").textContent = `Playing ${notes.length} notes in sequence`;
  });
  draw();
  return () => { stopPlayback(); audio?.close(); };
}

export function lesson(root, subjectId, topic = {}) {
  const title = topic.title || "";
  const relevant = /\b(notes?|scales?|octaves?|pitch|chromatic|intervals?|key signatures?|middle c)\b/i.test(title);
  if (!relevant) { root.replaceChildren(); return () => {}; }
  const track = TRACKS[subjectId] || TRACKS.music;
  root.innerHTML = `<section class="music-lesson-mount">${scoreLessonMarkup(track)}</section>`;
  return createScoreLesson(root, track);
}
