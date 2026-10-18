export const WORDS = [
  { answer: "UPSTREAM", term: "upstream", clue: "Named group of application servers used by proxy_pass" },
  { answer: "LOCATION", term: "location", clue: "Selects how a request URI is handled" },
  { answer: "WORKER", term: "worker", clue: "Event-driven process that handles client connections" },
  { answer: "RELOAD", term: "reload", clue: "Gracefully applies validated configuration changes" },
  { answer: "TLS", term: "TLS", clue: "Protects HTTP traffic with encryption and identity checks" },
  { answer: "PROXY", term: "reverse proxy", clue: "Receives a request and forwards it to an application" },
  { answer: "TIMEOUT", term: "timeout", clue: "Limit on waiting for a connection or upstream response" },
  { answer: "BUFFERING", term: "buffering", clue: "Temporarily stores upstream data while relaying a response" },
  { answer: "SERVER", term: "server block", clue: "Configuration for a host and listener combination" },
  { answer: "ACCESSLOG", term: "access log", clue: "Record of completed client requests" },
];
export const RUSH = [
  { task: "Validate NGINX configuration", answer: "nginx -t", wrong: ["nginx --check", "nginx -v -t", "nginx validate"] },
  { task: "Apply a valid config without stopping active requests", answer: "nginx -s reload", wrong: ["kill -9 nginx", "nginx -s stop", "rm nginx.pid"] },
  { task: "Select a named upstream from a location", answer: "proxy_pass http://app_pool;", wrong: ["upstream app_pool;", "route app_pool;", "server app_pool;"] },
];
export const BUGS = [];
export const META = { rushLabel: "NGINX Rush", rushIntro: "Choose the right request handling action.", rushMono: true, bugLabel: "NGINX Config Hunt", bugNoun: "finding" };
