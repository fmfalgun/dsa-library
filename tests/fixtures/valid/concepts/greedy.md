---
slug: greedy
kind: concept
title: Greedy algorithms
summary: Build a solution by repeatedly taking the locally best choice, valid only when that choice is provably safe.
type: paradigm
aliases: [greedy approach, greedy choice]
tags: [greedy, proofs]
status: stub
show_on: []
created: 2026-11-18
updated: 2026-11-18
---

## Intuition

At each step commit to the choice that looks best right now and never revisit it. It is fast and simple, but only correct when a local best is always part of some global best.

## How it works

Argue correctness with an exchange argument (any optimal solution can be changed to use the greedy choice without getting worse) or by showing the greedy solution stays ahead.

## Operations and complexity

Usually dominated by a sort: O(n log n).

## Implementation

Stub.

## Variants

Stub: interval scheduling, Huffman coding, Kruskal and Prim.

## When to use / signals in a problem

An optimization problem where a sort order or priority queue suggests an obvious next choice. If you cannot prove the choice safe, suspect `dynamic-programming`.

## Pitfalls

A plausible greedy rule with no proof. See the coin-change discussion for a standard counter-example.

## Notes

Stub.
