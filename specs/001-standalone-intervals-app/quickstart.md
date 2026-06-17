# quickstart.md

Prerequisites

- Python 3.10+
- `pip install -r requirements.txt`
- Claude Desktop installed and running (MCP enabled)

Run locally (development)

```bash
export INTERVALS_API_KEY="your_api_key"
export INTERVALS_ATHLETE_ID="your_athlete_id"
python server.py
```

Run smoke tests

```bash
export INTERVALS_API_KEY="your_api_key"
export INTERVALS_ATHLETE_ID="your_athlete_id"
python test_server.py
```

Packaging & distribution (high level)

- macOS: build app bundle, sign and notarize, create DMG/PKG
- Windows: create signed installer (MSI or NSIS)
- Use CI runners for macOS and Windows to build artifacts
