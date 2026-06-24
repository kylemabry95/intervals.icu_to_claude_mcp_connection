# Research: UI Preview Before DMG Download

## Decision 1: Delivery Model for Preview Experience

- Decision: Use a browser-hosted interactive preview embedded on the download landing page.
- Rationale: Users can evaluate core UX before install, reducing uncertainty and improving conversion to download.
- Alternatives considered:
  - Embedded video only: Faster to produce, but less confidence because users cannot interact.
  - Separate downloadable demo app: Defeats the goal of pre-download validation.

## Decision 2: Demo Data Strategy

- Decision: Use static anonymized demo datasets and deterministic response templates.
- Rationale: Eliminates exposure of real user data and avoids dependency on live intervals.icu or Claude APIs.
- Alternatives considered:
  - Live API passthrough: Better realism, but introduces auth complexity and security risk.
  - Fully mocked placeholder text: Too artificial and less representative of actual UX.

## Decision 3: Interaction Fidelity Scope (v1)

- Decision: High-fidelity chat interaction for P1; guided auth flow and settings walkthrough for P2/P3.
- Rationale: Focuses engineering effort on the highest-value conversion driver while preserving extensibility.
- Alternatives considered:
  - Full parity with installed app: Higher maintenance and unnecessary for pre-download qualification.
  - Screenshot-only previews: Lower trust and weaker user understanding.

## Decision 4: Performance and Reliability Approach

- Decision: Keep preview client lightweight with preloaded scenario bundles and deterministic local response rendering.
- Rationale: Supports p95 load <3s and sub-1s interaction targets with low operational complexity.
- Alternatives considered:
  - Dynamic server-rendered previews: More flexible but slower and more failure-prone.
  - Heavy frontend framework bundle: Risk of exceeding performance goals and mobile degradation.

## Decision 5: Security and Compliance Boundaries

- Decision: Hard-separate preview environment from production credentials and data access; no real API keys accepted.
- Rationale: Satisfies constitution security principles and prevents accidental secret exposure.
- Alternatives considered:
  - Optional real account login in preview: Greater realism but violates low-risk preview objective.
  - Hidden “advanced mode” for real data: Increases support and misuse risk.

## Decision 6: Conversion and Measurement

- Decision: Instrument engagement and CTA conversion events at key funnel points (preview start, first query, CTA click).
- Rationale: Enables validation of SC-001 and SC-002 without over-collecting user data.
- Alternatives considered:
  - No analytics: Cannot validate business impact.
  - Session replay tooling: High overhead and privacy concerns for limited additional value.

## Decision 7: Platform Messaging

- Decision: Desktop-first messaging with responsive fallback and explicit macOS/Windows download CTAs.
- Rationale: Aligns feature goal (preview before DMG/install) while preserving functional access on mobile.
- Alternatives considered:
  - Desktop-only hard block: Excludes mobile discovery traffic.
  - Mobile-first design parity: Misaligned with product install targets.
