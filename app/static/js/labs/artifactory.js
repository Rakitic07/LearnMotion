import { showBuilder, showLab } from "./devops_catalog.js";
export const lab = (view, content) => showLab(view, "ART", "mint", "Repository Flow Lab", "Trace package resolution, promotion, permissions and provenance through JFrog Artifactory or Sonatype Nexus.", content);
export const playground = (view, content) => showBuilder(view, "Repository Policy Builder", "Select a package repository lesson and adapt its publishing or verification example.", content);
