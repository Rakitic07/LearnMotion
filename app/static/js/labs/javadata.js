/** Java release facts and side-by-side code for the Version Explorer. JEP numbers are from openjdk.org/jeps. */

export const RELEASES = [
  { v: 8, date: "Mar 2014", lts: true, theme: "Functional Java", features: [
    ["126", "Lambda expressions", "Pass behaviour as a value: (a, b) -> a + b; method references like String::length."],
    ["107", "Stream API", "Declarative filter / map / reduce pipelines over collections, sequential or parallel."],
    ["150", "java.time", "Immutable LocalDate, Instant, Duration and ZonedDateTime replace Date and Calendar."],
    ["", "Default methods and Optional", "Interfaces can ship method bodies; Optional makes 'maybe absent' explicit."],
    ["", "CompletableFuture", "Composable async pipelines: supplyAsync, thenApply, thenCombine, exceptionally."],
    ["122", "Metaspace replaces PermGen", "Class metadata moves to native memory: no more PermGen OutOfMemoryError."],
  ] },
  { v: 9, date: "Sep 2017", lts: false, theme: "Modules", features: [
    ["261", "Module system (JPMS)", "module-info.java declares requires / exports; the JDK itself is split into modules."],
    ["222", "JShell", "A REPL for Java: try snippets without a class or main method."],
    ["269", "Collection factory methods", "List.of, Set.of, Map.of create compact immutable collections."],
    ["248", "G1 is the default GC", "Region-based, pause-target collector replaces Parallel GC as the default."],
    ["254", "Compact strings", "Latin-1 strings store one byte per char, roughly halving String memory."],
    ["213", "Private interface methods", "Share code between default methods; try-with-resources on effectively final variables."],
  ] },
  { v: 10, date: "Mar 2018", lts: false, theme: "var", features: [
    ["286", "Local-variable type inference", "var list = new ArrayList<String>(); the type is still static, just inferred."],
    ["", "Unmodifiable copies", "List.copyOf, Collectors.toUnmodifiableList, Optional.orElseThrow()."],
    ["307", "Parallel full GC for G1", "G1's worst-case full collection uses all cores."],
    ["310", "Application class-data sharing", "Share pre-parsed classes between JVMs for faster startup."],
  ] },
  { v: 11, date: "Sep 2018", lts: true, theme: "Modern LTS", features: [
    ["321", "HTTP Client", "java.net.http.HttpClient: HTTP/2, async with CompletableFuture, WebSocket."],
    ["330", "Launch single-file programs", "java Hello.java compiles in memory and runs; no javac step."],
    ["323", "var in lambda parameters", "(var a, @NonNull var b) -> ... lets you annotate inferred parameters."],
    ["", "String and Files helpers", "isBlank, strip, lines, repeat; Files.readString / writeString; Predicate.not."],
    ["320", "Java EE and CORBA removed", "JAXB, JAX-WS and friends leave the JDK; add them as dependencies."],
    ["332", "TLS 1.3", "The JSSE stack supports TLS 1.3."],
    ["333", "ZGC (experimental)", "Low-latency collector with sub-millisecond pause goals."],
  ] },
  { v: 12, date: "Mar 2019", lts: false, theme: "Small wins", features: [
    ["325", "Switch expressions (preview)", "First preview of arrow-case switch that returns a value."],
    ["", "Collectors.teeing", "Feed one stream into two collectors and merge the results."],
    ["", "String.indent / transform", "Indent or pipe a string through a function."],
    ["189", "Shenandoah (experimental)", "Concurrent compacting low-pause collector."],
  ] },
  { v: 13, date: "Sep 2019", lts: false, theme: "Previews", features: [
    ["355", "Text blocks (preview)", "First preview of triple-quoted multi-line strings."],
    ["354", "yield in switch (preview)", "Switch expressions gain yield for block bodies."],
    ["353", "New socket implementation", "Legacy Socket API reimplemented on modern internals."],
  ] },
  { v: 14, date: "Mar 2020", lts: false, theme: "Switch expressions", features: [
    ["361", "Switch expressions", "case A, B -> value; no fall-through; yield in blocks; exhaustive over enums."],
    ["358", "Helpful NullPointerExceptions", "Messages name exactly what was null (on by default from 15)."],
    ["359", "Records (preview)", "First preview of data carrier classes."],
    ["305", "Pattern matching for instanceof (preview)", "if (o instanceof String s) without a cast."],
  ] },
  { v: 15, date: "Sep 2020", lts: false, theme: "Text blocks", features: [
    ["378", "Text blocks", "\"\"\" multi-line strings with automatic indentation stripping; formatted() helper."],
    ["377", "ZGC production-ready", "ZGC is no longer experimental."],
    ["379", "Shenandoah production-ready", "Shenandoah is no longer experimental."],
    ["371", "Hidden classes", "Framework-generated classes that cannot be linked by name."],
    ["372", "Nashorn removed", "The JavaScript engine is gone; use GraalJS if needed."],
  ] },
  { v: 16, date: "Mar 2021", lts: false, theme: "Records", features: [
    ["395", "Records", "record Point(int x, int y) {} gives constructor, accessors, equals, hashCode, toString."],
    ["394", "Pattern matching for instanceof", "if (o instanceof String s && !s.isEmpty()) binds s safely."],
    ["", "Stream.toList and mapMulti", "stream.toList() returns an unmodifiable list."],
    ["396", "Strongly encapsulate JDK internals by default", "Illegal reflective access is denied unless opened."],
    ["392", "jpackage", "Build native installers (msi, pkg, deb) for Java apps."],
  ] },
  { v: 17, date: "Sep 2021", lts: true, theme: "Sealed types LTS", features: [
    ["409", "Sealed classes", "sealed interface Shape permits Circle, Square: a closed hierarchy the compiler knows."],
    ["403", "Strongly encapsulate JDK internals", "--illegal-access is gone; internal APIs need explicit --add-opens."],
    ["356", "Enhanced pseudo-random generators", "RandomGenerator interface and new algorithms (LXM family)."],
    ["306", "Always-strict floating point", "strictfp semantics everywhere."],
    ["406", "Pattern matching for switch (preview)", "First preview of type patterns in switch."],
  ] },
  { v: 18, date: "Mar 2022", lts: false, theme: "UTF-8 everywhere", features: [
    ["400", "UTF-8 by default", "Standard APIs use UTF-8 regardless of OS locale: no more mojibake on Windows."],
    ["408", "Simple web server", "jwebserver serves a directory over HTTP for testing and prototyping."],
    ["413", "Code snippets in Javadoc", "@snippet tags with regions, highlighting and external files."],
    ["421", "Finalization deprecated for removal", "Use try-with-resources or Cleaner instead of finalize()."],
    ["416", "Core reflection on method handles", "Reflection reimplemented internally for consistency."],
  ] },
  { v: 19, date: "Sep 2022", lts: false, theme: "Loom previews", features: [
    ["425", "Virtual threads (preview)", "First preview of lightweight JVM-scheduled threads."],
    ["405", "Record patterns (preview)", "First preview of deconstructing records in patterns."],
    ["424", "Foreign function and memory API (preview)", "Call native code without JNI."],
  ] },
  { v: 20, date: "Mar 2023", lts: false, theme: "More previews", features: [
    ["429", "Scoped values (incubator)", "Immutable per-scope context sharing, a ThreadLocal alternative."],
    ["432", "Record patterns (second preview)", "Refinements before finalization."],
    ["433", "Pattern matching for switch (fourth preview)", "Final round before Java 21."],
  ] },
  { v: 21, date: "Sep 2023", lts: true, theme: "Virtual threads LTS", features: [
    ["444", "Virtual threads", "Millions of cheap threads; write blocking code that scales like async."],
    ["431", "Sequenced collections", "getFirst, getLast, reversed, addFirst on List, Deque, LinkedHashSet, LinkedHashMap."],
    ["440", "Record patterns", "if (o instanceof Point(int x, int y)) deconstructs in one step; nests too."],
    ["441", "Pattern matching for switch", "case Circle c ->, case null ->, guards with when, exhaustive over sealed types."],
    ["439", "Generational ZGC", "ZGC with young and old generations for higher throughput."],
    ["452", "Key encapsulation mechanism API", "javax.crypto.KEM for modern key exchange such as DHKEM."],
  ] },
  { v: 22, date: "Mar 2024", lts: false, theme: "Unnamed variables", features: [
    ["456", "Unnamed variables and patterns", "_ for things you must declare but never use: catch (Exception _), case Point(var x, _)."],
    ["454", "Foreign function and memory API", "Panama is final: Linker, Arena and MemorySegment replace most JNI."],
    ["458", "Launch multi-file source programs", "java Main.java can now use other source files in the same tree."],
    ["423", "Region pinning for G1", "No more GC stalls during JNI critical regions."],
  ] },
  { v: 23, date: "Sep 2024", lts: false, theme: "Markdown docs", features: [
    ["467", "Markdown documentation comments", "/// comments written in Markdown instead of HTML."],
    ["474", "ZGC generational by default", "The generational mode becomes the ZGC default."],
    ["471", "sun.misc.Unsafe memory methods deprecated", "Migrate to VarHandle and the FFM API."],
  ] },
  { v: 24, date: "Mar 2025", lts: false, theme: "Gatherers and PQC", features: [
    ["485", "Stream gatherers", "Custom intermediate operations: windowFixed, windowSliding, fold, scan, mapConcurrent."],
    ["484", "Class-File API", "Standard API to parse, generate and transform class files."],
    ["491", "Virtual threads without pinning", "synchronized no longer pins a virtual thread to its carrier."],
    ["496", "ML-KEM", "Post-quantum key encapsulation (FIPS 203) via the KEM API."],
    ["497", "ML-DSA", "Post-quantum digital signatures (FIPS 204)."],
    ["483", "Ahead-of-time class loading and linking", "Faster startup from a training run cache."],
    ["486", "Security Manager permanently disabled", "It can no longer be enabled."],
  ] },
  { v: 25, date: "Sep 2025", lts: true, theme: "On-ramp LTS", features: [
    ["512", "Compact source files and instance main", "void main() { IO.println(\"Hi\"); } is a complete program."],
    ["513", "Flexible constructor bodies", "Validate arguments and set fields before calling super(...)."],
    ["511", "Module import declarations", "import module java.base; imports every exported package."],
    ["506", "Scoped values", "Final: safe, immutable context passing that works with virtual threads."],
    ["519", "Compact object headers", "Object headers shrink to 8 bytes on 64-bit, cutting heap use."],
    ["510", "Key derivation function API", "javax.crypto.KDF for HKDF and future PQC KDFs."],
    ["521", "Generational Shenandoah", "Shenandoah's generational mode becomes a product feature."],
  ] },
];

export const LTS = RELEASES.filter((r) => r.lts).map((r) => r.v);

/** Each task shows how the same job is written across versions; `since` is the release that made the change. */
export const TASKS = [
  {
    id: "hello", title: "Hello, World", group: "Basics",
    versions: [
      { v: 8, note: "A class, a static main and System.out. Compile with javac, then run with java.", code: `// javac Hello.java && java Hello
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, Java");
    }
}` },
      { v: 11, note: "Same code, but JEP 330 lets you skip javac: java Hello.java compiles in memory and runs.", code: `// java Hello.java   (no javac needed, JEP 330)
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, Java");
    }
}` },
      { v: 25, note: "JEP 512: a compact source file. No class, no static, no String[] args; IO.println comes from java.lang.", code: `// java Hello.java
void main() {
    IO.println("Hello, Java");
}` },
    ],
  },
  {
    id: "data-class", title: "Data class: POJO to record", group: "Types",
    versions: [
      { v: 8, note: "Fields, constructor, getters, equals, hashCode and toString, all by hand (or by Lombok).", code: `public final class Point {
    private final int x;
    private final int y;

    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    public int getX() { return x; }
    public int getY() { return y; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Point)) return false;
        Point p = (Point) o;
        return x == p.x && y == p.y;
    }

    @Override
    public int hashCode() { return Objects.hash(x, y); }

    @Override
    public String toString() { return "Point[x=" + x + ", y=" + y + "]"; }
}` },
      { v: 16, note: "JEP 395: a record declares the state; the compiler writes the constructor, accessors x() and y(), equals, hashCode and toString.", code: `public record Point(int x, int y) {}` },
      { v: 17, note: "Records can validate in a compact constructor and add methods; they are still final and shallowly immutable.", code: `public record Point(int x, int y) {
    public Point {
        if (x < 0 || y < 0) throw new IllegalArgumentException("negative coordinate");
    }

    public double distanceTo(Point other) {
        return Math.hypot(x - other.x, y - other.y);
    }
}` },
    ],
  },
  {
    id: "instanceof", title: "Type checks: cast to patterns", group: "Pattern matching",
    versions: [
      { v: 8, note: "Check, then cast, repeating the type name.", code: `if (obj instanceof Point) {
    Point p = (Point) obj;
    int x = p.getX();
    int y = p.getY();
    System.out.println(x + y);
}` },
      { v: 16, note: "JEP 394: instanceof binds a variable when the test succeeds. Usable in && conditions too.", code: `if (obj instanceof Point p && p.x() > 0) {
    int x = p.x();
    int y = p.y();
    System.out.println(x + y);
}` },
      { v: 21, note: "JEP 440: record patterns deconstruct the record directly into its components.", code: `if (obj instanceof Point(int x, int y) && x > 0) {
    System.out.println(x + y);
}` },
      { v: 22, note: "JEP 456: _ ignores components you do not need.", code: `if (obj instanceof Point(int x, _) && x > 0) {
    System.out.println(x);
}` },
    ],
  },
  {
    id: "switch", title: "Switch: statement to expression", group: "Pattern matching",
    versions: [
      { v: 8, note: "A statement: break on every case or fall through by accident; the variable is assigned in each branch.", code: `int letters;
switch (day) {
    case MONDAY:
    case FRIDAY:
    case SUNDAY:
        letters = 6;
        break;
    case TUESDAY:
        letters = 7;
        break;
    default:
        letters = day.name().length();
        break;
}` },
      { v: 14, note: "JEP 361: switch is an expression. Arrow cases never fall through; several labels share one case; yield returns from a block.", code: `int letters = switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> 6;
    case TUESDAY -> 7;
    default -> {
        int n = day.name().length();
        yield n;
    }
};` },
    ],
  },
  {
    id: "sealed", title: "Closed hierarchies: sealed + pattern switch", group: "Pattern matching",
    versions: [
      { v: 8, note: "The compiler cannot know all subtypes, so you need an if-chain and a default that throws.", code: `abstract class Shape {}
final class Circle extends Shape { final double r; Circle(double r) { this.r = r; } }
final class Square extends Shape { final double side; Square(double s) { this.side = s; } }

static double area(Shape s) {
    if (s instanceof Circle) {
        Circle c = (Circle) s;
        return Math.PI * c.r * c.r;
    } else if (s instanceof Square) {
        Square q = (Square) s;
        return q.side * q.side;
    }
    throw new IllegalArgumentException("unknown shape");
}` },
      { v: 17, note: "JEP 409: sealed + permits closes the hierarchy. Records keep each variant to one line.", code: `sealed interface Shape permits Circle, Square {}
record Circle(double r) implements Shape {}
record Square(double side) implements Shape {}

static double area(Shape s) {
    if (s instanceof Circle c) {
        return Math.PI * c.r() * c.r();
    } else if (s instanceof Square q) {
        return q.side() * q.side();
    }
    throw new IllegalArgumentException("unknown shape");
}` },
      { v: 21, note: "JEP 441 + 440: an exhaustive pattern switch. No default: add a new Shape and every switch stops compiling until you handle it.", code: `sealed interface Shape permits Circle, Square {}
record Circle(double r) implements Shape {}
record Square(double side) implements Shape {}

static double area(Shape s) {
    return switch (s) {
        case Circle(double r) -> Math.PI * r * r;
        case Square(double side) -> side * side;
    };
}` },
    ],
  },
  {
    id: "pattern-switch", title: "Switch on any type with guards", group: "Pattern matching",
    versions: [
      { v: 8, note: "An instanceof ladder with manual null handling.", code: `static String describe(Object o) {
    if (o == null) return "null";
    if (o instanceof Integer) {
        Integer i = (Integer) o;
        return i > 100 ? "big number " + i : "number " + i;
    }
    if (o instanceof String) {
        return "text of length " + ((String) o).length();
    }
    return "something else";
}` },
      { v: 21, note: "JEP 441: type patterns, case null, and when guards in one switch.", code: `static String describe(Object o) {
    return switch (o) {
        case null -> "null";
        case Integer i when i > 100 -> "big number " + i;
        case Integer i -> "number " + i;
        case String s -> "text of length " + s.length();
        default -> "something else";
    };
}` },
    ],
  },
  {
    id: "text", title: "Multi-line strings", group: "Strings",
    versions: [
      { v: 8, note: "Concatenation and escaped quotes and newlines.", code: `String json = "{\\n" +
    "  \\"name\\": \\"Ada\\",\\n" +
    "  \\"langs\\": [\\"Java\\", \\"SQL\\"]\\n" +
    "}";` },
      { v: 15, note: "JEP 378: text blocks. Indentation relative to the closing quotes is stripped; quotes need no escaping. formatted() fills placeholders.", code: `String json = """
    {
      "name": "%s",
      "langs": ["Java", "SQL"]
    }
    """.formatted("Ada");` },
    ],
  },
  {
    id: "strings", title: "String helpers", group: "Strings",
    versions: [
      { v: 8, note: "trim only removes ASCII spaces; repeating and blank checks are manual.", code: `boolean blank = s.trim().isEmpty();
String clean = s.trim();
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 3; i++) sb.append("ab");
String repeated = sb.toString();
long lineCount = new BufferedReader(new StringReader(text)).lines().count();` },
      { v: 11, note: "isBlank, Unicode-aware strip, repeat and lines.", code: `boolean blank = s.isBlank();
String clean = s.strip();
String repeated = "ab".repeat(3);
long lineCount = text.lines().count();` },
      { v: 12, note: "indent and transform for fluent formatting.", code: `boolean blank = s.isBlank();
String clean = s.strip();
String repeated = "ab".repeat(3);
long lineCount = text.lines().count();
String block = text.indent(4);
int length = s.transform(String::strip).length();` },
    ],
  },
  {
    id: "collections", title: "Immutable collections", group: "Collections",
    versions: [
      { v: 8, note: "Wrap a mutable list. Arrays.asList is fixed-size but still writable through set().", code: `List<String> langs = Collections.unmodifiableList(Arrays.asList("Java", "Kotlin"));
Map<String, Integer> ports = new HashMap<>();
ports.put("http", 80);
ports.put("https", 443);
ports = Collections.unmodifiableMap(ports);
List<String> upper = names.stream().map(String::toUpperCase).collect(Collectors.toList());` },
      { v: 9, note: "JEP 269: List.of, Set.of, Map.of. Truly immutable and null-hostile.", code: `List<String> langs = List.of("Java", "Kotlin");
Map<String, Integer> ports = Map.of("http", 80, "https", 443);
List<String> upper = names.stream().map(String::toUpperCase).collect(Collectors.toList());` },
      { v: 10, note: "copyOf and toUnmodifiableList make defensive copies one call.", code: `List<String> langs = List.of("Java", "Kotlin");
Map<String, Integer> ports = Map.of("http", 80, "https", 443);
List<String> safe = List.copyOf(incoming);
List<String> upper = names.stream().map(String::toUpperCase).collect(Collectors.toUnmodifiableList());` },
      { v: 16, note: "stream.toList() returns an unmodifiable list directly.", code: `List<String> langs = List.of("Java", "Kotlin");
Map<String, Integer> ports = Map.of("http", 80, "https", 443);
List<String> safe = List.copyOf(incoming);
List<String> upper = names.stream().map(String::toUpperCase).toList();` },
    ],
  },
  {
    id: "sequenced", title: "First and last elements", group: "Collections",
    versions: [
      { v: 8, note: "Every collection type had its own way, and LinkedHashMap had none.", code: `String first = list.get(0);
String last = list.get(list.size() - 1);
String firstInSet = linkedSet.iterator().next();
Map.Entry<String, Integer> firstEntry = linkedMap.entrySet().iterator().next();
List<String> backwards = new ArrayList<>(list);
Collections.reverse(backwards);` },
      { v: 21, note: "JEP 431: SequencedCollection and SequencedMap give one API for encounter order.", code: `String first = list.getFirst();
String last = list.getLast();
String firstInSet = linkedSet.getFirst();
Map.Entry<String, Integer> firstEntry = linkedMap.firstEntry();
List<String> backwards = list.reversed();` },
    ],
  },
  {
    id: "streams", title: "Stream API over the years", group: "Collections",
    versions: [
      { v: 8, note: "filter, map, collect. Stopping early needs a loop.", code: `List<Integer> evens = nums.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n * n)
    .collect(Collectors.toList());` },
      { v: 9, note: "takeWhile and dropWhile for ordered streams; iterate with a stop condition.", code: `List<Integer> evens = nums.stream()
    .takeWhile(n -> n < 100)
    .filter(n -> n % 2 == 0)
    .map(n -> n * n)
    .collect(Collectors.toList());
Stream.iterate(1, n -> n < 1000, n -> n * 2).forEach(System.out::println);` },
      { v: 12, note: "Collectors.teeing runs two collectors in one pass.", code: `List<Integer> evens = nums.stream()
    .takeWhile(n -> n < 100)
    .filter(n -> n % 2 == 0)
    .map(n -> n * n)
    .collect(Collectors.toList());
double avgOfMinMax = nums.stream().collect(Collectors.teeing(
    Collectors.minBy(Integer::compare), Collectors.maxBy(Integer::compare),
    (min, max) -> (min.get() + max.get()) / 2.0));` },
      { v: 16, note: "toList() replaces collect(Collectors.toList()).", code: `List<Integer> evens = nums.stream()
    .takeWhile(n -> n < 100)
    .filter(n -> n % 2 == 0)
    .map(n -> n * n)
    .toList();` },
      { v: 24, note: "JEP 485: gatherers add custom intermediate steps such as fixed windows (batches).", code: `List<Integer> evens = nums.stream()
    .takeWhile(n -> n < 100)
    .filter(n -> n % 2 == 0)
    .map(n -> n * n)
    .toList();
List<List<Integer>> batches = nums.stream().gather(Gatherers.windowFixed(3)).toList();` },
    ],
  },
  {
    id: "batching", title: "Batch a list into chunks", group: "Collections",
    versions: [
      { v: 8, note: "Index arithmetic with subList.", code: `List<List<Integer>> batches = new ArrayList<>();
for (int i = 0; i < nums.size(); i += 3) {
    batches.add(new ArrayList<>(nums.subList(i, Math.min(i + 3, nums.size()))));
}` },
      { v: 24, note: "Gatherers.windowFixed(3) in a pipeline: [1,2,3,4,5] becomes [[1,2,3],[4,5]].", code: `List<List<Integer>> batches = nums.stream()
    .gather(Gatherers.windowFixed(3))
    .toList();` },
    ],
  },
  {
    id: "var", title: "Local type inference", group: "Basics",
    versions: [
      { v: 8, note: "The type is written twice.", code: `Map<String, List<Order>> byCustomer = new HashMap<String, List<Order>>();
for (Map.Entry<String, List<Order>> e : byCustomer.entrySet()) {
    System.out.println(e.getKey());
}
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;` },
      { v: 10, note: "JEP 286: var for locals with initializers. Still statically typed.", code: `var byCustomer = new HashMap<String, List<Order>>();
for (var e : byCustomer.entrySet()) {
    System.out.println(e.getKey());
}
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;` },
      { v: 11, note: "JEP 323: var in lambda parameters, mainly so they can carry annotations.", code: `var byCustomer = new HashMap<String, List<Order>>();
for (var e : byCustomer.entrySet()) {
    System.out.println(e.getKey());
}
BiFunction<Integer, Integer, Integer> add = (@NonNull var a, @NonNull var b) -> a + b;` },
    ],
  },
  {
    id: "http", title: "HTTP GET", group: "I/O and networking",
    versions: [
      { v: 8, note: "HttpURLConnection plus manual stream reading.", code: `URL url = new URL("https://example.com/api");
HttpURLConnection con = (HttpURLConnection) url.openConnection();
con.setRequestMethod("GET");
StringBuilder body = new StringBuilder();
try (BufferedReader in = new BufferedReader(
        new InputStreamReader(con.getInputStream(), StandardCharsets.UTF_8))) {
    String line;
    while ((line = in.readLine()) != null) body.append(line);
}
System.out.println(con.getResponseCode() + " " + body.length());` },
      { v: 11, note: "JEP 321: HttpClient with HTTP/2, builders and body handlers. sendAsync returns a CompletableFuture.", code: `HttpClient client = HttpClient.newHttpClient();
HttpRequest req = HttpRequest.newBuilder(URI.create("https://example.com/api")).build();
HttpResponse<String> res = client.send(req, HttpResponse.BodyHandlers.ofString());
System.out.println(res.statusCode() + " " + res.body().length());` },
      { v: 21, note: "HttpClient is AutoCloseable since 21, and blocking send is cheap on a virtual thread.", code: `try (var client = HttpClient.newHttpClient()) {
    var req = HttpRequest.newBuilder(URI.create("https://example.com/api")).build();
    var res = client.send(req, HttpResponse.BodyHandlers.ofString());
    System.out.println(res.statusCode() + " " + res.body().length());
}` },
    ],
  },
  {
    id: "files", title: "Read and write a text file", group: "I/O and networking",
    versions: [
      { v: 7, note: "Java 7 NIO.2: Path, Files and try-with-resources, but bytes need decoding.", code: `Path path = Paths.get("notes.txt");
String text = new String(Files.readAllBytes(path), StandardCharsets.UTF_8);
Files.write(path, "done".getBytes(StandardCharsets.UTF_8));` },
      { v: 11, note: "Path.of and Files.readString / writeString.", code: `Path path = Path.of("notes.txt");
String text = Files.readString(path);
Files.writeString(path, "done");` },
      { v: 18, note: "JEP 400: the default charset is UTF-8 everywhere, so FileReader and friends no longer depend on the OS locale.", code: `Path path = Path.of("notes.txt");
String text = Files.readString(path);
Files.writeString(path, "done");
try (var reader = new FileReader("notes.txt")) {   // UTF-8 by default
    System.out.println((char) reader.read());
}` },
    ],
  },
  {
    id: "webserver", title: "Serve a folder over HTTP", group: "I/O and networking",
    versions: [
      { v: 8, note: "com.sun.net.httpserver with a hand-written handler.", code: `HttpServer server = HttpServer.create(new InetSocketAddress(8000), 0);
server.createContext("/", exchange -> {
    byte[] body = Files.readAllBytes(Paths.get("site/index.html"));
    exchange.sendResponseHeaders(200, body.length);
    try (OutputStream os = exchange.getResponseBody()) { os.write(body); }
});
server.start();` },
      { v: 18, note: "JEP 408: jwebserver from the command line, or SimpleFileServer from code. Static files only, for testing.", code: `// shell: jwebserver -d /srv/site -p 8000
HttpServer server = SimpleFileServer.createFileServer(
    new InetSocketAddress(8000), Path.of("/srv/site"), SimpleFileServer.OutputLevel.INFO);
server.start();` },
    ],
  },
  {
    id: "npe", title: "Debugging NullPointerException", group: "Basics",
    versions: [
      { v: 8, note: "The message says nothing about which reference was null.", code: `String city = user.getAddress().getCity().toLowerCase();
// Exception in thread "main" java.lang.NullPointerException
//     at App.main(App.java:12)` },
      { v: 14, note: "JEP 358: helpful messages name the null expression (flag in 14, on by default from 15).", code: `String city = user.getAddress().getCity().toLowerCase();
// Exception in thread "main" java.lang.NullPointerException:
//   Cannot invoke "String.toLowerCase()" because the return value of
//   "Address.getCity()" is null` },
    ],
  },
  {
    id: "threads", title: "10,000 concurrent blocking tasks", group: "Concurrency",
    versions: [
      { v: 8, note: "Platform threads are expensive (about 1 MB stack each), so a fixed pool of 200 caps concurrency: 10,000 one-second tasks take about 50 seconds.", code: `ExecutorService pool = Executors.newFixedThreadPool(200);
for (int i = 0; i < 10_000; i++) {
    pool.submit(() -> {
        Thread.sleep(1000);
        return null;
    });
}
pool.shutdown();
pool.awaitTermination(5, TimeUnit.MINUTES);` },
      { v: 21, note: "JEP 444: one virtual thread per task. Blocking parks the virtual thread, not the OS thread, so all 10,000 finish in about one second.", code: `try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 10_000; i++) {
        executor.submit(() -> {
            Thread.sleep(Duration.ofSeconds(1));
            return null;
        });
    }
}   // close() waits for all tasks` },
      { v: 24, note: "JEP 491: synchronized blocks no longer pin virtual threads to carrier threads, so legacy locking code scales too.", code: `try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 10_000; i++) {
        executor.submit(() -> {
            synchronized (lock) {           // no pinning since 24
                Thread.sleep(Duration.ofMillis(1));
            }
            return null;
        });
    }
}` },
    ],
  },
  {
    id: "context", title: "Request context: ThreadLocal to ScopedValue", group: "Concurrency",
    versions: [
      { v: 8, note: "Mutable, must be removed manually, and copied into every child thread if inheritable.", code: `private static final ThreadLocal<String> USER = new ThreadLocal<>();

void handle(Request r) {
    USER.set(r.user());
    try {
        service.process();      // reads USER.get()
    } finally {
        USER.remove();
    }
}` },
      { v: 25, note: "JEP 506: a scoped value is bound for the duration of run() and is immutable inside it. Cheap with millions of virtual threads.", code: `private static final ScopedValue<String> USER = ScopedValue.newInstance();

void handle(Request r) {
    ScopedValue.where(USER, r.user())
        .run(() -> service.process());   // reads USER.get()
}` },
    ],
  },
  {
    id: "unnamed", title: "Variables you do not use", group: "Pattern matching",
    versions: [
      { v: 8, note: "Unused names you are forced to invent.", code: `try {
    int n = Integer.parseInt(input);
} catch (NumberFormatException ignored) {
    System.out.println("not a number");
}
int count = 0;
for (String unused : items) count++;
map.forEach((key, value) -> System.out.println(value));` },
      { v: 22, note: "JEP 456: _ says 'intentionally unused' in catch, loops, lambdas and patterns.", code: `try {
    int n = Integer.parseInt(input);
} catch (NumberFormatException _) {
    System.out.println("not a number");
}
int count = 0;
for (String _ : items) count++;
map.forEach((_, value) -> System.out.println(value));` },
    ],
  },
  {
    id: "ctor", title: "Validate before super()", group: "Types",
    versions: [
      { v: 8, note: "super(...) must be the first statement, so validation hides in a static helper.", code: `class Employee extends Person {
    Employee(String name, int salary) {
        super(validName(name));
        this.salary = salary;
    }

    private static String validName(String name) {
        if (name == null || name.trim().isEmpty()) throw new IllegalArgumentException("name required");
        return name;
    }
}` },
      { v: 25, note: "JEP 513: statements before super(...) may check arguments and assign fields; they just cannot use this.", code: `class Employee extends Person {
    Employee(String name, int salary) {
        if (name == null || name.isBlank()) throw new IllegalArgumentException("name required");
        this.salary = salary;
        super(name);
    }
}` },
    ],
  },
  {
    id: "imports", title: "Imports for a quick script", group: "Basics",
    versions: [
      { v: 8, note: "One import per package you touch.", code: `import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.nio.file.Files;
import java.nio.file.Paths;

public class Report {
    public static void main(String[] args) throws Exception {
        List<String> lines = Files.readAllLines(Paths.get("sales.csv"));
        Map<String, Long> byRegion = lines.stream()
            .collect(Collectors.groupingBy(l -> l.split(",")[0], Collectors.counting()));
        System.out.println(byRegion);
    }
}` },
      { v: 25, note: "JEP 511 + 512: import module brings in every exported package; compact source files import java.base automatically.", code: `import module java.base;   // implicit in a compact source file

void main() throws Exception {
    List<String> lines = Files.readAllLines(Path.of("sales.csv"));
    Map<String, Long> byRegion = lines.stream()
        .collect(Collectors.groupingBy(l -> l.split(",")[0], Collectors.counting()));
    IO.println(byRegion);
}` },
    ],
  },
  {
    id: "time", title: "Dates and times", group: "Basics",
    versions: [
      { v: 7, note: "Mutable Date and Calendar, zero-based months, and a SimpleDateFormat that is not thread-safe.", code: `Calendar cal = Calendar.getInstance();
cal.set(2026, Calendar.OCTOBER, 17);
cal.add(Calendar.DAY_OF_MONTH, 30);
Date due = cal.getTime();
String text = new SimpleDateFormat("yyyy-MM-dd").format(due);` },
      { v: 8, note: "JEP 150: immutable, thread-safe java.time types with clear names.", code: `LocalDate due = LocalDate.of(2026, 10, 17).plusDays(30);
String text = due.format(DateTimeFormatter.ISO_LOCAL_DATE);
long days = ChronoUnit.DAYS.between(LocalDate.now(), due);
Duration timeout = Duration.ofSeconds(30);` },
    ],
  },
  {
    id: "lambdas", title: "Behaviour as a value", group: "Basics",
    versions: [
      { v: 7, note: "Anonymous inner classes for every callback.", code: `Collections.sort(people, new Comparator<Person>() {
    @Override
    public int compare(Person a, Person b) {
        return a.getAge() - b.getAge();
    }
});
new Thread(new Runnable() {
    public void run() { System.out.println("work"); }
}).start();` },
      { v: 8, note: "JEP 126: lambdas and method references; Comparator gains combinators.", code: `people.sort(Comparator.comparingInt(Person::getAge).thenComparing(Person::getName));
new Thread(() -> System.out.println("work")).start();` },
    ],
  },
];

/** Feature detection rules for the Version Checker: [regex, name, minVersion, JEP, older alternative]. */
export const RULES = [
  [/->|::/, "Lambda or method reference", 8, "126", "anonymous inner class"],
  [/\.stream\(\)|\bStream\.|IntStream|Collectors\./, "Stream API", 8, "107", "for loops"],
  [/\bOptional\b/, "Optional", 8, "", "null checks"],
  [/\b(LocalDate|LocalDateTime|LocalTime|Instant|ZonedDateTime|Duration|ChronoUnit|DateTimeFormatter)\b/, "java.time", 8, "150", "Date / Calendar"],
  [/\bCompletableFuture\b/, "CompletableFuture", 8, "", "Future + callbacks"],
  [/\binterface\b[\s\S]*\bdefault\s+[\w<>[\],\s]+\s+\w+\s*\(/, "Default interface method", 8, "", "abstract base class"],
  [/\b(List|Set|Map)\.of(Entries)?\(/, "Collection factory (List.of / Map.of)", 9, "269", "Collections.unmodifiableList(Arrays.asList(...))"],
  [/\.(takeWhile|dropWhile)\(|Stream\.ofNullable|\.ifPresentOrElse\(/, "Stream / Optional additions", 9, "", "manual loops"],
  [/^\s*(open\s+)?module\s+[\w.]+\s*\{/m, "module-info declaration", 9, "261", "classpath only"],
  [/\bvar\s+[a-zA-Z_$][\w$]*\s*[=:]/, "Local variable type inference (var)", 10, "286", "explicit type"],
  [/\b(List|Set|Map)\.copyOf\(|toUnmodifiable(List|Set|Map)\b|\.orElseThrow\(\)/, "Unmodifiable copies / orElseThrow()", 10, "", "Collections.unmodifiableList(new ArrayList<>(x))"],
  [/\(\s*(@\w+\s+)*var\s+\w+\s*[,)][^;{]*->/, "var in lambda parameters", 11, "323", "implicit lambda parameters"],
  [/\b(HttpClient|HttpRequest|HttpResponse)\b/, "java.net.http HttpClient", 11, "321", "HttpURLConnection"],
  [/\.(isBlank|strip|stripLeading|stripTrailing)\(\)|"\s*\.repeat\(/, "String isBlank / strip / repeat", 11, "", "trim() / StringBuilder loop"],
  [/Files\.(readString|writeString)\(|\bPath\.of\(/, "Files.readString / Path.of", 11, "", "new String(Files.readAllBytes(p), UTF_8) / Paths.get"],
  [/Predicate\.not\(/, "Predicate.not", 11, "", "x -> !test(x)"],
  [/Collectors\.teeing\(/, "Collectors.teeing", 12, "", "two passes"],
  [/\.(indent|transform)\(/, "String.indent / transform", 12, "", "manual formatting"],
  [/(=|return|\()\s*switch\s*\(|\bcase\s+[^:;]*->|\byield\b/, "Switch expression", 14, "361", "switch statement with break"],
  [/"""/, "Text block", 15, "378", "concatenated strings with \\n"],
  [/\.formatted\(/, "String.formatted", 15, "", "String.format"],
  [/\brecord\s+[A-Z]\w*\s*(<[^>]*>)?\s*\(/, "Record", 16, "395", "final class with equals/hashCode/toString"],
  [/\binstanceof\s+(final\s+)?[A-Z][\w.]*(<[^>]*>)?\s+[a-z_]\w*/, "Pattern matching for instanceof", 16, "394", "instanceof + cast"],
  [/(?<!Collectors)\.toList\(\)|\.mapMulti\(/, "Stream.toList / mapMulti", 16, "", "collect(Collectors.toList())"],
  [/\bsealed\s+(interface|class|abstract)|\bnon-sealed\b|\bpermits\b/, "Sealed classes", 17, "409", "package-private constructors"],
  [/\bRandomGenerator(Factory)?\b/, "RandomGenerator", 17, "356", "java.util.Random"],
  [/\bSimpleFileServer\b|\bjwebserver\b/, "Simple web server", 18, "408", "com.sun.net.httpserver handler"],
  [/@snippet\b/, "Javadoc @snippet", 18, "413", "<pre>{@code ...}</pre>"],
  [/\b(instanceof|case)\s+[A-Z]\w*(<[^>]*>)?\s*\(/, "Record pattern", 21, "440", "accessor calls after a type pattern"],
  [/\bcase\s+null\b|\bcase\s+[A-Z][\w.]*(<[^>]*>)?\s+[a-z_]\w*\s*(->|when\b|:)|\bwhen\s+[^-]*->/, "Pattern matching for switch", 21, "441", "instanceof chain"],
  [/\btry\s*\(\s*(var|HttpClient)\s+\w+\s*=\s*HttpClient\./, "HttpClient in try-with-resources (AutoCloseable)", 21, "", "no close; rely on GC"],
  [/newVirtualThreadPerTaskExecutor|Thread\.ofVirtual|startVirtualThread/, "Virtual threads", 21, "444", "fixed thread pool / async code"],
  [/\.(getFirst|getLast|removeFirst|removeLast)\(\)|(?<!\))\.reversed\(\)|\b(firstEntry|lastEntry|pollFirstEntry|sequencedKeySet)\(|\bSequenced(Collection|Map|Set)\b/, "Sequenced collections", 21, "431", "get(0) / get(size()-1) (Deque and NavigableMap already had some of these)"],
  [/(?<![\w$])_(?![\w$])/, "Unnamed variable or pattern (_)", 22, "456", "a named, unused variable"],
  [/\b(Arena|MemorySegment|Linker|FunctionDescriptor)\.\w+/, "Foreign Function and Memory API", 22, "454", "JNI"],
  [/^\s*\/\/\/(?!\/)/m, "Markdown doc comment (///)", 23, "467", "/** HTML javadoc */"],
  [/\.gather\(|\bGatherers?\./, "Stream gatherers", 24, "485", "custom collector or loop"],
  [/java\.lang\.classfile|\bClassFile\.of\(/, "Class-File API", 24, "484", "ASM library"],
  [/"ML-KEM|"ML-DSA/, "Post-quantum ML-KEM / ML-DSA", 24, "496 / 497", "classical-only ECDH / ECDSA"],
  [/\bimport\s+module\s+[\w.]+\s*;/, "Module import declaration", 25, "511", "package imports"],
  [/\bScopedValue\b/, "Scoped values", 25, "506", "ThreadLocal"],
  [/\bIO\.(println|print|readln)\(/, "java.lang.IO console helpers", 25, "512", "System.out.println / BufferedReader"],
  [/\bKDF\.getInstance\(/, "Key derivation function API", 25, "510", "manual HKDF"],
];

/** Things that are not (or no longer) available in a standard release. */
export const WARNINGS = [
  [/\bSTR\.|\bFMT\./, "String templates were previewed in 21 and 22 and then withdrawn; they are in no release. Use formatted() or concatenation."],
  [/\bStructuredTaskScope\b/, "Structured concurrency is still a preview API (through Java 25): needs --enable-preview."],
  [/\bStableValue\b/, "Stable values are a preview API in Java 25: needs --enable-preview."],
  [/\binstanceof\s+(int|long|double|float|byte|short|char|boolean)\b|\bcase\s+(int|long|double|float)\s+\w+/, "Primitive types in patterns are a preview feature (23 to 25)."],
  [/SecurityManager|setSecurityManager/, "The Security Manager is permanently disabled since Java 24 (JEP 486)."],
  [/\b(thread|worker|t)\.stop\(\)|Thread\.currentThread\(\)\.stop\(/i, "Thread.stop throws UnsupportedOperationException since Java 20."],
  [/\bvoid\s+finalize\s*\(/, "finalize() is deprecated for removal (JEP 421). Use try-with-resources or Cleaner."],
  [/\bnew\s+(Integer|Long|Double|Float|Short|Byte|Boolean|Character)\s*\(/, "Boxed-primitive constructors are deprecated for removal; use valueOf()."],
  [/javax\.xml\.bind|javax\.xml\.ws|javax\.activation|javax\.annotation\.(PostConstruct|PreDestroy|Resource)\b/, "Java EE modules (JAXB, JAX-WS, javax.annotation) were removed in Java 11 (JEP 320): add them as dependencies."],
  [/\bnashorn\b|"(js|javascript|nashorn)"\)/i, "Nashorn was removed in Java 15 (JEP 372)."],
  [/\bnew\s+URL\s*\(/, "new URL(String) is deprecated since Java 20: use URI.create(s).toURL()."],
];

/** Compact source files: top-level methods without an enclosing class need 25 (JEP 512). */
export const isCompactSource = (src) => /^\s*(void|static\s+void|public\s+static\s+void)\s+main\s*\(/m.test(src) && !/\b(class|interface|enum|record)\s+[A-Z]/.test(src);
/** Statements before super(...) or this(...) inside a constructor need 25 (JEP 513). */
export const hasFlexibleCtor = (src) => /\b[A-Z]\w*\s*\([^)]*\)\s*(throws[\w\s,.]+)?\{(?:[^{}]|\{[^{}]*\})*?;\s*(super|this)\s*\(/.test(src);
