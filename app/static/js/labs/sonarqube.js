import { scenarioLab } from "./catalog.js";

export function lab(view, content) {
  scenarioLab(view, "SON", "sky", "SonarQube Quality Gate Lab", "Review findings, new-code conditions and pipeline outcomes before setting a gate.", content);
}

export { playground } from "./sonarqube_builder.js";
