export const WORDS = ["PROMQL", "GRAFANA", "LOGSTASH", "KIBANA", "JAEGER", "TRACE", "METRIC", "HISTOGRAM"].map((answer) => ({ answer, term: answer, clue: `Observability concept: ${answer}` }));
export const RUSH = [{ task: "Prometheus counter query", answer: "rate()", wrong: ["sum()", "label_join()", "absent()"] }, { task: "Kibana filter language", answer: "KQL", wrong: ["HCL", "SQL", "YAML"] }];
export const BUGS = [];
export const META = { rushLabel: "Observability Rush", rushIntro: "Choose the tool or query concept.", rushMono: true, bugLabel: "Telemetry Bug Hunt", bugNoun: "finding" };
