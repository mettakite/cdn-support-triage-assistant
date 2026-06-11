import sys
from pathlib import Path


TRIAGE_TEMPLATES = {
    "stale_content": {
        "category": "Stale content / cache freshness",
        "summary": (
            "The customer reports that updated content is not appearing for users. "
            "This may involve cache freshness, TTL behavior, or missing purge steps."
        ),
        "evidence": [
            "Affected URL or path",
            "Approximate time the content was updated",
            "Whether the issue affects all users or some users",
            "Response headers from the affected URL",
            "`Cache-Control` value",
            "`Age` value, if present",
            "Whether a purge was attempted",
        ],
        "checks": [
            "Run `curl -I <affected_url>` to inspect response headers.",
            "Check `Cache-Control` to understand how long the response can stay fresh.",
            "Check `Age` to see how long the object may have been stored by a cache.",
            "Confirm whether the customer expects this content to update immediately.",
            "Ask whether a purge was triggered after deployment.",
        ],
        "customer_response": (
            "I'd like to confirm the cache behavior for the affected URL. "
            "Please send one or two example URLs, the approximate time the content changed, "
            "and whether a purge was triggered after deployment. I'll check the response "
            "headers, including `Cache-Control` and `Age`, to determine whether users may "
            "still be receiving a cached version."
        ),
        "escalation": (
            "Escalate if the content continues to appear stale after confirming the expected "
            "TTL, checking response headers, and verifying that a purge completed successfully."
        ),
        "docs_improvement": (
            "Add or improve documentation explaining how TTLs and purge behavior affect "
            "content freshness after deployments."
        ),
    },
    "redirect_loop": {
        "category": "Redirect loop",
        "summary": (
            "The customer reports that users cannot reach a final page because requests "
            "keep redirecting."
        ),
        "evidence": [
            "Affected URL",
            "Redirect status codes",
            "`Location` headers",
            "Number of redirect hops",
            "Recent redirect rule changes",
            "Whether redirects exist at both the origin and edge layers",
        ],
        "checks": [
            "Run `curl -I -L --max-redirs 5 <affected_url>` to inspect the redirect chain.",
            "Check each `Location` header to see where the request is being sent.",
            "Look for HTTP-to-HTTPS or www-to-non-www conflicts.",
            "Confirm whether origin redirects and edge redirects disagree.",
        ],
        "customer_response": (
            "I'd like to inspect the redirect chain for the affected URL. "
            "Please send an example URL and any recent redirect rule changes. "
            "I'll check the redirect status codes and `Location` headers to see whether "
            "the request is being sent back to the same URL or bouncing between rules."
        ),
        "escalation": (
            "Escalate if redirect rules appear correct but the observed redirect chain "
            "still loops or changes unexpectedly at the edge."
        ),
        "docs_improvement": (
            "Add examples of common redirect loop causes, including duplicate HTTP-to-HTTPS "
            "rules, host canonicalization conflicts, and path rewrite issues."
        ),
    },
    "server_error": {
        "category": "503 / origin or service availability",
        "summary": (
            "The customer reports `503 Service Unavailable` errors. The first triage step "
            "is to determine whether the error is coming from the origin, the edge, or a "
            "configuration issue between them."
        ),
        "evidence": [
            "Affected URLs",
            "Whether the issue is path-specific or site-wide",
            "HTTP status code",
            "Response body or error text",
            "Recent deploys or backend changes",
            "Origin health indicators",
            "Any retry or timeout-related headers",
        ],
        "checks": [
            "Run `curl -i <affected_url>` to inspect the status code and response body.",
            "Check whether the issue affects one path or multiple paths.",
            "Ask whether the origin is healthy and reachable.",
            "Confirm whether there was a recent deploy or traffic change.",
            "Check whether stale-if-error or fallback behavior is configured.",
        ],
        "customer_response": (
            "I reproduced that users are seeing `503 Service Unavailable` responses. "
            "To narrow this down, I'd like to confirm whether the issue is limited to specific "
            "URLs or affecting the full site, and whether there were recent backend deploys or "
            "origin health changes. From there, I can help determine whether the error appears "
            "to come from the origin, the edge, or the configuration between them."
        ),
        "escalation": (
            "Escalate if the origin appears healthy but edge requests continue returning "
            "`503` responses, or if the error source cannot be confirmed from available headers "
            "and logs."
        ),
        "docs_improvement": (
            "Add a support checklist for `503` triage that separates origin availability, "
            "edge behavior, deploy changes, and fallback configuration."
        ),
    },
    "header_behavior": {
        "category": "Header-dependent behavior",
        "summary": (
            "The customer reports different behavior across clients. Request headers, cookies, "
            "authentication state, or cache variants may be involved."
        ),
        "evidence": [
            "Affected URL",
            "Client type or user agent",
            "Request headers from working and failing clients",
            "Response headers for each request",
            "`Vary` header, if present",
            "Authentication or cookie differences",
        ],
        "checks": [
            "Run `curl -i <affected_url>` without custom headers.",
            "Run `curl -i -H '<Header-Name>: <value>' <affected_url>` with the suspected header.",
            "Compare response bodies and response headers.",
            "Check whether the `Vary` header accounts for the request header.",
            "Confirm whether cache behavior should vary by client, header, or auth state.",
        ],
        "customer_response": (
            "I'd like to compare the request and response details for the clients seeing "
            "different behavior. Please send the affected URL and, if possible, the relevant "
            "request headers from a working client and a failing client. I'll compare the "
            "responses to see whether a header, cookie, auth state, or cache variant is "
            "driving the difference."
        ),
        "escalation": (
            "Escalate if users receive the wrong response variant after confirming the expected "
            "request headers, response headers, and cache behavior."
        ),
        "docs_improvement": (
            "Add guidance explaining how request headers and `Vary` behavior can affect cached "
            "response variants."
        ),
    },
    "unknown": {
        "category": "Unknown / needs more information",
        "summary": "The ticket does not contain enough clear information to classify the issue.",
        "evidence": [
            "Affected URL",
            "Expected behavior",
            "Actual behavior",
            "When the issue started",
            "Whether the issue affects all users or some users",
            "Any recent deploys or configuration changes",
            "Relevant response headers or error messages",
        ],
        "checks": [
            "Ask for a specific affected URL.",
            "Ask what changed and when.",
            "Ask whether the issue is reproducible.",
            "Run `curl -i <affected_url>` once an affected URL is provided.",
            "Collect status code, response headers, and response body.",
        ],
        "customer_response": (
            "I can help investigate this, but I'll need a bit more detail first. "
            "Please send an affected URL, what you expected to happen, what actually happened, "
            "when the issue started, and whether any deploys or configuration changes happened "
            "around that time."
        ),
        "escalation": (
            "Do not escalate yet. First collect the affected URL, expected behavior, actual "
            "behavior, timeline, and response details."
        ),
        "docs_improvement": (
            "Create an intake checklist for CDN-style support tickets so customers know what "
            "information helps speed up triage."
        ),
    },
}


def load_ticket(file_path):
    """Read a support ticket from a text file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Could not find file: {file_path}")

    return path.read_text(encoding="utf-8").strip()


def classify_ticket(ticket_text):
    """
    Classify a CDN-style support ticket using simple keyword matching.

    This is intentionally rule-based for now. The goal is not to replace
    human judgment or pretend the tool knows the answer. The goal is to
    structure the first pass of triage.
    """
    text = ticket_text.lower()

    if any(word in text for word in ["stale", "old version", "cached", "cache", "purge"]):
        return "stale_content"

    if any(word in text for word in ["redirect", "loop", "http to https", "https"]):
        return "redirect_loop"

    if any(word in text for word in ["503", "service unavailable", "origin", "backend"]):
        return "server_error"

    if any(word in text for word in ["header", "headers", "mobile app", "browser", "client"]):
        return "header_behavior"

    return "unknown"


def build_triage_response(category, ticket_text=None):
    """Return a structured triage response for the detected category."""
    return TRIAGE_TEMPLATES.get(category, TRIAGE_TEMPLATES["unknown"])


def format_response(response):
    """Format the triage response as readable Markdown."""
    lines = [
        f"# Triage Result: {response['category']}",
        "",
        "## Summary",
        response["summary"],
        "",
        "## Evidence to collect",
    ]

    for item in response["evidence"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Suggested checks"])
    for item in response["checks"]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Customer-safe response draft",
            response["customer_response"],
            "",
            "## Escalation note",
            response["escalation"],
            "",
            "## Documentation improvement",
            response["docs_improvement"],
            "",
        ]
    )

    return "\n".join(lines)


def triage_ticket(ticket_text):
    """Classify and format a support ticket."""
    category = classify_ticket(ticket_text)
    response = build_triage_response(category, ticket_text)
    return format_response(response)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 triage.py <ticket_file>")
        sys.exit(1)

    try:
        ticket_text = load_ticket(sys.argv[1])
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    print(triage_ticket(ticket_text))


if __name__ == "__main__":
    main()
