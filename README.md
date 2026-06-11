# CDN Support Triage Assistant

A small support triage assistant for turning CDN-style customer issues into diagnostic steps, customer-safe responses, escalation notes, and documentation improvements.

I built this project while preparing for Customer Support Engineer roles that involve edge platforms, CDNs, HTTP troubleshooting, and customer-facing technical support.

This is not meant to replace a support engineer. It is meant to model the first pass of support triage:

1. Read the customer issue.
2. Identify the likely issue category.
3. List the evidence needed.
4. Suggest useful diagnostic checks.
5. Draft a customer-safe response.
6. Create an escalation note.
7. Identify where documentation could prevent repeat issues.

## Why I built this

My background is in Tier 3 support, API documentation, developer documentation, and technical writing. I have supported customers, developers, and internal teams through complex product behavior, but I have not worked directly in CDN support.

I built this project to show how I approach a new technical support domain: by breaking recurring issues into patterns, creating structured triage paths, and turning messy tickets into clear next steps.

The goal is not to pretend the assistant always knows the answer. The goal is to keep the support workflow grounded:

- What did the customer report?
- What evidence do we need?
- What can we safely say?
- What should we avoid assuming?
- When should we escalate?
- What should be documented for next time?

## How it works

The first version uses simple keyword matching to classify a support ticket into one of these categories:

| Category | Example customer issue |
|---|---|
| Stale content / cache freshness | "We deployed an update, but users still see the old version." |
| Redirect loop | "The page keeps redirecting and never loads." |
| 503 / origin availability | "Users are seeing service unavailable errors." |
| Header-dependent behavior | "The page behaves differently for some clients." |
| Unknown / needs more information | "Something is broken, but we need more detail." |

For each category, the tool returns:

- Issue summary
- Evidence to collect
- Suggested diagnostic checks
- Customer-safe response draft
- Escalation note
- Documentation improvement

## Why this matters for support

A lot of support work is not immediately solving the issue. It is structuring the investigation.

A useful support response should not overclaim. It should:

- Confirm what is known
- Ask for the missing evidence
- Suggest the right checks
- Avoid blaming the wrong system too early
- Create clean notes for escalation
- Turn repeated confusion into better documentation

This project practices that motion.

## Run locally

Run a sample ticket:

```bash
python3 triage.py examples/stale_content.txt
```

Run another sample:

```bash
python3 triage.py examples/redirect_loop.txt
```

Run the test suite:

```bash
python3 -m unittest -v
```

## Example input

```text
Customer says they deployed a new version of their homepage about 20 minutes ago, but users are still seeing the old version. They want to know whether the CDN is serving stale content.
```

## Example output

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
- Confirm whether the customer expects this content to update immediately.
- Ask whether a purge was triggered after deployment.

## Customer-safe response draft
I'd like to confirm the cache behavior for the affected URL. Please send one or two example URLs, the approximate time the content changed, and whether a purge was triggered after deployment. I'll check the response headers, including `Cache-Control` and `Age`, to determine whether users may still be receiving a cached version.
```

## Project scope

This first version is intentionally small.

It does not call an external AI model yet. That is intentional. The first goal is to build a clean support triage workflow before adding an LLM.

Future versions could add:

- LLM-generated summaries
- Stricter guardrails against overclaiming
- JSON output
- Markdown report export
- Links to relevant documentation
- Integration with sample curl output
- Confidence scoring
- "Do not assume" warnings

## What this project demonstrates

This project shows that I can:

- Break support issues into clear categories
- Identify evidence needed for triage
- Write customer-safe technical responses
- Create useful escalation notes
- Connect support tickets back to documentation improvements
- Use Python to structure a repeatable support workflow
- Approach CDN and edge support concepts in a practical, grounded way
