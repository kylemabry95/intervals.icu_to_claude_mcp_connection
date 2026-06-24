export function activateFallback(message = "Preview temporarily unavailable. You can still download the app below.") {
  const banner = document.getElementById("fallback-banner");
  if (!banner) {
    return false;
  }
  banner.textContent = message;
  banner.classList.remove("hidden");
  return true;
}

export function recoverFallback() {
  const banner = document.getElementById("fallback-banner");
  if (!banner) {
    return false;
  }
  banner.classList.add("hidden");
  return true;
}
