import { topicBench, scenarioLab } from "./catalog.js";

export function showLab(view, badge, color, title, intro, content) {
  scenarioLab(view, badge, color, title, intro, content);
}

export function showBuilder(view, title, subtitle, content) {
  topicBench(view, title, subtitle, content, (topic) => topic.examples?.[0]?.code || topic.commands?.[0] || topic.key_points?.[0] || topic.what);
}
