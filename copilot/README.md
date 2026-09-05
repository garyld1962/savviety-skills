# Savviety workflows for GitHub Copilot

Canonical sources are `copilot/skills`, `prompts`, `agents`, `instructions`,
`templates` and `docs`. The installer maps these to the corresponding `.github/`
paths in a consuming repository. Repository authoring rules live in the source
repo's `.github/copilot-instructions.md`; consuming projects keep their own rules.

First run `./install.sh` from the source repo and open a new terminal, as described
in the [installation instructions](../README.md#installation). Then run:

```bash
skills --copilot --init /path/to/project
skills --copilot --update /path/to/project
```

The project must already be a Git repository; the installer requires Bash, jq and
rsync. Missing source assets fail before installation. User-owned instructions are
preserved. Shared source trees are managed by the installer; keep custom assets
in a separately managed location or add explicit installer protection before update.

Use [the coverage map](../docs/parity/claude-native.md) and [asset catalog](asset-catalog.md)
for entrypoints. Durable SKILL.md workflows contain behavior; prompt files are thin
shortcuts where the host supports them. The planning, execution, validation and nine
new capability workflows are available as skills, without relying on prompt discovery.

The source keeps prompt categories in subdirectories. For VS Code installations
that do not discover them, configure chat.promptFilesLocations for
`.github/prompts/ba`, `dev`, `review`, and `common` in existing workspace settings.
Do not overwrite a project's settings file to install a default.

Current host compatibility matters: [GitHub agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
can bundle instructions/scripts; [VS Code prompt files](https://code.visualstudio.com/docs/agent-customization/prompt-files)
are a separate entrypoint and are not loaded by Agent Host sessions. Do not assume
CLI commands such as /fleet are exposed by every Copilot host. Checked 2026-09-04.

Native task plans now use depends_on, write_scope and milestone_end. Migrate older
wave/lane plans explicitly; validate with the bundled Python/PyYAML script. Required
reviews and checks need evidence on the final code head. Missing/manual checks never
count as success. Governed process references and templates ship under `.github/docs`.

Validate source changes with:

```bash
bin/sync-native-contracts --check
python3 bin/validate-native-parity
python3 -m unittest discover -s tests -v
```
