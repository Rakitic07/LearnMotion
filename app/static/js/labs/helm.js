import { showBuilder, showLab } from "./devops_catalog.js";
export const lab = (view, content) => showLab(view, "HELM", "sky", "Chart Render Lab", "Review values, rendered manifests, hooks and release behavior before a Helm upgrade.", content);
export const playground = (view, content) => showBuilder(view, "Chart Values Builder", "Select a Helm lesson and adapt its chart, template or release example.", content);
