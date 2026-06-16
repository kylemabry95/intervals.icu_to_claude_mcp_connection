<!-- 
Sync Impact Report (Constitution v1.0.0)
========================================
Initial baseline constitution established with 9 core principles:
- AI Cost and Token Optimization (new)
- Approved AI Asset Usage (new)
- Testing as a Non-Negotiable Requirement (new)
- Security, Access Control, and Data Protection (new)
- Reproducibility and Automation (new)
- Maintainability and Reviewability (new)
- Troubleshooting and Debugging (new)
- Version Control Systems (new)
- Project-Specific Extensions (new)

Version bump: 1.0.0 (initial baseline constitution)
Ratified: 2026-06-16
Dependent templates requiring alignment checks (in progress):
- .specify/templates/plan-template.md
- .specify/templates/spec-template.md
- .specify/templates/tasks-template.md
-->

# intervals.icu MCP Server Constitution

This constitution establishes baseline governance for all AI-assisted development, engineering standards, and project-specific practices. These principles are non-negotiable and form the foundation for all development decisions.

## Core Principles

### I. AI Cost and Token Optimization

All AI-assisted development must prioritize cost-conscious engineering practices. This project uses LLMs, agents, prompts, and MCP servers; therefore token consumption and cost optimization are mandatory engineering concerns, not afterthoughts.

**Non-Negotiable Rules:**
- Use approved Skills (Caveman, RTK, compact) and structured workflows to reduce unnecessary token consumption
- Avoid repeated context loading; prefer summarized, indexed, or cached context when sufficient
- Use retrieval, decomposition, or task-specific context patterns to minimize prompt size
- Prefer deterministic tooling, scripts, tests, and automation over repeated LLM reasoning
- Document any project-specific AI workflows that require specialized cost optimization patterns
- Treat unnecessary LLM usage as an engineering inefficiency to be reduced during review and refactoring

**Required Workflows:**
- Use `/specify.clarify` or `/grill-me` before `/specify.plan` to validate requirements
- Use `/specify.analyze` after `/specify.tasks` and before `/specify.implement` to catch inefficiencies
- Code reviews must validate that AI-generated code does not introduce unnecessary token overhead

---

### II. Approved AI Asset Usage

Only approved or reviewed AI assets—Skills, prompts, agents, MCP servers—may be introduced without formal review. Any new AI asset must be documented with:
- Clear purpose and expected usage
- Identified risks and failure modes
- Cost-efficiency rationale and impact analysis

This ensures the project maintains control over its AI dependencies and prevents cost or quality regressions.

---

### III. Testing as a Non-Negotiable Requirement

All production code must include appropriate automated tests. This is not optional or deferred.

**Non-Negotiable Rules:**
- New features require automated tests where practical; deviations require explicit justification and approval
- Bug fixes must include regression tests when practical
- Critical workflows must have validation steps or integration tests
- Generated code (from AI or templates) must not be accepted without review and test verification
- Testing requirements must be explicitly documented in feature specifications and acceptance criteria

**Test Quality Standards:**
- Tests must be maintainable, clear, and independent of other tests
- Test coverage for new features must be documented and justified
- Flaky or unreliable tests are blockers for merging

---

### IV. Security, Access Control, and Data Protection

The project must follow secure-by-default engineering practices. All authentication, authorization, secrets, and data access must be explicitly handled; least-privilege design is non-negotiable.

**Non-Negotiable Rules:**
- Generated or human-written code must never expose credentials, bypass authorization, or weaken identity controls
- Secrets (API keys, tokens, credentials) must be stored in environment variables or secure vaults; never in code or documentation
- All API calls to intervals.icu must validate authentication tokens before use
- Data access must enforce the minimum necessary permissions required for each operation
- Security code reviews must verify no insecure defaults are introduced

**Specific to This Project:**
- intervals.icu API key access must be strictly controlled and never logged or exposed in error messages
- User training data must be treated as sensitive; access must be logged and auditable
- All external API communications must use HTTPS; no fallback to HTTP

---

### V. Reproducibility and Automation

Development and deployment workflows must be reproducible and automated wherever practical. Manual steps create risk, inconsistency, and inefficiency.

**Non-Negotiable Rules:**
- All environment setup must be documented clearly; one-shot commands should exist to bootstrap a complete development environment
- Infrastructure as Code practices must be applied where applicable
- Build, test, and deployment commands must be repeatable and deterministic
- Environment-specific configuration must be externalized (environment variables, config files, secrets management)
- Automated validation must catch common errors and drift before humans need to debug

**Project-Specific Automations:**
- MCP server startup must be automatable with a single command
- Environment validation must check Python version, required packages, API key availability before startup
- Test suite must be runnable with a single command; no manual setup required beyond environment variables

---

### VI. Maintainability and Reviewability

Code, specifications, and design artifacts must be maintainable by the broader team. This project values clarity and explicit assumptions over cleverness.

**Non-Negotiable Rules:**
- All commits must have clear, detailed messages explaining *why* changes were made, not just *what*
- Large changes must be broken into small, reviewable pieces
- Architecture decisions must be documented with rationale and tradeoffs
- Naming must be consistent and explicit; abbreviations must be justified and documented
- Complexity must be justified; prefer simple, obvious solutions
- Code reviews must verify comprehensibility, not just correctness

**Code Style Standards:**
- Follow PEP 8 for Python code; consistency is enforced via linting
- Comments must explain *why*, not *what*; code should be self-documenting where possible
- Avoid nested complexity; extract functions or classes when logic depth exceeds 2–3 levels

---

### VII. Troubleshooting and Debugging

Development workflow must include structured debugging and diagnostic practices. When issues arise, the root cause must be identified methodically, not through trial-and-error iteration.

**Debugging Standards:**
- Use `/diagnose` skill when available for systematic troubleshooting
- Failures must be reproducible before fixing; document reproduction steps
- Error messages must be actionable and include context for debugging
- Logs must include structured data (timestamps, function names, parameter values) to aid troubleshooting
- Post-mortems or investigation notes must be saved for future reference (in session memory or docs)

---

### VIII. Version Control Systems

All projects must be managed in a Git repository, even if local-only. Version control is not optional.

**Non-Negotiable Rules:**
- All changes must be committed; no lost work
- All commits must be signed (using GPG or equivalent); unsigned commits are not acceptable
- All commit messages must be explicit and detailed, explaining the *why* and *what*
- Commit history must be clean enough to serve as documentation; squash or fixup commits to maintain clarity
- Branching strategy must be documented and consistent; all feature work must have reviewable PR or merge request

**Suggested Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```
Example: `feat(mcp): add intervals.icu athlete endpoint integration - adds support for querying athlete profiles with caching`

---

### IX. Project-Specific Extensions

Teams may extend this constitution with stricter rules tailored to mission-critical, customer-facing, platform, or architecture-specific needs. **However, project-specific rules may not remove, contradict, or bypass these baseline principles.**

**When to add project-specific rules:**
- Mission-critical or customer-facing functionality requires additional safeguards (e.g., enhanced testing, security reviews)
- Platform constraints require specific practices (e.g., MCP protocol conformance rules, intervals.icu API versioning policy)
- Performance or reliability standards exceed baseline (e.g., P99 latency targets, uptime SLAs)
- Compliance or audit requirements demand additional controls

**Process for Adding Rules:**
- Proposed rules must be documented in this section with clear rationale
- Rules must be reviewed by the project maintainers
- Rules must preserve all baseline principles; contradictions are rejected
- Implementation plan and timeline must be included

---

## Governance

This constitution supersedes all ad hoc practices, team preferences, or prior informal guidance. All project decisions must align with these principles.

**Amendment Process:**
- Constitutional amendments require documented justification and impact analysis
- All amendments must preserve baseline principles (I–VIII); contradict at your own risk
- Version number must be incremented according to semantic versioning:
  - **MAJOR**: Backward-incompatible changes to principles or removal of core rules
  - **MINOR**: New principle added, significant clarification, or expanded guidance
  - **PATCH**: Clarifications, typo fixes, or non-semantic refinements
- All amendments must be reflected in the commit message and `.specify/memory/constitution.md`
- Amendment date must be recorded in the metadata line below

**Compliance and Review:**
- All pull requests and code reviews must verify compliance with this constitution
- Code review checklist must include: testing requirements met, security rules followed, cost optimization applied
- If a change conflicts with the constitution, the change is rejected; exceptions require explicit amendment
- Team members must raise constitutional concerns during code review, not after

**Development Guidance:**
- For runtime development workflow, see `.github/copilot-instructions.md` and project README
- For feature specification process, use `/specify.clarify`, `/specify.plan`, `/specify.tasks`, `/specify.analyze`, and `/specify.implement`
- For codebase improvements, use `/improve-codebase-architecture` skill when available
- For debugging and troubleshooting, use `/diagnose` skill and save investigation notes

**Version Control and History:**
- All commits implementing constitutional changes must reference this document
- Git commit history serves as an audit trail of governance evolution

---

**Version**: 1.0.0 | **Ratified**: 2026-06-16 | **Last Amended**: 2026-06-16
