---
name: vault
description: "Search, create, and manage notes in the Obsidian vault at /data/obsidian. Use when user wants to find, create, link, or organize notes — phrases like 'find my note on X', 'create a note about', 'add this to the vault', 'search my notes', 'open the vault'."
---

# /vault -- Obsidian Note Management

**Purpose:** Search, create, and manage notes in the Obsidian vault at `/data/obsidian`.

## Vault Location

```
/data/obsidian/
└── 00-Inbox/      ← landing zone for new and unsorted notes
```

## Conventions

> **TODO:** Document vault conventions here as they emerge — folder structure beyond Inbox, naming rules, note types, tagging system, linking strategy, template shapes. The skill works without this section but will default to placing new notes in `00-Inbox/` and using Title Case naming.

Defaults until overridden:
- New notes land in `00-Inbox/` unless a better folder is obvious
- Filename: Title Case, `.md` extension
- Link with Obsidian `[[wikilink]]` syntax
- Related notes linked at the bottom of each note

## Workflows

### Search by Filename

```bash
find /data/obsidian -name "*.md" | grep -i "keyword"
```

### Search by Content

```bash
grep -rl "keyword" /data/obsidian --include="*.md"
```

### Create a Note

1. Choose the right folder (default: `00-Inbox/` if unsure)
2. Name the file — Title Case, no special characters
3. Write content
4. Add `[[wikilinks]]` to related notes at the bottom

### Find Backlinks

```bash
grep -rl "\[\[Note Title\]\]" /data/obsidian --include="*.md"
```

### Find Notes in a Folder

```bash
find /data/obsidian -path "*/00-Inbox/*.md"
```

### List All Notes

```bash
find /data/obsidian -name "*.md" | sort
```
