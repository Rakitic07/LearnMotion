import { showBuilder, showLab } from "./devops_catalog.js";
export const lab = (view, content) => showLab(view, "ARGO", "peach", "GitOps Reconcile Lab", "Diagnose OutOfSync, health, permissions and reconciliation problems across an Argo CD application.", content);
export const playground = (view, content) => showBuilder(view, "Application Builder", "Select an Argo CD lesson to adapt an Application, project or sync policy example.", content);
