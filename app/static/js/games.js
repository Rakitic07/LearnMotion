import { $, $$, esc, highlightCode, store, toast } from "./util.js";
import { track } from "./account.js";

// Active subject's game data, set by renderGames.
let D = { sid: "k8s", WORDS: [], RUSH: [], BUGS: [] };
const bestKey = () => (D.sid === "k8s" ? "game-best" : `game-best:${D.sid}`);

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
const pick = (arr, n) => shuffle(arr).slice(0, n);
const clock = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

function recordBest(key, value, lowerIsBetter = false) {
  const bests = store.get(bestKey(), {});
  const prev = bests[key];
  const better = prev === undefined || (lowerIsBetter ? value < prev : value > prev);
  if (better) store.set(bestKey(), { ...bests, [key]: value });
  track("game_done", { sid: D.sid, topic: null, detail: `${key}: ${value}${better ? " (best)" : ""}` });
  return better;
}
const getBest = (key) => store.get(bestKey(), {})[key];

// ------------------------------------------------------------------ crossword
function generateCrossword(target = 12, maxCols = 40) {
  let best = null;
  for (let t = 0; t < 40 && !(best && best.words.length >= target); t++) {
    const cands = pick(D.WORDS, target + 8).sort((a, b) => b.answer.length - a.answer.length);
    const firstFit = cands.findIndex((w) => w.answer.length <= maxCols);
    cands.unshift(...cands.splice(firstFit, 1));
    const res = layoutAttempt(cands, target, maxCols);
    if (!best || res.words.length > best.words.length) best = res;
  }
  return best;
}

function layoutAttempt(cands, target, maxCols) {
  const N = 45;
  const grid = Array.from({ length: N }, () => Array(N).fill(null));
  const get = (r, c) => (r < 0 || c < 0 || r >= N || c >= N ? null : grid[r][c]);
  const step = (dir) => (dir === "a" ? [0, 1] : [1, 0]);
  const placed = [];
  let minC = N, maxC = -1;

  const score = (w, r, c, dir) => {
    const [dr, dc] = step(dir);
    if (r < 0 || c < 0 || r + dr * (w.length - 1) >= N || c + dc * (w.length - 1) >= N) return -1;
    if (get(r - dr, c - dc) || get(r + dr * w.length, c + dc * w.length)) return -1;
    if (Math.max(maxC, c + dc * (w.length - 1)) - Math.min(minC, c) + 1 > maxCols) return -1;
    let cross = 0;
    for (let i = 0; i < w.length; i++) {
      const rr = r + dr * i, cc = c + dc * i, cell = grid[rr][cc];
      if (cell) {
        if (cell.ch !== w[i] || cell[dir]) return -1;
        cross++;
      } else if (get(rr + dc, cc + dr) || get(rr - dc, cc - dr)) return -1;
    }
    return cross;
  };
  const place = (entry, r, c, dir) => {
    const [dr, dc] = step(dir);
    for (let i = 0; i < entry.answer.length; i++) {
      const rr = r + dr * i, cc = c + dc * i;
      grid[rr][cc] = grid[rr][cc] || { ch: entry.answer[i] };
      grid[rr][cc][dir] = true;
    }
    placed.push({ ...entry, r, c, dir });
    minC = Math.min(minC, c);
    maxC = Math.max(maxC, c + dc * (entry.answer.length - 1));
  };

  const first = cands[0];
  place(first, Math.floor(N / 2), Math.floor((N - first.answer.length) / 2), "a");
  for (const e of cands.slice(1)) {
    if (placed.length >= target) break;
    const options = [];
    for (const p of placed) {
      const dir = p.dir === "a" ? "d" : "a";
      for (let i = 0; i < p.answer.length; i++) {
        for (let j = 0; j < e.answer.length; j++) {
          if (p.answer[i] !== e.answer[j]) continue;
          const [pr, pc] = p.dir === "a" ? [p.r, p.c + i] : [p.r + i, p.c];
          const [r, c] = dir === "a" ? [pr, pc - j] : [pr - j, pc];
          const cross = score(e.answer, r, c, dir);
          if (cross > 0) options.push({ r, c, dir, cross });
        }
      }
    }
    if (!options.length) continue;
    const top = Math.max(...options.map((o) => o.cross));
    const o = pick(options.filter((x) => x.cross === top), 1)[0];
    place(e, o.r, o.c, o.dir);
  }

  const rs = placed.flatMap((w) => [w.r, w.dir === "d" ? w.r + w.answer.length - 1 : w.r]);
  const cs = placed.flatMap((w) => [w.c, w.dir === "a" ? w.c + w.answer.length - 1 : w.c]);
  const r0 = Math.min(...rs), c0 = Math.min(...cs);
  const words = placed.map((w) => ({ ...w, r: w.r - r0, c: w.c - c0 })).sort((a, b) => a.r - b.r || a.c - b.c);
  const nums = new Map();
  for (const w of words) {
    const key = `${w.r},${w.c}`;
    if (!nums.has(key)) nums.set(key, nums.size + 1);
    w.num = nums.get(key);
  }
  return { rows: Math.max(...rs) - r0 + 1, cols: Math.max(...cs) - c0 + 1, words, nums };
}

function crossword(mount) {
  let timer, seconds, revealed, puzzle, cur;
  const cellsOf = (w) => Array.from(w.answer, (ch, i) => ({ r: w.r + (w.dir === "d" ? i : 0), c: w.c + (w.dir === "a" ? i : 0), ch }));
  const wordAt = (r, c, dir) => puzzle.words.find((w) => w.dir === dir && cellsOf(w).some((x) => x.r === r && x.c === c));
  const input = (r, c) => $(`.cw-cell[data-r="${r}"][data-c="${c}"] input`, mount);
  const solution = new Map();

  function start() {
    const cell = Math.min(36, Math.max(24, window.innerWidth * 0.034)) + 3;
    const avail = (window.innerWidth > 980 ? mount.clientWidth - 340 : mount.clientWidth) - 50;
    puzzle = generateCrossword(12, Math.max(10, Math.floor(avail / cell)));
    solution.clear();
    for (const w of puzzle.words) for (const x of cellsOf(w)) solution.set(`${x.r},${x.c}`, x.ch);
    seconds = 0;
    revealed = false;
    cur = { r: puzzle.words[0].r, c: puzzle.words[0].c, dir: puzzle.words[0].dir };
    clearInterval(timer);
    timer = setInterval(() => { seconds++; const t = $("#cwTimer", mount); if (t) t.textContent = clock(seconds); }, 1000);

    const cells = [];
    for (let r = 0; r < puzzle.rows; r++) {
      for (let c = 0; c < puzzle.cols; c++) {
        if (!solution.has(`${r},${c}`)) { cells.push(`<div class="cw-block"></div>`); continue; }
        const n = puzzle.nums.get(`${r},${c}`);
        cells.push(`<div class="cw-cell" data-r="${r}" data-c="${c}">${n ? `<span class="cw-num">${n}</span>` : ""}<input maxlength="2" autocomplete="off" autocapitalize="characters" spellcheck="false" aria-label="Row ${r + 1} column ${c + 1}"></div>`);
      }
    }
    const clues = (dir) => puzzle.words.filter((w) => w.dir === dir)
      .map((w) => `<li data-num="${w.num}" data-dir="${dir}"><b>${w.num}</b>${esc(w.clue)} <span class="muted">(${w.answer.length})</span></li>`).join("");
    const best = getBest("crossword");
    mount.innerHTML = `
      <div class="game-bar">
        <span class="game-stat">Time <b id="cwTimer">0:00</b></span>
        <span class="game-stat">Words <b>${puzzle.words.length}</b></span>
        ${best !== undefined ? `<span class="game-stat">Best <b>${clock(best)}</b></span>` : ""}
        <span class="spacer"></span>
        <button class="btn small" data-cw="check">Check</button>
        <button class="btn small" data-cw="word">Reveal word</button>
        <button class="btn small" data-cw="all">Reveal all</button>
        <button class="btn small primary" data-cw="new">New puzzle</button>
      </div>
      <div class="cw-layout">
        <div class="panel clay cw-board">
          <div class="cw-grid" style="--cols:${puzzle.cols}">${cells.join("")}</div>
          <div class="cw-current" id="cwCurrent"></div>
        </div>
        <div class="panel clay cw-clues">
          <h3>Across</h3><ol>${clues("a")}</ol>
          <h3>Down</h3><ol>${clues("d")}</ol>
        </div>
      </div>`;
    highlight();
  }

  function highlight() {
    const w = wordAt(cur.r, cur.c, cur.dir);
    $$(".cw-cell", mount).forEach((el) => el.classList.remove("in-word", "cur"));
    $$(".cw-clues li", mount).forEach((li) => li.classList.toggle("active", !!w && +li.dataset.num === w.num && li.dataset.dir === w.dir));
    if (!w) return;
    for (const x of cellsOf(w)) input(x.r, x.c).parentElement.classList.add("in-word");
    input(cur.r, cur.c).parentElement.classList.add("cur");
    $("#cwCurrent", mount).innerHTML = `<b>${w.num} ${w.dir === "a" ? "Across" : "Down"}:</b> ${esc(w.clue)}`;
  }

  function focusCell(r, c, dir = cur.dir) {
    const el = input(r, c);
    if (!el) return false;
    if (!wordAt(r, c, dir)) dir = dir === "a" ? "d" : "a";
    cur = { r, c, dir };
    el.focus();
    highlight();
    return true;
  }

  function move(delta) {
    const [dr, dc] = cur.dir === "a" ? [0, 1] : [1, 0];
    const r = cur.r + dr * delta, c = cur.c + dc * delta;
    if (input(r, c)) focusCell(r, c, cur.dir);
  }

  function markDone() {
    for (const w of puzzle.words) {
      const ok = cellsOf(w).every((x) => input(x.r, x.c).value === x.ch);
      const li = $(`.cw-clues li[data-num="${w.num}"][data-dir="${w.dir}"]`, mount);
      if (li) li.classList.toggle("done", ok);
    }
    const solved = [...solution].every(([k, ch]) => input(...k.split(",").map(Number)).value === ch);
    if (!solved) return;
    clearInterval(timer);
    $$(".cw-cell", mount).forEach((el) => el.classList.add("solved"));
    const isBest = !revealed && recordBest("crossword", seconds, true);
    toast(revealed ? "Puzzle complete (with reveals)" : `Solved in ${clock(seconds)}${isBest ? " · new best!" : ""}`);
  }

  function reveal(cells) {
    revealed = true;
    for (const x of cells) {
      const el = input(x.r, x.c);
      if (el.value !== x.ch) { el.value = x.ch; el.parentElement.classList.add("revealed"); }
      el.parentElement.classList.remove("wrong");
    }
    markDone();
  }

  mount.addEventListener("focusin", (e) => {
    const cell = e.target.closest(".cw-cell");
    if (!cell) return;
    const r = +cell.dataset.r, c = +cell.dataset.c;
    if (r !== cur.r || c !== cur.c) focusCell(r, c);
  });
  mount.addEventListener("mousedown", (e) => {
    const cell = e.target.closest(".cw-cell");
    if (!cell || +cell.dataset.r !== cur.r || +cell.dataset.c !== cur.c) return;
    const other = cur.dir === "a" ? "d" : "a";
    if (wordAt(cur.r, cur.c, other)) { cur.dir = other; highlight(); }
  });
  mount.addEventListener("input", (e) => {
    const el = e.target;
    if (!el.closest(".cw-cell")) return;
    el.value = el.value.toUpperCase().replace(/[^A-Z]/g, "").slice(-1);
    el.parentElement.classList.remove("wrong", "revealed");
    if (el.value) move(1);
    markDone();
  });
  mount.addEventListener("keydown", (e) => {
    if (!e.target.closest(".cw-cell")) return;
    const arrows = { ArrowRight: ["a", 1], ArrowLeft: ["a", -1], ArrowDown: ["d", 1], ArrowUp: ["d", -1] };
    if (arrows[e.key]) {
      e.preventDefault();
      const [dir, d] = arrows[e.key];
      const [dr, dc] = dir === "a" ? [0, d] : [d, 0];
      let r = cur.r + dr, c = cur.c + dc;
      while (r >= 0 && c >= 0 && r < puzzle.rows && c < puzzle.cols && !input(r, c)) { r += dr; c += dc; }
      if (input(r, c)) focusCell(r, c, dir);
    } else if (e.key === "Backspace" && !e.target.value) {
      e.preventDefault();
      move(-1);
      const el = input(cur.r, cur.c);
      el.value = "";
      el.parentElement.classList.remove("wrong", "revealed");
      markDone();
    }
  });
  mount.addEventListener("click", (e) => {
    const li = e.target.closest(".cw-clues li");
    if (li) {
      const w = puzzle.words.find((x) => x.num === +li.dataset.num && x.dir === li.dataset.dir);
      const firstEmpty = cellsOf(w).find((x) => !input(x.r, x.c).value) || cellsOf(w)[0];
      focusCell(firstEmpty.r, firstEmpty.c, w.dir);
      return;
    }
    const action = e.target.closest("[data-cw]")?.dataset.cw;
    if (action === "new") start();
    else if (action === "all") reveal([...solution].map(([k, ch]) => { const [r, c] = k.split(",").map(Number); return { r, c, ch }; }));
    else if (action === "word") { const w = wordAt(cur.r, cur.c, cur.dir); if (w) reveal(cellsOf(w)); }
    else if (action === "check") {
      let wrong = 0;
      for (const [k, ch] of solution) {
        const el = input(...k.split(",").map(Number));
        const bad = !!el.value && el.value !== ch;
        el.parentElement.classList.toggle("wrong", bad);
        wrong += bad;
      }
      toast(wrong ? `${wrong} letter${wrong > 1 ? "s" : ""} wrong` : "No mistakes so far", !!wrong);
    }
  });

  start();
  return () => clearInterval(timer);
}

// ------------------------------------------------------------------ kubectl rush
function rush(mount) {
  const DURATION = 60;
  let tick, deadline, score, streak, answered, correct, missed, queue, locked;

  function intro() {
    const best = getBest("rush");
    mount.innerHTML = `
      <div class="panel clay game-intro">
        <h2>${esc(D.rushLabel)}</h2>
        <p class="muted">60 seconds. ${esc(D.rushIntro)} Streaks add bonus points, and wrong answers cost a little time.</p>
        ${best !== undefined ? `<p>Best score: <b>${best}</b></p>` : ""}
        <button class="btn primary" data-rush="start">Start</button>
      </div>`;
  }

  function startGame() {
    score = 0; streak = 0; answered = 0; correct = 0; missed = []; queue = shuffle(D.RUSH); locked = false;
    deadline = Date.now() + DURATION * 1000;
    mount.innerHTML = `
      <div class="game-bar">
        <span class="game-stat">Score <b id="rushScore">0</b></span>
        <span class="game-stat">Streak <b id="rushStreak">0</b></span>
        <div class="rush-time"><i id="rushBar" style="width:100%"></i></div>
        <span class="game-stat"><b id="rushLeft">${DURATION}</b>s</span>
      </div>
      <div class="panel clay rush-card" id="rushCard"></div>`;
    next();
    tick = setInterval(() => {
      const left = Math.max(0, deadline - Date.now());
      $("#rushBar", mount).style.width = `${(left / (DURATION * 1000)) * 100}%`;
      $("#rushLeft", mount).textContent = Math.ceil(left / 1000);
      if (!left) finish();
    }, 100);
  }

  function next() {
    if (!queue.length) queue = shuffle(D.RUSH);
    const q = queue.pop();
    const opts = shuffle([q.answer, ...q.wrong]);
    locked = false;
    $("#rushCard", mount).innerHTML = `
      <div class="muted">Task</div>
      <div class="rush-task">${esc(q.task)}</div>
      <div class="rush-options${D.rushMono ? "" : " concept"}">${opts.map((o) => `<button class="btn rush-opt" data-opt="${esc(o)}">${esc(o)}</button>`).join("")}</div>`;
    $("#rushCard", mount).dataset.answer = q.answer;
    $("#rushCard", mount).dataset.task = q.task;
  }

  function choose(btn) {
    if (locked) return;
    locked = true;
    const card = $("#rushCard", mount);
    const ok = btn.dataset.opt === card.dataset.answer;
    answered++;
    if (ok) {
      correct++;
      streak++;
      score += 10 + Math.min(streak - 1, 5) * 2;
      btn.classList.add("right");
    } else {
      streak = 0;
      deadline -= 3000;
      missed.push({ task: card.dataset.task, answer: card.dataset.answer });
      btn.classList.add("wrong");
      $$(".rush-opt", card).find((b) => b.dataset.opt === card.dataset.answer)?.classList.add("right");
    }
    $("#rushScore", mount).textContent = score;
    $("#rushStreak", mount).textContent = streak;
    setTimeout(() => { if (Date.now() < deadline) next(); }, ok ? 350 : 1100);
  }

  function finish() {
    clearInterval(tick);
    const isBest = recordBest("rush", score);
    mount.innerHTML = `
      <div class="panel clay game-intro">
        <h2>Time's up</h2>
        <div class="big-number">${score}</div>
        <p class="muted">${correct} / ${answered} correct${isBest && score ? " · new best!" : ""}</p>
        <button class="btn primary" data-rush="start">Play again</button>
      </div>
      ${missed.length ? `<div class="panel clay" style="margin-top:1.2rem"><h3>Review</h3><ul class="clean cmd-list">${missed.map((m) => `<li><span>${esc(m.task)}</span><code>${esc(m.answer)}</code></li>`).join("")}</ul></div>` : ""}`;
  }

  mount.addEventListener("click", (e) => {
    if (e.target.closest('[data-rush="start"]')) startGame();
    const opt = e.target.closest(".rush-opt");
    if (opt) choose(opt);
  });
  intro();
  return () => clearInterval(tick);
}

// ------------------------------------------------------------------ YAML bug hunt
function bugHunt(mount) {
  let deck, i, score, tries, found;

  function start() {
    deck = shuffle(D.BUGS);
    i = 0; score = 0;
    draw();
  }

  function draw() {
    if (i >= deck.length) return finish();
    const p = deck[i];
    tries = 0; found = false;
    const lines = highlightCode(p.code ?? p.yaml, p.lang || "yaml").split("\n");
    mount.innerHTML = `
      <div class="game-bar">
        <span class="game-stat">Puzzle <b>${i + 1} / ${deck.length}</b></span>
        <span class="game-stat">Score <b>${score}</b></span>
        <span class="spacer"></span>
        <button class="btn small" data-bug="skip">Skip</button>
      </div>
      <div class="panel clay">
        <div class="bug-symptom"><span class="pill bad">${esc(D.bugNoun)}</span> ${esc(p.symptom)}</div>
        <p class="muted" style="margin:.6rem 0 0">Click the line that causes it.</p>
        <pre class="yaml bug-code">${lines.map((l, n) => `<button class="bug-line" data-line="${n}"><span class="ln">${n + 1}</span><span>${l || " "}</span></button>`).join("")}</pre>
        <div id="bugWhy"></div>
      </div>`;
  }

  function guess(btn) {
    if (found) return;
    const p = deck[i];
    const n = +btn.dataset.line;
    tries++;
    if (!p.bug.includes(n)) {
      btn.classList.add("miss");
      if (tries < 3) return;
    }
    found = true;
    const pts = p.bug.includes(n) ? Math.max(1, 4 - tries) : 0;
    score += pts;
    $$(".bug-line", mount).forEach((b) => b.classList.toggle("hit", p.bug.includes(+b.dataset.line)));
    $(".bug-code", mount).classList.add("done");
    $("#bugWhy", mount).innerHTML = `
      <div class="bug-why ${pts ? "good" : "bad"}"><b>${pts ? `+${pts} point${pts > 1 ? "s" : ""}` : "Out of tries"}.</b> ${esc(p.why)}</div>
      <div class="row" style="justify-content:flex-end;margin-top:.8rem"><button class="btn primary" data-bug="next">${i + 1 < deck.length ? "Next bug" : "See score"}</button></div>`;
  }

  function finish() {
    const max = deck.length * 3;
    const isBest = recordBest("bughunt", score);
    mount.innerHTML = `
      <div class="panel clay game-intro">
        <h2>Bug hunt complete</h2>
        <div class="big-number">${score} <span class="muted" style="font-size:1rem">/ ${max}</span></div>
        <p class="muted">3 points for a first-try find, 2 for the second, 1 for the third.${isBest && score ? " New best!" : ""}</p>
        <button class="btn primary" data-bug="restart">Play again</button>
      </div>`;
  }

  mount.addEventListener("click", (e) => {
    const line = e.target.closest(".bug-line");
    if (line) return guess(line);
    const a = e.target.closest("[data-bug]")?.dataset.bug;
    if (a === "next" || a === "skip") { i++; draw(); }
    if (a === "restart") start();
  });
  start();
}

// ------------------------------------------------------------------ memory match
function memory(mount) {
  let open, moves, matched, timer, seconds, lock;

  function start() {
    const pairs = pick(D.WORDS.filter((w) => w.clue.length <= 80), 6);
    const cards = shuffle(pairs.flatMap((w, k) => [{ k, kind: "term", text: w.term }, { k, kind: "clue", text: w.clue }]));
    open = []; moves = 0; matched = 0; seconds = 0; lock = false;
    clearInterval(timer);
    timer = null;
    const best = getBest("memory");
    mount.innerHTML = `
      <div class="game-bar">
        <span class="game-stat">Moves <b id="memMoves">0</b></span>
        <span class="game-stat">Time <b id="memTime">0:00</b></span>
        ${best !== undefined ? `<span class="game-stat">Best <b>${best} moves</b></span>` : ""}
        <span class="spacer"></span>
        <button class="btn small primary" data-mem="new">New deck</button>
      </div>
      <p class="muted" style="margin:0 0 1rem">Match each term with its definition.</p>
      <div class="mem-grid">${cards.map((c) => `
        <button class="mem-card" data-k="${c.k}" aria-label="Hidden card">
          <span class="mem-inner"><span class="mem-face mem-front">K8s</span><span class="mem-face mem-back ${c.kind}">${esc(c.text)}</span></span>
        </button>`).join("")}</div>`;
  }

  function flip(card) {
    if (lock || card.classList.contains("open") || card.classList.contains("matched")) return;
    if (!timer) timer = setInterval(() => { seconds++; const t = $("#memTime", mount); if (t) t.textContent = clock(seconds); }, 1000);
    card.classList.add("open");
    open.push(card);
    if (open.length < 2) return;
    moves++;
    $("#memMoves", mount).textContent = moves;
    const [a, b] = open;
    open = [];
    if (a.dataset.k === b.dataset.k) {
      a.classList.add("matched"); b.classList.add("matched");
      matched++;
      if (matched === 6) {
        clearInterval(timer);
        const isBest = recordBest("memory", moves, true);
        toast(`All pairs in ${moves} moves${isBest ? " · new best!" : ""}`);
      }
    } else {
      lock = true;
      setTimeout(() => { a.classList.remove("open"); b.classList.remove("open"); lock = false; }, 950);
    }
  }

  mount.addEventListener("click", (e) => {
    const card = e.target.closest(".mem-card");
    if (card) flip(card);
    if (e.target.closest('[data-mem="new"]')) start();
  });
  start();
  return () => clearInterval(timer);
}

// ------------------------------------------------------------------ scramble
function scramble(mount) {
  const ROUNDS = 10;
  let rounds, i, score, hints, letters;

  function start() {
    rounds = pick(D.WORDS.filter((w) => w.answer.length >= 4 && w.answer.length <= 11), ROUNDS);
    i = 0; score = 0;
    draw();
  }

  function draw() {
    if (i >= rounds.length) return finish();
    const w = rounds[i];
    hints = 0;
    do letters = shuffle([...w.answer]); while (letters.join("") === w.answer);
    mount.innerHTML = `
      <div class="game-bar">
        <span class="game-stat">Word <b>${i + 1} / ${rounds.length}</b></span>
        <span class="game-stat">Score <b>${score}</b></span>
        <span class="spacer"></span>
        <button class="btn small" data-scr="hint">Hint (−2)</button>
        <button class="btn small" data-scr="skip">Skip</button>
      </div>
      <div class="panel clay scr-card">
        <div class="muted">Clue</div>
        <div class="scr-clue">${esc(w.clue)}</div>
        <div class="scr-tiles">${letters.map((l, k) => `<button class="scr-tile" data-k="${k}">${l}</button>`).join("")}</div>
        <form class="row scr-form" id="scrForm">
          <input type="text" class="scr-input" id="scrInput" maxlength="${w.answer.length}" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="${"_ ".repeat(w.answer.length).trim()}" aria-label="Your answer">
          <button type="button" class="btn" data-scr="clear">Clear</button>
          <button class="btn primary">Submit</button>
        </form>
        <div id="scrMsg" class="scr-msg"></div>
      </div>`;
    $("#scrInput", mount).focus();
  }

  function sync() {
    const el = $("#scrInput", mount);
    el.value = el.value.toUpperCase().replace(/[^A-Z]/g, "");
    const used = new Set();
    for (const ch of el.value) {
      const k = letters.findIndex((l, n) => l === ch && !used.has(n));
      if (k >= 0) used.add(k);
    }
    $$(".scr-tile", mount).forEach((t) => t.classList.toggle("used", used.has(+t.dataset.k)));
  }

  function advance(msg, good) {
    const m = $("#scrMsg", mount);
    m.className = `scr-msg ${good ? "good" : "bad"}`;
    m.innerHTML = msg;
    $$(".scr-tile, #scrForm button, #scrInput, [data-scr]", mount).forEach((b) => (b.disabled = true));
    setTimeout(() => { i++; draw(); }, good ? 900 : 1600);
  }

  function finish() {
    const isBest = recordBest("scramble", score);
    mount.innerHTML = `
      <div class="panel clay game-intro">
        <h2>Scramble complete</h2>
        <div class="big-number">${score} <span class="muted" style="font-size:1rem">/ ${ROUNDS * 10}</span></div>
        <p class="muted">${isBest && score ? "New best!" : "Hints cost 2 points each."}</p>
        <button class="btn primary" data-scr="restart">Play again</button>
      </div>`;
  }

  mount.addEventListener("input", (e) => { if (e.target.id === "scrInput") sync(); });
  mount.addEventListener("submit", (e) => {
    e.preventDefault();
    const w = rounds[i];
    const val = $("#scrInput", mount).value.toUpperCase();
    if (val === w.answer) {
      const pts = Math.max(2, 10 - hints * 2);
      score += pts;
      advance(`Correct: <b>${esc(w.term)}</b> · +${pts}`, true);
    } else {
      const m = $("#scrMsg", mount);
      m.className = "scr-msg bad";
      m.textContent = val.length < w.answer.length ? `Needs ${w.answer.length} letters` : "Not quite, try again";
    }
  });
  mount.addEventListener("click", (e) => {
    const tile = e.target.closest(".scr-tile");
    if (tile && !tile.classList.contains("used")) {
      const el = $("#scrInput", mount);
      el.value += letters[+tile.dataset.k];
      sync();
      el.focus();
    }
    const a = e.target.closest("[data-scr]")?.dataset.scr;
    if (a === "clear") { $("#scrInput", mount).value = ""; sync(); }
    if (a === "skip") advance(`The answer was <b>${esc(rounds[i].term)}</b>`, false);
    if (a === "restart") start();
    if (a === "hint") {
      const w = rounds[i];
      const el = $("#scrInput", mount);
      let k = 0;
      while (k < el.value.length && el.value[k] === w.answer[k]) k++;
      if (k >= w.answer.length) return;
      hints++;
      el.value = w.answer.slice(0, k + 1);
      sync();
      el.focus();
    }
  });
  start();
}

// ------------------------------------------------------------------ hub
const GAMES = [
  { id: "crossword", label: "Crossword", render: crossword },
  { id: "rush", label: () => D.rushLabel, render: rush },
  { id: "bughunt", label: () => D.bugLabel, render: bugHunt },
  { id: "memory", label: "Memory Match", render: memory },
  { id: "scramble", label: "Term Scramble", render: scramble },
];

export function renderGames(view, content, params, data) {
  D = { sid: content.subject.id, ...data };
  let current = GAMES.find((g) => g.id === params.get("g")) || GAMES[0];
  let stop = () => {};

  view.innerHTML = `
    <section class="topic-hero clay">
      <div class="code tint-lilac">GM</div>
      <div>
        <h1>${esc(content.subject.name)} Mini Games</h1>
        <div class="muted">Learn by playing: a fresh crossword every time, ${esc(D.rushLabel)} drills, ${esc(D.bugLabel)}, memory pairs and word scrambles. Best scores stay in this browser.</div>
      </div>
    </section>
    <div class="filters"><div class="tabs" id="gameTabs">${GAMES.map((g) => `<button data-g="${g.id}">${esc(typeof g.label === "function" ? g.label() : g.label)}</button>`).join("")}</div></div>
    <div id="gameMount"></div>`;

  const open = (game) => {
    stop();
    current = game;
    $$("#gameTabs button").forEach((b) => b.classList.toggle("active", b.dataset.g === game.id));
    history.replaceState(null, "", `#/${D.sid}/games?g=${game.id}`);
    // Fresh node per game so listeners from the previous game don't pile up.
    const old = $("#gameMount");
    const mount = old.cloneNode(false);
    old.replaceWith(mount);
    stop = game.render(mount) || (() => {});
  };

  $("#gameTabs").addEventListener("click", (e) => {
    const g = GAMES.find((x) => x.id === e.target.closest("[data-g]")?.dataset.g);
    if (g && g !== current) open(g);
  });
  open(current);
  return () => stop();
}
