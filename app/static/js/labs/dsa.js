import { $, $$, esc, highlightCode } from "../util.js";
import { pyResultHtml, runPython } from "../runners.js";
import { codeEditor, labHero, sampleOptions, takeHandoff } from "./common.js";

// ===================================================================== sorting algorithms
// Each sort is a generator over an array it mutates in place. It yields events:
//   cmp {i, j} · swap {i, j} · write {i} · read {i}   one primitive operation each (one animation tick)
//   pivot {i} · range {lo, hi} · done {idx[]} · mark  markers that only update the picture
// Every event may carry `line` (index into the pseudo-code) and `note`.

const ID = (x) => x;
const OPS = new Set(["cmp", "swap", "write", "read"]);
const swap = (a, i, j) => {
  const t = a[i];
  a[i] = a[j];
  a[j] = t;
};
const span = (lo, hi) => Array.from({ length: Math.max(0, hi - lo + 1) }, (_, k) => lo + k);

function* bubble(a, key = ID) {
  const n = a.length;
  for (let end = n - 1; end > 0; end--) {
    let swapped = false;
    for (let i = 0; i < end; i++) {
      yield { t: "cmp", i, j: i + 1, line: 3 };
      if (key(a[i]) > key(a[i + 1])) {
        swap(a, i, i + 1);
        swapped = true;
        yield { t: "swap", i, j: i + 1, line: 4 };
      }
    }
    if (!swapped) {
      yield { t: "done", idx: span(0, end), line: 5 };
      return;
    }
    yield { t: "done", idx: [end], line: 0 };
  }
  if (n) yield { t: "done", idx: [0], line: 0 };
}

function* selection(a, key = ID) {
  const n = a.length;
  for (let i = 0; i < n - 1; i++) {
    let m = i;
    yield { t: "pivot", i: m, line: 1 };
    for (let j = i + 1; j < n; j++) {
      yield { t: "cmp", i: j, j: m, line: 3 };
      if (key(a[j]) < key(a[m])) {
        m = j;
        yield { t: "pivot", i: m, line: 3 };
      }
    }
    if (m !== i) {
      swap(a, i, m);
      yield { t: "swap", i, j: m, line: 4 };
    }
    yield { t: "done", idx: [i], line: 4 };
  }
  if (n) yield { t: "done", idx: [n - 1], line: 0 };
}

function* insertion(a, key = ID) {
  for (let i = 1; i < a.length; i++) {
    const v = a[i];
    let j = i - 1;
    yield { t: "pivot", i, line: 1 };
    while (j >= 0) {
      yield { t: "cmp", i: j, j: j + 1, line: 2 };
      if (!(key(a[j]) > key(v))) break;
      a[j + 1] = a[j];
      yield { t: "write", i: j + 1, line: 3 };
      j--;
    }
    if (j + 1 !== i) {
      a[j + 1] = v;
      yield { t: "write", i: j + 1, line: 4 };
    }
  }
}

function* merge(a, key = ID) {
  const aux = a.slice();
  function* sort(lo, hi) {
    if (hi <= lo) return;
    yield { t: "range", lo, hi, line: 2 };
    const mid = (lo + hi) >> 1;
    yield* sort(lo, mid);
    yield* sort(mid + 1, hi);
    for (let k = lo; k <= hi; k++) aux[k] = a[k];
    yield { t: "range", lo, hi, line: 3 };
    let i = lo;
    let j = mid + 1;
    let k = lo;
    while (i <= mid && j <= hi) {
      yield { t: "cmp", i, j, line: 4 };
      a[k] = key(aux[j]) < key(aux[i]) ? aux[j++] : aux[i++];
      yield { t: "write", i: k++, line: 5 };
    }
    while (i <= mid) {
      a[k] = aux[i++];
      yield { t: "write", i: k++, line: 6 };
    }
  }
  yield* sort(0, a.length - 1);
}

function* quickLomuto(a, key = ID) {
  const stack = [[0, a.length - 1]];
  while (stack.length) {
    const [lo, hi] = stack.pop();
    if (lo > hi) continue;
    yield { t: "range", lo, hi, line: 0 };
    if (lo === hi) {
      yield { t: "done", idx: [lo], line: 1 };
      continue;
    }
    const p = key(a[hi]);
    yield { t: "pivot", i: hi, line: 2 };
    let i = lo;
    for (let j = lo; j < hi; j++) {
      yield { t: "cmp", i: j, j: hi, line: 4 };
      if (key(a[j]) < p) {
        if (i !== j) {
          swap(a, i, j);
          yield { t: "swap", i, j, line: 4 };
        }
        i++;
      }
    }
    if (i !== hi) {
      swap(a, i, hi);
      yield { t: "swap", i, j: hi, line: 5 };
    }
    yield { t: "done", idx: [i], line: 5 };
    stack.push([i + 1, hi], [lo, i - 1]);
  }
}

function* quickHoare(a, key = ID) {
  const stack = [[0, a.length - 1]];
  while (stack.length) {
    const [lo, hi] = stack.pop();
    if (lo > hi) continue;
    yield { t: "range", lo, hi, line: 0 };
    if (lo === hi) {
      yield { t: "done", idx: [lo], line: 1 };
      continue;
    }
    let pi = (lo + hi) >> 1;
    const p = key(a[pi]);
    yield { t: "pivot", i: pi, line: 2 };
    let i = lo - 1;
    let j = hi + 1;
    for (;;) {
      do {
        i++;
        yield { t: "cmp", i, j: pi, line: 3 };
      } while (key(a[i]) < p);
      do {
        j--;
        yield { t: "cmp", i: j, j: pi, line: 4 };
      } while (key(a[j]) > p);
      if (i >= j) break;
      swap(a, i, j);
      yield { t: "swap", i, j, line: 6 };
      if (pi === i || pi === j) {
        pi = pi === i ? j : i;
        yield { t: "pivot", i: pi, line: 6 };
      }
    }
    yield { t: "mark", line: 7, note: `split at ${j}` };
    stack.push([j + 1, hi], [lo, j]);
  }
}

function* heap(a, key = ID) {
  const n = a.length;
  function* sift(i, size) {
    for (;;) {
      let c = 2 * i + 1;
      if (c >= size) return;
      if (c + 1 < size) {
        yield { t: "cmp", i: c, j: c + 1, line: 4 };
        if (key(a[c + 1]) > key(a[c])) c++;
      }
      yield { t: "cmp", i: c, j: i, line: 5 };
      if (!(key(a[c]) > key(a[i]))) return;
      swap(a, i, c);
      yield { t: "swap", i, j: c, line: 5 };
      i = c;
    }
  }
  for (let i = (n >> 1) - 1; i >= 0; i--) {
    yield { t: "pivot", i, line: 0 };
    yield* sift(i, n);
  }
  for (let end = n - 1; end > 0; end--) {
    swap(a, 0, end);
    yield { t: "swap", i: 0, j: end, line: 2 };
    yield { t: "done", idx: [end], line: 2 };
    yield { t: "range", lo: 0, hi: end - 1, line: 3 };
    yield* sift(0, end);
  }
  if (n) yield { t: "done", idx: [0], line: 1 };
}

function* shell(a, key = ID) {
  const n = a.length;
  let gap = 1;
  while (gap < Math.floor(n / 3)) gap = 3 * gap + 1;
  while (gap >= 1) {
    yield { t: "mark", line: 1, note: `gap = ${gap}` };
    for (let i = gap; i < n; i++) {
      const v = a[i];
      let j = i;
      yield { t: "pivot", i, line: 3 };
      while (j >= gap) {
        yield { t: "cmp", i: j - gap, j, line: 4 };
        if (!(key(a[j - gap]) > key(v))) break;
        a[j] = a[j - gap];
        yield { t: "write", i: j, line: 5 };
        j -= gap;
      }
      if (j !== i) {
        a[j] = v;
        yield { t: "write", i: j, line: 6 };
      }
    }
    gap = (gap - 1) / 3;
  }
}

const keyRange = (a, key) => {
  let lo = Infinity;
  let hi = -Infinity;
  for (const x of a) {
    const k = key(x);
    if (k < lo) lo = k;
    if (k > hi) hi = k;
  }
  return [lo, hi];
};

function* counting(a, key = ID) {
  const n = a.length;
  if (!n) return;
  const [lo, hi] = keyRange(a, key);
  const cnt = new Array(hi - lo + 1).fill(0);
  yield { t: "mark", line: 0, note: `${cnt.length} buckets for values ${lo}..${hi}` };
  for (let i = 0; i < n; i++) {
    cnt[key(a[i]) - lo]++;
    yield { t: "read", i, line: 1 };
  }
  for (let k = 1; k < cnt.length; k++) cnt[k] += cnt[k - 1];
  yield { t: "mark", line: 2 };
  const out = new Array(n);
  for (let i = n - 1; i >= 0; i--) {
    out[--cnt[key(a[i]) - lo]] = a[i];
    yield { t: "read", i, line: 3 };
  }
  for (let i = 0; i < n; i++) {
    a[i] = out[i];
    yield { t: "write", i, line: 4 };
  }
}

function* radix(a, key = ID) {
  const n = a.length;
  if (!n) return;
  const [lo, hi] = keyRange(a, key);
  const digit = (x, exp) => Math.floor((key(x) - lo) / exp) % 10;
  for (let exp = 1; exp === 1 || Math.floor((hi - lo) / exp) > 0; exp *= 10) {
    yield { t: "mark", line: 0, note: `sorting by the ${exp}s digit` };
    const cnt = new Array(10).fill(0);
    for (let i = 0; i < n; i++) {
      cnt[digit(a[i], exp)]++;
      yield { t: "read", i, line: 1 };
    }
    for (let d = 1; d < 10; d++) cnt[d] += cnt[d - 1];
    yield { t: "mark", line: 2 };
    const out = new Array(n);
    for (let i = n - 1; i >= 0; i--) {
      out[--cnt[digit(a[i], exp)]] = a[i];
      yield { t: "read", i, line: 3 };
    }
    for (let i = 0; i < n; i++) {
      a[i] = out[i];
      yield { t: "write", i, line: 4 };
    }
  }
}

export const SORTS = {
  bubble: {
    name: "Bubble sort",
    gen: bubble,
    code: [
      "for end = n-1 down to 1:",
      "  swapped = false",
      "  for i = 0 to end-1:",
      "    if a[i] > a[i+1]:",
      "      swap(a[i], a[i+1]); swapped = true",
      "  if not swapped: break      # already sorted",
    ],
    facts: { best: "O(n)", avg: "O(n²)", worst: "O(n²)", space: "O(1)", stable: true, inPlace: true, note: "Each pass bubbles the largest remaining value to the end. The early exit makes already-sorted input linear." },
  },
  selection: {
    name: "Selection sort",
    gen: selection,
    code: [
      "for i = 0 to n-2:",
      "  min = i",
      "  for j = i+1 to n-1:",
      "    if a[j] < a[min]: min = j",
      "  swap(a[i], a[min])",
    ],
    facts: { best: "O(n²)", avg: "O(n²)", worst: "O(n²)", space: "O(1)", stable: false, inPlace: true, note: "Always n(n-1)/2 comparisons, but at most n-1 swaps, which helps when writes are expensive. The long-distance swap breaks stability." },
  },
  insertion: {
    name: "Insertion sort",
    gen: insertion,
    code: [
      "for i = 1 to n-1:",
      "  key = a[i]; j = i - 1",
      "  while j >= 0 and a[j] > key:",
      "    a[j+1] = a[j]; j = j - 1     # shift right",
      "  a[j+1] = key",
    ],
    facts: { best: "O(n)", avg: "O(n²)", worst: "O(n²)", space: "O(1)", stable: true, inPlace: true, note: "Great on tiny or nearly sorted arrays, which is why Timsort and introsort use it for short runs." },
  },
  merge: {
    name: "Merge sort",
    gen: merge,
    code: [
      "mergeSort(lo, hi):",
      "  if hi - lo < 1: return",
      "  mid = (lo + hi) / 2; mergeSort(lo, mid); mergeSort(mid+1, hi)",
      "  copy a[lo..hi] into aux",
      "  while both halves have items:",
      "    a[k++] = smaller head (left wins ties)",
      "  copy left leftovers (right ones are already in place)",
    ],
    facts: { best: "O(n log n)", avg: "O(n log n)", worst: "O(n log n)", space: "O(n)", stable: true, inPlace: false, note: "Predictable n log n on every input. Taking from the left half on ties is what keeps it stable." },
  },
  quick: {
    name: "Quick sort (Lomuto)",
    gen: quickLomuto,
    code: [
      "quickSort(lo, hi):",
      "  if lo >= hi: return",
      "  pivot = a[hi]; i = lo",
      "  for j = lo to hi-1:",
      "    if a[j] < pivot: swap(a[i], a[j]); i++",
      "  swap(a[i], a[hi])          # pivot lands at its final index",
      "  quickSort(lo, i-1); quickSort(i+1, hi)",
    ],
    facts: { best: "O(n log n)", avg: "O(n log n)", worst: "O(n²)", space: "O(log n) avg, O(n) worst", stable: false, inPlace: true, note: "Lomuto partition: last element as pivot, one forward scan. Easy to write, but sorted, reversed and all-equal inputs degrade to n². Try 'reversed' and watch the comparison counter." },
  },
  quickh: {
    name: "Quick sort (Hoare)",
    gen: quickHoare,
    code: [
      "quickSort(lo, hi):",
      "  if lo >= hi: return",
      "  pivot = a[(lo+hi)/2]; i = lo-1; j = hi+1",
      "  loop: do i++ while a[i] < pivot",
      "        do j-- while a[j] > pivot",
      "        if i >= j: break      # p = j",
      "        swap(a[i], a[j])",
      "  quickSort(lo, p); quickSort(p+1, hi)",
    ],
    facts: { best: "O(n log n)", avg: "O(n log n)", worst: "O(n²)", space: "O(log n) avg, O(n) worst", stable: false, inPlace: true, note: "Hoare partition: middle pivot, two pointers walking inward. Roughly 3x fewer swaps than Lomuto and fine on sorted input and duplicates. The pivot does not necessarily end at its final index." },
  },
  heap: {
    name: "Heap sort",
    gen: heap,
    code: [
      "for i = n/2-1 down to 0: siftDown(i, n)    # build max-heap",
      "for end = n-1 down to 1:",
      "  swap(a[0], a[end])          # max goes to the back",
      "  siftDown(0, end)",
      "siftDown(i, size): child = larger of 2i+1, 2i+2",
      "  if a[child] > a[i]: swap; i = child; repeat",
    ],
    facts: { best: "O(n log n)", avg: "O(n log n)", worst: "O(n log n)", space: "O(1)", stable: false, inPlace: true, note: "Guaranteed n log n with constant extra memory, but jumps around the array, so it is cache-unfriendly and usually slower than quicksort in practice." },
  },
  shell: {
    name: "Shell sort",
    gen: shell,
    code: [
      "gap = largest of 1, 4, 13, 40, ... below n/3",
      "while gap >= 1:",
      "  for i = gap to n-1:          # gapped insertion sort",
      "    tmp = a[i]; j = i",
      "    while j >= gap and a[j-gap] > tmp:",
      "      a[j] = a[j-gap]; j -= gap",
      "    a[j] = tmp",
      "  gap = (gap - 1) / 3",
    ],
    facts: { best: "O(n log n)", avg: "about O(n^1.25)", worst: "O(n^1.5)", space: "O(1)", stable: false, inPlace: true, note: "Insertion sort over shrinking gaps (Knuth sequence). Far-apart moves early fix big disorder cheaply; the final gap-1 pass is a plain insertion sort on nearly sorted data." },
  },
  counting: {
    name: "Counting sort",
    gen: counting,
    code: [
      "lo, hi = min(a), max(a); count = [0] * (hi - lo + 1)",
      "for v in a: count[v - lo] += 1          # no comparisons",
      "prefix sums: count[k] += count[k-1]",
      "for i = n-1 down to 0: out[--count[a[i]-lo]] = a[i]",
      "copy out back into a",
    ],
    facts: { best: "O(n + k)", avg: "O(n + k)", worst: "O(n + k)", space: "O(n + k)", stable: true, inPlace: false, note: "k is the value range. Zero comparisons: it beats the n log n comparison bound when k is small (ages, grades) and wastes memory when k is huge. Walking backwards keeps it stable." },
  },
  radix: {
    name: "Radix sort (LSD)",
    gen: radix,
    code: [
      "for exp = 1, 10, 100, ... while (max - min) / exp > 0:",
      "  count digits d = (a[i] / exp) % 10",
      "  prefix sums over the 10 buckets",
      "  for i = n-1 down to 0: out[--count[d]] = a[i]",
      "  copy out back into a",
    ],
    facts: { best: "O(d(n + b))", avg: "O(d(n + b))", worst: "O(d(n + b))", space: "O(n + b)", stable: true, inPlace: false, note: "d digits in base b = 10. Runs a stable counting sort per digit, least significant first; each pass must be stable or the earlier digit order is lost." },
  },
};

const newStats = () => ({ steps: 0, comparisons: 0, swaps: 0, writes: 0, reads: 0 });
function tally(s, ev) {
  if (ev.t === "cmp") s.comparisons++;
  else if (ev.t === "swap") s.swaps++;
  else if (ev.t === "write") s.writes++;
  else if (ev.t === "read") s.reads++;
  if (OPS.has(ev.t)) s.steps++;
}

/** Runs a sort to completion on a copy. `key` maps items to numbers (counting/radix need integers). */
export function run(name, input, key = ID) {
  const array = input.slice();
  const stats = newStats();
  for (const ev of SORTS[name].gen(array, key)) tally(stats, ev);
  return { array, ...stats };
}

export const SHAPES = { random: "Random", nearly: "Nearly sorted", reversed: "Reversed", few: "Few unique" };

export function makeInput(n, shape = "random", rnd = Math.random) {
  const ri = (k) => Math.floor(rnd() * k);
  const asc = Array.from({ length: n }, (_, i) => i + 1);
  if (shape === "reversed") return asc.reverse();
  if (shape === "nearly") {
    for (let s = Math.max(1, Math.round(n / 12)); s > 0; s--) {
      const i = ri(n - 1);
      swap(asc, i, i + 1);
    }
    return asc;
  }
  if (shape === "few") {
    const vals = [0.25, 0.5, 0.75, 1].map((f) => Math.max(1, Math.round(n * f)));
    return Array.from({ length: n }, () => vals[ri(4)]);
  }
  for (let i = n - 1; i > 0; i--) swap(asc, i, ri(i + 1));
  return asc;
}

// ===================================================================== visualizer
const SPEEDS = [1, 2, 4, 8, 15, 30, 60, 120, 250, 600];
const STAT_LABELS = { steps: "steps", comparisons: "comparisons", swaps: "swaps", writes: "writes" };
const LEGEND = [["cmp", "compared"], ["swap", "swapped"], ["write", "written"], ["read", "read"], ["pivot", "pivot / min / key"], ["sorted", "in final place"]];
const yesNo = (b) => `<span class="pill ${b ? "ok" : "bad"}">${b ? "yes" : "no"}</span>`;

function makeLane(id, input) {
  const arr = input.slice();
  return { id, arr, gen: SORTS[id].gen(arr), stats: newStats(), hi: null, pivot: -1, range: null, sorted: new Set(), line: -1, note: "", done: false, rank: 0 };
}

/** Consumes events up to and including the next primitive operation. Returns false once the sort is finished. */
function advance(lane) {
  lane.hi = null;
  for (;;) {
    const r = lane.gen.next();
    if (r.done) {
      lane.done = true;
      lane.range = null;
      lane.pivot = -1;
      lane.arr.forEach((_, i) => lane.sorted.add(i));
      return false;
    }
    const ev = r.value;
    tally(lane.stats, ev);
    if (ev.line !== undefined) lane.line = ev.line;
    if (ev.note) lane.note = ev.note;
    if (ev.t === "done") ev.idx.forEach((i) => lane.sorted.add(i));
    else if (ev.t === "range") {
      lane.range = [ev.lo, ev.hi];
      lane.pivot = -1;
    } else if (ev.t === "pivot") lane.pivot = ev.i;
    else if (OPS.has(ev.t)) {
      lane.hi = { t: ev.t, idx: ev.j === undefined ? [ev.i] : [ev.i, ev.j] };
      return true;
    }
  }
}

export function lab(view) {
  const reduce = typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ids = Object.keys(SORTS);
  const st = { algo: "quick", n: 32, shape: "random", speed: 6, race: false, picks: ["insertion", "merge", "quick", "heap"], input: [], lanes: [], tick: 0 };
  let raf = 0;
  let playing = false;
  let lastT = 0;
  let acc = 0;

  view.innerHTML = `
    ${labHero("SORT", "sky", "Sorting Visualizer", "Watch ten sorting algorithms work step by step. Every tick is one primitive operation (a comparison, swap, write or read), so the counters are an honest cost model. Turn on <b>Race mode</b> to run several algorithms on the same input side by side.")}
    <div class="panel clay dsa-panel" style="margin-top:1.2rem">
      <div class="dsa-controls">
        <label class="dsa-field" id="dsaAlgoField">Algorithm<select id="dsaAlgo">${ids.map((id) => `<option value="${id}">${esc(SORTS[id].name)}</option>`).join("")}</select></label>
        <label class="dsa-field">Input shape<select id="dsaShape">${Object.entries(SHAPES).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join("")}</select></label>
        <label class="dsa-field"><span>Array size <b id="dsaNLbl"></b></span><input type="range" id="dsaN" min="8" max="80" step="1"></label>
        <label class="dsa-field"><span>Speed <b id="dsaSpeedLbl"></b></span><input type="range" id="dsaSpeed" min="1" max="10" step="1"></label>
      </div>
      <div class="filters">
        <button class="btn small primary" id="dsaPlay">Play</button>
        <button class="btn small" id="dsaStep" title="Right arrow">Step</button>
        <button class="btn small" id="dsaReset">Reset</button>
        <button class="btn small" id="dsaShuffle">New array</button>
        <label class="dsa-switch"><input type="checkbox" id="dsaRace"> Race mode</label>
      </div>
      <div id="dsaPicks" class="dsa-picks" hidden>
        <span class="muted">Pick 2 to 4 racers:</span>
        ${ids.map((id) => `<label class="dsa-pick"><input type="checkbox" value="${id}"> ${esc(SORTS[id].name)}</label>`).join("")}
      </div>
      <div class="dsa-legend">${LEGEND.map(([k, v]) => `<span><i class="dsa-sw is-${k}"></i>${esc(v)}</span>`).join("")}</div>
      ${reduce ? `<p class="muted dsa-note">Reduced motion is on: Play jumps straight to the result; use Step to walk through it.</p>` : ""}
    </div>
    <div id="dsaLanes" class="dsa-lanes"></div>
    <div class="lab-grid halves dsa-info" id="dsaInfo">
      <div class="panel clay" id="dsaCodePanel"><h3>Pseudo-code</h3><div id="dsaCode" class="dsa-code"></div><p class="muted dsa-note" id="dsaNote"></p></div>
      <div class="panel clay"><h3 id="dsaFactsTitle">Facts</h3><div id="dsaFacts"></div></div>
    </div>`;

  $("#dsaAlgo").value = st.algo;
  $("#dsaShape").value = st.shape;
  $("#dsaN").value = st.n;
  $("#dsaSpeed").value = st.speed;
  $$("#dsaPicks input").forEach((c) => (c.checked = st.picks.includes(c.value)));

  const labels = () => {
    $("#dsaNLbl").textContent = st.n;
    $("#dsaSpeedLbl").textContent = `${SPEEDS[st.speed - 1]} ops/s`;
  };

  const facts = () => {
    const list = st.race ? st.picks : [st.algo];
    $("#dsaFactsTitle").textContent = st.race ? "Racers compared" : `Facts: ${SORTS[st.algo].name}`;
    const rows = list.map((id) => {
      const f = SORTS[id].facts;
      return `<tr><th>${esc(SORTS[id].name)}</th><td>${esc(f.best)}</td><td>${esc(f.avg)}</td><td>${esc(f.worst)}</td><td>${esc(f.space)}</td><td>${yesNo(f.stable)}</td><td>${yesNo(f.inPlace)}</td></tr>`;
    }).join("");
    const head = `<tr><th>Algorithm</th><th>Best</th><th>Average</th><th>Worst</th><th>Space</th><th>Stable</th><th>In-place</th></tr>`;
    if (st.race) {
      $("#dsaFacts").innerHTML = `<div class="dsa-table-wrap"><table class="dsa-table"><thead>${head}</thead><tbody>${rows}</tbody></table></div>`;
      return;
    }
    const f = SORTS[st.algo].facts;
    $("#dsaFacts").innerHTML = `
      <div class="dsa-facts">
        <div><span>Best</span><b>${esc(f.best)}</b></div><div><span>Average</span><b>${esc(f.avg)}</b></div>
        <div><span>Worst</span><b>${esc(f.worst)}</b></div><div><span>Extra space</span><b>${esc(f.space)}</b></div>
        <div><span>Stable</span>${yesNo(f.stable)}</div><div><span>In-place</span>${yesNo(f.inPlace)}</div>
      </div>
      <p class="muted dsa-note">${esc(f.note)}</p>`;
  };

  const build = () => {
    stop();
    st.tick = 0;
    const list = st.race ? st.picks : [st.algo];
    st.lanes = list.map((id) => makeLane(id, st.input));
    const max = Math.max(1, ...st.input);
    st.max = max;
    $("#dsaLanes").className = `dsa-lanes${st.race ? " is-race" : ""}`;
    $("#dsaLanes").innerHTML = st.lanes.map((l, k) => `
      <div class="panel clay dsa-lane" data-lane="${k}">
        <div class="dsa-lane-head"><b>${esc(SORTS[l.id].name)}</b><span class="dsa-badge"></span></div>
        <div class="dsa-stats">${Object.entries(STAT_LABELS).map(([s, lbl]) => `<span class="dsa-stat">${lbl} <b data-s="${s}">0</b></span>`).join("")}</div>
        <div class="dsa-bars${st.input.length > 40 ? " dense" : ""}" role="img" aria-label="${esc(SORTS[l.id].name)} bars">${st.input.map(() => `<i class="dsa-bar"></i>`).join("")}</div>
        <div class="dsa-line"></div>
      </div>`).join("");
    st.lanes.forEach((l, k) => {
      const el = $(`[data-lane="${k}"]`, view);
      l.el = el;
      l.bars = $$(".dsa-bar", el);
    });
    $("#dsaInfo").classList.toggle("is-race", st.race);
    $("#dsaCodePanel").hidden = st.race;
    $("#dsaAlgoField").hidden = st.race;
    $("#dsaPicks").hidden = !st.race;
    facts();
    paint();
  };

  const fresh = () => {
    st.input = makeInput(st.n, st.shape);
    build();
  };

  const paintLane = (l) => {
    const hi = new Map();
    if (l.hi) l.hi.idx.forEach((i) => hi.set(i, l.hi.t));
    l.bars.forEach((b, i) => {
      b.style.height = `${(l.arr[i] / st.max) * 100}%`;
      let cls = "dsa-bar";
      if (l.sorted.has(i)) cls += " is-sorted";
      if (l.range && (i < l.range[0] || i > l.range[1])) cls += " is-out";
      if (i === l.pivot) cls += " is-pivot";
      if (hi.has(i)) cls += ` is-${hi.get(i)}`;
      b.className = cls;
    });
    $$("[data-s]", l.el).forEach((s) => (s.textContent = l.stats[s.dataset.s]));
    const badge = $(".dsa-badge", l.el);
    badge.className = `dsa-badge${l.done ? " pill ok" : ""}`;
    badge.textContent = l.done ? (st.race ? `#${l.rank} · ${l.stats.steps} ops` : "sorted") : "";
    const line = SORTS[l.id].code[l.line];
    $(".dsa-line", l.el).textContent = st.race ? (l.done ? "done" : line ? line.trim() : "") : l.note;
  };

  const paint = () => {
    st.lanes.forEach(paintLane);
    if (st.race) return;
    const l = st.lanes[0];
    $("#dsaCode").innerHTML = SORTS[l.id].code.map((c, i) => `<div class="${i === l.line && !l.done ? "cur" : ""}">${esc(c)}</div>`).join("");
    $("#dsaNote").textContent = l.done ? `Finished: ${l.stats.comparisons} comparisons, ${l.stats.swaps} swaps, ${l.stats.writes} writes, ${l.stats.reads} reads.` : l.note;
  };

  const allDone = () => st.lanes.every((l) => l.done);

  /** One tick: each unfinished lane performs exactly one primitive operation. */
  const tick = () => {
    st.tick++;
    const rank = st.lanes.filter((l) => l.done).length + 1;
    for (const l of st.lanes) {
      if (l.done) continue;
      advance(l);
      if (l.done) l.rank = rank;
    }
    return !allDone();
  };

  const stop = () => {
    playing = false;
    cancelAnimationFrame(raf);
    raf = 0;
    $("#dsaPlay").textContent = "Play";
  };

  const loop = (t) => {
    if (!playing) return;
    const dt = lastT ? Math.min(t - lastT, 250) : 16;
    lastT = t;
    acc += (dt * SPEEDS[st.speed - 1]) / 1000;
    let n = Math.floor(acc);
    acc -= n;
    while (n-- > 0 && tick());
    paint();
    if (allDone()) stop();
    else raf = requestAnimationFrame(loop);
  };

  const play = () => {
    if (playing) return stop();
    if (allDone()) build();
    if (reduce) {
      while (tick());
      paint();
      return;
    }
    playing = true;
    lastT = 0;
    acc = 1;
    $("#dsaPlay").textContent = "Pause";
    raf = requestAnimationFrame(loop);
  };

  $("#dsaPlay").onclick = play;
  $("#dsaStep").onclick = () => {
    stop();
    if (allDone()) build();
    tick();
    paint();
  };
  $("#dsaReset").onclick = build;
  $("#dsaShuffle").onclick = fresh;
  $("#dsaAlgo").onchange = (e) => {
    st.algo = e.target.value;
    build();
  };
  $("#dsaShape").onchange = (e) => {
    st.shape = e.target.value;
    fresh();
  };
  $("#dsaN").oninput = (e) => {
    st.n = +e.target.value;
    labels();
    fresh();
  };
  $("#dsaSpeed").oninput = (e) => {
    st.speed = +e.target.value;
    labels();
  };
  $("#dsaRace").onchange = (e) => {
    st.race = e.target.checked;
    build();
  };
  $("#dsaPicks").onchange = (e) => {
    const picked = $$("#dsaPicks input:checked").map((c) => c.value);
    if (picked.length < 2 || picked.length > 4) {
      e.target.checked = !e.target.checked;
      return;
    }
    st.picks = picked;
    build();
  };
  const keys = (e) => {
    if (e.target.matches("textarea, input, select") || e.key !== "ArrowRight") return;
    e.preventDefault();
    $("#dsaStep").click();
  };
  document.addEventListener("keydown", keys);

  labels();
  fresh();
  return () => {
    playing = false;
    cancelAnimationFrame(raf);
    document.removeEventListener("keydown", keys);
  };
}

// ===================================================================== big-O growth
export const GROWTH = [
  { id: "c", label: "O(1)", f: () => 1 },
  { id: "log", label: "O(log n)", f: (n) => Math.log2(n) },
  { id: "n", label: "O(n)", f: (n) => n },
  { id: "nlog", label: "O(n log n)", f: (n) => n * Math.log2(n) },
  { id: "n2", label: "O(n²)", f: (n) => n * n },
  { id: "exp", label: "O(2^n)", f: (n) => 2 ** n },
];

export const QUIZ = [
  { code: "def first(xs):\n    return xs[0]", answer: "c", why: "One index operation no matter how long the list is." },
  { code: "def total(xs):\n    s = 0\n    for x in xs:\n        s += x\n    return s", answer: "n", why: "One pass, constant work per element." },
  { code: "def has_dup(xs):\n    for i in range(len(xs)):\n        for j in range(i + 1, len(xs)):\n            if xs[i] == xs[j]:\n                return True\n    return False", answer: "n2", why: "Every pair is checked: n(n-1)/2 comparisons." },
  { code: "def find(xs, t):\n    lo, hi = 0, len(xs) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if xs[mid] == t: return mid\n        if xs[mid] < t: lo = mid + 1\n        else: hi = mid - 1\n    return -1", answer: "log", why: "Binary search halves the range every iteration." },
  { code: "def fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)", answer: "exp", why: "Each call branches into two; the call tree has about 2^n nodes (precisely about 1.618^n)." },
  { code: "def ranked(xs):\n    return sorted(xs)", answer: "nlog", why: "Timsort, like every comparison sort, needs n log n comparisons in the worst case." },
  { code: "def bits(n):\n    count = 0\n    while n > 0:\n        n //= 2\n        count += 1\n    return count", answer: "log", why: "n halves each iteration, so the loop runs about log2(n) times." },
  { code: "def subsets(xs):\n    if not xs:\n        return [[]]\n    rest = subsets(xs[1:])\n    return rest + [[xs[0]] + s for s in rest]", answer: "exp", why: "There are 2^n subsets and each is built once." },
  { code: "def price(catalog, sku):\n    return catalog[sku]    # catalog is a dict", answer: "c", why: "Hash table lookup is O(1) on average." },
  { code: "def pair_sum(xs, t):   # xs is sorted\n    i, j = 0, len(xs) - 1\n    while i < j:\n        s = xs[i] + xs[j]\n        if s == t: return i, j\n        if s < t: i += 1\n        else: j -= 1", answer: "n", why: "Two pointers move toward each other; together they take at most n steps." },
  { code: "def msort(xs):\n    if len(xs) <= 1:\n        return xs\n    m = len(xs) // 2\n    return merge(msort(xs[:m]), msort(xs[m:]))", answer: "nlog", why: "log n levels of splitting, O(n) merge work per level." },
  { code: "def table(n):\n    for i in range(n):\n        for j in range(n):\n            print(i * j, end=' ')", answer: "n2", why: "An n by n grid of prints." },
];

const fmtNum = (v) => {
  if (v >= 1e15) return v.toExponential(2).replace("e+", "e");
  if (v >= 1000) return Math.round(v).toLocaleString("en-US");
  return String(Math.round(v * 10) / 10);
};
const fmtTime = (ns) => {
  const units = [[1e9 * 3600 * 24 * 365, "years"], [1e9 * 3600 * 24, "days"], [1e9 * 3600, "h"], [1e9 * 60, "min"], [1e9, "s"], [1e6, "ms"], [1e3, "µs"]];
  for (const [d, u] of units) if (ns >= d) return `${fmtNum(ns / d)} ${u}`;
  return `${fmtNum(ns)} ns`;
};

export function growthSvg(N, on, log = false, focus = "") {
  const W = 600, H = 320, L = 64, R = 16, T = 14, B = 38;
  const yv = (v) => (log ? Math.log10(Math.max(v, 1)) : v);
  const shown = GROWTH.filter((g) => on.has(g.id));
  const ymax = Math.max(log ? 1 : 2, ...shown.map((g) => yv(g.f(N))));
  const X = (n) => L + ((n - 1) / (N - 1)) * (W - L - R);
  const Y = (v) => H - B - (yv(v) / ymax) * (H - T - B);
  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((f) => f * ymax);
  const xTicks = [...new Set([0, 0.25, 0.5, 0.75, 1].map((f) => Math.round(1 + f * (N - 1))))];
  const grid = yTicks.map((t) => {
    const y = H - B - (t / ymax) * (H - T - B);
    return `<line x1="${L}" x2="${W - R}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}"/><text x="${L - 8}" y="${(y + 4).toFixed(1)}" text-anchor="end">${esc(fmtNum(log ? 10 ** t : t))}</text>`;
  }).join("");
  const xLabels = xTicks.map((n) => `<text x="${X(n).toFixed(1)}" y="${H - B + 18}" text-anchor="middle">${n}</text>`).join("");
  const curves = GROWTH.map((g, k) => {
    if (!on.has(g.id)) return "";
    const pts = Array.from({ length: 121 }, (_, s) => 1 + (s / 120) * (N - 1)).map((n) => `${X(n).toFixed(1)},${Y(g.f(n)).toFixed(1)}`).join(" ");
    const end = Y(g.f(N));
    return `<polyline class="dsa-curve c${k}${focus === g.id ? " is-focus" : ""}" points="${pts}"/><circle class="dsa-dot c${k}" cx="${X(N).toFixed(1)}" cy="${end.toFixed(1)}" r="4"/>`;
  }).join("");
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Operations versus n for common complexity classes">
    <g class="dsa-grid">${grid}</g>
    <line class="dsa-axis" x1="${L}" x2="${L}" y1="${T}" y2="${H - B}"/><line class="dsa-axis" x1="${L}" x2="${W - R}" y1="${H - B}" y2="${H - B}"/>
    <g class="dsa-ticks">${xLabels}<text x="${(L + W - R) / 2}" y="${H - 4}" text-anchor="middle">n</text></g>
    ${curves}
  </svg>`;
}

// ===================================================================== algorithm runner
const PROBLEMS = [
  {
    label: "Two sum (hash map)",
    note: "One pass with a dict of value to index: O(n) time, O(n) space, instead of O(n²) for checking every pair.",
    code: `def two_sum(nums, target):
    seen = {}                       # value -> index
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return seen[need], i
        seen[x] = i
    return None

print(two_sum([2, 7, 11, 15], 9))      # (0, 1)
print(two_sum([3, 2, 4], 6))           # (1, 2)
print(two_sum([1, 2, 3], 100))         # None`,
  },
  {
    label: "Binary search (count the steps)",
    note: "Halving the range each step means 100,000 items need at most 17 probes: O(log n).",
    code: `def binary_search(xs, target):
    lo, hi = 0, len(xs) - 1
    steps = 0
    while lo <= hi:
        steps += 1
        mid = (lo + hi) // 2
        if xs[mid] == target:
            return mid, steps
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, steps

xs = list(range(0, 200_000, 2))         # 100,000 sorted even numbers
for t in (0, 123_456, 199_998, 7):
    idx, steps = binary_search(xs, t)
    print(f"target={t:>7}  index={idx:>6}  steps={steps}")
print("ceil(log2(n)) =", len(xs).bit_length())`,
  },
  {
    label: "BFS shortest path on a grid",
    note: "Breadth-first search explores in rings of equal distance, so the first time it reaches E is a shortest path. O(rows * cols).",
    code: `from collections import deque

GRID = [
    "S.#.....",
    ".##.###.",
    "....#...",
    ".##...#E",
]

def shortest_path(grid):
    rows, cols = len(grid), len(grid[0])
    start = next((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == "S")
    prev = {start: None}
    q = deque([start])
    while q:
        r, c = q.popleft()
        if grid[r][c] == "E":
            path, node = [], (r, c)
            while node is not None:
                path.append(node)
                node = prev[node]
            return path[::-1]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#" and (nr, nc) not in prev:
                prev[(nr, nc)] = (r, c)
                q.append((nr, nc))
    return None

path = shortest_path(GRID)
print("steps:", len(path) - 1)
canvas = [list(row) for row in GRID]
for r, c in path[1:-1]:
    canvas[r][c] = "*"
print("\\n".join("".join(row) for row in canvas))`,
  },
  {
    label: "LRU cache",
    note: "A hash map for O(1) lookup plus a linked order for recency. OrderedDict gives both; move_to_end marks a key as fresh.",
    code: `from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return -1
        self.data.move_to_end(key)           # most recently used
        return self.data[key]

    def put(self, key, value):
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if len(self.data) > self.capacity:
            evicted, _ = self.data.popitem(last=False)
            print(f"  evict {evicted}")

cache = LRUCache(2)
cache.put("a", 1)
cache.put("b", 2)
print("get a ->", cache.get("a"))
cache.put("c", 3)                          # evicts b
print("get b ->", cache.get("b"))
cache.put("d", 4)                          # evicts a
print("keys:", list(cache.data))`,
  },
  {
    label: "0/1 knapsack (DP)",
    note: "best[c] is the best value for capacity c. Looping capacity backwards ensures each item is used at most once. O(n * capacity).",
    code: `def knapsack(items, capacity):
    best = [0] * (capacity + 1)
    keep = [[False] * (capacity + 1) for _ in items]
    for i, (name, weight, value) in enumerate(items):
        for c in range(capacity, weight - 1, -1):     # backwards
            if best[c - weight] + value > best[c]:
                best[c] = best[c - weight] + value
                keep[i][c] = True
    chosen, c = [], capacity
    for i in range(len(items) - 1, -1, -1):
        if keep[i][c]:
            chosen.append(items[i][0])
            c -= items[i][1]
    return best[capacity], chosen[::-1]

items = [("tent", 5, 60), ("stove", 3, 50), ("camera", 4, 70), ("book", 2, 30), ("snacks", 1, 15)]
value, chosen = knapsack(items, 8)
print("best value:", value)
print("take:", chosen)`,
  },
  {
    label: "Dijkstra (heapq)",
    note: "Always expand the closest unsettled node. With a binary heap: O((V + E) log V). Stale heap entries are skipped instead of decreased.",
    code: `import heapq

GRAPH = {
    "A": {"B": 4, "C": 1},
    "B": {"D": 1},
    "C": {"B": 2, "D": 5},
    "D": {"E": 3},
    "E": {},
}

def dijkstra(graph, source):
    dist = {node: float("inf") for node in graph}
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue                       # stale entry
        for nxt, w in graph[node].items():
            if d + w < dist[nxt]:
                dist[nxt] = d + w
                heapq.heappush(heap, (dist[nxt], nxt))
    return dist

print(dijkstra(GRAPH, "A"))`,
  },
  {
    label: "Sliding window maximum (deque)",
    note: "The deque keeps indices of a decreasing run; every index enters and leaves once, so it is O(n) instead of O(n * k).",
    code: `from collections import deque

def window_max(nums, k):
    dq, out = deque(), []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

print(window_max([1, 3, -1, -3, 5, 3, 6, 7], 3))    # [3, 3, 5, 5, 6, 7]`,
  },
  {
    label: "Measure growth: O(n²) vs O(n log n)",
    note: "Count comparisons while doubling n: the quadratic column roughly quadruples, the n log n column a bit more than doubles. Compare with the chart below.",
    code: `import random

def insertion_ops(xs):
    xs, ops = xs[:], 0
    for i in range(1, len(xs)):
        j = i
        while j > 0:
            ops += 1
            if xs[j - 1] <= xs[j]:
                break
            xs[j - 1], xs[j] = xs[j], xs[j - 1]
            j -= 1
    return ops

def merge_ops(xs):
    ops = 0
    def sort(a):
        nonlocal ops
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left, right = sort(a[:mid]), sort(a[mid:])
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            ops += 1
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        return out + left[i:] + right[j:]
    sort(xs)
    return ops

random.seed(1)
print(f"{'n':>6} {'insertion':>12} {'merge':>10}")
for n in (100, 200, 400, 800, 1600):
    xs = [random.random() for _ in range(n)]
    print(f"{n:>6} {insertion_ops(xs):>12} {merge_ops(xs):>10}")`,
  },
];

export function playground(view, content) {
  const samples = sampleOptions(content, ["python"]);
  view.innerHTML = `
    ${labHero("O(n)", "mint", "Algorithm Runner", "Solve classic problems in sandboxed Python 3 (standard library only, 6 second timeout), then build intuition for growth rates with the Big-O chart and quiz below.")}
    <div class="panel clay" style="margin-top:1.2rem">
      <div class="row">
        <select id="dsaProblem" class="dsa-grow"><option value="">Classic problem…</option>${PROBLEMS.map((p, i) => `<option value="${i}">${esc(p.label)}</option>`).join("")}</select>
        <select id="sample" class="dsa-grow"><option value="">Load a sample from the lessons…</option>${samples.map((s, i) => `<option value="${i}">${esc(s.label)}</option>`).join("")}</select>
      </div>
      <p class="muted dsa-note" id="dsaProbNote"></p>
      <textarea id="code" class="code code-editor" spellcheck="false" rows="16"></textarea>
      <div class="row" style="margin-top:.8rem;justify-content:flex-end">
        <button class="btn" id="toViz">Step through in Python lab</button>
        <button class="btn primary" id="run">Run <kbd>⌘/Ctrl ↵</kbd></button>
      </div>
    </div>
    <div class="panel clay" id="out" style="margin-top:1.2rem"><span class="muted">Output appears here.</span></div>
    <div class="lab-grid halves" style="margin-top:1.2rem">
      <div class="panel clay">
        <h3>Big-O growth</h3>
        <div class="dsa-toggles">${GROWTH.map((g, k) => `<label class="dsa-toggle"><input type="checkbox" value="${g.id}" checked><i class="dsa-sw c${k}"></i>${esc(g.label)}</label>`).join("")}</div>
        <div class="dsa-controls" style="margin-top:.8rem">
          <label class="dsa-field"><span>n = <b id="dsaGN"></b></span><input type="range" id="dsaGrowN" min="2" max="64" step="1" value="12"></label>
          <label class="dsa-switch"><input type="checkbox" id="dsaLog"> Log scale</label>
        </div>
        <div class="dsa-chart" id="dsaChart"></div>
        <div class="dsa-table-wrap"><table class="dsa-table" id="dsaReadout"></table></div>
      </div>
      <div class="panel clay">
        <h3>Which curve is this code?</h3>
        <div id="dsaQuiz"></div>
      </div>
    </div>`;

  const ta = $("#code");
  ta.value = takeHandoff("dsa-code") || PROBLEMS[0].code;
  $("#dsaProbNote").textContent = PROBLEMS[0].note;
  const run = async () => {
    $("#run").disabled = true;
    $("#out").innerHTML = `<span class="muted">Running…</span>`;
    const r = await runPython(ta.value);
    $("#run").disabled = false;
    $("#out").innerHTML = pyResultHtml(r);
  };
  codeEditor(ta, run, 4);
  $("#run").onclick = run;
  $("#dsaProblem").onchange = (e) => {
    if (e.target.value === "") return;
    const p = PROBLEMS[+e.target.value];
    ta.value = p.code;
    $("#dsaProbNote").textContent = p.note;
    $("#sample").value = "";
  };
  $("#sample").onchange = (e) => {
    if (e.target.value === "") return;
    ta.value = samples[+e.target.value].code;
    $("#dsaProbNote").textContent = "";
    $("#dsaProblem").value = "";
  };
  $("#toViz").onclick = () => {
    sessionStorage.setItem("py-code", ta.value);
    location.hash = "#/python/lab";
  };

  // growth chart
  const g = { n: 12, on: new Set(GROWTH.map((x) => x.id)), log: false, focus: "" };
  const draw = () => {
    $("#dsaGN").textContent = g.n;
    $("#dsaChart").innerHTML = g.on.size ? growthSvg(g.n, g.on, g.log, g.focus) : `<p class="muted">Turn on at least one curve.</p>`;
    $("#dsaReadout").innerHTML = `<thead><tr><th>Class</th><th>Operations at n = ${g.n}</th><th>At 1 ns per op</th></tr></thead><tbody>${GROWTH.map((c, k) => {
      const v = c.f(g.n);
      return `<tr class="${g.on.has(c.id) ? "" : "is-off"}"><th><i class="dsa-sw c${k}"></i>${esc(c.label)}</th><td>${esc(fmtNum(v))}</td><td>${esc(fmtTime(v))}</td></tr>`;
    }).join("")}</tbody>`;
  };
  $(".dsa-toggles").onchange = (e) => {
    if (e.target.checked) g.on.add(e.target.value);
    else g.on.delete(e.target.value);
    draw();
  };
  $("#dsaGrowN").oninput = (e) => {
    g.n = +e.target.value;
    draw();
  };
  $("#dsaLog").onchange = (e) => {
    g.log = e.target.checked;
    draw();
  };

  // quiz
  const order = QUIZ.map((_, i) => i);
  for (let i = order.length - 1; i > 0; i--) swap(order, i, Math.floor(Math.random() * (i + 1)));
  const q = { i: 0, score: 0, answered: 0, locked: false };
  const ask = () => {
    const item = QUIZ[order[q.i % order.length]];
    q.locked = false;
    $("#dsaQuiz").innerHTML = `
      <div class="row dsa-quiz-bar"><span class="pill neutral">Question ${q.answered + 1}</span><span class="muted">Score ${q.score} / ${q.answered}</span></div>
      <pre class="yaml dsa-snippet">${highlightCode(item.code, "python")}</pre>
      <div class="dsa-quiz-opts">${GROWTH.map((c) => `<button class="btn small dsa-opt" data-g="${c.id}">${esc(c.label)}</button>`).join("")}</div>
      <div id="dsaQuizWhy"></div>`;
  };
  $("#dsaQuiz").onclick = (e) => {
    if (e.target.closest("#dsaNext")) {
      q.i++;
      g.focus = "";
      draw();
      return ask();
    }
    const btn = e.target.closest(".dsa-opt");
    if (!btn || q.locked) return;
    q.locked = true;
    const item = QUIZ[order[q.i % order.length]];
    const ok = btn.dataset.g === item.answer;
    q.answered++;
    if (ok) q.score++;
    $$(".dsa-opt", $("#dsaQuiz")).forEach((b) => {
      b.disabled = true;
      if (b.dataset.g === item.answer) b.classList.add("is-right");
      else if (b === btn) b.classList.add("is-wrong");
    });
    $(".dsa-quiz-bar .muted").textContent = `Score ${q.score} / ${q.answered}`;
    const label = GROWTH.find((c) => c.id === item.answer).label;
    $("#dsaQuizWhy").innerHTML = `<div class="bug-why ${ok ? "good" : "bad"}"><b>${ok ? "Correct" : `It is ${esc(label)}`}.</b> ${esc(item.why)}</div>
      <div class="row" style="justify-content:flex-end;margin-top:.7rem"><button class="btn small primary" id="dsaNext">Next</button></div>`;
    g.on.add(item.answer);
    $$(".dsa-toggles input").forEach((c) => (c.checked = g.on.has(c.value)));
    g.focus = item.answer;
    draw();
  };

  draw();
  ask();
}
