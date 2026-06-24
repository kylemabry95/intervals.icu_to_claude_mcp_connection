const DATASET = {
  athletes: [
    { name: "Jordan", load: 589, wellness: "stable" },
    { name: "Casey", load: 540, wellness: "improving" },
  ],
  workouts: [
    { day: "Mon", type: "Threshold", duration: 58 },
    { day: "Tue", type: "Recovery", duration: 40 },
    { day: "Wed", type: "VO2", duration: 52 },
  ],
};

export function getDemoDataset() {
  return JSON.parse(JSON.stringify(DATASET));
}

export function hasSensitiveData(obj) {
  return JSON.stringify(obj).match(/api[_-]?key|token|pass(?:phrase|code)|secret/i) !== null;
}
