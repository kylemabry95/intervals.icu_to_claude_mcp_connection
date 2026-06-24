import { API_GUIDANCE_TEXT } from "./messages.js";

export function renderAuthPreview(container) {
  container.innerHTML = `
    <h2>Authentication Preview</h2>
    <ol>
      <li>Open intervals.icu and generate an API key.</li>
      <li>Paste the key in the installed app login screen.</li>
      <li>Start asking Claude about your training data.</li>
    </ol>
    <p>${API_GUIDANCE_TEXT}</p>
    <a href="https://intervals.icu/settings" target="_blank" rel="noreferrer">Open intervals.icu settings</a>
  `;
}

export function createDemoAuthState() {
  return {
    apiKeyEntered: false,
    completed: false,
  };
}
