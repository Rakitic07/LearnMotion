export const WORDS = [
  { answer: "LIST", term: "list", clue: "Mutable ordered sequence written with square brackets" },
  { answer: "TUPLE", term: "tuple", clue: "Immutable ordered sequence, often used as a record or dict key" },
  { answer: "DICT", term: "dict", clue: "Hash map from keys to values; keeps insertion order" },
  { answer: "SET", term: "set", clue: "Unordered collection of unique, hashable items" },
  { answer: "MUTABLE", term: "Mutable", clue: "Can be changed in place, like a list or dict" },
  { answer: "IMMUTABLE", term: "Immutable", clue: "Cannot change after creation, like str, int or tuple" },
  { answer: "HASHABLE", term: "Hashable", clue: "Has a stable hash, so it can be a dict key or set member" },
  { answer: "ALIAS", term: "Aliasing", clue: "Two names referring to the same object" },
  { answer: "COMPREHENSION", term: "Comprehension", clue: "Concise syntax that builds a list, dict or set from an iterable" },
  { answer: "LAMBDA", term: "lambda", clue: "Anonymous single-expression function" },
  { answer: "ARGS", term: "*args", clue: "Collects extra positional arguments into a tuple" },
  { answer: "KWARGS", term: "**kwargs", clue: "Collects extra keyword arguments into a dict" },
  { answer: "CLOSURE", term: "Closure", clue: "Inner function that remembers variables from its enclosing scope" },
  { answer: "NONLOCAL", term: "nonlocal", clue: "Lets an inner function rebind a variable of the enclosing function" },
  { answer: "LEGB", term: "LEGB", clue: "Name lookup order: Local, Enclosing, Global, Built-in" },
  { answer: "DECORATOR", term: "Decorator", clue: "Function that wraps another function, applied with @" },
  { answer: "WRAPS", term: "functools.wraps", clue: "Copies the name and docstring onto a decorator's wrapper" },
  { answer: "DATACLASS", term: "dataclass", clue: "Decorator that generates __init__, __repr__ and __eq__" },
  { answer: "DUNDER", term: "Dunder method", clue: "Special double-underscore method like __len__" },
  { answer: "INHERITANCE", term: "Inheritance", clue: "A class reusing and extending another class" },
  { answer: "MRO", term: "MRO", clue: "Method resolution order that super() follows" },
  { answer: "ITERATOR", term: "Iterator", clue: "Object with __next__ that raises StopIteration when done" },
  { answer: "GENERATOR", term: "Generator", clue: "Function that yields values lazily, pausing between them" },
  { answer: "YIELD", term: "yield", clue: "Keyword that produces a value and pauses a generator" },
  { answer: "EXCEPTION", term: "Exception", clue: "Error object raised and caught with try/except" },
  { answer: "FINALLY", term: "finally", clue: "Block that always runs, error or not" },
  { answer: "CONTEXTMANAGER", term: "Context manager", clue: "Object used with 'with' that sets up and tears down" },
  { answer: "ASYNC", term: "async def", clue: "Defines a coroutine function" },
  { answer: "AWAIT", term: "await", clue: "Pauses a coroutine until the awaitable finishes" },
  { answer: "COROUTINE", term: "Coroutine", clue: "Function that can suspend and resume, driven by an event loop" },
  { answer: "GIL", term: "GIL", clue: "Lock that lets only one thread run Python bytecode at a time" },
  { answer: "THREAD", term: "Thread", clue: "Concurrent unit sharing memory; great for I/O-bound work" },
  { answer: "PROCESS", term: "Process", clue: "Separate interpreter with its own memory; true CPU parallelism" },
  { answer: "PEP", term: "PEP", clue: "Python Enhancement Proposal, e.g. number 8 for style" },
];

export const RUSH = [
  { task: "Copy a list so changes don't affect the original", answer: "b = a[:]   # or list(a), a.copy()", wrong: ["b = a", "b = &a", "b = a.clone"] },
  { task: "Default argument that is a fresh list each call", answer: "def f(items=None): items = items or []", wrong: ["def f(items=[]):", "def f(items=list):", "def f(items=[].copy):"] },
  { task: "Squares of even numbers in xs", answer: "[x * x for x in xs if x % 2 == 0]", wrong: ["[x * x if x % 2 == 0 for x in xs]", "{x * x for x in xs: x % 2}", "map(x * x, xs if even)"] },
  { task: "Invert a dict d (values become keys)", answer: "{v: k for k, v in d.items()}", wrong: ["d.reverse()", "dict(d.values(), d.keys)", "{k: v for v, k in d}"] },
  { task: "Count word frequencies", answer: "collections.Counter(words)", wrong: ["dict.count(words)", "len(set(words))", "sorted(words).count()"] },
  { task: "Iterate with both index and value", answer: "for i, x in enumerate(xs):", wrong: ["for i, x in xs:", "for i in xs.index():", "for x in range(xs):"] },
  { task: "Iterate two lists in parallel", answer: "for a, b in zip(xs, ys):", wrong: ["for a, b in xs, ys:", "for a, b in merge(xs, ys):", "for a in xs and b in ys:"] },
  { task: "Sort people by age, then name", answer: "sorted(people, key=lambda p: (p.age, p.name))", wrong: ["people.sort(p.age, p.name)", "sorted(people, by='age,name')", "sorted(people).age.name"] },
  { task: "Read a file and always close it", answer: "with open(path) as f:", wrong: ["f = open(path); read; hope", "open(path).autoclose()", "try: open(path)"] },
  { task: "Lazily produce a million numbers", answer: "(n for n in range(10**6))", wrong: ["[n for n in range(10**6)]", "list(range(10**6))", "{n for n in range(10**6)}"] },
  { task: "Keep a function's __name__ inside a decorator", answer: "@functools.wraps(fn)", wrong: ["@staticmethod", "@property", "@fn.keep_name"] },
  { task: "Speed up a CPU-bound loop over 8 cores", answer: "ProcessPoolExecutor", wrong: ["ThreadPoolExecutor", "asyncio.gather", "time.sleep(0)"] },
  { task: "Fetch 100 URLs concurrently with asyncio", answer: "await asyncio.gather(*(fetch(u) for u in urls))", wrong: ["for u in urls: await fetch(u)", "asyncio.run(fetch) * 100", "threading.gather(urls)"] },
  { task: "Catch only missing keys", answer: "except KeyError:", wrong: ["except:", "except Exception: pass", "if error == KeyError:"] },
  { task: "Re-raise with context from the original error", answer: "raise ConfigError('bad') from err", wrong: ["raise err as ConfigError", "throw ConfigError(err)", "return ConfigError"] },
  { task: "Immutable, hashable record with auto __init__", answer: "@dataclass(frozen=True)", wrong: ["@dataclass(mutable=False)", "class P(tuple, dict)", "@freeze"] },
  { task: "Group items by a key without KeyError", answer: "collections.defaultdict(list)", wrong: ["dict.setdefault = list", "collections.OrderedDict(list)", "{}.group()"] },
  { task: "Check identity, not equality", answer: "a is b", wrong: ["a == b", "a === b", "id(a) == b"] },
];

export const BUGS = [
  {
    symptom: "Each new cart already contains items from previous carts.",
    lang: "python",
    code: `def new_cart(items=[]):
    return items

c1 = new_cart()
c1.append("apple")
c2 = new_cart()
print(c2)   # ['apple'] ?!`,
    bug: [0],
    why: "Default values are evaluated once at definition time, so every call shares the same list. Use items=None and create a new list inside the function.",
  },
  {
    symptom: "Changing one row of the board changes all three rows.",
    lang: "python",
    code: `board = [[0] * 3] * 3
board[0][0] = 1
print(board)
# [[1, 0, 0], [1, 0, 0], [1, 0, 0]]`,
    bug: [0],
    why: "Multiplying the outer list repeats a reference to the same inner list. Build independent rows: [[0] * 3 for _ in range(3)].",
  },
  {
    symptom: "All the callbacks print 2 instead of 0, 1 and 2.",
    lang: "python",
    code: `callbacks = []
for i in range(3):
    callbacks.append(lambda: print(i))

for cb in callbacks:
    cb()`,
    bug: [2],
    why: "Closures capture the variable, not its value, and i is 2 when they run. Bind it at definition: lambda i=i: print(i).",
  },
  {
    symptom: "UnboundLocalError: local variable 'count' referenced before assignment.",
    lang: "python",
    code: `count = 0

def hit():
    count += 1
    return count`,
    bug: [3],
    why: "Assigning makes count local to hit(), so reading it first fails. Declare global count (or better, keep state in an object or closure with nonlocal).",
  },
  {
    symptom: "The program skips some items while removing negatives.",
    lang: "python",
    code: `nums = [1, -2, -3, 4, -5]
for n in nums:
    if n < 0:
        nums.remove(n)
print(nums)   # [1, -3, 4]`,
    bug: [3],
    why: "Mutating a list while iterating shifts elements under the iterator, so items are skipped. Build a new list: nums = [n for n in nums if n >= 0].",
  },
  {
    symptom: "The async version is no faster than the sync one.",
    lang: "python",
    code: `import asyncio, time

async def fetch(n):
    time.sleep(1)
    return n

async def main():
    return await asyncio.gather(*(fetch(i) for i in range(5)))`,
    bug: [3],
    why: "time.sleep blocks the whole event loop, so the coroutines run one after another. Use await asyncio.sleep(1) (or an async HTTP client) so they overlap.",
  },
  {
    symptom: "The decorated function's name shows up as 'wrapper' in logs and docs.",
    lang: "python",
    code: `def timed(fn):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        log(fn.__name__, time.perf_counter() - start)
        return result
    return wrapper`,
    bug: [1],
    why: "The wrapper replaces the original's metadata. Decorate it with @functools.wraps(fn) to copy __name__, __doc__ and friends.",
  },
];

export const META = {
  rushLabel: "Python Rush",
  rushIntro: "Pick the idiomatic Python that does the job.",
  rushMono: true,
  bugLabel: "Python Bug Hunt",
  bugNoun: "symptom",
};
