# CDN Triage Assistant

A small support triage assistant for turning user reported content delivery network (CDN) issues into diagnostic steps, user-safe responses, escalation notes, and documentation improvements.

I built this while preparing for support engineering roles that involve edge platforms, CDNs, HTTP troubleshooting, and user-facing technical support.

The goal is not to build a magic answer machine. The goal is to model the first useful support move:

> Take a vague user report and turn it into a structured investigation.

## Background

A lot of technical support work starts with incomplete information.

User's report a varity of issues with little background ranging from:

- “Users are seeing old content.”
- “The page keeps redirecting.”
- “We’re seeing 503s.”

Those reports matter, but they are not enough to solve the issue. A good support engineer needs to slow the problem down:

- What exactly is affected?
- What changed?
- What evidence do we have?
- What can we verify?
- What should we avoid assuming?
- What can we safely tell the user?
- When should this be escalated?
- What should be documented so the next person has a better path?

That is the workflow this project practices.

My background is in technical support, SaaS troubleshooting, API documentation, developer documentation, UX writing, and technical writing. I’ve spent a lot of time in the gap between product behavior and user confusion. This project applies that same muscle to CDN-style support issues.

## Overview

The assistant reads a short user-style report and classifies it into a support scenario.

For each scenario, it returns:

- A short issue summary
- Evidence to collect
- Suggested diagnostic checks
- A user-safe response draft
- An escalation note
- A documentation improvement

The output is intentionally structured. The point is to make the first pass of triage easier to review, improve, and hand off.

## Scenarios

| Scenario                         | Example user report                                       | What the assistant helps with                                           |
| -------------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Stale content / cache freshness  | “We deployed an update, but users still see the old version.” | Cache headers, TTLs, purge questions, freshness expectations            |
| Redirect loop                    | “The page keeps redirecting and never loads.”                 | Redirect chains, `Location` headers, HTTP/HTTPS or host conflicts       |
| 503 / origin availability        | “Users are seeing service unavailable errors.”                | Origin health, backend changes, path scope, edge vs. origin questions   |
| Header-dependent behavior        | “The page behaves differently for some clients.”              | Request headers, response variants, `Vary`, cookies, client differences |
| Unknown / needs more information | “Something is broken.”                                        | Intake questions, missing evidence, next-step structure                 |

## How it works

The first version uses simple keyword matching. That is intentional.

Before adding an LLM, I wanted the workflow to be explicit and reviewable. The tool should not pretend to know more than it knows.

The classifier looks for common issue patterns and maps the ticket to a scenario:

```text
stale content → stale_content
redirect loop → redirect_loop
503 / service unavailable → server_error
headers / client differences → header_behavior
unclear report → unknown
```

Each scenario has a predefined triage template. That keeps the output consistent and makes the support reasoning easy to inspect.

### Stale-content ticket

```bash
python3 triage.py examples/stale_content.txt
```

### Redirect-loop ticket

```bash
python3 triage.py examples/redirect_loop.txt
```

### Server-error ticket

```bash
python3 triage.py examples/server_error.txt
```

### Header-behavior ticket

```bash
python3 triage.py examples/header_behavior.txt
```

### Test suite

```bash
python3 -m unittest -v
```

### Example input

```text
User says they deployed a new version of their homepage about 20 minutes ago, but users are still seeing the old version. They want to know whether the CDN is serving stale content.
```

### Example output

```markdown

# Triage Result: Stale content / cache freshness

## Summary

The customer reports that updated content is not appearing for users. This may involve cache freshness, TTL behavior, or missing purge steps.

## Evidence to collect

- Affected URL or path
- Approximate time the content was updated
- Whether the issue affects all users or some users
- Response headers from the affected URL
- `Cache-Control` value
- `Age` value, if present
- Whether a purge was attempted

## Suggested checks

- Run `curl -I <affected_url>` to inspect response headers.
- Check `Cache-Control` to understand how long the response can stay fresh.
- Check `Age` to see how long the object may have been stored by a cache.
- Confirm whether the user expects this content to update immediately.
- Ask whether a purge was triggered after deployment.

## User-safe response draft

I’d like to confirm the cache behavior for the affected URL. Please send one or two example URLs, the approximate time the content changed, and whether a purge was triggered after deployment. I’ll check the response headers, including `Cache-Control` and `Age`, to determine whether users may still be receiving a cached version.

## Escalation note

Escalate if the content continues to appear stale after confirming the expected TTL, checking response headers, and verifying that a purge completed successfully.

## Documentation improvement

Add or improve documentation explaining how TTLs and purge behavior affect content freshness after deployments.

```

## Next steps

This is a small first version.

It does not call an external AI model yet. That is deliberate. I wanted the support workflow to be clear before adding model-generated output.

This version focuses on:

- Support triage structure
- Repeatable issue categories
- Evidence collection
- User-safe communication
- Escalation quality
- Documentation follow-up

Future versions could add:

- LLM-generated summaries
- Confidence scoring
- “Do not assume” warnings
- JSON output
- Markdown report export
- Links to relevant docs
- Sample `curl` output parsing
- Stronger classification logic
- Guardrails for risky or unsupported claims

## What this project demonstrates

This project shows how I approach support engineering work:

- I break vague issues into clear categories.
- I separate evidence from assumptions.
- I write responses that are useful without overpromising.
- I create escalation notes that give the next team context.
- I connect recurring support issues back to documentation improvements.
- I use Python to turn a repeatable support pattern into a small working tool.
- I learn new technical domains by building practical, reviewable examples.

This is the same support motion I’ve used across technical support, API documentation, developer documentation, and user-facing troubleshooting: understand the issue, verify the behavior, explain it clearly, and make the next case easier.