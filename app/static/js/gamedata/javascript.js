export const WORDS = [
  { answer: "PROMISE", term: "Promise", clue: "Represents the eventual result of asynchronous work" },
  { answer: "CLOSURE", term: "Closure", clue: "Function plus the lexical bindings it can still access" },
  { answer: "PROTOTYPE", term: "Prototype", clue: "Object used for inherited property lookup" },
  { answer: "MODULE", term: "ES module", clue: "File boundary with explicit import and export declarations" },
  { answer: "EVENTLOOP", term: "Event loop", clue: "Coordinates tasks, microtasks, rendering and callbacks" },
  { answer: "AWAIT", term: "await", clue: "Pauses an async function until a promise settles" },
  { answer: "BIGINT", term: "BigInt", clue: "Integer type for values beyond Number's safe range" },
  { answer: "DESTRUCTURING", term: "Destructuring", clue: "Syntax for unpacking values into bindings" },
  { answer: "ABORTCONTROLLER", term: "AbortController", clue: "Signals cancellation to APIs such as fetch" },
  { answer: "TEXTCONTENT", term: "textContent", clue: "Sets DOM text without parsing it as HTML" },
];
export const RUSH = [
  { task: "Check a fetch response's HTTP status", answer: "response.ok", wrong: ["response.catch", "response.json.ok", "fetch.status"] },
  { task: "Use a fallback only for null or undefined", answer: "??", wrong: ["||", "&&", "?."] },
  { task: "Add a module's public function", answer: "export function", wrong: ["public function", "module function", "share function"] },
];
export const BUGS = [];
export const META = { rushLabel: "JavaScript Rush", rushIntro: "Choose the language behavior that fits.", rushMono: true, bugLabel: "JavaScript Bug Hunt", bugNoun: "finding" };
