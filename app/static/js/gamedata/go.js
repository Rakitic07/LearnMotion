export const WORDS = [
  { answer: "GOROUTINE", term: "Goroutine", clue: "Lightweight concurrent execution" },
  { answer: "CHANNEL", term: "Channel", clue: "Typed conduit for communication between goroutines" },
  { answer: "INTERFACE", term: "Interface", clue: "A set of method requirements satisfied implicitly" },
  { answer: "POINTER", term: "Pointer", clue: "Value that refers to another value's address" },
  { answer: "SLICE", term: "Slice", clue: "Flexible view over an underlying array" },
  { answer: "CONTEXT", term: "Context", clue: "Carries deadlines and cancellation across calls" },
  { answer: "MODULE", term: "Module", clue: "Versioned collection of Go packages" },
  { answer: "DEFER", term: "Defer", clue: "Schedules a call at function return" },
  { answer: "MUTEX", term: "Mutex", clue: "Protects shared state from concurrent access" },
  { answer: "ERROR", term: "Error", clue: "Explicit returned value describing failure" },
];
export const RUSH = [
  { task: "Go interface satisfaction", answer: "Implicit", wrong: ["Explicit implements", "Runtime only", "Inheritance"] },
  { task: "Channel close owner", answer: "Sender", wrong: ["Any receiver", "Runtime", "All goroutines"] },
  { task: "Context cancellation signal", answer: "ctx.Done()", wrong: ["ctx.Close()", "cancel.All()", "done(ctx)"] },
];
export const BUGS = [];
export const META = { rushLabel: "Go Rush", rushIntro: "Pick the Go behavior or construct.", rushMono: true, bugLabel: "Go Bug Hunt", bugNoun: "finding" };
