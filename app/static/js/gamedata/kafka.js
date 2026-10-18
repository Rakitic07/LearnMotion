export const WORDS = [
  { answer: "PARTITION", term: "Partition", clue: "Ordered and replicated unit of a Kafka topic" },
  { answer: "OFFSET", term: "Offset", clue: "Position of a record within one partition" },
  { answer: "BROKER", term: "Broker", clue: "Kafka server that stores partition replicas" },
  { answer: "PRODUCER", term: "Producer", clue: "Client that publishes records to topics" },
  { answer: "CONSUMER", term: "Consumer", clue: "Client that reads records and tracks progress" },
  { answer: "REBALANCE", term: "Rebalance", clue: "Redistributes partitions within a group" },
  { answer: "REPLICA", term: "Replica", clue: "Copy of a partition log on another broker" },
  { answer: "COMPACTION", term: "Compaction", clue: "Keeps the latest record for each key" },
  { answer: "IDEMPOTENT", term: "Idempotent", clue: "Retry-safe producer behavior against duplicates" },
  { answer: "CONSUMERGROUP", term: "Consumer group", clue: "Consumers that divide partitions and share offsets" },
];
export const RUSH = [
  { task: "Kafka ordering boundary", answer: "Partition", wrong: ["Topic", "Broker", "Consumer group"] },
  { task: "Consumer progress marker", answer: "Offset", wrong: ["Sequence", "Replica", "ISR"] },
  { task: "Ordering records for one entity", answer: "Stable key", wrong: ["Random key", "No key", "New topic per event"] },
];
export const BUGS = [];
export const META = { rushLabel: "Kafka Rush", rushIntro: "Choose the Kafka concept that matches.", rushMono: true, bugLabel: "Kafka Bug Hunt", bugNoun: "finding" };
