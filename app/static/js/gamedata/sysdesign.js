export const WORDS = [
  { answer: "LATENCY", term: "Latency", clue: "Time one request takes, usually reported as p50, p95, p99" },
  { answer: "THROUGHPUT", term: "Throughput", clue: "How many requests a system completes per second" },
  { answer: "SCALABILITY", term: "Scalability", clue: "Ability to handle more load by adding resources" },
  { answer: "HORIZONTAL", term: "Horizontal scaling", clue: "Scaling out by adding more machines" },
  { answer: "VERTICAL", term: "Vertical scaling", clue: "Scaling up with a bigger machine" },
  { answer: "STATELESS", term: "Stateless service", clue: "Keeps no session data locally, so any instance can serve any request" },
  { answer: "LOADBALANCER", term: "Load balancer", clue: "Spreads requests across healthy backends" },
  { answer: "ROUNDROBIN", term: "Round robin", clue: "Balancing algorithm that takes backends in turn" },
  { answer: "CACHE", term: "Cache", clue: "Fast store for hot data in front of a slower one" },
  { answer: "TTL", term: "TTL", clue: "How long a cached entry lives before it expires" },
  { answer: "EVICTION", term: "Eviction", clue: "Removing entries when the cache is full, e.g. LRU" },
  { answer: "LRU", term: "LRU", clue: "Eviction policy: drop whatever was used longest ago" },
  { answer: "CDN", term: "CDN", clue: "Edge servers near users that cache static and media content" },
  { answer: "QUEUE", term: "Message queue", clue: "Buffer that decouples producers from consumers" },
  { answer: "IDEMPOTENT", term: "Idempotent", clue: "Safe to retry: doing it twice has the same effect as once" },
  { answer: "BACKPRESSURE", term: "Backpressure", clue: "Signal from a slow consumer telling producers to slow down" },
  { answer: "SHARDING", term: "Sharding", clue: "Splitting data across nodes by a key" },
  { answer: "REPLICATION", term: "Replication", clue: "Keeping copies of data on several nodes" },
  { answer: "QUORUM", term: "Quorum", clue: "Majority of replicas that must agree, e.g. W + R > N" },
  { answer: "PARTITION", term: "Network partition", clue: "Nodes cannot talk to each other; the P in CAP" },
  { answer: "EVENTUAL", term: "Eventual consistency", clue: "Replicas converge if writes stop, but reads may be stale" },
  { answer: "CONSISTENTHASHING", term: "Consistent hashing", clue: "Ring placement where adding a node moves only about 1/N of keys" },
  { answer: "RATELIMIT", term: "Rate limiting", clue: "Capping requests per client per time window" },
  { answer: "TOKENBUCKET", term: "Token bucket", clue: "Rate limiter that refills at a fixed rate and allows short bursts" },
  { answer: "CIRCUITBREAKER", term: "Circuit breaker", clue: "Stops calling a failing dependency and fails fast instead" },
  { answer: "GATEWAY", term: "API gateway", clue: "Single entry point that handles auth, routing and rate limits" },
  { answer: "MICROSERVICES", term: "Microservices", clue: "Small, independently deployable services that own their data" },
  { answer: "WEBSOCKET", term: "WebSocket", clue: "Persistent two-way connection used for chat and live updates" },
  { answer: "FANOUT", term: "Fan-out", clue: "Delivering one write to many readers' feeds or inboxes" },
  { answer: "HOTSPOT", term: "Hot spot", clue: "One key or shard receiving far more traffic than the rest" },
  { answer: "SLA", term: "SLA", clue: "Contract promising a level of availability, e.g. 99.9%" },
  { answer: "REDUNDANCY", term: "Redundancy", clue: "Duplicate components so there is no single point of failure" },
  { answer: "BASESIXTYTWO", term: "Base62", clue: "Encoding with 0-9, a-z and A-Z, popular for short URLs" },
];

export const RUSH = [
  { task: "1 million requests per day is roughly…", answer: "12 QPS", wrong: ["1,200 QPS", "120 QPS", "1 QPS"] },
  { task: "Reads overwhelm a single database", answer: "Add a cache and read replicas", wrong: ["Shard on day one", "Buy a bigger load balancer", "Add more app servers"] },
  { task: "Absorb a sudden spike of writes", answer: "Put a queue in front and process asynchronously", wrong: ["Raise the HTTP timeout", "Add a CDN", "Disable indexes"] },
  { task: "Serve images fast worldwide", answer: "Object storage behind a CDN", wrong: ["Store images in the SQL database", "One big server in us-east-1", "Base64 them into HTML"] },
  { task: "Make a payment retry safe", answer: "Idempotency key per request", wrong: ["Retry with no limit", "Use UDP", "Increase the timeout"] },
  { task: "Spread keys so adding a node moves few of them", answer: "Consistent hashing", wrong: ["hash(key) mod N", "Round robin", "Range on the first letter"] },
  { task: "Allow short bursts but cap the average rate", answer: "Token bucket", wrong: ["Fixed window counter", "Unlimited retries", "Leaky abstraction"] },
  { task: "A dependency keeps timing out", answer: "Circuit breaker with fallback", wrong: ["Retry immediately forever", "Increase thread pool to 10,000", "Remove all timeouts"] },
  { task: "Push new chat messages to clients instantly", answer: "WebSockets", wrong: ["Poll every 30 seconds", "Email", "Batch nightly job"] },
  { task: "Generate a unique short code for a URL", answer: "Counter or ID → base62", wrong: ["MD5 the URL and keep 2 chars", "Random 3-digit number", "Timestamp in seconds"] },
  { task: "Celebrity with 50M followers posts", answer: "Pull at read time for celebrities, push for normal users", wrong: ["Write to 50M inboxes synchronously", "Block the post", "Shard by post length"] },
  { task: "Cache pattern where the app loads on miss", answer: "Cache-aside", wrong: ["Write-behind", "Read-through only", "No-cache"] },
  { task: "A replica serves stale data after a write", answer: "Read your own writes from the primary", wrong: ["Disable replication", "Add more replicas", "Lower the TTL to zero everywhere"] },
  { task: "Quorum rule for strong reads with N replicas", answer: "W + R > N", wrong: ["W + R = N", "W = R = 1", "R > N"] },
  { task: "99.9% availability allows about … of downtime per month", answer: "43 minutes", wrong: ["4 minutes", "7 hours", "3 days"] },
  { task: "Avoid a single point of failure in the app tier", answer: "Multiple stateless instances behind a load balancer", wrong: ["One huge instance", "Sticky sessions on one server", "Store sessions in memory"] },
  { task: "One shard gets most of the traffic", answer: "Hot key: add salt or split the key", wrong: ["Add an index", "Lower replication", "Use a bigger CDN"] },
  { task: "Route, authenticate and rate-limit all public APIs in one place", answer: "API gateway", wrong: ["Service mesh sidecar only", "DNS round robin", "Database trigger"] },
];

export const BUGS = [
  {
    symptom: "Adding a fourth cache node made the hit rate collapse to almost zero.",
    lang: "python",
    code: `NODES = ["cache-a", "cache-b", "cache-c", "cache-d"]

def node_for(key: str) -> str:
    h = hash_32(key)
    return NODES[h % len(NODES)]`,
    bug: [4],
    why: "hash mod N remaps almost every key when N changes, so the cache is effectively empty. Use consistent hashing (a ring with virtual nodes) so only about 1/N of keys move.",
  },
  {
    symptom: "Customers were charged twice when the mobile app retried after a timeout.",
    lang: "python",
    code: `@app.post("/charge")
def charge(req):
    user = auth(req)
    payment = gateway.charge(user.card, req.json["amount"])
    db.insert("payments", payment)
    return {"ok": True}`,
    bug: [3],
    why: "The charge is not idempotent. Require an Idempotency-Key, store it with the result and return the stored result on retries instead of charging again.",
  },
  {
    symptom: "After a cache flush the database fell over from thousands of identical queries.",
    lang: "python",
    code: `def get_product(pid):
    item = cache.get(pid)
    if item is None:
        item = db.query("SELECT * FROM products WHERE id = ?", pid)
        cache.set(pid, item, ttl=3600)
    return item`,
    bug: [3],
    why: "Cache stampede: every concurrent miss hits the database. Let one caller rebuild (lock or request coalescing), serve stale while refreshing, and add jitter to TTLs.",
  },
  {
    symptom: "One slow downstream service made every API endpoint hang.",
    lang: "python",
    code: `def recommendations(user_id):
    resp = http.get(f"http://recs/users/{user_id}", timeout=None)
    return resp.json()

def home(user_id):
    return {"feed": feed(user_id), "recs": recommendations(user_id)}`,
    bug: [1],
    why: "No timeout means threads pile up waiting forever. Set a short timeout, wrap it in a circuit breaker and fall back to an empty list so the page still loads.",
  },
  {
    symptom: "Users get logged out randomly after we added a second app server.",
    lang: "python",
    code: `SESSIONS = {}

@app.post("/login")
def login(req):
    sid = new_session_id()
    SESSIONS[sid] = req.user
    return set_cookie("sid", sid)`,
    bug: [0],
    why: "Sessions live in one process's memory, so a request routed to the other server finds nothing. Keep servers stateless: store sessions in Redis or use signed tokens.",
  },
  {
    symptom: "The rate limiter lets clients send 2x the limit around minute boundaries.",
    lang: "python",
    code: `def allow(client):
    window = int(time.time() // 60)
    key = f"rl:{client}:{window}"
    count = redis.incr(key)
    redis.expire(key, 60)
    return count <= 100`,
    bug: [1],
    why: "A fixed window resets on the minute, so 100 requests at 0:59 plus 100 at 1:00 all pass. Use a sliding window or a token bucket.",
  },
];

export const META = {
  rushLabel: "Design Rush",
  rushIntro: "Pick the design decision a senior engineer would make.",
  rushMono: false,
  bugLabel: "Design Bug Hunt",
  bugNoun: "incident",
};
