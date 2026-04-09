# Code Review Report

- **Run ID:** {{RUN_ID}}
- **Generated (local):** {{TIMESTAMP}}
- **Scope:** {{SCOPE}}
- **Mode:** {{MODE}}
- **Reviewer:** Code Review Orchestrator
- **Files reviewed:** {{FILES_REVIEWED_COUNT}}
- **Sampling note:** {{SAMPLING_NOTE}}

## Summary
- Blockers: {{COUNT_BLOCKER}}
- High: {{COUNT_HIGH}}
- Medium: {{COUNT_MEDIUM}}
- Low: {{COUNT_LOW}}
- Info: {{COUNT_INFO}}

## Findings (by severity, then domain)

### Blocker

#### csharp-quality
{{FINDINGS_BLOCKER_CSHARP_QUALITY}}

#### async-safety
{{FINDINGS_BLOCKER_ASYNC_SAFETY}}

#### security
{{FINDINGS_BLOCKER_SECURITY}}

#### complexity
{{FINDINGS_BLOCKER_COMPLEXITY}}

#### di-architecture
{{FINDINGS_BLOCKER_DI_ARCHITECTURE}}

#### k8s-readiness
{{FINDINGS_BLOCKER_K8S_READINESS}}

### High

#### csharp-quality
{{FINDINGS_HIGH_CSHARP_QUALITY}}

#### async-safety
{{FINDINGS_HIGH_ASYNC_SAFETY}}

#### security
{{FINDINGS_HIGH_SECURITY}}

#### complexity
{{FINDINGS_HIGH_COMPLEXITY}}

#### di-architecture
{{FINDINGS_HIGH_DI_ARCHITECTURE}}

#### k8s-readiness
{{FINDINGS_HIGH_K8S_READINESS}}

### Medium

#### csharp-quality
{{FINDINGS_MEDIUM_CSHARP_QUALITY}}

#### async-safety
{{FINDINGS_MEDIUM_ASYNC_SAFETY}}

#### security
{{FINDINGS_MEDIUM_SECURITY}}

#### complexity
{{FINDINGS_MEDIUM_COMPLEXITY}}

#### di-architecture
{{FINDINGS_MEDIUM_DI_ARCHITECTURE}}

#### k8s-readiness
{{FINDINGS_MEDIUM_K8S_READINESS}}

### Low

#### csharp-quality
{{FINDINGS_LOW_CSHARP_QUALITY}}

#### async-safety
{{FINDINGS_LOW_ASYNC_SAFETY}}

#### security
{{FINDINGS_LOW_SECURITY}}

#### complexity
{{FINDINGS_LOW_COMPLEXITY}}

#### di-architecture
{{FINDINGS_LOW_DI_ARCHITECTURE}}

#### k8s-readiness
{{FINDINGS_LOW_K8S_READINESS}}

### Info

#### csharp-quality
{{FINDINGS_INFO_CSHARP_QUALITY}}

#### async-safety
{{FINDINGS_INFO_ASYNC_SAFETY}}

#### security
{{FINDINGS_INFO_SECURITY}}

#### complexity
{{FINDINGS_INFO_COMPLEXITY}}

#### di-architecture
{{FINDINGS_INFO_DI_ARCHITECTURE}}

#### k8s-readiness
{{FINDINGS_INFO_K8S_READINESS}}

<!-- Omit any severity section that has zero findings across all domains. -->
<!-- Omit any domain sub-heading within a severity that has zero findings. -->

## Files reviewed
{{FILES_REVIEWED_LIST}}

## Notes & assumptions
{{NOTES}}
