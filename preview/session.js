export function nowIso() {
  return new Date().toISOString();
}

export function createSession(context = {}) {
  const started = nowIso();
  const deviceType = context.device_type || "desktop";
  if (!["desktop", "tablet", "mobile"].includes(deviceType)) {
    throw new Error("Invalid device_type");
  }
  return {
    session_id: crypto.randomUUID(),
    started_at: started,
    last_interaction_at: started,
    device_type: deviceType,
    browser_family: context.browser_family || "unknown",
    locale: context.locale || null,
    completed_first_query: false,
    clicked_download_cta: false,
  };
}

export function touchSession(session) {
  const updated = { ...session, last_interaction_at: nowIso() };
  if (updated.last_interaction_at < updated.started_at) {
    throw new Error("Invalid timestamp ordering");
  }
  return updated;
}
