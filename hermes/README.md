# Hermes Agent skills

An initial four-skill package using Hermes entrypoints and the same shared
workflow instructions as our native Codex and Copilot packages.

| Command | Purpose |
|---|---|
| `/simplify` | Explain the latest update or a supplied report in plain language |
| `/validate-plan <path>` | Check a plan's structure and readiness without implementing it |
| `/execute-prd <source>` | Audit requirements, write a plan, and implement when requested |
| `/execute-plan <path>` | Execute or resume a validated plan and record verification evidence |

Simplification applies automatically to assistant-written updates throughout
PRD/plan execution. Raw tool output rendered directly by Hermes is outside the
skill's control. Linear remains the tracker when supplied as the source; its
connector must already be configured to fetch live issues. The skills do not
install a tracker, connect accounts or authorize posting issue updates.

## Install and update

From this checkout, install missing development utilities and the skill package:

```bash
./update.sh --hermes
```

This uses `HERMES_HOME` when set, otherwise `~/.hermes`. An explicit argument
is the **profile home**, not the project or its skills directory:

```bash
./update.sh --hermes "$HOME/.hermes/profiles/coder"
```

The wrapper reuses `bin/install-agentic-tools` for uv and the existing utility
set, including ShellCheck and gh-axi. Python 3.9+ must already be available for
the Hermes installation preflight. It does not install Hermes Agent itself.
Skill installation alone uses Bash and Python's standard library:

```bash
bash cli/skill.sh --hermes --init --dry-run
bash cli/skill.sh --hermes --init
bash cli/skill.sh --hermes --update
```

After `./install.sh`, these are also available as `skills --hermes ...`.
Start a new Hermes session in your **project directory** using the selected
profile, then invoke the slash commands. Profile selection in a Hermes wrapper
does not necessarily export HERMES_HOME into your calling shell; pass the
profile path explicitly when installing for a named profile.

The installer copies only `hermes/skills/` and records fingerprints in
`<profile-home>/.savviety-skills.json`. No permissions, settings, hooks, persona,
memory or account configuration is copied. Updates refresh unmodified managed
skills. Existing unrelated skills and skills withdrawn from our catalog remain.

A locally changed, added or deleted file in a managed skill stops the entire
update before skill writes; an existing unmanaged destination also stops it.
Keep your edited copy outside the discoverable skills directory, compare it
with `hermes/skills/<name>`, and reconcile deliberately before retrying. Either
restore the last installed tree or reconcile the installed tree to the incoming
source. Preserve the install record; deleting it loses ownership history.
There is no Hermes `--force` or `--prune` option. `--dry-run` writes nothing.
Do not edit managed skills concurrently with an installation.

## Runtime and validation

The plan/report helpers need Python and PyYAML in the execution environment.
They can use the project's environment or `uv run --with pyyaml python ...`;
the latter may download PyYAML. Container/remote backends must have access to
the packaged scripts. See [Hermes runtime guidance](skills/validate-plan/references/hermes.md).

Shared sources live under `shared/workflow-contracts/` and `shared/simplify/`.
Run `bin/sync-native-contracts` after changing them. CI checks package drift,
frontmatter, resource links, installer behavior and the installed validators.
The pilot does not rely on Claude's Workflow runtime and does not yet ship
separate review/checkpoint skills. Required checks and reviews are performed
through the available Hermes tools with evidence retained.

The local tests verify packaging and helper behavior. They do **not** certify
live model execution. Once Hermes is configured, try these in a disposable Git
project with declared lint/build/test commands:

1. `/simplify The code checks passed. The empty-export acceptance test failed
   because the CSV header is missing. Nothing is deployed.` Expect a clear
   account of the remaining defect, verification limits and next step.
2. `/validate-plan <path>` with one valid task graph, then one with a dependency
   cycle. Expect a readiness review for the former and a clear refusal for the
   latter, with no implementation edits.
3. `/execute-prd <small fixture PRD>` requesting a greeting CLI and its test.
   Expect a plan, implementation, real checks, recorded evidence, and clear
   updates. A planning-only request must stop before implementation.

Verify that Hermes loaded these entrypoints. A same-name skill in another
discovery location or a configured command bundle can affect invocation.

Compatibility references: [Hermes skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/)
and [profile homes](https://hermes-agent.nousresearch.com/docs/user-guide/profiles/).
