const EVENT_TYPES = [
  "preview_loaded",
  "query_submitted",
  "response_rendered",
  "cta_clicked",
  "error_fallback",
];

export function validateEventType(eventType) {
  if (!EVENT_TYPES.includes(eventType)) {
    throw new Error(`Unknown event_type: ${eventType}`);
  }
  return true;
}

export function sanitizeEventMetadata(metadata = {}) {
  const forbidden = new Set(["api_key", "token", "secret", "password", "user_id"]);
  return Object.fromEntries(
    Object.entries(metadata).filter(([k]) => !forbidden.has(k.toLowerCase()))
  );
}

export function buildEvent(sessionId, eventType, metadata = {}) {
  validateEventType(eventType);
  return {
    event_id: crypto.randomUUID(),
    session_id: sessionId,
    event_type: eventType,
    event_time: new Date().toISOString(),
    metadata: sanitizeEventMetadata(metadata),
  };
}
