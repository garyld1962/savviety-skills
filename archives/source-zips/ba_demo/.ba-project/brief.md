# Project Brief — Technical Debt Tracker

**Type:** Living document
**Purpose:** Accumulated output from the BA Process Pipeline.

---

## === PROJECT BRIEF ===

### SECTION 0: PROCESS METADATA

**Project Name:** Technical Debt Tracker
**Date Created:** 2026-03-13
**Last Updated:** 2026-03-13
**Current Phase:** 1
**Brief Version:** 1.0

**Phase Tracker:**
| Phase | Status | Date Started | Date Completed | Notes |
|-------|--------|-------------|----------------|-------|
| 1. Problem Statement & Thesis | Complete | 2026-03-13 | 2026-03-13 | Thesis formed, 3 alternatives |
| 2. Stakeholders & Context | Not Started | | | |
| 3. Current State & Gaps | Not Started | | | |
| 4. Requirements Definition | Not Started | | | |
| 5. Validation & Constraints | Not Started | | | |
| 6. Solution & Business Case | Not Started | | | |

**Session Log:**
| Session # | Date | Phase(s) Covered | Key Decisions | AI Tool Used |
|-----------|------|-----------------|---------------|-------------|
| 1 | 2026-03-13 | Phase 1 | | GitHub Copilot |

**Cross-Phase Open Questions:**
_(none yet)_

---

### SECTION 1: PROBLEM STATEMENT & THESIS
*Filled by: Phase 1 — Problem Statement & Thesis skill*

**1.1 Original Problem (as stated)**

> From: Sarah Chen, VP of Engineering Operations
>
> We need a way to get technical debt under control across the organization. Right now every BU and team tracks it differently — some use spreadsheets, some use Jira labels, some don't track it at all. Leadership keeps asking how much tech debt we have and what it's costing us, and we can't answer that confidently.
>
> What we need is an application that gives us: a central inventory of technical debt items across all BUs and teams, BU/team filtering, prioritization based on risk/cost/impact, risk assessment, cost estimation, mitigation planning, and scheduling/assignment. The VP of Engineering and CTO have flagged this as a Q3 priority. We've been burned twice this year by outages traced to known tech debt nobody was tracking centrally — the last incident cost ~$200K in lost revenue and took 3 teams offline for a week. Several teams want to buy off the shelf; others want to build internally. Need adoption across 8 BUs and ~40 engineering teams.

**1.2 Refined Problem Statement**

CURRENT STATE:
Technical debt is tracked inconsistently across 8 BUs and ~40 engineering teams — some use spreadsheets, some use Jira labels, most don't track at all. There is no standardized process for identifying, categorizing, scoring, or surfacing debt. This was historically tolerable because tech debt was a local team concern. A recent organizational restructuring now requires more cross-team collaboration, exposing inter-team debt dependencies that no single team can see or manage. Leadership cannot answer "how much tech debt do we have" or "what is it costing us."

IMPACT:
- **Financial:** At least ~$400K in lost revenue this year from 2 debt-related outages; true cost likely higher when including engineering time for incident response
- **Operational:** Cross-team projects are at risk of delays from unknown tech debt in dependent systems; engineering time spent on ad-hoc tracking across inconsistent systems
- **Risk:** Unknown exposure — the organization cannot assess which debt items are high-risk because there is no consistent risk scoring or cross-BU visibility
- **Strategic:** The recent reorg promoting cross-team work has made this a structural risk, not just a local nuisance

DESIRED FUTURE STATE:
A standardized, organization-wide system for inventorying, scoring, prioritizing, and scheduling tech debt remediation — with BU/team-level views for teams and executive dashboards for leadership. Teams dedicate 5-10% of sprint capacity to debt remediation. The CTO can answer debt exposure questions from a dashboard in under 5 minutes. Debt-related outages that could have been predicted are eliminated.

AFFECTED STAKEHOLDERS:
- **Decision authority:** CTO, VP of Engineering, Sarah Chen (VP Eng Ops)
- **Directly affected:** ~40 engineering team leads and their teams across 8 BUs
- **Beneficiaries:** Leadership (visibility), cross-team project managers (risk reduction), individual teams (structured remediation time)
- **Potential data consumers:** SecOps (for security-related debt), project managers for cross-team initiatives

SCOPE BOUNDARIES:
- **In scope:** Central debt inventory, BU/team filtering, risk/cost/impact scoring, prioritization, mitigation planning, scheduling, assignment, executive dashboard, export to ADO sprint boards
- **Out of scope:** Automated debt detection from code (static analysis), remediation execution, non-engineering debt (process debt, organizational debt), integration with tools beyond ADO
- **TBD:** Build vs. buy decision (to be evaluated in Phase 6)

**1.3 Root Cause Hypothesis (Thesis)**

We believe the organization cannot manage technical debt effectively because debt has historically been treated as a local team concern with no standardized process for identification, scoring, or cross-BU visibility — and cross-team project dependencies have now made this an organizational-level risk that no single team can manage alone.

Test criteria: Verify that teams with existing local tracking still experience debt-related project delays when working cross-team (proving that local tracking alone is insufficient).

Invalidation criteria: If teams with strong local tracking processes rarely experience cross-team debt impacts — meaning the problem is isolated to teams that don't track at all, and the fix is adoption enforcement rather than centralized tooling + process.

**1.4 Alternative Hypotheses**
| # | Alternative Explanation | Supporting Evidence | Likelihood |
|---|------------------------|--------------------|-----------:|
| 1 | It's a prioritization problem — teams know about debt but can't get capacity because feature work always wins. A tracking tool without executive air cover for remediation time would create a well-documented backlog that never shrinks. | Teams currently dedicate near-zero capacity to debt remediation. | Medium |
| 2 | It's a governance problem — no organizational authority can require teams to report, categorize, or address debt. Without governance, any tool becomes optional and won't get adopted across 40 teams. | No existing standard was ever established; each BU operates independently. | Medium |
| 3 | It's a risk assessment literacy problem — teams create debt but can't accurately assess which items are dangerous. The $200K incidents weren't caused by untracked debt but by debt misjudged as low-risk. | Incident post-mortems may show the debt was known but misclassified. | Low-Medium |

**1.5 Success Metrics**
| Metric | Baseline (Current) | Target | Measurement Method | Timeframe |
|--------|-------------------|--------|-------------------|-----------|
| Debt items tracked centrally | 0% | 90%+ of known debt items | Count in central inventory vs. estimated total | 6 months post-launch |
| Debt-related outages | 2 per year (~$400K+) | 0 predictable debt-related outages | Incident post-mortem classification | 12 months post-launch |
| Cross-team project delays from unknown debt | [TO MEASURE] — newly visible due to reorg | <1 per quarter | Project retrospective tagging | 12 months post-launch |
| Sprint capacity for debt remediation | ~0% | 5-10% of sprint capacity | Sprint planning data from ADO | 6 months post-launch |
| Leadership debt visibility | Cannot answer basic questions | CTO can pull dashboard and answer in <5 min | Stakeholder validation | 3 months post-launch |

**1.6 Assumptions**
| # | Assumption | Impact if Wrong | Validation Method | Status |
|---|-----------|----------------|------------------|--------|
| 1 | Teams will adopt a centralized tool if the process is reasonable and leadership mandates it | Tool becomes shelfware; problem persists | Pilot with 2-3 willing teams before org-wide rollout | Unvalidated |
| 2 | The workload concern is the primary resistance — not philosophical objection to centralized tracking | Need a different change management approach if resistance is deeper | Stakeholder interviews in Phase 2 | Unvalidated |
| 3 | ADO integration (export to sprint boards) is sufficient for scheduling workflow | Teams may need deeper integration or use different tools | Survey of current team tooling in Phase 2 | Unvalidated |
| 4 | A cursory SecOps review is sufficient — no full security audit required | Timeline and budget increase significantly | Confirm with SecOps in Phase 2 | Unvalidated |
| 5 | 5-10% sprint capacity for debt remediation is achievable without executive mandate | Teams won't allocate capacity voluntarily | Requires governance discussion in Phase 2 | Unvalidated |

---

**SECTION 1 QUALITY CHECK:**
- Problem completeness: Strong — quantified impact, clear stakeholders, scope boundaries defined
- Thesis strength: Strong — falsifiable, testable, grounded in organizational context (reorg exposing cross-team dependencies)
- Gaps remaining: Cross-team delay baseline is [TO MEASURE]; full annual cost is estimated from incidents only; alternative hypotheses #1 and #2 (prioritization and governance) are closely related to the thesis and may be co-factors rather than alternatives
- Notable: The original request was solution-prescriptive ("we need an application") — the thesis reframes it as a process + visibility problem that a tool enables but doesn't solve alone

**HANDOFF NOTES FOR PHASE 2:**
- Key stakeholders to investigate: CTO (sponsor), VP Engineering, BU leaders (8), team leads (~40), SecOps, ADO/tooling administrators, cross-team project managers
- Political dynamics to probe: Recent reorg may have created new power structures; BU autonomy vs. centralized mandates; who "owns" tech debt governance
- Critical validation: Is workload truly the only resistance? Are there BUs that would actively resist?
- Domain terminology to capture: How do different BUs define "tech debt"? Is there a shared taxonomy or does each team categorize differently?
- Governance gap: The thesis implies both a tool AND a process. Who will own the process? This is the #1 adoption risk.

---

### SECTION 2: STAKEHOLDERS & CONTEXT
*Filled by: Phase 2 — Stakeholder & Context Discovery skill*

_(not started)_

---

### SECTION 3: CURRENT STATE & GAPS
*Filled by: Phase 3 — Current State & Gap Analysis skill*

_(not started)_

---

### SECTION 4: REQUIREMENTS
*Filled by: Phase 4 — Requirements Definition skill*

_(not started)_

---

### SECTION 5: VALIDATION & CONSTRAINTS
*Filled by: Phase 5 — Validation & Constraints skill*

_(not started)_

---

### SECTION 6: SOLUTION RECOMMENDATION & BUSINESS CASE
*Filled by: Phase 6 — Solution Recommendation & Business Case skill*

_(not started)_
