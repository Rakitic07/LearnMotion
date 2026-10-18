"""More sysdesign topics, appended to the core module."""

from ._dsl import chain, ex, qa, topic

CATEGORIES = [
    {"id": "edge-api", "title": "Edge & APIs", "color": "slate", "blurb": "DNS, CDNs, API contracts and auth."},
    {"id": "reliability", "title": "Reliability & Ops", "color": "rose", "blurb": "Retries, breakers, SLOs, DR."},
]

TOPICS = [
    topic(
        "latency-throughput", "Latency, Throughput & Percentiles", "fundamentals", "basic", "LT",
        "Why p99 explodes near full utilization, and how to report latency honestly.",
        "A supermarket checkout: throughput is shoppers per hour, latency is how long you stand in line. When the cashier is busy 95% of the time, the line gets long fast even though nobody works slower.",
        "Latency is the time one request takes; throughput is how many requests complete per unit time. They are linked by Little's law: concurrency = throughput × latency. As utilization of a resource approaches 100%, queueing delay grows non-linearly (for an M/M/1 queue, wait ∝ ρ/(1−ρ)), so a server at 90% busy has roughly 9× the queueing of one at 50%. Latency must be reported as percentiles (p50, p95, p99, p99.9) because distributions are long-tailed and averages hide the slow requests users actually notice. Percentiles cannot be averaged across hosts; aggregate raw histograms (HDR, t-digest, Prometheus buckets) and compute the percentile on the merged data. Fan-out amplifies tails: a request touching 100 backends sees the backend p99 on most calls. Plan capacity to keep steady-state utilization around 50-70% so bursts do not push you into the steep part of the curve.",
        ["Choosing a target CPU utilization for autoscaling.", "Defining latency SLOs on p99 rather than mean.", "Explaining why a slightly busier database suddenly times out.", "Designing dashboards that merge per-host histograms correctly."],
        [
            "Little's law: L = λW (in-flight = arrival rate × time in system).",
            "Queueing delay grows like ρ/(1−ρ); the knee is around 70-80% utilization.",
            "Report p50/p95/p99/p99.9 with the time window and sample count.",
            "Never average percentiles; merge histograms, then compute.",
            "Fan-out: P(at least one slow) = 1 − (1 − p)^n.",
        ],
        [
            ex("Utilization vs queueing latency", "intermediate", "Simulates a single-server queue (exponential arrivals and service, mean service 1 ms).", "python", """
                import random
                random.seed(42)

                def simulate(util, n=20000, service=1.0):
                    t = free_at = 0.0
                    lat = []
                    for _ in range(n):
                        t += random.expovariate(util / service)
                        start = max(t, free_at)
                        free_at = start + random.expovariate(1 / service)
                        lat.append(free_at - t)
                    lat.sort()
                    return sum(lat) / n, lat[int(0.99 * n)]

                for u in (0.5, 0.7, 0.9, 0.95):
                    mean, p99 = simulate(u)
                    print(f"utilization {u:.0%}: mean {mean:5.1f} ms   p99 {p99:6.1f} ms")
            """),
            ex("Averaging percentiles is wrong", "intermediate", "Two hosts; the fleet p99 must come from merged samples.", "python", """
                import random
                random.seed(1)
                a = [random.gauss(50, 5) for _ in range(1000)]
                b = [random.gauss(50, 5) for _ in range(900)] + [random.uniform(400, 600) for _ in range(100)]

                def pct(xs, q):
                    xs = sorted(xs)
                    return xs[min(len(xs) - 1, int(q * len(xs)))]

                print(f"p99 host A {pct(a, .99):.0f} ms, host B {pct(b, .99):.0f} ms")
                print(f"average of the two p99s: {(pct(a, .99) + pct(b, .99)) / 2:.0f} ms  (meaningless)")
                print(f"true fleet p99 (merged): {pct(a + b, .99):.0f} ms")
            """),
            ex("Tail amplification from fan-out", "basic", "Chance a user request hits at least one slow backend.", "python", """
                for fanout in (1, 10, 50, 100):
                    slow = 1 - 0.99 ** fanout
                    print(f"fan-out {fanout:>3}: {slow:6.1%} of requests see a backend p99")
            """),
        ],
        ["Little's law: in-flight = rps × latency", "M/M/1 wait ≈ service × ρ/(1−ρ)", "Target steady utilization 50-70%", "P(slow) = 1 − (1 − 0.01)^fanout", "Histogram buckets: 5,10,25,50,100,250,500,1000 ms"],
        ["Measuring latency at the client of a load generator that waits for responses (coordinated omission hides queueing).", "Autoscaling at 90% CPU and wondering why p99 triples.", "Averaging per-host p99 values on a dashboard."],
        [
            qa("basic", "What is the difference between latency and throughput?", "Latency is the duration of a single operation; throughput is operations completed per unit time. You can raise throughput with parallelism without improving latency, and batching often raises throughput while worsening latency."),
            qa("intermediate", "Why does latency spike when utilization goes from 70% to 95%?", "Queueing delay is proportional to ρ/(1−ρ): at 70% that factor is about 2.3, at 95% it is 19. Small bursts can no longer be absorbed, so requests wait in queues and tail latency explodes even though per-request work is unchanged."),
            qa("intermediate", "How do you compute a fleet-wide p99?", "Collect mergeable histograms or sketches (HDR histogram, t-digest, Prometheus buckets) from every host, merge them and compute the percentile from the merged distribution. Averaging per-host percentiles is mathematically wrong and usually hides a bad host."),
            qa("advanced", "What is coordinated omission?", "A load generator that waits for each response before sending the next one stops sending while the server is stalled, so the stall is recorded as one slow sample instead of many. Use open-loop load (fixed arrival rate) or correct for intended start times, as wrk2 and HdrHistogram do."),
            qa("advanced", "How do you reduce tail latency in a fan-out service?", "Reduce fan-out, set tight per-call timeouts, use hedged requests (send a backup after the p95 delay), return partial results, and keep utilization of leaf nodes moderate so queueing stays low."),
        ],
        ["scalability", "back-of-envelope", "slos-error-budgets"],
        chain(
            ("Arrivals", "λ = 900 rps", "Requests arrive", "Requests arrive at a rate λ; bursts are random, not evenly spaced."),
            ("Queue", "wait ∝ ρ/(1−ρ)", "Queueing", "At 90% utilization most of the latency is time spent waiting, not working.", "req"),
            ("Server", "service 1 ms", "Service", "The actual work stays ~1 ms; only the wait changed.", "req"),
            ("Histogram", "p50 p99 p99.9", "Record", "Each latency lands in a histogram bucket that can be merged across hosts.", "latency"),
            ("Dashboard", "merged p99", "Report", "Merge all hosts' histograms, then read the percentile. Never average p99s.", "buckets"),
        ),
    ),
    topic(
        "slos-error-budgets", "Availability, SLIs, SLOs & Error Budgets", "reliability", "intermediate", "SL",
        "Measure what users feel, promise a little less, and spend the difference on change.",
        "A train company promises 99% of trains arrive within 5 minutes. The 1% it is allowed to miss is a budget: spend it on track maintenance, and when it runs out, stop risky work.",
        "An SLI (service level indicator) is a measured ratio of good events to total events, for example the fraction of HTTP requests that return non-5xx within 300 ms. An SLO (objective) is the internal target for that SLI over a window, such as 99.9% over 28 days. An SLA (agreement) is the contractual promise with penalties, usually looser than the SLO. The error budget is 1 − SLO: at 99.9% over 30 days you may fail 0.1% of requests, about 43 minutes of full outage. Teams spend the budget on releases and experiments; when it is exhausted, they freeze risky changes and invest in reliability. Alerting uses burn rate (how fast the budget is consumed) over multiple windows, for example page when the 1-hour and 5-minute burn rates both exceed 14.4×. Good SLIs are measured as close to the user as possible (load balancer logs or synthetic probes), not from CPU graphs.",
        ["Agreeing release velocity vs reliability between product and SRE.", "Replacing noisy CPU alerts with burn-rate pages.", "Writing customer SLAs with a safety margin.", "Prioritizing reliability work when the budget is exhausted."],
        [
            "SLI = good events ÷ valid events, measured near the user.",
            "SLO < SLA headroom: miss the internal target before you owe credits.",
            "Error budget = (1 − SLO) × events in the window.",
            "Burn rate 1 = budget lasts exactly the window; 14.4 = 2% of a 30-day budget in 1 hour.",
            "Multi-window alerts (long + short) give fast detection and quick reset.",
        ],
        [
            ex("Error budget and burn rate", "intermediate", "How much budget a 30-minute incident consumes.", "python", """
                slo = 0.999
                window_days = 30
                rps = 2_000
                total = rps * 86_400 * window_days
                budget = (1 - slo) * total
                print(f"budget: {budget:,.0f} failed requests (~{(1 - slo) * window_days * 1440:.0f} min of full outage)")

                incident_minutes, error_rate = 30, 0.05
                spent = rps * 60 * incident_minutes * error_rate
                burn = error_rate / (1 - slo)
                print(f"incident burned {spent / budget:.1%} of the budget at burn rate {burn:.0f}x")
            """),
            ex("Multi-window burn-rate alert", "advanced", "Page only if both the long and short window burn fast.", "python", """
                def burn(errors, total, slo=0.999):
                    return (errors / total) / (1 - slo)

                windows = {"1h": (900, 50_000), "5m": (60, 4_000)}
                rates = {w: burn(e, t) for w, (e, t) in windows.items()}
                print({w: round(r, 1) for w, r in rates.items()})
                print("PAGE" if all(r > 14.4 for r in rates.values()) else "no page")
            """),
            ex("Prometheus SLO alert rule", "advanced", "A fast-burn page for a 99.9% availability SLO.", "yaml", """
                groups:
                - name: slo-api
                  rules:
                  - alert: APIErrorBudgetFastBurn
                    expr: |
                      (sum(rate(http_requests_total{code=~"5.."}[1h])) / sum(rate(http_requests_total[1h]))) > (14.4 * 0.001)
                      and
                      (sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) > (14.4 * 0.001)
                    labels: {severity: page}
            """, runnable=False),
        ],
        ["Budget = (1 − SLO) × window", "99.9%/30d ≈ 43 min · 99.95% ≈ 22 min · 99.99% ≈ 4.3 min", "Fast burn: 14.4× over 1h and 5m → page", "Slow burn: 6× over 6h and 30m → page; 1× over 3d → ticket", "SLI: good / valid, measured at the LB"],
        ["Setting a 100% SLO; it forbids all change and is impossible anyway.", "Measuring SLIs from server metrics that miss requests dropped at the load balancer.", "SLOs nobody acts on: an exhausted budget must change priorities."],
        [
            qa("basic", "What is the difference between an SLI, SLO and SLA?", "The SLI is the measurement (e.g. fraction of requests succeeding under 300 ms), the SLO is the internal target for it (99.9% over 28 days), and the SLA is the external contract with penalties. The SLA is set looser than the SLO so you notice and react before breaching the contract."),
            qa("intermediate", "What is an error budget used for?", "It quantifies acceptable unreliability, 1 − SLO. While budget remains, teams ship features and take risks; when it is exhausted they freeze risky launches and spend time on reliability, turning a political argument into a data-driven policy."),
            qa("intermediate", "Why alert on burn rate instead of error rate thresholds?", "Burn rate ties alerts to user impact relative to the SLO: a 1% error rate is a disaster for a 99.99% service but fine for a 95% one. Multi-window burn-rate alerts catch fast outages quickly and slow leaks eventually, with fewer false pages."),
            qa("advanced", "How do you compose availability for a request path?", "Hard dependencies in series multiply (three 99.9% services give ~99.7%), so a service cannot promise more than its critical dependencies allow. Raise it with redundancy, caching and graceful degradation so a dependency failure is not a user-visible failure."),
        ],
        ["latency-throughput", "observability", "multi-region-dr"],
        chain(
            ("Requests", "LB access logs", "Collect events", "Every request is logged at the load balancer with status and latency."),
            ("SLI", "good / valid", "Compute SLI", "Good = non-5xx and under 300 ms. Health checks are excluded as invalid.", "events"),
            ("SLO", "99.9% / 30d", "Compare to target", "The SLO leaves 0.1% of requests as the error budget.", "ratio"),
            ("Burn rate", "1h & 5m windows", "Watch the burn", "If both windows burn faster than 14.4×, the budget would be gone in ~2 days.", "burn"),
            ("Policy", "page or freeze", "Act", "Page on fast burn; freeze risky launches when the budget is exhausted.", "alert"),
        ),
    ),
    topic(
        "dns", "DNS", "edge-api", "basic", "DN",
        "How names become IPs, why TTLs matter, and how DNS steers global traffic.",
        "A phone book with layers: the root tells you which book covers .com, that book tells you which company owns example.com, and the company's own book gives the number. Your neighbour (the resolver) remembers answers for a while.",
        "DNS maps names to records: A/AAAA (IPv4/IPv6), CNAME (alias), MX (mail), TXT (verification, SPF), NS (delegation) and SRV (service ports). A client asks a recursive resolver, which walks root → TLD → authoritative servers and caches each answer for its TTL. TTLs trade agility for load and latency: a 60-second TTL lets you fail over quickly but causes more lookups, and some clients ignore low TTLs anyway. Managed DNS adds traffic steering: weighted records for canaries, latency-based or geo routing to the nearest region, and health-checked failover. Anycast serves the same IP from many locations so queries reach the closest name server. CNAMEs cannot sit at the zone apex, which is why providers offer ALIAS/ANAME records. DNSSEC signs records to prevent spoofing, and DNS over HTTPS/TLS encrypts the client-to-resolver hop.",
        ["Failing over a region by flipping a health-checked record.", "Routing users to the nearest region with latency-based records.", "Gradual migrations with weighted records.", "Service discovery inside a cluster (Kubernetes CoreDNS)."],
        [
            "Resolution path: stub → recursive resolver → root → TLD → authoritative.",
            "TTL is the cache lifetime; lower it days before a planned migration.",
            "Negative answers (NXDOMAIN) are cached too, per the SOA minimum.",
            "DNS load balancing is coarse: clients cache and pick IPs unevenly.",
            "Use ALIAS/ANAME at the apex; CNAME is not allowed there.",
        ],
        [
            ex("Resolver cache with TTLs", "basic", "A simulated clock shows cache hits until the TTL expires.", "python", """
                AUTHORITATIVE = {"api.example.com": ("203.0.113.10", 60), "cdn.example.com": ("198.51.100.7", 300)}
                cache, upstream_queries = {}, 0

                def resolve(name, now):
                    global upstream_queries
                    hit = cache.get(name)
                    if hit and hit[1] > now:
                        return hit[0], "cache"
                    upstream_queries += 1
                    ip, ttl = AUTHORITATIVE[name]
                    cache[name] = (ip, now + ttl)
                    return ip, "upstream"

                for now in (0, 10, 59, 61, 120, 400):
                    print(now, "s", resolve("api.example.com", now), resolve("cdn.example.com", now))
                print("upstream queries:", upstream_queries)
            """),
            ex("Weighted and failover routing", "intermediate", "Health-checked weighted records shift traffic away from a failed region.", "python", """
                import random
                random.seed(5)
                records = [{"ip": "us-east", "w": 70, "healthy": True}, {"ip": "eu-west", "w": 30, "healthy": True}]

                def answer():
                    live = [r for r in records if r["healthy"]]
                    return random.choices([r["ip"] for r in live], [r["w"] for r in live])[0]

                for phase in ("normal", "us-east down"):
                    if phase != "normal":
                        records[0]["healthy"] = False
                    counts = {}
                    for _ in range(1000):
                        ip = answer()
                        counts[ip] = counts.get(ip, 0) + 1
                    print(phase, counts)
            """),
            ex("Inspecting DNS", "basic", "Everyday commands.", "bash", """
                dig +trace api.example.com
                dig api.example.com A +short
                dig example.com NS
                dig -x 203.0.113.10
            """, runnable=False),
        ],
        ["dig +trace name · dig name +short", "Lower TTL to 60s 48h before a migration", "A/AAAA · CNAME · ALIAS (apex) · MX · TXT · SRV", "Routing: weighted · latency · geo · failover", "Anycast: one IP announced from many PoPs"],
        ["Changing a record with a 24-hour TTL and expecting instant cut-over.", "Using DNS round robin as a real load balancer; clients and resolvers cache and stick.", "Long-lived clients (JVM, connection pools) that cache DNS forever and never notice failover."],
        [
            qa("basic", "Walk through what happens when you type a URL.", "The browser checks its cache, then asks the OS stub resolver, which asks a recursive resolver. On a miss the resolver queries a root server for the TLD, the TLD servers for the domain's authoritative name servers, and finally the authoritative server for the A/AAAA record, caching each step for its TTL. Then the browser opens a TCP/QUIC connection and TLS handshake to that IP."),
            qa("intermediate", "How do you choose a TTL?", "Short TTLs (30-60 s) give fast failover and migrations but more queries and slightly higher latency; long TTLs (hours) reduce load but slow changes. Common practice is moderate TTLs for endpoints you may fail over, long TTLs for stable records, and lowering TTLs ahead of planned changes."),
            qa("intermediate", "How can DNS route users to the nearest region?", "Latency-based or geo DNS answers with the region closest to the resolver (EDNS Client Subnet improves accuracy). Combined with health checks, an unhealthy region's records are withdrawn so new lookups go elsewhere."),
            qa("advanced", "Why is DNS failover slower than you expect?", "Resolvers and clients cache answers until the TTL expires, some ignore low TTLs, and long-lived processes or connection pools keep using already-resolved IPs. Pair DNS failover with anycast or a global load balancer when you need second-level failover."),
        ],
        ["cdn", "load-balancing", "multi-region-dr"],
        chain(
            ("Browser", "api.example.com", "Lookup", "The browser and OS caches miss, so the stub asks the recursive resolver."),
            ("Resolver", "recursive, caches", "Recursive resolver", "The resolver checks its cache, then walks the hierarchy.", "query"),
            ("Root / TLD", ". → .com", "Delegation", "Root points to .com servers; .com points to example.com's name servers.", "NS?"),
            ("Authoritative", "A 203.0.113.10", "Answer", "The authoritative server returns the A record with TTL 60.", "A?"),
            ("Cached", "TTL 60 s", "Cache and connect", "The resolver caches it for 60 s and the browser connects to the IP.", "IP"),
        ),
    ),
    topic(
        "cdn", "Content Delivery Networks", "edge-api", "basic", "CD",
        "Serve bytes from the edge: caching rules, cache keys, purging and origin shielding.",
        "Instead of shipping every book from one central warehouse, a publisher stocks popular titles in neighbourhood shops. Only rare books still come from the warehouse.",
        "A CDN is a network of edge points of presence (PoPs) that cache and serve content close to users, cutting latency and offloading the origin. Requests reach the nearest PoP via anycast or DNS steering; on a hit the edge responds directly, on a miss it fetches from an origin shield (a mid-tier cache) or the origin. Caching is controlled by Cache-Control headers (max-age, s-maxage, stale-while-revalidate, stale-if-error) and by the cache key, usually host + path + selected query parameters and headers. Static assets use content-hashed filenames with year-long TTLs, so a deploy simply references new URLs; dynamic or personalized content uses short TTLs or bypass. Purges by URL or surrogate key/tag invalidate content quickly but should not be part of every request path. CDNs also terminate TLS, absorb DDoS traffic, apply WAF rules, and can run edge compute. Signed URLs or cookies (HMAC-SHA256 with short expiry) protect paid or private media.",
        ["Serving static assets and images for a global web app.", "Video segment delivery with origin shielding.", "Absorbing traffic spikes and DDoS at the edge.", "Caching public API responses for a few seconds."],
        [
            "Hit ratio drives everything: origin load = requests × (1 − hit ratio).",
            "Fingerprinted asset names + long max-age beat purging.",
            "Keep the cache key minimal; every extra Vary splits the cache.",
            "Origin shield collapses misses from many PoPs into one origin fetch.",
            "stale-while-revalidate and stale-if-error hide origin slowness and outages.",
        ],
        [
            ex("Hit ratio vs cache size (Zipf traffic)", "intermediate", "Popular objects dominate, so a small edge cache absorbs most requests.", "python", """
                import random
                from collections import OrderedDict
                random.seed(3)
                objects = 10_000
                weights = [1 / (i + 1) for i in range(objects)]
                reqs = random.choices(range(objects), weights, k=50_000)

                def hit_ratio(capacity):
                    cache, hits = OrderedDict(), 0
                    for o in reqs:
                        if o in cache:
                            hits += 1
                            cache.move_to_end(o)
                        else:
                            cache[o] = True
                            if len(cache) > capacity:
                                cache.popitem(last=False)
                    return hits / len(reqs)

                for cap in (100, 500, 2000):
                    h = hit_ratio(cap)
                    print(f"edge cache {cap:>5} objects: hit {h:.0%}, origin gets {1 - h:.0%} of traffic")
            """),
            ex("Cache key normalization", "basic", "Dropping irrelevant query params raises the hit ratio.", "python", """
                from urllib.parse import urlsplit, parse_qsl, urlencode
                KEEP = {"w", "h", "fmt"}

                def cache_key(url):
                    u = urlsplit(url)
                    q = sorted((k, v) for k, v in parse_qsl(u.query) if k in KEEP)
                    return f"{u.netloc}{u.path}?{urlencode(q)}"

                urls = ["https://img.example.com/a.jpg?w=200&utm_source=x",
                        "https://img.example.com/a.jpg?utm_campaign=y&w=200",
                        "https://img.example.com/a.jpg?w=200&fbclid=123"]
                print({cache_key(u) for u in urls})
            """),
            ex("Cache-Control recipes", "basic", "Headers the origin should send.", "text", """
                # fingerprinted static asset: app.3f9c2a.js
                Cache-Control: public, max-age=31536000, immutable
                # HTML shell: always revalidate
                Cache-Control: no-cache
                # public API list, edge caches 10 s, serves stale while refreshing
                Cache-Control: public, s-maxage=10, stale-while-revalidate=30, stale-if-error=300
                # personalized responses
                Cache-Control: private, no-store
            """, runnable=False),
        ],
        ["Origin rps = total rps × (1 − hit ratio)", "Static: max-age=31536000, immutable + hashed names", "s-maxage for shared caches, max-age for browsers", "stale-while-revalidate=30 · stale-if-error=300", "Purge by surrogate key/tag, not wildcard"],
        ["Caching responses that set cookies or vary per user (data leak).", "Including tracking query params or full cookies in the cache key.", "Relying on purges for every deploy instead of versioned URLs.", "Forgetting the CDN also needs TLS 1.3 and HSTS configured."],
        [
            qa("basic", "How does a CDN reduce latency?", "It serves content from a PoP close to the user, cutting the round-trip time, and reuses warm TCP/TLS connections to the origin. Only cache misses travel the long path to the origin."),
            qa("intermediate", "How do you deploy new static assets without stale content?", "Use content-hashed file names (app.3f9c2a.js) with a one-year immutable TTL, and serve the HTML that references them with no-cache. A deploy just changes the URLs in the HTML, so no purge is needed."),
            qa("intermediate", "What is an origin shield?", "A designated mid-tier cache between the edge PoPs and the origin. Misses from many PoPs collapse into a single fetch at the shield, raising the effective hit ratio and protecting the origin from thundering herds."),
            qa("advanced", "Can you cache API responses on a CDN?", "Yes for public, non-personalized data with short s-maxage and stale-while-revalidate, a tight cache key and correct Vary headers. Never cache responses that depend on Authorization or cookies unless the key includes the identity, and send private, no-store on personalized data."),
        ],
        ["caching", "dns", "blob-storage"],
        chain(
            ("User", "Mumbai", "Request", "The user requests /img/a.jpg; anycast routes them to the nearest PoP."),
            ("Edge PoP", "hit 92%", "Edge cache", "On a hit the PoP answers in ~10 ms. On a miss it asks the shield.", "GET"),
            ("Shield", "mid-tier cache", "Origin shield", "Misses from many PoPs collapse into one request here.", "miss"),
            ("Origin", "object store", "Origin fetch", "The origin returns the object with Cache-Control: max-age=31536000.", "miss"),
            ("Edge PoP", "now cached", "Fill and serve", "Shield and edge cache the response; next users get a hit.", "200 + headers"),
        ),
    ),
    topic(
        "api-design", "API Design: REST, gRPC & GraphQL", "edge-api", "intermediate", "AP",
        "Resource modeling, status codes, versioning, and when to pick each style.",
        "REST is a well-labeled filing cabinet, gRPC is a direct phone line with a strict script, and GraphQL is a personal shopper you hand a precise list to.",
        "REST models resources with nouns and standard HTTP verbs: GET is safe and cacheable, PUT and DELETE are idempotent, POST creates or triggers actions, and PATCH applies partial updates. Good REST APIs use consistent plural resource paths, meaningful status codes (201, 204, 400, 404, 409, 412, 422, 429), a uniform error body, pagination, and ETags for caching and optimistic concurrency. gRPC uses HTTP/2 with Protocol Buffers contracts, giving compact payloads, generated clients, deadlines and streaming, which suits internal service-to-service calls. GraphQL exposes a typed schema where clients choose fields, which helps aggregate many backends for varied UIs, but needs query depth/cost limits, persisted queries and DataLoader-style batching to avoid N+1 queries. Evolve APIs additively: add optional fields, never change meanings, and version (URL or header) only for breaking changes. Every API needs authentication, authorization per resource, input validation against a schema, and rate limits.",
        ["Public partner APIs (REST + OpenAPI).", "Low-latency internal RPC with streaming (gRPC).", "Mobile/web backends-for-frontends aggregating many services (GraphQL).", "Optimistic concurrency on edits with ETag/If-Match."],
        [
            "Safe: GET/HEAD. Idempotent: GET, PUT, DELETE. Not idempotent: POST (use idempotency keys).",
            "Errors: one shape, e.g. RFC 9457 problem+json with type, title, detail.",
            "Backward compatible changes only: add optional fields; tolerate unknown ones.",
            "gRPC: always set deadlines; propagate them downstream.",
            "GraphQL: limit depth and cost, batch resolvers, disable introspection in production.",
        ],
        [
            ex("ETag optimistic concurrency", "intermediate", "If-Match prevents lost updates between two editors.", "python", """
                import hashlib, json
                doc = {"id": 7, "title": "Draft", "version": 1}

                def etag(d):
                    return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()[:12]

                def patch(if_match, changes):
                    global doc
                    if if_match != etag(doc):
                        return 412, "Precondition Failed: reload and retry"
                    doc = {**doc, **changes, "version": doc["version"] + 1}
                    return 200, etag(doc)

                alice = bob = etag(doc)
                print("alice:", patch(alice, {"title": "Final"}))
                print("bob:  ", patch(bob, {"title": "Oops"}))
                print("doc:  ", doc)
            """),
            ex("Status code cheat-sheet as code", "basic", "Map outcomes to the right HTTP codes.", "python", """
                OUTCOMES = {
                    "created": 201, "deleted / no body": 204, "malformed JSON": 400, "not logged in": 401,
                    "logged in, not allowed": 403, "missing resource": 404, "duplicate / state conflict": 409,
                    "ETag mismatch": 412, "valid JSON, invalid fields": 422, "rate limited": 429, "bug": 500, "dependency down": 503,
                }
                for outcome, code in OUTCOMES.items():
                    print(f"{code}  {outcome}")
            """),
            ex("gRPC contract", "intermediate", "Protobuf service with a server-streaming method.", "protobuf", """
                syntax = "proto3";
                package orders.v1;

                service Orders {
                  rpc GetOrder(GetOrderRequest) returns (Order);
                  rpc WatchOrders(WatchOrdersRequest) returns (stream Order);
                }
                message GetOrderRequest { string order_id = 1; }
                message WatchOrdersRequest { string customer_id = 1; }
                message Order { string order_id = 1; string status = 2; int64 total_cents = 3; }
            """, runnable=False),
        ],
        ["GET /v1/orders?limit=50&cursor=… · POST /v1/orders · PATCH /v1/orders/{id}", "If-None-Match → 304 · If-Match → 412 on conflict", "Content-Type: application/problem+json", "gRPC: deadline 300ms, status DEADLINE_EXCEEDED", "GraphQL: maxDepth 8, cost limit, persisted queries"],
        ["Verbs in URLs (/getOrder) and 200 OK with an error inside the body.", "Breaking clients by renaming fields or reusing protobuf field numbers.", "GraphQL N+1 resolvers hammering the database.", "Leaking internal exceptions and stack traces in error bodies."],
        [
            qa("basic", "Which HTTP methods are idempotent and why does it matter?", "GET, HEAD, PUT, DELETE and OPTIONS are idempotent: repeating them leaves the same state. Clients, proxies and retry libraries can safely retry them after timeouts, whereas POST and PATCH need idempotency keys or conditional requests."),
            qa("intermediate", "REST vs gRPC vs GraphQL: when would you use each?", "REST for public, cacheable, broadly compatible APIs; gRPC for internal low-latency calls with strict contracts, deadlines and streaming; GraphQL when many clients need different shapes of data aggregated from several services. Many systems use gRPC internally and REST or GraphQL at the edge."),
            qa("intermediate", "How do you version an API?", "Prefer additive, backward-compatible evolution so most changes need no version. For breaking changes, introduce a new major version (/v2 or a header), run both in parallel, communicate a deprecation timeline with Sunset headers, and track usage before removal."),
            qa("advanced", "How do you prevent lost updates in a REST API?", "Use optimistic concurrency: return an ETag (or version) with the resource and require If-Match on updates. The server applies the change only if the current version matches, otherwise returns 412 so the client re-reads and merges."),
            qa("advanced", "What protections does a GraphQL endpoint need?", "Query depth and complexity limits, pagination limits, timeouts, persisted or allow-listed queries for public clients, field-level authorization, and batching (DataLoader) to avoid N+1 queries. Disable introspection and GraphiQL in production."),
        ],
        ["idempotency-keys", "pagination", "microservices-gateway"],
        chain(
            ("Client", "PATCH /orders/7", "Request", "The client sends a partial update with If-Match: \"a1b2\" and a bearer token."),
            ("Gateway", "auth + rate limit", "Edge checks", "The gateway validates the token, enforces quotas and the JSON schema.", "PATCH"),
            ("Service", "orders.v1", "Business logic", "The service authorizes this user for order 7 and checks the ETag.", "validated"),
            ("Database", "version = 3", "Conditional write", "UPDATE … WHERE id = 7 AND version = 3; zero rows means a conflict.", "UPDATE"),
            ("Response", "200 / 412", "Reply", "200 with a new ETag, or 412 problem+json telling the client to reload.", "result"),
        ),
    ),
    topic(
        "idempotency-keys", "Idempotency Keys", "edge-api", "intermediate", "IK",
        "Make retries safe: the same request applied twice has the effect of once.",
        "A coat check ticket: hand in the same ticket twice and you get the same coat, not two coats.",
        "Networks fail ambiguously: a client that times out cannot tell whether the server never got the request, processed it, or crashed halfway. Retrying a non-idempotent operation like 'charge $50' can then double-charge. An idempotency key is a client-generated unique id (UUIDv4) sent with the request; the server stores key → (request fingerprint, status, response) and, on a repeat, returns the stored response instead of re-executing. The record must be created atomically before work starts (insert with a unique constraint) so two concurrent retries cannot both run; a concurrent duplicate gets 409 or waits. The fingerprint (SHA-256 of the canonical body) detects a reused key with a different payload, which should be rejected with 422. Keys are scoped per client/account and expire after a retention window (Stripe uses 24 hours). Downstream, the same idea appears as dedup tables on consumers and natural keys (order_id) with unique constraints.",
        ["Payment and order creation APIs.", "Mobile clients retrying on flaky networks.", "Queue consumers handling at-least-once delivery.", "Webhook receivers that get the same event twice."],
        [
            "The client generates the key once per logical operation and reuses it on every retry.",
            "Reserve the key atomically (unique constraint) before doing side effects.",
            "Store the full response so replays are byte-identical.",
            "Same key + different body = client bug → 422.",
            "Scope keys per tenant and expire them (e.g. 24 h).",
        ],
        [
            ex("Idempotent charge endpoint", "intermediate", "Retries return the stored response; a reused key with a different body is rejected.", "python", """
                import hashlib, json, uuid
                store, ledger = {}, []

                def charge(key, body):
                    fp = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
                    if key in store:
                        saved_fp, resp = store[key]
                        return resp if saved_fp == fp else (422, "key reused with a different body")
                    store[key] = (fp, (102, "in progress"))
                    ledger.append(body["amount"])
                    resp = (201, f"charge ch_{len(ledger)} for {body['amount']}")
                    store[key] = (fp, resp)
                    return resp

                key = str(uuid.UUID(int=12345))
                print(charge(key, {"amount": 50}))
                print(charge(key, {"amount": 50}), "(retry after timeout)")
                print(charge(key, {"amount": 99}))
                print("ledger:", ledger)
            """),
            ex("Consumer dedup with a processed set", "basic", "At-least-once delivery made effectively-once.", "python", """
                deliveries = ["m1", "m2", "m2", "m3", "m1"]
                processed, emails = set(), []
                for msg_id in deliveries:
                    if msg_id in processed:
                        print("skip duplicate", msg_id)
                        continue
                    emails.append(msg_id)
                    processed.add(msg_id)
                print("emails sent:", emails)
            """),
            ex("SQL schema for keys", "intermediate", "Unique constraint makes reservation atomic.", "sql", """
                CREATE TABLE idempotency_keys (
                  account_id   BIGINT      NOT NULL,
                  idem_key     UUID        NOT NULL,
                  request_hash CHAR(64)    NOT NULL,  -- SHA-256 hex
                  status       TEXT        NOT NULL,  -- started | completed
                  response     JSONB,
                  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
                  PRIMARY KEY (account_id, idem_key)
                );
                -- reserve: INSERT ... ON CONFLICT DO NOTHING; 0 rows means replay or in-flight
            """, runnable=False),
        ],
        ["Header: Idempotency-Key: <uuid v4>", "PRIMARY KEY (account_id, idem_key)", "Fingerprint = SHA-256(canonical body)", "Replay → stored response · in-flight → 409 · body mismatch → 422", "Retention ~24 h, then purge"],
        ["Checking then inserting without a unique constraint (race lets two retries run).", "Generating a new key on each retry, which defeats the purpose.", "Storing the key only after the side effect, so a crash in between replays the charge."],
        [
            qa("basic", "Why are idempotency keys needed if we already use HTTPS?", "Transport security does not solve ambiguity: on a timeout the client cannot know whether the server applied the request. Keys let it retry safely because the server recognizes the repeat and returns the original result."),
            qa("intermediate", "How do you handle two concurrent requests with the same key?", "Reserve the key with an atomic insert under a unique constraint before doing work. The loser sees the row in 'started' state and returns 409 (or waits briefly and returns the final response), so the side effect runs once."),
            qa("intermediate", "What do you store with the key?", "The scope (account), a hash of the request body, the processing status, and the final response code and body. The hash catches key reuse with different parameters, and the stored response makes replays identical."),
            qa("advanced", "How does idempotency extend to downstream calls?", "Propagate a derived key (e.g. the payment id) to the payment provider and to events, and make consumers dedupe on message or business ids with unique constraints. Each hop must be idempotent or the guarantee breaks at the weakest link."),
        ],
        ["api-design", "sagas", "exactly-once"],
        chain(
            ("Client", "key = 9f1c…", "Send with key", "The client creates one UUID for this checkout and sends it with POST /charges."),
            ("API", "INSERT key", "Reserve", "An insert with a unique constraint reserves the key in 'started' state.", "POST"),
            ("Payment", "charge once", "Side effect", "The charge runs and the response is saved next to the key.", "charge"),
            ("Timeout", "client retries", "Ambiguous failure", "The response is lost; the client retries with the same key.", "retry"),
            ("Replay", "stored 201", "Replay", "The API finds the completed key and returns the stored 201. No second charge.", "same key"),
        ),
    ),
    topic(
        "pagination", "Pagination at Scale", "edge-api", "intermediate", "PG",
        "Offset vs keyset cursors, stable ordering and opaque tokens.",
        "Offset pagination is counting 10,000 pages from the start of a book every time; a cursor is a bookmark you hand back.",
        "Offset pagination (LIMIT 50 OFFSET 10000) is simple and supports jumping to page N, but the database must scan and discard all skipped rows, so deep pages get slower, and concurrent inserts or deletes shift rows so users see duplicates or miss items. Keyset (seek) pagination remembers the last seen sort key and asks for rows after it: WHERE (created_at, id) < (:ts, :id) ORDER BY created_at DESC, id DESC LIMIT 50. With a matching composite index each page is an index range scan of constant cost regardless of depth, and results are stable under writes. The sort must be on a unique, deterministic key, so add the primary key as a tie-breaker. Expose the position as an opaque cursor (base64 of the last key, optionally signed with HMAC-SHA256 to prevent tampering) so you can change the implementation later. Total counts are expensive at scale; return has_more or an approximate count instead. For search engines and fan-out reads, use search_after or scroll/point-in-time APIs.",
        ["Infinite-scroll feeds and timelines.", "Public list APIs (Stripe-style starting_after).", "Batch exports that walk an entire table.", "Admin tables that need page numbers (offset, but bounded)."],
        [
            "Offset cost grows with depth: O(offset + limit).",
            "Keyset cost is O(limit) with an index on the sort columns.",
            "Always include a unique tie-breaker in ORDER BY.",
            "Cursors are opaque to clients; never let them encode raw SQL.",
            "Prefer has_more over COUNT(*) on large tables.",
        ],
        [
            ex("Offset drift vs keyset stability", "intermediate", "A new item arrives between page requests.", "python", """
                items = [{"id": i, "ts": 100 - i} for i in range(1, 11)]

                def newest_first():
                    return sorted(items, key=lambda r: (r["ts"], r["id"]), reverse=True)

                def offset_page(offset, limit=3):
                    return [r["id"] for r in newest_first()[offset:offset + limit]]

                def keyset_page(after, limit=3):
                    rows = [r for r in newest_first() if after is None or (r["ts"], r["id"]) < after]
                    page = rows[:limit]
                    return [r["id"] for r in page], ((page[-1]["ts"], page[-1]["id"]) if page else None)

                p1 = offset_page(0)
                k1, cursor = keyset_page(None)
                items.append({"id": 99, "ts": 200})
                print("offset page 1, 2:", p1, offset_page(3), "<- id 3 repeated")
                print("keyset page 1, 2:", k1, keyset_page(cursor)[0])
            """),
            ex("Opaque, signed cursor", "advanced", "Base64 JSON plus an HMAC-SHA256 tag; the key is generated at runtime, never hardcoded.", "python", """
                import base64, hashlib, hmac, json, secrets
                KEY = secrets.token_bytes(32)

                def encode(pos):
                    raw = json.dumps(pos, separators=(",", ":")).encode()
                    tag = hmac.new(KEY, raw, hashlib.sha256).digest()[:16]
                    return base64.urlsafe_b64encode(raw + tag).decode().rstrip("=")

                def decode(cur):
                    blob = base64.urlsafe_b64decode(cur + "=" * (-len(cur) % 4))
                    raw, tag = blob[:-16], blob[-16:]
                    if not hmac.compare_digest(tag, hmac.new(KEY, raw, hashlib.sha256).digest()[:16]):
                        raise ValueError("tampered cursor")
                    return json.loads(raw)

                c = encode({"ts": 1700000000, "id": 42})
                print(c, decode(c))
                try:
                    decode(c[:-2] + ("A" if c[-2] != "A" else "B") + c[-1])
                except ValueError as e:
                    print("rejected:", e)
            """),
            ex("Keyset query and index", "basic", "Row-value comparison with a matching index.", "sql", """
                CREATE INDEX posts_feed ON posts (author_id, created_at DESC, id DESC);

                SELECT id, created_at, body
                FROM posts
                WHERE author_id = :author
                  AND (created_at, id) < (:last_ts, :last_id)
                ORDER BY created_at DESC, id DESC
                LIMIT 50;
            """, runnable=False),
        ],
        ["Offset: LIMIT 50 OFFSET n (slow when n is large)", "Keyset: WHERE (ts,id) < (:ts,:id) ORDER BY ts DESC, id DESC", "Response: {data, next_cursor, has_more}", "Cap page size (e.g. max 100)", "Elasticsearch: search_after + point in time"],
        ["Sorting by a non-unique column without a tie-breaker, causing skipped rows.", "Running COUNT(*) on every page of a huge table.", "Accepting unlimited page sizes from clients."],
        [
            qa("basic", "Why is OFFSET pagination slow for deep pages?", "The database still reads and discards every skipped row, so page 10,000 costs about 500,000 row visits. Latency grows linearly with depth."),
            qa("intermediate", "How does keyset pagination work?", "The client sends the sort key of the last row it saw, and the query fetches rows strictly after it using an index on the same columns. Each page is a cheap index range scan and stays correct when rows are inserted or deleted."),
            qa("intermediate", "Why make cursors opaque?", "It hides the internal sort keys, lets you change the strategy later without breaking clients, and if signed prevents clients from forging positions. Clients treat it as a token to pass back."),
            qa("advanced", "How do you paginate results merged from many shards?", "Each shard returns its own top-N after the cursor; the aggregator merges by the global sort key and returns the top N, and the cursor stores the last global key (or per-shard positions). Deep pagination stays bounded because each shard does a keyset scan."),
        ],
        ["api-design", "indexes-at-scale", "case-news-feed"],
        chain(
            ("Client", "GET ?limit=50", "First page", "No cursor yet: fetch the newest 50 rows."),
            ("API", "decode cursor", "Decode", "On later pages, verify the cursor's HMAC and read (ts, id).", "cursor"),
            ("Index scan", "(ts, id) < …", "Seek", "The index jumps straight to the position and reads 51 rows.", "range"),
            ("Response", "next_cursor", "Return", "Return 50 rows, has_more from the 51st, and a new opaque cursor.", "rows"),
        ),
    ),
    topic(
        "realtime-delivery", "WebSockets, SSE & Long Polling", "edge-api", "intermediate", "RT",
        "Pushing updates to clients: pick the simplest transport that fits.",
        "Short polling is asking 'are we there yet?' every minute; long polling is asking once and waiting for an answer; SSE is the driver announcing each town; a WebSocket is a two-way walkie-talkie.",
        "Short polling sends a request every N seconds, which is simple but wastes requests and adds up to N seconds of delay. Long polling holds the request open until data arrives or a timeout, then the client immediately re-requests, giving near-real-time updates over plain HTTP. Server-Sent Events (SSE) stream text events from server to client over one HTTP response, with automatic reconnect and Last-Event-ID resume; they are ideal for one-way feeds such as notifications, tickers and LLM token streams. WebSockets upgrade an HTTP connection to a full-duplex message channel, needed for chat, multiplayer and collaborative editing. Persistent connections change scaling: each server holds tens of thousands of sockets, load balancers need long idle timeouts and connection-aware balancing, and a pub/sub layer (Redis, Kafka, NATS) routes messages to the server holding the user's connection. Plan for reconnect storms after deploys with jittered backoff, heartbeats to detect dead connections, and resumable sequence numbers so no messages are lost.",
        ["Live notifications and dashboards (SSE).", "Chat and collaborative editing (WebSocket).", "Environments where proxies block upgrades (long polling fallback).", "Streaming AI responses token by token (SSE)."],
        [
            "Start with SSE if traffic is server-to-client only.",
            "Connections are stateful: route messages via pub/sub to the holding server.",
            "Heartbeats (ping/pong every 20-30 s) detect half-open connections.",
            "Resume with sequence numbers or Last-Event-ID after reconnect.",
            "Jittered reconnect backoff prevents thundering herds after deploys.",
        ],
        [
            ex("Polling cost vs push", "basic", "Requests and average delay for 100k clients.", "python", """
                clients = 100_000
                events_per_client_hour = 6
                for interval in (5, 30, 60):
                    rps = clients / interval
                    useful = clients * events_per_client_hour / 3600
                    print(f"poll every {interval:>2}s: {rps:>8,.0f} rps, {useful / rps:5.1%} useful, avg delay {interval / 2:.1f}s")
                print(f"push (SSE/WS): {clients * events_per_client_hour / 3600:,.0f} msgs/s, delay ~network RTT")
            """),
            ex("SSE resume with Last-Event-ID", "intermediate", "The server replays missed events after a reconnect.", "python", """
                log = [(i, f"price tick {i}") for i in range(1, 11)]

                def stream(last_event_id=0):
                    for eid, data in log:
                        if eid > last_event_id:
                            yield f"id: {eid}|data: {data}"

                seen = 0
                for line in stream():
                    seen = int(line.split("|")[0].split(": ")[1])
                    if seen == 4:
                        print("connection dropped after id", seen)
                        break
                print("reconnect with Last-Event-ID:", seen)
                print([l for l in stream(seen)][:3], "...")
            """),
            ex("Nginx WebSocket proxying", "intermediate", "Upgrade headers and long timeouts.", "nginx", """
                map $http_upgrade $connection_upgrade { default upgrade; '' close; }
                server {
                    listen 443 ssl;
                    ssl_protocols TLSv1.3;
                    location /ws/ {
                        proxy_pass http://chat_backend;
                        proxy_http_version 1.1;
                        proxy_set_header Upgrade $http_upgrade;
                        proxy_set_header Connection $connection_upgrade;
                        proxy_read_timeout 3600s;
                    }
                }
            """, runnable=False),
        ],
        ["SSE: Content-Type: text/event-stream", "WS: Upgrade: websocket (101 Switching Protocols)", "Heartbeat 25 s; idle timeout > heartbeat", "Reconnect: min(30s, 2^n) × random jitter", "Connection registry: user → gateway node"],
        ["Load balancer idle timeout (often 60 s) silently killing quiet sockets.", "Deploys dropping all connections at once and causing a reconnect storm.", "Assuming delivery: no acks or sequence numbers means lost messages on reconnect."],
        [
            qa("basic", "When would you choose SSE over WebSockets?", "When data flows only from server to client: SSE is plain HTTP, works through most proxies, auto-reconnects and resumes with Last-Event-ID. WebSockets are needed when the client also sends frequent low-latency messages."),
            qa("intermediate", "How does long polling work?", "The client sends a request that the server holds open until there is data or a timeout (say 30 s); the server responds and the client immediately sends the next request. It gives near-real-time delivery using only regular HTTP, at the cost of extra request overhead."),
            qa("intermediate", "How do you scale WebSocket servers horizontally?", "Keep connections on stateless gateway nodes, store user → node mappings in a registry, and fan messages out through pub/sub so any service can reach any user. Use connection-aware load balancing and drain connections gradually during deploys."),
            qa("advanced", "How do you avoid losing messages when a client reconnects?", "Assign per-user or per-channel sequence numbers, persist messages, and have the client acknowledge and reconnect with its last sequence. The server replays everything after it, and clients dedupe by id."),
        ],
        ["case-chat", "event-driven", "load-balancing"],
        chain(
            ("Client", "EventSource", "Connect", "The browser opens GET /events with Accept: text/event-stream."),
            ("Gateway", "holds 50k conns", "Hold connection", "A gateway node keeps the response open and registers user → node.", "subscribe"),
            ("Pub/sub", "Redis / NATS", "Publish", "A backend publishes an event for the user to the channel.", "event"),
            ("Gateway", "id: 42", "Push", "The holding node writes 'id: 42 data: …' down the open stream.", "msg"),
            ("Client", "Last-Event-ID", "Resume", "After a drop the client reconnects with Last-Event-ID: 42 and gets the rest.", "reconnect"),
        ),
    ),
    topic(
        "auth-tokens", "AuthN/AuthZ: OAuth2, OIDC, JWT & TLS 1.3", "edge-api", "advanced", "AU",
        "Who are you, what may you do, and how services verify tokens safely.",
        "OAuth is a hotel key card: the front desk (authorization server) checks your ID once, then the card opens only your room and the gym, and stops working at checkout time.",
        "Authentication establishes identity; authorization decides what that identity may do. OAuth 2.0 is a delegation framework: a client obtains an access token from an authorization server and presents it to resource servers. For browser and mobile apps use the Authorization Code flow with PKCE; services use the Client Credentials flow; avoid the implicit and password grants. OpenID Connect adds an ID token (a JWT) that tells the client who logged in. A JWT is a signed JSON claim set; resource servers validate it locally by verifying the signature with keys from the issuer's JWKS endpoint, pinning the expected algorithm (ES256 or RS256, never 'none'), and checking iss, aud, exp, nbf and scopes. Access tokens should be short-lived (5-15 minutes) with rotating refresh tokens, because self-contained JWTs cannot be revoked instantly; use opaque tokens with introspection when instant revocation matters. In transit, enforce TLS 1.3 (or 1.2 with AEAD ciphers only), HSTS, and mTLS between services where possible.",
        ["Single sign-on across web apps with OIDC.", "Machine-to-machine API access with client credentials.", "An API gateway validating JWTs before routing.", "Zero-trust service-to-service calls with mTLS."],
        [
            "Authorization Code + PKCE for public clients; never the implicit flow.",
            "Validate signature, alg (pinned), iss, aud, exp, nbf, then scopes.",
            "Fetch and cache JWKS; support key rotation by kid.",
            "Short access tokens + rotating refresh tokens; revoke refresh on logout.",
            "Authorize every request against the specific resource (prevent IDOR).",
        ],
        [
            ex("Validate an HS256 JWT with the standard library", "advanced", "Demonstrates the checks; real deployments use a vetted library and asymmetric keys from JWKS. The key is generated at runtime.", "python", """
                import base64, hashlib, hmac, json, secrets, time
                KEY = secrets.token_bytes(32)
                b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
                unb64 = lambda s: base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

                def sign(claims):
                    head = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
                    body = b64(json.dumps(claims).encode())
                    sig = hmac.new(KEY, f"{head}.{body}".encode(), hashlib.sha256).digest()
                    return f"{head}.{body}.{b64(sig)}"

                def verify(token, aud, iss, now):
                    head, body, sig = token.split(".")
                    if json.loads(unb64(head)).get("alg") != "HS256":
                        return "reject: unexpected alg"
                    good = hmac.new(KEY, f"{head}.{body}".encode(), hashlib.sha256).digest()
                    if not hmac.compare_digest(good, unb64(sig)):
                        return "reject: bad signature"
                    c = json.loads(unb64(body))
                    if c["iss"] != iss or c["aud"] != aud:
                        return "reject: wrong issuer/audience"
                    if now >= c["exp"]:
                        return "reject: expired"
                    return f"ok: sub={c['sub']} scope={c['scope']}"

                now = int(time.time())
                t = sign({"iss": "https://id.example.com", "aud": "orders-api", "sub": "u42", "scope": "orders:read", "exp": now + 600})
                print(verify(t, "orders-api", "https://id.example.com", now))
                print(verify(t, "billing-api", "https://id.example.com", now))
                print(verify(t, "orders-api", "https://id.example.com", now + 601))
                print(verify(t[:-3] + "AAA", "orders-api", "https://id.example.com", now))
            """),
            ex("PKCE verifier and challenge", "intermediate", "S256 challenge derived from a random verifier.", "python", """
                import base64, hashlib, secrets
                verifier = secrets.token_urlsafe(48)
                challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
                print("send in /authorize: code_challenge =", challenge, "method = S256")
                print("send in /token:     code_verifier length =", len(verifier))
            """),
            ex("TLS 1.3 only (nginx)", "intermediate", "Modern transport settings.", "nginx", """
                server {
                    listen 443 ssl;
                    http2 on;
                    ssl_protocols TLSv1.3;
                    ssl_ecdh_curve X25519:prime256v1;
                    ssl_certificate     /etc/ssl/certs/api.pem;      # verify expiry, key size, SHA-256 signature
                    ssl_certificate_key /etc/ssl/private/api.key;    # loaded from a secret store, never committed
                    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
                }
            """, runnable=False),
        ],
        ["Browser/mobile: Authorization Code + PKCE (S256)", "Service-to-service: client credentials or mTLS", "JWT checks: alg pinned · sig · iss · aud · exp · nbf · scope", "Access token 5-15 min · refresh token rotated", "TLS 1.3 · HSTS max-age=31536000"],
        ["Accepting alg from the token header (alg=none or RS/HS confusion).", "Long-lived JWTs that cannot be revoked after a breach.", "Storing tokens in localStorage where XSS can read them.", "Checking authentication but not per-resource authorization."],
        [
            qa("basic", "What is the difference between OAuth 2.0 and OpenID Connect?", "OAuth 2.0 delegates authorization: it issues access tokens for calling APIs. OIDC is an identity layer on top that adds an ID token and userinfo endpoint so the client learns who the user is."),
            qa("intermediate", "How should a resource server validate a JWT?", "Pin the expected algorithm, find the key by kid in the issuer's cached JWKS, verify the signature, then check iss, aud, exp and nbf with small clock skew, and finally enforce scopes and per-resource authorization. Reject anything that fails any step."),
            qa("intermediate", "Why use PKCE?", "Public clients cannot keep a client secret, so an intercepted authorization code could be redeemed by an attacker. PKCE binds the code to a random verifier known only to the original client, which must present it when exchanging the code."),
            qa("advanced", "JWT vs opaque tokens: trade-offs?", "JWTs are validated locally without a network call, which scales well, but cannot be revoked before expiry, so keep them short-lived. Opaque tokens require introspection or a cache but can be revoked instantly; many systems use opaque tokens at the edge and short internal JWTs."),
            qa("advanced", "What does TLS 1.3 improve over TLS 1.2?", "A one round-trip handshake (0-RTT optional, with replay caveats), mandatory forward secrecy via ephemeral (EC)DHE, and only AEAD cipher suites such as AES-256-GCM and ChaCha20-Poly1305. Legacy options like static RSA key exchange, CBC modes and renegotiation were removed."),
        ],
        ["api-design", "microservices-gateway", "rate-limiting"],
        chain(
            ("User", "login + MFA", "Authenticate", "The app redirects to the identity provider with a PKCE challenge."),
            ("IdP", "code → tokens", "Issue tokens", "After login the app exchanges the code + verifier for access and ID tokens.", "code"),
            ("Gateway", "verify JWT", "Validate", "Signature via JWKS, alg pinned, iss/aud/exp checked, scopes read.", "Bearer"),
            ("Service", "owns order 7?", "Authorize", "The service checks this user may access this specific resource.", "identity"),
            ("Response", "TLS 1.3", "Respond", "Data returns over TLS 1.3; the token expires in 10 minutes.", "200"),
        ),
    ),
    topic(
        "case-typeahead", "Case Study: Typeahead / Autocomplete", "case-studies", "advanced", "TA",
        "Top-k suggestions per prefix in under 100 ms, built offline and served from memory.",
        "A librarian who has already sorted, for every first few letters, the ten most borrowed titles, so they answer instantly instead of searching the shelves.",
        "Typeahead returns the top k completions for a prefix on every keystroke, so it needs p99 under ~100 ms end-to-end and handles very high QPS (each search produces several requests). The core structure is a trie where each node stores the precomputed top-k completions for its prefix, making a lookup O(prefix length) instead of a subtree scan. Popularity scores come from an offline pipeline over search logs (counts with time decay), rebuilt hourly or daily, plus a small streaming layer for trending queries. The trie is sharded by prefix range or hash of the first characters and replicated; it is small enough to sit in memory, and results for short prefixes are cached at the CDN and in the browser. Clients debounce keystrokes (~100 ms), cancel stale requests and cache prior results. Filtering removes offensive or personal queries, and personalization blends global results with the user's recent searches.",
        ["Search box suggestions for a web search or e-commerce site.", "Contact or command palette completion.", "Tag and location autocompletion in forms."],
        [
            "Precompute top-k per trie node; serving is a pointer walk.",
            "Build offline from logs with time decay; hot-swap the new trie.",
            "Shard by prefix; cache short prefixes aggressively (few distinct values).",
            "Client: debounce, cancel in-flight requests, cache per prefix.",
            "Filter and blocklist before data reaches the index.",
        ],
        [
            ex("Trie with precomputed top-k", "advanced", "Builds from query counts and answers prefixes.", "python", """
                import heapq
                counts = {"system design": 900, "system of a down": 400, "systemd": 650, "syntax error": 300,
                          "symbolic link": 120, "sydney weather": 500, "sync folders": 220}
                K = 3
                root = {}

                for q, c in counts.items():
                    node = root
                    for ch in q:
                        node = node.setdefault(ch, {})
                        top = node.setdefault("$top", [])
                        heapq.heappush(top, (c, q))
                        if len(top) > K:
                            heapq.heappop(top)

                def suggest(prefix):
                    node = root
                    for ch in prefix:
                        if ch not in node:
                            return []
                        node = node[ch]
                    return [q for c, q in sorted(node["$top"], reverse=True)]

                for p in ("s", "sy", "sys", "syn", "x"):
                    print(f"{p!r:7} -> {suggest(p)}")
            """),
            ex("Time-decayed popularity", "intermediate", "Recent searches count more than old ones.", "python", """
                import math
                half_life_days = 7
                events = {"world cup": [(0, 5000), (30, 200000)], "tax return": [(1, 30000), (2, 30000)]}

                def score(hist):
                    return sum(n * math.exp(-math.log(2) * age / half_life_days) for age, n in hist)

                for q, hist in events.items():
                    print(f"{q:12} score {score(hist):>10,.0f}")
            """),
        ],
        ["Latency budget: < 100 ms p99 end to end", "Client debounce ~100 ms, min 1-2 chars", "Trie node: children + top-k list", "Rebuild hourly/daily; trending via stream", "Cache prefixes ≤ 2 chars at CDN"],
        ["Scanning the subtree per request instead of precomputing top-k.", "Updating the live trie on every search (write contention); batch instead.", "Not filtering offensive, private or legally sensitive suggestions."],
        [
            qa("intermediate", "Why store top-k at each trie node?", "Without it, each request walks the whole subtree under the prefix and sorts, which is expensive for short prefixes with millions of completions. Precomputing makes lookups O(length of prefix) at the cost of extra memory and offline build time."),
            qa("advanced", "How do you keep suggestions fresh?", "Aggregate search logs offline with time decay and rebuild the trie periodically, swapping it in atomically. For trends, a streaming job counts recent queries in sliding windows and a small 'trending' index is merged with the base results at query time."),
            qa("advanced", "How would you scale the service?", "Shard tries by prefix range (balanced by traffic, not alphabet), replicate each shard, keep them in memory, and cache very short prefixes at the CDN and client. Load is dominated by reads, so replicas scale linearly."),
            qa("intermediate", "What client-side optimizations matter?", "Debounce keystrokes, cancel outdated requests so responses do not arrive out of order, cache prior prefix results locally, and prefetch the next likely prefix."),
        ],
        ["caching", "search-systems", "data-pipelines"],
        chain(
            ("Keystroke", "'sys'", "User types", "The client debounces for 100 ms and checks its local prefix cache."),
            ("CDN/edge", "short prefixes", "Edge cache", "Short prefixes are cached for minutes at the edge.", "GET ?q=sys"),
            ("Router", "shard by prefix", "Route", "The request goes to the shard owning prefixes 'sx'-'tb'.", "miss"),
            ("Trie", "top-3 at node", "Lookup", "Walk s → y → s and read the precomputed top-3 list.", "prefix"),
            ("Builder", "logs → trie", "Offline rebuild", "Hourly jobs aggregate logs with decay and hot-swap a new trie.", "snapshot"),
        ),
    ),
    topic(
        "database-selection", "Choosing a Database", "building-blocks", "basic", "DB",
        "Start from access patterns, consistency needs and scale, not from fashion.",
        "Picking a vehicle: a sedan (relational) handles most trips well; a truck (wide-column) hauls huge loads on fixed routes; a taxi app (key-value) is perfect for quick point-to-point hops.",
        "Database choice follows from access patterns, consistency requirements, data shape and scale. Relational databases (PostgreSQL, MySQL) give ACID transactions, joins, constraints and flexible queries, and with replicas and partitioning they handle far more than most products need; they are the default. Key-value stores (Redis, DynamoDB) serve point lookups by key at very low latency and scale horizontally, but queries outside the key design are expensive. Wide-column stores (Cassandra, ScyllaDB, Bigtable) excel at massive write throughput and partition-plus-range reads like time series and message history. Document stores (MongoDB) suit nested, evolving records read as a whole. Search engines (Elasticsearch, OpenSearch) handle full-text and faceted queries, graph databases traverse relationships, and columnar warehouses (BigQuery, Snowflake, ClickHouse) scan billions of rows for analytics. Real systems are polyglot: a transactional source of truth plus derived stores fed by change data capture.",
        ["Picking the source of truth for orders and payments.", "Storing chat history or IoT time series at high write rates.", "Adding search or analytics alongside the primary store.", "Justifying a NoSQL choice in an interview."],
        [
            "Default to a relational DB until a concrete requirement rules it out.",
            "NoSQL models data around queries: design keys from access patterns first.",
            "Money and inventory need transactions and constraints.",
            "Derived stores (search, cache, warehouse) are fed by CDC, not dual writes.",
            "Operational maturity (backups, tooling, team skill) matters as much as features.",
        ],
        [
            ex("Requirement-driven chooser", "basic", "A toy rule set that mirrors interview reasoning.", "python", """
                def choose(req):
                    if req.get("analytics"):
                        return "columnar warehouse (BigQuery / Snowflake / ClickHouse)"
                    if req.get("full_text"):
                        return "search engine (OpenSearch) fed from the primary DB"
                    if req.get("transactions") or req.get("joins"):
                        return "relational (PostgreSQL), add replicas/partitioning as needed"
                    if req.get("writes_per_sec", 0) > 100_000 and req.get("access") == "partition+range":
                        return "wide-column (Cassandra / ScyllaDB)"
                    if req.get("access") == "key":
                        return "key-value (DynamoDB / Redis)"
                    return "relational (PostgreSQL) - the safe default"

                cases = {
                    "payments": {"transactions": True},
                    "chat history": {"writes_per_sec": 500_000, "access": "partition+range"},
                    "session store": {"access": "key"},
                    "product search": {"full_text": True},
                    "BI dashboards": {"analytics": True},
                }
                for name, req in cases.items():
                    print(f"{name:15} -> {choose(req)}")
            """),
            ex("Same query, two data models", "intermediate", "Relational join vs a denormalized key-value item (sqlite3 in memory).", "python", """
                import sqlite3, json
                db = sqlite3.connect(":memory:")
                db.executescript('''
                    CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT);
                    CREATE TABLE orders(id INTEGER PRIMARY KEY, user_id INT REFERENCES users(id), total INT);
                    INSERT INTO users VALUES (1, 'asha');
                    INSERT INTO orders VALUES (10, 1, 500), (11, 1, 250);
                ''')
                print(db.execute("SELECT u.name, COUNT(*), SUM(o.total) FROM users u JOIN orders o ON o.user_id = u.id GROUP BY u.id").fetchall())

                kv = {"user#1": json.dumps({"name": "asha", "orders": [{"id": 10, "total": 500}, {"id": 11, "total": 250}]})}
                item = json.loads(kv["user#1"])
                print(item["name"], len(item["orders"]), sum(o["total"] for o in item["orders"]))
            """),
        ],
        ["OLTP + joins + constraints → PostgreSQL/MySQL", "Point lookups at any scale → DynamoDB/Redis", "Huge writes, partition + range reads → Cassandra", "Full text / facets → OpenSearch", "Analytics scans → columnar warehouse"],
        ["Choosing NoSQL for 'scale' at 100 QPS and then reimplementing joins in code.", "Dual-writing to the DB and search index from the app (they drift apart).", "Designing a DynamoDB/Cassandra table before listing the queries."],
        [
            qa("basic", "SQL or NoSQL for a new product?", "Usually start with a relational database: ACID, flexible queries and mature tooling, and it scales further than people expect with indexes, replicas and partitioning. Choose NoSQL when a specific need appears, such as extreme write throughput, very simple key access at global scale, or a schema-less document model."),
            qa("intermediate", "When is a wide-column store a good fit?", "When writes are huge and reads follow a known pattern: fetch a partition (user, device, conversation) and a range within it (by time). Examples are time series, activity logs and chat history; ad-hoc queries and multi-row transactions are poor fits."),
            qa("intermediate", "How do you keep a search index in sync with the primary database?", "Treat the database as the source of truth and stream changes via CDC (Debezium, DynamoDB Streams) or an outbox to an indexer. Dual writes from the application risk inconsistency when one write fails."),
            qa("advanced", "What does 'model around access patterns' mean for DynamoDB?", "You list every query first, then design partition and sort keys (and a few GSIs) so each query is a single key or range read, often storing several entity types in one table. Queries not anticipated by the key design require scans or new indexes."),
        ],
        ["indexes-at-scale", "sharding", "search-systems"],
        chain(
            ("Requirements", "queries, SLAs", "List access patterns", "Write down the top queries, read:write ratio, consistency and growth."),
            ("Primary DB", "PostgreSQL", "Pick the source of truth", "Orders and payments need transactions, so a relational DB owns them.", "writes"),
            ("CDC stream", "Debezium/Kafka", "Stream changes", "Every committed change is captured from the WAL and published.", "changes"),
            ("Derived stores", "search, cache, DW", "Specialized reads", "Indexers fill OpenSearch, Redis and the warehouse from the stream.", "events"),
        ),
    ),
    topic(
        "indexes-at-scale", "Indexes at Scale", "building-blocks", "intermediate", "IX",
        "B-trees vs LSM trees, composite and covering indexes, and the write cost of every index.",
        "A book's index lets you jump to a page instead of reading the whole book, but every new page you write also means updating the index.",
        "An index is a secondary data structure that maps column values to row locations so queries avoid full scans. Most relational databases use B+ trees: balanced, shallow (3-4 levels for billions of rows), good for equality and range queries and ordered scans. LSM-tree engines (RocksDB, Cassandra) buffer writes in memory and flush sorted files, trading read amplification and compaction work for very high write throughput. Composite indexes follow the leftmost-prefix rule: an index on (tenant_id, created_at) serves 'WHERE tenant_id = ? ORDER BY created_at' but not 'WHERE created_at > ?' alone. A covering index includes all selected columns so the query never touches the table. Every index slows writes and uses memory, so index for the important queries, verify with EXPLAIN, and drop unused ones. At scale, build indexes online (CREATE INDEX CONCURRENTLY), watch for low-selectivity columns, and remember that global secondary indexes on sharded stores are often eventually consistent.",
        ["Fixing a slow endpoint found in the slow query log.", "Designing indexes for keyset pagination.", "Choosing an LSM store for write-heavy telemetry.", "Rolling out a new index on a 2 TB table without downtime."],
        [
            "Equality columns first, then range/sort columns, in composite indexes.",
            "Covering indexes remove table lookups for hot queries.",
            "Each index adds write amplification and memory pressure.",
            "Low-selectivity indexes (boolean flags) are rarely used; consider partial indexes.",
            "Always confirm with EXPLAIN on production-like data.",
        ],
        [
            ex("EXPLAIN before and after a composite index", "intermediate", "SQLite in memory shows the plan change.", "python", """
                import sqlite3, random
                random.seed(0)
                db = sqlite3.connect(":memory:")
                db.execute("CREATE TABLE events(id INTEGER PRIMARY KEY, tenant INT, ts INT, kind TEXT)")
                db.executemany("INSERT INTO events(tenant, ts, kind) VALUES (?,?,?)",
                               [(random.randint(1, 100), i, random.choice("abc")) for i in range(20000)])
                q = "SELECT ts, kind FROM events WHERE tenant = 42 ORDER BY ts DESC LIMIT 10"

                def plan():
                    return [r[3] for r in db.execute("EXPLAIN QUERY PLAN " + q)]

                print("before:", plan())
                db.execute("CREATE INDEX ev_tenant_ts ON events(tenant, ts)")
                print("composite:", plan())
                db.execute("CREATE INDEX ev_cover ON events(tenant, ts, kind)")
                print("covering:", plan())
            """),
            ex("B-tree depth for big tables", "basic", "Why lookups stay at a handful of page reads.", "python", """
                import math
                fanout = 400
                for rows in (1e6, 1e9, 1e12):
                    print(f"{rows:>8.0e} rows -> depth {math.ceil(math.log(rows, fanout))}")
            """),
            ex("Online and partial indexes (PostgreSQL)", "advanced", "Avoid long write locks; index only the rows you query.", "sql", """
                CREATE INDEX CONCURRENTLY orders_tenant_created
                    ON orders (tenant_id, created_at DESC) INCLUDE (status, total_cents);

                CREATE INDEX CONCURRENTLY orders_pending
                    ON orders (created_at) WHERE status = 'pending';

                EXPLAIN (ANALYZE, BUFFERS) SELECT status, total_cents FROM orders
                WHERE tenant_id = 42 ORDER BY created_at DESC LIMIT 20;
            """, runnable=False),
        ],
        ["Leftmost prefix: (a, b, c) serves a · a,b · a,b,c", "Equality first, then range, then sort", "CREATE INDEX CONCURRENTLY … INCLUDE (…)", "Partial index: WHERE status = 'pending'", "EXPLAIN (ANALYZE, BUFFERS)"],
        ["Indexing every column 'just in case' and slowing every write.", "Functions on indexed columns (WHERE lower(email) = …) without an expression index.", "Building a big index with a blocking lock during peak traffic."],
        [
            qa("basic", "How does a B-tree index speed up a query?", "It keeps keys sorted in a shallow, balanced tree of pages, so finding a key takes a few page reads (log base ~hundreds of N) instead of scanning every row. Leaf pages are linked, so range scans and ORDER BY are cheap too."),
            qa("intermediate", "What is the leftmost-prefix rule?", "A composite index on (a, b, c) can serve predicates on a, a+b, or a+b+c, and sort by them in order, but not queries filtering only on b or c. Put equality columns first and the range or sort column last."),
            qa("intermediate", "What is a covering index?", "An index that contains every column the query needs (key plus INCLUDE columns), so the database answers from the index alone without fetching table rows. It removes random I/O for hot read paths at the cost of a larger index."),
            qa("advanced", "B-tree vs LSM tree: when would you pick each?", "B-trees update in place and give predictable reads, suiting mixed OLTP workloads. LSM trees turn writes into sequential appends and background compaction, giving much higher write throughput but more read and space amplification, which suits write-heavy logs, metrics and wide-column stores."),
        ],
        ["database-selection", "pagination", "sharding"],
        chain(
            ("Query", "tenant=42 by ts", "Incoming query", "WHERE tenant = 42 ORDER BY ts DESC LIMIT 10."),
            ("Planner", "pick index", "Plan", "The planner sees an index on (tenant, ts) that matches filter and order.", "SQL"),
            ("B+ tree", "3 levels", "Seek", "Root → branch → leaf: three page reads to reach tenant 42's newest entry.", "seek"),
            ("Leaf scan", "10 entries", "Range scan", "Walk 10 entries backwards; with a covering index no table lookups are needed.", "range"),
            ("Result", "~1 ms", "Return", "Instead of scanning 20,000 rows, the query touched a handful of pages.", "rows"),
        ),
    ),
    topic(
        "cache-invalidation", "Cache Invalidation & Stampedes", "building-blocks", "advanced", "CI",
        "Keeping caches correct, and keeping cache misses from taking down the database.",
        "A whiteboard of today's specials: if nobody erases it when the kitchen runs out, customers order dishes that no longer exist. If you erase everything at once, every customer runs to the kitchen at the same time.",
        "Invalidation keeps cached data consistent with the source of truth. TTL expiry is simple and bounds staleness; explicit invalidation deletes or updates keys when data changes, ideally driven by change data capture so no write path is forgotten. Deleting (not updating) the key after the DB commit is the usual cache-aside rule, because concurrent updates can otherwise leave an older value in the cache; a short TTL bounds any remaining race. Versioned keys (user:42:v7) make invalidation a pointer bump. A stampede (dogpile) happens when a hot key expires and thousands of requests miss simultaneously and hit the database. Defences are request coalescing (single-flight: one request rebuilds while others wait or get stale data), stale-while-revalidate, probabilistic early refresh (XFetch), TTL jitter so many keys do not expire together, and rate-limited fallbacks to the database. After a cold start or cache flush, warm hot keys before shifting traffic.",
        ["Product pages backed by a cache after price updates.", "Protecting the DB when a celebrity profile's cache entry expires.", "Rolling out a new cache cluster without a cold-start outage.", "Invalidating CDN and app caches from one change stream."],
        [
            "Cache-aside write path: update DB, then delete the cache key.",
            "TTL is the safety net that bounds staleness from missed invalidations.",
            "Single-flight turns N concurrent misses into one DB query.",
            "Jitter TTLs (±10-20%) to avoid synchronized expiry.",
            "Serve stale on errors; a slightly old value beats an outage.",
        ],
        [
            ex("Stampede with and without single-flight", "advanced", "1,000 concurrent requests arrive just after a hot key expires.", "python", """
                def run(single_flight):
                    db_queries, inflight, cache = 0, False, {}
                    for _ in range(1000):
                        if "hot" in cache:
                            continue
                        if single_flight and inflight:
                            continue
                        db_queries += 1
                        inflight = True
                    cache["hot"] = "value"
                    return db_queries

                print("naive cache-aside :", run(False), "DB queries")
                print("with single-flight:", run(True), "DB query")
            """),
            ex("TTL jitter spreads expiry", "intermediate", "Keys loaded together expire at different times.", "python", """
                import random
                from collections import Counter
                random.seed(9)
                base = 300
                flat = Counter(base // 30 for _ in range(10_000))
                jittered = Counter(int(base * random.uniform(0.8, 1.2)) // 30 for _ in range(10_000))
                print("no jitter, expiries per 30s bucket:", dict(flat))
                print("jitter +-20%:                     ", dict(sorted(jittered.items())))
            """),
            ex("Probabilistic early refresh (XFetch)", "advanced", "Refresh before expiry with rising probability, scaled by rebuild cost.", "python", """
                import math, random
                random.seed(4)
                ttl_end, rebuild_cost, beta = 100.0, 2.0, 1.0

                def should_refresh(now):
                    return now - rebuild_cost * beta * math.log(random.random()) >= ttl_end

                for now in (80, 90, 95, 98, 99.5):
                    p = sum(should_refresh(now) for _ in range(10_000)) / 10_000
                    print(f"t={now:>5}: refresh probability {p:.1%}")
            """),
        ],
        ["Write: UPDATE db; DEL cache_key (after commit)", "TTL = base × uniform(0.8, 1.2)", "Single-flight / lock: SET rebuild:key 1 NX PX 5000", "Cache-Control: stale-while-revalidate=30", "Versioned keys: product:{id}:v{version}"],
        ["Updating the cache before the DB commit, caching data that then rolls back.", "Flushing the whole cache during a deploy and stampeding the database.", "Invalidating only from the app write path, missing batch jobs and admin edits."],
        [
            qa("intermediate", "Why delete the cache key instead of writing the new value?", "With concurrent writers, two updates can reach the cache in the opposite order of their DB commits, leaving a stale value indefinitely. Deleting forces the next read to load the current DB value; a short TTL covers the remaining read-after-delete race."),
            qa("intermediate", "What is a cache stampede and how do you prevent it?", "When a hot key expires, many requests miss at once and all query the database, which can overload it. Prevent it with request coalescing (single-flight or a short rebuild lock), serving stale while one request refreshes, early probabilistic refresh, and TTL jitter."),
            qa("advanced", "How would you invalidate caches reliably across many services?", "Publish change events from the source of truth via CDC or an outbox to a topic; cache owners consume them and delete affected keys, including CDN purges by surrogate key. TTLs remain as a backstop for missed events."),
            qa("advanced", "How do you recover from a full cache flush safely?", "Warm the hottest keys from logs or a snapshot before taking traffic, shift traffic gradually, coalesce misses, and rate-limit database fallbacks so excess requests get degraded responses instead of queueing on the DB."),
        ],
        ["caching", "cache-write-policies", "cdn"],
        chain(
            ("Writer", "price = 90", "Write", "The service updates the product price in the database."),
            ("Database", "commit", "Commit first", "The transaction commits; this is the source of truth.", "UPDATE"),
            ("Invalidate", "DEL product:7", "Delete key", "After commit, delete the key (or emit a CDC event that does).", "event"),
            ("Readers", "1,000 misses", "Coalesce", "Concurrent misses wait on one in-flight rebuild instead of all hitting the DB.", "GET"),
            ("Cache", "TTL 300±20%", "Refill", "One read reloads the value with a jittered TTL; everyone else gets it from cache.", "set"),
        ),
    ),
    topic(
        "cache-write-policies", "Write-Through, Write-Back & Write-Around", "building-blocks", "intermediate", "WP",
        "How writes flow through a cache, and what each policy risks.",
        "Write-through is updating both your notebook and the master ledger at once. Write-back is noting it in the notebook and copying to the ledger tonight. Write-around is writing only to the ledger and letting the notebook catch up later.",
        "Cache write policies decide when writes reach the backing store. Write-through writes to the cache and the database synchronously, keeping the cache warm and consistent at the cost of write latency, and caching data that may never be read. Write-back (write-behind) acknowledges after writing to the cache and flushes to the database asynchronously, often batching and coalescing many updates; it gives the fastest writes and absorbs bursts, but risks data loss if the cache node fails before flushing and complicates consistency. Write-around writes only to the database and lets reads populate the cache (cache-aside), avoiding cache pollution for write-once data at the cost of a miss on first read. Read-through means the cache itself loads missing entries from the database. Most web systems use cache-aside with write-around plus invalidation; write-back appears in counters, metrics aggregation, CPU caches and storage controllers with battery-backed memory.",
        ["Like and view counters (write-back with periodic flush).", "User profile reads after updates (write-through).", "Logs or bulk imports rarely read soon (write-around).", "Disk controllers and CPU caches (write-back with protection)."],
        [
            "Write-through: consistent, warm, slower writes.",
            "Write-back: fastest writes, coalescing, risk of loss on crash.",
            "Write-around: no pollution, first read misses.",
            "Durability of write-back depends on replicated or persistent cache.",
            "Cache-aside + invalidation is the most common web default.",
        ],
        [
            ex("Compare the three policies", "intermediate", "Counts DB writes and data lost if the cache crashes before a flush.", "python", """
                import random
                random.seed(2)
                writes = [(random.choice("abcde"), i) for i in range(1037)]

                def simulate(policy, flush_every=100):
                    db, cache, dirty, db_writes = {}, {}, {}, 0
                    for n, (k, v) in enumerate(writes, 1):
                        if policy == "through":
                            cache[k] = db[k] = v
                            db_writes += 1
                        elif policy == "around":
                            db[k] = v
                            db_writes += 1
                            cache.pop(k, None)
                        else:
                            cache[k] = dirty[k] = v
                            if n % flush_every == 0:
                                db.update(dirty)
                                db_writes += len(dirty)
                                dirty.clear()
                    lost = len(dirty)
                    return db_writes, lost

                for p in ("through", "around", "back"):
                    w, lost = simulate(p)
                    print(f"write-{p:8}: {w:>5} DB writes, keys lost on crash: {lost}")
            """),
            ex("Write-back counter with periodic flush", "basic", "Thousands of increments become one DB update per key.", "python", """
                from collections import Counter
                buffer = Counter()
                for post in ["p1"] * 5000 + ["p2"] * 1200:
                    buffer[post] += 1
                updates = [f"UPDATE posts SET likes = likes + {n} WHERE id = '{p}'" for p, n in buffer.items()]
                print(len(updates), "DB statements instead of", sum(buffer.values()))
                print(updates[0])
            """),
        ],
        ["Write-through: set cache + DB, ack after both", "Write-back: ack after cache, flush every N s / N ops", "Write-around: DB only; cache fills on read", "Read-through: cache loads on miss", "Redis INCR + periodic flush for counters"],
        ["Write-back on a single non-persistent cache node holding money or orders.", "Write-through without handling partial failure (DB succeeds, cache fails).", "Assuming write-around is consistent without invalidating old cached values."],
        [
            qa("basic", "What is the difference between write-through and write-back?", "Write-through updates the cache and the database before acknowledging, so data is durable and the cache is warm but writes are slower. Write-back acknowledges after the cache write and persists later, giving fast writes and batching but risking loss of unflushed data."),
            qa("intermediate", "When is write-around better?", "When written data is unlikely to be read soon, like logs, bulk imports or audit records. Writing only to the database keeps the cache full of genuinely hot data; the first read pays a miss."),
            qa("intermediate", "How would you implement a high-volume like counter?", "Increment in Redis (INCR) or an in-memory buffer and flush aggregated deltas to the database periodically or via a stream processor. Accept slight staleness, and make flushes idempotent or transactional so retries do not double-count."),
            qa("advanced", "How can you make write-back safer?", "Persist the cache log (Redis AOF), replicate the cache synchronously to another node, or write through a durable log such as Kafka first and apply to the database asynchronously. Bound the flush interval to limit potential loss."),
        ],
        ["caching", "cache-invalidation", "message-queues"],
        chain(
            ("Write", "like +1", "Write arrives", "A 'like' increment arrives at the service."),
            ("Cache", "INCR likes:p1", "Write to cache", "Write-back: increment in cache and acknowledge immediately.", "+1"),
            ("Dirty set", "p1: +5,000", "Coalesce", "Thousands of increments accumulate as one dirty delta per key.", "delta"),
            ("Flush", "every 5 s", "Flush", "A background job writes aggregated deltas to the database.", "batch"),
            ("Database", "likes += 5,000", "Persist", "One UPDATE per key instead of one per like. Unflushed deltas are the risk.", "UPDATE"),
        ),
    ),
    topic(
        "blob-storage", "Blob & Object Storage", "building-blocks", "basic", "OB",
        "Store large immutable files cheaply and durably; keep metadata elsewhere.",
        "A self-storage warehouse: you rent numbered lockers, put boxes in, and keep the inventory list in your own notebook. The warehouse does not care what is inside.",
        "Object storage (S3, GCS, Azure Blob) stores immutable blobs addressed by bucket and key, accessed over HTTP, with effectively unlimited capacity and very high durability (eleven nines) via replication or erasure coding across devices and zones. It is the right home for images, video, backups, logs and data lake files, while the database stores metadata and the object key. Clients upload directly to storage with pre-signed URLs (time-limited, signed with HMAC-SHA256 by the server), which keeps large payloads off application servers. Large files use multipart upload: parallel parts, per-part checksums, retry only failed parts. Objects are read through a CDN for egress efficiency. Lifecycle rules move cold data to cheaper tiers (infrequent access, archive) and delete expired data. Modern S3 offers strong read-after-write consistency, but there is no partial update: changing an object means writing a new version, and listing many keys is slow, so keep an index in your own database.",
        ["User uploads of photos and videos.", "Database backups and long-term archives.", "Data lake storage for Parquet files.", "Static website and build artifact hosting."],
        [
            "Blobs in object storage, metadata (owner, size, key) in the database.",
            "Pre-signed URLs let clients upload/download directly, with short expiry.",
            "Multipart upload for files over ~100 MB; parallel parts, per-part checksums.",
            "Erasure coding gives replication-level durability at ~1.4× overhead instead of 3×.",
            "Lifecycle policies tier cold data and enforce retention.",
        ],
        [
            ex("Multipart upload plan with SHA-256 checksums", "intermediate", "Split a payload into parts and compute integrity hashes.", "python", """
                import hashlib, random
                random.seed(1)
                payload = bytes(random.getrandbits(8) for _ in range(2_500_000))
                part_size = 1_000_000
                parts = [payload[i:i + part_size] for i in range(0, len(payload), part_size)]
                for n, p in enumerate(parts, 1):
                    print(f"part {n}: {len(p):>9,} bytes sha256={hashlib.sha256(p).hexdigest()[:16]}...")
                print("whole object sha256:", hashlib.sha256(payload).hexdigest()[:16], "...")
            """),
            ex("Pre-signed URL (HMAC-SHA256)", "intermediate", "Server signs bucket, key and expiry; the storage tier verifies. Key generated at runtime.", "python", """
                import hashlib, hmac, secrets
                SIGNING_KEY = secrets.token_bytes(32)

                def presign(method, key, expires_at):
                    msg = f"{method}|{key}|{expires_at}".encode()
                    sig = hmac.new(SIGNING_KEY, msg, hashlib.sha256).hexdigest()
                    return f"https://media.example.com/{key}?exp={expires_at}&sig={sig}"

                def verify(method, key, exp, sig, now):
                    good = hmac.new(SIGNING_KEY, f"{method}|{key}|{exp}".encode(), hashlib.sha256).hexdigest()
                    return hmac.compare_digest(good, sig) and now < exp

                url = presign("PUT", "uploads/u42/photo.jpg", 1_000_900)
                sig = url.split("sig=")[1]
                print(url[:70] + "...")
                print("valid now:", verify("PUT", "uploads/u42/photo.jpg", 1_000_900, sig, 1_000_000))
                print("expired:  ", verify("PUT", "uploads/u42/photo.jpg", 1_000_900, sig, 1_001_000))
                print("other key:", verify("PUT", "uploads/u1/photo.jpg", 1_000_900, sig, 1_000_000))
            """),
            ex("Replication vs erasure coding overhead", "basic", "Storage needed for 1 PB of data.", "python", """
                data_pb = 1
                print(f"3x replication : {data_pb * 3:.1f} PB raw, survives 2 lost copies")
                k, m = 10, 4
                print(f"RS({k}+{m}) coding: {data_pb * (k + m) / k:.1f} PB raw, survives {m} lost fragments")
            """),
        ],
        ["Key layout: {tenant}/{yyyy}/{mm}/{uuid}.jpg", "Pre-signed URL expiry: 5-15 min", "Multipart: parts 8-100 MB, parallel, checksum each", "Lifecycle: → IA after 30d, → archive after 180d", "Encrypt at rest (SSE-KMS, AES-256), block public access"],
        ["Proxying large uploads through app servers instead of pre-signed URLs.", "Using LIST as a query engine; keep an index in the database.", "Public buckets by accident; enforce block-public-access and scoped policies.", "Trusting client-supplied content type and file names; validate and generate keys server-side."],
        [
            qa("basic", "Why store images in object storage instead of the database?", "Blobs bloat database storage, backups and replication, and object storage is cheaper, more durable and serves bytes efficiently through a CDN. The database keeps metadata and the object key."),
            qa("intermediate", "How do direct uploads with pre-signed URLs work?", "The client asks the API for upload permission; the API authorizes the user, generates a key and returns a URL signed for that key, method and short expiry. The client uploads straight to storage, and a completion event or callback records the object in the database."),
            qa("intermediate", "How do you upload a 10 GB file reliably?", "Use multipart upload: split into parts, upload in parallel with per-part checksums, retry only failed parts, then complete the upload, which assembles the object atomically. Abort incomplete uploads with a lifecycle rule."),
            qa("advanced", "What is erasure coding and why use it?", "Data is split into k data fragments plus m parity fragments spread over devices; any k of k+m fragments reconstruct it. It tolerates m failures at (k+m)/k overhead, e.g. 1.4× for 10+4, versus 3× for triple replication, at the cost of more CPU and network on reconstruction."),
        ],
        ["cdn", "data-pipelines", "database-selection"],
        chain(
            ("Client", "wants upload", "Ask permission", "The app requests an upload slot for a 40 MB video."),
            ("API", "authorize + sign", "Pre-sign", "The API checks the user, picks a server-generated key and returns a 10-minute signed URL.", "POST /uploads"),
            ("Object store", "multipart PUT", "Direct upload", "Parts upload in parallel straight to storage with SHA-256 checksums.", "PUT parts"),
            ("Event", "object created", "Notify", "Storage emits an event; a worker validates, scans and transcodes.", "event"),
            ("Metadata DB", "key, size, owner", "Record", "The database stores the key and metadata; reads go through the CDN.", "INSERT"),
        ),
    ),
    topic(
        "search-systems", "Search Systems", "building-blocks", "intermediate", "SE",
        "Inverted indexes, relevance scoring, sharded query fan-out and near-real-time indexing.",
        "The index at the back of a cookbook: for every ingredient it lists the pages that mention it, so you find 'garlic and lemon' recipes by intersecting two short lists.",
        "Search engines (Elasticsearch, OpenSearch, Solr, Lucene-based systems) build an inverted index: for each term, a postings list of documents and positions. Text goes through analysis (tokenizing, lowercasing, stemming, synonyms) at both index and query time, so analyzers must match. Relevance is scored with BM25, which rewards rare terms and term frequency with saturation and normalizes for document length, then often re-ranked with business signals or learned models. Indexes are sharded (each shard is a Lucene index) and replicated; a query fans out to one copy of every shard, each returns its top-k, and a coordinator merges them. Indexing is near-real-time: documents become searchable after a refresh (~1 s) when a new segment is opened, and segments are merged in the background. The search index is a derived store: feed it from the source of truth via CDC or an outbox, support full reindexing into a new index with an alias swap, and never treat it as the system of record.",
        ["Product search with facets and filters.", "Log search and observability (ELK/OpenSearch).", "Autocomplete and fuzzy matching.", "Relevance tuning with business boosts."],
        [
            "Inverted index: term → postings (doc ids, frequencies, positions).",
            "BM25: idf × saturated tf, normalized by document length.",
            "Query fan-out to all shards; coordinator merges top-k.",
            "Near-real-time: refresh interval trades freshness for indexing throughput.",
            "Reindex into a new index and atomically switch an alias.",
        ],
        [
            ex("Tiny inverted index with BM25", "intermediate", "Index four documents and rank a query.", "python", """
                import math, re
                from collections import Counter, defaultdict
                docs = {1: "fast red running shoes", 2: "red dress for summer", 3: "running shoes for trail running",
                        4: "blue shoes"}
                tok = lambda s: re.findall("[a-z]+", s.lower())
                index, lengths = defaultdict(dict), {}
                for d, text in docs.items():
                    terms = tok(text)
                    lengths[d] = len(terms)
                    for t, f in Counter(terms).items():
                        index[t][d] = f
                avg = sum(lengths.values()) / len(lengths)

                def bm25(query, k1=1.2, b=0.75):
                    scores = Counter()
                    for t in tok(query):
                        post = index.get(t, {})
                        idf = math.log(1 + (len(docs) - len(post) + 0.5) / (len(post) + 0.5))
                        for d, f in post.items():
                            scores[d] += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * lengths[d] / avg))
                    return [(d, round(s, 2)) for d, s in scores.most_common()]

                print("postings for 'shoes':", index["shoes"])
                print("query 'running shoes':", bm25("running shoes"))
            """),
            ex("Scatter-gather across shards", "intermediate", "Each shard returns its top 2; the coordinator merges.", "python", """
                import heapq
                shards = {"s0": [("d1", 9.1), ("d4", 3.0), ("d7", 2.2)], "s1": [("d2", 7.5), ("d5", 6.9)], "s2": [("d3", 8.8), ("d9", 1.0)]}
                k = 3
                partial = [hit for hits in shards.values() for hit in heapq.nlargest(2, hits, key=lambda h: h[1])]
                print("global top-3:", heapq.nlargest(k, partial, key=lambda h: h[1]))
            """),
            ex("Index mapping and alias swap", "advanced", "Zero-downtime reindex.", "json", """
                PUT products_v2
                { "settings": { "number_of_shards": 6, "number_of_replicas": 1, "refresh_interval": "1s" },
                  "mappings": { "properties": {
                    "title": { "type": "text", "analyzer": "english" },
                    "brand": { "type": "keyword" }, "price": { "type": "scaled_float", "scaling_factor": 100 } } } }

                POST _aliases
                { "actions": [ { "remove": { "index": "products_v1", "alias": "products" } },
                               { "add":    { "index": "products_v2", "alias": "products" } } ] }
            """, runnable=False),
        ],
        ["Shard size target: 10-50 GB", "refresh_interval 1s (raise to 30s for bulk loads)", "BM25 defaults: k1 = 1.2, b = 0.75", "Reads hit one copy per shard; replicas add read capacity", "Alias swap for reindexing"],
        ["Using the search cluster as the primary database.", "Too many tiny shards (overhead) or giant shards (slow recovery).", "Deep pagination with from/size; use search_after."],
        [
            qa("basic", "What is an inverted index?", "A map from each term to the list of documents (and positions) containing it. A query looks up each term's postings and intersects or unions them, which is far faster than scanning every document."),
            qa("intermediate", "How does a distributed search query execute?", "The coordinating node sends the query to one copy of every shard; each shard scores locally and returns its top-k ids and scores. The coordinator merges them into a global top-k and then fetches the documents (query then fetch)."),
            qa("intermediate", "How do you keep the index in sync with the database?", "Stream changes via CDC or an outbox into an indexing pipeline with idempotent upserts keyed by document id and version. For mapping changes, rebuild into a new index and switch an alias atomically."),
            qa("advanced", "Why is search 'near real-time' rather than real-time?", "New documents are buffered and become visible when a refresh opens a new segment (default about 1 s). Refreshing more often lowers indexing throughput and creates more segments to merge, so the interval is a freshness vs throughput trade-off."),
        ],
        ["database-selection", "case-typeahead", "data-pipelines"],
        chain(
            ("Query", "'running shoes'", "Search request", "The user searches; the request reaches a coordinating node."),
            ("Analyzer", "running → run", "Analyze", "Tokenize, lowercase and stem with the same analyzer used at index time.", "text"),
            ("Shards", "6 shards", "Scatter", "Each shard looks up postings and scores with BM25.", "terms"),
            ("Coordinator", "merge top-k", "Gather", "Merge each shard's top-k into a global top-k.", "top-k"),
            ("Fetch", "docs + facets", "Fetch and return", "Fetch the winning documents and aggregations and return them.", "ids"),
        ),
    ),
    topic(
        "bloom-filters", "Bloom Filters & Probabilistic Structures", "building-blocks", "intermediate", "BF",
        "Trade a little accuracy for huge memory savings: Bloom, Count-Min and HyperLogLog.",
        "A bouncer with a fuzzy memory: if they say they've never seen you, they're right. If they say they have, they might be confusing you with someone similar.",
        "A Bloom filter is a bit array with k hash functions that answers 'definitely not present' or 'probably present'. Adding sets k bits; a query checks those k bits, so false positives are possible but false negatives are not. With m bits for n items, the optimal k is (m/n)·ln 2, and about 9.6 bits per item gives a 1% false-positive rate regardless of item size. Classic uses are avoiding disk reads for absent keys in LSM stores (RocksDB, Cassandra), skipping already-crawled URLs, and checking weak-password lists. Standard Bloom filters cannot delete; counting Bloom filters or cuckoo filters can. A Count-Min sketch estimates frequencies (heavy hitters, rate limiting) with bounded overestimation, and HyperLogLog estimates distinct counts with about 1-2% error in a few KB (Redis PFADD/PFCOUNT). All of these are mergeable, which makes them ideal for distributed aggregation.",
        ["Skipping SSTable reads for missing keys.", "A crawler's 'seen URL' check.", "Counting unique visitors per day (HyperLogLog).", "Finding top talkers in network traffic (Count-Min)."],
        [
            "No false negatives; false positive rate tuned by bits per item.",
            "Bits per item ≈ −1.44 · log2(p): 1% ≈ 9.6 bits, 0.1% ≈ 14.4 bits.",
            "Optimal k = (m/n) · ln 2 hash functions.",
            "Double hashing (h1 + i·h2) simulates k hashes cheaply.",
            "Sketches are mergeable: union Bloom filters with OR, HLLs with max.",
        ],
        [
            ex("Bloom filter with blake2b double hashing", "intermediate", "Measure the false-positive rate against theory.", "python", """
                import hashlib, math

                class Bloom:
                    def __init__(self, n, p):
                        self.m = math.ceil(-n * math.log(p) / math.log(2) ** 2)
                        self.k = max(1, round(self.m / n * math.log(2)))
                        self.bits = bytearray((self.m + 7) // 8)

                    def _idx(self, item):
                        d = hashlib.blake2b(item.encode(), digest_size=16).digest()
                        h1, h2 = int.from_bytes(d[:8], "big"), int.from_bytes(d[8:], "big") | 1
                        return [(h1 + i * h2) % self.m for i in range(self.k)]

                    def add(self, item):
                        for i in self._idx(item):
                            self.bits[i // 8] |= 1 << (i % 8)

                    def __contains__(self, item):
                        return all(self.bits[i // 8] >> (i % 8) & 1 for i in self._idx(item))

                bf = Bloom(n=5000, p=0.01)
                for i in range(5000):
                    bf.add(f"url-{i}")
                fp = sum(f"other-{i}" in bf for i in range(20000)) / 20000
                print(f"m={bf.m} bits ({bf.m / 5000:.1f}/item), k={bf.k}")
                print("false negatives:", sum(f"url-{i}" not in bf for i in range(5000)))
                print(f"false positive rate: {fp:.2%} (target 1%)")
            """),
            ex("Count-Min sketch for heavy hitters", "advanced", "Estimate frequencies in fixed memory; estimates never undercount.", "python", """
                import hashlib, random
                random.seed(8)
                W, D = 1000, 4
                table = [[0] * W for _ in range(D)]
                h = lambda row, x: int.from_bytes(hashlib.blake2b(f"{row}:{x}".encode(), digest_size=8).digest(), "big") % W
                stream = ["ip-1"] * 3000 + ["ip-2"] * 1500 + [f"ip-{random.randint(3, 5000)}" for _ in range(20000)]
                for x in stream:
                    for r in range(D):
                        table[r][h(r, x)] += 1
                est = lambda x: min(table[r][h(r, x)] for r in range(D))
                for ip in ("ip-1", "ip-2", "ip-77"):
                    print(ip, "true", stream.count(ip), "estimate", est(ip))
            """),
            ex("Redis probabilistic commands", "basic", "Built-in HyperLogLog; Bloom via the RedisBloom module.", "bash", """
                PFADD visitors:2026-10-17 user:1 user:2 user:3
                PFCOUNT visitors:2026-10-17
                PFMERGE visitors:week visitors:2026-10-11 visitors:2026-10-17
                BF.RESERVE seen_urls 0.01 10000000
                BF.ADD seen_urls https://example.com/a
                BF.EXISTS seen_urls https://example.com/b
            """, runnable=False),
        ],
        ["m = −n·ln(p) / (ln 2)²", "k = (m/n)·ln 2", "1% FPR ≈ 9.6 bits/item", "HLL error ≈ 1.04/√registers (Redis ≈ 0.81%)", "Count-Min: width ≈ e/ε, depth ≈ ln(1/δ)"],
        ["Using a Bloom filter where a false positive causes harm without a fallback check.", "Overfilling the filter beyond its design n, so the FPR climbs quickly.", "Trying to delete from a standard Bloom filter."],
        [
            qa("basic", "What guarantees does a Bloom filter give?", "If it says an item is absent, it is definitely absent; if it says present, it is probably present with a tunable false-positive rate. It never produces false negatives as long as items are only added."),
            qa("intermediate", "How do you size a Bloom filter?", "From the expected item count n and target false-positive rate p: m = −n·ln p / (ln 2)² bits and k = (m/n)·ln 2 hashes. For 1% you need about 9.6 bits per item, independent of item size."),
            qa("intermediate", "Where do databases use Bloom filters?", "LSM-tree stores keep a Bloom filter per SSTable so a point lookup skips files that cannot contain the key, avoiding most disk reads for absent keys. Joins and distributed queries also use them to prune data before shuffling."),
            qa("advanced", "How would you count unique users across 100 servers?", "Each server maintains a HyperLogLog per time bucket; merge them by taking the register-wise max to get a global estimate with about 1% error in kilobytes of memory, instead of shipping and deduplicating raw user ids."),
        ],
        ["case-kv-store", "rate-limiting", "caching"],
        chain(
            ("Lookup", "key = user:9", "Point lookup", "A read for a key arrives at an LSM-tree store with many SSTables."),
            ("Hash", "k = 7 positions", "Hash", "Hash the key into 7 bit positions with double hashing.", "key"),
            ("Bloom", "bit check", "Check bits", "Any zero bit means 'definitely absent': skip this SSTable.", "bits"),
            ("SSTable", "disk read", "Read only if needed", "Only files whose filter says 'maybe' are read from disk (~1% wasted).", "maybe"),
        ),
    ),
    topic(
        "replication", "Replication Strategies", "distributed", "intermediate", "RE",
        "Single-leader, multi-leader and leaderless replication; sync vs async; lag and its anomalies.",
        "A teacher dictating notes: students copying in real time (synchronous) slow the teacher down; students catching up from a friend's notebook later (asynchronous) may be a few lines behind.",
        "Replication keeps copies of data on multiple nodes for availability, durability and read scaling. Single-leader replication sends all writes to one leader, which ships its log to followers; it is simple and gives a clear order, and is used by PostgreSQL, MySQL and MongoDB. Synchronous replication waits for followers before acknowledging (no data loss on failover, higher latency); asynchronous acknowledges immediately (fast, but recent writes can be lost if the leader dies); semi-synchronous waits for one follower. Asynchronous followers lag, causing anomalies: a user may not see their own write (fix with read-your-writes by routing to the leader or waiting for a log position) or see time go backwards across replicas (fix with monotonic reads by sticking to one replica). Multi-leader replication accepts writes in several regions but must resolve conflicts (last-writer-wins, CRDTs, application merge). Leaderless systems (Dynamo, Cassandra) write to N replicas and use quorums W + R > N, with read repair and hinted handoff to converge.",
        ["Read replicas to scale a read-heavy app.", "Cross-zone standby for automatic failover.", "Multi-region writes for a collaborative app.", "Highly available writes with tunable consistency (Cassandra)."],
        [
            "Sync: zero RPO, higher write latency; async: low latency, possible loss.",
            "Replication lag breaks read-your-writes and monotonic reads.",
            "Failover risks split brain; use fencing and consensus-based election.",
            "Quorum: W + R > N ensures read and write sets overlap.",
            "Multi-leader needs a conflict resolution strategy from day one.",
        ],
        [
            ex("Quorum reads and writes (N=3)", "intermediate", "W + R > N guarantees a read sees the latest acknowledged write.", "python", """
                import random
                random.seed(11)
                N = 3

                def run(W, R, trials=2000):
                    stale = 0
                    for _ in range(trials):
                        replicas = [1] * N
                        for i in random.sample(range(N), W):
                            replicas[i] = 2
                        seen = max(replicas[i] for i in random.sample(range(N), R))
                        stale += seen != 2
                    return stale / trials

                for W, R in ((1, 1), (2, 1), (2, 2), (3, 1)):
                    print(f"W={W} R={R} (W+R{'>' if W + R > N else '<='}N): stale reads {run(W, R):.1%}")
            """),
            ex("Read-your-writes with replication lag", "intermediate", "Route a user's reads to the leader for a short window after they write.", "python", """
                leader = {"bio": "old"}
                follower = {"bio": "old"}
                last_write_at = {}

                def write(user, value, now):
                    leader["bio"] = value
                    last_write_at[user] = now

                def read(user, now, sticky_window=5):
                    use_leader = now - last_write_at.get(user, -99) < sticky_window
                    return ("leader", leader["bio"]) if use_leader else ("follower", follower["bio"])

                write("u1", "new bio", now=100)
                print("u1 at t=101:", read("u1", 101))
                print("u2 at t=101:", read("u2", 101), "(lagging follower is fine for others)")
                follower.update(leader)
                print("u1 at t=110:", read("u1", 110))
            """),
        ],
        ["RPO: sync = 0, async = replication lag", "Quorum: W + R > N (N=3, W=2, R=2)", "PostgreSQL: synchronous_standby_names = 'ANY 1 (s1, s2)'", "Read-your-writes: read from leader for ~lag window", "Monitor lag: pg_stat_replication replay_lag"],
        ["Reading from async replicas right after a write and showing stale data.", "Failing over to an async replica and silently losing acknowledged writes.", "Two leaders after a partition (split brain) without fencing."],
        [
            qa("basic", "Why replicate a database?", "For high availability (a replica takes over on failure), durability (copies survive disk or node loss), read scaling (serve reads from followers) and lower latency for distant users."),
            qa("intermediate", "Synchronous vs asynchronous replication?", "Synchronous waits for replicas to confirm before acknowledging, so a failover loses nothing but every write pays the slowest replica's latency. Asynchronous acknowledges after the leader writes, so it is fast but a failover can lose the latest writes. Semi-sync (wait for one of N) is a common compromise."),
            qa("intermediate", "How do you provide read-your-writes on a replicated DB?", "Route a user's reads to the leader for a short time after they write, or record the leader's log position (LSN) at write time and read from a replica only once it has replayed past it. Some databases expose this as causal consistency tokens."),
            qa("advanced", "How do leaderless systems converge after failures?", "Writes go to N replicas and succeed with W acks; failed replicas get hinted handoff when they return. Reads query R replicas and repair stale ones (read repair), and background anti-entropy compares Merkle trees to fix divergence."),
        ],
        ["consistency-cap", "sharding", "leader-election"],
        chain(
            ("Client", "UPDATE bio", "Write", "The client writes to the leader."),
            ("Leader", "WAL lsn 900", "Append to log", "The leader appends to its write-ahead log and applies it.", "write"),
            ("Sync replica", "ack lsn 900", "Synchronous copy", "One standby must confirm before the commit is acknowledged.", "WAL"),
            ("Async replica", "lag 200 ms", "Asynchronous copy", "Other replicas apply the log a bit later; reads there may be stale.", "WAL"),
            ("Reads", "leader or replica", "Route reads", "The writer reads from the leader briefly; everyone else uses replicas.", "SELECT"),
        ),
    ),
    topic(
        "sharding", "Sharding & Partitioning Strategies", "distributed", "intermediate", "SH",
        "Split data across nodes by hash, range or directory, and survive hot keys and resharding.",
        "A library splitting its collection over several buildings: by first letter of the author (range), by a shuffled code (hash), or by a lookup desk that tells you which building (directory).",
        "Sharding horizontally partitions data so each node stores and serves a subset, scaling writes and storage beyond one machine. Hash partitioning (hash(key) mod partitions, or consistent hashing) spreads keys evenly but makes range queries scatter to all shards. Range partitioning keeps keys ordered, which is great for range scans and time series, but sequential keys create hot shards; split ranges dynamically (Bigtable, CockroachDB). Directory-based sharding stores key → shard in a lookup service, allowing arbitrary placement and tenant moves at the cost of an extra dependency. The shard key is the critical decision: it should have high cardinality, spread load evenly, and match the dominant query so most queries hit one shard; for SaaS, tenant_id is common. Cross-shard queries need scatter-gather, and cross-shard transactions need 2PC or sagas. Use many logical partitions (e.g. 1,024) mapped to fewer physical nodes so resharding moves whole partitions instead of rehashing every key. Hot keys (a celebrity) need splitting with key salting, caching or dedicated shards.",
        ["Scaling a multi-tenant SaaS database by tenant_id.", "Partitioning time-series data by time range.", "Splitting a users table that outgrew one primary.", "Isolating a whale customer on a dedicated shard."],
        [
            "Choose the shard key from the most frequent query path.",
            "Hash = even load, poor ranges; range = good scans, hot spots.",
            "Fixed logical partitions >> nodes make rebalancing cheap.",
            "Avoid cross-shard transactions; design aggregates to live on one shard.",
            "Detect and split hot keys (salting, caching, read replicas).",
        ],
        [
            ex("Hash vs range partitioning load", "intermediate", "Sequential ids pile onto the last range shard; hashing spreads them.", "python", """
                import hashlib
                from collections import Counter
                shards = 4
                new_ids = range(900_000, 1_000_000)
                h = lambda k: int.from_bytes(hashlib.sha256(str(k).encode()).digest()[:8], "big")
                by_hash = Counter(h(i) % shards for i in new_ids)
                by_range = Counter(min(i // 250_000, shards - 1) for i in new_ids)
                print("hash  :", dict(sorted(by_hash.items())))
                print("range :", dict(sorted(by_range.items())), "<- today's writes all on shard 3")
            """),
            ex("Logical partitions make resharding cheap", "advanced", "Compare keys moved when going from 4 to 5 nodes.", "python", """
                import hashlib
                h = lambda k: int.from_bytes(hashlib.sha256(k.encode()).digest()[:8], "big")
                keys = [f"user:{i}" for i in range(50_000)]
                moved_mod = sum(h(k) % 4 != h(k) % 5 for k in keys)
                P = 1024
                old = {p: p % 4 for p in range(P)}
                new = {p: 4 if p % 5 == 0 else old[p] for p in range(P)}
                moved = {p for p in range(P) if old[p] != new[p]}
                moved_parts = sum(h(k) % P in moved for k in keys)
                print(f"hash mod N: {moved_mod / len(keys):.0%} of keys move")
                print(f"1024 logical partitions: {moved_parts / len(keys):.0%} of keys move")
            """),
            ex("Salting a hot key", "intermediate", "Spread a celebrity's counter over 8 sub-keys.", "python", """
                import random
                from collections import Counter
                random.seed(6)
                writes = Counter()
                for _ in range(80_000):
                    writes[f"likes:celebrity#{random.randrange(8)}"] += 1
                print(writes.most_common(3), "...")
                print("read = sum of", len(writes), "sub-keys =", sum(writes.values()))
            """),
        ],
        ["shard = hash(tenant_id) % 1024 → partition map → node", "Range: split when partition > 10 GB or hot", "Shard key: high cardinality + even load + query locality", "Hot key: key#{0..N-1} salting, sum on read", "Cross-shard: scatter-gather, avoid 2PC"],
        ["Sharding on a low-cardinality key (country) and getting a few giant shards.", "Auto-increment ids with range sharding (all writes on the newest shard).", "Sharding too early; vertical scaling and read replicas go a long way."],
        [
            qa("basic", "What is sharding and why use it?", "Splitting a dataset across multiple database nodes, each owning a subset of keys. It scales write throughput and storage beyond one machine and limits the blast radius of a node failure."),
            qa("intermediate", "How do you choose a shard key?", "Pick a high-cardinality key that matches the dominant access pattern so most queries hit a single shard, and that distributes load evenly over time. Tenant id or user id are common; avoid monotonically increasing keys with range partitioning and low-cardinality fields."),
            qa("intermediate", "Hash vs range partitioning?", "Hash spreads keys evenly and avoids hot spots but turns range queries into scatter-gather across all shards. Range keeps order for efficient scans but needs dynamic splitting to handle hot or growing ranges."),
            qa("advanced", "How do you reshard with minimal disruption?", "Pre-split into many logical partitions mapped to nodes, then move whole partitions: copy a snapshot, stream changes (CDC) to catch up, briefly block writes or use dual-writes to cut over, and update the routing map. Consistent hashing similarly limits movement to about 1/N of keys."),
            qa("advanced", "How do you handle a hot key?", "Cache reads aggressively, add read replicas, and for writes split the key into N salted sub-keys aggregated on read. Very large tenants can be moved to dedicated shards via directory-based routing."),
        ],
        ["consistent-hashing", "replication", "database-selection"],
        chain(
            ("Request", "tenant 42", "Request", "A query for tenant 42 arrives at the routing layer."),
            ("Hash", "p = h(42) % 1024", "Partition", "Hash the shard key into one of 1,024 logical partitions.", "key"),
            ("Map", "p 817 → node C", "Lookup", "A small partition map (from config or a coordinator) names the node.", "p 817"),
            ("Shard C", "primary + replicas", "Execute", "The query runs on one shard; no scatter-gather needed.", "query"),
            ("Rebalance", "move p 817", "Rebalance", "Adding node E moves whole partitions; the map is updated atomically.", "snapshot"),
        ),
    ),
    topic(
        "consensus-raft", "Consensus: Raft & Paxos", "distributed", "advanced", "RA",
        "How a cluster agrees on one ordered log despite crashes and partitions.",
        "A committee that keeps one official minutes book: a chair proposes each line, and it becomes official only once a majority has written it into their copies. If the chair disappears, the committee votes in a new one.",
        "Consensus lets a group of nodes agree on a sequence of values so they can act as one fault-tolerant state machine (replicated state machine). Paxos is the classic protocol; Raft was designed to be easier to understand and is used by etcd, Consul, CockroachDB and Kafka's KRaft. In Raft, time is divided into terms; each term has at most one leader, elected by a majority vote after followers time out without heartbeats (randomized election timeouts avoid split votes). The leader appends client commands to its log and replicates them with AppendEntries; an entry is committed once stored on a majority, and only then applied and acknowledged. Election restriction (voters only grant votes to candidates with logs at least as up to date) ensures a new leader holds all committed entries. A cluster of 2f+1 nodes tolerates f failures, so 3 nodes survive 1 and 5 survive 2; a minority partition cannot make progress, which preserves safety (CP). Consensus is expensive (a majority round trip per write), so systems use it for metadata, leases and configuration, not every user write.",
        ["Cluster metadata and configuration (etcd for Kubernetes).", "Leader election and locks with fencing tokens.", "Strongly consistent replicated databases (CockroachDB, Spanner).", "Kafka controller metadata (KRaft)."],
        [
            "Majority quorum: 2f+1 nodes tolerate f failures.",
            "Terms + randomized election timeouts give one leader per term.",
            "Committed = replicated on a majority; only then apply.",
            "Even cluster sizes add cost without extra fault tolerance.",
            "Linearizable reads need a leader lease or read-index round.",
        ],
        [
            ex("Raft-style majority commit", "advanced", "Leader replicates entries; a crashed follower does not block commit.", "python", """
                nodes = {"A": [], "B": [], "C": [], "D": [], "E": []}
                up = {"A", "B", "C", "E"}
                leader, term, commit_index = "A", 3, 0

                def append(cmd):
                    global commit_index
                    entry = (term, cmd)
                    acks = 0
                    for n, log in nodes.items():
                        if n in up:
                            log.append(entry)
                            acks += 1
                    majority = len(nodes) // 2 + 1
                    if acks >= majority:
                        commit_index = len(nodes[leader])
                    return acks, majority

                for cmd in ("set x=1", "set y=2"):
                    acks, maj = append(cmd)
                    print(f"{cmd}: {acks}/{len(nodes)} acks (need {maj}) -> commit_index={commit_index}")
                up -= {"B", "C"}
                acks, maj = append("set z=3")
                print(f"set z=3 with 3 nodes down: {acks} acks (need {maj}) -> commit_index={commit_index} (not committed)")
            """),
            ex("Randomized election timeouts", "intermediate", "The first follower to time out usually wins; ties are rare.", "python", """
                import random
                random.seed(21)
                ties = 0
                for _ in range(10_000):
                    t = sorted(random.uniform(150, 300) for _ in range(4))
                    ties += t[1] - t[0] < 5
                print(f"near-simultaneous candidates in {ties / 10_000:.1%} of elections (split-vote risk)")
                for size in (3, 4, 5, 7):
                    print(f"{size} nodes: majority {size // 2 + 1}, tolerates {(size - 1) // 2} failures")
            """),
        ],
        ["Cluster size 3 (tolerate 1) or 5 (tolerate 2)", "Election timeout 150-300 ms randomized; heartbeat ~50 ms", "Commit when matchIndex on majority ≥ N", "etcdctl endpoint status --cluster -w table", "Never span a 3-node quorum over 2 sites"],
        ["Running 2 or 4 nodes (no extra fault tolerance over 1 or 3).", "Putting consensus on the hot path of every user write.", "Spreading a quorum across two data centers so either outage halts writes."],
        [
            qa("intermediate", "Why do consensus clusters have an odd number of nodes?", "Progress requires a majority. A 4-node cluster needs 3 votes and tolerates 1 failure, the same as 3 nodes, but with more replication cost and more chances of failure; 5 nodes tolerate 2."),
            qa("advanced", "How does Raft elect a leader?", "A follower that misses heartbeats for a randomized timeout increments the term, votes for itself and requests votes. Nodes grant one vote per term, and only to candidates whose log is at least as up to date; a majority makes it leader, and it sends heartbeats to suppress new elections."),
            qa("advanced", "When is a Raft log entry committed?", "When the leader has replicated it to a majority of nodes in its current term; then it advances commitIndex, applies the entry to the state machine and replies to the client. Followers learn the commit index from later AppendEntries."),
            qa("advanced", "What happens during a network partition?", "The side with a majority can elect a leader and continue; the minority side cannot commit anything, and a stale leader there steps down when it sees a higher term. This sacrifices availability on the minority side to keep a single consistent log."),
            qa("intermediate", "Why not use consensus for every write in a large system?", "Each write needs a majority round trip and goes through one leader, limiting throughput and adding latency, especially across regions. Systems shard data into many consensus groups (Multi-Raft) or use consensus only for metadata, leases and coordination."),
        ],
        ["leader-election", "distributed-locks", "consistency-cap"],
        chain(
            ("Client", "set x=1", "Command", "The client sends a write to the current leader (term 3)."),
            ("Leader", "log index 8", "Append", "The leader appends the entry to its log.", "cmd"),
            ("Followers", "AppendEntries", "Replicate", "It sends the entry to followers, which append and acknowledge.", "entry"),
            ("Majority", "3 of 5 acks", "Commit", "Once a majority stores it, the entry is committed.", "acks"),
            ("State machine", "x = 1", "Apply and reply", "The leader applies the entry and answers the client; followers apply later.", "commit"),
        ),
    ),
    topic(
        "leader-election", "Leader Election & Leases", "distributed", "advanced", "LE",
        "Pick exactly one active node, renew its authority with a lease, and fence the old one.",
        "A relay baton: only the runner holding it may run. If a runner trips and freezes, officials hand a new baton with a higher number, and the track ignores anyone holding an older one.",
        "Many systems need a single active node: a scheduler, a partition owner, a primary database, a cron runner. Leader election chooses one, typically by delegating to a consensus system (etcd, ZooKeeper, Consul, or Kubernetes Lease objects) instead of inventing a protocol. The winner holds a lease: a record with an owner and expiry that it must renew periodically (e.g. TTL 15 s, renew every 5 s). If it stops renewing, the lease expires and another candidate acquires it. Because a paused or partitioned leader may not know it lost the lease, every term issues a monotonically increasing epoch or fencing token, and downstream resources reject requests with an older token. Leases depend on bounded clock drift, so leaders should stop acting before expiry (safety margin) and check the lease before each critical operation. Election by itself does not give exactly-once work: design leader actions to be idempotent so a brief overlap or retry is harmless.",
        ["Running one instance of a scheduler or cron job in a replicated deployment.", "Kubernetes controllers (leader election via Lease objects).", "Partition ownership in Kafka or a sharded service.", "Database primary failover managed by Patroni with etcd."],
        [
            "Delegate election to a consensus-backed store; do not build your own.",
            "Lease = owner + expiry; renew well before TTL (e.g. every TTL/3).",
            "Epoch/fencing tokens let resources reject a deposed leader.",
            "Stop leading on renewal failure before the lease could expire elsewhere.",
            "Make leader actions idempotent to tolerate brief overlap.",
        ],
        [
            ex("Lease-based election with epochs", "advanced", "A leader pauses, its lease expires, and its stale write is fenced.", "python", """
                store = {"lease": None, "epoch": 0}
                TTL = 15

                def try_acquire(node, now):
                    lease = store["lease"]
                    if lease is None or lease["expires"] <= now or lease["owner"] == node:
                        if lease is None or lease["owner"] != node:
                            store["epoch"] += 1
                        store["lease"] = {"owner": node, "expires": now + TTL, "epoch": store["epoch"]}
                        return store["epoch"]
                    return None

                resource = {"last_epoch": 0, "value": None}

                def write(epoch, value):
                    if epoch < resource["last_epoch"]:
                        return f"rejected stale epoch {epoch}"
                    resource.update(last_epoch=epoch, value=value)
                    return f"ok epoch {epoch}"

                e_a = try_acquire("A", now=0)
                print("A leads, epoch", e_a, write(e_a, "from A"))
                print("B tries at t=10:", try_acquire("B", now=10))
                e_b = try_acquire("B", now=20)
                print("A paused; B leads at t=20, epoch", e_b, write(e_b, "from B"))
                print("A wakes up and writes:", write(e_a, "late A"))
                print("resource:", resource)
            """),
            ex("Kubernetes Lease object", "intermediate", "What client-go leader election maintains.", "yaml", """
                apiVersion: coordination.k8s.io/v1
                kind: Lease
                metadata:
                  name: report-scheduler
                  namespace: jobs
                spec:
                  holderIdentity: report-scheduler-7d9f-abcde
                  leaseDurationSeconds: 15
                  renewTime: "2026-10-17T17:10:05.000000Z"
                  leaseTransitions: 4
            """, runnable=False),
        ],
        ["Lease TTL 15 s, renew every 5 s, retry every 2 s", "Fencing: resource rejects token < last seen", "etcd: election via lease + txn (compare create_revision)", "Kubernetes: coordination.k8s.io Lease", "Leader steps down on renewal failure"],
        ["Assuming the lease holder is the only actor without fencing downstream.", "Long GC pauses or blocking I/O longer than the lease TTL.", "Electing via a database row without TTL, leaving a dead leader forever."],
        [
            qa("intermediate", "Why use a lease instead of a permanent lock for leadership?", "A permanent lock held by a crashed node never releases. A lease expires unless renewed, so leadership moves automatically when the leader dies or is partitioned, bounded by the TTL."),
            qa("advanced", "What is a fencing token and why is it needed?", "A number that increases with every new leadership term or lock grant. A paused old leader may still believe it leads; downstream systems that store the highest token seen reject its requests, preventing two leaders from both writing."),
            qa("advanced", "How does etcd-based election work?", "Candidates create a key under an election prefix attached to their lease; the key with the lowest create revision is the leader, and others watch the key just before theirs. When the leader's lease expires its key is deleted and the next candidate takes over."),
            qa("intermediate", "How do you pick the lease TTL?", "Short TTLs fail over faster but risk false failovers from GC pauses or network blips; long TTLs mean longer outages after real failures. Typical values are 10-30 s with renewal every third of the TTL and a safety margin for clock drift."),
        ],
        ["consensus-raft", "distributed-locks", "replication"],
        chain(
            ("Candidates", "A, B, C", "Compete", "Three replicas try to acquire the same lease in etcd."),
            ("Lease store", "etcd, TTL 15 s", "Grant", "A wins with epoch 7; B and C watch the lease.", "acquire"),
            ("Leader A", "renew every 5 s", "Lead", "A renews the lease and does the work, tagging writes with epoch 7.", "epoch 7"),
            ("Expiry", "A paused 20 s", "Lose lease", "A stops renewing; the lease expires and B acquires epoch 8.", "timeout"),
            ("Resource", "rejects epoch 7", "Fence", "When A wakes and writes with epoch 7, storage rejects it.", "stale write"),
        ),
    ),
    topic(
        "distributed-locks", "Distributed Locks", "distributed", "advanced", "DL",
        "Mutual exclusion across machines: leases, fencing tokens and when to avoid locks entirely.",
        "A meeting-room booking system: you can book the room for an hour, but if you fall asleep inside, the next team will come in when your booking ends. The room should check bookings, not trust whoever is inside.",
        "A distributed lock ensures only one process at a time performs an operation, such as processing a file or refreshing a cache entry. It must have a TTL so a crashed holder does not block everyone forever, which means a slow holder can lose the lock while still working. Locks therefore come in two flavours. Efficiency locks avoid duplicate work where an occasional overlap is harmless; a single Redis SET key value NX PX 30000 with a random owner value (and a check-and-delete script on release) is fine. Correctness locks protect data where overlap causes corruption; they need a consensus-backed store (etcd, ZooKeeper) and fencing tokens checked by the resource being protected. Redlock across several independent Redis nodes is debated because it relies on timing assumptions. Often the better design avoids locks: use database transactions with row locks (SELECT … FOR UPDATE), optimistic concurrency with version checks, unique constraints, or single-writer partitioning where each key has one owner.",
        ["Ensuring one worker processes a given job or file.", "Preventing duplicate cache rebuilds (efficiency).", "Serializing account operations across services (correctness, with fencing).", "One-at-a-time database migrations."],
        [
            "Always set a TTL and a unique owner value; release only if you still own it.",
            "Efficiency lock: Redis NX PX is enough. Correctness: consensus + fencing.",
            "The protected resource must validate the fencing token.",
            "Prefer DB transactions, version checks or partition ownership when possible.",
            "Keep critical sections short and bounded by the TTL.",
        ],
        [
            ex("Why TTL locks need fencing", "advanced", "Client 1 pauses past its TTL; storage protects itself with tokens.", "python", """
                import itertools
                tokens = itertools.count(33)
                lock = {"owner": None, "expires": 0}
                storage = {"max_token": 0, "data": []}

                def acquire(owner, now, ttl=10):
                    if lock["owner"] is None or lock["expires"] <= now:
                        lock.update(owner=owner, expires=now + ttl)
                        return next(tokens)
                    return None

                def store_write(token, item):
                    if token <= storage["max_token"]:
                        return f"rejected token {token}"
                    storage["max_token"] = token
                    storage["data"].append(item)
                    return f"accepted token {token}"

                t1 = acquire("client-1", now=0)
                print("client-1 got token", t1, "then GC-pauses for 15 s")
                t2 = acquire("client-2", now=12)
                print("client-2 got token", t2, store_write(t2, "write from client-2"))
                print("client-1 resumes:", store_write(t1, "write from client-1"))
                print(storage)
            """),
            ex("Safe release: compare owner then delete", "intermediate", "Never delete a lock someone else now holds.", "python", """
                import uuid
                redis = {}

                def set_nx(key, val):
                    if key in redis:
                        return False
                    redis[key] = val
                    return True

                def release(key, val):
                    if redis.get(key) == val:
                        del redis[key]
                        return "released"
                    return "not owner: left untouched"

                me = str(uuid.UUID(int=1))
                print(set_nx("lock:report", me))
                redis["lock:report"] = str(uuid.UUID(int=2))
                print(release("lock:report", me), redis)
            """),
            ex("Redis lock commands", "intermediate", "Acquire with NX PX, release with an atomic Lua check.", "bash", """
                SET lock:report:2026-10-17 <random-owner-id> NX PX 30000
                EVAL "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end" 1 lock:report:2026-10-17 <random-owner-id>
            """, runnable=False),
        ],
        ["SET lock:k <owner> NX PX 30000", "Release: compare owner, then DEL (atomic Lua)", "Correctness: etcd/ZooKeeper + fencing token", "Alternative: SELECT … FOR UPDATE / version column", "Critical section ≪ TTL"],
        ["Releasing a lock with plain DEL, freeing someone else's lock after your TTL expired.", "Locks without TTL that stay held forever after a crash.", "Using an efficiency lock (single Redis) where correctness is required."],
        [
            qa("intermediate", "How do you implement a simple distributed lock with Redis?", "SET key with a random owner value, NX (only if absent) and PX (TTL). Release with a Lua script that deletes the key only if the value still matches, so you never remove another client's lock."),
            qa("advanced", "Why can a TTL-based lock be held by two clients at once?", "If the holder pauses (GC, VM migration, network stall) longer than the TTL, the lock expires and another client acquires it while the first still believes it holds it. Only fencing tokens validated by the protected resource make this safe."),
            qa("advanced", "When should you avoid distributed locks?", "When the database can enforce the invariant itself (transactions, unique constraints, conditional updates) or when work can be partitioned so each key has a single owner. These are simpler and fail more safely than external locks."),
            qa("intermediate", "What is the difference between an efficiency lock and a correctness lock?", "An efficiency lock only prevents wasted duplicate work; occasional double execution is acceptable, so a simple Redis lock works. A correctness lock prevents data corruption and needs a consensus-backed lock service plus fencing tokens."),
        ],
        ["leader-election", "consensus-raft", "idempotency-keys"],
        chain(
            ("Client 1", "SET NX PX", "Acquire", "Client 1 acquires the lock and receives fencing token 33."),
            ("Lock service", "token 33", "Grant", "The lock has a 10 s TTL.", "acquire"),
            ("GC pause", "15 s stall", "Stall", "Client 1 freezes; its lease expires and client 2 gets token 34.", "expires"),
            ("Storage", "max token 34", "Accept newer", "Storage accepts client 2's write with token 34.", "token 34"),
            ("Client 1", "token 33", "Fenced", "Client 1 resumes and writes with token 33; storage rejects it.", "rejected"),
        ),
    ),
    topic(
        "clocks-ordering", "Clocks & Ordering: Lamport and Vector Clocks", "distributed", "advanced", "CL",
        "Why wall clocks lie, and how logical clocks capture happened-before.",
        "Two diaries kept in different countries cannot be ordered by their handwritten times if one person's watch is wrong. But if a letter mentions the other's entry, you know which came first.",
        "Physical clocks on different machines drift and are corrected by NTP, so timestamps can be skewed by milliseconds or more and may even jump backwards; ordering events across machines by wall-clock time can reorder causally related events and make last-writer-wins drop data. Lamport clocks are counters incremented on every event and set to max(local, received) + 1 on message receipt; they guarantee that if A happened before B then L(A) < L(B), giving a total order consistent with causality (ties broken by node id), but cannot tell you whether two events were concurrent. Vector clocks keep one counter per node; comparing vectors tells you whether A happened before B, B before A, or they are concurrent, which is how Dynamo-style stores detect conflicting writes for siblings or merges. Hybrid logical clocks (HLC) combine physical time with a logical counter, staying close to wall time while preserving causality (CockroachDB, MongoDB). Google Spanner's TrueTime exposes clock uncertainty bounds and waits them out to provide externally consistent timestamps.",
        ["Detecting concurrent updates in a leaderless key-value store.", "Ordering events in distributed logs and traces.", "Generating causally consistent timestamps for MVCC (HLC).", "Explaining why last-writer-wins loses updates."],
        [
            "Never rely on wall-clock order across machines for correctness.",
            "Lamport: happened-before ⇒ smaller timestamp (not the converse).",
            "Vector clocks detect concurrency; size grows with writers.",
            "HLC ≈ physical time + logical counter, fits in 64 bits.",
            "Use monotonic clocks for measuring durations and timeouts.",
        ],
        [
            ex("Lamport clocks across three processes", "intermediate", "Message receipt pulls the receiver's clock forward.", "python", """
                clock = {"A": 0, "B": 0, "C": 0}

                def local(p, what):
                    clock[p] += 1
                    print(f"{p} {what:<16} L={clock[p]}")
                    return clock[p]

                def send(src, dst):
                    ts = local(src, f"send to {dst}")
                    clock[dst] = max(clock[dst], ts) + 1
                    print(f"{dst} recv from {src:<6} L={clock[dst]}")

                local("A", "write x")
                send("A", "B")
                local("C", "write y")
                send("B", "C")
                local("C", "write z")
            """),
            ex("Vector clocks detect concurrent writes", "advanced", "Compare versions to decide overwrite vs conflict.", "python", """
                def compare(a, b):
                    keys = set(a) | set(b)
                    le = all(a.get(k, 0) <= b.get(k, 0) for k in keys)
                    ge = all(a.get(k, 0) >= b.get(k, 0) for k in keys)
                    if le and ge:
                        return "equal"
                    if le:
                        return "a happened before b"
                    if ge:
                        return "b happened before a"
                    return "concurrent -> keep both siblings / merge"

                base = {"n1": 1}
                alice = {"n1": 2}
                bob = {"n1": 1, "n2": 1}
                merged = {"n1": 2, "n2": 1, "n3": 1}
                print("base vs alice :", compare(base, alice))
                print("alice vs bob  :", compare(alice, bob))
                print("bob vs merged :", compare(bob, merged))
            """),
            ex("Clock skew breaks last-writer-wins", "basic", "The later write loses because its server clock is behind.", "python", """
                writes = [("server-1 (clock +0 ms)", 1_000_000, "cart=[book]"),
                          ("server-2 (clock -80 ms)", 1_000_050 - 80, "cart=[book, pen]")]
                winner = max(writes, key=lambda w: w[1])
                print("real order: server-1 then server-2 (50 ms later)")
                print("LWW keeps:", winner[2], "from", winner[0])
            """),
        ],
        ["Lamport: on send L+=1; on recv L = max(L, msg)+1", "Vector: a ≤ b for all entries ⇒ a → b", "HLC = (max(physical, last), logical counter)", "Durations: time.monotonic(), not time.time()", "NTP skew: assume ms, sometimes seconds"],
        ["Using wall-clock timestamps for last-writer-wins across nodes.", "Measuring timeouts with wall-clock time that can jump.", "Unbounded vector clock growth with many clients (prune or use dotted version vectors)."],
        [
            qa("intermediate", "Why can't you order events across servers by timestamp?", "Each server's clock drifts and NTP corrections can step it, so skew of milliseconds to seconds is normal. A causally later event can carry an earlier timestamp, so wall-clock ordering can reorder events and make last-writer-wins drop newer data."),
            qa("advanced", "What does a Lamport clock guarantee?", "If event A happened before B, then L(A) < L(B), so sorting by (L, node id) gives a total order consistent with causality. The converse does not hold: L(A) < L(B) does not mean A caused B, so it cannot detect concurrency."),
            qa("advanced", "How do vector clocks detect conflicts?", "Each replica keeps a counter per node; a version dominates another if every entry is greater or equal. If neither dominates, the writes were concurrent and the store keeps both siblings for the application or a CRDT to merge."),
            qa("advanced", "What are hybrid logical clocks?", "Timestamps that track the maximum physical time seen plus a logical counter for events within the same tick. They stay close to wall time for human readability and bounded staleness reads while still respecting causality, and are used by CockroachDB and MongoDB."),
        ],
        ["consistency-cap", "replication", "case-kv-store"],
        chain(
            ("Process A", "L = 1", "Local event", "A writes x and increments its clock to 1."),
            ("Message", "carries L = 2", "Send", "A sends a message stamped with L = 2.", "L=2"),
            ("Process B", "max(0, 2)+1 = 3", "Receive", "B jumps its clock past the sender's: L = 3.", "recv"),
            ("Process C", "L = 5", "Causal chain", "Anything caused by B's event gets a larger timestamp.", "L=4"),
            ("Vector clock", "{A:1, B:1}", "Detect concurrency", "Vectors also reveal when two writes are concurrent, not ordered.", "compare"),
        ),
    ),
    topic(
        "gossip-protocols", "Gossip Protocols & Failure Detection", "distributed", "intermediate", "GP",
        "Spread membership and state epidemically, and detect failed nodes without a central monitor.",
        "Office rumours: each person tells a few random colleagues every hour, and within a morning the whole building knows, even if some people are out sick.",
        "Gossip (epidemic) protocols spread information by having each node periodically pick a few random peers and exchange state. Because informed nodes grow exponentially, a message reaches all N nodes in O(log N) rounds with high probability, and the protocol keeps working when nodes fail or messages drop. Cassandra, Consul (Serf/memberlist), DynamoDB-style stores and Redis Cluster use gossip for membership, ring ownership, load and schema versions. Failure detection piggybacks on it: heartbeat counters that stop increasing mark a node as suspect, or SWIM-style probes ask a peer to ping directly and then indirectly through k other nodes before declaring it dead, which reduces false positives from a single bad link. The phi accrual detector (Cassandra) outputs a suspicion level based on the observed inter-arrival distribution instead of a fixed timeout. Gossip is eventually consistent: state converges but there is no single moment when everyone agrees, so it is used for soft state, not for decisions that need consensus.",
        ["Cluster membership in Cassandra and Consul.", "Spreading ring/token ownership and load information.", "Decentralized failure detection without a single monitor.", "Anti-entropy repair between replicas."],
        [
            "Spread time ≈ O(log N) rounds; fan-out of 2-3 peers per round is typical.",
            "Robust to node failures and message loss; no single point of failure.",
            "SWIM: direct ping → indirect ping via k peers → suspect → dead.",
            "Phi accrual adapts the threshold to observed heartbeat jitter.",
            "Eventual convergence: use consensus for decisions that must be agreed.",
        ],
        [
            ex("Rounds to spread a rumour", "intermediate", "Push gossip with fan-out 2 across cluster sizes.", "python", """
                import math, random
                random.seed(13)

                def rounds_to_spread(n, fanout=2, loss=0.1):
                    informed, rounds = {0}, 0
                    while len(informed) < n:
                        rounds += 1
                        for node in list(informed):
                            for peer in random.sample(range(n), fanout):
                                if random.random() > loss:
                                    informed.add(peer)
                    return rounds

                for n in (10, 100, 1000, 5000):
                    print(f"{n:>5} nodes: {rounds_to_spread(n):>2} rounds (log2 N = {math.log2(n):.1f}), 10% message loss")
            """),
            ex("Heartbeat-counter failure detection", "intermediate", "A node whose counter stops advancing becomes suspect, then dead.", "python", """
                SUSPECT_AFTER, DEAD_AFTER = 3, 6
                view = {"n1": [0, 0], "n2": [0, 0], "n3": [0, 0]}
                for tick in range(1, 9):
                    for node, (hb, last) in view.items():
                        if node == "n3" and tick > 2:
                            continue
                        view[node] = [hb + 1, tick]
                    status = {}
                    for node, (hb, last) in view.items():
                        age = tick - last
                        status[node] = "dead" if age >= DEAD_AFTER else "suspect" if age >= SUSPECT_AFTER else "alive"
                    print(f"tick {tick}: {status}")
            """),
        ],
        ["Gossip interval ~1 s, fan-out 2-3", "Convergence ≈ log_fanout(N) rounds", "SWIM: ping timeout → ping-req via k=3 peers", "Cassandra: phi_convict_threshold = 8", "consul members · nodetool status"],
        ["Declaring nodes dead on one missed heartbeat (false positives during GC or network blips).", "Using gossip state for decisions that require agreement, like leader choice.", "Large gossip payloads that grow with cluster size and saturate the network."],
        [
            qa("basic", "What is a gossip protocol?", "A decentralized way to disseminate state where each node periodically exchanges information with a few random peers. Information spreads exponentially, reaching all nodes in about log N rounds, and tolerates failures without a central coordinator."),
            qa("intermediate", "How does SWIM reduce false failure detections?", "If a direct ping times out, the node asks k other members to ping the target on its behalf. Only if all indirect probes fail is the node marked suspect, and it can refute suspicion by gossiping an incarnation number before being declared dead."),
            qa("advanced", "What is the phi accrual failure detector?", "Instead of a fixed timeout, it models the distribution of heartbeat inter-arrival times and outputs phi, the suspicion level that the node has failed given the time since the last heartbeat. Applications choose a phi threshold, which adapts automatically to noisy networks."),
            qa("intermediate", "Why is gossip unsuitable for electing a leader?", "Gossip gives eventual convergence, so different nodes can temporarily hold different views and two could both believe they lead. Leadership needs consensus with a majority quorum to guarantee a single agreed answer."),
        ],
        ["consistent-hashing", "case-kv-store", "consensus-raft"],
        chain(
            ("Node A", "learns change", "New state", "Node A learns node F joined the cluster."),
            ("Round 1", "A → B, D", "Gossip", "A tells two random peers.", "digest"),
            ("Round 2", "4 nodes know", "Exponential spread", "Each informed node tells two more.", "digest"),
            ("Round log N", "all nodes", "Converged", "After ~log N rounds every node has the update, despite losses.", "digest"),
            ("Detector", "suspect → dead", "Failure detection", "Heartbeats that stop advancing mark a node suspect, then dead.", "heartbeats"),
        ),
    ),
    topic(
        "exactly-once", "Delivery Semantics & the Exactly-Once Myth", "distributed", "advanced", "EO",
        "At-most-once, at-least-once, and how 'exactly-once' really means idempotent effects.",
        "Mailing a cheque: if you never resend, it might get lost (at most once). If you resend whenever unsure, the payee might get two (at least once). The bank refusing duplicate cheque numbers is what makes it effectively once.",
        "Over an unreliable network, a sender cannot distinguish a lost message from a lost acknowledgement, so end-to-end exactly-once delivery is impossible in general. At-most-once sends without retry (or commits progress before processing) and may lose messages. At-least-once retries until acknowledged (or processes before committing progress) and may duplicate. What systems actually provide is exactly-once processing or effects: at-least-once delivery combined with idempotent or transactional handling. Techniques include idempotent consumers that dedupe by message id, upserts keyed by business id, storing the consumer offset in the same transaction as the result, and Kafka's idempotent producers plus transactions, which give exactly-once semantics for read-process-write pipelines within Kafka. Effects that leave the system (emails, card charges, third-party API calls) are outside any broker transaction and need idempotency keys at the external system. The rule of thumb: assume duplicates and reordering, and make every handler safe to run twice.",
        ["Payment and order event consumers.", "Stream processing aggregations (Kafka Streams, Flink).", "Webhook delivery to customers.", "Billing usage metering."],
        [
            "Commit after process = at-least-once; commit before process = at-most-once.",
            "Exactly-once effect = at-least-once + idempotent handler.",
            "Store offset and result atomically to avoid gaps and duplicates.",
            "Kafka EOS covers Kafka-to-Kafka; external side effects need their own keys.",
            "Design for duplicates and out-of-order delivery everywhere.",
        ],
        [
            ex("Crash between process and commit", "intermediate", "At-least-once redelivers; dedup makes the effect happen once.", "python", """
                messages = [("m1", 10), ("m2", 20), ("m3", 30)]

                def consume(dedupe):
                    committed, balance, seen = 0, 0, set()
                    crashed = False
                    while committed < len(messages):
                        mid, amount = messages[committed]
                        if not (dedupe and mid in seen):
                            balance += amount
                            seen.add(mid)
                        if mid == "m2" and not crashed:
                            crashed = True
                            continue
                        committed += 1
                    return balance

                print("at-least-once, naive  :", consume(False), "(expected 60)")
                print("at-least-once + dedupe:", consume(True))
            """),
            ex("Atomic offset + result", "advanced", "Keep the consumer position in the same SQLite transaction as the effect.", "python", """
                import sqlite3
                db = sqlite3.connect(":memory:")
                db.executescript("CREATE TABLE totals(k TEXT PRIMARY KEY, v INT); CREATE TABLE offsets(p INT PRIMARY KEY, off INT);"
                                 "INSERT INTO totals VALUES ('sum', 0); INSERT INTO offsets VALUES (0, 0);")
                log = [5, 7, 11, 13]

                def process_from_stored_offset(crash_at=None):
                    off = db.execute("SELECT off FROM offsets WHERE p = 0").fetchone()[0]
                    for i in range(off, len(log)):
                        with db:
                            db.execute("UPDATE totals SET v = v + ? WHERE k = 'sum'", (log[i],))
                            if i == crash_at:
                                raise RuntimeError("crash mid-transaction")
                            db.execute("UPDATE offsets SET off = ? WHERE p = 0", (i + 1,))

                try:
                    process_from_stored_offset(crash_at=2)
                except RuntimeError as e:
                    print("first run:", e)
                process_from_stored_offset()
                print("sum =", db.execute("SELECT v FROM totals").fetchone()[0], "(expected 36)")
            """),
            ex("Kafka exactly-once settings", "advanced", "Idempotent producer and transactional read-process-write.", "properties", """
                # producer
                enable.idempotence=true
                acks=all
                transactional.id=orders-enricher-1
                # consumer
                isolation.level=read_committed
                enable.auto.commit=false
                # Kafka Streams
                processing.guarantee=exactly_once_v2
            """, runnable=False),
        ],
        ["At-most-once: commit → process", "At-least-once: process → commit", "Effectively-once: at-least-once + dedupe/upsert", "Kafka: enable.idempotence=true, acks=all, isolation.level=read_committed", "External calls: pass an idempotency key"],
        ["Believing a broker's 'exactly-once' flag covers emails or payment API calls.", "Auto-committing offsets before processing finishes (silent message loss).", "Dedupe tables without expiry or bounded windows growing forever."],
        [
            qa("intermediate", "Why is exactly-once delivery impossible in general?", "When an acknowledgement does not arrive, the sender cannot tell whether the message or the ack was lost. It must either retry, risking duplicates, or not retry, risking loss; no protocol avoids both over an unreliable network (Two Generals problem)."),
            qa("intermediate", "How do you get exactly-once effects in practice?", "Use at-least-once delivery and make processing idempotent: dedupe by message or business id, use upserts and conditional writes, or commit the consumer offset in the same transaction as the result."),
            qa("advanced", "What does Kafka's exactly-once semantics actually guarantee?", "Idempotent producers remove duplicates from producer retries, and transactions atomically write output records and consumer offsets, so read-process-write within Kafka has each input reflected exactly once for read_committed consumers. Side effects outside Kafka are not covered."),
            qa("advanced", "Where should offsets be committed relative to processing?", "After processing for at-least-once; the safest pattern stores the offset with the result in the same database transaction, so on restart the consumer resumes exactly where its last committed effect ended."),
        ],
        ["idempotency-keys", "message-queues", "outbox-pattern"],
        chain(
            ("Broker", "offset 41", "Deliver", "The broker delivers message 41 to a consumer."),
            ("Consumer", "process", "Process", "The consumer applies the effect, e.g. credit an account.", "msg 41"),
            ("Crash", "before commit", "Crash", "It crashes before committing offset 42.", "crash"),
            ("Redelivery", "msg 41 again", "At-least-once", "On restart the broker redelivers message 41.", "msg 41"),
            ("Dedupe", "seen msg 41", "Idempotent effect", "The consumer sees it already applied 41 and skips: effectively once.", "skip"),
        ),
    ),
    topic(
        "event-driven", "Event-Driven Architecture", "architecture", "intermediate", "ED",
        "Services publish facts; others react. Loose coupling with new failure modes.",
        "A newspaper: the paper publishes stories without knowing who reads them, and each reader reacts in their own way. Adding a reader does not require the paper to change.",
        "In event-driven architecture, services publish events describing facts that happened (OrderPlaced, PaymentCaptured) to a broker such as Kafka, SNS/SQS, Pub/Sub or NATS, and other services subscribe and react. Publishers do not know their consumers, so new features can be added by subscribing without changing the source, and the publisher is not blocked by slow consumers. Event notification carries just an id (consumers call back for details), while event-carried state transfer includes the data consumers need, reducing coupling at runtime. Choreography (each service reacts to events) suits simple flows; orchestration (a coordinator issues commands) keeps complex workflows visible. Costs include eventual consistency, harder debugging across asynchronous hops, duplicate and out-of-order delivery, and schema evolution: version events, add fields compatibly, and use a schema registry. Partition by entity id to preserve per-entity ordering, give every event an id, type, version, timestamp and correlation id, and make consumers idempotent.",
        ["Order placed → inventory, email, analytics, fraud react independently.", "Decoupling a monolith gradually (strangler with events).", "Real-time analytics and feature pipelines.", "Audit trails of business facts."],
        [
            "Events are past-tense facts; commands are requests to do something.",
            "Partition by entity id for per-entity ordering.",
            "Consumers are idempotent and tolerate reordering.",
            "Schema registry + compatible evolution (add optional fields).",
            "Trace with correlation ids across async hops.",
        ],
        [
            ex("In-process event bus with independent subscribers", "basic", "One event, several reactions; a failing subscriber does not block the others.", "python", """
                from collections import defaultdict
                subs = defaultdict(list)
                dead_letter = []

                def on(event_type):
                    def register(fn):
                        subs[event_type].append(fn)
                        return fn
                    return register

                def publish(event):
                    for fn in subs[event["type"]]:
                        try:
                            fn(event)
                        except Exception as e:
                            dead_letter.append((fn.__name__, event["id"], str(e)))

                @on("OrderPlaced")
                def reserve_stock(e): print("inventory: reserve", e["items"])

                @on("OrderPlaced")
                def send_email(e): raise TimeoutError("smtp timeout")

                @on("OrderPlaced")
                def analytics(e): print("analytics: revenue +", e["total"])

                publish({"id": "evt-1", "type": "OrderPlaced", "version": 2, "order_id": 7, "items": ["book"], "total": 499})
                print("dead letters:", dead_letter)
            """),
            ex("Per-key ordering with partitions", "intermediate", "Events for the same order always land on the same partition.", "python", """
                import hashlib
                partitions = {i: [] for i in range(3)}
                events = [("order-1", "Placed"), ("order-2", "Placed"), ("order-1", "Paid"), ("order-1", "Shipped"), ("order-2", "Cancelled")]
                for key, ev in events:
                    p = int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], "big") % 3
                    partitions[p].append(f"{key}:{ev}")
                for p, evs in partitions.items():
                    print(p, evs)
            """),
            ex("Event envelope", "intermediate", "Fields every event should carry.", "json", """
                {
                  "id": "01J9Z6Q4N8C2V7K3M5T1R0W9XY",
                  "type": "OrderPlaced",
                  "version": 2,
                  "occurred_at": "2026-10-17T17:15:02Z",
                  "source": "orders-service",
                  "correlation_id": "req-7f3a",
                  "key": "order-7",
                  "data": { "order_id": 7, "customer_id": 42, "total_cents": 49900 }
                }
            """, runnable=False),
        ],
        ["Event: past tense, immutable · Command: imperative", "Kafka key = entity id → per-entity order", "Schema registry: BACKWARD compatibility", "Envelope: id, type, version, occurred_at, correlation_id", "DLQ + replay tooling"],
        ["Publishing events from the app after a DB commit without an outbox (lost events on crash).", "Choreography so tangled nobody can explain the order workflow.", "Breaking consumers with incompatible schema changes."],
        [
            qa("basic", "What are the benefits of event-driven architecture?", "Loose coupling (publishers do not know consumers), independent scaling and deployment, resilience to slow consumers through buffering, and easy addition of new reactions to existing events."),
            qa("intermediate", "Choreography vs orchestration?", "In choreography each service listens and reacts to events, which is decentralized but makes long workflows hard to see and change. In orchestration a coordinator sends commands and tracks state, which centralizes logic and visibility at the cost of a component that knows every step."),
            qa("intermediate", "How do you evolve event schemas safely?", "Use a schema registry with compatibility rules, only add optional fields, never change field meanings, and introduce a new event version or type for breaking changes while publishing both during migration."),
            qa("advanced", "How do you debug a flow spanning many async services?", "Propagate a correlation or trace id in every event, emit traces for publish and consume spans (OpenTelemetry links), log event ids, and monitor consumer lag and dead-letter queues per subscription."),
        ],
        ["message-queues", "event-sourcing-cqrs", "outbox-pattern"],
        chain(
            ("Orders svc", "commit order 7", "Fact happens", "An order is placed and committed in the orders database."),
            ("Topic", "orders, key=7", "Publish", "OrderPlaced is published to a partitioned topic.", "OrderPlaced"),
            ("Inventory", "reserve stock", "React", "Inventory reserves stock from its own consumer group.", "event"),
            ("Email", "send receipt", "React", "Email sends a receipt; failures go to a DLQ for retry.", "event"),
            ("Analytics", "update revenue", "React", "Analytics updates dashboards; adding it required no change to Orders.", "event"),
        ),
    ),
    topic(
        "event-sourcing-cqrs", "Event Sourcing & CQRS", "architecture", "advanced", "ES",
        "Store every change as an immutable event; build read models optimized for queries.",
        "A bank statement instead of a balance field: the balance is just the sum of every transaction, and you can always recompute it or answer 'what was it last March?'.",
        "Event sourcing persists the state of an entity as an append-only sequence of domain events (AccountOpened, MoneyDeposited, MoneyWithdrawn) rather than overwriting the current state. Current state is rebuilt by folding events, and snapshots every N events keep rebuilds fast. Writes append events with an expected version (optimistic concurrency), so two conflicting commands on the same aggregate cannot both succeed. The event log gives a complete audit trail, time travel, and the ability to build new projections by replaying history. CQRS (command query responsibility segregation) separates the write model, which validates commands and emits events, from one or more read models (projections) optimized for specific queries, such as a denormalized table, a search index or a cache. Read models are updated asynchronously, so they are eventually consistent with the write side. The costs are real: event schema versioning (upcasters), replay times, harder ad-hoc queries, and GDPR deletion (crypto-shredding or keeping personal data outside events). Use it for domains where history and auditability matter, not as a default for every service.",
        ["Ledgers, payments and accounting.", "Order lifecycles with audit requirements.", "Collaborative tools that need history and undo.", "Building new analytics views by replaying events."],
        [
            "State = fold(events); snapshot every N events.",
            "Append with expected version for optimistic concurrency.",
            "Projections are disposable: rebuild by replay.",
            "Read models are eventually consistent; design the UI for it.",
            "Version events and upcast old ones on read.",
        ],
        [
            ex("Event-sourced account with projection", "advanced", "Rebuild state, reject a conflicting append, and maintain a read model.", "python", """
                store = {}

                def append(stream, expected_version, event):
                    events = store.setdefault(stream, [])
                    if len(events) != expected_version:
                        raise ValueError(f"concurrency conflict: expected v{expected_version}, at v{len(events)}")
                    events.append(event)

                def balance(stream, upto=None):
                    total = 0
                    for e in store.get(stream, [])[:upto]:
                        total += e["amount"] if e["type"] == "Deposited" else -e["amount"]
                    return total

                append("acct-1", 0, {"type": "Deposited", "amount": 100})
                append("acct-1", 1, {"type": "Withdrawn", "amount": 30})
                append("acct-1", 2, {"type": "Deposited", "amount": 50})
                try:
                    append("acct-1", 2, {"type": "Withdrawn", "amount": 500})
                except ValueError as e:
                    print("rejected:", e)
                print("balance now:", balance("acct-1"), "| after 2 events:", balance("acct-1", 2))

                read_model = {s: {"balance": balance(s), "txns": len(ev)} for s, ev in store.items()}
                print("projection:", read_model)
            """),
            ex("Snapshots bound replay cost", "intermediate", "Replay only events after the latest snapshot.", "python", """
                events = [1] * 10_437
                SNAP_EVERY = 1000
                snapshots = {i: sum(events[:i]) for i in range(0, len(events) + 1, SNAP_EVERY)}
                last = max(i for i in snapshots if i <= len(events))
                state = snapshots[last] + sum(events[last:])
                print(f"replayed {len(events) - last} events from snapshot at {last}; state = {state}")
            """),
        ],
        ["Append: INSERT … WHERE version = expected", "Snapshot every 100-1,000 events", "Projection: consume events → upsert read table", "Rebuild read model: replay from offset 0", "PII: crypto-shredding (delete per-user key)"],
        ["Event sourcing a simple CRUD service and paying the complexity tax for nothing.", "Storing technical 'row updated' events instead of meaningful domain events.", "Reading your own write from an async projection and showing stale data."],
        [
            qa("intermediate", "What problem does event sourcing solve?", "It keeps the full history of changes as the source of truth, enabling audit trails, temporal queries, debugging by replay, and new read models built from history. It fits domains like finance where 'how did we get here' matters."),
            qa("intermediate", "What is CQRS and how does it relate to event sourcing?", "CQRS splits the write model (commands, validation) from read models optimized for queries. It pairs naturally with event sourcing because events feed projections, but each can be used without the other."),
            qa("advanced", "How do you handle concurrency in an event-sourced aggregate?", "Each append carries the expected stream version; the store only appends if the current version matches, otherwise the command is retried after reloading. This is optimistic concurrency per aggregate, with no locks."),
            qa("advanced", "How do you change an event's schema after years of history?", "Never rewrite history in place. Add versioned event types, write upcasters that transform old versions when reading, or run a controlled migration that copies streams into new ones, and keep consumers tolerant to unknown fields."),
            qa("advanced", "How do you delete personal data from an immutable event log?", "Keep PII out of events where possible, referencing it by id, or encrypt each user's personal fields with a per-user key and delete the key on request (crypto-shredding), which makes those fields unreadable everywhere."),
        ],
        ["event-driven", "sagas", "outbox-pattern"],
        chain(
            ("Command", "Withdraw 30", "Command", "A command arrives for account 1."),
            ("Aggregate", "fold → 100", "Load and validate", "Replay events (from a snapshot) to get balance 100; 30 is allowed.", "load"),
            ("Event store", "append v2", "Append", "Append MoneyWithdrawn with expected version 1.", "event"),
            ("Projector", "consume events", "Project", "A projector consumes new events asynchronously.", "stream"),
            ("Read model", "balance = 70", "Query", "Queries read a denormalized balance table, slightly behind the log.", "upsert"),
        ),
    ),
    topic(
        "sagas", "Sagas & Distributed Transactions", "architecture", "advanced", "SG",
        "Multi-service workflows with local transactions and compensations instead of 2PC.",
        "Booking a trip: reserve the flight, then the hotel, then the car. If the car is unavailable, you cancel the hotel and the flight, rather than locking all three companies' systems until you decide.",
        "When a business operation spans services with separate databases, a single ACID transaction is not available. Two-phase commit (2PC) coordinates a prepare and commit across participants, but it blocks while the coordinator is down, holds locks across the network, and is poorly supported by modern brokers and SaaS APIs. A saga splits the operation into a sequence of local transactions, each publishing an event or reply; if a step fails, previously completed steps are undone by compensating transactions (refund, release stock, cancel booking). Orchestrated sagas use a coordinator that persists the saga state and sends commands, which makes the flow explicit and testable; choreographed sagas react to each other's events. Sagas give atomicity of outcome but not isolation: other transactions can see intermediate states, so use semantic locks (status = PENDING), commutative updates, and reorder steps so irreversible actions (sending an email, charging a card) come last or are pivot steps. Every step and compensation must be idempotent and retryable, and a workflow engine (Temporal, Step Functions, Camunda) often handles durability, timers and retries.",
        ["Order checkout across order, payment, inventory and shipping services.", "Travel bookings across external providers.", "Account onboarding spanning KYC, billing and provisioning.", "Long-running workflows with human approval steps."],
        [
            "Each step is a local ACID transaction + a message.",
            "Compensations are semantic undo, not rollback; they must be idempotent.",
            "Order steps: retryable first, pivot, then non-compensatable last.",
            "No isolation: use pending states and semantic locks.",
            "Persist saga state; use a workflow engine for timers and retries.",
        ],
        [
            ex("Orchestrated saga with compensation", "advanced", "Shipping fails, so earlier steps are compensated in reverse order.", "python", """
                log = []

                def step(name, fail=False):
                    def do():
                        if fail:
                            raise RuntimeError(f"{name} failed")
                        log.append(f"do {name}")
                    def undo():
                        log.append(f"undo {name}")
                    return name, do, undo

                def run_saga(steps):
                    done = []
                    for name, do, undo in steps:
                        try:
                            do()
                            done.append((name, undo))
                        except RuntimeError as e:
                            log.append(f"error: {e}")
                            for prev, comp in reversed(done):
                                comp()
                            return "COMPENSATED"
                    return "COMPLETED"

                result = run_saga([step("create order (PENDING)"), step("reserve stock"), step("authorize payment"), step("book courier", fail=True)])
                print(result)
                print(*log, sep=" | ")
            """),
            ex("Why 2PC blocks", "intermediate", "Participants that voted yes must wait for a crashed coordinator.", "python", """
                participants = {"orders": "prepared", "payments": "prepared", "inventory": "prepared"}
                coordinator_alive = False
                for name, state in participants.items():
                    if state == "prepared" and not coordinator_alive:
                        print(f"{name}: holding locks, cannot commit or abort until coordinator recovers")
            """),
        ],
        ["Saga state: PENDING → … → COMPLETED | COMPENSATED", "Compensation: refund, release, cancel (idempotent)", "Pivot step: the point of no return", "Timeouts trigger compensation", "Engines: Temporal, AWS Step Functions, Camunda"],
        ["Compensations that are not idempotent, refunding twice on retry.", "Sending irreversible side effects (emails, shipments) before the pivot step.", "Assuming isolation: other requests can read PENDING orders."],
        [
            qa("intermediate", "Why not use two-phase commit across microservices?", "2PC holds locks across the network until the coordinator decides, blocks if the coordinator fails after prepare, couples availability of all participants, and many datastores and external APIs do not support XA. Sagas avoid these by committing locally and compensating."),
            qa("intermediate", "What is a compensating transaction?", "A business-level action that semantically undoes a completed step, such as refunding a captured payment or releasing reserved stock. It does not erase history, may leave traces (a refund record), and must be idempotent and retryable."),
            qa("advanced", "Orchestration vs choreography for sagas?", "Orchestration uses a coordinator that stores saga state and sends commands, making the flow explicit, easier to monitor and change. Choreography has services react to events, which avoids a central component but spreads the workflow logic and makes cycles and failures harder to reason about."),
            qa("advanced", "How do you deal with the lack of isolation in sagas?", "Use semantic locks such as status = PENDING so other operations know a record is mid-saga, design commutative updates, re-read values before acting (pessimistic view), and put risky or irreversible steps after the pivot so fewer compensations are needed."),
        ],
        ["outbox-pattern", "event-driven", "idempotency-keys"],
        chain(
            ("Orchestrator", "saga #881", "Start", "The orchestrator persists saga state and creates a PENDING order."),
            ("Inventory", "reserve 1 book", "Step 1", "Inventory reserves stock in its local transaction and replies.", "ReserveStock"),
            ("Payment", "authorize ₹499", "Step 2", "Payment authorizes the card (the pivot step).", "Authorize"),
            ("Shipping", "fails", "Step 3 fails", "No courier is available; the step fails after retries.", "BookCourier"),
            ("Compensate", "void + release", "Compensate", "The orchestrator voids the authorization and releases stock, marking the order CANCELLED.", "undo"),
        ),
    ),
    topic(
        "outbox-pattern", "Transactional Outbox & CDC", "architecture", "intermediate", "OX",
        "Update the database and publish an event atomically, without distributed transactions.",
        "Writing a letter and putting it in your own outbox tray in the same motion as filing the copy. The mail clerk empties the tray later, so the letter is never lost even if you leave early.",
        "The dual-write problem: a service that commits to its database and then publishes to a broker can crash between the two, losing the event, or publish and then fail to commit, emitting an event for something that never happened. The transactional outbox fixes this by inserting the event into an outbox table in the same local transaction as the business change; the commit makes both durable or neither. A separate relay then publishes outbox rows to the broker, either by polling the table (SELECT … FOR UPDATE SKIP LOCKED, mark sent) or by tailing the database log with change data capture (Debezium reading the PostgreSQL WAL or MySQL binlog). The relay delivers at least once, so events carry unique ids and consumers dedupe. Ordering is preserved per aggregate by publishing with the aggregate id as the partition key. Clean up published rows periodically. The inbox pattern is the consumer-side mirror: record processed message ids in the same transaction as the consumer's state change.",
        ["Publishing OrderPlaced reliably from an orders service.", "Keeping search indexes and caches in sync via CDC.", "Feeding sagas with reliable step events.", "Migrating from a monolith by streaming its changes."],
        [
            "Business row + outbox row in one local transaction.",
            "Relay: polling with SKIP LOCKED, or CDC from the WAL/binlog.",
            "At-least-once publish; consumers dedupe by event id.",
            "Partition key = aggregate id for ordering.",
            "Inbox table on consumers makes handling idempotent.",
        ],
        [
            ex("Outbox with SQLite: crash-safe publishing", "intermediate", "The relay publishes only committed events, even after a crash.", "python", """
                import sqlite3, json
                db = sqlite3.connect(":memory:")
                db.executescript('''
                    CREATE TABLE orders(id INTEGER PRIMARY KEY, total INT);
                    CREATE TABLE outbox(id INTEGER PRIMARY KEY, topic TEXT, payload TEXT, sent INT DEFAULT 0);
                ''')
                broker = []

                def place_order(order_id, total, crash=False):
                    with db:
                        db.execute("INSERT INTO orders VALUES (?, ?)", (order_id, total))
                        db.execute("INSERT INTO outbox(topic, payload) VALUES ('orders', ?)",
                                   (json.dumps({"type": "OrderPlaced", "order_id": order_id}),))
                        if crash:
                            raise RuntimeError("crash before commit")

                def relay():
                    rows = db.execute("SELECT id, topic, payload FROM outbox WHERE sent = 0 ORDER BY id").fetchall()
                    for rid, topic, payload in rows:
                        broker.append((topic, json.loads(payload)))
                        db.execute("UPDATE outbox SET sent = 1 WHERE id = ?", (rid,))
                    db.commit()

                place_order(1, 500)
                try:
                    place_order(2, 900, crash=True)
                except RuntimeError as e:
                    print(e)
                relay()
                print("orders:", db.execute("SELECT id FROM orders").fetchall())
                print("published:", broker)
            """),
            ex("Polling relay query (PostgreSQL)", "intermediate", "Several relays can run safely with SKIP LOCKED.", "sql", """
                BEGIN;
                SELECT id, aggregate_id, type, payload
                FROM outbox
                WHERE published_at IS NULL
                ORDER BY id
                LIMIT 100
                FOR UPDATE SKIP LOCKED;
                -- publish each row with key = aggregate_id, then:
                UPDATE outbox SET published_at = now() WHERE id = ANY(:ids);
                COMMIT;
            """, runnable=False),
            ex("Debezium outbox connector", "advanced", "CDC from the WAL with the outbox event router.", "json", """
                {
                  "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
                  "database.hostname": "orders-db",
                  "database.user": "${env:DEBEZIUM_DB_USER}",
                  "database.password": "${env:DEBEZIUM_DB_PASSWORD}",
                  "table.include.list": "public.outbox",
                  "transforms": "outbox",
                  "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
                  "transforms.outbox.table.field.event.key": "aggregate_id"
                }
            """, runnable=False),
        ],
        ["BEGIN; INSERT order; INSERT outbox; COMMIT;", "Relay: FOR UPDATE SKIP LOCKED, batch 100", "CDC: Debezium + WAL (wal_level=logical)", "Kafka key = aggregate_id", "Purge published rows after N days"],
        ["Publishing to Kafka inside the DB transaction (broker call can succeed while the commit fails).", "Relays that publish then crash before marking sent, without consumer dedupe.", "Unbounded outbox growth with no cleanup job."],
        [
            qa("intermediate", "What is the dual-write problem?", "Writing to two systems (database and broker) without a shared transaction means a crash between them leaves them inconsistent: either the event is lost or an event describes an uncommitted change."),
            qa("intermediate", "How does the transactional outbox solve it?", "The event is written to an outbox table in the same local transaction as the business data, so both commit or neither does. A relay publishes committed outbox rows to the broker asynchronously, retrying until success."),
            qa("advanced", "Polling relay vs CDC: trade-offs?", "Polling is simple and database-agnostic but adds query load and latency proportional to the poll interval. CDC reads the transaction log with low latency and no extra queries, but needs connector infrastructure, logical replication setup and monitoring of replication slots."),
            qa("advanced", "Does the outbox give exactly-once delivery?", "No, it gives at-least-once: the relay may publish a row and crash before marking it sent. Events therefore carry unique ids and consumers must be idempotent, often with an inbox table."),
        ],
        ["exactly-once", "event-driven", "sagas"],
        chain(
            ("Service", "place order", "Handle request", "The orders service handles a checkout."),
            ("Local txn", "orders + outbox", "One transaction", "It inserts the order row and an OrderPlaced outbox row, then commits.", "BEGIN…COMMIT"),
            ("Relay / CDC", "reads WAL", "Capture", "A relay or Debezium picks up the committed outbox row.", "row"),
            ("Broker", "key = order 7", "Publish", "The event is published with the aggregate id as key, at least once.", "event"),
            ("Consumers", "inbox dedupe", "Consume", "Consumers record the event id and skip duplicates.", "OrderPlaced"),
        ),
    ),
    topic(
        "service-discovery", "Service Discovery", "architecture", "intermediate", "SD",
        "How services find healthy instances of each other as they scale and move.",
        "A hospital switchboard: you ask for 'cardiology' rather than memorizing which doctor is on shift in which room, and the operator only connects you to doctors currently on duty.",
        "In dynamic environments instances come and go with autoscaling, deploys and failures, so hard-coded addresses do not work. A service registry (Consul, etcd, ZooKeeper, Eureka, or the Kubernetes API with Endpoints/EndpointSlices) tracks the live instances of each service. Registration is either self-registration (the instance registers and heartbeats, with a TTL) or third-party registration (the platform registers it, as Kubernetes does from pod readiness). Discovery is client-side (the client queries the registry and load balances itself, e.g. gRPC with xDS) or server-side (the client calls a stable virtual address, such as a Kubernetes ClusterIP, cloud load balancer or service mesh sidecar, which forwards to a healthy instance). DNS is the most universal interface (service.namespace.svc.cluster.local, SRV records), but caching can delay updates. Health checks, readiness gates and graceful deregistration on shutdown prevent traffic to dying instances. Service meshes (Istio, Linkerd) add mTLS, retries and traffic shifting on top of discovery.",
        ["Microservices on Kubernetes calling each other by name.", "VM fleets registering with Consul.", "Client-side load balancing for gRPC.", "Blue/green and canary routing via a mesh."],
        [
            "Registry holds instance → address, health and metadata.",
            "Heartbeats with TTL remove crashed instances automatically.",
            "Readiness, not liveness, controls whether traffic is sent.",
            "Deregister and drain before shutdown (preStop, SIGTERM handling).",
            "Clients cache discovery results; bound staleness and retry on failure.",
        ],
        [
            ex("Registry with TTL heartbeats and client-side balancing", "intermediate", "A crashed instance disappears after its TTL; clients round-robin over the rest.", "python", """
                import itertools
                registry = {}
                TTL = 10

                def heartbeat(service, addr, now):
                    registry.setdefault(service, {})[addr] = now + TTL

                def healthy(service, now):
                    return sorted(a for a, exp in registry.get(service, {}).items() if exp > now)

                for addr in ("10.0.0.5:8080", "10.0.0.6:8080", "10.0.0.7:8080"):
                    heartbeat("payments", addr, now=0)
                for t in (5, 10):
                    heartbeat("payments", "10.0.0.5:8080", t)
                    heartbeat("payments", "10.0.0.6:8080", t)

                for now in (8, 15):
                    live = healthy("payments", now)
                    rr = itertools.cycle(live)
                    print(f"t={now}: healthy={live} -> next calls {[next(rr) for _ in range(4)]}")
            """),
            ex("Kubernetes Service and readiness", "basic", "Server-side discovery by DNS name; only ready pods receive traffic.", "yaml", """
                apiVersion: v1
                kind: Service
                metadata: {name: payments, namespace: shop}
                spec:
                  selector: {app: payments}
                  ports: [{port: 80, targetPort: 8080}]
                ---
                # in the Deployment's container spec
                readinessProbe:
                  httpGet: {path: /ready, port: 8080}
                  periodSeconds: 5
                lifecycle:
                  preStop:
                    exec: {command: ["sleep", "10"]}
                # clients call http://payments.shop.svc.cluster.local
            """, runnable=False),
        ],
        ["K8s DNS: <svc>.<ns>.svc.cluster.local", "SRV: _grpc._tcp.payments.service.consul", "Heartbeat every TTL/3; deregister on SIGTERM", "Readiness gates traffic; liveness restarts", "Mesh: Envoy xDS endpoints + mTLS"],
        ["Clients caching DNS results forever and calling dead IPs.", "Instances that receive traffic before warming up (no readiness check).", "Killing pods without draining, causing errors during every deploy."],
        [
            qa("basic", "Why do microservices need service discovery?", "Instance addresses change constantly with autoscaling, deploys and failures. Discovery lets callers use a logical name and always reach a current healthy instance without manual configuration."),
            qa("intermediate", "Client-side vs server-side discovery?", "Client-side: the client fetches instances from the registry and load balances itself, saving a hop and allowing smart balancing, but every client needs the logic. Server-side: the client calls a stable address (load balancer, ClusterIP, sidecar) that does the routing, keeping clients simple."),
            qa("intermediate", "How does Kubernetes implement service discovery?", "Pods matching a Service's selector and passing readiness are listed in EndpointSlices; CoreDNS resolves the service name to a ClusterIP, and kube-proxy (iptables/IPVS) or eBPF forwards connections to ready endpoints."),
            qa("advanced", "How do you avoid errors during instance shutdown?", "On SIGTERM, fail the readiness check or deregister first, wait for the registry and load balancers to propagate (preStop delay), finish in-flight requests, then exit. Clients should retry idempotent requests on connection errors."),
        ],
        ["load-balancing", "microservices-gateway", "circuit-breakers"],
        chain(
            ("Instance", "payments-7", "Register", "A new instance starts, passes readiness and is registered."),
            ("Registry", "TTL 10 s", "Track health", "Heartbeats keep it listed; missed ones expire it.", "heartbeat"),
            ("Client", "resolve 'payments'", "Discover", "The caller resolves the logical name via DNS or the registry API.", "lookup"),
            ("Balancer", "pick healthy", "Choose", "Client library or sidecar picks one healthy instance.", "endpoints"),
            ("Shutdown", "drain, deregister", "Leave", "On SIGTERM it fails readiness, drains, then exits.", "SIGTERM"),
        ),
    ),
    topic(
        "data-pipelines", "Data Pipelines: Batch vs Stream", "architecture", "intermediate", "DP",
        "Moving and transforming data: nightly batches, continuous streams, windows and late events.",
        "Batch is doing laundry once a week in big loads; streaming is washing each item as soon as it is dirty. The weekly load is efficient, the continuous one keeps you always dressed.",
        "Data pipelines move data from operational systems into analytics, search, ML features and other services. Batch processing (Spark, dbt, Hadoop-style jobs) reads a bounded dataset, computes results and writes outputs, typically hourly or daily; it is simple to reason about, easy to rerun and cheap per record, but results are as stale as the schedule. Stream processing (Kafka Streams, Flink, Spark Structured Streaming) consumes unbounded event streams and updates results continuously with seconds of latency. Streams require windowing (tumbling, sliding, session), event-time semantics with watermarks to decide when a window is complete, policies for late data, and state stores with checkpointing for fault tolerance. Lambda architecture runs batch and stream side by side and merges them; Kappa architecture uses only a replayable log, reprocessing history by replaying the stream. Practical pipelines ingest via CDC and event logs into a lake (Parquet/Iceberg on object storage), make every stage idempotent and partitioned by date or key, validate schemas and data quality, and track lineage.",
        ["Daily revenue reports and finance reconciliation (batch).", "Fraud detection and real-time dashboards (stream).", "Feature pipelines for ML models.", "Replicating operational data into a warehouse via CDC."],
        [
            "Batch: bounded input, rerunnable, minutes-hours latency.",
            "Stream: unbounded input, windows, state, seconds latency.",
            "Event time + watermarks handle out-of-order data.",
            "Idempotent, partitioned outputs make backfills safe (overwrite a partition).",
            "Kappa: one code path, reprocess by replaying the log.",
        ],
        [
            ex("Tumbling windows with a watermark", "advanced", "Events arrive out of order; late events beyond the allowed lateness are dropped.", "python", """
                from collections import defaultdict
                WINDOW, LATENESS = 60, 30
                events = [(5, "click"), (61, "click"), (40, "click"), (130, "click"), (59, "click"), (200, "click"), (100, "click")]
                windows, closed, max_seen = defaultdict(int), set(), 0

                for ts, _ in events:
                    max_seen = max(max_seen, ts)
                    watermark = max_seen - LATENESS
                    w = ts // WINDOW * WINDOW
                    if w in closed:
                        print(f"event@{ts}: window {w} already closed -> late, sent to side output")
                        continue
                    windows[w] += 1
                    for start in sorted(windows):
                        if start + WINDOW <= watermark and start not in closed:
                            closed.add(start)
                            print(f"watermark {watermark}: emit window [{start},{start + WINDOW}) count={windows[start]}")
                print("open windows:", {k: v for k, v in windows.items() if k not in closed})
            """),
            ex("Idempotent batch backfill by partition", "intermediate", "Rerunning a day overwrites its partition instead of appending duplicates.", "python", """
                lake = {}
                raw = {"2026-10-15": [120, 80], "2026-10-16": [200, 50, 25]}

                def run_daily(day):
                    lake[f"revenue/dt={day}"] = sum(raw[day])

                run_daily("2026-10-15")
                run_daily("2026-10-16")
                raw["2026-10-16"].append(5)
                run_daily("2026-10-16")
                print(lake)
            """),
        ],
        ["Batch: schedule (Airflow) → Spark/dbt → partitioned Parquet", "Stream: Kafka → Flink (checkpoints) → sink", "Windows: tumbling · sliding · session", "Watermark = max event time − allowed lateness", "Backfill: INSERT OVERWRITE PARTITION (dt=…)"],
        ["Using processing time instead of event time, so replays produce different results.", "Appending on rerun and double-counting a day.", "Stream jobs without checkpointed state, losing aggregates on restart."],
        [
            qa("basic", "Batch vs stream processing?", "Batch processes a bounded dataset on a schedule: simple, efficient and easy to rerun, but results are hours old. Stream processing handles events continuously with seconds of latency, at the cost of windowing, state management and late-data complexity."),
            qa("intermediate", "What is a watermark?", "A stream processor's estimate that no more events older than time T will arrive, typically max event time seen minus an allowed lateness. When the watermark passes a window's end, the window's result is emitted; later events are dropped, sent to a side output, or trigger an update."),
            qa("intermediate", "Lambda vs Kappa architecture?", "Lambda runs a batch layer for accurate recomputation and a speed layer for fresh results, merging them at query time, which means two codebases. Kappa uses a single streaming pipeline over a replayable log and reprocesses history by replaying, simplifying the system when the log retains enough data."),
            qa("advanced", "How do you make a pipeline safe to rerun?", "Make every stage deterministic and idempotent: read a fixed input partition, compute with event-time logic, and atomically overwrite the output partition (or upsert by key). Track run metadata and data-quality checks so backfills are routine instead of risky."),
        ],
        ["message-queues", "event-driven", "blob-storage"],
        chain(
            ("Sources", "DB CDC + events", "Ingest", "Change data capture and app events flow into Kafka."),
            ("Stream job", "Flink windows", "Real-time path", "A stream job computes per-minute aggregates with event-time windows.", "events"),
            ("Lake", "Parquet by dt", "Land raw data", "Raw events are also written to object storage, partitioned by date.", "raw"),
            ("Batch job", "nightly Spark", "Recompute", "Nightly batch jobs recompute exact results and overwrite partitions.", "partitions"),
            ("Serving", "dashboards, ML", "Serve", "Dashboards read fresh stream results and corrected batch results.", "tables"),
        ),
    ),
    topic(
        "retries-backoff", "Retries, Exponential Backoff & Jitter", "reliability", "intermediate", "RB",
        "Retry transient failures without turning a blip into a self-inflicted outage.",
        "If a crowded shop door jams and everyone pushes again at exactly the same moment, it jams again. If each person waits a random, growing amount of time, the crowd flows through.",
        "Retries recover from transient failures such as timeouts, connection resets, 503 and 429 responses, but naive retries multiply load exactly when a dependency is struggling. Exponential backoff increases the wait after each attempt (base × 2^attempt, capped), and jitter randomizes it so clients that failed together do not retry together; 'full jitter' (sleep uniform(0, backoff)) spreads load best. Retry only idempotent operations or those protected by idempotency keys, only on retryable errors (not 400 or 403), and honour Retry-After. Limit attempts (2-3) and bound total time with the caller's deadline. In deep call chains, retries at every layer multiply: 3 retries at each of 4 layers can send 3^4 = 81 requests to the bottom service, so retry at one layer (usually closest to the client) and use retry budgets (for example at most 10% extra requests) or token buckets to cap retry volume. Hedged requests are a related technique: send a second copy after the p95 latency and take whichever answers first, reducing tail latency at a small load cost.",
        ["Client SDKs calling cloud APIs that return 429/503.", "Queue consumers retrying failed messages with delay.", "Service-to-service calls through a mesh retry policy.", "Mobile apps reconnecting after network loss."],
        [
            "Retry only transient errors and idempotent operations.",
            "Exponential backoff with full jitter, capped (e.g. 20 s).",
            "Limit attempts and respect the overall deadline.",
            "Retry at one layer; use retry budgets to avoid amplification.",
            "Honour Retry-After from 429/503 responses.",
        ],
        [
            ex("Backoff with full jitter (deterministic seed)", "basic", "Computes the delays a client would wait; no real sleeping.", "python", """
                import random
                random.seed(42)
                base, cap = 0.1, 20.0

                def full_jitter(attempt):
                    return random.uniform(0, min(cap, base * 2 ** attempt))

                for attempt in range(7):
                    print(f"attempt {attempt}: ceiling {min(cap, base * 2 ** attempt):6.2f}s  sleep {full_jitter(attempt):5.2f}s")
            """),
            ex("Synchronized retries vs jitter", "intermediate", "1,000 clients fail at t=0 (base 1 s); count retries landing in each 100 ms bucket.", "python", """
                import random
                from collections import Counter
                random.seed(7)
                clients, base = 1000, 1.0

                def peak(jitter):
                    buckets = Counter()
                    for _ in range(clients):
                        t = 0.0
                        for attempt in range(4):
                            delay = base * 2 ** attempt
                            t += random.uniform(0, delay) if jitter else delay
                            buckets[int(t * 10)] += 1
                    return max(buckets.values())

                print("no jitter  : peak", peak(False), "retries in one 100 ms bucket")
                print("full jitter: peak", peak(True))
            """),
            ex("Retry amplification across layers", "intermediate", "Why only one layer should retry.", "python", """
                attempts_per_layer = 3
                for layers in range(1, 5):
                    print(f"{layers} layers retrying: up to {attempts_per_layer ** layers:>3} calls hit the bottom service")
            """),
        ],
        ["sleep = uniform(0, min(cap, base × 2^attempt))", "Max 3 attempts; total ≤ caller deadline", "Retry on: timeout, reset, 503, 429 (honour Retry-After)", "Never retry: 400, 401, 403, 404, 422", "Retry budget: retries ≤ 10% of requests"],
        ["Retrying non-idempotent POSTs without idempotency keys.", "Retries at every layer of a deep call chain.", "Fixed-interval retries that synchronize clients into waves."],
        [
            qa("basic", "Why add jitter to exponential backoff?", "Clients that fail at the same time would otherwise retry at the same times, producing synchronized waves that overload the recovering service again. Randomizing the delay spreads retries out so the service sees a smooth load."),
            qa("intermediate", "Which errors should be retried?", "Transient ones: timeouts, connection errors, 502/503/504 and 429 (after Retry-After). Do not retry client errors such as 400, 401, 403, 404 or 422, because they will fail again and only add load."),
            qa("advanced", "What is retry amplification and how do you prevent it?", "When each layer of a call chain retries, attempts multiply (3 per layer over 4 layers is 81 calls). Retry at a single layer, propagate deadlines so inner layers stop when the caller has given up, and use retry budgets that cap retries to a fraction of normal traffic."),
            qa("advanced", "What are hedged requests?", "After waiting about the p95 latency without a response, send a duplicate request to another replica and use the first reply, cancelling the other. It cuts tail latency for idempotent reads at the cost of a few percent extra load."),
        ],
        ["circuit-breakers", "idempotency-keys", "bulkheads-timeouts"],
        chain(
            ("Client", "GET /quote", "Call", "The client calls a dependency with a 2 s overall deadline."),
            ("Failure", "503 / timeout", "Transient error", "The dependency returns 503; the error is retryable.", "request"),
            ("Backoff", "0-200 ms jitter", "Wait", "Sleep uniform(0, 0.1 × 2^1) instead of a fixed delay.", "retry 1"),
            ("Budget", "≤ 10% retries", "Check budget", "Only retry if the retry budget and remaining deadline allow.", "retry 2"),
            ("Success", "200 OK", "Recover", "A later attempt succeeds; synchronized waves were avoided.", "retry"),
        ),
    ),
    topic(
        "circuit-breakers", "Circuit Breakers & Graceful Degradation", "reliability", "intermediate", "CB",
        "Stop calling a failing dependency, fail fast, and serve a fallback.",
        "A household fuse trips when there is a fault so the wiring does not burn; you fix the problem and reset it, testing carefully before turning everything back on.",
        "A circuit breaker wraps calls to a dependency and tracks failures over a rolling window. In the closed state calls pass through; when the failure rate (or slow-call rate) exceeds a threshold with enough volume, it opens and immediately rejects calls for a cool-down period, so callers fail fast instead of tying up threads and the dependency gets room to recover. After the cool-down it goes half-open and lets a few trial requests through; success closes the circuit, failure reopens it. Fail fast is only useful with a fallback: cached or default data, a reduced feature (no recommendations), queueing the work for later, or a clear error. Breakers should be per dependency (and sometimes per endpoint or host) so one bad backend does not block others, and their state changes should be logged and alerted on. Combined with timeouts, bulkheads and retry budgets, breakers prevent cascading failures where one slow service exhausts resources across the whole call graph. Libraries include Resilience4j and Polly, and service meshes provide outlier detection with a similar effect.",
        ["Product pages calling optional services (recommendations, reviews).", "Payment gateways with flaky third-party providers.", "Mesh outlier detection ejecting bad hosts.", "Protecting a database from a retry storm."],
        [
            "Closed → open on failure-rate threshold with minimum volume.",
            "Open: fail fast for a cool-down; half-open: limited trial calls.",
            "Always pair with a fallback and a timeout.",
            "Scope breakers per dependency or host.",
            "Emit metrics and alerts on state transitions.",
        ],
        [
            ex("Circuit breaker state machine", "intermediate", "A simulated clock drives closed → open → half-open → closed.", "python", """
                class Breaker:
                    def __init__(self, threshold=0.5, min_calls=4, cooldown=10):
                        self.state, self.calls, self.fails, self.opened_at = "closed", 0, 0, 0
                        self.threshold, self.min_calls, self.cooldown = threshold, min_calls, cooldown

                    def call(self, now, ok):
                        if self.state == "open":
                            if now - self.opened_at < self.cooldown:
                                return "fast-fail -> fallback"
                            self.state = "half-open"
                        if self.state == "half-open":
                            if ok:
                                self.state, self.calls, self.fails = "closed", 0, 0
                                return "trial ok -> closed"
                            self.state, self.opened_at = "open", now
                            return "trial failed -> open"
                        self.calls += 1
                        self.fails += not ok
                        if self.calls >= self.min_calls and self.fails / self.calls >= self.threshold:
                            self.state, self.opened_at = "open", now
                            return "failure -> OPEN"
                        return "ok" if ok else "failure"

                b = Breaker()
                timeline = [(0, True), (1, False), (2, False), (3, False), (4, True), (8, True), (15, False), (20, True), (31, True), (32, True)]
                for now, ok in timeline:
                    print(f"t={now:>2} dependency {'up  ' if ok else 'down'}: {b.call(now, ok):24} state={b.state}")
            """),
            ex("Fallback chain", "basic", "Fresh → cached → default, never an error page for an optional widget.", "python", """
                cache = {"recs:u42": ["book-1", "book-9"]}

                def live_recommendations(user):
                    raise TimeoutError("recs service timed out")

                def recommendations(user):
                    try:
                        return live_recommendations(user), "live"
                    except TimeoutError:
                        if f"recs:{user}" in cache:
                            return cache[f"recs:{user}"], "stale cache"
                        return ["bestseller-1", "bestseller-2"], "default"

                print(recommendations("u42"))
                print(recommendations("u7"))
            """),
            ex("Resilience4j configuration", "intermediate", "Typical breaker settings.", "yaml", """
                resilience4j.circuitbreaker:
                  instances:
                    recommendations:
                      slidingWindowType: COUNT_BASED
                      slidingWindowSize: 50
                      minimumNumberOfCalls: 20
                      failureRateThreshold: 50
                      slowCallDurationThreshold: 800ms
                      slowCallRateThreshold: 50
                      waitDurationInOpenState: 10s
                      permittedNumberOfCallsInHalfOpenState: 5
            """, runnable=False),
        ],
        ["Open when failure rate ≥ 50% over ≥ 20 calls", "Cool-down 10-30 s; half-open 3-5 trial calls", "Count slow calls (> p99 SLO) as failures", "Fallback: cache → default → queued", "Envoy outlier_detection: consecutive_5xx: 5"],
        ["A breaker without a fallback, which just turns slow errors into fast errors.", "One global breaker for many hosts, tripping on a single bad instance.", "Tripping on client errors (4xx) that say nothing about dependency health."],
        [
            qa("basic", "What problem does a circuit breaker solve?", "It stops sending requests to a dependency that is failing, so callers fail fast instead of waiting on timeouts and exhausting threads and connections, and the dependency gets room to recover. It prevents one failure from cascading through the system."),
            qa("intermediate", "Explain the three states of a circuit breaker.", "Closed: calls flow and failures are counted. Open: calls are rejected immediately for a cool-down. Half-open: a few trial calls go through; success closes the breaker, failure reopens it."),
            qa("intermediate", "What makes a good fallback?", "Something useful without the dependency: cached or stale data, a default or simplified result, hiding an optional feature, or accepting the request and processing it later. The fallback must be cheap and must not call the same failing dependency."),
            qa("advanced", "How do circuit breakers, retries and timeouts interact?", "Timeouts bound each attempt, retries recover transient failures, and the breaker stops retries from hammering a dependency that is clearly down. Order them so the breaker sees each attempt's outcome, retries respect the breaker (no retry when open), and total time stays within the caller's deadline."),
        ],
        ["retries-backoff", "bulkheads-timeouts", "microservices-gateway"],
        chain(
            ("Closed", "calls pass", "Normal", "Calls flow; the breaker counts failures over a rolling window."),
            ("Threshold", "60% failing", "Trip", "Failure rate crosses 50% over 20+ calls.", "errors"),
            ("Open", "fail fast 10 s", "Open", "Calls are rejected instantly and served a fallback.", "trip"),
            ("Half-open", "5 trial calls", "Probe", "After the cool-down a few trial calls test the dependency.", "trial"),
            ("Closed", "recovered", "Close", "Trials succeed, so normal traffic resumes.", "ok"),
        ),
    ),
    topic(
        "bulkheads-timeouts", "Timeouts, Deadlines, Bulkheads & Load Shedding", "reliability", "intermediate", "BH",
        "Bound every wait, isolate resources per dependency, and reject excess work early.",
        "Ships have watertight compartments so one breach floods a single section, not the whole hull. And a captain who waits forever for a reply from the shore never sails.",
        "Every network call needs a timeout; without one, a hung dependency holds threads, connections and memory until the caller collapses. Timeouts should be set from the dependency's latency distribution (somewhat above its p99) and fit within an end-to-end deadline that is propagated downstream (gRPC deadlines, a header with the remaining budget), so inner services stop working on requests the client already abandoned. Bulkheads isolate resources: separate thread pools, connection pools or concurrency limits per dependency or tenant, so a slow recommendations service can exhaust only its own 20 slots instead of all request threads. Load shedding rejects work early when the server is saturated (queue full, concurrency limit reached, CPU high), returning 429 or 503 quickly rather than letting latency grow for everyone; prioritize critical traffic (checkout over analytics). Bounded queues with short wait limits, adaptive concurrency limits (based on latency, like TCP congestion control) and admission control keep the system in its efficient operating region during overload.",
        ["Isolating optional dependencies from critical request paths.", "Protecting a multi-tenant API from one noisy tenant.", "Surviving traffic spikes by shedding low-priority work.", "Propagating gRPC deadlines across a call chain."],
        [
            "Every remote call has a timeout; every request has a deadline.",
            "Propagate the remaining deadline; drop work past it.",
            "Separate pools/limits per dependency (bulkheads).",
            "Bounded queues; reject fast instead of queueing forever.",
            "Shed by priority: protect checkout, drop prefetches.",
        ],
        [
            ex("Deadline propagation across a call chain", "intermediate", "Each hop gets only the remaining budget and skips work that cannot finish.", "python", """
                hops = [("gateway", 30), ("orders", 120), ("pricing", 400), ("tax", 200)]

                def call_chain(deadline_ms):
                    remaining = deadline_ms
                    for name, cost in hops:
                        if cost > remaining:
                            print(f"{name:8} needs {cost} ms, only {remaining} ms left -> DEADLINE_EXCEEDED, skip downstream")
                            return
                        remaining -= cost
                        print(f"{name:8} done in {cost} ms, {remaining} ms left")
                    print("response within deadline")

                call_chain(800)
                print("---")
                call_chain(500)
            """),
            ex("Bulkhead: per-dependency concurrency limits", "intermediate", "A hung dependency saturates only its own slots.", "python", """
                limits = {"recommendations": 4, "payments": 4}
                in_use = {k: 0 for k in limits}
                results = []
                hung = {"recommendations"}
                for i in range(12):
                    dep = "recommendations" if i % 2 else "payments"
                    if in_use[dep] >= limits[dep]:
                        results.append(f"{dep}: rejected (bulkhead full) -> fallback")
                        continue
                    in_use[dep] += 1
                    if dep not in hung:
                        in_use[dep] -= 1
                        results.append(f"{dep}: ok")
                    else:
                        results.append(f"{dep}: waiting (hung)")
                print(*results, sep="  |  ")
                print("in use:", in_use)
            """),
            ex("Load shedding by priority", "basic", "Under overload keep critical traffic.", "python", """
                capacity = 100
                incoming = {"checkout": 40, "browse": 70, "prefetch": 50}
                priority = ["checkout", "browse", "prefetch"]
                admitted, left = {}, capacity
                for cls in priority:
                    admitted[cls] = min(incoming[cls], left)
                    left -= admitted[cls]
                for cls in priority:
                    print(f"{cls:9} admitted {admitted[cls]:>3}/{incoming[cls]:<3} shed {incoming[cls] - admitted[cls]} (429)")
            """),
        ],
        ["Timeout ≈ dependency p99 × 1.5, within the deadline", "gRPC: deadline propagated via grpc-timeout", "Bulkhead: max 20 concurrent calls to recs", "Queue: bounded, max wait 50 ms, then 503", "Shed order: prefetch → analytics → browse → checkout"],
        ["Default timeouts of 'infinite' or 60 s in HTTP clients and DB drivers.", "Inner timeouts longer than outer ones, so work continues after the client gave up.", "Unbounded queues that convert overload into huge latency and memory blowups."],
        [
            qa("basic", "Why must every remote call have a timeout?", "Without one, a hung dependency holds the caller's threads, sockets and memory indefinitely; enough of them and the caller stops serving everyone. A timeout converts an unbounded wait into a bounded, handleable error."),
            qa("intermediate", "What is deadline propagation?", "The edge assigns a total deadline and each service passes the remaining time to its downstream calls, which use it as their timeout. Work stops as soon as the deadline passes instead of continuing for a client that has already given up."),
            qa("intermediate", "What is the bulkhead pattern?", "Partitioning resources such as thread pools, connection pools or concurrency limits per dependency, tenant or traffic class, so exhaustion in one partition cannot take down the others."),
            qa("advanced", "Why shed load instead of queueing it?", "Under overload, queues grow, every request waits longer, and by the time work is done many clients have timed out, so the server does useless work (congestion collapse). Rejecting excess quickly with 429/503 keeps latency low for admitted requests and gives clients a clear signal to back off."),
        ],
        ["circuit-breakers", "retries-backoff", "rate-limiting"],
        chain(
            ("Edge", "deadline 800 ms", "Set deadline", "The gateway sets an 800 ms end-to-end deadline."),
            ("Admission", "queue ≤ 50 ms", "Admit or shed", "If concurrency or queue limits are hit, return 503 immediately.", "request"),
            ("Bulkheads", "recs: 20 slots", "Isolate", "Each dependency has its own pool; a hung one fills only its slots.", "admitted"),
            ("Downstream", "remaining 300 ms", "Propagate", "Calls carry the remaining budget as their timeout.", "deadline"),
            ("Fallback", "partial page", "Degrade", "If an optional call times out, render without it.", "timeout"),
        ),
    ),
    topic(
        "observability", "Observability: Logs, Metrics & Traces", "reliability", "basic", "OV",
        "Know what your system is doing: the three signals, RED/USE, and distributed tracing.",
        "A car dashboard (metrics) tells you something is wrong, the trip recorder (traces) shows where the slowdown happened on the route, and the mechanic's notes (logs) explain exactly what broke.",
        "Observability is the ability to understand a system's internal state from its outputs. Metrics are cheap numeric time series (counters, gauges, histograms) aggregated over time, ideal for dashboards and alerts; use the RED method for services (rate, errors, duration) and USE for resources (utilization, saturation, errors). Logs are timestamped records of discrete events; structured JSON logs with consistent fields (service, level, trace_id, user-agnostic ids) make them searchable, and they must never contain secrets or raw personal data. Distributed traces follow a request across services as a tree of spans with timings, showing where latency and errors come from; context is propagated in headers (W3C traceparent), and sampling (head-based or tail-based to keep slow and error traces) controls cost. OpenTelemetry provides vendor-neutral SDKs and a collector for all three signals. Watch metric cardinality: labels like user_id or full URLs create millions of series. Alerts should fire on symptoms tied to SLOs (error budget burn), while dashboards and traces support diagnosis.",
        ["Diagnosing a latency regression after a deploy.", "Alerting on SLO burn rather than CPU.", "Finding which downstream call slows a request.", "Auditing and debugging with correlated logs."],
        [
            "Metrics for alerting, traces for where, logs for why.",
            "RED for request-driven services, USE for resources.",
            "Propagate trace context (traceparent) through every hop, including queues.",
            "Keep metric label cardinality bounded.",
            "Structured logs with trace_id; no secrets or raw PII.",
        ],
        [
            ex("Trace waterfall from spans", "intermediate", "Reconstruct the critical path from parent/child spans.", "python", """
                spans = [
                    {"id": "a", "parent": None, "name": "GET /checkout", "start": 0, "dur": 480},
                    {"id": "b", "parent": "a", "name": "auth.verify", "start": 5, "dur": 20},
                    {"id": "c", "parent": "a", "name": "cart.get", "start": 30, "dur": 60},
                    {"id": "d", "parent": "a", "name": "pricing.quote", "start": 95, "dur": 360},
                    {"id": "e", "parent": "d", "name": "db SELECT rates", "start": 100, "dur": 330},
                ]
                children = {}
                for s in spans:
                    children.setdefault(s["parent"], []).append(s)

                def show(parent=None, depth=0):
                    for s in children.get(parent, []):
                        bar = " " * (s["start"] // 20) + "#" * max(1, s["dur"] // 20)
                        print(f"{'  ' * depth + s['name']:<22}{s['dur']:>4} ms |{bar}")
                        show(s["id"], depth + 1)

                show()
                slowest = max((s for s in spans if s["id"] not in {c["parent"] for c in spans}), key=lambda s: s["dur"])
                print("slowest leaf:", slowest["name"])
            """),
            ex("RED metrics from request records", "basic", "Rate, errors and duration percentiles over one minute.", "python", """
                import random
                random.seed(3)
                reqs = [(random.random() < 0.02, random.lognormvariate(4, 0.5)) for _ in range(6000)]
                lat = sorted(d for _, d in reqs)
                p = lambda q: lat[int(q * len(lat))]
                print(f"rate {len(reqs) / 60:.0f} rps | errors {sum(e for e, _ in reqs) / len(reqs):.1%} | p50 {p(.5):.0f} ms p99 {p(.99):.0f} ms")
            """),
            ex("Structured log line and trace header", "basic", "What a good log event and propagated context look like.", "text", """
                traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01

                {"ts":"2026-10-17T17:20:01.123Z","level":"error","service":"pricing","trace_id":"4bf92f3577b34da6a3ce929d0e0e4736",
                 "span_id":"00f067aa0ba902b7","msg":"rates query timeout","db":"rates","timeout_ms":300,"attempt":2}
            """, runnable=False),
        ],
        ["RED: rate, errors, duration (per endpoint)", "USE: utilization, saturation, errors (per resource)", "W3C traceparent: 00-<trace>-<span>-<flags>", "histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))", "Tail sampling: keep errors + slow traces"],
        ["High-cardinality labels (user_id, request path with ids) exploding the metrics bill.", "Logging tokens, passwords or full request bodies.", "Losing trace context at async boundaries (queues, thread pools)."],
        [
            qa("basic", "What are the three pillars of observability?", "Metrics (aggregated numbers over time for dashboards and alerts), logs (detailed event records for investigation) and traces (end-to-end request paths across services showing where time and errors occur). They are most useful when correlated by trace id."),
            qa("intermediate", "What are the RED and USE methods?", "RED, for request-driven services, tracks request rate, error rate and duration distribution. USE, for resources like CPU, disks and pools, tracks utilization, saturation (queueing) and errors. Together they quickly locate whether a problem is in a service or a resource."),
            qa("intermediate", "How does distributed tracing work?", "The first service creates a trace id and root span; each outgoing call carries the context in headers (W3C traceparent) and the callee creates child spans. Spans are exported to a collector and assembled into a tree showing timing and errors per hop."),
            qa("advanced", "How do you control observability cost at scale?", "Bound metric cardinality, aggregate before export, sample traces (tail-based sampling keeps all errors and slow requests while dropping most fast successes), set log levels and retention per tier, and route data through an OpenTelemetry collector that filters and batches."),
        ],
        ["slos-error-budgets", "latency-throughput", "microservices-gateway"],
        chain(
            ("Request", "traceparent", "Start trace", "The gateway starts a trace and passes traceparent downstream."),
            ("Services", "spans + logs", "Instrument", "Each service records spans, RED metrics and structured logs with trace_id.", "context"),
            ("Collector", "OTel, sampling", "Collect", "An OpenTelemetry collector batches, filters and tail-samples.", "telemetry"),
            ("Backends", "TSDB, logs, traces", "Store", "Metrics go to a time-series DB, logs to a log store, traces to a trace store.", "export"),
            ("Alert → debug", "SLO burn page", "Use", "An SLO alert fires; the trace shows a slow DB span; its logs explain why.", "query"),
        ),
    ),
    topic(
        "multi-region-dr", "Multi-Region & Disaster Recovery", "reliability", "advanced", "MR",
        "RPO, RTO and the spectrum from backups to active-active across regions.",
        "Keeping a spare house key: under the doormat (backup), at a neighbour's (warm standby), or living in two houses at once (active-active). Each costs more and gets you back inside faster.",
        "Disaster recovery planning starts with two numbers: RPO (recovery point objective), how much data you can afford to lose, and RTO (recovery time objective), how long you can be down. Strategies range from backup and restore (hours of RTO, RPO = backup interval, cheapest), through pilot light (core data replicated, compute off) and warm standby (scaled-down copy running in another region), to active-active (all regions serve traffic, RTO of seconds to minutes). Asynchronous cross-region replication keeps write latency low but means RPO equals replication lag; synchronous cross-region writes give RPO near zero at the cost of every write paying inter-region latency (tens of ms). Active-active writes require conflict handling: partition users to a home region, use globally consistent databases (Spanner, CockroachDB), or CRDTs/last-writer-wins for tolerant data. Failover needs global traffic management (DNS, anycast, global load balancers), automation, and regular game days, because untested runbooks fail. Back up across accounts and regions, keep backups immutable against ransomware, and test restores, not just backups.",
        ["Surviving a full cloud region outage.", "Meeting regulatory RPO/RTO requirements.", "Serving global users with low latency (active-active).", "Recovering from accidental deletion or ransomware."],
        [
            "Define RPO and RTO per service; they drive cost.",
            "Async replication: RPO = lag. Sync: RPO ≈ 0, slower writes.",
            "Active-active needs a write-conflict strategy (home region, global DB, CRDTs).",
            "Automate failover; rehearse with game days.",
            "Immutable, cross-account backups; test restores regularly.",
        ],
        [
            ex("Compare DR strategies", "intermediate", "Rough RPO/RTO/cost trade-offs.", "python", """
                strategies = [
                    ("backup & restore", "24 h (nightly)", "4-24 h", 1.05),
                    ("pilot light", "minutes (async)", "30-60 min", 1.2),
                    ("warm standby", "seconds-minutes", "5-15 min", 1.5),
                    ("active-active", "~0-seconds", "< 1 min", 2.0),
                ]
                print(f"{'strategy':18}{'RPO':18}{'RTO':12}cost")
                for name, rpo, rto, cost in strategies:
                    print(f"{name:18}{rpo:18}{rto:12}{cost:.2f}x")
            """),
            ex("Data lost at failover with async replication", "advanced", "Writes in the replication-lag window are lost.", "python", """
                import random
                random.seed(17)
                write_rps = 2_000
                for lag_ms in (50, 500, 5_000):
                    lost = write_rps * lag_ms / 1000
                    print(f"replication lag {lag_ms:>5} ms -> ~{lost:,.0f} acknowledged writes lost on failover (RPO {lag_ms / 1000:g}s)")
                rtt = 70
                print(f"synchronous cross-region commit adds >= {rtt} ms to every write")
            """),
            ex("Home-region routing for active-active", "advanced", "Each user writes to one home region, avoiding conflicts.", "python", """
                import hashlib
                regions = ["ap-south-1", "eu-west-1", "us-east-1"]
                healthy = {"ap-south-1": True, "eu-west-1": False, "us-east-1": True}

                def home(user):
                    i = int.from_bytes(hashlib.sha256(user.encode()).digest()[:4], "big") % len(regions)
                    return regions[i]

                def route_write(user):
                    h = home(user)
                    if healthy[h]:
                        return h
                    fallback = next(r for r in regions if healthy[r])
                    return f"{fallback} (failover from {h}, after replication catch-up)"

                for u in ("asha", "liam", "mei", "omar"):
                    print(u, "->", route_write(u))
            """),
        ],
        ["RPO = max tolerable data loss · RTO = max tolerable downtime", "Async RPO ≈ replication lag; sync adds inter-region RTT per write", "Backups: 3-2-1, immutable, cross-account", "Failover via DNS/global LB health checks", "Game day quarterly; restore test monthly"],
        ["Replicating to a second region but keeping a single-region dependency (IAM, DNS, secrets, CI).", "Never testing failover, then discovering stale runbooks during an outage.", "Failing back too early and losing writes made in the secondary."],
        [
            qa("basic", "What are RPO and RTO?", "RPO is the maximum acceptable data loss measured in time (how old the last recoverable data may be); RTO is the maximum acceptable time to restore service. Lower values require more expensive architectures."),
            qa("intermediate", "Active-passive vs active-active?", "Active-passive serves from one region and keeps another ready (warm or cold); it is simpler but failover takes minutes and capacity sits idle. Active-active serves from all regions, giving low latency and fast failover, but requires handling cross-region write conflicts and consistency."),
            qa("advanced", "How do you handle writes in an active-active multi-region system?", "Options: assign each user or tenant a home region for writes (no conflicts, failover moves the home), use a globally consistent database with consensus across regions (higher write latency), or use conflict-tolerant data types (CRDTs, last-writer-wins) for data where merges are acceptable."),
            qa("advanced", "How would you test disaster recovery?", "Run scheduled game days that fail a region or dependency in production-like conditions, measure actual RPO and RTO against targets, automate failover and failback, and regularly restore backups into an isolated environment to verify integrity."),
        ],
        ["replication", "dns", "slos-error-budgets"],
        chain(
            ("Users", "global", "Normal traffic", "Global DNS or anycast routes users to the nearest healthy region."),
            ("Region A", "primary writes", "Primary", "Region A serves traffic and replicates data asynchronously.", "requests"),
            ("Region B", "warm standby", "Standby", "Region B runs a scaled-down copy with replicas lagging ~1 s.", "replication"),
            ("Outage", "A health fails", "Detect", "Health checks fail for region A; automation declares a disaster.", "failover"),
            ("Promote B", "RPO ≈ 1 s", "Recover", "B's database is promoted, capacity scales up, and DNS points users to B.", "DNS switch"),
        ),
    ),
    topic(
        "case-news-feed", "Case Study: News Feed", "case-studies", "advanced", "NF",
        "Fan-out on write vs read, the celebrity problem, and ranking a timeline fast.",
        "A postman who copies every letter into each subscriber's mailbox (fan-out on write) versus subscribers walking to every friend's house to read their latest letters (fan-out on read). For a celebrity with millions of followers, nobody wants to copy every letter.",
        "A news feed shows each user recent posts from accounts they follow, ranked. Requirements: low-latency feed reads (p99 < 200 ms), high read:write ratio (around 100:1), and eventual consistency is acceptable (a post can appear seconds later). Fan-out on write pushes each new post id into every follower's precomputed feed (a Redis list or wide-column row), making reads cheap but writes expensive for accounts with millions of followers. Fan-out on read assembles the feed at request time by querying followed accounts' recent posts, which is cheap on write but slow for users following many accounts. The standard answer is hybrid: fan-out on write for normal users, and for celebrities (above a follower threshold) merge their recent posts at read time. Feeds store only post ids (the hydration step fetches post bodies, authors and counts from caches), are capped (e.g. last 800 ids), and are rebuilt lazily for inactive users. Ranking scores candidates by recency, affinity and engagement, often with an ML model, and pagination uses cursors. Media goes to object storage behind a CDN.",
        ["Social network home timelines.", "Activity feeds in collaboration tools.", "Notification inboxes with similar fan-out trade-offs."],
        [
            "Fan-out on write: fast reads, write cost ∝ followers.",
            "Fan-out on read: cheap writes, slow reads for heavy followers.",
            "Hybrid: push for most, pull for celebrities at read time.",
            "Store ids in feeds; hydrate from caches.",
            "Skip fan-out for inactive users; rebuild on next visit.",
        ],
        [
            ex("Fan-out cost: push vs pull vs hybrid", "advanced", "Estimate daily feed writes and per-read fetches.", "python", """
                import random
                random.seed(10)
                users = 100_000
                followers = [int(random.paretovariate(1.2) * 20) for _ in range(users)]
                followers[:5] = [20_000_000, 8_000_000, 5_000_000, 1_000_000, 900_000]
                posts_per_user_day = 0.5
                CELEB = 100_000

                push_writes = sum(f * posts_per_user_day for f in followers)
                hybrid_writes = sum(f * posts_per_user_day for f in followers if f < CELEB)
                celebs = sum(f >= CELEB for f in followers)
                print(f"push all     : {push_writes:,.0f} feed inserts/day")
                print(f"hybrid       : {hybrid_writes:,.0f} feed inserts/day ({celebs} celebrities pulled at read time)")
                print(f"pull all     : 0 inserts, but each read queries ~{sum(followers) / users:.0f} followees' timelines")
            """),
            ex("Merge precomputed feed with celebrity posts", "intermediate", "Read-time merge by timestamp, then take the top page.", "python", """
                import heapq
                precomputed = [(1700000300, "p:friend-3"), (1700000200, "p:friend-1"), (1700000100, "p:friend-2")]
                celebrity_recent = {"@star": [(1700000250, "p:star-9"), (1700000050, "p:star-8")]}
                streams = [precomputed] + list(celebrity_recent.values())
                feed = heapq.merge(*streams, key=lambda x: -x[0])
                print([pid for _, pid in list(feed)[:4]])
            """),
        ],
        ["Read:write ≈ 100:1; feed read p99 < 200 ms", "Feed cache: LPUSH feed:{uid} post_id; LTRIM 0 799", "Celebrity threshold ~10^5-10^6 followers → pull", "Hydrate: post cache + user cache + counters", "Cursor pagination on (score, post_id)"],
        ["Pushing a celebrity post synchronously to 20M feeds.", "Storing full post bodies in every feed (massive duplication, edits hard).", "Fanning out to millions of inactive users who will never read it."],
        [
            qa("intermediate", "Fan-out on write vs fan-out on read?", "On write, each post is inserted into all followers' feeds, giving O(1) feed reads but write cost proportional to follower count. On read, the feed is built by querying followees at request time, making writes cheap but reads slow for users who follow many accounts."),
            qa("advanced", "How do you handle celebrities with millions of followers?", "Do not fan out their posts; mark them as pull accounts. At read time, merge the user's precomputed feed with recent posts from the few celebrities they follow (cached heavily), then rank. This bounds write amplification while keeping reads fast."),
            qa("advanced", "What data model would you use for feeds?", "A per-user list of post ids with scores in Redis or a wide-column store keyed by user id, capped to a few hundred entries. Posts live in a sharded posts store keyed by post id, with bodies and counters cached separately for hydration."),
            qa("intermediate", "How do you make the feed feel real-time?", "Fan-out workers consume a post-created stream asynchronously so new posts appear within seconds, and online users receive a push (SSE/WebSocket) hint to refresh. Exact global ordering is not required."),
        ],
        ["caching", "message-queues", "pagination"],
        chain(
            ("Post", "user writes", "Create post", "A user publishes a post; it is stored in the posts DB and media in object storage."),
            ("Stream", "PostCreated", "Publish", "A PostCreated event goes to a partitioned topic.", "event"),
            ("Fan-out", "followers < 100k", "Push", "Workers insert the post id into each active follower's feed list.", "ids"),
            ("Feed read", "merge celebrities", "Read", "On read, merge the precomputed list with cached celebrity posts.", "GET /feed"),
            ("Rank + hydrate", "top 20", "Rank and hydrate", "Score candidates, fetch bodies and counters from cache, return a page.", "candidates"),
        ),
    ),
    topic(
        "case-ride-sharing", "Case Study: Ride Sharing", "case-studies", "advanced", "RS",
        "Real-time driver locations, geospatial matching and trip state at city scale.",
        "A taxi dispatcher with a city map divided into squares: drivers radio their square every few seconds, and when a rider calls, the dispatcher looks in the rider's square and the ones around it.",
        "A ride-sharing system tracks millions of drivers sending GPS updates every few seconds, matches riders to nearby available drivers within seconds, and manages each trip through a reliable state machine. Location updates are a write-heavy, ephemeral stream: drivers send updates over persistent connections to location services that keep the latest position in memory (Redis GEO or in-process indexes), partitioned by geographic cell, not in a relational database. Spatial indexing maps coordinates to cells (geohash, Google S2 or Uber's H3 hexagons); a nearby search looks at the rider's cell and its neighbours, then ranks candidates by ETA from a routing service rather than straight-line distance. Matching must avoid double-assigning a driver: offer a ride to one driver at a time with a timeout, and claim the driver atomically (conditional update or per-driver lock). Trips are a durable state machine (requested → accepted → arrived → in progress → completed) stored in a transactional database, with payments processed asynchronously and idempotently at the end. Surge pricing is computed per cell from supply and demand over short windows.",
        ["Ride hailing and food delivery dispatch.", "Fleet tracking and logistics.", "Any 'find nearby X' feature."],
        [
            "Latest locations in memory, sharded by geo cell; history to a stream/lake.",
            "Cells (geohash/S2/H3) + neighbour cells for nearby search.",
            "Rank by ETA from a routing engine, not straight-line distance.",
            "Claim a driver atomically to avoid double dispatch.",
            "Trip lifecycle in a durable, transactional state machine.",
        ],
        [
            ex("Grid index for nearby drivers", "advanced", "Bucket drivers into cells, search the rider's cell and neighbours, rank by haversine distance.", "python", """
                import math, random
                from collections import defaultdict
                random.seed(12)
                CELL = 0.01

                def cell(lat, lon):
                    return (math.floor(lat / CELL), math.floor(lon / CELL))

                def haversine_km(a, b):
                    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
                    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
                    return 2 * 6371 * math.asin(math.sqrt(h))

                grid = defaultdict(list)
                for i in range(5000):
                    pos = (12.90 + random.random() * 0.2, 77.50 + random.random() * 0.2)
                    grid[cell(*pos)].append((f"driver-{i}", pos))

                rider = (12.9716, 77.5946)
                cx, cy = cell(*rider)
                candidates = [d for dx in (-1, 0, 1) for dy in (-1, 0, 1) for d in grid[(cx + dx, cy + dy)]]
                best = sorted(candidates, key=lambda d: haversine_km(rider, d[1]))[:3]
                print(f"checked {len(candidates)} of 5000 drivers in 9 cells")
                for name, pos in best:
                    print(name, f"{haversine_km(rider, pos):.2f} km")
            """),
            ex("Atomic driver claim prevents double dispatch", "intermediate", "Two matchers race for the same driver; a conditional update lets one win.", "python", """
                drivers = {"driver-7": {"status": "available", "version": 3}}

                def claim(driver, trip, expected_version):
                    d = drivers[driver]
                    if d["status"] != "available" or d["version"] != expected_version:
                        return f"{trip}: lost race, pick next driver"
                    d.update(status=f"assigned:{trip}", version=d["version"] + 1)
                    return f"{trip}: assigned {driver}"

                print(claim("driver-7", "trip-A", 3))
                print(claim("driver-7", "trip-B", 3))
                print(drivers)
            """),
            ex("Location ingestion estimate", "basic", "Write load from GPS pings.", "python", """
                active_drivers = 1_500_000
                ping_every_s = 4
                bytes_per_ping = 100
                rps = active_drivers / ping_every_s
                print(f"{rps:,.0f} location writes/s, {rps * bytes_per_ping * 8 / 1e6:,.0f} Mbit/s ingress")
                print("keep only the latest position in memory; stream history to the lake")
            """),
        ],
        ["GPS ping every 4 s → ~375k writes/s for 1.5M drivers", "Redis: GEOADD drivers:cell lon lat id · GEOSEARCH … BYRADIUS 2 km", "Index: geohash / S2 / H3 cells + neighbours", "Claim: UPDATE drivers SET status='assigned' WHERE id=? AND status='available'", "Trip states: requested → accepted → arrived → started → completed"],
        ["Storing every GPS ping in the transactional database.", "Matching by straight-line distance across rivers and highways.", "Offering the same driver to two riders at once."],
        [
            qa("intermediate", "How do you store and query driver locations?", "Keep only the latest location per driver in memory (Redis GEO or a custom index) sharded by geographic cell, updated over persistent connections. A nearby query scans the rider's cell and its neighbours, then filters available drivers and ranks by ETA."),
            qa("advanced", "Why use geohash, S2 or H3?", "They map 2D coordinates to cell ids so nearby points share prefixes or neighbouring ids, turning spatial search into key lookups and making sharding by region natural. H3 hexagons have uniform neighbour distances, which helps surge pricing and supply heat maps."),
            qa("advanced", "How do you prevent two riders getting the same driver?", "Offer the trip to one driver at a time with a short acceptance timeout, and claim the driver with an atomic conditional update or compare-and-set on the driver's state and version. The loser of a race moves to the next candidate."),
            qa("intermediate", "How do you handle hot areas like airports or stadiums?", "Use smaller cells or split hot cells across shards, cache supply snapshots, queue riders fairly (FIFO airport queues), and compute surge pricing per cell from short-window supply and demand to rebalance drivers."),
        ],
        ["realtime-delivery", "sharding", "distributed-locks"],
        chain(
            ("Driver app", "GPS every 4 s", "Ping", "Drivers stream locations over a persistent connection."),
            ("Location svc", "cell 7f3a…", "Index", "The latest position is stored in memory under its geo cell.", "lat/lon"),
            ("Rider", "request ride", "Request", "A rider requests a ride; matching looks up the rider's cell and neighbours.", "request"),
            ("Matcher", "rank by ETA", "Match", "Candidates are ranked by routing ETA; the best is claimed atomically.", "candidates"),
            ("Trip svc", "state machine", "Trip lifecycle", "The trip moves requested → accepted → started → completed; payment runs once at the end.", "assigned"),
        ),
    ),
    topic(
        "case-kv-store", "Case Study: Distributed Key-Value Store", "case-studies", "advanced", "KV",
        "Design a Dynamo-style store: partitioning, replication, quorums and an LSM storage engine.",
        "A chain of storage lockers in a ring of buildings: your key decides which building holds the locker, two neighbours keep copies, and you only need most of them to answer to trust the result.",
        "A distributed key-value store (Dynamo, Cassandra, Riak) offers get(key) and put(key, value) with high availability and horizontal scale. Keys are partitioned with consistent hashing and virtual nodes, and each key is replicated to the next N distinct nodes on the ring (its preference list), ideally in different availability zones. Any node can coordinate a request; it sends writes to all N replicas and waits for W acks, and reads ask R replicas, where W + R > N gives read-your-latest-write overlap and lower values favour latency and availability. Concurrent writes are detected with vector clocks or resolved with last-writer-wins timestamps. When a replica is down, a neighbour accepts the write with a hint (sloppy quorum, hinted handoff) and forwards it later; read repair and Merkle-tree anti-entropy fix remaining divergence. Membership and failure detection use gossip. On each node an LSM tree provides fast writes: append to a commit log, insert into a memtable, flush to immutable sorted SSTables, use Bloom filters to skip files on reads, and compact in the background with tombstones for deletes.",
        ["Session and shopping-cart storage.", "User profiles and preferences at massive scale.", "Metadata stores for larger systems.", "Time series and event storage (wide-column variants)."],
        [
            "Consistent hashing + vnodes; replicate to N distinct nodes/zones.",
            "Tunable consistency: W + R > N for overlap; W=1/R=1 for latency.",
            "Sloppy quorum + hinted handoff keep writes available during failures.",
            "Read repair and Merkle-tree anti-entropy converge replicas.",
            "LSM engine: commit log → memtable → SSTables + Bloom filters + compaction.",
        ],
        [
            ex("Ring placement with replication factor 3", "advanced", "Find each key's preference list on a SHA-256 hash ring with virtual nodes.", "python", """
                import bisect, hashlib
                h = lambda s: int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")
                nodes = ["A", "B", "C", "D", "E"]
                ring = sorted((h(f"{n}#{v}"), n) for n in nodes for v in range(50))
                points = [p for p, _ in ring]

                def preference_list(key, n=3):
                    i = bisect.bisect(points, h(key)) % len(ring)
                    out = []
                    while len(out) < n:
                        node = ring[i % len(ring)][1]
                        if node not in out:
                            out.append(node)
                        i += 1
                    return out

                for key in ("user:42", "cart:7", "session:abc"):
                    print(key, "->", preference_list(key))
            """),
            ex("Quorum write with hinted handoff", "advanced", "One replica is down; a fallback node holds a hint and replays it.", "python", """
                N, W = 3, 2
                replicas = {"A": {}, "B": {}, "C": {}}
                up = {"A": True, "B": False, "C": True}
                hints = []

                def put(key, value, version):
                    acks = 0
                    for node in replicas:
                        if up[node]:
                            replicas[node][key] = (version, value)
                            acks += 1
                        else:
                            hints.append((node, key, (version, value)))
                            acks += 1
                    return "OK" if acks >= W else "FAIL"

                print("put:", put("cart:7", ["book"], 1), "| hints held by D:", hints)
                up["B"] = True
                for node, key, val in hints:
                    replicas[node][key] = val
                hints.clear()
                print("after handoff:", {n: r.get("cart:7") for n, r in replicas.items()})
            """),
            ex("LSM write and read path", "intermediate", "Memtable flushes to sorted SSTables; reads check newest first.", "python", """
                memtable, sstables, LIMIT = {}, [], 3

                def put(k, v):
                    memtable[k] = v
                    if len(memtable) >= LIMIT:
                        sstables.insert(0, dict(sorted(memtable.items())))
                        memtable.clear()

                def get(k):
                    if k in memtable:
                        return memtable[k], "memtable"
                    for i, t in enumerate(sstables):
                        if k in t:
                            return t[k], f"sstable {i}"
                    return None, "miss"

                for i, k in enumerate(["a", "b", "c", "a", "d", "e", "f"]):
                    put(k, i)
                print("sstables:", sstables, "memtable:", memtable)
                for k in ("a", "f", "z"):
                    print(k, get(k))
                merged = {}
                for t in reversed(sstables):
                    merged.update(t)
                print("after compaction:", dict(sorted(merged.items())))
            """),
        ],
        ["N=3, W=2, R=2 (strong-ish) · W=1, R=1 (fast, eventual)", "Preference list: next N distinct nodes clockwise", "Hinted handoff + read repair + Merkle anti-entropy", "LSM: commit log → memtable → SSTable, Bloom filter per SSTable", "Deletes = tombstones, purged after gc_grace"],
        ["Replicas on the same rack or zone, so one failure loses all copies.", "Last-writer-wins with skewed clocks silently dropping writes.", "Purging tombstones before all replicas saw them, resurrecting deleted data."],
        [
            qa("intermediate", "How does the store decide which nodes hold a key?", "It hashes the key onto a consistent-hash ring with virtual nodes and walks clockwise to pick the first N distinct physical nodes (skipping same-zone duplicates). Adding a node moves only the ranges it takes over."),
            qa("advanced", "What do N, W and R mean and how do you choose them?", "N is the replication factor, W the acks required for a write, R the replicas consulted on a read. W + R > N guarantees read and write sets overlap so reads see the latest acknowledged write (barring sloppy quorums); lower W or R improves latency and availability at the cost of staleness."),
            qa("advanced", "How do replicas converge after failures?", "Hinted handoff replays writes that a fallback node stored for a down replica, read repair fixes stale replicas noticed during reads, and periodic anti-entropy compares Merkle trees of key ranges to sync only differing ranges."),
            qa("advanced", "Why use an LSM tree for the storage engine?", "Writes become sequential appends to a commit log plus an in-memory insert, giving very high write throughput. Reads check the memtable and SSTables newest-first, with Bloom filters and indexes to limit disk reads, while compaction merges files and drops overwritten data and expired tombstones."),
            qa("intermediate", "How do you handle conflicting concurrent writes?", "Either last-writer-wins using timestamps (simple but can drop data under clock skew) or version vectors that detect concurrency and keep siblings for the client or a CRDT merge to resolve, as Dynamo did for shopping carts."),
        ],
        ["consistent-hashing", "replication", "bloom-filters"],
        chain(
            ("Client", "put cart:7", "Request", "The client sends a put to any node, which becomes the coordinator."),
            ("Coordinator", "ring lookup", "Locate replicas", "Hash the key; the preference list is A, B, C.", "put"),
            ("Replicas", "W = 2 of 3", "Quorum write", "Send to all three; reply OK after two acks.", "write"),
            ("Hinted handoff", "B down → D", "Handle failure", "D stores a hint for B and replays it when B returns.", "hint"),
            ("LSM engine", "log → memtable", "Persist", "Each replica appends to its commit log and memtable, later flushing to SSTables.", "append"),
        ),
    ),
]

TOPICS += [
    topic(
        "three-tier-architecture", "3-Tier Architecture: Web, Application & Data", "reliability", "basic", "3T", "3-tier architecture separates presentation, application logic and data storage into distinct layers. A typical request travels from a browser through a web or edge tier, into stateless application servers, and finally to a private database tier. Each boundary has its own scaling, availability and security choices.",
        "A restaurant separates the dining room (presentation), kitchen (application rules) and pantry (data). Guests do not walk into the pantry, and the kitchen can add cooks without rebuilding the dining room.",
        "The web tier terminates TLS and serves static content or forwards API requests; the application tier validates identity and business rules; the data tier persists state. Keep the database private, allow only required ports from the app tier, and make stateless app instances horizontally scalable. Add a load balancer, health checks, autoscaling, database backups and observability as requirements grow. The pattern is not automatically three physical servers: tiers are logical responsibilities and may run as processes, containers, managed services or separate subnets.",
        ["Designing a classic web application on premises or in a cloud VPC.", "Explaining the request path, trust boundaries and scaling levers in an interview.", "Finding why a web request can reach the app but fail at the database."],
        ["Web/presentation tier accepts user traffic and forwards requests.", "Application tier owns domain logic and should not expose its database directly.", "Data tier stays private and accepts connections only from the app tier.", "Scale and deploy tiers independently; instrument each hop.", "Three tiers are logical boundaries, not a requirement for three machines."],
        [
            ex("A private three-tier network", "basic", "Only the edge accepts public traffic; app and data tiers remain private.", "text", "Browser → HTTPS load balancer (public) → app service (private) → database (private)", runnable=False),
            ex("Capacity estimate", "intermediate", "If 4 app instances each handle 250 requests/s, the tier's rough steady capacity is 1,000 requests/s before headroom.", "python", "instances = 4\ncapacity_per_instance = 250\nheadroom = 0.70\nprint(instances * capacity_per_instance * headroom, \"safe RPS\")"),
        ],
        ["Edge → app → data is the request path.", "Public ingress should terminate at a controlled edge or load balancer.", "The app-to-database rule should name the app security group, not the whole VPC.", "Scale each tier using its own bottleneck and SLO.", "Model the failure path: retries, timeouts, health checks and database failover."],
        ["A web server can reach the API but the API times out to its database: trace the app subnet route, egress, DB ingress and listener separately.", "A single app instance is saturated while the database is idle: add stateless app replicas behind a load balancer, then measure again."],
        [
            qa("basic", "What are the three tiers?", "Presentation/web accepts and renders requests; application owns business logic; data stores durable state. They are logical responsibilities and need not map one-to-one to three physical servers."),
            qa("intermediate", "Why should the database tier be private?", "It reduces direct exposure. Only the application identity and network path that need database access should reach it, while user traffic terminates at the web or edge tier."),
            qa("advanced", "How would you scale a 3-tier application under read-heavy traffic?", "Measure each tier. Add edge caching for static/read-mostly data, scale stateless app instances behind a load balancer, and use a database cache/read replicas only if database reads remain the bottleneck. Preserve consistency requirements and headroom."),
        ],
        ["scalability", "vpc-design", "caching", "load-balancers"],
        chain(("Web tier", "edge + TLS", "Accept the request", "Authenticate the transport and route only supported requests."),
              ("Application tier", "business rules", "Process safely", "Validate input, authorize the caller and apply domain logic."),
              ("Data tier", "private + durable", "Read or write state", "Persist state behind a narrow, monitored app-to-data path.")),
    ),
]

from ._catalog import build_lessons

TOPICS += build_lessons([
    ("observability-toolchain", "Observability Toolchain: Prometheus, Grafana, ELK & Jaeger", "reliability", "intermediate", "An observability stack collects metrics, logs and traces from instrumented services. Prometheus scrapes and stores time-series metrics; Grafana visualizes and alerts; Elasticsearch, Logstash and Kibana (ELK) ingest, transform, search and display logs; Jaeger explores distributed traces. OpenTelemetry provides vendor-neutral instrumentation and collection across tools.", "Service SDKs → OpenTelemetry Collector → Prometheus/Grafana (metrics) · Logstash/Elasticsearch/Kibana (logs) · Jaeger (traces)", "Correlate signals with trace IDs and deployment versions. Keep metric labels bounded, redact sensitive log fields and set retention/cost limits for each store.", "A request is slow but CPU and error metrics are normal. Which signal helps next?", "Use a distributed trace to identify which dependency span consumes the time, then correlate its trace ID with structured logs and the deployment version. Metrics show aggregate symptoms; traces localize a request path.", ["observability", "slo-error-budgets", "tracing"]),
    ("chaos-engineering-game-days", "Chaos Engineering & Game Days", "reliability", "advanced", "Chaos engineering tests a steady-state hypothesis by injecting a controlled failure such as latency, packet loss, pod termination or dependency errors. Start with a small blast radius, staffed owners, measurable abort conditions and a recovery plan; feed findings into reliability work.", "Hypothesis: checkout success stays ≥ 99.5% during one worker failure; abort if error budget burns too quickly", "Run experiments only when observability can show the result and the rollback is understood; random failure without a hypothesis is not a useful experiment.", "What must be defined before injecting a production failure?", "A measurable steady-state hypothesis, approved target and blast radius, staffed owner, abort thresholds tied to customer impact, recovery procedure and clear communication plan.", ["observability", "multi-region-dr", "retries-backoff"]),
], "SD", "Reliable systems connect architecture choices to measurable service behavior.")

TOPICS += [
    topic(
        "browser-url-request-lifecycle", "What Happens When You Type a URL in a Browser?", "edge-api", "basic", "URL",
        "Follow a navigation from the address bar through browser policy, DNS, network layers, TLS, HTTP, server processing and pixels on screen.",
        "A browser navigation is like sending a carefully addressed package: the browser interprets the address, discovers a route, establishes a protected conversation, asks for a resource, and then turns the response into a page.",
        "The browser first distinguishes a search query from a URL, parses scheme, host, port, path, query and fragment, and resolves relative URLs against the current document. The fragment (after #) stays client-side and is not included in the HTTP request. Browser policy may upgrade a site to HTTPS through HSTS, consult a service worker, reuse memory/disk caches, or block the navigation under extensions or enterprise policy. For an uncached hostname, the OS stub resolver asks a recursive DNS resolver; that resolver can answer from cache or query root, TLD and authoritative name servers for A/AAAA (or follow a CNAME). DNS normally uses UDP, with TCP fallback for large replies; DoT/DoH encrypt the resolver hop. The resulting IP is routed across networks: link layer (Wi-Fi/Ethernet frames and next-hop MAC), internet layer (IP addressing and router forwarding), and transport layer (TCP or QUIC ports, reliability and congestion control). These are the TCP/IP layers; they map approximately onto the seven-layer OSI model, whose physical, data-link, network, transport, session, presentation and application layers are a teaching model rather than seven separate boxes in every modern stack. HTTPS adds TLS: TCP-based HTTP/1.1 or HTTP/2 typically performs a TCP handshake then TLS 1.3 negotiation, certificate and hostname validation, key agreement and encrypted records; HTTP/3 uses QUIC over UDP and integrates TLS 1.3 into its transport handshake. The browser sends an HTTP request with method, path, Host/:authority, cookies, accept and cache validators. CDNs, WAFs, reverse proxies and load balancers may route or answer it before an application server runs authentication, business logic and data calls. The response returns with a status, headers, cookies, cache policy, content encoding and body. The browser streams and decompresses bytes, parses HTML into the DOM, discovers CSS/JS/images, builds CSSOM and render tree, runs scripts, computes layout, paints and composites layers to the screen. Same-origin policy, CORS, CSP, cookie SameSite/Secure rules and mixed-content checks constrain what scripts and subresources can do. A warm navigation can skip DNS, connection setup, TLS negotiation or even the origin request by reusing caches, service worker responses, persistent connections and HTTP cache validators.",
        ["Debugging a page that loads slowly or fails only on one network.", "Understanding where CDN, TLS termination, load balancing and application work sit in a request path.", "Explaining DNS, TCP/IP and HTTP clearly in a system design interview."],
        [
            "URL: scheme + authority (host/port) + path + query; the fragment is not sent to the server.",
            "Browser fast paths: HSTS upgrade, service worker, memory/disk cache, connection reuse, DNS cache and preconnect.",
            "DNS resolves names to addresses; resolvers cache answers by TTL. DNSSEC authenticates data; DoH/DoT encrypt the client-to-resolver link.",
            "TCP/IP layers: link → internet/IP → transport (TCP/UDP/QUIC) → application (DNS, TLS, HTTP). OSI is a seven-layer conceptual mapping.",
            "HTTPS: TCP + TLS for HTTP/1.1 and HTTP/2; QUIC over UDP with integrated TLS 1.3 for HTTP/3.",
            "TLS authenticates the server certificate and derives encryption keys; it does not hide the destination IP and may expose the hostname depending on ECH support.",
            "Edge path: anycast/CDN → WAF/reverse proxy → load balancer → application → cache/database/dependencies.",
            "HTTP cache: Cache-Control, freshness, ETag/If-None-Match and Last-Modified/If-Modified-Since can avoid transferring unchanged bodies.",
            "Rendering path: bytes → DOM/CSSOM → style/layout → paint → compositing; scripts can pause parsing and trigger more requests.",
            "Diagnose each phase separately: DNS, connect, TLS, TTFB, download, parsing, script execution and rendering."
        ],
        [
            ex("Inspect a navigation request", "basic", "Show redirects, request headers, response headers and timing from curl.", "bash", "curl -v -L --trace-time https://example.com/", runnable=False),
            ex("Inspect DNS answers", "basic", "Compare address records and TTLs returned by a recursive resolver.", "bash", "dig example.com A +noall +answer\ndig example.com AAAA +noall +answer", runnable=False),
            ex("Inspect the TLS certificate and negotiated protocol", "intermediate", "Check hostname validation details, certificate chain and ALPN protocol.", "bash", "openssl s_client -connect example.com:443 -servername example.com -alpn h2 -showcerts", runnable=False),
        ],
        [
            "URL parse / browser policy → cache and service worker → DNS → route and connection → TLS → HTTP request → edge and origin → response → render.",
            "Use DevTools Network timing to separate queueing/stalled, DNS, connect, SSL, request wait (TTFB), content download and main-thread work.",
            "A 304 Not Modified response saves the body but still requires a request; a fresh cache hit can avoid the network entirely.",
            "HTTP/2 multiplexes streams on one TCP connection but TCP packet loss can block all streams; HTTP/3 uses QUIC streams to reduce cross-stream head-of-line blocking.",
            "Routers forward IP packets hop by hop; BGP selects inter-network paths, while DNS/CDN decisions can steer the initial destination.",
        ],
        [
            "Do not say DNS runs on top of HTTP for ordinary lookups; classic DNS uses port 53 over UDP/TCP, while DoH is DNS carried over HTTPS.",
            "TLS encrypts application data in transit but does not itself make a site trustworthy or prevent vulnerable server-side code.",
            "The OSI model is useful vocabulary; real networking stacks combine responsibilities and do not add seven serial handshakes.",
            "A page can be network-complete yet still appear slow because JavaScript, style recalculation, layout or main-thread tasks block rendering.",
            "A cache hit can be stale or vary by cookies, authorization, Vary headers and cache key; inspect the effective policy before assuming it is safe.",
        ],
        [
            qa("basic", "What happens after the browser resolves the hostname?", "It selects or opens a connection to the destination IP. For TCP-based HTTPS it establishes TCP, negotiates TLS and validates the certificate; for HTTP/3 it establishes QUIC with TLS integrated. It then sends an HTTP request, potentially through a CDN, proxy and load balancer, and processes the response into DOM/CSSOM, layout, paint and composited pixels."),
            qa("basic", "Which network layers are involved when loading an HTTPS page?", "At the application layer the browser uses HTTP and DNS; TLS provides presentation/session-like encryption and identity; TCP or QUIC provides transport; IP handles addressing and routing; Ethernet or Wi-Fi carries frames over each local link. The OSI seven-layer model names physical, data link, network, transport, session, presentation and application, but TCP/IP implementations combine several of these responsibilities."),
            qa("intermediate", "How does HTTP/3 differ from HTTP/2?", "HTTP/2 typically multiplexes streams over one TCP connection, so packet loss can stall delivery across streams while TCP recovers. HTTP/3 maps HTTP onto independent QUIC streams over UDP, uses integrated TLS 1.3 and can avoid cross-stream transport head-of-line blocking. Both still need congestion control, flow control, certificates and application-level request handling."),
            qa("intermediate", "Why might a warm page navigation be much faster than the first one?", "The browser may reuse DNS answers, a TCP/TLS or QUIC connection, parsed resources, memory/disk cache entries, service worker responses and preconnected sockets. The origin may also return a small 304 response after ETag validation, or a CDN may serve the resource without contacting the origin."),
            qa("advanced", "How would you determine whether a slow page is a network or rendering problem?", "Use browser performance and network traces. Compare DNS/connect/TLS, TTFB and download time with resource waterfalls, then inspect main-thread scripting, style/layout, long tasks, paint and compositing. A fast TTFB with a delayed Largest Contentful Paint points toward render-blocking resources or client work; a long TTFB points toward edge/origin queueing or backend dependencies."),
        ],
        ["dns", "cdn", "caching", "auth-tokens", "load-balancing"],
        chain(
            ("Address bar", "URL parse + policy", "Interpret the URL", "Resolve a search string or URL; apply HSTS, service worker and browser cache rules."),
            ("DNS", "name → IP", "Find the destination", "Use cached answers or ask a recursive resolver, which follows DNS delegation as needed."),
            ("Network", "link → IP → transport", "Reach the server", "Frames cross local links; routers forward IP packets; TCP or QUIC manages transport."),
            ("TLS", "certificate + keys", "Protect the connection", "Validate the server identity and derive keys; HTTP/3 negotiates TLS as part of QUIC."),
            ("HTTP request", "method + path + headers", "Ask for a resource", "Send cookies, cache validators and accepted formats over a persistent connection."),
            ("Edge and origin", "CDN → proxy → app", "Route and process", "Edge services may answer, filter or forward; application code can read caches and databases."),
            ("HTTP response", "status + headers + body", "Return bytes", "Caches, compression, content type and security headers shape what the browser receives."),
            ("Browser rendering", "DOM → layout → paint", "Show pixels", "Parse HTML and CSS, run scripts, fetch dependencies, lay out boxes, paint and composite layers."),
        ),
    ),
]

SCENARIOS = [
    {"level": "advanced", "topic": "retries-backoff", "q": "A 30-second database blip turned into a 20-minute outage: every service kept retrying and the database never recovered.", "a": "Retry amplification and synchronized retries. Retry at one layer only, use exponential backoff with full jitter and a retry budget, add circuit breakers so callers fail fast to fallbacks, and shed load at the edge until the database recovers."},
    {"level": "advanced", "topic": "outbox-pattern", "q": "Some orders exist in the database but downstream services never received the OrderPlaced event.", "a": "Dual-write problem: the service committed and then crashed (or the broker call failed) before publishing. Write the event to an outbox table in the same transaction and publish it with a relay or CDC, with consumers deduping by event id."},
    {"level": "intermediate", "topic": "pagination", "q": "Users report seeing the same post twice while scrolling, and page 500 of the admin list takes 8 seconds.", "a": "Offset pagination shifts when new rows arrive and scans all skipped rows. Switch to keyset pagination on (created_at, id) with a matching index and an opaque cursor; cap page size and avoid COUNT(*) on every request."},
    {"level": "advanced", "topic": "distributed-locks", "q": "A nightly job occasionally runs twice and double-bills a few customers, even though it takes a Redis lock.", "a": "The lock's TTL expired during a long pause, so a second instance acquired it. Make billing idempotent (unique constraint per customer and period), use a consensus-backed lock with fencing tokens checked by the billing store, and keep the critical section well inside the TTL."},
    {"level": "advanced", "topic": "multi-region-dr", "q": "During a region failover, the standby came up but logins failed for everyone.", "a": "A hidden single-region dependency (identity provider, secrets store, DNS zone or config service) was not replicated. Inventory every dependency on the critical path, make each multi-region or regionally independent, and prove it with regular game days."},
    {"level": "intermediate", "topic": "case-news-feed", "q": "When a celebrity posts, the fan-out queue backs up for an hour and everyone's feed goes stale.", "a": "Fan-out on write for a 20M-follower account floods the workers. Use a hybrid model: skip fan-out for accounts above a follower threshold and merge their recent posts at read time, and skip inactive followers entirely."},
]
