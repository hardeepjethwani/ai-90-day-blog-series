#!/usr/bin/env python3
"""A tiny next-token predictor using only Python's standard library.

This is not an LLM. It is a small bigram model that makes the central idea
visible: learn which tokens tend to follow other tokens, then predict the next
token from counts.
"""

from collections import Counter, defaultdict
import random
import re


TOKEN_RE = re.compile(r"\w+|[^\w\s]")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def train(corpus: str) -> dict[str, Counter[str]]:
    tokens = ["<start>"] + tokenize(corpus) + ["<end>"]
    transitions: dict[str, Counter[str]] = defaultdict(Counter)

    for current_token, next_token in zip(tokens, tokens[1:]):
        transitions[current_token][next_token] += 1

    return transitions


def distribution(model: dict[str, Counter[str]], token: str) -> list[tuple[str, float]]:
    counts = model.get(token.lower(), Counter())
    total = sum(counts.values())
    if total == 0:
        return []

    return sorted(
        ((next_token, count / total) for next_token, count in counts.items()),
        key=lambda item: item[1],
        reverse=True,
    )


def generate(model: dict[str, Counter[str]], start: str, max_tokens: int = 16) -> str:
    output = tokenize(start)
    current = output[-1] if output else "<start>"

    for _ in range(max_tokens):
        options = distribution(model, current)
        if not options:
            break

        tokens = [token for token, _ in options]
        weights = [weight for _, weight in options]
        current = random.choices(tokens, weights=weights, k=1)[0]

        if current == "<end>":
            break

        output.append(current)

    return " ".join(output).replace(" .", ".").replace(" ,", ",")


if __name__ == "__main__":
    corpus = """
    llms predict the next token.
    llms use context to answer questions.
    context helps llms avoid nonsense.
    software engineers use llms to explain code.
    code needs tests because confidence is not correctness.
    """

    model = train(corpus)

    print("Distribution after 'llms':")
    for token, probability in distribution(model, "llms"):
        print(f"  {token:>8}  {probability:.0%}")

    print("\nGenerated text:")
    print(generate(model, "llms"))
