---
slug: 2026-11-17-why-greedy-fails-coin-change
kind: discussion
title: Why greedy fails for coin change
summary: Counter-examples, and why dynamic programming is needed unless the coin system is canonical.
question: Why does picking the largest coin first fail for some coin systems?
about: [coin-change, dynamic-programming, greedy]
tags: [greedy, dynamic-programming]
status: answered
show_on: []
created: 2026-11-17
updated: 2026-11-17
---

## Question

Why does taking the largest coin that fits, again and again, sometimes give more coins than necessary?

## Short answer

The largest coin is a locally best move, but nothing guarantees it belongs to an optimal solution. For some coin systems it does not, so the greedy answer can be beaten.

## Reasoning / proof

A greedy rule is safe only if an exchange argument shows that some optimal solution contains the greedy choice. For the coin system {1, 5, 10, 25} that argument holds. For general systems it does not, and `dynamic-programming` checks every last-coin choice instead.

## Counter-examples

Coins {1, 3, 4} and target 6: greedy takes 4 then 1 then 1 (three coins), but 3 + 3 uses two.

Coins {1, 5, 6} and target 10: greedy takes 6 then four 1s (five coins), but 5 + 5 uses two.

## Takeaways

- Never use `greedy` on `coin-change` without checking the coin system is canonical.
- When unsure, use the dynamic-programming recurrence: it is correct for every system.
