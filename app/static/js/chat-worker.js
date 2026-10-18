const MODEL_ID = "Qwen2.5-1.5B-Instruct-q4f16_1-MLC";
const FALLBACK_MODEL_ID = "Qwen2.5-0.5B-Instruct-q4f16_1-MLC";
const WEBLLM_URL = "https://esm.run/@mlc-ai/web-llm@0.2.86";
let enginePromise;

async function getEngine(modelId) {
  if (!enginePromise) {
    enginePromise = (async () => {
      const { CreateMLCEngine } = await import(WEBLLM_URL);
      return CreateMLCEngine(modelId, {
        initProgressCallback: (progress) => postMessage({ type: "progress", text: progress.text || "Preparing browser model…", progress: progress.progress ?? null }),
      });
    })().catch((error) => {
      enginePromise = null;
      throw error;
    });
  }
  return enginePromise;
}

function isQuotaError(error) {
  return error?.name === "QuotaExceededError" || /quota exceeded|storage quota/i.test(error?.message || "");
}

function shouldTrySmallerModel(error) {
  return isQuotaError(error) || /out of memory|memory allocation|allocation failed|device lost|gpu memory/i.test(error?.message || "");
}

async function preloadModel(modelId) {
  try {
    const engine = await getEngine(modelId);
    await engine.unload();
    enginePromise = null;
    return { modelId, fallback: false };
  } catch (error) {
    if (!shouldTrySmallerModel(error) || modelId !== MODEL_ID) throw error;
    postMessage({ type: "status", text: "The larger tutor model exceeded this device's available storage or GPU memory. Removing its partial download and trying the smaller model…" });
    enginePromise = null;
    try {
      const { deleteModelAllInfoInCache } = await import(WEBLLM_URL);
      await deleteModelAllInfoInCache(MODEL_ID);
    } catch (cleanupError) {
      console.warn("Could not clear the incomplete larger model cache:", cleanupError);
    }
    const engine = await getEngine(FALLBACK_MODEL_ID);
    await engine.unload();
    enginePromise = null;
    return { modelId: FALLBACK_MODEL_ID, fallback: true };
  }
}

self.onmessage = async (event) => {
  const type = event.data?.type;
  if (type !== "chat" && type !== "preload") return;
  const modelId = event.data?.modelId || MODEL_ID;
  try {
    postMessage({ type: "status", text: type === "preload" ? "Downloading and preparing the tutor in the background…" : "Loading the cached tutor on this device…" });
    if (type === "preload") {
      const prepared = await preloadModel(modelId);
      postMessage({ type: "preloaded", ...prepared });
      return;
    }
    const engine = await getEngine(modelId);
    postMessage({ type: "status", text: "Writing a brief answer…" });
    const stream = await engine.chat.completions.create({
      messages: event.data.messages,
      temperature: 0.2,
      max_tokens: 320,
      stream: true,
    });
    for await (const chunk of stream) {
      const token = chunk.choices?.[0]?.delta?.content;
      if (token) postMessage({ type: "token", text: token });
    }
    postMessage({ type: "done", sources: event.data.sources || [] });
  } catch (error) {
    console.error("LearnMotion browser model setup failed:", error);
    const message = error?.message || "The browser mini model could not start.";
    const cause = error?.cause?.message;
    postMessage({ type: type === "preload" ? "prefetch-error" : "error", text: cause ? `${message} (${cause})` : message });
  }
};
