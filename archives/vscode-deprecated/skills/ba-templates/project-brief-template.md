# Project Brief Template

**Type:** Living document template
**Purpose:** The single growing document that accumulates all output from the BA Process Pipeline. Each phase fills its designated section. The Brief serves as both working document and state transfer mechanism between sessions.
**How to use:** Copy this template at the start of a new project. Each pipeline phase (or its corresponding skill prompt) fills one section. Sections build on each other -- earlier sections provide context for later ones.

---

## === PROJECT BRIEF ===

### SECTION 0: PROCESS METADATA

**Project Name:** [name]
**Date Created:** [date]
**Last Updated:** [date]
**Current Phase:** [1-6 or Complete]
**Brief Version:** [increment on major revisions]

**Phase Tracker:**
| Phase | Status | Date Started | Date Completed | Notes |
|-------|--------|-------------|----------------|-------|
| 1. Problem Statement & Thesis | Not Started | | | |
| 2. Stakeholders & Context | Not Started | | | |
| 3. Current State & Gaps | Not Started | | | |
| 4. Requirements Definition | Not Started | | | |
| 5. Validation & Constraints | Not Started | | | |
| 6. Solution & Business Case | Not Started | | | |

**Session Log:**
| Session # | Date | Phase(s) Covered | Key Decisions | AI Tool Used |
|-----------|------|-----------------|---------------|-------------|
| 1 | | | | |

**Cross-Phase Open Questions:**
[Questions that surfaced in one phase but need resolution in a later phase. Carry forward until resolved.]
- [Phase X → Phase Y] Question: [question] | Status: Open / Resolved in Phase [N]

---

### SECTION 1: PROBLEM STATEMENT & THESIS
*Filled by: Phase 1 -- Problem Statement & Thesis skill*

**1.1 Original Problem (as stated)**
[Paste the original problem description, stakeholder request, or business complaint -- verbatim, unedited]

**1.2 Refined Problem Statement**

CURRENT STATE:
[What is happening today -- specific, evidence-based, quantified where possible]

IMPACT:
[Business cost of the current state -- financial, operational, customer, risk, compliance]

DESIRED FUTURE STATE:
[What "solved" looks like -- specific, measurable, time-bound]

AFFECTED STAKEHOLDERS:
[Who experiences the problem, who benefits from the solution, who has decision authority]

SCOPE BOUNDARIES:
[What's in scope for this initiative and what's explicitly out of scope]

**1.3 Root Cause Hypothesis (Thesis)**
[The testable hypothesis about WHY the problem exists]

We believe [problem] exists because [root cause].

Test criteria: [How we would confirm or disprove this hypothesis]
Invalidation criteria: [What evidence would prove this hypothesis wrong]

**1.4 Alternative Hypotheses**
| # | Alternative Explanation | Supporting Evidence | Likelihood |
|---|------------------------|--------------------|-----------:|
| 1 | | | |
| 2 | | | |
| 3 | | | |

**1.5 Success Metrics**
| Metric | Baseline (Current) | Target | Measurement Method | Timeframe |
|--------|-------------------|--------|-------------------|-----------|
| | | | | |

**1.6 Assumptions**
[Assumptions made during problem definition. Each must be validated before Phase 4.]
| # | Assumption | Impact if Wrong | Validation Method | Status |
|---|-----------|----------------|------------------|--------|
| 1 | | | | Unvalidated |

---

### SECTION 2: STAKEHOLDERS & CONTEXT
*Filled by: Phase 2 -- Stakeholder & Context Discovery skill*

**2.1 Stakeholder Register**
| Name/Role | Category | Interest/Concern | Influence | Stance | Engagement Strategy |
|-----------|----------|------------------|-----------|--------|-------------------|
| | Decision-maker / Affected / Blocker / Beneficiary | | High/Med/Low | Supportive/Neutral/Resistant | |

**2.2 Decision Authority Map**
| Decision Type | Who Decides | Who Must Be Consulted | Who Must Be Informed |
|--------------|-------------|----------------------|---------------------|
| | | | |

**2.3 Organizational Context**
- Industry/Domain: [industry]
- Regulatory environment: [applicable regulations]
- Appetite for change: [high/medium/low + evidence]
- Relevant history: [past projects, failed attempts, organizational changes]
- Culture and decision-making style: [formal/informal, consensus/authority-driven]

**2.4 Domain Glossary**
[Organization-specific terms, acronyms, system names -- only terms that differ from standard meaning or are unique to this context]
| Term | Definition | Notes |
|------|-----------|-------|
| | | |

**2.5 Dependencies**
| Dependency | Type | Owner | Impact on This Project | Status |
|-----------|------|-------|----------------------|--------|
| | Project / System / Vendor / Regulatory | | | |

**2.6 End User Profile**
- Who they are: [description]
- Technical sophistication: [level]
- Experience with the problem domain: [description]
- Current workarounds: [how they cope today]
- Expectations: [what they expect from a solution]

**2.7 Cross-Reference Check**
[Flag if Phase 2 findings challenge anything from Phase 1]
- Scope challenges: [do new stakeholders expand or contract the scope?]
- New problem dimensions: [did stakeholder interviews reveal aspects of the problem not captured in Phase 1?]
- Thesis impact: [does stakeholder context support or challenge the root cause hypothesis?]

---

### SECTION 3: CURRENT STATE & GAPS
*Filled by: Phase 3 -- Current State & Gap Analysis skill*

**3.1 As-Is Process Description**
[How the current process/system/situation works today. Who does what, when, with what tools.]

**3.2 Process Map**
[Step-by-step walkthrough of the current process. Use numbered steps, decision points, and handoffs.]

Step 1: [actor] does [action] using [tool/system]
→ Step 2: [actor] does [action]
→ Decision: [condition]
  → If yes: Step 3a...
  → If no: Step 3b...

**3.3 Pain Points Register**
| # | Pain Point | Who Experiences It | Frequency | Severity | Evidence Type |
|---|-----------|-------------------|-----------|----------|--------------|
| 1 | | | Daily/Weekly/Monthly | High/Med/Low | Data/Observation/Anecdote |

**3.4 Gap Analysis**
| # | Area | Current State | Desired State | Gap | Root Cause of Gap | Priority |
|---|------|--------------|---------------|-----|-------------------|----------|
| 1 | | | | | | |

**3.5 Thesis Checkpoint**
[MANDATORY -- Does the gap analysis support or challenge the Phase 1 hypothesis?]

Thesis from 1.3: "[restate hypothesis]"

Evidence supporting thesis:
- [evidence from gap analysis]

Evidence challenging thesis:
- [evidence from gap analysis]

Verdict: Confirmed / Refined / Needs Revision
[If Refined or Needs Revision, state the updated hypothesis and flag for Phase 1 revisit]

**3.6 Data & Evidence Inventory**
| Claim/Finding | Evidence Type | Source | Confidence | Notes |
|--------------|--------------|--------|------------|-------|
| | Data / Observation / Stakeholder report / Assumption | | High/Med/Low | |

**3.7 Greenfield Adaptation**
[If there is no current state -- e.g., a new product or process -- describe instead:]
- Closest analogous process or system: [what exists that's similar]
- Market/competitor reference: [how others solve this]
- User expectations: [what users expect based on experience elsewhere]

---

### SECTION 4: REQUIREMENTS
*Filled by: Phase 4 -- Requirements Definition skill*

**4.1 Business Objectives**
[Refined from Phase 1 success criteria. Each numbered, measurable, tied to a business outcome.]
| ID | Objective | Metric | Target | Traces to Success Metric |
|----|-----------|--------|--------|------------------------|
| OBJ-001 | | | | 1.5 row # |

**4.2 Functional Requirements**
[For each Phase 3 gap: what capability closes this gap? Area-prefixed IDs.]
| ID | Requirement | Priority | Acceptance Criteria | Traces to Gap | Traces to Objective |
|----|------------|----------|-------------------|---------------|-------------------|
| [AREA]-001 | | Must/Should/Could | | 3.4 row # | OBJ-# |

**4.3 Non-Functional Requirements**
| ID | Category | Requirement | Measurable Threshold | Rationale |
|----|----------|------------|---------------------|-----------|
| NFR-001 | Performance / Security / Usability / Scalability / Availability / Accessibility / Compliance | | | |

**4.4 Business Rules**
| ID | Rule Statement | Classification | Source | Affected Requirements |
|----|---------------|---------------|--------|---------------------|
| BR-001 | | Constraint / Calculation / Condition / Inference / Policy | | [AREA]-# |

**4.5 User Stories / Use Cases**
[For key requirements, provide user stories or use case narratives]

**Story [AREA]-US-001:**
As a [role], I want to [action] so that [business value].
Acceptance criteria:
- Given [context], when [action], then [outcome]
- Given [context], when [action], then [outcome]

**4.6 Data Requirements**
| Data Element | Consumed / Produced / Stored | Source/Destination | Quality Requirements | Related Requirements |
|-------------|---------------------------|-------------------|---------------------|---------------------|
| | | | | |

**4.7 Traceability Summary**
[Confirm that every objective traces to at least one requirement, every requirement traces to at least one acceptance criterion, and every requirement traces back to a gap or objective.]
- Objectives without requirements: [list or "None"]
- Requirements without acceptance criteria: [list or "None"]
- Requirements not tracing to a gap or objective: [list or "None"]
- Gaps without corresponding requirements: [list or "None"]

**4.8 Priority Summary**
| Priority | Count | Key Areas |
|----------|------:|-----------|
| Must Have | | |
| Should Have | | |
| Could Have | | |
| Won't Have (this phase) | | |

If scope must be cut by 30%, remove: [list the Could Have and lowest-priority Should Have items]

---

### SECTION 5: VALIDATION & CONSTRAINTS
*Filled by: Phase 5 -- Validation & Constraints skill*

**5.1 Constraint Architecture**

MUST DO (Non-negotiable Requirements):
| # | Constraint | Why Non-negotiable | Verification Method |
|---|-----------|-------------------|-------------------|
| 1 | | | |

MUST NOT DO (Explicit Prohibitions):
| # | Prohibition | Prevents Failure Mode | Test |
|---|-----------|---------------------|------|
| 1 | | | |

PREFER (Judgment Guidance):
| # | When [situation] | Prefer [A] over [B] | Because [business reason] |
|---|-----------------|---------------------|------------------------|
| 1 | | | |

ESCALATE (Don't Decide -- Ask):
| # | If you encounter... | Stop and ask because... | Who to ask |
|---|-------------------|----------------------|-----------|
| 1 | | | |

**5.2 Failure Mode Register**
| # | Failure Mode | Likelihood | Impact | Prevented By (Constraint #) | Severity if Missed |
|---|-------------|-----------|--------|---------------------------|-------------------|
| 1 | | | | | |

**5.3 Edge Cases**
| # | Scenario | Expected Behavior | Requirements Affected | Resolution |
|---|---------|-------------------|---------------------|------------|
| 1 | | | | |

**5.4 Scope Boundary Validation**
[Check Phase 1 scope boundaries against everything learned since]
- Original scope (from 1.2): [restate]
- Scope additions discovered: [list items that emerged in Phases 2-4]
- Scope removals recommended: [items that should be descoped based on new understanding]
- Verdict: Scope Confirmed / Scope Adjusted (document changes)

**5.5 Thesis Final Validation**
[MANDATORY -- Final check on the root cause hypothesis before solution design]

Thesis from 1.3: "[restate hypothesis]"
Checkpoint from 3.5: [Confirmed / Refined / Needs Revision]

Evidence summary (all phases):
- Supporting: [consolidated evidence]
- Challenging: [consolidated evidence]

Final verdict: Confirmed / Refined / Pivoted
[If Refined: state the refined hypothesis]
[If Pivoted: state the new hypothesis and document why the original was abandoned]

Impact on requirements: [which requirements are affected by thesis confirmation/revision?]

**5.6 Ambiguity Register**
| # | Ambiguous Item | Why It's Ambiguous | Recommended Resolution | Owner | Status |
|---|---------------|-------------------|----------------------|-------|--------|
| 1 | | | | | Open/Resolved |

**5.7 Consolidated Assumptions**
[All assumptions from all phases, with current status]
| # | Assumption | Source Phase | Impact if Wrong | Affected Requirements | Status |
|---|-----------|-------------|----------------|---------------------|--------|
| 1 | | Phase [N] | | [AREA]-# | Validated / Still Assumed / Invalidated |

---

### SECTION 6: SOLUTION & BUSINESS CASE
*Filled by: Phase 6 -- Solution Recommendation & Business Case skill*

**6.1 Options Analysis**
[Always includes "Do Nothing" as the baseline]

**Option A: Do Nothing**
- Description: [maintain current state]
- Cost: [ongoing cost of the current problem -- from 1.2 Impact]
- Benefits: [no implementation risk, no change management]
- Risks: [problem persists or worsens]

**Option B: [Minimal Viable Solution]**
- Description: [what it is]
- Cost: [one-time + recurring]
- Benefits: [quantified where possible]
- Risks: [implementation and business risks]

**Option C: [Full Solution]**
- Description: [what it is]
- Cost: [one-time + recurring]
- Benefits: [quantified where possible]
- Risks: [implementation and business risks]

[Add additional options as needed]

**6.2 Cost-Benefit Summary**
| Option | One-Time Cost | Annual Recurring Cost | Annual Benefit | Payback Period | Confidence |
|--------|-------------|---------------------|---------------|----------------|------------|
| A: Do Nothing | $0 | [ongoing problem cost] | $0 | N/A | High |
| B: | | | | | |
| C: | | | | | |

**6.3 Risk Assessment**
| Option | Risk | Likelihood | Impact | Mitigation |
|--------|------|-----------|--------|-----------|
| | | High/Med/Low | High/Med/Low | |

**6.4 Recommendation**
[Which option and why. Must explicitly reference:]
- The thesis from 1.3: [how the recommendation addresses the root cause]
- Gap analysis from 3.4: [which gaps the recommendation closes]
- Requirements coverage: [which Must Have requirements are satisfied]
- Constraints compliance: [confirmation that the recommendation satisfies all Must Do / Must Not from 5.1]

**6.5 Implementation Roadmap**
| Phase | Milestone | Dependencies | Timeline | Key Deliverables |
|-------|----------|-------------|----------|-----------------|
| 1 | | | | |

**6.6 Measurement Plan**
[Ties back to thesis test criteria from 1.3 and success metrics from 1.5]
| Metric | Baseline | Target | Measurement Method | Measurement Point | Traces to |
|--------|---------|--------|-------------------|-------------------|-----------|
| | | | | [when to measure] | 1.3 test / 1.5 metric # |

**6.7 Sign-Off Tracker**
| Stakeholder | Role | What They Need to See | Sign-Off Status | Date |
|------------|------|---------------------|----------------|------|
| | Sponsor / Decision-maker / Technical | | Pending / Approved / Conditional | |

---

## END OF PROJECT BRIEF
