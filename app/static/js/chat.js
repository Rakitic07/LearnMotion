import { $, highlightCode } from "./util.js";

let context = { sid: null, topic: null, subjectName: "", lesson: null };
let turns = [];
let busy = false;
let currentReply = null;
let root;
let signedIn = false;

function setChatStatus(message) {
  const status = $("#chatStatus");
  if (status) status.textContent = message;
}

function setChatReady() {
  const input = $("#chatInput");
  const send = $("#chatSend");
  const enabled = signedIn;
  if (input) input.disabled = !enabled;
  if (send) send.disabled = !enabled || busy;
}

function refreshChatAvailability() {
  const modelLabel = $("#chatModelLabel");
  if (modelLabel) modelLabel.textContent = "OpenRouter free router · model varies";
  // Lesson context is optional: the tutor can still answer general questions
  // from the home page or when no subject is selected.
  setChatReady();
  if (!root?.hidden) setChatStatus(signedIn
    ? "OpenRouter live tutor is ready. Lesson context and messages are sent to the server-side model."
    : "Sign in to use the LearnMotion tutor.");
}

export function setChatContext(sid, topic, subjectName = "", lesson = null) {
  const next = { sid: sid || null, topic: topic || null, subjectName, lesson };
  if (context.sid !== next.sid || context.topic !== next.topic) {
    turns = [];
    const log = $("#chatMessages");
    if (log) log.replaceChildren();
  }
  context = next;
  const title = $("#chatTitle");
  if (title) title.textContent = topic ? "Ask about this chapter" : subjectName ? `Ask about ${subjectName}` : "Ask LearnMotion";
  const label = $("#chatContextLabel");
  if (label) label.textContent = topic ? `Using the current ${subjectName} chapter` : subjectName ? `Using ${subjectName} lesson context` : "General LearnMotion tutor · open a subject for lesson context.";
  refreshChatAvailability();
}

function addMessage(role, text = "", pending = false) {
  const item = document.createElement("div");
  item.className = `chat-message ${role === "user" ? "chat-user" : "chat-assistant"}${pending ? " chat-pending" : ""}`;
  if (role === "user") item.textContent = text;
  else renderAssistantMarkdown(item, text);
  $("#chatMessages").append(item);
  item.scrollIntoView({ block: "nearest" });
  return item;
}

function appendInlineMarkdown(parent, source) {
  const token = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*\n]+\*|_[^_\n]+_|\[[^\]]+\]\(https?:\/\/[^\s)]+\))/g;
  let last = 0;
  for (const match of source.matchAll(token)) {
    parent.append(document.createTextNode(source.slice(last, match.index)));
    const value = match[0];
    let node;
    if (value.startsWith("`")) {
      node = document.createElement("code");
      node.textContent = value.slice(1, -1);
    } else if (value.startsWith("**")) {
      node = document.createElement("strong");
      node.textContent = value.slice(2, -2);
    } else if (value.startsWith("*") || value.startsWith("_")) {
      node = document.createElement("em");
      node.textContent = value.slice(1, -1);
    } else {
      const link = /^\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)$/.exec(value);
      node = document.createElement("a");
      node.href = link[2];
      node.target = "_blank";
      node.rel = "noopener noreferrer";
      node.textContent = link[1];
    }
    parent.append(node);
    last = match.index + value.length;
  }
  parent.append(document.createTextNode(source.slice(last)));
}

function renderAssistantMarkdown(target, markdown) {
  target.replaceChildren();
  const lines = String(markdown || "").replace(/\r\n?/g, "\n").split("\n");
  for (let i = 0; i < lines.length;) {
    const line = lines[i];
    if (!line.trim()) { i++; continue; }
    const fence = /^\s*```\s*([\w.+-]*)\s*$/.exec(line);
    if (fence) {
      const code = [];
      i++;
      while (i < lines.length && !/^\s*```\s*$/.test(lines[i])) code.push(lines[i++]);
      if (i < lines.length) i++;
      const pre = document.createElement("pre");
      pre.className = "chat-code";
      const codeNode = document.createElement("code");
      codeNode.innerHTML = highlightCode(code.join("\n"), fence[1] || "generic");
      pre.append(codeNode);
      target.append(pre);
      continue;
    }
    const heading = /^(#{1,4})\s+(.+?)\s*#*\s*$/.exec(line);
    if (heading) {
      const node = document.createElement(`h${heading[1].length}`);
      appendInlineMarkdown(node, heading[2]);
      target.append(node);
      i++;
      continue;
    }
    if (/^\s*(?:---+|___+|\*\*\*+)\s*$/.test(line)) {
      target.append(document.createElement("hr"));
      i++;
      continue;
    }
    const listItem = /^\s*(?:[-*+]\s+|\d+[.)]\s+)/.test(line);
    if (listItem) {
      const ordered = /^\s*\d+[.)]\s+/.test(line);
      const list = document.createElement(ordered ? "ol" : "ul");
      while (i < lines.length && (ordered ? /^\s*\d+[.)]\s+/.test(lines[i]) : /^\s*[-*+]\s+/.test(lines[i]))) {
        const item = document.createElement("li");
        appendInlineMarkdown(item, lines[i].replace(/^\s*(?:[-*+]\s+|\d+[.)]\s+)/, ""));
        list.append(item);
        i++;
      }
      target.append(list);
      continue;
    }
    if (/^\s*>\s?/.test(line)) {
      const quote = document.createElement("blockquote");
      const paragraph = document.createElement("p");
      while (i < lines.length && /^\s*>\s?/.test(lines[i])) {
        if (paragraph.childNodes.length) paragraph.append(document.createTextNode(" "));
        appendInlineMarkdown(paragraph, lines[i++].replace(/^\s*>\s?/, ""));
      }
      quote.append(paragraph);
      target.append(quote);
      continue;
    }
    const paragraph = document.createElement("p");
    const content = [];
    while (i < lines.length && lines[i].trim() && !/^\s*```/.test(lines[i]) && !/^(#{1,4})\s+/.test(lines[i]) && !/^\s*(?:[-*+]\s+|\d+[.)]\s+)/.test(lines[i]) && !/^\s*>/.test(lines[i])) content.push(lines[i++]);
    appendInlineMarkdown(paragraph, content.join(" "));
    target.append(paragraph);
  }
}

function close() {
  if (!root) return;
  root.hidden = true;
  document.body.classList.remove("gs-locked");
  $("#chatOpen")?.focus({ preventScroll: true });
}

function showSources(message, sources) {
  if (!sources.length) return;
  const list = document.createElement("div");
  list.className = "chat-sources";
  const label = document.createElement("span");
  label.textContent = "Live sources:";
  list.append(label);
  for (const source of sources) {
    const link = document.createElement("a");
    link.href = source.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = source.title;
    list.append(link);
  }
  message.append(list);
}

async function show() {
  root.hidden = false;
  document.body.classList.add("gs-locked");
  setChatStatus(signedIn
    ? "OpenRouter live tutor is ready. Lesson context and messages are sent to the server-side model."
    : "Sign in to use the LearnMotion tutor.");
  setChatReady();
  $("#chatInput").focus();
}

async function submit(event) {
  event.preventDefault();
  if (busy) return;
  const input = $("#chatInput");
  const question = input.value.trim();
  if (!question) return;
  if (!signedIn) {
    setChatStatus("Sign in to use the LearnMotion tutor.");
    return;
  }

  busy = true;
  input.value = "";
  input.style.height = "";
  addMessage("user", question);
  turns.push({ role: "user", content: question });
  turns = turns.slice(-8);
  currentReply = addMessage("assistant", "", true);
  setChatReady();
  setChatStatus("Asking the OpenRouter model…");

  const lessonContext = context.lesson || (context.subjectName
    ? { subject: context.subjectName }
    : { scope: "general LearnMotion guidance; no subject or chapter is selected" });
  try {
    const response = await fetch("/api/chat/live", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-K8s-Playground": "1" },
      body: JSON.stringify({ subject: context.subjectName, lesson: lessonContext, messages: turns.slice(-12) }),
      signal: AbortSignal.timeout(45_000),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok || !payload.ok) throw new Error(payload.error || `Live chat failed (${response.status}).`);
    renderAssistantMarkdown(currentReply, payload.answer);
    currentReply.classList.remove("chat-pending");
    showSources(currentReply, payload.sources || []);
    turns.push({ role: "assistant", content: payload.answer });
    turns = turns.slice(-8);
    const model = String(payload.model || "openrouter/free");
    setChatStatus(`Answered with ${model}.`);
  } catch (error) {
    const message = error?.name === "TimeoutError"
      ? "The tutor took too long to respond. Please try again."
      : error?.message || "Live chat could not answer this request.";
    if (currentReply) {
      currentReply.textContent = message;
      currentReply.classList.remove("chat-pending");
    }
    setChatStatus(`Live chat failed: ${message}`);
  } finally {
    currentReply = null;
    busy = false;
    setChatReady();
  }
}

export function initChat() {
  root = document.createElement("div");
  root.id = "chatDialog";
  root.className = "chat-backdrop";
  root.hidden = true;
  root.innerHTML = `
    <section class="chat-panel clay" role="dialog" aria-modal="true" aria-labelledby="chatTitle">
      <header class="chat-head"><div><span class="chat-kicker" id="chatModelLabel">OpenRouter free router · model varies</span><h2 id="chatTitle">Ask LearnMotion</h2><p id="chatContextLabel" class="muted"></p></div><button type="button" class="chat-close" id="chatClose" aria-label="Close tutor">×</button></header>
      <p id="chatStatus" class="chat-status muted" aria-live="polite">Sign in to use the LearnMotion tutor.</p>
      <div id="chatMessages" class="chat-messages" role="log" aria-live="polite" aria-label="Tutor conversation"></div>
      <form id="chatForm" class="chat-form"><textarea id="chatInput" rows="1" maxlength="700" placeholder="Ask a question about LearnMotion or the current lesson…" required></textarea><button class="btn primary" type="submit" id="chatSend">Ask</button></form>
      <p class="chat-privacy muted">Live chat uses the server-side OpenRouter model and may be rate limited. Lesson context and messages are sent to the provider.</p>
    </section>`;
  document.body.append(root);
  $("#chatOpen").addEventListener("click", show);
  $("#chatClose").addEventListener("click", close);
  root.addEventListener("click", (event) => { if (event.target === root) close(); });
  $("#chatForm").addEventListener("submit", submit);
  $("#chatInput").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      $("#chatForm").requestSubmit();
    }
  });
  $("#chatInput").addEventListener("input", (event) => {
    event.currentTarget.style.height = "auto";
    event.currentTarget.style.height = `${Math.min(event.currentTarget.scrollHeight, 130)}px`;
  });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && !root.hidden) close(); });
  document.addEventListener("lm:auth-state", (event) => {
    signedIn = Boolean(event.detail?.authenticated);
    if (!signedIn && root && !root.hidden) close();
    refreshChatAvailability();
  });
  setChatContext(null, null, "");
  refreshChatAvailability();
}
