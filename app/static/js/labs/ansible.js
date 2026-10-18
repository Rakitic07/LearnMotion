import { showBuilder, showLab } from "./devops_catalog.js";
export const lab = (view, content) => showLab(view, "ANS", "rose", "Ansible Playbook Run Lab", "Diagnose inventory, task, permission and Controller workflow failures from realistic automation runs.", content);
export const playground = (view, content) => showBuilder(view, "Playbook Builder", "Select an Ansible or Automation Controller lesson and adapt its example.", content);
