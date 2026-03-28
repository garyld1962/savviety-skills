---
description: "Retrieve an Azure DevOps work item by ID: fetch title, description, acceptance criteria, and discussion from an ADO board."
argument-hint: "Provide the work item ID (e.g., 12345)"
---

# ADO Work Item Retrieval

Fetch a work item from Azure DevOps and present its story details.

## When to Use

- User provides an ADO work item ID
- User wants to understand requirements before planning or coding

## Prerequisites

- The `az` CLI must be installed with the `azure-devops` extension
- User must be authenticated (`az login`)
- Organization and project must be configured (or provided)

## Configuration

| Variable | Example |
|----------|---------|
| `ADO_ORG` | `https://dev.azure.com/myorg` |
| `ADO_PROJECT` | `MyProject` |

## Workflow

### Step 1: Resolve Configuration

```bash
az devops configure --list
```

If org/project are not configured, look for `.ado-config` in repo root, then ask the user. Once known:
```bash
az devops configure --defaults organization=<ADO_ORG> project="<ADO_PROJECT>"
```

> **Important:** `az boards work-item show` does NOT accept `--project` inline. Set via `az devops configure --defaults`.

### Step 2: Fetch the Work Item

```bash
az boards work-item show --id <ITEM_ID> --output json
```

### Step 3: Extract Key Fields

- **ID** — `id`
- **Type** — `fields["System.WorkItemType"]`
- **Title** — `fields["System.Title"]`
- **State** — `fields["System.State"]`
- **Assigned To** — `fields["System.AssignedTo"].displayName`
- **Description** — `fields["System.Description"]` (HTML → readable text)
- **Acceptance Criteria** — `fields["Microsoft.VSTS.Common.AcceptanceCriteria"]`
- **Story Points** — `fields["Microsoft.VSTS.Scheduling.StoryPoints"]`
- **Tags** — `fields["System.Tags"]`
- **Parent** — from relations where `rel == "System.LinkTypes.Hierarchy-Reverse"`

### Step 4: Present to User

```markdown
## ADO #<ID>: <Title>
**Type:** User Story | **State:** Active | **Points:** 5
**Assigned To:** Jane Doe

### Description
<cleaned description text>

### Acceptance Criteria
<cleaned AC text>

### Tags
tag1, tag2
```

### Step 5 (Optional): Fetch Comments

If the user asks for discussion/comments:
```bash
az boards work-item show --id <ITEM_ID> --expand all --output json
```
