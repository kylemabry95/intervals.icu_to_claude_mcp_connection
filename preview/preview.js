import { createSession, touchSession } from "./session.js";
import { resolveTemplate } from "./template_engine.js";
import { INSTALLED_APP_DISCLAIMER } from "./messages.js";
import { getCtas, validateCtas } from "./cta.js";
import { renderAuthPreview } from "./auth_preview.js";
import { renderSettingsPreview } from "./settings_preview.js";
import { renderHelpPreview } from "./help_preview.js";
import { createEvent, emitEvent } from "./analytics.js";
import { activateFallback } from "./fallbacks.js";

const eventBus = [];
let session = createSession({
  device_type: window.innerWidth < 768 ? "mobile" : "desktop",
  browser_family: navigator.userAgent,
  locale: navigator.language,
});

function addMessage(kind, text) {
  const history = document.getElementById("chat-history");
  const item = document.createElement("p");
  item.className = `chat-message ${kind}`;
  item.textContent = text;
  history.appendChild(item);
}

function setupTabs() {
  const tabs = document.querySelectorAll(".tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      document.querySelectorAll(".panel").forEach((panel) => panel.classList.remove("active"));
      document.getElementById(`panel-${tab.dataset.tab}`)?.classList.add("active");
    });
  });
}

function setupChat() {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const disclaimer = document.getElementById("chat-disclaimer");

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    session = touchSession(session);
    emitEvent(eventBus, createEvent(session.session_id, "query_submitted", { query_length: query.length }));

    addMessage("user", query);
    const response = resolveTemplate(query);
    addMessage("assistant", response.response);
    disclaimer.textContent = INSTALLED_APP_DISCLAIMER;

    emitEvent(eventBus, createEvent(session.session_id, "response_rendered", { template_id: response.template_id }));
    input.value = "";
  });
}

function setupCtas() {
  try {
    const ctas = validateCtas(getCtas());
    ctas.forEach((cta) => {
      const element = document.getElementById(`download-${cta.platform}`);
      if (!element) return;
      element.href = cta.url;
      element.textContent = cta.label;
      element.addEventListener("click", () => {
        session.clicked_download_cta = true;
        emitEvent(eventBus, createEvent(session.session_id, "cta_clicked", { platform: cta.platform }));
      });
    });
  } catch (error) {
    activateFallback("Download links unavailable. Please try again later.");
    emitEvent(eventBus, createEvent(session.session_id, "error_fallback", { reason: "cta_validation_failed" }));
  }
}

function setupContentPanels() {
  renderAuthPreview(document.getElementById("auth-content"));
  renderSettingsPreview(document.getElementById("settings-content"));
  renderHelpPreview(document.getElementById("help-content"));
}

try {
  setupTabs();
  setupChat();
  setupCtas();
  setupContentPanels();
  emitEvent(eventBus, createEvent(session.session_id, "preview_loaded"));
} catch (error) {
  activateFallback();
  emitEvent(eventBus, createEvent(session.session_id, "error_fallback", { reason: "bootstrap_failure" }));
}

window.__previewEventBus = eventBus;
