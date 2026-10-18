import { $, esc } from "../util.js";
import { labHero } from "./common.js";

const IPV4_MAX = (1n << 32n) - 1n;
const IPV6_MAX = (1n << 128n) - 1n;
const commas = (n) => n.toLocaleString("en-US");

function parseV4(text) {
  const parts = text.split(".");
  if (parts.length !== 4 || parts.some((x) => !/^\d{1,3}$/.test(x) || +x > 255)) throw new Error("Enter four IPv4 octets from 0 to 255.");
  return parts.reduce((n, x) => (n << 8n) | BigInt(x), 0n);
}
function printV4(n) { return [24n, 16n, 8n, 0n].map((s) => Number((n >> s) & 255n)).join("."); }
function parseV6(text) {
  if (!text.includes(":")) throw new Error("Enter an IPv6 address such as 2001:db8:1::25.");
  if ((text.match(/::/g) || []).length > 1) throw new Error("An IPv6 address can use :: only once.");
  const [leftText, rightText] = text.split("::");
  const left = leftText ? leftText.split(":") : [];
  const right = text.includes("::") && rightText ? rightText.split(":") : [];
  const fill = 8 - left.length - right.length;
  const groups = text.includes("::") ? [...left, ...Array(fill).fill("0"), ...right] : text.split(":");
  if (groups.length !== 8 || groups.some((g) => !/^[0-9a-f]{1,4}$/i.test(g))) throw new Error("Enter a valid eight-group IPv6 address (zero groups may be compressed with ::).");
  return BigInt("0x" + groups.map((g) => g.padStart(4, "0")).join(""));
}
function printV6(n) {
  const groups = Array.from({ length: 8 }, (_, i) => ((n >> BigInt((7 - i) * 16)) & 65535n).toString(16));
  let bestStart = -1, bestLen = 1;
  for (let i = 0; i < 8;) {
    if (groups[i] !== "0") { i++; continue; }
    let j = i; while (j < 8 && groups[j] === "0") j++;
    if (j - i > bestLen) { bestStart = i; bestLen = j - i; }
    i = j;
  }
  if (bestStart < 0) return groups.join(":");
  const before = groups.slice(0, bestStart).join(":");
  const after = groups.slice(bestStart + bestLen).join(":");
  return `${before}::${after}`;
}
function calculate(value, family) {
  const [address, prefixText] = value.trim().split("/");
  const bits = family === "v4" ? 32 : 128;
  const prefix = Number(prefixText);
  if (!Number.isInteger(prefix) || prefix < 0 || prefix > bits) throw new Error(`Prefix must be between /0 and /${bits}.`);
  const ip = family === "v4" ? parseV4(address) : parseV6(address);
  const max = family === "v4" ? IPV4_MAX : IPV6_MAX;
  const hostBits = BigInt(bits - prefix);
  const size = 1n << hostBits;
  const network = (ip / size) * size;
  const last = network + size - 1n;
  const fmt = family === "v4" ? printV4 : printV6;
  const mask = max ^ (size - 1n);
  const usable = family === "v6" ? size : prefix >= 31 ? size : size - 2n;
  const first = family === "v6" || prefix >= 31 ? network : network + 1n;
  const end = family === "v6" || prefix >= 31 ? last : last - 1n;
  const base = 10n ** 18n;
  const sizeText = size > base ? size.toLocaleString("en-US") : commas(size);
  return { family, bits, prefix, ip: fmt(ip), network: fmt(network), last: fmt(last), mask: fmt(mask), first: fmt(first), end: fmt(end), total: sizeText, usable: usable.toLocaleString("en-US"), broadcast: family === "v4" ? fmt(last) : "No broadcast in IPv6" };
}

function render(view, mode = "playground") {
  view.innerHTML = `${mode === "lab" ? labHero("NET", "sky", "Packet Path Lab", "Trace an address through prefixes, routes and firewall boundaries. Try /24, /32 and IPv6 /64; see why the prefix length is not the number of addresses.") : `<section class="topic-hero clay"><div class="code tint-sky">CIDR</div><div><h1>CIDR Calculator</h1><div class="muted">Calculate the aligned network, address range, masks and subnet split. /24 means 24 network bits; /32 is one IPv4 address; /64 is a common IPv6 subnet.</div></div></section>`}
    <div class="grid two" style="margin-top:1rem">
      <section class="panel clay">
        <h3>Address &amp; prefix</h3>
        <div class="row"><select id="cidrFamily" aria-label="Address family"><option value="v4">IPv4 (32 bits)</option><option value="v6">IPv6 (128 bits)</option></select><input id="cidrInput" aria-label="IP address and prefix" value="192.168.10.77/24" style="flex:1;min-width:180px;font-family:var(--mono)"></div>
        <div class="row" style="margin-top:.7rem"><button class="btn small" data-cidr="10.20.3.14/24" data-family="v4">IPv4 /24</button><button class="btn small" data-cidr="10.20.3.14/32" data-family="v4">IPv4 /32</button><button class="btn small" data-cidr="2001:db8:1234:1::25/64" data-family="v6">IPv6 /64</button><button class="btn small" data-cidr="172.16.18.9/20" data-family="v4">IPv4 /20</button></div>
        <label style="display:block;margin-top:1rem">Split this subnet into child prefixes <input id="childPrefix" type="number" min="0" max="128" value="26" style="width:6rem"></label>
        <div class="muted" id="cidrError" role="status" style="margin-top:.6rem;min-height:1.4rem"></div>
      </section>
      <section class="panel clay" id="cidrResult" aria-live="polite"></section>
    </div>
    <section class="panel clay" style="margin-top:1rem"><h3>Network bits</h3><p class="muted" id="bitHint"></p><div id="bitMap" class="cidr-bitmap"></div></section>
    <section class="panel clay" style="margin-top:1rem"><h3>First child subnets</h3><div class="grid two" id="subnetList"></div></section>
    <section class="panel clay" style="margin-top:1rem"><h3>Quick mental math</h3><div class="grid three"><div><b>IPv4 /24</b><p class="muted">32 − 24 = 8 host bits → 2⁸ = 256 total addresses, usually 254 usable.</p></div><div><b>IPv4 /32</b><p class="muted">32 − 32 = 0 host bits → exactly one IPv4 address, often used for a host route.</p></div><div><b>IPv6 /64</b><p class="muted">128 − 64 = 64 interface bits → 2⁶⁴ addresses. The “64” counts network bits, not total addresses.</p></div></div></section>`;

  const family = $("#cidrFamily", view), input = $("#cidrInput", view), child = $("#childPrefix", view);
  function draw() {
    try {
      const net = calculate(input.value, family.value);
      $("#cidrError", view).textContent = "";
      const maxPrefix = net.bits;
      child.min = net.prefix;
      child.max = maxPrefix;
      if (+child.value < net.prefix || +child.value > maxPrefix) child.value = Math.min(maxPrefix, Math.max(net.prefix, net.family === "v4" ? 26 : 80));
      $("#cidrResult", view).innerHTML = `<h3>${net.family === "v4" ? "IPv4" : "IPv6"} ${esc(net.network)}/${net.prefix}</h3><div class="grid two"><div><span class="muted">Network address</span><br><b>${esc(net.network)}</b></div><div><span class="muted">Last address</span><br><b>${esc(net.last)}</b></div><div><span class="muted">Prefix mask</span><br><b>${esc(net.mask)}</b></div><div><span class="muted">Host bits</span><br><b>${net.bits - net.prefix}</b></div><div><span class="muted">Total addresses</span><br><b>${net.total}</b></div><div><span class="muted">Usable addresses</span><br><b>${net.usable}</b></div><div><span class="muted">First usable</span><br><b>${esc(net.first)}</b></div><div><span class="muted">Last usable</span><br><b>${esc(net.end)}</b></div><div><span class="muted">Broadcast</span><br><b>${esc(net.broadcast)}</b></div></div>`;
      $("#bitHint", view).textContent = `${net.prefix} network bits + ${net.bits - net.prefix} host bits = ${net.bits} total bits. The prefix counts network bits.`;
      $("#bitMap", view).innerHTML = Array.from({ length: net.bits }, (_, i) => `<i class="${i < net.prefix ? "network-bit" : "host-bit"}" title="bit ${i + 1}: ${i < net.prefix ? "network" : "host"}"></i>${net.family === "v4" && (i + 1) % 8 === 0 && i < 31 ? `<span class="bit-dot">.</span>` : ""}`).join("");
      const split = Number(child.value);
      const count = 1n << BigInt(split - net.prefix);
      const step = 1n << BigInt(net.bits - split);
      const start = net.family === "v4" ? parseV4(net.network) : parseV6(net.network);
      const fmt = net.family === "v4" ? printV4 : printV6;
      const shown = Number(count > 8n ? 8n : count);
      $("#subnetList", view).innerHTML = `<p class="muted" style="grid-column:1/-1">${count.toLocaleString("en-US")} child subnet${count === 1n ? "" : "s"} of /${split}; showing the first ${shown}.</p>${Array.from({ length: shown }, (_, i) => `<div class="pill neutral">${esc(fmt(start + BigInt(i) * step))}/${split}</div>`).join("")}`;
    } catch (err) {
      $("#cidrError", view).textContent = err.message;
      $("#cidrResult", view).innerHTML = `<p class="muted">Enter a valid IP/prefix to calculate the range.</p>`;
      $("#bitMap", view).innerHTML = "";
      $("#subnetList", view).innerHTML = "";
    }
  }
  view.addEventListener("input", draw);
  view.addEventListener("click", (event) => {
    if (event.target.matches("[data-cidr]")) {
      family.value = event.target.dataset.family;
      input.value = event.target.dataset.cidr;
      const pref = +input.value.split("/")[1];
      child.value = family.value === "v4" ? Math.min(32, Math.max(pref, 26)) : Math.min(128, Math.max(pref, 80));
    }
    draw();
  });
  view.addEventListener("change", draw);
  draw();
}

export function lab(view) { render(view, "lab"); }
export function playground(view) { render(view, "playground"); }
