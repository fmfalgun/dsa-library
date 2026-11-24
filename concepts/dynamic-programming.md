---
slug: dynamic-programming
kind: concept
title: Dynamic programming
summary: Solve a problem by combining answers to overlapping subproblems, each computed once.
type: paradigm
aliases: [dp]
related: [greedy]
tags: [dynamic-programming, recursion]
status: stub
show_on: [portfolio]
created: 2026-11-18
updated: 2026-11-24
---

## Intuition

If a problem splits into subproblems that repeat, store each answer the first time and reuse it. Time drops from exponential to the number of distinct subproblems times the work per subproblem.

## How it works

1. Define the state: what the subproblem is.
2. Write the transition: how a state follows from smaller states.
3. Fix the base cases and the order of evaluation (top-down with memoization, or bottom-up).

## Operations and complexity

States times transitions per state; space can often be reduced by keeping only the layers still needed.

## Implementation

Stub.

## Variants

Stub: knapsack, interval DP, bitmask DP, DP on trees.

## When to use / signals in a problem

Counting or optimizing over choices where a greedy rule fails and the same sub-case appears again and again.

## Pitfalls

A state that omits something the future depends on, giving wrong answers that look plausible.

## Notes

Stub.
