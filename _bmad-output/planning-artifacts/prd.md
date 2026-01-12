---
stepsCompleted: [1, 2, 3, 4, 6, 7, 8, 9, 10, 11]
inputDocuments:
  - path: '_bmad-output/analysis/brainstorming-session-2026-01-10.md'
    type: 'brainstorming'
  - path: 'https://docs.novahunting.ai/'
    type: 'external-documentation'
workflowType: 'prd'
lastStep: 6
documentCounts:
  briefs: 0
  research: 0
  brainstorming: 1
  projectDocs: 1
---

# Product Requirements Document - nova_claude_code_protector

**Author:** Fr0gger
**Date:** 2026-01-10

## Executive Summary

NOVA Claude Code Protector is a standalone security and observability tool for Claude Code users. It addresses a critical gap in AI-assisted development: **visibility and protection during autonomous code execution**.

As AI coding assistants gain more autonomy - reading files, executing commands, editing code - the need for comprehensive audit trails and real-time security becomes essential. NOVA Claude Code Protector solves this with two integrated capabilities:

1. **Session Tracing** - Captures every Claude Code action in detail: tool calls, inputs, outputs, timing, and context. Generates interactive HTML reports for investigation, audit, and review.

2. **Security Protection** - Integrates NOVA's prompt pattern matching to detect injection attacks, malicious prompts, and suspicious behavior during execution. Provides real-time verdicts (allowed/warned/blocked) inline with the session trace.

**Target Users:** Claude Code users and Security Analysts who need complete visibility into AI-assisted development sessions.

### What Makes This Special

> "You wouldn't fly a plane without a black box. Why run AI without one?"

NOVA Claude Code Protector is the **first dedicated tool combining execution tracing with security protection for AI coding assistants**. While other tools focus on prompt safety or output filtering, this captures the complete picture - every action, every decision, with security verdicts inline.

The result: A human-readable timeline that answers "what did Claude do?" and "was any of it suspicious?" in seconds.

## Project Classification

| Attribute | Value |
|-----------|-------|
| **Technical Type** | CLI Tool (Claude Code hooks integration) |
| **Domain** | AI Security & Observability |
| **Complexity** | Medium |
| **Project Context** | Standalone product (leverages NOVA framework) |
| **Primary Users** | Claude Code users, Security Analysts |

## Success Criteria

### User Success

| Criteria | Measure |
|----------|---------|
| **Real-time Protection** | Attacks/exploits blocked or flagged during Claude Code session |
| **Complete Visibility** | Every step reviewable in final HTML report |
| **10-Second Understanding** | User sees health badge + AI summary and knows session status immediately |
| **Investigation Efficiency** | Security analyst can identify suspicious events within 30 seconds via timeline |

**Success Moments:**
1. Attack attempt → NOVA blocks/flags → user protected without manual intervention
2. Session ends → report auto-generates → complete audit trail available
3. Compliance request → report provides timestamped evidence of all AI actions

### Business Success

| Criteria | Measure |
|----------|---------|
| **Distribution** | Open source (MIT license) |
| **Goal** | Thought leadership + training promotion |
| **Visibility** | GitHub stars, social shares, security community mentions |
| **Credibility** | First-mover positioning on Claude Code security tooling |
| **Funnel** | NOVA users → recognize expertise → training signups |

**Success = Fr0gger recognized as the AI Security expert for agentic coding tools.**

### Technical Success

| Criteria | Measure |
|----------|---------|
| **Performance** | ~1ms overhead per event capture |
| **Accuracy** | Zero gaps - every tool call captured |
| **Reliability** | Report generation never fails on session exit |
| **Integration** | Seamless Claude Code hooks installation |

### Measurable Outcomes

- [ ] 100% of Claude Code tool calls captured with full context
- [ ] NOVA verdicts (allowed/warned/blocked) attached to every scanned event
- [ ] HTML report generates automatically on every session exit
- [ ] User can identify flagged events within 10 seconds of opening report

## Product Scope

### MVP - Minimum Viable Product

| Feature | Rationale |
|---------|-----------|
| Complete event capture (10 fields) | Foundation - timestamps, tool name, inputs, outputs |
| NOVA integration inline (7 fields) | Security verdicts per event |
| JSON → HTML pipeline | Core architecture |
| Visual timeline | Instant comprehension |
| Click-to-expand events | Progressive disclosure |
| AI summary | 10-second understanding |
| Auto-generate on exit | Zero friction |
| Color coding + icons | Visual scanning |

### Growth Features (Post-MVP)

| Feature | Rationale |
|---------|-----------|
| Filter by tool/status | Investigation efficiency |
| Search functionality | Find specific content |
| Copy as JSON | Power user export |

### Vision (Future)

| Feature | Rationale |
|---------|-----------|
| Checksum integrity | Compliance hardening |
| Session diff/comparison | Advanced analysis |
| Replay mode | Step-by-step review |

## User Journeys

### Journey 1: Alex Chen - The Security Analyst Who Catches the Attack

Alex is a security analyst at a mid-size tech company that recently adopted Claude Code for their engineering team. His job is to ensure AI-assisted development doesn't introduce vulnerabilities or become a vector for attacks. He's been burned before - a prompt injection in a competitor's AI tool led to leaked credentials. He's paranoid, and rightfully so.

One Tuesday morning, Alex gets an alert from NOVA Claude Code Protector: a session was flagged with a **BLOCKED** verdict. His heart rate spikes. He opens the HTML report and immediately sees the red health badge at the top: "1 BLOCKED, 2 WARNED."

He scrolls to the AI summary: *"Session attempted to read ~/.ssh/id_rsa after processing a file containing embedded instructions. NOVA blocked the read operation based on rule 'credential_exfiltration'."*

Within 30 seconds, Alex knows exactly what happened. He clicks the timeline, expands the blocked event, and sees the full context - the malicious file that triggered it, the prompt injection attempt, and NOVA's real-time intervention. He exports the JSON, attaches it to his incident report, and forwards it to the dev team lead.

**The attack was stopped. The evidence is complete. Alex looks like a hero.**

---

### Journey 2: Maya Rodriguez - The Developer Who Needs to Know What Claude Did

Maya is a senior developer who uses Claude Code daily. She loves the productivity boost - what used to take hours now takes minutes. But sometimes Claude makes changes she doesn't fully understand, and her code reviews are getting questions she can't answer: "Why did Claude structure it this way?" "What files did it touch?"

After a particularly complex refactoring session, Maya's PR gets pushback. A teammate asks: "Did Claude actually run the tests, or did it just say it would?" Maya realizes she doesn't know. She trusted Claude, but she can't prove what happened.

She installs NOVA Claude Code Protector. The next day, she finishes a feature implementation and opens the auto-generated report. The AI summary tells her: *"Session completed 47 tool calls over 12 minutes. Modified 8 files, ran test suite twice (all passed), created 2 new files."*

She scrolls the visual timeline - every Read, Edit, Bash command is there. She clicks on the test execution, sees the full output. She copies the report link and drops it in her PR: "Full session trace attached."

**Her code review is approved in record time. She finally has receipts.**

---

### Journey 3: David Park - The Compliance Officer Who Needs Proof

David works in a regulated fintech company. His nightmare scenario: an auditor asks "Can you prove your AI coding assistant didn't access customer data?" and he has nothing to show. The company adopted Claude Code six months ago, and David has been pushing for better governance ever since.

When he hears about NOVA Claude Code Protector, he immediately sees the value. This isn't just security - it's **evidence**. Every AI action, timestamped, with full context.

During the quarterly audit, the external auditor asks the dreaded question: "How do you ensure AI-assisted development follows your data access policies?" David pulls up the reports folder. He shows the auditor a sample session report - the timeline, the NOVA verdicts, the complete trail.

The auditor is impressed: "This is better than what I see at most companies for *human* developers." David walks them through how NOVA rules enforce the company's security policies in real-time, and how every blocked or warned action is logged.

**The audit passes. David's months of advocacy paid off. He gets budget for security training - from Fr0gger, naturally.**

---

### Journey 4: Sam Torres - The Curious User Who Just Wants to Understand

Sam is a junior developer, three months into their first job. They're using Claude Code because everyone on the team does, but honestly? It feels like magic. Claude reads files, writes code, runs commands - and Sam just... trusts it. They don't really know what's happening under the hood.

One day, Sam's mentor says: "You should understand what your tools are doing. Install this." It's NOVA Claude Code Protector.

After their next Claude session, Sam opens the HTML report expecting a wall of text. Instead, they see a clean health badge (all green), a friendly AI summary: *"Session helped refactor the user authentication module. Read 6 files, edited 3, ran tests successfully."*

Sam clicks around. The visual timeline shows the flow - oh, *that's* why Claude read the config file first. The click-to-expand reveals the actual prompts and outputs. It's like watching a replay of the session.

For the first time, Sam understands the "magic." They start noticing patterns - how Claude approaches problems, which files it checks first, how it validates its work. They're not just using AI anymore. They're *learning* from it.

**Sam goes from "I hope this works" to "I know what this did." That's the real unlock.**

---

### Journey Requirements Summary

| Journey | Key Capabilities Required |
|---------|---------------------------|
| **Alex (Security Analyst)** | Real-time blocking, alert notifications, health badge, NOVA verdicts, JSON export, incident-ready evidence |
| **Maya (Developer)** | Auto-generated reports, AI summary, visual timeline, click-to-expand details, shareable report links |
| **David (Compliance Officer)** | Complete audit trail, timestamps, policy enforcement logging, auditor-friendly presentation |
| **Sam (Curious User)** | Clean UI, progressive disclosure, educational value, session replay understanding |

**Cross-Journey Requirements:**
- Health badge for instant status
- AI summary for 10-second understanding
- Visual timeline for flow comprehension
- Click-to-expand for progressive disclosure
- Color coding for severity (green/amber/red)
- JSON export for integration/evidence

## Innovation & Novel Patterns

### Core Innovation: Simple AI Agent Governance

NOVA Claude Code Protector challenges the assumption that AI governance must be complex, enterprise-grade, and difficult to implement. The innovation is **accessibility through simplicity**.

**Innovation Thesis:** Anyone using Claude Code should be able to protect and monitor their AI agent with minimal effort - not just organizations with dedicated security teams.

### What Makes This Novel

| Aspect | Traditional Approach | NOVA Claude Code Protector |
|--------|---------------------|---------------------------|
| **Setup** | Complex enterprise deployment | Single install script |
| **Configuration** | Extensive policy configuration | Works out of the box |
| **Target Audience** | Security teams at large orgs | Individual developers + analysts |
| **Integration** | API wrappers, proxies, middleware | Native Claude Code hooks |
| **Output** | Dashboards, logs, SIEMs | Human-readable HTML reports |

### Market Position

**First mover in "simple AI agent security"** - while others build platforms, we build a tool that just works.

### Validation Approach

- **Adoption metric:** GitHub stars and installs indicate resonance
- **Community signal:** Security community sharing and discussion
- **Qualitative:** Developer testimonials on ease of use

### Risk Mitigation

If the combined tracing + security approach doesn't resonate:
- **Fallback 1:** Ship security (NOVA protection) and tracing (reports) as separate tools
- **Fallback 2:** Focus on one use case (e.g., security-only) based on adoption signals

## CLI Tool Specific Requirements

### Interaction Model: Zero-Touch Automation

NOVA Claude Code Protector operates as a **fully automated hooks-based system** with no direct CLI interaction required during normal operation.

| Phase | Trigger | Action | User Involvement |
|-------|---------|--------|------------------|
| **Session Start** | Claude Code launches | Hooks activate, tracing begins | None (automatic) |
| **During Session** | Each tool call | Event captured, NOVA scans executed | None (background) |
| **Session Exit** | Claude Code exits | JSON finalized, HTML report generated | None (automatic) |
| **Post-Session** | User decision | Open HTML report to review | View/investigate |

### Command Structure

**No direct CLI commands required for normal operation.**

Installation is the only user action: `./install.sh`

### Output Formats

| Format | Purpose | When Generated |
|--------|---------|----------------|
| **JSON** | Session data (append-only during session) | Real-time during session |
| **HTML** | Human-readable interactive report | On session exit |

### Configuration Schema

| Config File | Location | Purpose |
|-------------|----------|---------|
| **Claude Code hooks** | `~/.claude/settings.json` | Register hooks with Claude Code |
| **NOVA rules** | `rules/*.nov` | Define security detection patterns |
| **Tool config** | `config/nova-protector.yaml` (optional) | Override defaults |

### Hooks Integration

| Hook Type | Trigger | Action |
|-----------|---------|--------|
| **PreToolUse** | Before each tool call | (Optional) Pre-scan if needed |
| **PostToolUse** | After each tool call | Capture event + NOVA scan + log verdict |
| **Stop** | Session exit | Generate HTML report from JSON |

### Scripting Support

- **Programmatic access:** Python API for custom integrations
- **Report location:** Predictable path (`~/.nova-protector/reports/`)
- **Exit codes:** For CI/CD integration (0 = clean, 1 = warnings, 2 = blocked)

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Problem-Solving MVP - Solve the core protection and visibility problem with minimal, reliable features.

**Strategic Rationale:**
- First-mover advantage requires speed to market
- Open source adoption grows from "it just works"
- Validation comes from real users, not feature speculation
- Thought leadership established by shipping, not planning

**Resource Requirements:** Solo developer can ship MVP; complexity is in integration, not scale.

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**

| Journey | MVP Support Level |
|---------|------------------|
| Alex (Security Analyst) | Full - Health badge, NOVA verdicts, timeline flags |
| Maya (Developer) | Full - AI summary, timeline, click-to-expand |
| David (Compliance) | Full - Complete audit trail with timestamps |
| Sam (Curious User) | Full - Progressive disclosure UI |

**Must-Have Capabilities (v1):**

| Capability | Rationale |
|------------|-----------|
| Complete event capture (10 fields) | Foundation - without this, nothing else matters |
| NOVA integration inline (7 fields) | Security verdicts per event - the "Guard" in "Flight Recorder + Security Guard" |
| JSON → HTML pipeline | Core architecture enabling human-readable output |
| Visual timeline | Instant comprehension of session flow |
| Click-to-expand events | Progressive disclosure for all personas |
| AI summary | 10-second understanding promise delivered |
| Auto-generate on exit | Zero friction - the "zero-touch" commitment |
| Color coding + icons | Visual scanning efficiency |

### Post-MVP Features

**Phase 2 - Growth (Should Have):**

| Feature | Rationale |
|---------|-----------|
| Filter by tool/status | Investigation efficiency for power users |
| Search functionality | Find specific content in large sessions |
| Copy as JSON | Power user export for integration |

**Phase 3 - Expansion (Nice to Have):**

| Feature | Rationale |
|---------|-----------|
| Checksum integrity | Compliance hardening for regulated industries |
| Session diff/comparison | Advanced analysis for recurring patterns |
| Replay mode | Step-by-step review for training/debugging |

### Risk Mitigation Strategy

**Technical Risks:**

| Risk | Mitigation |
|------|------------|
| Claude Code hook API changes | Design for graceful degradation; monitor Anthropic announcements |
| Performance overhead > 1ms | Profile early; JSON append is fast; optimize HTML generation as separate process |
| NOVA pattern matching accuracy | Leverage existing NOVA rules; false positives preferable to missed attacks |

**Market Risks:**

| Risk | Mitigation |
|------|------------|
| Claude Code market share shrinks | Architecture extensible to other AI coding assistants |
| Competing tools emerge | First-mover + open source = community moat |
| Users don't care about tracing | Security angle is primary; tracing is bonus value |

**Resource Risks:**

| Risk | Mitigation |
|------|------------|
| Less time than planned | MVP scope already minimal; could ship without AI summary |
| Maintenance burden | Open source community contributions; minimal surface area |

### Out of Scope (Explicit Exclusions)

- Multi-user/team features (this is individual tooling)
- Cloud storage/sync (reports are local)
- Real-time dashboards (HTML reports are sufficient for v1)
- Support for other AI assistants (Claude Code only in MVP)
- Custom rule authoring UI (use NOVA directly)

## Functional Requirements

### Session Tracing

- FR1: System can capture every Claude Code tool call during a session
- FR2: System can record timestamp (start, end, duration) for each tool call
- FR3: System can capture complete tool input for each tool call
- FR4: System can capture complete tool output for each tool call
- FR5: System can assign sequential identifiers to maintain event order
- FR6: System can record the tool name for each captured event
- FR7: System can capture working directory context for relevant operations
- FR8: System can identify file paths accessed or modified during tool calls
- FR9: System can store captured events in append-only JSON during session

### Security Protection

- FR10: System can scan tool inputs against NOVA security rules
- FR11: System can scan tool outputs against NOVA security rules
- FR12: System can assign a verdict (allowed/warned/blocked) to each scanned event
- FR13: System can assign severity level to flagged events
- FR14: System can record which NOVA rules matched for each flagged event
- FR15: System can record scan timing for performance monitoring
- FR16: System can block tool execution when NOVA rules detect critical threats (PreToolUse hook)

### Report Generation

- FR17: System can automatically generate HTML report when Claude Code session exits
- FR18: System can convert session JSON to human-readable HTML format
- FR19: System can generate AI summary describing session purpose and key actions
- FR20: System can calculate aggregate statistics (total events, tools used, files touched)
- FR21: System can save reports to predictable location for easy retrieval
- FR22: System can include session metadata (platform, NOVA version, timestamps) in report

### Report Viewing - Overview

- FR23: User can view health badge showing session security status at a glance
- FR24: User can read AI summary to understand session in 10 seconds
- FR25: User can see count of warnings and blocked events immediately
- FR26: User can identify session duration and event count from report header

### Report Viewing - Timeline & Navigation

- FR27: User can view visual timeline showing session flow chronologically
- FR28: User can click timeline nodes to navigate to specific events
- FR29: User can scan timeline to identify flagged events visually (color coding)
- FR30: User can see tool icons indicating event types in timeline

### Report Viewing - Event Details

- FR31: User can expand events to reveal full details (input, output, NOVA verdict)
- FR32: User can collapse events to maintain clean overview
- FR33: User can view NOVA verdict details for flagged events (rules matched, severity)
- FR34: User can view complete tool input/output for investigation

### Report Viewing - Visual Design

- FR35: User can distinguish event severity via color coding (green/amber/red)
- FR36: User can identify tool types via icons (Read, Edit, Bash, etc.)
- FR37: User can view timestamps for each event in the timeline

### Installation & Configuration

- FR38: User can install system via single install script
- FR39: System can automatically register hooks with Claude Code settings
- FR40: System can operate with zero configuration for default use case
- FR41: User can customize report output location via configuration file (optional)
- FR42: User can add custom NOVA rules to extend security coverage

## Non-Functional Requirements

### Performance

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| Event capture overhead | < 1ms per tool call | Must be imperceptible during Claude Code usage |
| NOVA scan time | < 5ms per event | Security scanning cannot slow down development flow |
| JSON append operation | < 0.5ms per write | File I/O must not block tool execution |
| HTML report generation | < 3 seconds for 500 events | User should not wait long for report after session |
| Memory footprint | < 50MB during session | Tool runs in background; must not compete with Claude Code |

**Performance Philosophy:** The tool must be "invisible" during normal operation. Users should never notice performance impact from tracing or security scanning.

### Security

| Requirement | Specification |
|-------------|---------------|
| Report sensitivity | Reports are treated as sensitive artifacts (contain full session data) |
| Storage location | Reports stored in user-controlled directory with standard file permissions |
| No external transmission | All processing is local; no data leaves the user's machine |
| Credential handling | Tool does not store or manage credentials; uses existing NOVA installation |
| Report lifecycle | Users responsible for securing/deleting reports containing sensitive data |

**Security Philosophy:** The tool captures everything for investigation purposes. This means reports may contain sensitive data (file contents, command outputs). Users must treat reports as confidential artifacts.

### Reliability

| Requirement | Target |
|-------------|--------|
| Event capture rate | 100% - zero gaps in session recording |
| Report generation success | 100% - must never fail on session exit |
| Graceful degradation | If NOVA scan fails, event is logged with "scan_failed" status (not lost) |
| Hook registration | Must survive Claude Code updates when possible |
| Error recovery | Corrupted session JSON should not prevent partial report generation |

**Reliability Philosophy:** The "black box" analogy means we cannot afford data loss. Every event must be captured, and a report must always be generated - even if partial.

### Integration

| Requirement | Specification |
|-------------|---------------|
| Claude Code hooks | Compatible with official hooks API (PreToolUse, PostToolUse, Stop) |
| NOVA framework | Uses NOVA Python package for pattern matching |
| Installation method | Single script modifies `~/.claude/settings.json` to register hooks |
| Uninstallation | Clean removal script restores original Claude Code settings |
| Update path | Hook scripts can be updated independently of Claude Code |

**Integration Philosophy:** Tight integration with Claude Code hooks is the only external dependency. The tool must work with whatever version of Claude Code the user has, and fail gracefully if hooks API changes.

### Compatibility

| Requirement | Specification |
|-------------|---------------|
| Operating systems | macOS (primary), Linux (supported), Windows (best effort) |
| Python version | Python 3.9+ |
| Claude Code version | Compatible with current stable release |
| Browser support | HTML reports viewable in any modern browser (Chrome, Firefox, Safari, Edge)
