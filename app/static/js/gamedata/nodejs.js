export const WORDS = [
  { answer: "EVENTLOOP", term: "Event loop", clue: "Coordinates callbacks, timers and asynchronous work" },
  { answer: "PROMISE", term: "Promise", clue: "Represents a future fulfillment or rejection" },
  { answer: "STREAM", term: "Stream", clue: "Processes data incrementally with backpressure" },
  { answer: "BACKPRESSURE", term: "Backpressure", clue: "Slows a producer to match a consumer" },
  { answer: "WORKER", term: "Worker thread", clue: "Runs CPU-heavy JavaScript off the main event loop" },
  { answer: "ABORT", term: "AbortSignal", clue: "Communicates cancellation to a supported operation" },
  { answer: "MODULE", term: "Module", clue: "A reusable file/package boundary" },
  { answer: "LOCKFILE", term: "Lockfile", clue: "Records exact dependency versions and integrity" },
  { answer: "MIDDLEWARE", term: "Middleware", clue: "Request processing function composed into a chain" },
  { answer: "HEAP", term: "Heap", clue: "Memory area for dynamically allocated objects" },
];
export const RUSH = [{ task: "Node CPU-bound JS blocks what?", answer: "Event loop", wrong: ["DNS only", "Package manager", "TCP handshake"] }, { task: "Stream write returns false", answer: "Wait for drain", wrong: ["Ignore it", "Close process", "Retry synchronously"] }];
export const BUGS = [];
export const META = { rushLabel: "Node.js Rush", rushIntro: "Choose the runtime behavior.", rushMono: true, bugLabel: "Node Bug Hunt", bugNoun: "finding" };
