#!/usr/bin/env python3
"""Tiny tokenizer demo.

Real LLM tokenizers are more advanced. This intentionally simple script shows
the core idea: a model processes chunks of text, not raw human vibes.
"""

import re


TOKEN_RE = re.compile(r"\w+|[^\w\s]")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


if __name__ == "__main__":
    text = "LLMs don't read like humans; they read tokens."

    print("Input:")
    print(text)
    print("\nToy tokens:")
    for index, token in enumerate(tokenize(text)):
        print(f"{index:02d}: {token!r}")
