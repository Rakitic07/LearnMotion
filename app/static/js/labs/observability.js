import { showBuilder, showLab } from "./devops_catalog.js";
export const lab = (view, content) => showLab(view, "OBS", "peach", "Telemetry Triage Lab", "Trace a symptom from Prometheus metrics through Grafana dashboards, Elasticsearch logs and Jaeger traces.", content);
export const playground = (view, content) => showBuilder(view, "Query & Rule Builder", "Select a lesson to load its PromQL, Logstash, KQL or telemetry example.", content);
