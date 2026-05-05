---
description: "Search one repo, multiple repos, or a repo folder for a code pattern or behavior and produce a Markdown investigation index."
argument-hint: "Describe what to find and where to search"
---

# Code Investigation

Search code for a requested pattern or behavior and produce a formatted report under `docs/code-investigations/`.

## Good Uses

- Find all places where the code sends email
- Find all places where the code reads or writes files
- Find uses of a specific API, library, class, method, header, queue, or config key
- Search across several related repositories and compare how a behavior is implemented

## Inputs to Provide

- **What to find** - exact pattern, API, or natural-language behavior
- **Where to search** - one repo, an explicit repo list, or a folder containing repos
- Optional limits or exclusions

## Runtime Questions

If you do not specify them up front, the investigation workflow should ask:

1. Should the report include matching code lines?
2. Should the report summarize what the code is doing at each match?

If scope or search intent is unclear, it should ask for clarification before running.

## Example Requests

- `Investigate all places in ./beqom where code sends email.`
- `Search acs-webapp and ACS-web-services for file upload logic. Include code lines but skip summaries.`
- `Find where these repos call Service Bus and write a report.`
- `Search the pcrs folder for code that reads files from disk and summarize each match.`

## Expected Output

A Markdown report that acts like an index and includes:

- repo name
- project name
- filename
- line range
- confidence score that the match is real
- optional code lines
- optional short behavior summary
