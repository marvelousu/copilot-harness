#!/usr/bin/env python3
"""Copilot preToolUse hook: guard credential files and irreversible git commands.

Protocol: read the tool call as JSON on stdin, write a decision as JSON on stdout.
  {"permissionDecision": "deny" | "ask", "permissionDecisionReason": "..."}
Emitting nothing leaves the normal permission flow untouched.

Two tiers:
  deny  credential-bearing files are never touched, whatever the user said.
  ask   force push and --no-verify need a human in the loop. Under cloud agent
        "ask" degrades to deny because nobody can answer, which is the safe side.

Copilot's stdin schema is not identical across surfaces, so this walks every
string in the payload instead of relying on specific key names. It fails open:
any parse error or unexpected shape allows the call rather than blocking work.
"""

import json
import re
import sys

DENY_PATTERNS = [
    r"(^|[\s\\/=\"'`:])\.env($|[\s\"'`;<>|&])",
    r"(^|[\s\\/=\"'`:])\.env\.",
    r"secrets?\.(json|ya?ml|txt)($|[\s\"'`;<>|&])",
    r"credentials?\.",
    r"\.pem($|[\s\"'`;<>|&])",
    r"\.key($|[\s\"'`;<>|&])",
    r"\.p12($|[\s\"'`;<>|&])",
    r"\.pfx($|[\s\"'`;<>|&])",
    r"auth\.json($|[\s\"'`;<>|&])",
    r"(^|[\s\\/=\"'`:])id_(rsa|ed25519|ecdsa|dsa)($|[\s\"'`;<>|&])",
    r"(^|[\s\\/=\"'`:])authorized_keys($|[\s\"'`;<>|&])",
    r"(^|[\s\\/])\.npmrc($|[\s\"'`;<>|&])",
    r"(^|[\s\\/])\.aws([\\/]|$)",
]

ASK_PATTERNS = [
    r"\bgit\b[^\n]*\bpush\b[^\n]*(\s--force\b|\s-f\b|\s--force-with-lease\b)",
    r"\bgit\b[^\n]*\s--no-verify\b",
    r"\bgit\b[^\n]*\breset\b[^\n]*\s--hard\b",
]

DENY = [re.compile(p, re.IGNORECASE) for p in DENY_PATTERNS]
ASK = [re.compile(p, re.IGNORECASE) for p in ASK_PATTERNS]


def walk_strings(node):
    """Yield every string found anywhere in the decoded payload."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from walk_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk_strings(value)


def decide(payload):
    """Return (decision, reason) or None when the call needs no intervention."""
    for text in walk_strings(payload):
        normalized = text.replace("\\", "/")
        snippet = text[:120].replace("\n", " ")
        for pattern in DENY:
            if pattern.search(normalized):
                return "deny", "resource holding credentials: " + snippet
        for pattern in ASK:
            if pattern.search(text):
                return "ask", "irreversible git operation needs explicit approval: " + snippet
    return None


def main():
    # Windows text-mode stdin decodes as the ANSI code page and raises on UTF-8
    # input, so decode the raw buffer explicitly.
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        payload = json.loads(raw)
    except Exception:
        return  # fail open

    verdict = decide(payload)
    if verdict:
        decision, reason = verdict
        print(json.dumps({"permissionDecision": decision, "permissionDecisionReason": reason}))


if __name__ == "__main__":
    main()
