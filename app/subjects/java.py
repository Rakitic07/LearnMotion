"""Java: from the JVM to virtual threads, with how each feature evolved from Java 8 to 25. No JDK runs on the server, so examples are read-only; the Version Checker lab analyses code statically."""

from ._dsl import ex, flow, node, pkt, qa, step

CATEGORIES = [
    {"id": "basics", "title": "Foundations", "color": "sky", "blurb": "The JVM and object-oriented Java."},
    {"id": "core", "title": "Core APIs", "color": "mint", "blurb": "Collections, generics, lambdas, streams."},
    {"id": "modern", "title": "Modern Java", "color": "peach", "blurb": "Records, sealed types and patterns."},
    {"id": "runtime", "title": "Runtime", "color": "lilac", "blurb": "Exceptions, concurrency, memory and GC."},
    {"id": "versions", "title": "Versions", "color": "lemon", "blurb": "What changed from 8 to 25."},
]

_B = lambda id, label, x, y, tint="sky", sub="", hidden=False: node(id, label, x, y, tint, sub, "box", hidden)
_P = lambda id, label, x, y, tint="lemon", sub="", hidden=False: node(id, label, x, y, tint, sub, "pill", hidden)
_R = lambda id, label, x, y, tint="mint", sub="", hidden=False: node(id, label, x, y, tint, sub, "round", hidden)


def jx(title, level, description, src):
    return ex(title, level, description, "java", src, runnable=False)


TOPICS = [
    {
        "id": "jvm-basics", "title": "JDK, JRE & the JVM", "category": "basics", "level": "basic", "code": "JV",
        "tagline": "Source to bytecode to machine code: javac, class loading and the JIT.",
        "analogy": "A touring play. The script is written once (bytecode); every theatre (JVM on Windows, Linux, macOS) has its own crew that stages it. Scenes performed every night get memorised (JIT compiled) so they run faster.",
        "what": "javac compiles .java source into platform-independent bytecode in .class files (or JARs). The Java Virtual Machine loads classes on demand through class loaders, verifies the bytecode, and executes it, first in the interpreter and then by compiling hot methods to native code with the JIT compilers (C1 for quick compilation, C2 for heavy optimisation, together called tiered compilation). The JDK contains the compiler and tools (javac, jshell, jcmd, jfr); since Java 11 there is no separate JRE download, and jlink builds a trimmed runtime. Memory is split into the heap (objects, managed by the garbage collector), thread stacks, and metaspace (class metadata). Since Java 11 a single file can run directly with java Hello.java, and since 22 multi-file programs too.",
        "use_cases": ["Running the same JAR on any OS.", "Diagnosing slow startup (class loading, JIT warm-up).", "Building small container images with jlink.", "Profiling with Java Flight Recorder."],
        "key_points": [
            "Write once, run anywhere: bytecode targets the JVM, not the CPU.",
            "Hot code is JIT-compiled; benchmarks need warm-up (use JMH).",
            "Heap = objects, stack = frames and local primitives/references, metaspace = classes.",
            "Since Java 9 the JDK is modular; jlink can ship only the modules you use.",
        ],
        "examples": [
            jx("Compile and run", "basic", "The classic two steps, and the Java 11 shortcut.", """
                // Hello.java
                public class Hello {
                    public static void main(String[] args) {
                        System.out.println("Hello from " + System.getProperty("java.version"));
                    }
                }
                // javac Hello.java && java Hello      (Java 8+)
                // java Hello.java                      (Java 11+, JEP 330)
            """),
            jx("Java 25 compact source file", "basic", "JEP 512: no class or static main needed.", """
                // Hello.java, run with: java Hello.java
                void main() {
                    String name = IO.readln("Your name: ");
                    IO.println("Hello, " + name);
                }
            """),
            jx("Inspect the runtime", "intermediate", "Useful JDK tools.", """
                // jshell                          interactive REPL (Java 9+)
                // javap -c Hello                   disassemble bytecode
                // jcmd <pid> VM.flags              flags of a running JVM
                // jcmd <pid> GC.heap_info          heap usage
                // java -XX:+PrintFlagsFinal -version | grep MaxHeapSize
                // jlink --add-modules java.base,java.net.http --output myjre
                Runtime rt = Runtime.getRuntime();
                System.out.printf("cpus=%d max heap=%d MB%n", rt.availableProcessors(), rt.maxMemory() >> 20);
            """),
        ],
        "commands": ["javac Hello.java · java Hello", "java Hello.java (11+)", "jshell", "javap -c Hello", "jcmd <pid> help · jfr"],
        "gotchas": ["Microbenchmarks without warm-up measure the interpreter, not your code.", "Class-version errors (UnsupportedClassVersionError) mean the JVM is older than the compiler target: use --release.", "In containers, set heap with -XX:MaxRAMPercentage rather than a fixed -Xmx guess.", "The PATH java and JAVA_HOME can point at different versions."],
        "interview": [
            qa("basic", "JDK vs JRE vs JVM?", "The JVM executes bytecode. The JRE was the JVM plus standard libraries for running apps. The JDK adds development tools such as javac, jshell and jcmd. Since Java 11 vendors ship the JDK, and jlink creates custom runtimes."),
            qa("basic", "Why is Java platform independent?", "javac produces bytecode for the JVM, not native code for a CPU. Each OS has its own JVM that runs the same bytecode."),
            qa("intermediate", "What does the JIT compiler do?", "It profiles running code and compiles hot methods to optimised native code (C1 quickly, C2 aggressively, with inlining, escape analysis and more), deoptimising if assumptions break."),
            qa("intermediate", "What is the difference between heap and stack?", "Each thread has a stack of frames with local variables and references; it is freed when methods return. Objects live on the shared heap and are reclaimed by the garbage collector."),
            qa("advanced", "How does class loading work?", "Loading, linking (verify, prepare, resolve) and initialisation happen lazily on first use. Loaders delegate parent-first: bootstrap, platform, then application; frameworks add custom loaders for isolation and hot reload."),
        ],
        "related": ["memory-gc", "java-versions"],
        "flow": flow(
            [_B("src", "Hello.java", 10, 50, "slate", "source"), _B("javac", "javac", 30, 50, "sky", "compiler"), _B("cls", "Hello.class", 50, 50, "lemon", "bytecode"),
             _B("cl", "Class loader", 70, 20, "lilac", "load + verify"), _B("int", "Interpreter", 70, 80, "mint", "runs bytecode"), _B("jit", "JIT (C1/C2)", 92, 50, "rose", "native code", True)],
            [("src", "javac"), ("javac", "cls"), ("cls", "cl"), ("cl", "int"), ("int", "jit")],
            [
                step("Compile", "<b>javac</b> turns source into bytecode, once, on any machine.", ["javac", "cls"], [pkt("src", "javac"), pkt("javac", "cls", ".class")]),
                step("Load", "At runtime the class loader reads, verifies and links Hello.class on first use.", ["cl"], [pkt("cls", "cl", "load")]),
                step("Interpret", "Execution starts in the interpreter while the JVM counts method calls and loops.", ["int"], [pkt("cl", "int")]),
                step("JIT", "Hot methods are compiled to native code; the program speeds up as it warms up.", ["jit"], [pkt("int", "jit", "hot")], {"jit": {"hidden": False}}),
            ],
        ),
    },
    {
        "id": "oop-basics", "title": "Classes, Interfaces & OOP", "category": "basics", "level": "basic", "code": "OO",
        "tagline": "Encapsulation, inheritance, polymorphism and equals/hashCode.",
        "analogy": "A car company. The blueprint is the class, each car built from it is an object, 'anything you can drive' is an interface, and a sports model extends the base model, changing how accelerate() feels (overriding).",
        "what": "Java code is organised into classes that bundle state (fields) with behaviour (methods). Encapsulation hides fields behind methods (private plus accessors). A class extends one superclass but can implement many interfaces; interfaces gained default and static methods in Java 8 and private methods in 9. Polymorphism means a variable of an interface type can hold any implementation, and the overridden method of the actual object runs (dynamic dispatch). Every class inherits from Object; if you override equals you must override hashCode consistently, or hash-based collections break. Prefer composition over inheritance, final for classes not designed for extension, and records (16+) for plain data.",
        "use_cases": ["Modelling a domain (Order, Customer).", "Plugging in implementations behind an interface (PaymentGateway).", "Defining value objects with correct equality.", "Template method or strategy patterns."],
        "key_points": [
            "Access: private < package-private < protected < public.",
            "Override equals and hashCode together; keep them consistent with fields used.",
            "Interfaces define capabilities; abstract classes share state and code.",
            "Favour immutability: final fields, no setters, defensive copies.",
        ],
        "examples": [
            jx("Interface and polymorphism", "basic", "Callers depend on the abstraction.", """
                interface Notifier {
                    void send(String to, String message);

                    default void sendAll(List<String> to, String message) {   // Java 8 default method
                        to.forEach(t -> send(t, message));
                    }
                }

                class EmailNotifier implements Notifier {
                    @Override
                    public void send(String to, String message) {
                        System.out.println("email to " + to + ": " + message);
                    }
                }

                Notifier n = new EmailNotifier();      // could be SmsNotifier tomorrow
                n.sendAll(List.of("a@x.io", "b@x.io"), "deploy done");
            """),
            jx("equals and hashCode", "intermediate", "Required for HashMap/HashSet keys.", """
                public final class Money {
                    private final long cents;
                    private final String currency;

                    public Money(long cents, String currency) {
                        this.cents = cents;
                        this.currency = Objects.requireNonNull(currency);
                    }

                    @Override public boolean equals(Object o) {
                        return o instanceof Money m && cents == m.cents && currency.equals(m.currency);   // 16+ pattern
                    }
                    @Override public int hashCode() { return Objects.hash(cents, currency); }
                }
                // Java 16+: record Money(long cents, String currency) {} generates all of this.
            """),
            jx("Composition over inheritance", "advanced", "Wrap instead of extend.", """
                // Fragile: extending HashSet and overriding add/addAll double-counts,
                // because addAll calls add internally.
                class CountingSet<E> {
                    private final Set<E> inner = new HashSet<>();
                    private int added;

                    boolean add(E e) { added++; return inner.add(e); }
                    boolean addAll(Collection<? extends E> c) { added += c.size(); return inner.addAll(c); }
                    int added() { return added; }
                }
            """),
        ],
        "commands": ["class / interface / abstract class", "extends (one) · implements (many)", "@Override", "equals + hashCode + toString", "final · private · static"],
        "gotchas": ["Overloading is chosen at compile time, overriding at runtime.", "Mutable objects used as HashMap keys get lost when their hash changes.", "Calling overridable methods from a constructor sees half-initialised subclasses.", "== compares references for objects; use equals (and never == for Strings)."],
        "interview": [
            qa("basic", "Abstract class vs interface?", "An abstract class can hold state, constructors and any access level, and a class extends only one. An interface defines a contract a class can implement many of; since Java 8 it can have default and static methods, but no instance state."),
            qa("basic", "Overloading vs overriding?", "Overloading: same name, different parameters, resolved at compile time. Overriding: a subclass replaces an inherited method with the same signature, chosen at runtime by the object's class."),
            qa("intermediate", "Why override hashCode when you override equals?", "Hash-based collections first use hashCode to pick a bucket, then equals. Equal objects must have equal hash codes or lookups fail."),
            qa("intermediate", "What is the diamond problem with default methods?", "If a class inherits the same default method from two interfaces, it must override it and may call a specific one with InterfaceA.super.method()."),
        ],
        "related": ["records-sealed", "generics"],
        "flow": flow(
            [_P("iface", "Notifier", 50, 12, "lilac", "interface"), _B("email", "EmailNotifier", 25, 50, "sky"), _B("sms", "SmsNotifier", 75, 50, "mint"),
             _B("caller", "OrderService", 50, 88, "lemon", "Notifier n")],
            [("email", "iface"), ("sms", "iface"), ("caller", "iface")],
            [
                step("Contract", "<b>Notifier</b> says what can be done, not how.", ["iface"]),
                step("Implementations", "Two classes implement it in different ways.", ["email", "sms"], [pkt("email", "iface", "implements"), pkt("sms", "iface", "implements")]),
                step("Depend on the interface", "OrderService only knows Notifier, so you can swap or mock implementations.", ["caller"], [pkt("caller", "iface", "n.send()")]),
                step("Dynamic dispatch", "At runtime the JVM calls the method of the actual object: here EmailNotifier.send.", ["email"], [pkt("iface", "email", "send", "mint")]),
            ],
        ),
    },
    {
        "id": "collections", "title": "Collections Framework", "category": "core", "level": "basic", "code": "CO",
        "tagline": "List, Set, Map, Deque: choosing and using the right one.",
        "analogy": "Storage furniture: a numbered shelf (ArrayList), a chain of linked boxes (LinkedList), a coat check that gives you a ticket for each coat (HashMap), and a bouncer's guest list where names appear once (HashSet).",
        "what": "The Collections Framework provides interfaces (Collection, List, Set, Queue, Deque, Map) and implementations with different trade-offs. ArrayList gives O(1) index access and amortised O(1) append; HashMap and HashSet give average O(1) lookup using hashCode and equals (with tree bins for big collisions since Java 8); TreeMap keeps keys sorted in O(log n); LinkedHashMap keeps insertion or access order (handy for LRU caches); ArrayDeque is the go-to stack and queue. Java 9 added immutable factories (List.of, Map.of), Java 10 copyOf, and Java 21 sequenced collections with getFirst, getLast and reversed. Concurrent variants such as ConcurrentHashMap support safe access from many threads.",
        "use_cases": ["Ordered list of results (ArrayList).", "Deduplication (HashSet).", "Counting by key (HashMap.merge).", "Sorted leaderboard (TreeMap).", "LRU cache (LinkedHashMap with removeEldestEntry)."],
        "key_points": [
            "Default to ArrayList, HashMap, HashSet, ArrayDeque.",
            "List.of / Map.of are immutable and reject nulls.",
            "Modifying a collection while iterating throws ConcurrentModificationException (use removeIf or an Iterator).",
            "HashMap iteration order is unspecified; use LinkedHashMap or TreeMap when order matters.",
        ],
        "examples": [
            jx("The everyday four", "basic", "List, Set, Map and Deque.", """
                List<String> names = new ArrayList<>(List.of("Ada", "Linus", "Grace"));
                names.add("Ada");
                Set<String> unique = new HashSet<>(names);             // [Ada, Linus, Grace]
                Map<String, Integer> ages = new HashMap<>();
                ages.put("Ada", 36);
                ages.putIfAbsent("Linus", 54);
                Deque<Integer> stack = new ArrayDeque<>();
                stack.push(1); stack.push(2);
                System.out.println(stack.pop());                       // 2
            """),
            jx("Counting and grouping", "intermediate", "merge, computeIfAbsent and getOrDefault.", """
                Map<String, Integer> counts = new HashMap<>();
                for (String w : words) counts.merge(w, 1, Integer::sum);

                Map<String, List<Order>> byCustomer = new HashMap<>();
                for (Order o : orders) byCustomer.computeIfAbsent(o.customer(), k -> new ArrayList<>()).add(o);

                int n = counts.getOrDefault("java", 0);
            """),
            jx("LRU cache in a few lines", "advanced", "LinkedHashMap in access order.", """
                class Lru<K, V> extends LinkedHashMap<K, V> {
                    private final int capacity;
                    Lru(int capacity) { super(16, 0.75f, true); this.capacity = capacity; }
                    @Override protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
                        return size() > capacity;
                    }
                }
                var cache = new Lru<String, String>(2);
                cache.put("a", "1"); cache.put("b", "2"); cache.get("a"); cache.put("c", "3");
                System.out.println(cache.keySet());   // [a, c]  ("b" was least recently used)
                System.out.println(cache.firstEntry()); // Java 21 SequencedMap
            """),
        ],
        "commands": ["new ArrayList<>() · List.of(...)", "map.merge(k, 1, Integer::sum)", "map.computeIfAbsent(k, x -> new ArrayList<>())", "list.removeIf(x -> ...)", "list.getFirst() · list.reversed() (21)"],
        "gotchas": ["Arrays.asList is fixed-size: add throws UnsupportedOperationException.", "List.of(...).contains(null) throws NullPointerException.", "LinkedList is rarely faster than ArrayList in practice (poor cache locality).", "Collections.synchronizedMap locks every call; prefer ConcurrentHashMap."],
        "interview": [
            qa("basic", "ArrayList vs LinkedList?", "ArrayList is a resizable array: O(1) random access and cache-friendly iteration, O(n) inserts in the middle. LinkedList is doubly linked: O(1) insert at known nodes but O(n) access and heavy memory use. ArrayList (or ArrayDeque) wins almost always."),
            qa("intermediate", "How does HashMap work?", "It hashes the key (spreading the hashCode bits) to choose a bucket in an array. Collisions are chained in a list, turned into a balanced tree when a bucket grows past 8 (Java 8+). It resizes (doubles) when size exceeds capacity × load factor (0.75)."),
            qa("intermediate", "HashMap vs ConcurrentHashMap vs Hashtable?", "HashMap is not thread-safe. Hashtable synchronises every method (legacy). ConcurrentHashMap allows concurrent reads and fine-grained locked writes with atomic compute and merge, and never throws ConcurrentModificationException."),
            qa("advanced", "What are sequenced collections (Java 21)?", "New interfaces SequencedCollection, SequencedSet and SequencedMap give a uniform API for collections with a defined encounter order: getFirst, getLast, addFirst, addLast, removeFirst, removeLast and reversed views."),
        ],
        "related": ["generics", "lambdas-streams", "concurrency"],
        "flow": flow(
            [_B("key", "\"ada\"", 10, 50, "sky", "key"), _B("hash", "hashCode()", 32, 50, "lemon", "spread bits"), _B("b0", "bucket 0", 62, 15, "slate"),
             _B("b1", "bucket 5", 62, 50, "mint", "ada → 36"), _B("b2", "bucket 9", 62, 85, "slate"), _B("tree", "tree bin", 90, 50, "lilac", ">8 collisions", True)],
            [("key", "hash"), ("hash", "b1"), ("b1", "tree")],
            [
                step("Hash the key", "map.get(\"ada\") calls <b>hashCode()</b> and mixes the bits.", ["key", "hash"], [pkt("key", "hash")]),
                step("Pick a bucket", "hash & (capacity - 1) selects bucket 5.", ["b1"], [pkt("hash", "b1", "index 5")]),
                step("Compare with equals", "Entries in the bucket are compared with <b>equals()</b> until a match is found: O(1) on average.", ["b1"], set={"b1": {"sub": "found: 36"}}),
                step("Collisions", "If one bucket gets more than 8 entries, it becomes a red-black tree: O(log n) worst case.", ["tree"], [pkt("b1", "tree", "treeify")], {"tree": {"hidden": False}}),
            ],
        ),
    },
    {
        "id": "generics", "title": "Generics", "category": "core", "level": "intermediate", "code": "GN",
        "tagline": "Type parameters, bounded types, wildcards and erasure.",
        "analogy": "Labelled storage boxes. A box labelled 'Books' (List<Book>) lets the warehouse reject a sandwich at the door instead of discovering it later. After shipping, the labels are peeled off (type erasure): the truck only sees boxes.",
        "what": "Generics let classes and methods work with any type while keeping compile-time type safety: List<String> only accepts strings and get() returns String without a cast. Type parameters can be bounded (<T extends Comparable<T>>). Wildcards make APIs flexible: ? extends T for producers you read from, ? super T for consumers you write to (PECS). Generics are implemented by erasure: at runtime List<String> and List<Integer> are both just List, so you cannot do new T(), instanceof List<String> or create generic arrays, and primitives must be boxed. The diamond operator (<>) infers type arguments (Java 7, anonymous classes since 9), and var (10) infers local variable types.",
        "use_cases": ["Type-safe collections and caches.", "Reusable utilities like max(Collection<T>).", "Repository<T, ID> in data layers.", "Fluent builders and Optional<T>."],
        "key_points": [
            "PECS: Producer Extends, Consumer Super.",
            "Type erasure: no runtime generic type info (except in signatures via reflection).",
            "Avoid raw types; they disable checks.",
            "Generic methods declare their own <T> before the return type.",
        ],
        "examples": [
            jx("A generic class and method", "basic", "Type-safe container and a bounded method.", """
                record Pair<A, B>(A first, B second) {}

                static <T extends Comparable<T>> T max(List<T> items) {
                    T best = items.get(0);
                    for (T t : items) if (t.compareTo(best) > 0) best = t;
                    return best;
                }

                Pair<String, Integer> p = new Pair<>("age", 36);
                int biggest = max(List.of(3, 9, 4));        // T inferred as Integer
            """),
            jx("Wildcards (PECS)", "intermediate", "Read from extends, write to super.", """
                static double sum(Collection<? extends Number> nums) {   // producer
                    double s = 0;
                    for (Number n : nums) s += n.doubleValue();
                    return s;
                }

                static void fill(List<? super Integer> out) {            // consumer
                    for (int i = 0; i < 3; i++) out.add(i);
                }

                sum(List.of(1, 2.5, 3L));
                List<Number> target = new ArrayList<>();
                fill(target);
            """),
            jx("Erasure in practice", "advanced", "Why some things do not compile.", """
                List<String> a = new ArrayList<>();
                List<Integer> b = new ArrayList<>();
                System.out.println(a.getClass() == b.getClass());   // true: both ArrayList

                // new T()                 -> not allowed: pass a Supplier<T> instead
                // obj instanceof List<String> -> not allowed (List<?> is fine)
                static <T> T create(Supplier<T> factory) { return factory.get(); }
                StringBuilder sb = create(StringBuilder::new);
            """),
        ],
        "commands": ["class Box<T> { }", "static <T> T first(List<T> xs)", "<T extends Comparable<T>>", "? extends T · ? super T", "new HashMap<>() (diamond)"],
        "gotchas": ["List<Integer> is not a List<Number>, even though Integer is a Number.", "Raw types compile with warnings and can cause heap pollution.", "Overloads that differ only in generic parameters clash after erasure.", "Boxing in generic collections costs memory and can NPE on unboxing null."],
        "interview": [
            qa("intermediate", "What is type erasure?", "The compiler checks generic types, then replaces type parameters with their bounds (Object by default) and inserts casts. At runtime the generic arguments are gone, which keeps compatibility with pre-generics code."),
            qa("intermediate", "Explain ? extends vs ? super.", "? extends T accepts T or subtypes: safe to read as T, cannot add (except null). ? super T accepts T or supertypes: safe to add T, reads come back as Object. Mnemonic PECS."),
            qa("intermediate", "Why is List<Integer> not a subtype of List<Number>?", "If it were, you could add a Double through the List<Number> reference into a list of integers. Generics are invariant to prevent this; wildcards express safe variance."),
            qa("advanced", "How can you create a generic array or instance?", "Not directly because of erasure. Pass a Class<T> or Supplier<T>, use IntFunction<T[]> (as in toArray(String[]::new)), or use a List instead."),
        ],
        "related": ["collections", "lambdas-streams"],
        "flow": flow(
            [_B("src", "List<String> names", 15, 30, "sky", "source"), _B("chk", "javac type check", 45, 30, "mint", "names.add(42)? error"), _B("erase", "Erasure", 75, 30, "lemon", "List, casts inserted"),
             _B("rt", "Runtime", 75, 80, "lilac", "just ArrayList")],
            [("src", "chk"), ("chk", "erase"), ("erase", "rt")],
            [
                step("Declare", "The type argument documents and constrains what the list holds.", ["src"]),
                step("Compile-time safety", "Adding an Integer fails at compile time, not at runtime.", ["chk"], [pkt("src", "chk", "add(42)", "rose")], {"chk": {"sub": "error: incompatible types"}}),
                step("Erasure", "javac removes type arguments and inserts a cast where you read: (String) names.get(0).", ["erase"], [pkt("chk", "erase")]),
                step("Runtime", "The JVM sees a plain ArrayList: List<String>.class does not exist.", ["rt"], [pkt("erase", "rt")]),
            ],
        ),
    },
    {
        "id": "lambdas-streams", "title": "Lambdas & Streams", "category": "core", "level": "intermediate", "code": "LS",
        "tagline": "Functional interfaces, method references, pipelines and collectors.",
        "analogy": "An assembly line. Items ride a conveyor (stream); stations filter out defects, repaint (map) and box results (collect). Nothing moves until someone at the end asks for boxes (lazy terminal operation).",
        "what": "Java 8 introduced lambdas: concise implementations of functional interfaces (one abstract method) such as Function, Predicate, Supplier, Consumer and Comparator. Method references (String::length, this::save) are shorthand for lambdas. Streams describe data pipelines: a source (collection.stream()), lazy intermediate operations (filter, map, flatMap, sorted, distinct) and one terminal operation (collect, toList, reduce, forEach, count) that triggers processing. Collectors build maps and groups (groupingBy, partitioningBy, joining, toMap). Later releases added takeWhile and dropWhile (9), teeing (12), toList and mapMulti (16), and gatherers for custom intermediate steps (24). Lambdas can capture only effectively final local variables. Parallel streams split work over the common ForkJoinPool; only use them for large CPU-bound workloads.",
        "use_cases": ["Transforming and filtering collections.", "Grouping and aggregating data in memory.", "Passing behaviour such as comparators and callbacks.", "Batch processing with gatherers (24)."],
        "key_points": [
            "Streams are lazy and single-use.",
            "Prefer stateless, side-effect-free lambdas.",
            "Collectors.toMap throws on duplicate keys unless you pass a merge function.",
            "stream.toList() (16) is unmodifiable; Collectors.toList() makes no guarantee.",
        ],
        "examples": [
            jx("From loop to pipeline", "basic", "Same logic, two styles.", """
                // Before Java 8
                List<String> result = new ArrayList<>();
                for (User u : users) {
                    if (u.isActive()) result.add(u.getEmail().toLowerCase());
                }
                Collections.sort(result);

                // Java 8+  (Java 16+: .toList())
                List<String> emails = users.stream()
                    .filter(User::isActive)
                    .map(u -> u.getEmail().toLowerCase())
                    .sorted()
                    .collect(Collectors.toList());
            """),
            jx("Grouping and statistics", "intermediate", "Collectors do the heavy lifting.", """
                Map<String, Long> ordersPerCity = orders.stream()
                    .collect(Collectors.groupingBy(Order::city, Collectors.counting()));

                Map<Boolean, List<Order>> bigOrNot = orders.stream()
                    .collect(Collectors.partitioningBy(o -> o.total() > 1000));

                DoubleSummaryStatistics stats = orders.stream().mapToDouble(Order::total).summaryStatistics();
                String csv = names.stream().collect(Collectors.joining(", ", "[", "]"));
            """),
            jx("Evolution of the API", "advanced", "takeWhile (9), teeing (12), toList (16), gatherers (24).", """
                var firstSmall = nums.stream().takeWhile(n -> n < 10).toList();          // 9 + 16

                var range = nums.stream().collect(Collectors.teeing(                         // 12
                    Collectors.minBy(Integer::compare),
                    Collectors.maxBy(Integer::compare),
                    (min, max) -> max.get() - min.get()));

                var batches = nums.stream().gather(Gatherers.windowFixed(3)).toList();      // 24
                var running = nums.stream().gather(Gatherers.scan(() -> 0, Integer::sum)).toList();
            """),
        ],
        "commands": ["x -> x * 2 · (a, b) -> a + b", "String::length · ArrayList::new", ".filter().map().toList()", "Collectors.groupingBy(f, counting())", "Optional.ofNullable(x).map(...).orElse(d)"],
        "gotchas": ["Reusing a consumed stream throws IllegalStateException.", "peek is for debugging; do not rely on it for side effects.", "Parallel streams on small or I/O-bound work are slower and share one pool.", "Checked exceptions do not fit Function: wrap them or use a loop."],
        "interview": [
            qa("basic", "What is a functional interface?", "An interface with exactly one abstract method (it may have default and static methods), so a lambda or method reference can implement it. @FunctionalInterface makes the compiler check this."),
            qa("intermediate", "Intermediate vs terminal operations?", "Intermediate operations (filter, map, sorted) return a new lazy stream. A terminal operation (collect, forEach, reduce, count) runs the pipeline and closes the stream."),
            qa("intermediate", "map vs flatMap?", "map transforms each element into exactly one element. flatMap transforms each element into a stream and flattens them, for example orders to their line items."),
            qa("advanced", "When should you use parallel streams?", "For large, CPU-bound, easily splittable workloads (arrays, ArrayList, ranges) with stateless operations, after measuring. Avoid them for I/O, small data, ordered or stateful operations, and in servers sharing the common pool."),
            qa("advanced", "What are stream gatherers (Java 24)?", "Gatherers let you define custom intermediate operations with state, early termination and parallel support: stream.gather(Gatherers.windowFixed(3)), windowSliding, fold, scan and mapConcurrent are built in."),
        ],
        "related": ["collections", "generics", "java-versions"],
        "flow": flow(
            [_B("src", "orders.stream()", 10, 50, "slate", "source"), _B("f", "filter(total > 100)", 32, 50, "sky"), _B("m", "map(Order::city)", 54, 50, "lemon"),
             _B("d", "distinct()", 74, 50, "mint"), _B("t", "toList()", 92, 50, "lilac", "terminal")],
            [("src", "f"), ("f", "m"), ("m", "d"), ("d", "t")],
            [
                step("Build the pipeline", "filter, map and distinct only describe the work: nothing runs yet.", ["f", "m", "d"]),
                step("Terminal operation", "<b>toList()</b> pulls elements through the pipeline one at a time.", ["t"], [pkt("src", "f", "order 1"), pkt("f", "m"), pkt("m", "d", "Pune")]),
                step("Short-circuit", "Orders that fail the filter never reach map: work per element is minimal.", ["f"], [pkt("src", "f", "order 2", "rose")], {"f": {"sub": "dropped 2"}}),
                step("Result", "Collected into an unmodifiable list: [Pune, Berlin].", ["t"], [pkt("d", "t", "Berlin")], {"t": {"sub": "[Pune, Berlin]"}}),
            ],
        ),
    },
    {
        "id": "records-sealed", "title": "Records & Sealed Types", "category": "modern", "level": "intermediate", "code": "RS",
        "tagline": "Data carriers in one line and closed hierarchies the compiler understands.",
        "analogy": "A record is a printed form: fixed fields, filled once, and two forms with the same values are the same form. A sealed interface is a menu with a fixed list of dishes: the kitchen (compiler) knows every possible order, so it can check that each one is handled.",
        "what": "Records (final in Java 16, JEP 395) are transparent, shallowly immutable data carriers: record Point(int x, int y) {} gives a canonical constructor, accessors x() and y(), and equals, hashCode and toString based on the components. You can add a compact constructor for validation, static factories and methods, and implement interfaces, but not extend classes or add instance fields. Sealed classes and interfaces (Java 17, JEP 409) restrict which types may extend them with permits; subclasses must be final, sealed or non-sealed. Together they model algebraic data types: a sealed interface of records, deconstructed with record patterns and exhaustive switch (Java 21) so adding a new variant produces compile errors wherever it is not handled.",
        "use_cases": ["DTOs and API responses.", "Value objects (Money, Email).", "Result types: sealed interface Result permits Ok, Err.", "Commands and events in domain models.", "Compound map keys."],
        "key_points": [
            "Records are final, components are private final, accessors have no get prefix.",
            "Validate in the compact constructor; copy mutable inputs (List.copyOf).",
            "Sealed + records + pattern switch = exhaustive handling without default.",
            "Records work well with Jackson (2.12+) and as map keys.",
        ],
        "examples": [
            jx("A record with validation", "basic", "Compact constructor and defensive copy.", """
                public record Order(String id, List<String> items, BigDecimal total) {
                    public Order {
                        Objects.requireNonNull(id, "id");
                        if (total.signum() < 0) throw new IllegalArgumentException("negative total");
                        items = List.copyOf(items);          // keep the record immutable
                    }

                    public boolean isLarge() { return total.compareTo(BigDecimal.valueOf(1000)) > 0; }

                    public static Order empty(String id) { return new Order(id, List.of(), BigDecimal.ZERO); }
                }
            """),
            jx("A sealed result type", "intermediate", "A closed set of outcomes.", """
                public sealed interface Result<T> permits Ok, Err {}
                public record Ok<T>(T value) implements Result<T> {}
                public record Err<T>(String message, int code) implements Result<T> {}

                static String render(Result<User> r) {
                    return switch (r) {                         // Java 21: exhaustive, no default
                        case Ok<User>(var user) -> "Welcome " + user.name();
                        case Err<User>(var msg, var code) when code == 404 -> "Not found";
                        case Err<User>(var msg, var code) -> "Error " + code + ": " + msg;
                    };
                }
            """),
            jx("Before and after", "intermediate", "Java 8 value class vs Java 16 record.", """
                // Java 8: about 30 lines of constructor, getters, equals, hashCode, toString
                // Java 16+:
                record Point(int x, int y) {
                    Point withX(int newX) { return new Point(newX, y); }   // 'wither' style
                }
                var p = new Point(1, 2);
                System.out.println(p);                 // Point[x=1, y=2]
                System.out.println(p.equals(new Point(1, 2)));   // true
            """),
        ],
        "commands": ["record Point(int x, int y) {}", "public Point { /* validate */ }", "sealed interface S permits A, B {}", "final / sealed / non-sealed subclasses", "switch (s) { case A a -> ...; case B b -> ...; }"],
        "gotchas": ["Records are shallowly immutable: a List component can still be mutated unless copied.", "Records cannot extend another class (they extend java.lang.Record).", "JPA entities should not be records (they need mutability and proxies); use records for DTOs.", "Permitted subclasses must be in the same module (or package in the unnamed module)."],
        "interview": [
            qa("basic", "What does a record generate?", "A private final field and public accessor per component, a canonical constructor, and equals, hashCode and toString based on all components."),
            qa("intermediate", "Record vs Lombok @Value?", "Records are a language feature with fixed semantics (final, no inheritance, accessors without get), supported by pattern matching and serialisation. Lombok generates code via annotation processing and is more configurable."),
            qa("intermediate", "Why use sealed classes?", "To declare a closed hierarchy. The compiler knows all subtypes, so pattern switches can be checked for exhaustiveness without a default branch, and APIs can prevent unexpected implementations."),
            qa("advanced", "How do records and sealed types model algebraic data types?", "Records are product types (all components together), sealed interfaces are sum types (one of several variants). Combined with record patterns and exhaustive switch (21), you get safe, concise data-oriented programming."),
        ],
        "related": ["pattern-matching", "oop-basics", "java-versions"],
        "flow": flow(
            [_P("shape", "sealed Shape", 50, 12, "lilac", "permits Circle, Square"), _B("c", "record Circle(r)", 25, 50, "sky"), _B("s", "record Square(side)", 75, 50, "mint"),
             _B("sw", "switch (shape)", 50, 85, "lemon", "exhaustive"), _B("t", "record Triangle", 92, 20, "rose", "not permitted", True)],
            [("c", "shape"), ("s", "shape"), ("shape", "sw")],
            [
                step("Closed hierarchy", "<b>permits</b> lists every allowed subtype.", ["shape"]),
                step("Records as variants", "Each variant is a one-line record with its data.", ["c", "s"], [pkt("c", "shape"), pkt("s", "shape")]),
                step("Exhaustive switch", "The compiler checks that Circle and Square are both handled; no default needed.", ["sw"], [pkt("shape", "sw", "2 cases")]),
                step("Blocked", "A new class that is not permitted cannot implement Shape: compile error.", ["t"], set={"t": {"hidden": False}}),
            ],
        ),
    },
    {
        "id": "pattern-matching", "title": "Pattern Matching & Switch", "category": "modern", "level": "advanced", "code": "PM",
        "tagline": "instanceof patterns, switch expressions, record patterns and unnamed _.",
        "analogy": "A mail sorter. Old style: pick up a parcel, check the label, then open it with a separate tool. Pattern matching: one motion checks the label, opens it and hands you exactly the items inside, and a guard says 'only if heavier than 2 kg'.",
        "what": "Pattern matching arrived in steps. Java 14 made switch an expression (arrows, no fall-through, yield, multiple labels). Java 16 added type patterns to instanceof (if (o instanceof String s)). Java 21 finalised pattern matching for switch (type patterns, case null, when guards, exhaustiveness for sealed types) and record patterns that deconstruct records, even nested. Java 22 added unnamed variables and patterns (_) for parts you do not need. Primitive types in patterns are still a preview in 25. The result is data-oriented code: model with records and sealed interfaces, then switch over shapes of data instead of chains of instanceof and casts.",
        "use_cases": ["Parsing JSON-like trees or ASTs.", "Handling result and event types.", "Replacing visitor pattern boilerplate.", "Cleaner equals implementations."],
        "key_points": [
            "Arrow cases never fall through; yield returns from a block case.",
            "Order matters: specific patterns (with guards) before general ones; the compiler flags dominated cases.",
            "Pattern switch throws NullPointerException on null unless you add case null.",
            "Switch over a sealed type without default gets compile errors when a new subtype appears.",
        ],
        "examples": [
            jx("Switch expression (14)", "basic", "A value-returning switch.", """
                String kind = switch (day) {
                    case SATURDAY, SUNDAY -> "weekend";
                    case FRIDAY -> {
                        log("almost there");
                        yield "weekday";
                    }
                    default -> "weekday";
                };
            """),
            jx("Patterns with guards (21)", "intermediate", "Type patterns, null and when.", """
                static String format(Object o) {
                    return switch (o) {
                        case null -> "null";
                        case Integer i when i < 0 -> "negative " + (-i);
                        case Integer i -> "int " + i;
                        case String s when s.isBlank() -> "blank string";
                        case String s -> "\\"" + s + "\\"";
                        case int[] arr -> "int array of " + arr.length;
                        default -> o.toString();
                    };
                }
            """),
            jx("Nested record patterns and _ (21, 22)", "advanced", "Deconstruct a small expression tree.", """
                sealed interface Expr permits Num, Add, Mul, Neg {}
                record Num(int value) implements Expr {}
                record Add(Expr left, Expr right) implements Expr {}
                record Mul(Expr left, Expr right) implements Expr {}
                record Neg(Expr inner) implements Expr {}

                static int eval(Expr e) {
                    return switch (e) {
                        case Num(int v) -> v;
                        case Add(Num(int a), Num(int b)) -> a + b;          // nested pattern fast path
                        case Add(var l, var r) -> eval(l) + eval(r);
                        case Mul(Num(int z), _) when z == 0 -> 0;           // unnamed pattern (22)
                        case Mul(var l, var r) -> eval(l) * eval(r);
                        case Neg(var inner) -> -eval(inner);
                    };
                }
            """),
        ],
        "commands": ["case A, B -> value", "yield value;", "if (o instanceof Point(int x, int y))", "case Circle c when c.r() > 10 ->", "case null, default ->"],
        "gotchas": ["Old colon-style switch still falls through; do not mix styles in one switch.", "A dominated case (Integer i before Integer i when i > 0) does not compile.", "Record patterns call accessors: keep them side-effect free.", "Exhaustiveness relies on sealed hierarchies or enums; otherwise add default."],
        "interview": [
            qa("basic", "What changed with switch expressions?", "switch can produce a value, uses -> cases that never fall through, supports several labels per case, uses yield for block bodies, and must be exhaustive."),
            qa("intermediate", "What does instanceof pattern matching give you?", "Test and bind in one step: if (o instanceof String s) gives a typed variable s scoped to where the test is true, removing the cast and duplication."),
            qa("advanced", "What are record patterns?", "Patterns that match a record type and destructure its components into variables, possibly nesting other patterns: case Line(Point(var x1, var y1), Point p2)."),
            qa("advanced", "How does exhaustiveness checking work with sealed types?", "If the selector's type is sealed and every permitted subtype is covered, no default is needed. Recompiling after adding a subtype fails where it is not handled; at runtime an unexpected subtype throws MatchException."),
        ],
        "related": ["records-sealed", "java-versions"],
        "flow": flow(
            [_B("obj", "Object o", 10, 50, "slate", "Add(Num 2, Num 3)"), _P("c1", "case Num(int v)", 45, 15, "sky"), _P("c2", "case Add(Num a, Num b)", 45, 50, "mint"),
             _P("c3", "case Add(var l, var r)", 45, 85, "lemon"), _B("res", "result", 88, 50, "lilac", "?")],
            [("obj", "c1"), ("obj", "c2"), ("obj", "c3"), ("c2", "res")],
            [
                step("Selector", "switch (e) tries each case from top to bottom.", ["obj"]),
                step("No match", "Not a Num, so the first pattern fails.", ["c1"], [pkt("obj", "c1", "Num?", "rose")]),
                step("Deconstruct", "Add with two Num children matches: a = 2 and b = 3 are bound.", ["c2"], [pkt("obj", "c2", "match", "mint")], {"c2": {"sub": "a=2, b=3"}}),
                step("Evaluate", "The arrow body runs: 2 + 3. Later cases are skipped.", ["res"], [pkt("c2", "res", "5")], {"res": {"sub": "5"}}),
            ],
        ),
    },
    {
        "id": "exceptions", "title": "Exceptions & Resources", "category": "runtime", "level": "basic", "code": "EX",
        "tagline": "Checked vs unchecked, try-with-resources and Optional.",
        "analogy": "A fire alarm system. A checked exception is a fire drill on the official plan (you must have an exit procedure), an unchecked exception is a surprise fire from faulty wiring (a bug). try-with-resources is the automatic door that always closes behind you.",
        "what": "Exceptions signal abnormal conditions and unwind the call stack until a matching catch. Checked exceptions (IOException, SQLException) must be declared or caught; unchecked ones (RuntimeException subclasses such as NullPointerException, IllegalArgumentException) usually indicate bugs. Errors (OutOfMemoryError) should rarely be caught. try-with-resources (Java 7) closes AutoCloseable resources automatically, in reverse order, keeping suppressed exceptions; Java 9 allows effectively final variables in the header. Multi-catch (catch (A | B e)) reduces duplication. Java 14 added helpful NullPointerException messages that name the null expression. Optional (8) makes 'maybe absent' return values explicit, but should not be used for fields or parameters.",
        "use_cases": ["Closing files, sockets and JDBC connections reliably.", "Translating low-level exceptions into domain errors.", "Validating arguments early.", "Returning Optional from finders."],
        "key_points": [
            "Never swallow exceptions silently; log or rethrow with cause.",
            "Use try-with-resources for anything AutoCloseable.",
            "Catch the most specific type; avoid catch (Exception e) in libraries.",
            "Do not log secrets or full request bodies in exception messages.",
        ],
        "examples": [
            jx("try-with-resources", "basic", "Resources close even when exceptions fly.", """
                try (BufferedReader in = Files.newBufferedReader(Path.of("data.csv"));
                     BufferedWriter out = Files.newBufferedWriter(Path.of("clean.csv"))) {
                    String line;
                    while ((line = in.readLine()) != null) {
                        if (!line.isBlank()) out.write(line.strip() + "\\n");
                    }
                } catch (IOException e) {
                    throw new UncheckedIOException("could not clean data.csv", e);   // keep the cause
                }
            """),
            jx("Custom exceptions and multi-catch", "intermediate", "Domain errors with context.", """
                public class PaymentDeclinedException extends RuntimeException {
                    private final String orderId;
                    public PaymentDeclinedException(String orderId, Throwable cause) {
                        super("payment declined for order " + orderId, cause);
                        this.orderId = orderId;
                    }
                    public String orderId() { return orderId; }
                }

                try {
                    gateway.charge(order);
                } catch (TimeoutException | ConnectException e) {
                    retryLater(order);
                } catch (GatewayException e) {
                    throw new PaymentDeclinedException(order.id(), e);
                }
            """),
            jx("Optional instead of null", "intermediate", "Make absence explicit in return types.", """
                Optional<User> findByEmail(String email) {
                    return Optional.ofNullable(users.get(email));
                }

                String city = findByEmail("ada@x.io")
                    .map(User::address)
                    .map(Address::city)
                    .orElse("unknown");

                User u = findByEmail("ada@x.io").orElseThrow();   // Java 10: NoSuchElementException
                findByEmail("x").ifPresentOrElse(this::greet, this::signup);   // Java 9
            """),
        ],
        "commands": ["try (var r = open()) { ... }", "catch (A | B e)", "throw new X(\"msg\", cause)", "Objects.requireNonNull(x, \"x\")", "Optional.ofNullable(x).orElse(d)"],
        "gotchas": ["catch (Exception e) {} hides bugs and interrupts.", "finally with return overrides exceptions from try.", "Catching InterruptedException without restoring the interrupt flag (Thread.currentThread().interrupt()).", "Optional.get() without a check is just a different NPE."],
        "interview": [
            qa("basic", "Checked vs unchecked exceptions?", "Checked exceptions extend Exception (not RuntimeException) and must be caught or declared: recoverable conditions like I/O failures. Unchecked ones extend RuntimeException, are not enforced by the compiler, and usually mean programming errors."),
            qa("basic", "What does try-with-resources do?", "It declares resources that implement AutoCloseable and closes them automatically at the end of the block, in reverse order, even if an exception is thrown. Exceptions from close are added as suppressed."),
            qa("intermediate", "final vs finally vs finalize?", "final makes variables unassignable, methods non-overridable and classes non-extendable. finally is a block that always runs after try/catch. finalize was a GC callback, deprecated for removal in Java 18 (JEP 421); use Cleaner or try-with-resources."),
            qa("intermediate", "When should you use Optional?", "As a return type when a result may be absent. Not for fields, parameters, collections (return empty collections) or in performance-critical code."),
        ],
        "related": ["concurrency", "jvm-basics"],
        "flow": flow(
            [_B("main", "main()", 12, 50, "sky", "try { ... }"), _B("svc", "service.load()", 40, 50, "lemon"), _B("io", "Files.readString", 68, 50, "rose", "IOException!"),
             _B("res", "reader.close()", 68, 85, "mint", "auto"), _B("catch", "catch (IOException e)", 12, 85, "lilac")],
            [("main", "svc"), ("svc", "io"), ("io", "res"), ("res", "catch")],
            [
                step("Call down the stack", "main calls service, which reads a file.", ["main", "svc", "io"], [pkt("main", "svc"), pkt("svc", "io")]),
                step("Throw", "The file is missing: an IOException is thrown and frames start unwinding.", ["io"], set={"io": {"tint": "rose"}}),
                step("Resources close", "try-with-resources closes the reader before the catch block runs.", ["res"], [pkt("io", "res", "close()")]),
                step("Handled", "The matching catch in main handles it, with the original stack trace as the cause.", ["catch"], [pkt("res", "catch", "e")]),
            ],
        ),
    },
    {
        "id": "concurrency", "title": "Concurrency & Virtual Threads", "category": "runtime", "level": "advanced", "code": "VT",
        "tagline": "Threads, executors, the memory model, CompletableFuture and Loom.",
        "analogy": "A restaurant. Platform threads are full-time waiters: expensive, so you hire a fixed number and customers queue. Virtual threads are a waiter who takes your order, then serves other tables while your food cooks (blocking I/O), so a few real staff can look after thousands of tables.",
        "what": "Java threads share the heap, so shared mutable state needs synchronisation: synchronized blocks and ReentrantLock provide mutual exclusion and visibility; volatile gives visibility for single variables; java.util.concurrent offers atomics, ConcurrentHashMap, queues, CountDownLatch and Semaphore. The Java Memory Model defines happens-before relationships that make writes visible across threads. ExecutorService manages thread pools; CompletableFuture (8) composes async work. Java 21 made virtual threads final (JEP 444): lightweight threads scheduled by the JVM on a few carrier threads; when one blocks on I/O it unmounts, so you can have millions and write simple blocking code. Java 24 removed pinning on synchronized (JEP 491). Scoped values (final in 25) share immutable context safely; structured concurrency (StructuredTaskScope) is still a preview in 25.",
        "use_cases": ["High-concurrency HTTP servers and clients.", "Fan-out calls to many services.", "Background jobs with executors.", "Thread-safe caches and counters."],
        "key_points": [
            "Use virtual threads for I/O-bound tasks; do not pool them.",
            "CPU-bound work still needs about one thread per core.",
            "Prefer immutable data and concurrent collections over manual locks.",
            "Every shared mutable variable needs a happens-before edge (lock, volatile, atomic).",
        ],
        "examples": [
            jx("Race condition and fix", "basic", "count++ is read-modify-write, not atomic.", """
                class Counter {
                    private int unsafe;
                    private final AtomicInteger safe = new AtomicInteger();

                    void hit() {
                        unsafe++;                  // lost updates under contention
                        safe.incrementAndGet();     // atomic
                    }
                }
                // Alternatives: synchronized void hit(), LongAdder for hot counters
            """),
            jx("CompletableFuture composition (8)", "intermediate", "Run calls in parallel and combine.", """
                ExecutorService io = Executors.newFixedThreadPool(16);
                CompletableFuture<User> user = CompletableFuture.supplyAsync(() -> users.fetch(id), io);
                CompletableFuture<List<Order>> orders = CompletableFuture.supplyAsync(() -> ordersApi.fetch(id), io);

                Profile profile = user.thenCombine(orders, Profile::new)
                    .orTimeout(2, TimeUnit.SECONDS)                 // Java 9
                    .exceptionally(ex -> Profile.empty(id))
                    .join();
            """),
            jx("Virtual threads (21)", "intermediate", "Thread-per-request, at scale.", """
                try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
                    List<Future<String>> results = urls.stream()
                        .map(url -> executor.submit(() -> httpGet(url)))   // blocking call is fine
                        .toList();
                    for (var f : results) System.out.println(f.get().length());
                }

                Thread.ofVirtual().name("worker-", 0).start(() -> System.out.println("hi"));
                Thread.startVirtualThread(() -> process(job));
            """),
            jx("Scoped values (25)", "advanced", "Immutable request context for virtual threads.", """
                static final ScopedValue<String> REQUEST_ID = ScopedValue.newInstance();

                void handle(Request req) {
                    ScopedValue.where(REQUEST_ID, req.id()).run(() -> {
                        service.process(req);          // anywhere below: REQUEST_ID.get()
                    });
                }
                // Unlike ThreadLocal: no set(), no remove(), the binding ends with run().
            """),
        ],
        "commands": ["Executors.newVirtualThreadPerTaskExecutor()", "Thread.ofVirtual().start(r)", "CompletableFuture.supplyAsync(...).thenApply(...)", "synchronized · ReentrantLock · AtomicLong", "jcmd <pid> Thread.dump_to_file -format=json f.json"],
        "gotchas": ["Pooling virtual threads defeats their purpose; limit concurrency with a Semaphore instead.", "Before Java 24, long blocking inside synchronized pinned the carrier thread.", "ThreadLocal caches per thread multiply memory with millions of virtual threads.", "Deadlocks: always acquire locks in a consistent order."],
        "interview": [
            qa("intermediate", "synchronized vs volatile?", "volatile guarantees visibility and ordering for one variable but not atomic compound actions. synchronized gives mutual exclusion plus visibility for everything inside the block."),
            qa("intermediate", "What is a happens-before relationship?", "A guarantee in the Java Memory Model that one action's effects are visible to another: unlocking a monitor happens-before a later lock of it, a volatile write before later reads, Thread.start before the thread's actions, and actions before join returns."),
            qa("advanced", "How do virtual threads work?", "They are JVM-managed threads mounted on a small pool of carrier (platform) threads. When a virtual thread blocks on I/O or a lock, its stack is saved on the heap and the carrier runs another one. They are cheap to create, so you use one per task."),
            qa("advanced", "When do virtual threads not help?", "For CPU-bound work (the number of cores is the limit), when a downstream resource has a small fixed capacity (use a semaphore), and with native calls that pin the carrier."),
            qa("advanced", "What problem do scoped values solve?", "Passing immutable context (request id, user) down a call chain without parameters. Unlike ThreadLocal they cannot be mutated, are bounded to a scope, and are cheap with many virtual threads."),
        ],
        "related": ["memory-gc", "exceptions", "java-versions"],
        "flow": flow(
            [_R("v1", "virtual 1", 12, 20, "sky", "handle(req1)"), _R("v2", "virtual 2", 12, 50, "sky", "handle(req2)"), _R("v3", "virtual 3", 12, 80, "sky", "handle(req3)"),
             _B("c1", "carrier thread", 50, 35, "lilac", "ForkJoinPool"), _B("heap", "heap", 50, 80, "lemon", "parked stacks"), _B("db", "database", 88, 35, "mint", "I/O")],
            [("v1", "c1"), ("v2", "c1"), ("c1", "db"), ("v1", "heap")],
            [
                step("Mount", "Virtual thread 1 runs on a carrier thread.", ["v1", "c1"], [pkt("v1", "c1", "mount")]),
                step("Block on I/O", "It calls the database. Instead of blocking the carrier, its stack is parked on the heap.", ["db", "heap"], [pkt("c1", "db", "query"), pkt("v1", "heap", "park")], {"v1": {"sub": "waiting"}}),
                step("Carrier is free", "Virtual thread 2 mounts on the same carrier and makes progress.", ["v2"], [pkt("v2", "c1", "mount")]),
                step("Resume", "When the response arrives, thread 1 is scheduled again, possibly on another carrier.", ["v1"], [pkt("db", "c1", "rows", "mint")], {"v1": {"sub": "running"}}),
            ],
        ),
    },
    {
        "id": "memory-gc", "title": "Memory & Garbage Collection", "category": "runtime", "level": "advanced", "code": "GC",
        "tagline": "Heap generations, G1, ZGC, leaks and tuning in containers.",
        "analogy": "A city's waste service. Most rubbish is from today's takeaway (young objects die young), so a quick daily pickup (young GC) handles it. Furniture that stays for years moves to the attic (old generation), cleaned rarely. ZGC is a crew that tidies while people keep living in the house.",
        "what": "The JVM allocates objects on the heap and reclaims unreachable ones automatically. Reachability is traced from GC roots (thread stacks, static fields, JNI handles). Generational collectors exploit the weak generational hypothesis: new objects are allocated in the young generation (Eden and survivor spaces) and survivors are promoted to the old generation. G1 (default since 9) divides the heap into regions and targets a pause time (-XX:MaxGCPauseMillis). ZGC (production in 15, generational in 21 and default mode in 23) and Shenandoah do most work concurrently, with pauses usually under a millisecond regardless of heap size. Parallel GC maximises throughput, Serial suits tiny heaps, and Epsilon does nothing (testing). Java 8 replaced PermGen with Metaspace. Memory leaks in Java are objects that stay reachable: static caches, listeners, ThreadLocals. Java 25 compact object headers (JEP 519) shrink every object header to 8 bytes.",
        "use_cases": ["Choosing a GC for latency vs throughput.", "Sizing the heap in Kubernetes pods.", "Hunting a memory leak with a heap dump.", "Reading GC logs to explain latency spikes."],
        "key_points": [
            "Default G1 is a good start; try ZGC for low-latency, large heaps.",
            "In containers use -XX:MaxRAMPercentage=75 instead of fixed -Xmx guesses.",
            "Leaks are reachable objects; find the GC root path in a heap dump.",
            "Measure with GC logs (-Xlog:gc*) and JFR before tuning flags.",
        ],
        "examples": [
            jx("A classic leak", "intermediate", "A static map that only grows.", """
                class SessionRegistry {
                    private static final Map<String, Session> SESSIONS = new HashMap<>();

                    static void login(Session s) { SESSIONS.put(s.id(), s); }
                    // logout never removes: every Session stays reachable from a static root forever
                }
                // Fixes: remove on logout, bound the cache (Caffeine with maximumSize/expireAfterAccess),
                // or use WeakHashMap only when keys have independent lifecycles.
            """),
            jx("JVM flags that matter", "intermediate", "Containers, GC choice and diagnostics.", """
                // java -XX:MaxRAMPercentage=75 -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -jar app.jar
                // java -XX:+UseZGC -jar app.jar                     (generational by default since 23)
                // java -Xlog:gc*:file=gc.log:time,uptime -jar app.jar
                // java -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/dumps -jar app.jar
                // java -XX:+UseCompactObjectHeaders -jar app.jar    (Java 25, JEP 519)
                // jcmd <pid> GC.heap_dump /tmp/heap.hprof   then open in Eclipse MAT or VisualVM
            """),
            jx("References and cleanup", "advanced", "Soft, weak and Cleaner instead of finalize.", """
                WeakReference<Image> weak = new WeakReference<>(load());   // cleared at next GC if unused
                SoftReference<byte[]> soft = new SoftReference<>(cache);    // cleared under memory pressure

                private static final Cleaner CLEANER = Cleaner.create();
                class NativeBuffer implements AutoCloseable {
                    private final Cleaner.Cleanable cleanable;
                    NativeBuffer(long address) { cleanable = CLEANER.register(this, () -> free(address)); }
                    @Override public void close() { cleanable.clean(); }   // prefer explicit close
                }
            """),
        ],
        "commands": ["-Xms / -Xmx · -XX:MaxRAMPercentage", "-XX:+UseG1GC · -XX:+UseZGC", "-Xlog:gc*", "jcmd <pid> GC.heap_dump file", "jfr start / JDK Mission Control"],
        "gotchas": ["Setting -Xmx to the full container limit leaves no room for metaspace, threads and native memory: OOMKilled.", "System.gc() is a hint; do not call it in production code.", "A huge young generation can make young pauses long with G1.", "Off-heap (direct buffers, native) memory is not shown in heap graphs."],
        "interview": [
            qa("intermediate", "How does the GC decide what is garbage?", "It traces reachability from GC roots (thread stacks, static fields, JNI references). Anything not reachable is garbage, even if objects reference each other in a cycle."),
            qa("intermediate", "Why generational collection?", "Most objects die young. Collecting the small young generation often is cheap (copying only survivors), and long-lived objects are promoted to the old generation, which is collected less frequently."),
            qa("advanced", "G1 vs ZGC?", "G1 is a regional, mostly concurrent collector with pause-time targets, good default throughput and memory overhead. ZGC does marking, relocation and compaction concurrently using coloured pointers and load barriers, giving sub-millisecond pauses on heaps from MBs to TBs, at some CPU and memory cost."),
            qa("advanced", "How would you diagnose an OutOfMemoryError?", "Read the message (heap, metaspace, direct memory, unable to create native thread). For heap: enable HeapDumpOnOutOfMemoryError, analyse the dump's dominator tree and GC root paths in MAT, and check GC logs and JFR allocation profiling."),
            qa("advanced", "What is Metaspace?", "Native memory for class metadata, which replaced PermGen in Java 8. It grows automatically (cap with -XX:MaxMetaspaceSize); leaks come from class loaders that are never released, for example on hot redeploys."),
        ],
        "related": ["jvm-basics", "concurrency"],
        "flow": flow(
            [_B("eden", "Eden", 15, 30, "mint", "new objects"), _B("surv", "Survivor", 40, 30, "lemon", "survived 1+ GCs"), _B("old", "Old gen", 75, 30, "lilac", "long-lived"),
             _B("roots", "GC roots", 15, 80, "sky", "stacks, statics"), _B("dead", "garbage", 55, 80, "rose", "unreachable", True)],
            [("eden", "surv"), ("surv", "old"), ("roots", "eden"), ("eden", "dead")],
            [
                step("Allocate", "new Order() bumps a pointer in Eden: very fast.", ["eden"]),
                step("Young GC", "When Eden fills, the GC traces from roots and copies live objects to a survivor space.", ["roots", "surv"], [pkt("roots", "eden", "trace"), pkt("eden", "surv", "copy live")]),
                step("Dead objects are free", "Unreachable objects are not touched: Eden is reset in one go.", ["dead"], set={"dead": {"hidden": False}, "eden": {"sub": "empty"}}),
                step("Promote", "Objects that survive several cycles move to the old generation, collected concurrently by G1 or ZGC.", ["old"], [pkt("surv", "old", "promote")]),
            ],
        ),
    },
    {
        "id": "java-versions", "title": "Java Versions 8 to 25", "category": "versions", "level": "intermediate", "code": "VS",
        "tagline": "LTS releases, what each one changed, and how to upgrade.",
        "analogy": "Smartphone OS updates. A feature update arrives every six months; every two years one is marked 'long-term support', which companies install on their fleet and keep for years. Skipping from a very old version means catching up on many changes at once.",
        "what": "Since Java 10, a feature release ships every six months (March and September). Long-term support (LTS) releases get years of updates from vendors: 8 (2014), 11 (2018), 17 (2021), 21 (2023) and 25 (2025); since 17, LTS comes every two years. Features often appear first as preview (enabled with --enable-preview) or incubator modules, then become final. Highlights: 8 lambdas, streams, java.time, Optional; 9 modules, JShell, List.of; 10 var; 11 HttpClient and single-file launch; 14 switch expressions and helpful NPEs; 15 text blocks and production ZGC; 16 records and instanceof patterns; 17 sealed classes and strong encapsulation; 18 UTF-8 by default and jwebserver; 21 virtual threads, sequenced collections, record patterns and pattern switch; 22 unnamed variables and the FFM API; 23 Markdown doc comments; 24 stream gatherers, class-file API, ML-KEM and ML-DSA; 25 compact source files with instance main, flexible constructor bodies, module imports, scoped values and compact object headers. The Version Explorer lab shows the same code in each version side by side.",
        "use_cases": ["Choosing a target version for a new service (21 or 25).", "Planning an upgrade from 8 or 11.", "Explaining compile errors such as 'records are not supported in -source 11'.", "Knowing which interview features are final vs preview."],
        "key_points": [
            "LTS: 8, 11, 17, 21, 25. Target the newest LTS your frameworks support.",
            "Compile with --release N to target an older runtime correctly.",
            "Preview features change between releases; avoid them in production.",
            "Biggest upgrade hurdles: 8 → 11 (modules, removed Java EE) and 11 → 17 (strong encapsulation).",
        ],
        "examples": [
            jx("One program, four eras", "basic", "Reading a file and counting words by length.", """
                // Java 8
                Map<Integer, Long> byLength8 = Files.lines(Paths.get("words.txt"))
                    .collect(Collectors.groupingBy(String::length, Collectors.counting()));

                // Java 11: Path.of, String.isBlank
                var byLength11 = Files.lines(Path.of("words.txt"))
                    .filter(w -> !w.isBlank())
                    .collect(Collectors.groupingBy(String::length, Collectors.counting()));

                // Java 21: record + pattern switch on the result
                record Stat(int length, long count) {}
                var stats = byLength11.entrySet().stream().map(e -> new Stat(e.getKey(), e.getValue())).toList();
                String top = switch (stats.getFirst()) { case Stat(var len, var n) -> len + " letters: " + n; };

                // Java 25: compact source file with java.base auto-imported
                void main() throws IOException { IO.println(Files.readString(Path.of("words.txt")).lines().count()); }
            """),
            jx("Upgrade checklist", "intermediate", "Typical steps from 8 or 11 to 21/25.", """
                // 1. Build with the new JDK but --release of the old one; fix deprecation warnings.
                // 2. Replace removed Java EE modules (JAXB, JAX-WS) with Jakarta dependencies (removed in 11).
                // 3. Run jdeps --jdk-internals app.jar to find internal API use (strongly encapsulated in 17).
                // 4. Upgrade frameworks first: Spring Boot 3 needs 17+, Jakarta EE 10 needs 11+.
                // 5. Update build plugins (Maven compiler, Surefire, Lombok, Mockito, ByteBuddy).
                // 6. Raise --release, adopt records, text blocks, pattern matching gradually.
                // 7. Benchmark GC (G1 vs generational ZGC) and try virtual threads for I/O-heavy code.
            """),
            jx("Preview features", "advanced", "How to try a preview and why to be careful.", """
                // javac --release 25 --enable-preview Demo.java
                // java --enable-preview Demo
                // In Java 25, structured concurrency (StructuredTaskScope), stable values and
                // primitive patterns are previews. String templates (STR."...") were previewed in
                // 21 and 22, then withdrawn: they are not in any release.
                try (var scope = StructuredTaskScope.open()) {        // preview API, shape may change
                    var user = scope.fork(() -> findUser(id));
                    var orders = scope.fork(() -> findOrders(id));
                    scope.join();
                    return new Profile(user.get(), orders.get());
                }
            """),
        ],
        "commands": ["java -version · javac --release 21", "--enable-preview", "jdeps --jdk-internals app.jar", "jlink --add-modules ...", "sdk install java 25-tem (SDKMAN)"],
        "gotchas": ["Compiling with -source/-target but not --release can link against newer APIs that are missing at runtime.", "Non-LTS releases stop getting updates six months later.", "Some features changed shape between previews (switch yield, string templates removed).", "Old build tools and bytecode libraries fail on new class-file versions."],
        "interview": [
            qa("basic", "Which Java versions are LTS?", "8, 11, 17, 21 and 25. Since Java 17 there is an LTS every two years; feature releases ship every six months."),
            qa("intermediate", "What are the most important features from 8 to 17?", "8 lambdas and streams, 9 modules and collection factories, 10 var, 11 HttpClient, 14 switch expressions, 15 text blocks, 16 records and instanceof patterns, 17 sealed classes, plus big GC improvements (G1 default, ZGC)."),
            qa("intermediate", "What did Java 21 bring?", "Virtual threads, sequenced collections, record patterns, pattern matching for switch, generational ZGC and the KEM API, all final, in an LTS."),
            qa("advanced", "What is new in Java 25 LTS?", "Compact source files and instance main methods (IO.println), flexible constructor bodies, module import declarations, final scoped values, compact object headers, the KDF API and generational Shenandoah, among others."),
            qa("advanced", "What is a preview feature?", "A fully specified feature that is not yet permanent. It must be enabled at compile and run time with --enable-preview, may change or be removed (string templates were), and class files using it only run on that exact release."),
        ],
        "related": ["records-sealed", "pattern-matching", "concurrency"],
        "flow": flow(
            [_R("v8", "8", 8, 50, "sky", "2014 LTS"), _R("v11", "11", 26, 50, "sky", "2018 LTS"), _R("v17", "17", 44, 50, "mint", "2021 LTS"),
             _R("v21", "21", 62, 50, "lemon", "2023 LTS"), _R("v25", "25", 80, 50, "peach", "2025 LTS"), _B("note", "Feature releases", 44, 88, "slate", "every 6 months in between")],
            [("v8", "v11"), ("v11", "v17"), ("v17", "v21"), ("v21", "v25")],
            [
                step("Java 8", "Lambdas, streams, java.time, Optional: the baseline many systems still run.", ["v8"]),
                step("11 and 17", "HttpClient and single-file launch (11); records, text blocks, switch expressions and sealed types land by 17.", ["v11", "v17"], [pkt("v8", "v11"), pkt("v11", "v17")]),
                step("21", "Virtual threads, sequenced collections, record patterns and pattern switch.", ["v21"], [pkt("v17", "v21")]),
                step("25", "Compact source files, flexible constructors, module imports, scoped values, compact object headers.", ["v25", "note"], [pkt("v21", "v25")]),
            ],
        ),
    },
]

SCENARIOS = [
    {"level": "intermediate", "topic": "memory-gc", "q": "A Spring Boot pod in Kubernetes keeps getting OOMKilled although -Xmx equals the memory limit.", "a": "The heap is only part of JVM memory: metaspace, thread stacks, code cache, direct buffers and GC structures also count. Use -XX:MaxRAMPercentage=70-75 (or a smaller -Xmx), watch native memory with -XX:NativeMemoryTracking=summary and jcmd VM.native_memory, and size the limit for the total."},
    {"level": "advanced", "topic": "concurrency", "q": "An I/O-heavy service with a 200-thread pool cannot handle traffic spikes; CPU is at 20%.", "a": "Threads are blocked on I/O, so the pool is the bottleneck. On Java 21+ switch to virtual threads (Executors.newVirtualThreadPerTaskExecutor or spring.threads.virtual.enabled=true), protect downstream resources with semaphores or connection pool limits, and check for pinning (before 24) with -Djdk.tracePinnedThreads."},
    {"level": "intermediate", "topic": "java-versions", "q": "You must upgrade a Java 8 monolith to Java 21.", "a": "Upgrade build tooling and frameworks first, compile on JDK 21 with --release 8, then fix removed Java EE APIs (add Jakarta or JAXB dependencies), internal API access found by jdeps, and illegal reflective access (--add-opens as a temporary bridge). Raise --release step by step, run full tests and benchmarks, then adopt new features gradually."},
    {"level": "advanced", "topic": "memory-gc", "q": "p99 latency spikes every few minutes to 800 ms.", "a": "Check GC logs (-Xlog:gc*) and JFR for long pauses coinciding with spikes. If they are full GCs or long mixed collections, look for allocation spikes or a leak, then tune or switch to generational ZGC for sub-millisecond pauses. Also rule out safepoint pauses, CPU throttling in containers and downstream latency."},
    {"level": "basic", "topic": "collections", "q": "A HashMap lookup returns null although you just put the same key.", "a": "The key class probably overrides equals without hashCode (or neither), or the key was mutated after insertion so its hash changed. Make keys immutable (records are ideal) and implement equals and hashCode consistently."},
    {"level": "intermediate", "topic": "exceptions", "q": "Production logs show 'NullPointerException' with no detail, from Java 8 code.", "a": "On Java 14+ (on by default from 15), helpful NPE messages name the null expression. Upgrade, or split chained calls and add Objects.requireNonNull checks with messages. Then fix the root cause: return Optional or empty collections instead of null."},
]

from .java_more import CATEGORIES as _MORE_CATEGORIES, SCENARIOS as _MORE_SCENARIOS, TOPICS as _MORE_TOPICS

CATEGORIES += _MORE_CATEGORIES
TOPICS += _MORE_TOPICS
SCENARIOS += _MORE_SCENARIOS
