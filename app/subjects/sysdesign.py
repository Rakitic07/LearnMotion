"""System Design: building blocks, estimation and classic case studies. Python examples are runnable."""

from ._dsl import ex, flow, node, pkt, qa, step

CATEGORIES = [
    {"id": "fundamentals", "title": "Fundamentals", "color": "sky", "blurb": "Scale, latency and estimation."},
    {"id": "building-blocks", "title": "Building Blocks", "color": "mint", "blurb": "Load balancers, caches, queues."},
    {"id": "distributed", "title": "Distributed Data", "color": "lilac", "blurb": "Consistency, partitioning, limits."},
    {"id": "architecture", "title": "Architecture", "color": "lemon", "blurb": "Services, gateways, resilience."},
    {"id": "case-studies", "title": "Case Studies", "color": "peach", "blurb": "Put it all together."},
]

TOPICS = [
    {
        "id": "scalability", "title": "Scalability, Latency & Availability", "category": "fundamentals", "level": "basic", "code": "SC",
        "tagline": "Vertical vs horizontal scaling, latency percentiles and the nines of availability.",
        "analogy": "A restaurant: buy a bigger stove (vertical) or open more kitchens (horizontal). Customers judge you by the slowest plate on busy nights (p99), not the average.",
        "what": "Scalability is handling more load by adding resources. Vertical scaling uses a bigger machine (simple, has a ceiling). Horizontal scaling adds machines (needs stateless services, load balancing and data partitioning). Latency is measured in percentiles (p50, p95, p99) because tails hurt users at scale. Availability is uptime as nines: 99.9% allows ~8.8 hours of downtime per year, 99.99% ~53 minutes. Redundancy removes single points of failure.",
        "use_cases": ["Deciding whether to upgrade the DB box or add replicas.", "Setting SLOs like p99 < 300 ms and 99.9% availability.", "Spotting a single point of failure in a design review."],
        "key_points": [
            "Stateless app servers scale horizontally; state goes to DBs, caches, object stores.",
            "Components in series multiply availability (0.999 × 0.999 = 0.998); redundancy in parallel improves it.",
            "Throughput ≈ concurrency ÷ latency (Little's law: L = λW).",
            "Measure, then scale the bottleneck; everything else is waste.",
        ],
        "examples": [
            ex("Nines to downtime", "basic", "How much downtime each availability target allows.", "python", """
                for nines in [0.99, 0.999, 0.9999, 0.99999]:
                    minutes = (1 - nines) * 365 * 24 * 60
                    print(f"{nines:.5%} -> {minutes:8.1f} min/year")
            """),
            ex("Series vs parallel availability", "intermediate", "Chaining components lowers availability; redundancy raises it.", "python", """
                lb, app, db = 0.9995, 0.999, 0.9995
                series = lb * app * db
                app_pair = 1 - (1 - app) ** 2          # two app servers, either is enough
                print(f"single path: {series:.5f}")
                print(f"with 2 app servers: {lb * app_pair * db:.5f}")
            """),
            ex("Percentiles from samples", "intermediate", "Why p99 matters more than the mean.", "python", """
                import random, statistics
                random.seed(7)
                lat = [random.gauss(80, 10) for _ in range(990)] + [random.uniform(800, 1500) for _ in range(10)]
                lat.sort()
                pct = lambda p: lat[int(p / 100 * len(lat)) - 1]
                print(f"mean {statistics.mean(lat):.0f} ms, p50 {pct(50):.0f}, p95 {pct(95):.0f}, p99.5 {pct(99.5):.0f}")
            """),
        ],
        "commands": ["Little's law: concurrency = throughput × latency", "99.9% ≈ 8.8 h/yr · 99.99% ≈ 53 min/yr", "Availability(series) = Π a_i", "Availability(parallel) = 1 − Π (1 − a_i)"],
        "gotchas": ["Averages hide tail latency.", "Scaling app servers while the database is the bottleneck.", "Sticky sessions make horizontal scaling and deploys harder."],
        "interview": [
            qa("basic", "Vertical vs horizontal scaling?", "Vertical: bigger machine, no code changes, hard ceiling and single point of failure. Horizontal: more machines, near-unlimited and redundant, but needs statelessness, load balancing and partitioned data."),
            qa("intermediate", "Why measure p99 instead of average latency?", "A page fanning out to many services hits the tail almost every time; averages hide slow outliers that real users feel."),
            qa("intermediate", "How do you increase availability?", "Remove single points of failure with redundancy across zones, health checks and automatic failover, graceful degradation, and reduce the blast radius of deploys (canaries)."),
            qa("advanced", "What is tail latency amplification?", "If one request fans out to 100 backends each with 1% chance of being slow, ~63% of requests are slow. Mitigate with hedged requests, timeouts, and reducing fan-out."),
        ],
        "related": ["back-of-envelope", "load-balancing"],
        "flow": flow(
            [node("u", "Users", 10, 50, "slate", "1k → 100k rps"), node("big", "Big server", 45, 20, "rose", "vertical"), node("lb", "Load balancer", 45, 70, "lilac", "horizontal", hidden=True),
             node("a1", "App 1", 80, 50, "sky", "stateless", hidden=True), node("a2", "App 2", 80, 70, "sky", "stateless", hidden=True), node("a3", "App 3", 80, 90, "sky", "stateless", hidden=True)],
            [("u", "big"), ("u", "lb"), ("lb", "a1"), ("lb", "a2"), ("lb", "a3")],
            [
                step("One box", "Traffic grows; the first move is often a bigger machine.", ["u", "big"], [pkt("u", "big", "rps")]),
                step("The ceiling", "CPU maxes out and the box is a single point of failure.", ["big"], set={"big": {"sub": "CPU 100% · SPOF"}}),
                step("Scale out", "Put a load balancer in front of several <b>stateless</b> servers.", ["lb", "a1", "a2", "a3"], [pkt("u", "lb"), pkt("lb", "a1"), pkt("lb", "a2"), pkt("lb", "a3")], {"lb": {"hidden": False}, "a1": {"hidden": False}, "a2": {"hidden": False}, "a3": {"hidden": False}, "big": {"tint": "slate"}}),
                step("Lose one, stay up", "If App 2 dies, health checks remove it and traffic continues.", ["a1", "a3"], [pkt("lb", "a1"), pkt("lb", "a3")], {"a2": {"tint": "rose", "sub": "down"}}),
            ],
        ),
    },
    {
        "id": "back-of-envelope", "title": "Back-of-the-Envelope Estimation", "category": "fundamentals", "level": "basic", "code": "BE",
        "tagline": "QPS, storage, bandwidth and memory from a few assumptions.",
        "analogy": "Planning a party: 50 guests × 3 drinks = 150 drinks. You don't need the exact number, just the right order of magnitude to buy enough.",
        "what": "Estimation turns product numbers into infrastructure numbers. Start with daily active users and actions per user → requests per day → average QPS (÷ 86,400 ≈ 10⁵) → peak QPS (×2–5). Storage = writes/day × size × retention × replication. Bandwidth = QPS × payload. Cache memory often follows the 80/20 rule (cache the hot 20%). Know latency numbers: memory ~100 ns, SSD read ~100 µs, same-region round trip ~0.5 ms, cross-continent ~150 ms.",
        "use_cases": ["Sizing a URL shortener's database for 5 years.", "Deciding if a cache fits in one Redis node.", "Justifying sharding in an interview."],
        "key_points": [
            "1 day ≈ 86,400 s ≈ 10⁵ s; 1M req/day ≈ 12 QPS.",
            "Powers of two: 2¹⁰ ≈ 1 thousand (KB), 2²⁰ ≈ million (MB), 2³⁰ ≈ billion (GB).",
            "State assumptions out loud; round aggressively.",
            "Read:write ratio drives cache and replica decisions.",
        ],
        "examples": [
            ex("QPS and storage for a photo app", "basic", "Change the assumptions and rerun.", "python", """
                dau = 10_000_000
                uploads_per_user = 0.2
                views_per_user = 30
                photo_mb = 2
                write_qps = dau * uploads_per_user / 86_400
                read_qps = dau * views_per_user / 86_400
                storage_tb_year = dau * uploads_per_user * photo_mb * 365 / 1_000_000
                print(f"writes ~{write_qps:,.0f}/s, reads ~{read_qps:,.0f}/s (peak x3: {read_qps*3:,.0f}/s)")
                print(f"storage ~{storage_tb_year:,.0f} TB/year before replication")
            """),
            ex("Bandwidth and cache size", "intermediate", "Egress at peak and memory for the hot 20%.", "python", """
                read_qps = 3_500 * 3
                thumb_kb = 200
                print(f"egress ~{read_qps * thumb_kb / 1e6:.1f} GB/s at peak -> CDN territory")
                daily_reads = 300_000_000
                meta_bytes = 500
                hot = 0.2 * daily_reads * meta_bytes / 1e9
                print(f"cache for hot 20% of metadata ~{hot:.0f} GB")
            """),
            ex("Latency numbers", "basic", "Relative cost of common operations (approximate).", "python", """
                ops = {"L1 cache": 1, "RAM": 100, "SSD random read": 100_000, "same-DC round trip": 500_000,
                       "HDD seek": 10_000_000, "US to EU round trip": 150_000_000}
                for name, ns in ops.items():
                    print(f"{name:20} {ns/1e6:>10.4f} ms  " + "#" * max(1, len(str(ns)) - 1))
            """),
        ],
        "commands": ["QPS = DAU × actions ÷ 86,400", "Peak ≈ 2–5 × average", "Storage = items/day × size × days × replicas", "Bandwidth = QPS × payload size", "Cache ≈ 20% of daily hot data"],
        "gotchas": ["Forgetting replication (×3) and indexes in storage.", "Using average QPS to size for peaks.", "Spending ten minutes on arithmetic in a 45-minute interview."],
        "interview": [
            qa("basic", "Estimate QPS for 100M DAU making 10 requests per day.", "1B requests/day ÷ ~10⁵ s ≈ 10k QPS average, ~30–50k QPS peak."),
            qa("intermediate", "How much storage does a tweet-like service need for 5 years?", "Example: 200M tweets/day × 300 bytes ≈ 60 GB/day text, ×365×5 ≈ 110 TB, ×3 replicas ≈ 330 TB; media dominates and goes to object storage."),
            qa("intermediate", "When does estimation change your design?", "When numbers cross thresholds: write QPS beyond one primary (shard), data beyond one node (partition), egress in GB/s (CDN), hot set fitting in memory (cache)."),
            qa("basic", "Why round numbers?", "The goal is the order of magnitude; rounding keeps you fast and makes trade-offs obvious."),
        ],
        "related": ["scalability", "case-url-shortener"],
        "flow": flow(
            [node("dau", "10M DAU", 10, 50, "slate", "assumption"), node("rpd", "Requests/day", 32, 50, "sky", "× 30 = 300M"), node("qps", "QPS", 54, 50, "mint", "÷ 86,400 ≈ 3.5k"),
             node("peak", "Peak", 76, 30, "lemon", "× 3 ≈ 10k"), node("store", "Storage", 76, 72, "peach", "2M × 2 MB/day"), node("dec", "Design", 94, 50, "lilac", "CDN + cache + shards", "round")],
            [("dau", "rpd"), ("rpd", "qps"), ("qps", "peak"), ("qps", "store"), ("peak", "dec"), ("store", "dec")],
            [
                step("State assumptions", "10M daily users, 30 views and 0.2 uploads each.", ["dau"]),
                step("Per day", "300M reads/day.", ["rpd"], [pkt("dau", "rpd", "×30")]),
                step("Per second", "Divide by ~10⁵: about 3,500 QPS average.", ["qps"], [pkt("rpd", "qps", "÷86,400")]),
                step("Peaks and storage", "Size for ~3× peak. Storage: 2M photos/day × 2 MB = 4 TB/day.", ["peak", "store"], [pkt("qps", "peak", "×3"), pkt("qps", "store", "writes")]),
                step("Numbers drive design", "4 TB/day → object storage. 10k QPS reads → CDN and cache.", ["dec"], [pkt("peak", "dec"), pkt("store", "dec")]),
            ],
        ),
    },
    {
        "id": "load-balancing", "title": "Load Balancing", "category": "building-blocks", "level": "basic", "code": "LB",
        "tagline": "L4 vs L7, algorithms, health checks and sticky sessions.",
        "analogy": "The host at a busy restaurant seats each group at the table with the fewest diners, and stops seating at a table whose waiter is out sick.",
        "what": "A load balancer spreads requests across healthy backends. L4 balancers route TCP/UDP by IP and port (fast, protocol agnostic). L7 balancers understand HTTP: route by path or header, terminate TLS, retry, and rewrite. Algorithms: round robin, weighted, least connections, least response time, consistent hashing (affinity). Health checks remove failing backends. DNS and anycast balance across regions.",
        "use_cases": ["Spreading web traffic over many app servers.", "Path routing /api → API service, /static → CDN origin.", "Blue/green and canary deployments with weights."],
        "key_points": [
            "Least connections handles uneven request costs better than round robin.",
            "The balancer itself must be redundant (active-passive pair, managed service).",
            "Sticky sessions trade even load for local state; prefer external session stores.",
            "Connection draining lets in-flight requests finish during deploys.",
        ],
        "examples": [
            ex("Round robin vs least connections", "intermediate", "Simulate slow and fast requests on 3 servers.", "python", """
                import random
                random.seed(1)
                jobs = [random.choice([1, 1, 1, 10]) for _ in range(60)]

                def simulate(pick):
                    busy = [0, 0, 0]
                    for i, cost in enumerate(jobs):
                        busy = [max(0, b - 1) for b in busy]
                        busy[pick(i, busy)] += cost
                    return busy

                print("round robin  :", simulate(lambda i, b: i % 3))
                print("least conns  :", simulate(lambda i, b: b.index(min(b))))
            """),
            ex("Weighted canary", "intermediate", "Send ~10% of traffic to the new version.", "python", """
                import random
                random.seed(3)
                weights = {"v1": 90, "v2-canary": 10}
                hits = {k: 0 for k in weights}
                for _ in range(10_000):
                    hits[random.choices(list(weights), weights=list(weights.values()))[0]] += 1
                print(hits)
            """),
            ex("Nginx L7 upstream", "basic", "Least connections with passive health checks.", "nginx", """
                upstream api {
                    least_conn;
                    server 10.0.1.10:8080 max_fails=3 fail_timeout=10s;
                    server 10.0.1.11:8080 max_fails=3 fail_timeout=10s;
                }
                server {
                    listen 80;
                    location /api/ { proxy_pass http://api; }
                }
            """),
        ],
        "commands": ["Round robin · weighted · least_conn · ip_hash", "Health check: GET /healthz every 5s, 3 failures = out", "L4: TCP/UDP (NLB) · L7: HTTP (ALB, Envoy, Nginx)", "Connection draining / deregistration delay"],
        "gotchas": ["Health checks that only test 'process is up', not dependencies (or the reverse, cascading failures).", "Retrying non-idempotent POSTs at the balancer.", "Uneven load from long-lived connections (WebSockets, gRPC) with L4 balancing."],
        "interview": [
            qa("basic", "L4 vs L7 load balancer?", "L4 sees IPs/ports and forwards connections: fast, any protocol. L7 parses HTTP: path/host routing, TLS termination, header-based decisions, retries, at more CPU cost."),
            qa("intermediate", "How does a load balancer know a server is unhealthy?", "Active health checks (periodic probes to an endpoint) and passive checks (errors and timeouts on real traffic). After N failures the server is removed until it passes again."),
            qa("intermediate", "Why avoid sticky sessions?", "They pin users to servers, causing uneven load and lost sessions when a server dies. Store session state in Redis or a signed token so any server can serve any request."),
            qa("advanced", "How do you balance gRPC or HTTP/2 traffic?", "Long-lived multiplexed connections defeat L4 balancing; use L7 (Envoy, service mesh) or client-side load balancing per request."),
        ],
        "related": ["scalability", "consistent-hashing"],
        "flow": flow(
            [node("c", "Clients", 10, 50, "slate"), node("lb", "L7 LB", 38, 50, "lilac", "least connections"), node("s1", "Server 1", 75, 18, "sky", "2 conns"),
             node("s2", "Server 2", 75, 50, "sky", "0 conns"), node("s3", "Server 3", 75, 82, "sky", "5 conns")],
            [("c", "lb"), ("lb", "s1"), ("lb", "s2"), ("lb", "s3")],
            [
                step("Requests arrive", "All traffic hits the balancer's single address.", ["c", "lb"], [pkt("c", "lb", "GET /")]),
                step("Pick the least busy", "Least connections chooses Server 2.", ["s2"], [pkt("lb", "s2", "req")], {"s2": {"sub": "1 conn"}}),
                step("Health checks", "Server 3 fails three /healthz probes in a row.", ["s3"], [pkt("lb", "s3", "/healthz", "rose")], {"s3": {"tint": "rose", "sub": "unhealthy"}}),
                step("Route around failure", "Traffic continues on Servers 1 and 2 until 3 recovers.", ["s1", "s2"], [pkt("lb", "s1"), pkt("lb", "s2")]),
            ],
        ),
    },
    {
        "id": "caching", "title": "Caching & CDNs", "category": "building-blocks", "level": "intermediate", "code": "CA",
        "tagline": "Cache-aside, write-through, TTLs, eviction and edge caching.",
        "analogy": "Keeping your most-used spices on the counter instead of in the basement pantry. Fast to grab, but you must restock when they go stale.",
        "what": "A cache stores results closer to the reader. Layers: browser, CDN edge, reverse proxy, application (Redis/Memcached), database buffer pool. Patterns: cache-aside (app reads cache, falls back to DB, then fills), read-through, write-through (write both), write-behind (write cache, flush later). Invalidation via TTL or explicit delete. Eviction: LRU, LFU. Dangers: stampedes on popular keys, stale data, and the cache becoming a hidden dependency.",
        "use_cases": ["Product pages served from a CDN.", "User profile lookups in Redis.", "Expensive aggregate results with a short TTL."],
        "key_points": [
            "Hit ratio drives everything: 90% hits = 10× less DB load.",
            "On writes, delete the cache key rather than updating it (avoids races).",
            "Stampede protection: request coalescing, locks, early refresh, jittered TTLs.",
            "CDNs cache static and cacheable dynamic content at the edge (Cache-Control headers).",
        ],
        "examples": [
            ex("Cache-aside with TTL", "basic", "A dict acts as Redis; the slow function is the database.", "python", """
                import time
                cache, ttl = {}, 2.0
                db_calls = 0

                def db_get(uid):
                    global db_calls
                    db_calls += 1
                    return {"id": uid, "name": f"user{uid}"}

                def get_user(uid, now):
                    hit = cache.get(uid)
                    if hit and hit[1] > now:
                        return hit[0]
                    value = db_get(uid)
                    cache[uid] = (value, now + ttl)
                    return value

                for t in [0, 0.5, 1.0, 2.5, 3.0]:
                    get_user(1, t)
                print("db calls:", db_calls, "of 5 reads")
            """),
            ex("LRU eviction", "intermediate", "OrderedDict keeps recency; evict the oldest when full.", "python", """
                from collections import OrderedDict

                class LRU:
                    def __init__(self, cap):
                        self.cap, self.d = cap, OrderedDict()
                    def get(self, k):
                        if k not in self.d:
                            return None
                        self.d.move_to_end(k)
                        return self.d[k]
                    def put(self, k, v):
                        self.d[k] = v
                        self.d.move_to_end(k)
                        if len(self.d) > self.cap:
                            print("evict", self.d.popitem(last=False)[0])

                c = LRU(2)
                c.put("a", 1); c.put("b", 2); c.get("a"); c.put("c", 3)
                print(list(c.d))
            """),
            ex("HTTP caching headers", "intermediate", "What a CDN reads to decide what to cache.", "http", """
                Cache-Control: public, max-age=86400, immutable      # hashed static assets
                Cache-Control: public, s-maxage=60, stale-while-revalidate=30   # product page
                Cache-Control: private, no-store                      # account page
                ETag: "v42"                                           # revalidate with If-None-Match
            """, runnable=False),
        ],
        "commands": ["Redis: SET k v EX 300 · GET k · DEL k", "Cache-Control: max-age, s-maxage, stale-while-revalidate", "Eviction: allkeys-lru / allkeys-lfu", "Versioned keys: user:42:v7"],
        "gotchas": ["Caching errors or empty results for a long time.", "Thundering herd when a hot key expires.", "Cache and DB diverge when you update both without ordering."],
        "interview": [
            qa("intermediate", "Cache-aside vs write-through?", "Cache-aside: app reads cache, on miss loads DB and fills; writes go to DB and invalidate. Simple and resilient. Write-through: writes update cache and DB together, so reads are always warm, but every write pays both costs."),
            qa("advanced", "How do you prevent a cache stampede?", "Coalesce concurrent misses (single flight / lock), refresh popular keys early (probabilistic early expiration), add TTL jitter, and serve stale while revalidating."),
            qa("intermediate", "What would you cache at a CDN?", "Static assets with long TTLs and content hashes, public pages with short TTLs, media. Not personalized or private responses (or vary carefully)."),
            qa("advanced", "Why delete instead of update cache on writes?", "Concurrent writers may update the cache in the wrong order, leaving stale data forever. Deleting forces the next reader to load the fresh DB value."),
        ],
        "related": ["load-balancing", "case-url-shortener"],
        "flow": flow(
            [node("c", "Client", 8, 50, "slate"), node("cdn", "CDN edge", 30, 50, "mint", "static + public"), node("app", "App", 52, 50, "sky"),
             node("redis", "Redis", 74, 22, "lemon", "cache-aside"), node("db", "Database", 74, 78, "lilac", "source of truth", "db")],
            [("c", "cdn"), ("cdn", "app"), ("app", "redis"), ("app", "db")],
            [
                step("Edge hit", "Images and CSS come straight from the nearest CDN edge.", ["cdn"], [pkt("c", "cdn", "logo.png"), pkt("cdn", "c", "HIT", "mint")]),
                step("Cache miss", "GET /users/42: not at the edge, the app asks Redis, which misses.", ["app", "redis"], [pkt("cdn", "app", "/users/42"), pkt("app", "redis", "MISS", "rose")]),
                step("Load and fill", "The app reads the database and stores the result in Redis with a TTL.", ["db", "redis"], [pkt("app", "db", "SELECT"), pkt("app", "redis", "SET EX 300")]),
                step("Next read hits", "The next request is served from memory in under a millisecond.", ["redis"], [pkt("app", "redis", "GET"), pkt("redis", "app", "HIT", "mint")]),
                step("Writes invalidate", "On update, write the DB, then DEL the key so the next read reloads.", ["db", "redis"], [pkt("app", "db", "UPDATE"), pkt("app", "redis", "DEL", "rose")]),
            ],
        ),
    },
    {
        "id": "message-queues", "title": "Message Queues & Streams", "category": "building-blocks", "level": "intermediate", "code": "MQ",
        "tagline": "Decouple producers and consumers: queues, pub/sub, Kafka partitions and delivery guarantees.",
        "analogy": "A restaurant ticket rail: waiters (producers) clip orders; cooks (consumers) take them at their own pace. A rush of orders waits on the rail instead of overwhelming the kitchen.",
        "what": "Queues buffer work between services so producers are not blocked by slow consumers and spikes are smoothed. Point-to-point queues (SQS, RabbitMQ) deliver each message to one consumer. Pub/sub fans out to many subscribers. Logs/streams (Kafka, Kinesis) keep ordered, replayable partitions; consumers track offsets; ordering is per partition. Delivery is usually at-least-once, so consumers must be idempotent. Dead-letter queues hold poison messages.",
        "use_cases": ["Send emails and thumbnails asynchronously after an upload.", "Event-driven microservices (OrderPlaced → billing, shipping).", "Clickstream ingestion into analytics."],
        "key_points": [
            "At-most-once (may lose), at-least-once (may duplicate), exactly-once (expensive, scoped).",
            "Partition key decides ordering and parallelism in Kafka.",
            "Backpressure: monitor queue depth and consumer lag; autoscale consumers.",
            "Transactional outbox: write the event in the same DB transaction, relay it later.",
        ],
        "examples": [
            ex("Producer/consumer with a queue", "basic", "Consumers process at their own pace; the queue absorbs the burst.", "python", """
                from collections import deque
                q = deque()
                for i in range(8):
                    q.append(f"resize photo {i}")         # burst from producer
                tick = 0
                while q:
                    tick += 1
                    for _ in range(min(3, len(q))):      # 3 workers per tick
                        print(f"t{tick}: {q.popleft()}")
            """),
            ex("Idempotent consumer", "intermediate", "At-least-once delivery sends duplicates; dedupe with message ids.", "python", """
                deliveries = [("m1", 30), ("m2", 20), ("m1", 30), ("m3", 50)]
                seen, balance = set(), 0
                for msg_id, amount in deliveries:
                    if msg_id in seen:
                        print("skip duplicate", msg_id)
                        continue
                    seen.add(msg_id)
                    balance += amount
                print("balance", balance)
            """),
            ex("Kafka partitions by key", "advanced", "Same key → same partition → ordered for that key.", "python", """
                import zlib
                partitions = {p: [] for p in range(3)}
                events = [("order-1", "created"), ("order-2", "created"), ("order-1", "paid"), ("order-1", "shipped"), ("order-2", "paid")]
                for key, ev in events:
                    partitions[zlib.crc32(key.encode()) % 3].append(f"{key}:{ev}")
                for p, evs in partitions.items():
                    print(p, evs)
            """),
        ],
        "commands": ["Kafka: topic → partitions → consumer group offsets", "SQS: visibility timeout, DLQ after maxReceiveCount", "RabbitMQ: exchange (direct/fanout/topic) → queue", "Outbox table + relay/CDC (Debezium)"],
        "gotchas": ["Assuming exactly-once and skipping idempotency.", "Global ordering requirements that force one partition.", "Unbounded retries of a poison message blocking the partition."],
        "interview": [
            qa("intermediate", "Queue vs pub/sub vs log?", "Queue: each message to one worker, deleted after ack. Pub/sub: each message to every subscriber. Log (Kafka): append-only, retained, consumers keep offsets, can replay; ordering per partition."),
            qa("intermediate", "How do you make consumers idempotent?", "Use a unique message/business id and record processed ids (unique constraint), or make the operation naturally idempotent (SET status = 'paid' rather than balance += x)."),
            qa("advanced", "How do you publish an event reliably after a DB write?", "Transactional outbox: insert the event into an outbox table in the same transaction; a relay or CDC publishes it and marks it sent. Consumers dedupe."),
            qa("advanced", "Kafka consumer lag keeps growing. What do you do?", "Check consumer throughput and errors, add consumers up to the partition count, increase partitions if needed, batch work, fix slow downstream calls, and move poison messages to a DLQ."),
        ],
        "related": ["microservices-gateway", "case-chat"],
        "flow": flow(
            [node("p", "Upload API", 10, 50, "sky", "producer"), node("q", "Queue", 42, 50, "lemon", "depth 0", "pill"), node("w1", "Worker 1", 78, 22, "mint", "thumbnail"),
             node("w2", "Worker 2", 78, 50, "mint", "thumbnail"), node("dlq", "DLQ", 78, 82, "rose", "poison messages")],
            [("p", "q"), ("q", "w1"), ("q", "w2"), ("q", "dlq")],
            [
                step("Return fast", "The API saves the photo and enqueues a job, replying to the user immediately.", ["p", "q"], [pkt("p", "q", "job")]),
                step("Burst absorbed", "A spike of uploads piles up in the queue instead of overloading workers.", ["q"], [pkt("p", "q", "job"), pkt("p", "q", "job"), pkt("p", "q", "job")], {"q": {"sub": "depth 120"}}),
                step("Workers drain", "Workers pull at their own pace and ack after success.", ["w1", "w2"], [pkt("q", "w1", "job"), pkt("q", "w2", "job")], {"q": {"sub": "depth 40"}}),
                step("Poison message", "A corrupt file fails 5 times and moves to the dead-letter queue for inspection.", ["dlq"], [pkt("q", "dlq", "bad.jpg", "rose")]),
            ],
        ),
    },
    {
        "id": "consistency-cap", "title": "Consistency, Replication & CAP", "category": "distributed", "level": "intermediate", "code": "CP",
        "tagline": "Strong vs eventual consistency, quorums, leader election and the CAP/PACELC trade-offs.",
        "analogy": "Branches of a bank updating a shared ledger by phone. If the lines go down, each branch either stops serving (consistent) or keeps serving and reconciles later (available).",
        "what": "Replicating data improves availability and read scale but introduces divergence. Strong consistency (linearizability) means every read sees the latest write. Eventual consistency means replicas converge if writes stop. In between: read-your-writes, monotonic reads, causal consistency. CAP: under a partition choose C or A; PACELC: else choose latency or consistency. Consensus (Raft, Paxos) elects leaders and replicates logs safely with majorities.",
        "use_cases": ["Bank balances need strong consistency.", "Like counters and feeds tolerate eventual consistency.", "Leader election for a scheduler (etcd, ZooKeeper)."],
        "key_points": [
            "Quorums: W + R > N gives overlapping reads and writes.",
            "Majority (N/2 + 1) needed for consensus; 3 nodes tolerate 1 failure, 5 tolerate 2.",
            "Conflict resolution: last-write-wins (lossy), version vectors, CRDTs.",
            "Choose consistency per feature, not per company.",
        ],
        "examples": [
            ex("Quorum overlap", "intermediate", "Check which N/W/R choices guarantee reading the latest write.", "python", """
                for n, w, r in [(3, 1, 1), (3, 2, 2), (3, 3, 1), (5, 3, 3), (5, 2, 2)]:
                    print(f"N={n} W={w} R={r} ->", "strong" if w + r > n else "may read stale")
            """),
            ex("Last-write-wins loses data", "advanced", "Two replicas accept concurrent writes; LWW keeps only one.", "python", """
                a = {"cart": ["book"], "ts": 100}
                b = {"cart": ["lamp"], "ts": 101}
                lww = max([a, b], key=lambda r: r["ts"])
                merged = sorted(set(a["cart"]) | set(b["cart"]))
                print("LWW:", lww["cart"], "| set-union merge (CRDT-like):", merged)
            """),
            ex("Majority sizes", "basic", "How many failures a consensus cluster survives.", "python", """
                for n in [1, 2, 3, 4, 5, 7]:
                    majority = n // 2 + 1
                    print(f"{n} nodes: majority {majority}, tolerates {n - majority} failure(s)")
            """),
        ],
        "commands": ["W + R > N → overlapping quorum", "Raft: leader election, log replication, commit on majority", "Read-your-writes: read from leader after write", "CRDTs: G-counter, OR-set"],
        "gotchas": ["Even-sized clusters add cost without adding fault tolerance.", "Clock-based last-write-wins with skewed clocks.", "Calling a system 'CA': partitions happen, so the choice is forced."],
        "interview": [
            qa("intermediate", "Explain CAP with an example.", "Two replicas lose contact. If a write arrives at one, either reject reads/writes on the other until healed (CP, e.g. etcd) or keep serving possibly stale data and reconcile later (AP, e.g. Cassandra with low consistency)."),
            qa("advanced", "How does Raft work at a high level?", "Nodes elect a leader with randomized timeouts and majority votes per term. The leader appends entries to its log and replicates them; an entry commits once a majority has it. A new leader must have all committed entries."),
            qa("intermediate", "What is read-your-writes consistency and how do you provide it?", "A user always sees their own updates. Route their reads to the leader for a while, track a write version and wait for replicas to catch up, or pin the session to an up-to-date replica."),
            qa("advanced", "When would you use CRDTs?", "Collaborative editing, counters and sets replicated across regions or offline devices, where concurrent updates must merge automatically without coordination."),
        ],
        "related": ["consistent-hashing", "message-queues"],
        "flow": flow(
            [node("cl", "Client", 10, 50, "slate"), node("l", "Leader", 42, 50, "lilac", "term 3", "db"), node("f1", "Follower A", 80, 22, "sky", "", "db"), node("f2", "Follower B", 80, 78, "sky", "", "db")],
            [("cl", "l"), ("l", "f1"), ("l", "f2")],
            [
                step("Write to the leader", "Clients send writes to the elected leader.", ["cl", "l"], [pkt("cl", "l", "x=5")]),
                step("Replicate", "The leader appends to its log and sends the entry to followers.", ["f1", "f2"], [pkt("l", "f1", "append"), pkt("l", "f2", "append")]),
                step("Commit on majority", "With 2 of 3 acks the write is committed and acknowledged.", ["l", "f1"], [pkt("f1", "l", "ack"), pkt("l", "cl", "OK", "mint")]),
                step("Partition", "Follower B is cut off. The majority side keeps working (CP); B refuses stale reads.", ["f2"], [pkt("l", "f2", "✕", "rose")], {"f2": {"tint": "rose", "sub": "isolated"}}),
            ],
        ),
    },
    {
        "id": "consistent-hashing", "title": "Partitioning & Consistent Hashing", "category": "distributed", "level": "advanced", "code": "CH",
        "tagline": "Spread keys across nodes and move only a fraction when nodes change.",
        "analogy": "Seats around a round table. Each guest sits at the next chair clockwise from where their name lands. Adding a chair only moves the guests between it and its neighbour.",
        "what": "Partitioning spreads data across nodes. hash(key) % N is simple but changing N remaps almost every key. Consistent hashing places nodes and keys on a ring; each key belongs to the next node clockwise. Adding or removing a node moves only ~1/N of keys. Virtual nodes (many points per server) even out the load and allow weighting. Used by Dynamo, Cassandra, memcached clients and CDNs.",
        "use_cases": ["Distributing cache keys across Redis nodes.", "Partition ownership in Cassandra/DynamoDB.", "Sticky routing of users to backends."],
        "key_points": [
            "Modulo hashing remaps ~(N−1)/N keys when N changes.",
            "Virtual nodes reduce variance and help heterogeneous servers.",
            "Replication: store each key on the next R distinct nodes on the ring.",
            "Hot keys still need special handling (salting, caching).",
        ],
        "examples": [
            ex("Modulo vs consistent hashing", "advanced", "Count how many keys move when we add a 5th node.", "python", """
                import bisect, hashlib

                def h(s):
                    return int(hashlib.sha256(s.encode()).hexdigest(), 16) % 2**32

                def ring(nodes, vnodes=100):
                    pts = sorted((h(f"{n}#{i}"), n) for n in nodes for i in range(vnodes))
                    return [p for p, _ in pts], [n for _, n in pts]

                def owner(r, key):
                    pts, names = r
                    return names[bisect.bisect(pts, h(key)) % len(pts)]

                keys = [f"user{i}" for i in range(10_000)]
                before, after = ["A", "B", "C", "D"], ["A", "B", "C", "D", "E"]
                mod_moved = sum(h(k) % 4 != h(k) % 5 for k in keys)
                r1, r2 = ring(before), ring(after)
                ch_moved = sum(owner(r1, k) != owner(r2, k) for k in keys)
                print(f"modulo moved {mod_moved/100:.0f}% of keys, consistent hashing moved {ch_moved/100:.0f}%")
            """),
            ex("Load balance with virtual nodes", "advanced", "More virtual nodes → more even distribution.", "python", """
                import bisect, hashlib
                from collections import Counter
                h = lambda s: int(hashlib.sha256(s.encode()).hexdigest(), 16) % 2**32
                for v in [1, 10, 200]:
                    pts = sorted((h(f"{n}#{i}"), n) for n in "ABCD" for i in range(v))
                    keys = [h(f"k{i}") for i in range(20_000)]
                    c = Counter(pts[bisect.bisect([p for p, _ in pts], k) % len(pts)][1] for k in keys)
                    print(f"vnodes={v:>3}:", dict(sorted(c.items())))
            """),
        ],
        "commands": ["owner(key) = first node clockwise from hash(key)", "vnodes: 100–256 per physical node", "Replicas: next R distinct nodes on the ring", "Rendezvous hashing: highest hash(node, key) wins"],
        "gotchas": ["Too few virtual nodes → one node gets 2× its share.", "Forgetting to move data when ownership changes (or doing it all at once).", "Cross-partition queries become scatter-gather."],
        "interview": [
            qa("advanced", "Why consistent hashing instead of hash mod N?", "With mod N, changing N remaps nearly every key, causing a cache-miss storm or massive data movement. Consistent hashing only moves keys between the new node and its predecessor, ~1/N."),
            qa("advanced", "What are virtual nodes?", "Each physical node owns many points on the ring. This smooths uneven ranges, spreads the load of a failed node across many others, and lets bigger servers own more points."),
            qa("intermediate", "How would you pick a partition key?", "One that spreads load evenly and keeps the dominant query on a single partition (user_id, tenant_id). Avoid low-cardinality or time-ordered keys that create hot partitions."),
            qa("advanced", "Range vs hash partitioning?", "Range keeps neighbours together (efficient scans, risk of hot spots on recent keys). Hash spreads evenly but scatters range queries across partitions."),
        ],
        "related": ["consistency-cap", "caching"],
        "flow": flow(
            [node("A", "Node A", 50, 10, "sky", "", "round"), node("B", "Node B", 88, 50, "mint", "", "round"), node("C", "Node C", 50, 90, "lemon", "", "round"),
             node("D", "Node D", 12, 50, "peach", "", "round"), node("k", "key 'user42'", 76, 18, "slate", "hash → 0x5a…", "pill"), node("E", "Node E", 80, 80, "lilac", "new", "round", True)],
            [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")],
            [
                step("Nodes on a ring", "Hash each node name onto a ring of 2³² positions.", ["A", "B", "C", "D"]),
                step("Keys go clockwise", "user42 hashes between A and B, so <b>B owns it</b>.", ["k", "B"], [pkt("k", "B", "owner")]),
                step("Add a node", "Node E lands between B and C.", ["E"], set={"E": {"hidden": False}}),
                step("Only neighbours move", "Only keys between B and E move to E: ~1/N of data, not everything.", ["E", "C"], [pkt("C", "E", "some keys")]),
            ],
        ),
    },
    {
        "id": "rate-limiting", "title": "Rate Limiting", "category": "distributed", "level": "intermediate", "code": "RL",
        "tagline": "Token bucket, sliding windows and distributed limits with Redis.",
        "analogy": "A ticket machine at a ride that prints one token per second into a cup of five. You can ride five times quickly, then one per second.",
        "what": "Rate limiting protects services from abuse and overload and enforces quotas. Algorithms: fixed window counter (simple, bursty at edges), sliding window log (exact, memory heavy), sliding window counter (approximation), token bucket (allows bursts up to capacity, refills at a rate), leaky bucket (smooth outflow). Distributed limiters keep counters in Redis with atomic operations (INCR + EXPIRE, Lua scripts). Respond with 429 and Retry-After.",
        "use_cases": ["100 requests/minute per API key.", "Login attempts per IP.", "Protecting a fragile downstream from bursts."],
        "key_points": [
            "Limit by the right key: user, API key, IP, endpoint.",
            "Put limits at the edge (gateway) and protect critical internals too.",
            "Return X-RateLimit-Remaining and Retry-After headers.",
            "Fail open or closed when the limiter store is down: decide explicitly.",
        ],
        "examples": [
            ex("Token bucket", "intermediate", "Capacity 5, refill 1 token/second.", "python", """
                class TokenBucket:
                    def __init__(self, capacity, rate):
                        self.capacity, self.rate = capacity, rate
                        self.tokens, self.last = capacity, 0.0
                    def allow(self, now):
                        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
                        self.last = now
                        if self.tokens >= 1:
                            self.tokens -= 1
                            return True
                        return False

                b = TokenBucket(5, 1)
                times = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 1.6, 2.7, 2.8]
                print(["ok" if b.allow(t) else "429" for t in times])
            """),
            ex("Fixed vs sliding window", "advanced", "A burst at the window boundary doubles the allowed rate with fixed windows.", "python", """
                limit, window = 5, 60
                reqs = [55, 56, 57, 58, 59, 60, 61, 62, 63, 64]
                fixed = {}
                ok_fixed = 0
                for t in reqs:
                    w = t // window
                    fixed[w] = fixed.get(w, 0) + 1
                    ok_fixed += fixed[w] <= limit
                log, ok_slide = [], 0
                for t in reqs:
                    log = [x for x in log if x > t - window]
                    if len(log) < limit:
                        log.append(t); ok_slide += 1
                print(f"fixed window allowed {ok_fixed} in 10s, sliding log allowed {ok_slide}")
            """),
        ],
        "commands": ["Redis: INCR key; EXPIRE key 60 (fixed window)", "Redis sorted set: ZADD/ZREMRANGEBYSCORE (sliding log)", "HTTP 429 Too Many Requests + Retry-After", "Nginx: limit_req zone=api burst=20 nodelay"],
        "gotchas": ["Non-atomic read-then-write on the counter under concurrency.", "Rate limiting by IP behind a NAT or proxy (everyone shares one IP).", "Clients retrying immediately on 429 without backoff."],
        "interview": [
            qa("intermediate", "Design a rate limiter for an API.", "Gateway middleware keyed by API key; token bucket per key in Redis using an atomic Lua script; configurable rules per plan and endpoint; return 429 with Retry-After; local in-memory pre-check to cut Redis load; decide fail-open policy."),
            qa("intermediate", "Token bucket vs leaky bucket?", "Token bucket allows bursts up to capacity while enforcing an average rate. Leaky bucket outputs at a constant rate, smoothing bursts by queueing or dropping."),
            qa("advanced", "How do you rate limit across many gateway instances?", "Centralized counters in Redis (atomic ops), or local limits = global / instances with periodic sync, accepting slight inaccuracy for lower latency."),
            qa("basic", "Which status code and headers for rate limiting?", "429 Too Many Requests with Retry-After, plus informational headers such as RateLimit-Limit, RateLimit-Remaining and RateLimit-Reset."),
        ],
        "related": ["microservices-gateway", "caching"],
        "flow": flow(
            [node("c", "Client", 10, 50, "slate", "burst of 7"), node("gw", "Gateway", 40, 50, "lilac", "token bucket"), node("bucket", "Bucket", 40, 15, "lemon", "5 / 5 tokens", "pill"),
             node("api", "API", 78, 30, "mint"), node("rej", "429", 78, 75, "rose", "Retry-After: 1", "pill")],
            [("c", "gw"), ("gw", "api"), ("gw", "rej"), ("bucket", "gw")],
            [
                step("Bucket is full", "Capacity 5 tokens, refilling 1 per second.", ["bucket"]),
                step("Burst consumes tokens", "Five quick requests each take a token and pass.", ["gw", "api"], [pkt("c", "gw", "req ×5"), pkt("gw", "api", "allowed")], {"bucket": {"sub": "0 / 5 tokens"}}),
                step("Empty bucket", "Requests 6 and 7 are rejected with 429.", ["rej"], [pkt("gw", "rej", "429", "rose")]),
                step("Refill", "One second later a token is back; one more request passes.", ["bucket", "api"], [pkt("gw", "api", "allowed")], {"bucket": {"sub": "1 → 0 tokens"}}),
            ],
        ),
    },
    {
        "id": "microservices-gateway", "title": "Microservices, API Gateway & Resilience", "category": "architecture", "level": "advanced", "code": "MS",
        "tagline": "Service boundaries, gateways, timeouts, retries, circuit breakers and sagas.",
        "analogy": "A mall: each shop (service) runs independently with its own stock room (database). The information desk (gateway) directs visitors, and a shop that catches fire gets its shutters closed (circuit breaker) so the mall stays open.",
        "what": "Microservices split a system into independently deployable services owning their data, aligned to business capabilities. An API gateway handles cross-cutting edge concerns: routing, auth, rate limits, aggregation (BFF). Communication: synchronous (REST/gRPC) or asynchronous (events). Resilience patterns: timeouts, retries with exponential backoff and jitter, circuit breakers, bulkheads, fallbacks. Cross-service workflows use sagas instead of distributed transactions.",
        "use_cases": ["Teams shipping independently on separate services.", "A mobile BFF aggregating three backend calls.", "Payment provider outage handled by a circuit breaker."],
        "key_points": [
            "Start with a modular monolith; split when team or scaling pressure justifies it.",
            "Every network call needs a timeout; retries need idempotency and backoff.",
            "Circuit breaker states: closed → open (fail fast) → half-open (probe).",
            "Observability (tracing, correlation ids) is mandatory, not optional.",
        ],
        "examples": [
            ex("Retry with exponential backoff and jitter", "intermediate", "Spread retries so clients don't stampede a recovering service.", "python", """
                import random
                random.seed(5)
                base, cap = 0.1, 5.0
                for attempt in range(6):
                    sleep = random.uniform(0, min(cap, base * 2 ** attempt))
                    print(f"attempt {attempt + 1}: wait {sleep:.2f}s")
            """),
            ex("Circuit breaker", "advanced", "Open after 3 failures, fail fast, then probe after a cool-down.", "python", """
                class Breaker:
                    def __init__(self, threshold=3, cooldown=5):
                        self.state, self.fails, self.opened = "closed", 0, None
                        self.threshold, self.cooldown = threshold, cooldown
                    def call(self, ok, now):
                        if self.state == "open":
                            if now - self.opened < self.cooldown:
                                return "fail fast"
                            self.state = "half-open"
                        if ok:
                            self.state, self.fails = "closed", 0
                            return "success"
                        self.fails += 1
                        if self.state == "half-open" or self.fails >= self.threshold:
                            self.state, self.opened = "open", now
                        return "error"

                b = Breaker()
                for t, ok in [(0, False), (1, False), (2, False), (3, True), (4, True), (8, True), (9, True)]:
                    print(t, b.call(ok, t), "->", b.state)
            """),
        ],
        "commands": ["Timeouts on every call (connect + read)", "Retries: exponential backoff + full jitter, idempotency keys", "Circuit breaker: closed / open / half-open", "Saga: local transactions + compensations", "Tracing: W3C traceparent header"],
        "gotchas": ["Distributed monolith: services that must deploy together.", "Retry storms multiplying load at every layer.", "Shared database between services couples them tightly."],
        "interview": [
            qa("intermediate", "Monolith vs microservices?", "Monolith: simple deploys, easy transactions and refactoring, but scaling teams and components independently is hard. Microservices: independent deploys and scaling and fault isolation, at the cost of network failures, data consistency and operational complexity."),
            qa("intermediate", "What does an API gateway do?", "Single entry point that routes requests, terminates TLS, authenticates, rate limits, transforms and aggregates responses, and emits metrics, so services don't each reimplement edge concerns."),
            qa("advanced", "Explain the circuit breaker pattern.", "Wrap calls to a dependency; after a failure threshold the breaker opens and calls fail fast (or use a fallback) for a cool-down, then half-open lets a few probes through; success closes it. This prevents cascading failures and gives the dependency time to recover."),
            qa("advanced", "How do you implement an order flow spanning payment and inventory?", "Saga: reserve inventory, charge payment, confirm order; on failure run compensations (refund, release stock). Orchestrated by a coordinator or choreographed via events, with idempotent steps and an outbox."),
        ],
        "related": ["message-queues", "rate-limiting"],
        "flow": flow(
            [node("m", "Mobile app", 8, 50, "slate"), node("gw", "API Gateway", 32, 50, "lilac", "auth · rate limit · route"), node("u", "Users svc", 64, 16, "sky", "", "box"),
             node("o", "Orders svc", 64, 50, "mint"), node("p", "Payments svc", 64, 84, "peach", "3rd-party PSP"), node("cb", "Breaker", 90, 84, "lemon", "closed", "pill")],
            [("m", "gw"), ("gw", "u"), ("gw", "o"), ("o", "p"), ("p", "cb")],
            [
                step("One entry point", "The gateway authenticates the token and applies rate limits.", ["m", "gw"], [pkt("m", "gw", "POST /checkout")]),
                step("Route and aggregate", "It calls Users and Orders services; each owns its own database.", ["u", "o"], [pkt("gw", "u", "profile"), pkt("gw", "o", "create")]),
                step("Downstream fails", "The payment provider times out repeatedly.", ["p", "cb"], [pkt("p", "cb", "timeout", "rose")], {"cb": {"sub": "3 failures"}}),
                step("Breaker opens", "Calls now fail fast with a fallback ('payment pending') instead of piling up threads.", ["cb", "o"], [pkt("o", "p", "fail fast", "rose")], {"cb": {"sub": "open", "tint": "rose"}}),
                step("Half-open probe", "After a cool-down one probe succeeds and the breaker closes.", ["cb"], [pkt("p", "cb", "200", "mint")], {"cb": {"sub": "closed", "tint": "mint"}}),
            ],
        ),
    },
    {
        "id": "case-url-shortener", "title": "Case Study: URL Shortener", "category": "case-studies", "level": "intermediate", "code": "US",
        "tagline": "Key generation, redirects at scale, caching and analytics.",
        "analogy": "A coat check: hand over a long coat (URL), get a small numbered ticket (short code). Anyone with the ticket gets the coat back instantly.",
        "what": "Requirements: create short links, redirect fast (read-heavy, ~100:1), optional custom aliases and expiry, click analytics. Key generation: base62 of a unique id (counter ranges per server, Snowflake) or random 7-char codes with collision checks. Storage: key-value or SQL table code → long_url (billions of small rows). Redirect path: CDN/cache → DB on miss; 301 (cacheable) vs 302 (count every click). Analytics go async through a queue.",
        "use_cases": ["Marketing links with click tracking.", "Interview warm-up design question.", "Pastebin-style services (same pattern)."],
        "key_points": [
            "62⁷ ≈ 3.5 trillion codes: 7 characters is plenty.",
            "Pre-allocated id ranges avoid a single counter bottleneck.",
            "Cache hot links; most traffic goes to a small set.",
            "Validate URLs and block malicious destinations.",
        ],
        "examples": [
            ex("Base62 encode/decode", "basic", "Turn numeric ids into short codes.", "python", """
                ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

                def encode(n):
                    s = ""
                    while True:
                        n, r = divmod(n, 62)
                        s = ALPHABET[r] + s
                        if n == 0:
                            return s

                def decode(s):
                    n = 0
                    for ch in s:
                        n = n * 62 + ALPHABET.index(ch)
                    return n

                for i in [1, 61, 62, 125_000_000_000]:
                    print(i, "->", encode(i), "->", decode(encode(i)))
                print("7 chars hold", f"{62**7:,}", "codes")
            """),
            ex("Capacity estimate", "intermediate", "100M new links/month, 100:1 reads.", "python", """
                writes_month = 100_000_000
                write_qps = writes_month / (30 * 86_400)
                read_qps = write_qps * 100
                storage_tb = writes_month * 12 * 5 * 500 / 1e12
                print(f"writes {write_qps:.0f}/s, reads {read_qps:,.0f}/s, 5-year storage ~{storage_tb:.0f} TB")
            """),
        ],
        "commands": ["POST /urls {long_url} → {code}", "GET /{code} → 301/302 Location", "code = base62(id) · ids from range allocator", "Cache: code → url (LRU, TTL)", "Clicks → queue → analytics store"],
        "gotchas": ["Sequential codes are guessable; add salt or shuffle if privacy matters.", "301 responses get cached by browsers, so click counts drop.", "Hash-based codes (MD5 prefix) collide and need retries."],
        "interview": [
            qa("intermediate", "How do you generate unique short codes?", "Base62-encode unique ids from a distributed generator (each server leases a range of ids from a coordinator/DB), or random codes with an insert-if-absent check. Ranges avoid collisions and coordination per request."),
            qa("intermediate", "301 or 302?", "301 is permanent and cacheable, reducing load but hiding repeat clicks. 302/307 keeps every click hitting your service, needed for accurate analytics."),
            qa("advanced", "How do you scale redirects to 100k QPS?", "Cache hot codes in Redis and at the CDN edge, a horizontally scaled stateless redirect tier, a key-value store sharded by code, and async click logging via a queue."),
            qa("basic", "What data model would you use?", "urls(code PK, long_url, user_id, created_at, expires_at). Key-value fits well since access is by code; a secondary index on user_id lists a user's links."),
        ],
        "related": ["back-of-envelope", "caching"],
        "flow": flow(
            [node("u", "User", 8, 50, "slate"), node("api", "Shortener API", 32, 30, "sky", "POST /urls"), node("ids", "ID ranges", 32, 80, "lemon", "server gets 1M ids"),
             node("db", "KV store", 62, 30, "lilac", "code → url", "db"), node("cache", "Redis/CDN", 62, 80, "mint", "hot codes"), node("q", "Click queue", 90, 55, "peach", "analytics", "pill")],
            [("u", "api"), ("api", "ids"), ("api", "db"), ("u", "cache"), ("cache", "db"), ("cache", "q")],
            [
                step("Shorten", "POST a long URL. The API takes the next id from its leased range.", ["api", "ids"], [pkt("u", "api", "long url"), pkt("ids", "api", "id 125B")]),
                step("Encode and store", "base62(125000000000) = '2crtgcg'. Store code → url.", ["db"], [pkt("api", "db", "2crtgcg")]),
                step("Redirect", "GET /2crtgcg: the cache usually answers with a 302.", ["cache"], [pkt("u", "cache", "/2crtgcg"), pkt("cache", "u", "302", "mint")]),
                step("Miss and analytics", "On a miss the cache loads from the KV store; every click goes to a queue for analytics.", ["db", "q"], [pkt("cache", "db", "miss"), pkt("cache", "q", "click")]),
            ],
        ),
    },
    {
        "id": "case-chat", "title": "Case Study: Chat System", "category": "case-studies", "level": "advanced", "code": "CS",
        "tagline": "WebSockets, presence, message ordering, fan-out and offline delivery.",
        "analogy": "A post office with open phone lines: if your friend is on the line, the clerk reads your letter to them now; if not, it waits in their PO box until they come in.",
        "what": "Requirements: 1:1 and group messages, delivery receipts, online presence, history, push notifications. Clients hold persistent WebSocket connections to chat servers. A session registry (Redis) maps user → server. Sending: persist the message (wide-column store partitioned by conversation, ordered by a per-conversation sequence or Snowflake id), then route to recipients' servers via pub/sub; offline users get push notifications and fetch on reconnect. Group fan-out grows with members; large groups use fan-out on read.",
        "use_cases": ["WhatsApp/Slack style messaging.", "Live support chat.", "Multiplayer game lobbies."],
        "key_points": [
            "Message ids: per-conversation monotonic sequence gives ordering and gap detection.",
            "Client-generated ids make sends idempotent on retry.",
            "Presence via heartbeats with a TTL; broadcast changes lazily.",
            "Sticky connections complicate deploys; drain gracefully.",
        ],
        "examples": [
            ex("Routing a message", "advanced", "Session registry and per-conversation sequence numbers.", "python", """
                sessions = {"alice": "chat-1", "bob": "chat-2"}       # user -> server (Redis)
                seq = {}
                inbox_offline = {}

                def send(conv, sender, to, text):
                    seq[conv] = seq.get(conv, 0) + 1
                    msg = {"conv": conv, "seq": seq[conv], "from": sender, "text": text}
                    server = sessions.get(to)
                    if server:
                        print(f"{server} pushes to {to}: {msg}")
                    else:
                        inbox_offline.setdefault(to, []).append(msg)
                        print(f"{to} offline -> stored + push notification")

                send("a-b", "alice", "bob", "hi")
                send("a-b", "bob", "alice", "hey!")
                send("a-c", "alice", "carol", "lunch?")
                print("carol's pending:", inbox_offline["carol"])
            """),
            ex("Group fan-out cost", "intermediate", "Writes per message for fan-out on write.", "python", """
                for members in [5, 100, 10_000]:
                    msgs_per_day = 2_000
                    print(f"group of {members:>6}: {members * msgs_per_day:>12,} deliveries/day")
            """),
        ],
        "commands": ["WebSocket: persistent bi-directional connection", "Registry: SET user:42:conn chat-7 EX 60", "Storage: messages PRIMARY KEY ((conv_id), seq)", "Pub/sub between chat servers (Redis, Kafka)", "Push: APNs / FCM for offline users"],
        "gotchas": ["Ordering by server timestamp across machines with clock skew.", "Thundering reconnects after a chat server restart.", "Large groups fanning out every message to every member's inbox."],
        "interview": [
            qa("advanced", "How do messages reach a user connected to another server?", "Chat servers register user → server in a session store. The sending server looks up the recipient's server and publishes via a pub/sub channel or direct RPC; that server pushes over the WebSocket."),
            qa("advanced", "How do you guarantee message ordering?", "Order within a conversation using a per-conversation sequence number assigned by the partition owner (or a Snowflake id), and let clients reorder and detect gaps by sequence."),
            qa("intermediate", "How do you implement online presence?", "Clients send heartbeats; the server keeps a key with a TTL; expiry means offline. Publish presence changes to friends, batching to avoid storms."),
            qa("advanced", "What storage fits chat history?", "A wide-column store (Cassandra/ScyllaDB/HBase) partitioned by conversation id and clustered by sequence, giving fast appends and 'latest N messages' range reads."),
        ],
        "related": ["message-queues", "consistency-cap"],
        "flow": flow(
            [node("a", "Alice", 8, 30, "sky", "WebSocket"), node("s1", "Chat server 1", 34, 30, "lilac"), node("reg", "Session registry", 34, 80, "lemon", "bob → server 2"),
             node("store", "Message store", 64, 80, "mint", "conv, seq", "db"), node("s2", "Chat server 2", 64, 30, "lilac"), node("b", "Bob", 92, 30, "peach", "WebSocket"),
             node("push", "Push service", 92, 80, "rose", "APNs/FCM", hidden=True)],
            [("a", "s1"), ("s1", "reg"), ("s1", "store"), ("s1", "s2"), ("s2", "b"), ("s1", "push")],
            [
                step("Send over WebSocket", "Alice sends 'hi' with a client id for idempotency.", ["a", "s1"], [pkt("a", "s1", "hi")]),
                step("Persist with a sequence", "Server 1 stores it as seq 42 in the conversation partition.", ["store"], [pkt("s1", "store", "seq 42")]),
                step("Find Bob", "The registry says Bob is connected to server 2.", ["reg"], [pkt("s1", "reg", "where is bob?"), pkt("reg", "s1", "server 2")]),
                step("Deliver", "Server 1 forwards to server 2, which pushes over Bob's socket; Bob acks.", ["s2", "b"], [pkt("s1", "s2", "msg"), pkt("s2", "b", "hi")]),
                step("Offline path", "If Bob were offline, a push notification is sent and he syncs from seq 41 on reconnect.", ["push"], [pkt("s1", "push", "notify")], {"push": {"hidden": False}}),
            ],
        ),
    },
]

SCENARIOS = [
    {"level": "intermediate", "topic": "caching", "q": "After a deploy that flushed Redis, the database CPU spiked to 100% and the site went down.", "a": "Cache stampede on a cold cache. Warm critical keys before switching traffic, coalesce misses (single flight), add TTL jitter, rate limit DB access from the app, and roll out cache changes gradually instead of flushing everything."},
    {"level": "advanced", "topic": "microservices-gateway", "q": "A slow recommendation service makes the whole product page time out.", "a": "Add a short timeout and a circuit breaker around the call, render the page with a fallback (no recommendations or cached ones), isolate its thread pool (bulkhead), and load it asynchronously on the client."},
    {"level": "advanced", "topic": "message-queues", "q": "Customers sometimes get two confirmation emails for one order.", "a": "At-least-once delivery plus a non-idempotent consumer. Record processed message ids (or order_id + email type) with a unique constraint and skip duplicates; use the outbox pattern on the producer side."},
    {"level": "intermediate", "topic": "rate-limiting", "q": "A single customer's batch job is degrading the API for everyone.", "a": "Per-key token bucket limits at the gateway with 429 + Retry-After, separate quotas or a separate pool for batch traffic, and backpressure guidance (bulk endpoints, async jobs)."},
    {"level": "advanced", "topic": "consistent-hashing", "q": "Adding one cache node caused a 90% miss rate for an hour.", "a": "The client used hash(key) % N, so almost every key moved. Switch to consistent hashing with virtual nodes so only ~1/N of keys move, and add nodes gradually."},
]

from .sysdesign_more import CATEGORIES as _MORE_CATEGORIES, SCENARIOS as _MORE_SCENARIOS, TOPICS as _MORE_TOPICS

CATEGORIES += _MORE_CATEGORIES
TOPICS += _MORE_TOPICS
SCENARIOS += _MORE_SCENARIOS
