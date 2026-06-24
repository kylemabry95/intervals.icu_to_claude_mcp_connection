export function renderSettingsPreview(container) {
  container.innerHTML = `
    <h2>Settings Tour</h2>
    <ul>
      <li>Update checks (daily by default)</li>
      <li>Logging and diagnostics visibility</li>
      <li>Credential management in installed app</li>
    </ul>
    <p>All controls shown here are a preview. Real changes happen in the installed app.</p>
  `;
}
