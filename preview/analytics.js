import { nowIso } from "./session.js";

const REQUIRED_EVENTS = new Set([
  "preview_loaded",
  "query_submitted",
  "response_rendered",
  "cta_clicked",
  "error_fallback",
]);

export function sanitizeMetadata(metadata = {}) {
  const blocked = ["api_key", "token", "password", "secret", "user_id"];
  const out = {};
  for (const [key, value] of Object.entries(metadata)) {
    if (!blocked.includes(key.toLowerCase())) {
      out[key] = value;
    }
  }
  return out;
}

export function createEvent(sessionId, eventType, metadata = {}) {
  if (!REQUIRED_EVENTS.has(eventType)) {
    throw new Error(`Unsupported event type: ${eventType}`);
  }
  return {
    event_id: crypto.randomUUID(),
    session_id: sessionId,
    event_type: eventType,
    event_time: nowIso(),
    metadata: sanitizeMetadata(metadata),
  };
}

export function emitEvent(bus, event) {
  bus.push(event);
  return event;
}

export function computeEngagementRate(summary) {
  if (!summary.totalSessions) return 0;
  return summary.engagedSessions / summary.totalSessions;
}
