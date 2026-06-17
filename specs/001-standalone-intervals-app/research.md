# research.md

Decision: Update mechanism — Scheduled checks with user prompts (daily default)

Rationale: Balances security (regular checks) with user control; avoids silent restarts that could disrupt active workflows. Allows deferral.

Alternatives considered:
- Automatic silent updates — pros: immediate security patching; cons: potential disruption and user distrust
- Manual checks only — pros: user control; cons: slower adoption of fixes

Decision: OS targets — macOS and Windows for v1

Rationale: Covers the majority of desktop users while keeping packaging/testing scope manageable. Linux considered for v2.

Decision: Minimum OS versions — macOS 11 (Big Sur) and Windows 10 21H2

Rationale: Good balance between compatibility and modern OS features (native secure storage APIs, notarization support, signed installers)
