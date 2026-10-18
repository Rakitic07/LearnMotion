export const WORDS = [
  { answer: "CIDR", term: "CIDR", clue: "Slash notation for a network prefix" },
  { answer: "PREFIX", term: "Prefix", clue: "The network-bit count after a slash" },
  { answer: "SUBNET", term: "Subnet", clue: "A smaller logical IP network" },
  { answer: "ROUTER", term: "Router", clue: "Forwards packets between networks" },
  { answer: "GATEWAY", term: "Gateway", clue: "Next hop toward another network" },
  { answer: "DNS", term: "DNS", clue: "Maps names to records and addresses" },
  { answer: "TCP", term: "TCP", clue: "Reliable ordered byte-stream transport" },
  { answer: "UDP", term: "UDP", clue: "Datagram transport without delivery guarantees" },
  { answer: "NAT", term: "NAT", clue: "Rewrites network addresses at a boundary" },
  { answer: "MTU", term: "MTU", clue: "Largest packet size a link can carry" },
  { answer: "IPV6", term: "IPv6", clue: "128-bit Internet Protocol addressing" },
  { answer: "FIREWALL", term: "Firewall", clue: "Filters traffic by protocol, address and port" },
];
export const RUSH = [
  { task: "IPv4 addresses in a /24", answer: "256", wrong: ["24", "254", "32"] },
  { task: "IPv4 bits in a /32 host route", answer: "32 network bits", wrong: ["32 host bits", "32 addresses", "24 network bits"] },
  { task: "IPv6 address width", answer: "128 bits", wrong: ["64 bits", "32 bits", "256 bits"] },
  { task: "IPv6 addresses in a /64", answer: "2^64", wrong: ["64", "2^32", "256"] },
];
export const BUGS = [];
export const META = { rushLabel: "Networking Rush", rushIntro: "Answer the address and protocol question.", rushMono: true, bugLabel: "Packet Hunt", bugNoun: "finding" };
