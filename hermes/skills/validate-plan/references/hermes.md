# Running the shared workflows in Hermes

Skills are loaded on demand with `skill_view`. Read a reference inside its
own skill, for example:

```text
skill_view(name="validate-plan", file_path="references/execution.md")
skill_view(name="simplify", file_path="references/output.md")
```

Resolve sibling links by loading the named sibling skill or its reference;
do not pass `../` paths to skill_view. Follow all shared contract references
as needed, including the simplify guidance linked from execution/reporting.

Use the actual repository working directory for edits, Git and checks. A
Hermes profile home stores agent state; it is not the project directory.
Read applicable project instructions such as AGENTS.md and declared commands.
Use only tools exposed in the session, normally terminal for shell execution
and available file tools for reads/edits. No Claude Workflow host is needed.

Locate scripts from the loaded skill's actual location; do not assume the
default profile. Local installs normally live at
`${HERMES_HOME:-$HOME/.hermes}/skills/validate-plan/scripts/`. Check that this
location is reachable from the terminal backend. With a container/remote
backend, load scripts through skill_view and copy them unchanged into an
appropriate temporary directory there if they are not mounted. Keep
validate_plan.py and validate_report.py together: the report checker imports
the plan checker. Report an inaccessible script as a blocker, not a passed check.

The validators require Python 3 and PyYAML. Prefer the project's configured
Python environment. If it lacks PyYAML and uv is available, run:

```text
uv run --with pyyaml python <actual-script-path> <arguments>
```

This may download PyYAML; obey host network/installation permissions. Run
`validate_plan.py <plan.md>` before execution, and
`validate_report.py <report.json> --plan <plan.md>` before final certification.
Do not add a Python dependency to the application just to run skill helpers.

The shared contract names review and delivery capabilities, not mandatory
skill installations. Perform required reviews with available tools and the
shared criteria. For GitHub readiness, check the configured remote and actual
authentication (`gh auth status` if using gh) before an authorized operation.
For Linear, use the configured connector only when available; otherwise obtain
the issue content from the user. Do not invent APIs or install a second tracker.
