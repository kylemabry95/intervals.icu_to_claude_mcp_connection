export function getCtas() {
  return [
    {
      id: "download_macos",
      platform: "macos",
      label: "Download for macOS (.dmg)",
      url: "https://example.com/download/macos",
    },
    {
      id: "download_windows",
      platform: "windows",
      label: "Download for Windows",
      url: "https://example.com/download/windows",
    },
  ];
}

export function ensureHttps(url) {
  if (!String(url).startsWith("https://")) {
    throw new Error("CTA URL must use HTTPS");
  }
  return true;
}

export function validateCtas(ctas) {
  ctas.forEach((cta) => ensureHttps(cta.url));
  return ctas;
}
