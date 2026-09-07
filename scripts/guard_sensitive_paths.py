#!/usr/bin/env python3
"""Copilot preToolUse hook: block tool calls that touch credential-bearing files.

Protocol: read the tool call as JSON on stdin, write a decision as JSON on stdout.
  {"permissionDecision": "deny", "permissionDecisionReason": "..."}
Emitting nothing leaves the normal permission flow untouched.

Copilot's stdin schema is not identical across surfaces, so this walks every string
in the payload instead of relying on specific key names. It fails open: any parse
error or unexpected shape allows the call rather than blocking work.
"""

import json
import re
import sys

PATTERNS = [
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

COMPILED = [re.compile(p, re.IGNORECASE) for p in PATTERNS]


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


def main():
    # Windows text-mode stdin decodes as the ANSI code page and raises on UTF-8
    # input, so decode the raw buffer explicitly.
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        payload = json.loads(raw)
    except Exception:
        return  # fail open

    for text in walk_strings(payload):
        normalized = text.replace("\\", "/")
        for pattern in COMPILED:
            if pattern.search(normalized):
                snippet = text[:120].replace("\n", " ")
                print(
                    json.dumps(
                        {
                            "permissionDecision": "deny",
                            "permissionDecisionReason": (
                                "resource holding credentials: " + snippet
                            ),
                        }
                    )
                )
                return


if __name__ == "__main__":
    main()
