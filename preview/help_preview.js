import { HELP_OVERVIEW } from "./messages.js";

export function renderHelpPreview(container) {
  container.innerHTML = `
    <h2>Help Preview</h2>
    <p>${HELP_OVERVIEW}</p>
    <ul>
      <li>Tooltip guidance for key actions</li>
      <li>FAQ for common setup issues</li>
      <li>Error-to-guidance links for faster recovery</li>
    </ul>
  `;
}
