const DEFAULT_FALLBACK =
  "I can show sample insights in preview mode. Try: 'Show my recent workouts' or 'Who has highest training load this week?'";

const templates = [
  {
    id: "recent_workouts",
    triggers: ["recent workouts", "workouts"],
    response:
      "In this preview dataset, you completed 3 sessions this week: Threshold (58m), Recovery (40m), and VO2 (52m).",
    latency_budget_ms: 700,
  },
  {
    id: "highest_load",
    triggers: ["highest training load", "training load"],
    response:
      "Jordan currently has the highest weekly training load in this demo sample.",
    latency_budget_ms: 650,
  },
];

export function resolveTemplate(query) {
  const normalized = String(query || "").toLowerCase();
  const match = templates.find((t) => t.triggers.some((trigger) => normalized.includes(trigger)));
  if (!match) {
    return { template_id: "fallback", response: DEFAULT_FALLBACK, latency_budget_ms: 250 };
  }
  return { template_id: match.id, response: match.response, latency_budget_ms: match.latency_budget_ms };
}

export function isDeterministic(query) {
  const first = resolveTemplate(query);
  const second = resolveTemplate(query);
  return first.response === second.response;
}
