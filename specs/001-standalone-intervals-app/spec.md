# Feature Specification: Standalone intervals.icu + Claude Desktop Application

**Feature Branch**: `001-standalone-intervals-app`

**Created**: 2026-06-16

**Status**: Draft

**Input**: User description: "I want to build an application that runs this mcp server with Claude as a standalone application for users to interact with intervals.icu on their local machine."

## Clarifications

### Session 2026-06-16

- Q: Update Mechanism & Frequency → A: Scheduled checks with user prompts (daily by default; user can defer)


## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install and Launch Application (Priority: P1)

Users need a simple, self-contained way to install the application on their local machine without requiring command-line expertise or manual configuration. The application should launch with minimal setup and be ready to use immediately after installation.

**Why this priority**: P1 is the critical blocking requirement. Without a working installation and launch mechanism, users cannot access any other functionality. This forms the foundation of the entire standalone application.

**Independent Test**: "Can be fully tested by: downloading the installer, following installation instructions, and launching the app to see the login screen. Delivers: a running application ready to accept user input."

**Acceptance Scenarios**:

1. **Given** a user on macOS without the app installed, **When** they download and run the installer, **Then** the application installs to their Applications folder with no errors
2. **Given** a user on Windows without the app installed, **When** they download and run the installer, **Then** the application installs to their Program Files folder with no errors
3. **Given** the application is installed, **When** the user launches it, **Then** it starts within 3 seconds and displays the main UI (login or home screen)
4. **Given** the application is launched, **When** the user closes it, **Then** the process terminates cleanly with no orphaned processes

---

### User Story 2 - Authenticate with intervals.icu API (Priority: P1)

Users must authenticate their intervals.icu API key to access their personal training data. The authentication process should be secure, simple, and guide users through obtaining their API key if they don't have one.

**Why this priority**: P1 is required for MVP. Without authentication, users cannot connect to their intervals.icu account and no data can be retrieved. This is the second critical blocker.

**Independent Test**: "Can be fully tested by: entering a valid API key, seeing successful authentication, and being able to query training data. Also test invalid keys and see appropriate error messages. Delivers: authenticated access to user's intervals.icu account."

**Acceptance Scenarios**:

1. **Given** the application is running and unauthenticated, **When** user enters their intervals.icu API key, **Then** the application validates it against the intervals.icu API and displays success
2. **Given** user enters an invalid API key, **When** they try to authenticate, **Then** they see a clear error message and guidance on how to obtain a valid key
3. **Given** user is authenticated, **When** they close and reopen the app, **Then** they remain authenticated (credentials securely stored)
4. **Given** user is authenticated, **When** they click "Logout", **Then** they are logged out and credentials are removed

---

### User Story 3 - Query Training Data via Claude Conversation (Priority: P1)

Users need to interact with their intervals.icu training data using natural language through Claude. They should be able to ask questions about workouts, athletes, wellness metrics, and receive Claude's analysis and insights—all without learning a query language or API syntax.

**Why this priority**: P1 is the core value proposition. This is what differentiates the standalone app from manual API access. Users launch the app specifically to have Claude analyze their training data.

**Independent Test**: "Can be fully tested by: entering a natural language query (e.g., 'How are my athletes performing this week?'), and receiving Claude's response with relevant training data. Delivers: functional natural language interface to training data."

**Acceptance Scenarios**:

1. **Given** user is authenticated, **When** they type "Show me my recent workouts", **Then** Claude retrieves workouts and provides a natural language summary
2. **Given** user asks "Which of my athletes has the highest training load this week?", **When** Claude processes the query, **Then** Claude retrieves athlete and training data and answers the question
3. **Given** user asks a question about data they don't have access to, **When** Claude processes it, **Then** Claude gracefully indicates that the data is unavailable rather than erroring
4. **Given** the conversation history exists, **When** user asks a follow-up question, **Then** Claude maintains conversation context and provides coherent responses

---

### User Story 4 - Manage Application Settings (Priority: P2)

Users may need to update settings such as their API key, change authentication, enable/disable features, or view logs for troubleshooting. A settings panel provides centralized access to configuration without modifying files manually.

**Why this priority**: P2 enhances usability and flexibility. Users can change their API key without reinstalling, and troubleshoot issues independently. Not required for MVP but important for a complete product.

**Independent Test**: "Can be fully tested by: navigating to settings, changing an API key, updating preferences, and verifying changes persist. Delivers: functional settings management UI."

**Acceptance Scenarios**:

1. **Given** user is in the main application, **When** they navigate to Settings, **Then** they see options for API key, preferences, and logs
2. **Given** user is in Settings and enters a new API key, **When** they save, **Then** the new key is validated and the app re-authenticates
3. **Given** user views application logs, **When** an error occurs, **Then** logs contain sufficient detail to troubleshoot the issue

---

### User Story 5 - Receive Contextual Help and Guidance (Priority: P2)

Users may encounter unfamiliar workflows or need guidance on how to interact with the application. Contextual help, tooltips, and a user guide ensure users can self-serve and reduce support burden.

**Why this priority**: P2 improves user experience and reduces support load. Users can navigate the app independently and understand available features without asking for help.

**Independent Test**: "Can be fully tested by: hovering over UI elements to see tooltips, accessing the help menu, and finding clear documentation. Delivers: discoverable, self-service help."

**Acceptance Scenarios**:

1. **Given** user hovers over an input field, **When** they pause, **Then** a tooltip appears explaining the field's purpose
2. **Given** user is lost in the application, **When** they click "Help", **Then** they see a user guide or FAQ relevant to their current context
3. **Given** user encounters an error, **When** the error message appears, **Then** it includes a link to documentation or support

---

### Edge Cases

- What happens when the user's intervals.icu API key expires or is revoked? (Application should detect and prompt for re-authentication)
- How does the application handle network interruptions during Claude API calls? (Graceful retry with user notification)
- What if the user closes Claude Desktop while the MCP server is running in the standalone app? (Server continues running; user receives clear indication of connection status)
- What happens if the user tries to run multiple instances of the application? (Should either prevent duplicate instances or manage them gracefully)
- How does the application handle extremely large training datasets? (Should paginate or summarize rather than overwhelming the UI)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Application MUST bundle the MCP server as a local service that runs on the user's machine
- **FR-002**: Application MUST securely store and validate the user's intervals.icu API key
- **FR-003**: Application MUST provide a conversational interface that sends user queries to Claude Desktop and displays Claude's responses
- **FR-004**: Application MUST handle authentication errors gracefully and guide users to obtain valid API credentials
- **FR-005**: Application MUST maintain authentication state across application restarts (credentials stored securely)
- **FR-006**: Application MUST support querying all intervals.icu API endpoints (athletes, workouts, wellness, library, goals, etc.)
- **FR-007**: Application MUST include a settings panel for managing API key, preferences, and viewing logs
- **FR-008**: Application MUST detect and display the connection status between the local MCP server and Claude Desktop
- **FR-009**: Application MUST handle network errors (timeouts, disconnections) gracefully without crashing
- **FR-010**: Application MUST provide clear, actionable error messages to users when failures occur
- **FR-011**: Application MUST log errors and events for troubleshooting (accessible via settings panel)
- **FR-012**: Application MUST support automatic updates to incorporate new features and security fixes. Update strategy: Scheduled checks with user prompts (daily by default); users can defer updates. Update mechanism: app checks for updates daily and notifies the user with an option to install now or defer.
- **FR-013**: Application MUST work on [NEEDS CLARIFICATION: specific operating systems - macOS and Windows minimum, or include Linux?]
 - **FR-013**: Application MUST work on macOS and Windows (initial v1 targets). Linux support may be considered in later releases.

### Key Entities

- **User Account**: Represents an authenticated user with a valid intervals.icu API key; stores credentials securely and tracks authentication state
- **Training Session**: Represents a single workout or training event with metadata (date, duration, athlete, training zone, etc.)
- **Athlete Profile**: Represents an individual athlete with performance metrics, training history, and wellness data
- **Conversation**: Represents the chat history between user and Claude within a single application session; includes queries, responses, and context

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can install and launch the application without command-line interaction; average installation time is under 2 minutes
- **SC-002**: Users can authenticate with their intervals.icu API key in under 30 seconds
- **SC-003**: Claude responds to user queries about training data in under 5 seconds (p95 latency from user query to response displayed)
- **SC-004**: 95% of natural language queries about training data receive coherent, accurate responses from Claude
- **SC-005**: Application uptime is 99.5% for authenticated users (excluding scheduled maintenance)
- **SC-006**: Users report satisfaction with the natural language interface; 80% of surveyed users find it intuitive
- **SC-007**: Application supports at least macOS and Windows (minimum OS versions [NEEDS CLARIFICATION: which versions?])
 - **SC-007**: Application supports at least macOS and Windows (v1 targets). Minimum versions to be confirmed in clarifications.
- **SC-008**: The MCP server and application together handle 10k+ training records without performance degradation

## Assumptions

- **User Environment**: Users have stable internet connectivity to reach Claude API and intervals.icu API endpoints
- **Platform Support**: Desktop platforms (macOS, Windows) are the initial target; mobile/web are out of scope for v1
- **Authentication Method**: Users already have an intervals.icu API key; the application guides them to obtain one if missing
- **Security Storage**: The local machine is assumed to be trusted; credentials are stored in the system's native secure storage (Keychain on macOS, Credential Manager on Windows)
- **Claude Desktop Integration**: Users have Claude Desktop installed and configured; the application requires Claude Desktop's MCP server capabilities to function
- **Data Sensitivity**: User training data is treated as sensitive and is processed locally; no training data is sent to external servers except as required by intervals.icu and Claude APIs
- **Scope Boundaries**: Real-time synchronization with intervals.icu and push notifications are out of scope for v1; polling-based data fetching is acceptable
- **Update Mechanism**: The application can automatically check for updates; update delivery is via standard OS app update mechanisms (App Store for macOS, installer for Windows, or similar)
