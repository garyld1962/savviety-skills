# Deck — Simplified / De-Jargoned

Rewrite of the three core ideas for a *spoken* talk. Goal: a listener follows it the first
time, without a glossary. Plain words, one analogy per idea, short lines.

Three beats:
1. **AI is just coding, a different way** — 2 slides (story, then table)
2. **What a "skill" actually is** — 2 slides (story, then table)
3. **Ten ways to keep tokens under control** — flat list, no categories

---

# Part 1 — AI Is Just Coding, a Different Way

## Slide 1 — The Story

**Heading:** You didn't stop engineering. You moved up a floor.

Every few decades, programming moves up a level of abstraction.

- We went from flipping switches → to assembly → to C → to Python.
- Each jump, we wrote *less about how* and *more about what*.
- We never stopped engineering. We just stopped typing the boring parts.

**AI is the next jump.**

We used to write the exact steps. We you write the **intent**, hand the machine the
**right context**, set the **rules**, and **check the result**.

The machine writes the steps.

> The part that feels like magic — "it just wrote the code" — is the same part that used to
> feel like magic when the compiler turned C into machine code. The thinking didn't go away.
> It moved to what you feed in and how you check what comes out.

**The trap:** if you treat it like a magic wishing box, you ship bad software faster than
ever. The engineering didn't disappear. It moved to the inputs.

---

## Slide 2 — The Same Job, Renamed

**Heading:** Everything you already do still has a name here

| What you did before | What it's called now |
|---|---|
| Write the code | Write the intent and the rules |
| Pick the right library | Give it the right context |
| Read the docs | Tell it what "good" looks like |
| Run the tests | Check the output before you trust it |
| Review the pull request | Review what the AI produced |

> Same job. New tools. You're still the engineer — you're just working one floor up.

---

# BEAT 2 — What a "Skill" Actually Is

## Slide 3 — The Story

**Heading:** A prompt is asking a favor. A skill is writing it down.

Picture a new hire on day one.

- **The prompt way:** "Hey, can you handle the release? Figure it out." — You get a different
  result every time, depending on who's asking and what mood the day is in.
- **The skill way:** You hand them the checklist. *This* is the job, *here's* what you need,
  *these* are the steps, *this* is what done looks like, *here's* how we know it worked.

A **skill** is that checklist — written once, so the machine does the job the **same way
every time**, instead of improvising.

> A prompt asks the model to do something.
> A skill teaches the system to do something *repeatedly and reliably.*

That's the whole difference. One is a conversation. The other is an asset you own, version,
and improve — like any other piece of your codebase.

---

## Slide 4 — Prompt vs. Skill

**Heading:** When a request becomes a tool

| A prompt | A skill |
|---|---|
| One-off ask | Reusable tool |
| You re-explain it every time | Explained once, runs on command |
| Result varies | Result is consistent |
| Nothing to test | You can check it works |
| Lives in the chat | Lives in your repo, versioned and owned |

> A skill is just a prompt that grew up: it got a job description, an input list, a set of
> rules, and a way to prove it did the work.

---

## Slide 5 — What Makes a Skill *Good*

**Heading:** Twelve questions a good skill can answer

A *good* one answers twelve plain questions. 

| # | Characteristic | The question it answers |
|---:|---|---|
| 1 | **Job** | What does this actually do? |
| 2 | **Trigger** | When should it kick in? |
| 3 | **Boundaries** | What's *not* its job? |
| 4 | **Inputs it needs** | What does it need to see to do the work? |
| 5 | **Steps** | What's the actual process, in order? |
| 6 | **Required inputs** | What must you hand it, so it doesn't guess? |
| 7 | **Allowed tools** | What's it allowed to touch? |
| 8 | **Right model** | How much horsepower does this job need? |
| 9 | **Guardrails** | What must it never do? |
| 10 | **Output shape** | What should the result look like? |
| 11 | **Proof it works** | How do we know it did the job right? |
| 12 | **Ownership** | Who owns it, and how does it change over time? |

> First half is *setup* — what goes in and how it runs. Second half is *trust* — limits,
> output, proof, ownership. A skill missing the trust half is just a hopeful prompt.

---

# BEAT 3 — Ten Ways to Keep Tokens Under Control

**Heading:** Context is a budget. Spend it on thinking, not on noise.

The model has a fixed amount of room to "hold in its head" at once. Every wasted word is a
word it can't use to actually solve your problem. Ten habits that keep the budget clean —
each with what it looks like in a real run.

| # | The habit | In plain terms | What it looked like |
|---:|---|---|---|
| 1 | **Read narrow** | Pull the lines you need, not the whole file | Workers read `db.ts:170-213`, never the whole file |
| 2 | **Say less** | No preamble, no recaps, no re-pasting unchanged code | 18 surgical edits vs only 6 full rewrites |
| 3 | **Start fresh between phases** | When the job changes, drop the baggage from the last one | 8 reviews ran in their own windows — parent grew 38k, not 8× |
| 4 | **Carry a summary, not a transcript** | Next session reads a digest, not the whole history | Run produced a short report + postmortem to hand forward |
| 5 | **Right model for the job** | Cheap model for lookups, strong model for hard thinking | Adversarial review ran on a *different* model on purpose |
| 6 | **Compress the tools' output** | A proxy strips noisy command output before it lands | RTK: claimed 60–90% less text from everyday commands |
| 7 | **Split the work into lanes** | Run independent jobs side by side, each with its own context | One turn fanned out to **8 review agents at once** |
| 8 | **Use lean tools** | Plain Unix output beats verbose, decorated output | Every command piped through `head`/`tail`/`rg` |
| 9 | **Stop scanning at a limit** | Cap how much you read so there's room left to think | Reserve ~70% of the window for the actual work |
| 10 | **Set a retry limit** | After N tries, stop and surface the problem | Budget of 20 retries; this run used ~4 and asked a human when stuck |

> The point isn't to spend the fewest tokens. It's to make sure every token is buying you
> thinking — not re-reading, re-explaining, or chasing its own tail.

---

## Closing line

> The code changed shape. The engineering did not.
> AI is an abstraction of *coding* — not an abstraction of *thinking.*
