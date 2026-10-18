// Inline subject icons; they inherit currentColor plus two accent CSS variables.
const svg = (body) => `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${body}</svg>`;

export const ICONS = {
  db: svg(`<ellipse cx="24" cy="11" rx="15" ry="6" fill="var(--i1)" stroke="none" opacity=".9"/><path d="M9 11v26c0 3.3 6.7 6 15 6s15-2.7 15-6V11"/><path d="M9 20c0 3.3 6.7 6 15 6s15-2.7 15-6M9 29c0 3.3 6.7 6 15 6s15-2.7 15-6"/><ellipse cx="24" cy="11" rx="15" ry="6"/>`),
  sysdesign: svg(`<rect x="18" y="4" width="12" height="10" rx="3" fill="var(--i1)" stroke="none"/><rect x="4" y="34" width="12" height="10" rx="3" fill="var(--i2)" stroke="none"/><rect x="32" y="34" width="12" height="10" rx="3" fill="var(--i2)" stroke="none"/><rect x="18" y="34" width="12" height="10" rx="3"/><path d="M24 14v10M10 34v-6h28v6M24 24v10"/>`),
  git: svg(`<circle cx="14" cy="10" r="5" fill="var(--i1)" stroke="none"/><circle cx="14" cy="38" r="5"/><circle cx="34" cy="20" r="5" fill="var(--i2)" stroke="none"/><path d="M14 15v18M34 25c0 8-20 4-20 8"/>`),
  python: svg(`<path d="M24 4c-8 0-9 3.5-9 7v5h10v2H10c-4 0-6 3-6 8s2 9 6 9h4v-6c0-4 3-7 7-7h10c3 0 5-2 5-5v-6c0-4-4-7-12-7z" fill="var(--i1)" stroke="none"/><path d="M24 44c8 0 9-3.5 9-7v-5H23v-2h15c4 0 6-3 6-8s-2-9-6-9h-4v6c0 4-3 7-7 7H17c-3 0-5 2-5 5v6c0 4 4 7 12 7z" fill="var(--i2)" stroke="none"/><circle cx="19.5" cy="9.5" r="1.8" fill="currentColor" stroke="none"/><circle cx="28.5" cy="38.5" r="1.8" fill="currentColor" stroke="none"/>`),
  aws: svg(`<path d="M14 32h22a8 8 0 0 0 0-16 11 11 0 0 0-21-2 9 9 0 0 0-1 18z" fill="var(--i1)" stroke="none" opacity=".9"/><path d="M14 32h22a8 8 0 0 0 0-16 11 11 0 0 0-21-2 9 9 0 0 0-1 18z"/><path d="M12 40c8 4 16 4 24 0" stroke="var(--i2)"/><path d="M33 37l3 3-4 1"  stroke="var(--i2)"/>`),
  cicd: svg(`<path d="M6 24c0-5 4-9 9-9 8 0 10 18 18 18 5 0 9-4 9-9s-4-9-9-9c-8 0-10 18-18 18-5 0-9-4-9-9z"/><circle cx="15" cy="24" r="4" fill="var(--i1)" stroke="none"/><circle cx="33" cy="24" r="4" fill="var(--i2)" stroke="none"/><path d="M22 11l3 3-3 3" stroke="var(--i1)"/>`),
  dsa: svg(`<rect x="6" y="30" width="7" height="12" rx="2" fill="var(--i1)" stroke="none"/><rect x="16" y="22" width="7" height="20" rx="2" fill="var(--i1)" stroke="none" opacity=".8"/><rect x="26" y="14" width="7" height="28" rx="2" fill="var(--i2)" stroke="none"/><rect x="36" y="6" width="7" height="36" rx="2" fill="var(--i2)" stroke="none" opacity=".85"/><path d="M6 12c6-6 14-6 20 0" /><path d="M23 9l3 3-4 1"/>`),
  qa: svg(`<path d="M24 4l16 6v12c0 10-7 18-16 22C15 40 8 32 8 22V10z" fill="var(--i1)" stroke="none" opacity=".9"/><path d="M24 4l16 6v12c0 10-7 18-16 22C15 40 8 32 8 22V10z"/><path d="M16 24l6 6 11-12" stroke="var(--i2)" stroke-width="4"/>`),
  ds: svg(`<path d="M6 6v36h36"/><circle cx="14" cy="32" r="3" fill="var(--i1)" stroke="none"/><circle cx="20" cy="26" r="3" fill="var(--i1)" stroke="none"/><circle cx="27" cy="28" r="3" fill="var(--i2)" stroke="none"/><circle cx="32" cy="18" r="3" fill="var(--i2)" stroke="none"/><circle cx="38" cy="12" r="3" fill="var(--i1)" stroke="none"/><path d="M11 36L41 9" stroke-dasharray="3 4"/>`),
  ml: svg(`<path d="M10 12l14 12M10 24h14M10 36l14-12M24 24l14-10M24 24l14 10M10 12l14 0M24 12l14 2M10 36l14 0M24 36l14-2" stroke-width="1.8" opacity=".7"/><circle cx="10" cy="12" r="4" fill="var(--i1)" stroke="none"/><circle cx="10" cy="24" r="4" fill="var(--i1)" stroke="none"/><circle cx="10" cy="36" r="4" fill="var(--i1)" stroke="none"/><circle cx="24" cy="12" r="4"/><circle cx="24" cy="24" r="4"/><circle cx="24" cy="36" r="4"/><circle cx="38" cy="14" r="4" fill="var(--i2)" stroke="none"/><circle cx="38" cy="34" r="4" fill="var(--i2)" stroke="none"/>`),
  networking: svg(`<circle cx="24" cy="24" r="5" fill="var(--i1)" stroke="none"/><circle cx="9" cy="10" r="4"/><circle cx="39" cy="10" r="4"/><circle cx="9" cy="38" r="4"/><circle cx="39" cy="38" r="4"/><path d="M20 21L12 13M28 21l8-8M20 27l-8 8M28 27l8 8M9 14v20M39 14v20M14 10h20" stroke="var(--i2)"/>`),
  security: svg(`<path d="M24 4l16 6v12c0 10-7 18-16 22C15 40 8 32 8 22V10z" fill="var(--i1)" stroke="none" opacity=".9"/><path d="M24 4l16 6v12c0 10-7 18-16 22C15 40 8 32 8 22V10z"/><rect x="17" y="21" width="14" height="12" rx="3"/><path d="M20 21v-4a4 4 0 0 1 8 0v4M24 25v4" stroke="var(--i2)"/>`),
  go: svg(`<ellipse cx="24" cy="24" rx="18" ry="10" fill="var(--i1)" stroke="none"/><circle cx="17" cy="23" r="3" fill="#fff" stroke="none"/><circle cx="31" cy="23" r="3" fill="#fff" stroke="none"/><path d="M18 31c4 3 8 3 12 0" stroke="var(--i2)"/><path d="M11 17l-4-4M37 17l4-4" stroke="var(--i2)"/>`),
  kafka: svg(`<path d="M8 10h23a7 7 0 0 1 0 14H17a7 7 0 0 0 0 14h23"/><circle cx="8" cy="10" r="4" fill="var(--i1)" stroke="none"/><circle cx="40" cy="38" r="4" fill="var(--i2)" stroke="none"/><path d="M18 17h10M20 31h10" stroke-dasharray="2 4"/>`),
  azure: svg(`<path d="M7 35L20 9l7 10-8 16z" fill="var(--i1)" stroke="none"/><path d="M20 35l10-16 11 16H20z" fill="var(--i2)" stroke="none"/><path d="M7 35h34"/>`),
  gcp: svg(`<path d="M15 34a10 10 0 0 1 0-20c2-7 12-10 18-4a11 11 0 0 1 1 19" stroke="var(--i1)"/><path d="M13 36h22" stroke="var(--i2)"/><circle cx="24" cy="25" r="5" fill="var(--i1)" stroke="none"/>`),
  nodejs: svg(`<path d="M24 4l17 10v20L24 44 7 34V14z" fill="var(--i1)" stroke="none"/><path d="M24 4l17 10v20L24 44 7 34V14z"/><path d="M15 27c2 3 5 4 9 4s7-1 9-4" stroke="var(--i2)"/><circle cx="18" cy="22" r="2" fill="#fff" stroke="none"/><circle cx="30" cy="22" r="2" fill="#fff" stroke="none"/>`),
  observability: svg(`<path d="M5 25h8l5-13 8 25 6-17 4 5h7" stroke="var(--i1)"/><circle cx="18" cy="12" r="2" fill="var(--i2)" stroke="none"/><circle cx="26" cy="37" r="2" fill="var(--i2)" stroke="none"/>`),
  ansible: svg(`<circle cx="24" cy="24" r="18"/><path d="M17 32l7-17 8 17M20 26h9" stroke="var(--i1)"/>`),
  artifactory: svg(`<path d="M8 12h32v24H8z"/><path d="M13 18h22M13 24h15M13 30h18" stroke="var(--i1)"/><circle cx="35" cy="30" r="2" fill="var(--i2)" stroke="none"/>`),
  terraform: svg(`<path d="M5 10l13 7v15L5 25z" fill="var(--i1)" stroke="none"/><path d="M20 18l13 7v15l-13-7z" fill="var(--i2)" stroke="none"/><path d="M20 3l13 7v14l-13-7z"/>`),
  helm: svg(`<path d="M24 5l16 9v20l-16 9-16-9V14z"/><path d="M24 5v18m16-9l-16 9-16-9m16 9v19" stroke="var(--i1)"/><circle cx="24" cy="23" r="3" fill="var(--i2)" stroke="none"/>`),
  argocd: svg(`<path d="M24 6l15 7v11c0 9-6 15-15 19-9-4-15-10-15-19V13z"/><path d="M15 25h18M24 16v18" stroke="var(--i1)"/><circle cx="24" cy="25" r="4" fill="var(--i2)" stroke="none"/>`),
  guitar: svg(`<path d="M28 9l10-5 6 6-5 10-5-2-6 6c4 7-1 17-8 20-7 3-15-2-14-10 1-7 10-11 16-7l6-6-2-5z" fill="var(--i1)" stroke="none" opacity=".8"/><path d="M28 9l10-5 6 6-5 10-5-2-6 6c4 7-1 17-8 20-7 3-15-2-14-10 1-7 10-11 16-7l6-6-2-5z"/><circle cx="17" cy="32" r="3" stroke="var(--i2)"/><path d="M30 8l8 8M8 28l15-15" stroke="var(--i2)"/>`),
  theory: svg(`<path d="M8 34V15l18-8v24"/><ellipse cx="4.5" cy="36" rx="5" ry="3.5" fill="var(--i1)" stroke="none"/><ellipse cx="22.5" cy="32" rx="5" ry="3.5" fill="var(--i2)" stroke="none"/><path d="M26 12c8-4 13-1 13 4s-6 8-13 8"/>`),
  drums: svg(`<ellipse cx="24" cy="29" rx="16" ry="11" fill="var(--i1)" stroke="none" opacity=".75"/><ellipse cx="24" cy="29" rx="16" ry="11"/><path d="M8 29v8c0 6 32 6 32 0v-8M9 12h30M12 8l24 8M36 8L12 16" stroke="var(--i2)"/><path d="M15 8l-7-4M33 8l7-4"/>`),
  violin: svg(`<path d="M17 9c-4 4-4 8 0 11l-3 7c-5 3-6 10-2 14s11 3 13-2l5-5c4-3 4-7 1-10l3-5c4-3 4-8 0-11s-8-2-10 2l-5 3-2-4z" fill="var(--i1)" stroke="none" opacity=".75"/><path d="M17 9c-4 4-4 8 0 11l-3 7c-5 3-6 10-2 14s11 3 13-2l5-5c4-3 4-7 1-10l3-5c4-3 4-8 0-11s-8-2-10 2l-5 3-2-4z"/><path d="M20 18l11 12M24 15l-7 16M34 5l-9 38" stroke="var(--i2)"/>`),
  piano: svg(`<rect x="5" y="10" width="38" height="28" rx="4" fill="var(--i1)" stroke="none" opacity=".8"/><rect x="5" y="10" width="38" height="28" rx="4"/><path d="M13 11v18M20 11v18M27 11v18M34 11v18M5 29h38" stroke="var(--i2)"/><path d="M10 11v11M17 11v11M31 11v11M38 11v11" stroke="currentColor" stroke-width="4"/>`),
  voice: svg(`<path d="M24 29a7 7 0 0 0 7-7V13a7 7 0 0 0-14 0v9a7 7 0 0 0 7 7z" fill="var(--i1)" stroke="none"/><path d="M12 22a12 12 0 0 0 24 0M24 34v8m-7 0h14" stroke="var(--i2)"/>`),
  react: svg(`<circle cx="24" cy="24" r="3.5" fill="var(--i1)" stroke="none"/><ellipse cx="24" cy="24" rx="19" ry="8"/><ellipse cx="24" cy="24" rx="19" ry="8" transform="rotate(60 24 24)"/><ellipse cx="24" cy="24" rx="19" ry="8" transform="rotate(120 24 24)"/>`),
  sonarqube: svg(`<circle cx="22" cy="22" r="14"/><path d="M12 22a10 10 0 0 1 18-6M14 29a10 10 0 0 0 18 0" stroke="var(--i1)"/><path d="M32 32l9 9" stroke="var(--i2)"/>`),
  css: svg(`<path d="M24 5l16 6-2 20-14 12L10 31 8 11z" fill="var(--i1)" stroke="none" opacity=".7"/><path d="M24 5l16 6-2 20-14 12L10 31 8 11z"/><path d="M15 17h18M14 23h16M17 29h10" stroke="var(--i2)"/>`),
  all: svg(`<circle cx="15" cy="15" r="8" fill="var(--i1)" stroke="none"/><rect x="26" y="7" width="16" height="16" rx="5" fill="var(--i2)" stroke="none"/><rect x="6" y="26" width="16" height="16" rx="5"/><path d="M34 26l8 14H26z"/>`),
};

const LOGOS = new Set(["k8s", "db", "sysdesign", "git", "python", "aws", "linux", "java", "cicd", "dsa", "qa", "ds", "ml", "go", "security", "networking", "kafka", "azure", "gcp", "nodejs", "javascript", "nginx", "react", "css", "sonarqube", "artifactory", "ansible", "observability", "terraform", "helm", "argocd", "guitar", "theory", "drums", "violin", "piano"]);
const DARK_VARIANT = new Set(["db", "aws"]);

export function subjectIcon(s, staticRoot, { loading = "eager" } = {}) {
  const id = s?.id || "all";
  if (LOGOS.has(id)) {
    const img = (file, cls) => `<img class="${cls}" src="${staticRoot}img/${file}" alt="" width="32" height="32" loading="${loading}" decoding="async">`;
    if (id === "theory") return img("music-logo.webp", "logo");
    return DARK_VARIANT.has(id)
      ? img(`${id}-logo.webp`, "logo logo-light") + img(`${id}-logo-dark.webp`, "logo logo-dark")
      : img(`${id}-logo.webp`, "logo");
  }
  const [a, b] = s?.art || ["#8f7dff", "#46e0c4"];
  return `<span class="sicon" style="--i1:${a};--i2:${b}">${ICONS[id] || ICONS.all}</span>`;
}

// The all-subjects mark: a 2x2 tile where each cell cross-fades through every subject logo.
// Cells are offset by a quarter of the list, so the four cells never show the same logo at once.
export const LOGO_SLOT_SECONDS = 2.5;

function fadeKeyframes(n) {
  const slot = 100 / n;
  const pct = (x) => `${Math.min(100, x).toFixed(2)}%`;
  return `@keyframes alFade${n} { 0% { opacity: 0; transform: scale(.7); } ${pct(slot * 0.3)}, ${pct(slot)} { opacity: 1; transform: none; } ${pct(slot * 1.3)}, 100% { opacity: 0; transform: scale(.85); } }`;
}

export function appLogo(subjects, staticRoot) {
  const n = subjects.length;
  const shift = Math.max(1, Math.floor(n / 4));
  const cells = [0, 1, 2, 3].map((c) => subjects.map((s, i) => {
    const delay = ((((i - shift * c) % n) + n) % n) * LOGO_SLOT_SECONDS;
    return `<span class="al-item" style="animation-delay:${delay}s">${subjectIcon(s, staticRoot)}</span>`;
  }).join(""));
  return `<style>${fadeKeyframes(n)}</style><span class="app-logo" style="--al-cycle:${n * LOGO_SLOT_SECONDS}s;--al-anim:alFade${n}">${cells.map((c) => `<span class="al-cell">${c}</span>`).join("")}</span>`;
}
