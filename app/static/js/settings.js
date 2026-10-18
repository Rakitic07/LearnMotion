import { store } from "./util.js";

// The server copy is the source of truth for signed-in users; this local copy lets players read it synchronously.
const KEY = "settings";
export const SPEED_MIN = 0.1;
export const SPEED_MAX = 2;
export const SPEED_PRESETS = [0.25, 0.5, 0.75, 1, 1.5, 2];

export const clampSpeed = (v) => {
  const n = Number(v);
  if (!Number.isFinite(n)) return 1;
  return Math.round(Math.min(SPEED_MAX, Math.max(SPEED_MIN, n)) * 100) / 100;
};

export const formatSpeed = (v) => `${Number(v.toFixed(2))}×`;

export const animSpeed = () => clampSpeed(store.get(KEY, {}).animSpeed ?? 1);

export function setLocalSettings(settings) {
  store.set(KEY, { animSpeed: clampSpeed(settings?.animSpeed ?? 1) });
  window.dispatchEvent(new CustomEvent("lm:settings"));
}

export function clearLocalSettings() {
  store.remove(KEY);
  window.dispatchEvent(new CustomEvent("lm:settings"));
}

/** Keeps a player's speed select in sync with the global setting; returns a cleanup function. */
export function bindSpeed(player, select, onChange) {
  const show = (speed) => {
    const value = String(speed);
    if (![...select.options].some((o) => o.value === value)) {
      const opt = new Option(formatSpeed(speed), value);
      opt.dataset.custom = "1";
      const after = [...select.options].find((o) => +o.value > speed);
      select.insertBefore(opt, after || null);
    }
    select.value = value;
  };
  const apply = () => {
    player.speed = animSpeed();
    show(player.speed);
    onChange();
  };
  show(player.speed);
  window.addEventListener("lm:settings", apply);
  return () => window.removeEventListener("lm:settings", apply);
}
