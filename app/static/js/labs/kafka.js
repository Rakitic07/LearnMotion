import { $, highlightCode } from "../util.js";
import { scenarioLab } from "./catalog.js";

export function lab(view, content) {
  scenarioLab(view, "KAFKA", "peach", "Kafka Flow Simulator", "Follow a keyed event through a partition, replica set, consumer group and offset commit.", content);
}

export function playground(view) {
  view.innerHTML = `<section class="topic-hero clay"><div class="code tint-peach">KFK</div><div><h1>Kafka Config Builder</h1><div class="muted">Explore the relationship between partitioning, replication, acknowledgements and minimum in-sync replicas.</div></div></section><div class="grid two" style="margin-top:1rem"><section class="panel clay"><label>Partitions <b id="kPartLabel">6</b><input id="kParts" type="range" min="1" max="24" value="6"></label><label>Replication factor <b id="kRepLabel">3</b><input id="kRep" type="range" min="1" max="5" value="3"></label><label>Minimum in-sync replicas <b id="kIsrLabel">2</b><input id="kIsr" type="range" min="1" max="3" value="2"></label><label>Producer acknowledgements<select id="kAcks"><option value="all">all</option><option value="1">leader only (1)</option><option value="0">none (0)</option></select></label><label class="check" style="display:flex;gap:.6rem;margin-top:.7rem"><input type="checkbox" id="kIdempotent" checked> Enable idempotent producer</label></section><section class="panel clay"><h3>Configuration &amp; consequences</h3><pre id="kOut" class="code" style="white-space:pre-wrap"></pre><div id="kAdvice" aria-live="polite"></div></section></div>`;
  const draw = () => {
    const p = +$("#kParts", view).value, r = +$("#kRep", view).value, min = +$("#kIsr", view).value, acks = $("#kAcks", view).value, idem = $("#kIdempotent", view).checked;
    $("#kPartLabel", view).textContent = p; $("#kRepLabel", view).textContent = r; $("#kIsrLabel", view).textContent = min;
    $("#kIsr", view).max = r;
    const valid = min <= r && !(acks === "all" && min === 1);
    $("#kOut", view).innerHTML = highlightCode(`partitions=${p}\nreplication.factor=${r}\nmin.insync.replicas=${min}\nacks=${acks}\nenable.idempotence=${idem}`, "properties");
    $("#kAdvice", view).innerHTML = valid ? `<p class="pill success">Configuration is internally plausible</p><p class="muted">Same-key records stay ordered in one partition. ${acks === "all" ? `Acks=all waits for the current ISR; the cluster rejects writes below min ISR (${min}).` : "Weaker acknowledgements reduce the durability guarantee."}</p>` : `<p class="pill danger">Review durability settings</p><p class="muted">min.insync.replicas cannot exceed the replication factor. For durable replicated writes, pair acks=all with at least two in-sync replicas.</p>`;
  };
  view.querySelectorAll("#kParts, #kRep, #kIsr, #kAcks, #kIdempotent").forEach((el) => { el.addEventListener("input", draw); el.addEventListener("change", draw); });
  draw();
}
