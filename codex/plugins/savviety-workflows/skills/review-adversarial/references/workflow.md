# Adversarial Review Workflow

Use this only after normal review or when the user explicitly asks for adversarial review.

## Trigger

Run for:

- Auth, payments, secrets, permissions, migrations, crypto, or data loss risk.
- Large diffs.
- Architectural boundary changes.
- User-requested adversarial review.

Skip for small low-risk diffs unless the user asks.

## Reviewer Model

Prefer a different model or CLI from the current assistant when one is installed and authenticated. Use `scripts/cli_probe.py` to check known CLIs.

If no external reviewer is available:

- In automatic mode, skip cleanly and record the environment limitation.
- In explicit mode, fail loudly because the user asked for this gate.

Codex subagents are allowed only when the user explicitly authorizes them and accepts that this is a weaker same-model fallback, not a true cross-model review.

## Lenses

Read `references/reviewer-lenses.md`.

Choose by size and risk:

- Small: skeptic.
- Medium: skeptic and architect.
- Large or high-risk: skeptic, architect, and minimalist.

## Synthesis

1. State the author intent.
2. Collect reviewer outputs.
3. Deduplicate findings without losing file and line references.
4. Produce `PASS`, `CONTESTED`, or `REJECT`.
5. Add lead judgment that accepts or rejects each finding with a short rationale.

