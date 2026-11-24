---
slug: coin-change
kind: concept
title: Coin change
summary: Find the fewest coins (or the number of ways) that make a target amount from given denominations.
type: algorithm
aliases: [minimum coins]
prerequisites: [dynamic-programming]
related: [greedy]
complexity:
  min-coins-dp: {time: "O(amount * coins)", space: "O(amount)"}
tags: [dynamic-programming, greedy]
status: stub
show_on: [portfolio]
created: 2026-11-18
updated: 2026-11-24
---

## Intuition

The best way to make `x` ends with some coin `c`, and before that coin you were making `x - c` in the best possible way.

## How it works

`best[0] = 0`; for each amount `x` from 1 to the target, `best[x] = 1 + min(best[x - c])` over coins `c <= x` with a reachable `x - c`.

## Operations and complexity

O(amount * number of coins) time, O(amount) space.

## Implementation

Stub.

## Variants

Counting the number of combinations versus permutations changes the loop order.

## When to use / signals in a problem

A target built from unlimited items of fixed sizes.

## Pitfalls

Using the greedy rule on an arbitrary coin system. It works only for canonical systems such as 1, 5, 10, 25.

## Notes

Stub.
