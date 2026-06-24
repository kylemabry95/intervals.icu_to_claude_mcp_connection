# Feature Specification: UI Preview Before Download

**Feature Branch**: `004-preview-ui-before-download`

**Created**: 2026-06-24

**Status**: Draft

**Input**: User description: "I want to be able to preview the ui before downloading the .dmg file"

## Clarifications

None required at specification phase. Requirements are clear and scoped.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explore Chat Interface Preview (Priority: P1)

Users visiting the intervals.icu desktop app landing page want to see what the main chat interface looks like before deciding to download. They should be able to interact with a demo version in their browser, try sample queries, and see how the conversational interface works without committing to a 100+ MB download.

**Why this priority**: P1 is the critical blocker for all user research and conversion optimization. Users cannot make a download decision without seeing the interface. This directly impacts adoption and reduces support burden from confused installations.

**Independent Test**: "Can be fully tested by: visiting the preview landing page, interacting with demo chat, seeing example responses, and getting a clear understanding of core functionality. Delivers: working interactive preview of the main UI with realistic sample data."

**Acceptance Scenarios**:

1. **Given** a user visits the app landing page, **When** they scroll to the "Try It Now" section, **Then** they see an embedded interactive preview of the chat interface without needing to download
2. **Given** the user is in the preview, **When** they type a sample query (e.g., "Show my recent workouts"), **Then** they see a deterministic simulated response with realistic training data context
3. **Given** the preview is displayed, **When** the user reads the interface, **Then** they can understand the layout, input field, message history, and basic UX without confusion
4. **Given** the user interacts with the preview, **When** they attempt to log in or access real data, **Then** they see a clear message that live data requires the installed app, with a "Download App" call-to-action prominent

---

### User Story 2 - View Authentication Flow Preview (Priority: P2)

Users may wonder about the authentication experience. Showing a preview of the login screen and API key setup flow provides confidence that the onboarding process is straightforward and doesn't require technical expertise.

**Why this priority**: P2 enhances user confidence and reduces download hesitation. Not required for MVP but significantly improves conversion when combined with chat preview. Early adopters will self-select based on chat demo; P2 helps convince technically-hesitant users.

**Independent Test**: "Can be fully tested by: viewing the authentication flow preview (screenshots or lightweight demo), understanding the steps required, and seeing clear guidance on where to get an API key. Delivers: walkthrough of onboarding without requiring real API credentials."

**Acceptance Scenarios**:

1. **Given** the user is viewing the landing page, **When** they click "See How to Get Started", **Then** they see the login and authentication screens with annotations
2. **Given** the authentication preview is displayed, **When** the user reads the screen, **Then** they understand where to input the API key and get clear links to intervals.icu to obtain one
3. **Given** the user completes the preview flow, **When** they finish the demo auth, **Then** they see "Ready to Try It?" and a clear path to download the app

---

### User Story 3 - Browse Settings and Help Features (Priority: P3)

Users who are curious about advanced features may want to preview the settings panel and available help content before downloading, to confirm the app has the level of functionality they need.

**Why this priority**: P3 is nice-to-have for power users and supports feature awareness. Not required for MVP; can be added in v1.1 after launch. Provides value to users who care about updates, logging, and configurability.

**Independent Test**: "Can be fully tested by: viewing a settings preview (screenshots or lightweight tour), seeing available preferences, and confirming help is available. Delivers: confidence that the app is configurable and well-documented."

**Acceptance Scenarios**:

1. **Given** the user is exploring the app preview, **When** they access the "Features" tab, **Then** they see a tour of settings, update preferences, and help system
2. **Given** the settings preview is displayed, **When** the user reads it, **Then** they understand update frequency, logging levels, and available preferences

---

### Edge Cases

- What happens if the preview is accessed on a mobile device? (Should show a responsive design with clear "Download on macOS/Windows" messaging)
- How should the preview behave if users try to interact with features that require live API access? (Show clear limitations and provide education on what requires the live app)
- What if the preview fails to load due to network issues? (Display graceful fallback with direct download link and feature summary)

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Application MUST provide an interactive web-based preview of the chat interface accessible from the main landing page
- **FR-002**: Preview MUST accept sample user queries and display simulated or pre-recorded Claude responses with realistic training data context
- **FR-003**: Preview MUST clearly indicate which features require the installed app and link to download
- **FR-004**: Preview MUST display the authentication flow with API key guidance and links to intervals.icu API documentation
- **FR-005**: Preview MUST include visual walkthrough of settings, preferences, logging, and help features (P3 requirement; may be screenshots initially)
- **FR-006**: Preview MUST be responsive and work on desktop browsers (Chrome, Safari, Firefox); mobile support is secondary
- **FR-007**: Preview MUST load quickly (p95 < 3s) and not require heavy JavaScript dependencies
- **FR-008**: Preview MUST include clear call-to-action buttons linking to app download pages (macOS .dmg, Windows installer)
- **FR-009**: Preview MUST not expose sensitive API keys, service credentials, or intervals.icu user data

### Key Entities

- **Preview Session**: Represents a visitor's interaction with the preview; tracks interactions, queries, and time spent
- **Sample Dataset**: Pre-configured training data (athletes, workouts, wellness metrics) used for demo queries
- **Chat Response Template**: Pre-recorded or dynamically generated responses to common sample queries

### Non-Functional Requirements

- **Performance**: Preview loads in <3 seconds, responds to chat queries in <1 second (simulated)
- **Accessibility**: Preview is keyboard-navigable and screen-reader compatible
- **Browser Support**: Works on all major browsers (Chrome, Safari, Firefox, Edge)
- **Mobile**: Displays gracefully on mobile devices; optimized experience is desktop-first

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Preview has a 25%+ engagement rate (users who interact with preview vs. landing page visitors)
- **SC-002**: Users who interact with preview increase app download rate by 15% vs. users who don't see preview (measured via analytics)
- **SC-003**: Preview loads p95 latency in <3 seconds
- **SC-004**: Chat query simulations in preview execute in <1 second (perceived as instant)
- **SC-005**: 90% of preview users can successfully navigate the authentication flow explanation
- **SC-006**: Chat preview responses match actual app functionality; users report no significant surprise between preview and real app (survey)
- **SC-007**: Mobile traffic shows >80% successful rendering (no layout issues or crashes)

---

## Assumptions

- **Hosting**: Preview is web-based and hosted on the main intervals.icu website or a dedicated preview domain (intervals-preview.icu or similar)
- **Sample Data**: A static dataset of realistic (anonymized) training data is used for demo queries; no live API calls required
- **Response Simulation**: Responses can be pre-recorded or templated; Claude API calls are not required for preview
- **Download Links**: Preview has prominent, non-intrusive links to .dmg (macOS) and Windows installer download pages
- **Analytics**: Preview tracking is implemented to measure engagement and conversion impact
- **Maintenance**: Preview is updated when UI changes; sample responses remain realistic and aligned with current app behavior
- **Scope**: Video tours and 3D walkthroughs are out of scope for v1; static visuals and light interactive components are acceptable
- **Security**: No real user data, API keys, or intervals.icu credentials are used in the preview environment

---

## Out of Scope

- Live API integration with the demo preview
- Persistent user accounts or login in the preview
- Real-time data sync with intervals.icu
- Video tutorials or screen recordings (covered separately in marketing)
- Mobile app preview (desktop .dmg/.exe only; mobile support is future work)
