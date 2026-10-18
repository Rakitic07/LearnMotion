export const WORDS = [
  { answer: "JVM", term: "JVM", clue: "Virtual machine that executes bytecode" },
  { answer: "BYTECODE", term: "Bytecode", clue: "Platform-independent instructions in .class files" },
  { answer: "JIT", term: "JIT compiler", clue: "Turns hot methods into native code at runtime" },
  { answer: "JSHELL", term: "JShell", clue: "Java's REPL, added in Java 9" },
  { answer: "HEAP", term: "Heap", clue: "Memory area where objects live" },
  { answer: "METASPACE", term: "Metaspace", clue: "Native memory for class metadata that replaced PermGen in Java 8" },
  { answer: "ZGC", term: "ZGC", clue: "Concurrent collector with sub-millisecond pauses" },
  { answer: "EDEN", term: "Eden", clue: "Young-generation space where new objects are allocated" },
  { answer: "LAMBDA", term: "Lambda", clue: "Anonymous function such as (a, b) -> a + b, added in Java 8" },
  { answer: "STREAM", term: "Stream", clue: "Lazy pipeline of filter, map and collect operations" },
  { answer: "OPTIONAL", term: "Optional", clue: "Container that makes 'maybe absent' return values explicit" },
  { answer: "RECORD", term: "Record", clue: "Data carrier class, final in Java 16" },
  { answer: "SEALED", term: "Sealed", clue: "Modifier that restricts which classes may extend a type (17)" },
  { answer: "PERMITS", term: "permits", clue: "Clause listing the allowed subclasses of a sealed type" },
  { answer: "YIELD", term: "yield", clue: "Returns a value from a block inside a switch expression" },
  { answer: "VAR", term: "var", clue: "Local variable type inference from Java 10" },
  { answer: "TEXTBLOCK", term: "Text block", clue: "Triple-quoted multi-line string, final in Java 15" },
  { answer: "GENERICS", term: "Generics", clue: "Type parameters such as List<String>" },
  { answer: "ERASURE", term: "Type erasure", clue: "Why List<String> and List<Integer> are the same class at runtime" },
  { answer: "WILDCARD", term: "Wildcard", clue: "The ? in List<? extends Number>" },
  { answer: "HASHCODE", term: "hashCode", clue: "Must be overridden together with equals" },
  { answer: "HASHMAP", term: "HashMap", clue: "Bucketed key-value map with O(1) average lookup" },
  { answer: "DEQUE", term: "Deque", clue: "Double-ended queue; ArrayDeque is the go-to stack" },
  { answer: "VOLATILE", term: "volatile", clue: "Keyword that guarantees visibility of a field across threads" },
  { answer: "SYNCHRONIZED", term: "synchronized", clue: "Keyword for a monitor lock with mutual exclusion" },
  { answer: "DEADLOCK", term: "Deadlock", clue: "Two threads each waiting for a lock the other holds" },
  { answer: "VIRTUALTHREAD", term: "Virtual thread", clue: "Lightweight JVM-scheduled thread, final in Java 21" },
  { answer: "CARRIER", term: "Carrier thread", clue: "Platform thread that a virtual thread mounts on" },
  { answer: "SCOPEDVALUE", term: "ScopedValue", clue: "Immutable context sharing, final in Java 25" },
  { answer: "GATHERER", term: "Gatherer", clue: "Custom intermediate stream operation from Java 24" },
  { answer: "MODULE", term: "Module", clue: "Unit of the platform module system introduced in Java 9" },
  { answer: "JEP", term: "JEP", clue: "JDK Enhancement Proposal that describes a new feature" },
  { answer: "LTS", term: "LTS", clue: "Long-term support release such as 17, 21 or 25" },
  { answer: "CHECKED", term: "Checked exception", clue: "Exception the compiler forces you to catch or declare" },
  { answer: "FINALLY", term: "finally", clue: "Block that always runs after try and catch" },
];

export const RUSH = [
  { task: "Immutable list of three strings (Java 9+)", answer: "List.of(\"a\", \"b\", \"c\")", wrong: ["new List(\"a\", \"b\", \"c\")", "Arrays.toList(\"a\", \"b\", \"c\")", "List.add(\"a\", \"b\", \"c\")"] },
  { task: "Data class with x and y, equals and toString generated", answer: "record Point(int x, int y) {}", wrong: ["data class Point(int x, int y)", "struct Point { int x, y; }", "@Data class Point(int x, int y)"] },
  { task: "Infer a local variable's type (Java 10)", answer: "var map = new HashMap<String, Integer>();", wrong: ["auto map = new HashMap<>();", "let map = new HashMap<>();", "val map = HashMap();"] },
  { task: "Collect a stream into an unmodifiable list (Java 16)", answer: "stream.toList()", wrong: ["stream.asList()", "stream.collect()", "List.from(stream)"] },
  { task: "Last element of a list (Java 21)", answer: "list.getLast()", wrong: ["list.last()", "list[-1]", "list.peekLast()"] },
  { task: "Run 10,000 blocking tasks cheaply (Java 21)", answer: "Executors.newVirtualThreadPerTaskExecutor()", wrong: ["Executors.newFixedThreadPool(10_000)", "new Thread[10_000]", "ForkJoinPool.commonPool().block()"] },
  { task: "Bind and test a type in one step (Java 16)", answer: "if (o instanceof String s)", wrong: ["if (o is String s)", "if (String s = o)", "if (o instanceof String) as s"] },
  { task: "Return a value from a block inside a switch expression", answer: "yield value;", wrong: ["return value;", "break value;", "emit value;"] },
  { task: "Multi-line JSON string without escapes (Java 15)", answer: "\"\"\" ... \"\"\"", wrong: ["`...`", "r\"...\"", "@\"...\""] },
  { task: "Close a resource automatically", answer: "try (var in = Files.newBufferedReader(p)) { }", wrong: ["using (in) { }", "with open(p) as in:", "defer in.close();"] },
  { task: "Read a whole file as a String (Java 11)", answer: "Files.readString(path)", wrong: ["File.read(path)", "Files.readAll(path)", "new String(path)"] },
  { task: "Allow only Circle and Square to implement Shape", answer: "sealed interface Shape permits Circle, Square", wrong: ["final interface Shape extends Circle, Square", "interface Shape only Circle, Square", "enum Shape implements Circle, Square"] },
  { task: "Ignore an unused catch parameter (Java 22)", answer: "catch (Exception _)", wrong: ["catch (Exception)", "catch (_)", "catch (Exception ignored?)"] },
  { task: "Batch a stream into lists of 3 (Java 24)", answer: ".gather(Gatherers.windowFixed(3))", wrong: [".batch(3)", ".chunked(3)", ".window(3).collect()"] },
  { task: "Smallest complete program in Java 25", answer: "void main() { IO.println(\"hi\"); }", wrong: ["print(\"hi\")", "fun main() = println(\"hi\")", "static main => \"hi\""] },
  { task: "Count words per length", answer: "Collectors.groupingBy(String::length, Collectors.counting())", wrong: ["Collectors.toMap(String::length)", "Collectors.countBy(String::length)", "stream.groupBy(length).count()"] },
  { task: "Thread-safe counter without locks", answer: "AtomicLong", wrong: ["volatile long", "Long", "synchronized int"] },
  { task: "Pick a low-pause collector for a large heap", answer: "-XX:+UseZGC", wrong: ["-XX:+UseSerialGC", "-Xmx0", "-XX:+DisableGC"] },
  { task: "Size the heap relative to the container limit", answer: "-XX:MaxRAMPercentage=75", wrong: ["-Xmx=container", "-XX:HeapPercent=100", "-Xss75%"] },
  { task: "Share request context safely with virtual threads (Java 25)", answer: "ScopedValue.where(KEY, v).run(task)", wrong: ["ThreadLocal.global(KEY)", "static String context;", "System.setProperty(KEY, v)"] },
];

export const BUGS = [
  {
    symptom: "HashSet keeps two 'equal' points.",
    lang: "java",
    code: `class Point {
    final int x, y;
    Point(int x, int y) { this.x = x; this.y = y; }

    @Override public boolean equals(Object o) {
        return o instanceof Point p && p.x == x && p.y == y;
    }
}`,
    bug: [4, 5],
    why: "equals is overridden but hashCode is not, so equal points land in different buckets. Add hashCode (Objects.hash(x, y)) or simply use record Point(int x, int y).",
  },
  {
    symptom: "ConcurrentModificationException while cleaning a list.",
    lang: "java",
    code: `List<String> names = new ArrayList<>(input);
for (String n : names) {
    if (n.isBlank()) {
        names.remove(n);
    }
}`,
    bug: [3],
    why: "Removing from a list while iterating it with for-each invalidates the iterator. Use names.removeIf(String::isBlank) or an explicit Iterator.remove().",
  },
  {
    symptom: "Strings that look the same are reported as different.",
    lang: "java",
    code: `String a = readInput();
String b = "admin";
if (a == b) {
    grantAccess();
}`,
    bug: [2],
    why: "== compares references, not contents. Use \"admin\".equals(a) (null-safe) or Objects.equals(a, b).",
  },
  {
    symptom: "File handles leak under load until 'Too many open files'.",
    lang: "java",
    code: `String firstLine(Path p) throws IOException {
    BufferedReader in = Files.newBufferedReader(p);
    String line = in.readLine();
    in.close();
    return line;
}`,
    bug: [1, 3],
    why: "If readLine throws, close is skipped. Use try-with-resources: try (var in = Files.newBufferedReader(p)) { return in.readLine(); }.",
  },
  {
    symptom: "The visit counter is lower than the number of requests.",
    lang: "java",
    code: `class Stats {
    private int visits;

    void hit() {
        visits++;
    }
}`,
    bug: [4],
    why: "visits++ is read-modify-write and not atomic, so concurrent requests lose updates. Use AtomicInteger/LongAdder or synchronize the method.",
  },
  {
    symptom: "Pattern switch does not compile: 'this case label is dominated by a preceding case label'.",
    lang: "java",
    code: `return switch (o) {
    case Integer i -> "int " + i;
    case Integer i when i > 100 -> "big " + i;
    case String s -> s;
    default -> "other";
};`,
    bug: [1, 2],
    why: "The unguarded Integer case matches everything the guarded one would, so the guarded case is unreachable. Put the more specific guarded case first.",
  },
  {
    symptom: "Security scan: credentials committed to the repository.",
    lang: "java",
    code: `public class Db {
    private static final String URL = "jdbc:postgresql://db.internal/app";
    private static final String PASSWORD = "EXAMPLE-ONLY-not-a-real-secret";

    Connection open() throws SQLException {
        return DriverManager.getConnection(URL, "app", PASSWORD);
    }
}`,
    bug: [2],
    why: "A hardcoded password is visible to everyone with repo access and stays in Git history. Read it at runtime from the environment or a secret manager (System.getenv(\"DB_PASSWORD\"), Vault, AWS Secrets Manager) and rotate the leaked one.",
  },
  {
    symptom: "Virtual threads do not scale: throughput stays at about 200 requests at a time.",
    lang: "java",
    code: `ExecutorService pool = Executors.newFixedThreadPool(200, Thread.ofVirtual().factory());
for (Request r : requests) {
    pool.submit(() -> handle(r));
}`,
    bug: [0],
    why: "Pooling virtual threads caps concurrency at 200 and defeats their purpose. Use Executors.newVirtualThreadPerTaskExecutor() and limit access to scarce resources with a Semaphore instead.",
  },
  {
    symptom: "Text block output has unexpected leading spaces.",
    lang: "java",
    code: `String html = """
        <p>Hello</p>
    """;`,
    bug: [2],
    why: "Indentation is stripped relative to the least-indented line, and the closing delimiter counts. With the closing quotes further left, four spaces remain before <p>. Align the closing \"\"\" with the content (or use stripIndent).",
  },
];

export const META = {
  rushLabel: "Java Rush",
  rushIntro: "Pick the Java code or API that does the job.",
  rushMono: true,
  bugLabel: "Java Bug Hunt",
  bugNoun: "symptom",
};
