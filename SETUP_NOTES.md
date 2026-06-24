# Setup Notes - Critical Authentication Fix

## Important: Proper API Authentication

This MCP server requires **proper Basic Authentication** for the Intervals.icu API.

---

## Standalone Desktop Application

The standalone desktop app bundles the MCP server with a Claude-powered chat UI.

### Quick start (development)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up credentials
cp .env.example .env
# Edit .env and fill in:
#   INTERVALS_API_KEY    — from intervals.icu → Settings → API
#   INTERVALS_ATHLETE_ID — your athlete ID (e.g. i12345)
#   ANTHROPIC_API_KEY    — from https://console.anthropic.com

# 3. Launch
python -m desktop_app.main
```

### Run tests

```bash
# Fast unit + integration tests
pytest tests/unit tests/integration -v

# All tests excluding live e2e
pytest tests/ -v -m "not e2e"
```

### Build distributable packages

**macOS:**

```bash
./packaging/macos/build.sh --version 1.0.0
# Output: dist/macos/IntervalsICU-1.0.0.dmg
```

**Windows (PowerShell):**

```powershell
.\packaging\windows\build.ps1 -Version "1.0.0"
# Output: dist\windows\IntervalsICU-1.0.0-Setup.exe
```

### Troubleshooting the desktop app

| Problem                                  | Likely cause              | Fix                                                                             |
| ---------------------------------------- | ------------------------- | ------------------------------------------------------------------------------- |
| "Missing required environment variable"  | `.env` not configured     | Copy `.env.example` to `.env` and fill in credentials                           |
| Auth fails with 401/403                  | Invalid API key           | Regenerate at intervals.icu → Settings → API                                    |
| "The background service could not start" | `server.py` not found     | Run from the project root directory                                             |
| Claude not responding                    | Missing Anthropic API key | Add `ANTHROPIC_API_KEY` to `.env`                                               |
| App logs location                        | n/a                       | macOS: `~/Library/Logs/IntervalsICU/` · Windows: `%APPDATA%\IntervalsICU\Logs\` |

---

### Authentication Format

The Intervals.icu API uses Basic Authentication with a specific format:

- **Username:** Literally the string `"API_KEY"` (not your actual username)
- **Password:** Your actual API key from Intervals.icu settings
- **Encoding:** Base64-encoded as `"API_KEY:your_api_key_here"`

### Required Environment Variables

Your `claude_desktop_config.json` **MUST** include all three environment variables:

```json
{
  "mcpServers": {
    "intervals-icu": {
      "command": "/usr/local/bin/python3",
      "args": ["/ABSOLUTE/PATH/TO/server.py"],
      "env": {
        "INTERVALS_API_KEY": "your_actual_api_key",
        "INTERVALS_ATHLETE_ID": "i230309",
        "INTERVALS_API_BASE_URL": "https://intervals.icu/api/v1"
      }
    }
  }
}
```

### Common Issues

#### 403 Forbidden Errors

If you get 403 errors, check:

1. **API Key Invalid** - Regenerate your API key in Intervals.icu settings
2. **Missing INTERVALS_API_BASE_URL** - This variable is required (added in v2.0.1)
3. **Wrong Python Path** - Use full path like `/usr/local/bin/python3`, not just `python`
4. **Athlete ID Format** - Must include the `i` prefix (e.g., `i230309` not `230309`)

#### Debug Output

The server includes startup debug output in Claude Desktop logs:

```
============================================================
INTERVALS.ICU MCP SERVER - STARTUP DEBUG INFO
============================================================
API Key Present: ✓ YES
API Key (first 8 chars): ckw1e9g3...
Athlete ID: i230309
Base URL: https://intervals.icu/api/v1
Auth Header (first 20 chars): Basic QVBJX0tFWTpja3cx...
Test Athlete URL: https://intervals.icu/api/v1/athlete/i230309
============================================================
```

Check these logs if the connection fails:

- **macOS:** `~/Library/Logs/Claude/`
- **Windows:** `%APPDATA%\Claude\logs\`

### Testing Your API Key

Before configuring Claude Desktop, test your API key works:

```bash
curl -u API_KEY:your_api_key_here https://intervals.icu/api/v1/athlete/your_athlete_id
```

If this returns `{"status":403,"error":"Access denied"}`, your API key is invalid - regenerate it in Intervals.icu settings.

### Version History

- **v2.0.1** (March 2026) - Fixed authentication and added INTERVALS_API_BASE_URL requirement
- **v2.0.0** (March 2025) - Initial 36-tool release

## Getting Your Credentials

### API Key

1. Log in to [intervals.icu](https://intervals.icu)
2. Go to Settings
3. Scroll to "Developer Settings" (near the bottom)
4. Click "Generate API Key"
5. Copy the key immediately (you can't view it again)

### Athlete ID

Your athlete ID is visible in the URL when logged in:

```
https://intervals.icu/athlete/i230309/calendar
                              ^^^^^^^^
                              This is your athlete ID
```

**Important:** The athlete ID includes the `i` prefix!

## Full Setup Steps

1. Get your API key and athlete ID (see above)
2. Test the API key with curl (see above)
3. Copy `claude_desktop_config.example.json` to the correct location:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
4. Update the three required values:
   - Full path to `server.py`
   - Your `INTERVALS_API_KEY`
   - Your `INTERVALS_ATHLETE_ID`
5. Restart Claude Desktop completely
6. Check the logs for the startup debug output
7. Test by asking Claude: "Get my athlete profile"

## Troubleshooting Checklist

- [ ] API key is valid (tested with curl)
- [ ] Athlete ID includes the `i` prefix
- [ ] All three environment variables are set
- [ ] Python path is absolute and correct
- [ ] server.py path is absolute and correct
- [ ] Claude Desktop was restarted after config changes
- [ ] No JSON syntax errors in config file

## Support

If you're still having issues:

1. Check the debug output in Claude Desktop logs
2. Test your API key with curl
3. Open a GitHub issue with the debug output (redact your API key!)

---

## Feature 004: UI Preview Before Download

The repository includes a browser-hosted preview under `preview/` for pre-download product exploration.

### Local preview workflow

```bash
# from repo root
python -m http.server 8000
# open http://localhost:8000/preview/
```

### Maintenance checklist

- Keep `preview/scenarios/*.json` aligned with current UX copy and capabilities
- Keep `preview/template_engine.js` deterministic (no live API/LLM calls)
- Keep CTA links HTTPS-only in `preview/cta.js`
- Re-run preview tests after any UI text/flow change:

```bash
pytest tests/unit/test_preview_*.py tests/integration/test_preview_*.py tests/e2e/test_preview_*.py -v
```

### Security boundary

Preview mode must never collect or process real API keys, tokens, or user-identifying training data.
