import { esc, store } from "./util.js";
import { subjectIcon } from "./icons.js";
import { currentUser, openAuth } from "./account.js";

const PILLARS = [
  ["Learn", "Animated walkthroughs, analogies and examples for every concept.", "sky"],
  ["Lab", "A simulator per subject: scheduler, isolation levels, git graph, code stepper, IAM, shell challenges, Java version diffs.", "mint"],
  ["Playground", "Real SQL and Python, git and Linux shell sandboxes, a Kind cluster, VPC checks and a Java version checker.", "lilac"],
  ["Interview Prep", "Flashcards, scenario drills and cheat sheets from basic to advanced.", "peach"],
  ["Games", "Crosswords, timed rushes, bug hunts, memory pairs and scrambles.", "lemon"],
];

// Hero phone scenes. Node positions are percentages of the mini-flow box; links are [from, to] node indexes.
const SCENES = [
  { sid: "sysdesign", title: "Caching", nodes: [["Client", 20, 25], ["Redis", 80, 25], ["DB", 80, 79]], links: [[0, 1], [0, 2]],
    caps: ["Client asks the cache first", "Hit: Redis answers in under 1 ms", "Miss: read the DB, then fill the cache"],
    cards: [["Cache hit", "0.4 ms", 92], ["Interview streak", "12 days", 64]], fc2: ["GET user:42", "HIT"], fc3: ["TTL 300 s", "LRU eviction on"] },
  { sid: "k8s", title: "Scheduling", nodes: [["kubectl", 20, 25], ["API server", 78, 25], ["node-2", 50, 80]], links: [[0, 1], [1, 2]],
    caps: ["kubectl sends the manifest", "API server stores it in etcd", "Scheduler binds the pod to node-2"],
    cards: [["Pods ready", "3 / 3", 100], ["CPU vs HPA target", "48%", 48]], fc2: ["kubectl apply -f app.yaml", "applied"], fc3: ["pod/web-7c9 Running", "node-2 · 2 s"] },
  { sid: "db", title: "Index lookup", nodes: [["Query", 20, 25], ["B-tree", 80, 25], ["Rows", 80, 79]], links: [[0, 1], [1, 2]],
    caps: ["Planner reads WHERE email = ?", "Walks the B-tree in 3 hops", "Fetches only the matching rows"],
    cards: [["Index scan", "3 ms", 85], ["Rows returned", "12", 40]], fc2: ["EXPLAIN QUERY PLAN", "index used"], fc3: ["SELECT … JOIN", "12 rows · 3 ms"] },
  { sid: "git", title: "Rebase", nodes: [["feature", 20, 25], ["main", 80, 25], ["rebased", 50, 80]], links: [[0, 1], [1, 2]],
    caps: ["feature branched from an old main", "main moved ahead by 2 commits", "Commits replayed on top of main"],
    cards: [["Commits replayed", "3", 75], ["Conflicts", "0", 4]], fc2: ["git rebase main", "solved"], fc3: ["git log --oneline", "linear history"] },
  { sid: "python", title: "Generators", nodes: [["gen()", 20, 25], ["yield", 80, 25], ["for loop", 50, 80]], links: [[0, 1], [1, 2]],
    caps: ["Calling gen() runs nothing yet", "Each next() runs to the next yield", "The loop gets one item at a time"],
    cards: [["Items streamed", "1,000", 70], ["Peak memory", "2 KB", 12]], fc2: ["next(gen)", "42"], fc3: ["yield from chunks()", "lazy"] },
  { sid: "aws", title: "IAM decision", nodes: [["User", 20, 25], ["IAM", 80, 25], ["S3", 80, 79]], links: [[0, 1], [1, 2]],
    caps: ["Request: s3:GetObject", "IAM checks deny, then allow", "Allowed: S3 returns the object"],
    cards: [["Policy decision", "Allow", 100], ["p99 latency", "38 ms", 55]], fc2: ["s3:GetObject", "allowed"], fc3: ["Explicit deny wins", "policy eval"] },
  { sid: "linux", title: "Pipelines", nodes: [["cat", 20, 25], ["grep", 80, 25], ["wc -l", 50, 80]], links: [[0, 1], [1, 2]],
    caps: ["cat streams app.log to stdout", "grep keeps the ERROR lines", "wc -l counts what is left"],
    cards: [["Exit code", "0", 100], ["Lines matched", "42", 48]], fc2: ["grep -c ERROR app.log", "42"], fc3: ["chmod 750 deploy.sh", "rwxr-x---"] },
  { sid: "java", title: "Java upgrade", nodes: [["Java 8", 20, 25], ["Java 17", 80, 25], ["Java 21", 50, 80]], links: [[0, 1], [1, 2]],
    caps: ["Java 8: lambdas and streams", "Java 17: records and sealed types", "Java 21: virtual threads"],
    cards: [["Minimum version", "17", 70], ["Virtual threads", "10k", 90]], fc2: ["record Point(int x, int y)", "Java 16+"], fc3: ["switch pattern match", "Java 21"] },
  { sid: "sysdesign", title: "Load balancing", nodes: [["LB", 50, 22], ["App A", 20, 78], ["App B", 80, 78]], links: [[0, 1], [0, 2]],
    caps: ["Requests arrive at the LB", "Round robin sends one to App A", "The next goes to App B"],
    cards: [["Healthy targets", "2 / 2", 100], ["Requests / s", "1.2k", 66]], fc2: ["round robin", "balanced"], fc3: ["GET /ready", "200 OK"] },
  { sid: "cicd", title: "CI pipeline", nodes: [["Commit", 20, 25], ["Build+Test", 78, 25], ["Deploy", 50, 80]], links: [[0, 1], [1, 2]],
    caps: ["A push triggers the workflow", "Cached build, 4 test shards in parallel", "Canary gets 10% of traffic, then 100%"],
    cards: [["Pipeline time", "3m 12s", 40], ["Deploys this week", "27", 85]], fc2: ["on: push", "green"], fc3: ["canary 10% → 100%", "auto-rollback on"] },
  { sid: "dsa", title: "Quick sort", nodes: [["Pivot 5", 50, 22], ["< 5", 20, 78], ["> 5", 80, 78]], links: [[0, 1], [0, 2]],
    caps: ["Pick a pivot from the array", "Smaller values go to the left", "Larger values go right, then recurse"],
    cards: [["Comparisons", "n log n", 55], ["Worst case", "O(n²)", 95]], fc2: ["sorted(nums)", "Timsort"], fc3: ["binary search", "O(log n)"] },
  { sid: "qa", title: "Test pyramid", nodes: [["Unit", 20, 78], ["Integration", 50, 50], ["E2E", 80, 22]], links: [[0, 1], [1, 2]],
    caps: ["Many fast unit tests at the base", "Fewer integration tests in the middle", "A handful of end-to-end journeys on top"],
    cards: [["Branch coverage", "92%", 92], ["Mutation score", "81%", 81]], fc2: ["assert total == 42", "passed"], fc3: ["flaky: 0 of 412", "stable"] },
  { sid: "ds", title: "A/B test", nodes: [["Users", 20, 50], ["Variant A", 78, 25], ["Variant B", 78, 78]], links: [[0, 1], [0, 2]],
    caps: ["Randomly split the traffic", "A converts at 4.1%", "B converts at 4.8%, p = 0.03"],
    cards: [["Lift", "+17%", 70], ["Power", "80%", 80]], fc2: ["p < 0.05", "significant"], fc3: ["median 42 · IQR 18", "no outliers"] },
  { sid: "ml", title: "RAG agent", nodes: [["Question", 20, 25], ["Retriever", 78, 25], ["LLM", 50, 80]], links: [[0, 1], [1, 2]],
    caps: ["The agent reads AGENTS.md and the question", "Retriever finds the 3 best chunks", "The LLM answers, citing its sources"],
    cards: [["Eval pass rate", "94%", 94], ["Tokens per answer", "1.2k", 35]], fc2: ["SKILL.md loaded", "matched"], fc3: ["tool: run_tests", "exit 0"] },
  { sid: "k8s", title: "Autoscaling", nodes: [["Metrics", 20, 25], ["HPA", 80, 25], ["Pods", 50, 80]], links: [[0, 1], [1, 2]],
    caps: ["metrics-server reports 72% CPU", "HPA compares it to the 60% target", "Deployment scales from 2 to 5 pods"],
    cards: [["Replicas", "2 → 5", 80], ["CPU target", "60%", 60]], fc2: ["kubectl get hpa", "scaling"], fc3: ["replicas 5 / 10", "cpu 72%"] },
];
const SCENE_MS = 5000;
const FADE_MS = 450;
let sceneTimers = [];

const curve = ([, x1, y1], [, x2, y2]) => `M${x1 * 2} ${y1 * 1.2} Q${x1 * 2} ${y2 * 1.2} ${x2 * 2} ${y2 * 1.2}`;

function sceneHtml(sc, color) {
  const packets = sc.links.map(([a, b], i) => {
    const [, x0, y0] = sc.nodes[a];
    const [, x1, y1] = sc.nodes[b];
    return `<i class="mf-packet" style="--x0:${x0}%;--y0:${y0}%;--x1:${x1}%;--y1:${y1}%;animation-delay:${i * 0.9}s"></i>`;
  }).join("");
  return `
    <div class="phone-head"><span class="sdot"></span><b>${esc(sc.title)}</b><span class="pill ok" data-step>step 1/${sc.caps.length}</span></div>
    <div class="mini-flow" style="--sc:${color}">
      ${sc.nodes.map(([label, x, y], i) => `<span class="mf-node${i ? "" : " hot"}" style="left:${x}%;top:${y}%">${esc(label)}</span>`).join("")}
      ${packets}
      <svg viewBox="0 0 200 120" preserveAspectRatio="none">${sc.links.map(([a, b]) => `<path d="${curve(sc.nodes[a], sc.nodes[b])}"/>`).join("")}</svg>
    </div>
    <p class="phone-cap" data-cap>${esc(sc.caps[0])}</p>
    ${sc.cards.map(([label, value, pct]) => `<div class="phone-card"><small>${esc(label)}</small><b>${esc(value)}</b><div class="bar"><i style="width:${pct}%"></i></div></div>`).join("")}`;
}

function startScenes(view, subjects) {
  sceneTimers.forEach(clearTimeout);
  sceneTimers = [];
  const stage = view.querySelector(".phone-stage");
  const fc2 = view.querySelector(".fc2");
  const fc3 = view.querySelector(".fc3");
  const dots = view.querySelector(".phone-dots");
  const visual = view.querySelector(".land-visual");
  const phone = view.querySelector(".phone");
  const colorOf = (sid) => subjects.find((s) => s.id === sid)?.accent || "var(--accent)";
  const later = (fn, ms) => sceneTimers.push(setTimeout(() => (document.body.contains(stage) ? fn() : sceneTimers.forEach(clearTimeout)), ms));
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  let layoutFrame = 0;
  const positionFloatCards = () => {
    if (!visual.isConnected || !phone.isConnected) return;
    const cards = [view.querySelector(".fc1"), fc2, fc3];
    if (matchMedia("(max-width: 980px)").matches) {
      cards.forEach((card) => { card.style.left = ""; card.style.right = ""; card.style.maxWidth = ""; });
      return;
    }
    const visualRect = visual.getBoundingClientRect();
    const viewportWidth = document.documentElement.clientWidth;
    const phoneLeft = visualRect.left + phone.offsetLeft;
    const phoneRight = phoneLeft + phone.offsetWidth;
    const overlap = Math.max(8, Math.min(18, visualRect.width * .018));
    const setScreenLeft = (card, screenLeft) => {
      card.style.left = `${screenLeft - visualRect.left}px`;
      card.style.right = "auto";
    };
    [cards[0], cards[2]].forEach((card) => {
      const available = Math.max(140, phoneLeft - visualRect.left + overlap - 16);
      card.style.maxWidth = `${available}px`;
      const width = card.getBoundingClientRect().width;
      setScreenLeft(card, Math.max(16, phoneLeft + overlap - width));
    });
    const rightSpace = Math.max(140, viewportWidth - phoneRight + overlap - 16);
    fc2.style.maxWidth = `${rightSpace}px`;
    setScreenLeft(fc2, phoneRight - overlap);
  };
  const scheduleCardLayout = () => {
    cancelAnimationFrame(layoutFrame);
    layoutFrame = requestAnimationFrame(positionFloatCards);
  };
  const cardObserver = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(scheduleCardLayout);
  [visual, phone, fc2, fc3, view.querySelector(".fc1")].forEach((el) => cardObserver?.observe(el));
  window.addEventListener("resize", scheduleCardLayout);

  const paint = (k) => {
    const sc = SCENES[k];
    stage.innerHTML = sceneHtml(sc, colorOf(sc.sid));
    fc2.innerHTML = `<code>${esc(sc.fc2[0])}</code><span class="pill ok">✓ ${esc(sc.fc2[1])}</span>`;
    fc3.innerHTML = `<code>${esc(sc.fc3[0])}</code><span class="muted">${esc(sc.fc3[1])}</span>`;
    scheduleCardLayout();
    dots.innerHTML = SCENES.map((_, i) => `<i class="${i === k ? "on" : ""}"></i>`).join("");
    const nodes = stage.querySelectorAll(".mf-node");
    sc.caps.forEach((cap, i) => i && later(() => {
      nodes.forEach((n, j) => n.classList.toggle("hot", j === i));
      stage.querySelector("[data-step]").textContent = `step ${i + 1}/${sc.caps.length}`;
      stage.querySelector("[data-cap]").textContent = cap;
    }, (SCENE_MS / sc.caps.length) * i));
  };

  const show = (k) => {
    paint(k);
    [stage, fc2, fc3].forEach((el) => el.classList.remove("out"));
    if (still) return;
    later(() => {
      [stage, fc2, fc3].forEach((el) => el.classList.add("out"));
      later(() => show((k + 1) % SCENES.length), FADE_MS);
    }, SCENE_MS);
  };
  show(0);
  scheduleCardLayout();
  return () => {
    cardObserver?.disconnect();
    window.removeEventListener("resize", scheduleCardLayout);
    cancelAnimationFrame(layoutFrame);
  };
}

export function renderLanding(view, subjects, progress, staticRoot) {
  const totals = subjects.reduce((a, s) => ({ topics: a.topics + s.topics, qs: a.qs + s.questions, done: a.done + progress(s.id) }), { topics: 0, qs: 0, done: 0 });
  const pct = (s) => Math.round((progress(s.id) / Math.max(1, s.topics)) * 100);
  const groupedSubjects = subjects.reduce((groups, s) => {
    const domain = s.domain || "Technology & Engineering";
    (groups[domain] ||= []).push(s);
    return groups;
  }, {});
  const subjectSections = Object.entries(groupedSubjects).map(([domain, group]) => {
    const domainId = domain === "Music & Instruments" ? "music" : "engineering";
    return `
    <section class="subject-domain" data-domain-section="${domainId}"${domainId === "music" ? " hidden" : ""}>
      <div class="land-title"><h3 class="domain-heading">${domainId === "music" ? `<img src="${staticRoot}img/music-logo.webp" alt="" width="32" height="32" loading="lazy" decoding="async">` : ""}${esc(domain)}</h3><span class="muted">${domainId === "music" ? "Learn instruments, listening, and the language of music." : "Explore software, infrastructure, and engineering."}</span></div>
      <div class="subject-grid">${group.map((s, k) => `
        <div class="lift-slot"><a class="subject-card glass spot" href="#/${s.id}" style="--a1:${s.art[0]};--a2:${s.art[1]};--a3:${s.art[2]};--d:${k * 70}ms">
          <div class="s-art">
            <i class="s-blob b1"></i><i class="s-blob b2"></i><i class="s-blob b3"></i>
            <div class="s-icon">${subjectIcon(s, staticRoot, { loading: "lazy" })}</div>
            ${pct(s) ? `<span class="s-badge">${pct(s)}%</span>` : ""}
          </div>
          <div class="s-body">
            <h3>${esc(s.name)}</h3>
            <p>${esc(s.tagline)}</p>
            <div class="s-stats">
              <div><b>${s.topics}</b><span>topics</span></div>
              <div><b>${s.questions}</b><span>questions</span></div>
              <div><b>5</b><span>games</span></div>
            </div>
            <div class="s-tabs">${[s.tabs.lab, s.tabs.playground].map((t) => `<span>${esc(t)}</span>`).join("")}</div>
            <div class="s-progress"><i style="width:${pct(s)}%"></i></div>
            <div class="s-foot"><span class="muted">${progress(s.id)} / ${s.topics} learned</span><span class="s-go">${progress(s.id) ? "Continue" : "Start"} →</span></div>
          </div>
        </a></div>`).join("")}</div>
    </section>`;
  }).join("");
  const last = store.get("last-visit", null);
  const lastSubject = last && subjects.find((s) => s.id === last.sid);

  view.innerHTML = `
    <div class="landing">
      <div class="orbs" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
      <section class="land-hero">
        <div class="land-copy">
          <span class="glass-chip">Interactive · Basic → Advanced · Interview-ready</span>
          <h1>Learn <span class="grad">something new</span><br>one step at a time.</h1>
          <p class="lead">Explore technology and music through guided lessons, hands-on practice, and clear paths from your first steps to deeper skills.</p>
          <div class="row land-cta">
            ${lastSubject ? `<a class="btn primary" href="#/${lastSubject.id}${last.topic ? `/topic/${esc(last.topic)}` : ""}">Continue ${esc(lastSubject.name)}</a>` : `<a class="btn primary" href="#subjects" data-scroll>Choose a subject</a>`}
            <a class="btn glass-btn" href="#/${subjects[0].id}">Start with ${esc(subjects[0].name)}</a>
          </div>
          <div class="land-stats">
            <div><b data-count="subjects">0</b><span>subjects</span></div>
            <div><b data-count="topics">0</b><span>animated topics</span></div>
            <div><b data-count="questions">0</b><span>interview Qs</span></div>
            <div><b data-count="labs">0</b><span>labs & playgrounds</span></div>
            <div><b data-count="games">0</b><span>mini-games</span></div>
            <div><b data-count="puzzles">0</b><span>crossword terms</span></div>
          </div>
        </div>
        <div class="land-visual" aria-hidden="true">
          <div class="phone glass">
            <div class="phone-notch"></div>
            <div class="phone-stage"></div>
            <div class="phone-dots"></div>
          </div>
          <div class="float-card glass fc1"><small>Your progress</small><b>${totals.done} / ${totals.topics}</b><span>topics learned</span>${currentUser() ? "" : `<button type="button" class="fc-save" data-login>Log in to save your progress</button>`}</div>
          <div class="float-card glass fc2 swap"></div>
          <div class="float-card glass fc3 swap"></div>
        </div>
      </section>

      <section id="subjects" class="land-section">
        <div class="land-title"><h2>Choose what to study</h2><span class="muted">Choose a field, then pick a focused learning path.</span></div>
        <div class="tabs subject-domain-tabs" role="tablist" aria-label="Top-level categories">
          <button type="button" class="active" role="tab" aria-selected="true" data-domain-filter="engineering">Engineering</button>
          <button type="button" role="tab" aria-selected="false" data-domain-filter="music">Music</button>
          <button type="button" role="tab" aria-selected="false" data-domain-filter="all">All subjects</button>
        </div>
        ${subjectSections}
      </section>

      <section class="land-section">
        <div class="land-title"><h2>Inside every subject</h2></div>
        <div class="pillar-row">
          ${PILLARS.map(([t, d, c], k) => `<div class="pillar glass"><span class="pillar-n tint-${c}">${k + 1}</span><b>${t}</b><p>${d}</p></div>`).join("")}
        </div>
      </section>
      <footer class="land-footer">
        <span class="muted">LearnMotion</span>
        <a class="land-github" href="https://github.com/Rakitic07/LearnMotion" target="_blank" rel="noopener noreferrer" aria-label="LearnMotion on GitHub">
          <svg class="land-github-mark" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
          </svg>
          <span>GitHub</span>
        </a>
        <a href="/admin" class="land-admin">Admin panel</a>
      </footer>
    </div>`;

  const cleanupScenes = startScenes(view, subjects);
  // Keep this aggregate in sync when crossword vocabularies change; importing every game bundle
  // just to display one number made the homepage wait on 31 unnecessary module requests.
  animateLandingCounts(view, {
    subjects: subjects.length,
    topics: totals.topics,
    questions: totals.qs,
    labs: subjects.length * 2,
    games: subjects.length * 5,
    puzzles: 628,
  });

  view.querySelector(".subject-domain-tabs")?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-domain-filter]");
    if (!button) return;
    const filter = button.dataset.domainFilter;
    view.querySelectorAll("[data-domain-filter]").forEach((tab) => {
      const selected = tab === button;
      tab.classList.toggle("active", selected);
      tab.setAttribute("aria-selected", String(selected));
    });
    view.querySelectorAll("[data-domain-section]").forEach((section) => {
      section.hidden = filter !== "all" && section.dataset.domainSection !== filter;
    });
  });

  view.querySelector("[data-login]")?.addEventListener("click", () => openAuth("login"));
  view.querySelector("[data-scroll]")?.addEventListener("click", (e) => {
    e.preventDefault();
    view.querySelector("#subjects").scrollIntoView({ behavior: "smooth" });
  });
  return cleanupScenes;
}

function animateLandingCounts(root, targets) {
  const counters = [...root.querySelectorAll("[data-count]")];
  const duration = 1500;
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const started = performance.now();
  const update = (now) => {
    if (!root.isConnected || !counters.some((counter) => counter.isConnected)) return;
    const progress = reducedMotion ? 1 : Math.min(1, (now - started) / duration);
    const eased = progress * progress * (3 - 2 * progress);
    counters.forEach((counter) => {
      const target = targets[counter.dataset.count] || 0;
      counter.textContent = String(Math.round(target * eased));
    });
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}
