import chatScenarios from "./scenarios/chat_scenarios.json" assert { type: "json" };
import authScenarios from "./scenarios/auth_scenarios.json" assert { type: "json" };
import settingsScenarios from "./scenarios/settings_scenarios.json" assert { type: "json" };

export function getScenariosByCategory(category) {
  const all = [...chatScenarios, ...authScenarios, ...settingsScenarios];
  return all.filter((s) => s.category === category && s.enabled);
}

export function getAllScenarios() {
  return [...chatScenarios, ...authScenarios, ...settingsScenarios].filter((s) => s.enabled);
}
