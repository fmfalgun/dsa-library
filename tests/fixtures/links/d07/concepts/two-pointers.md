---
slug: two-pointers
kind: concept
title: Two pointers
summary: Move two indices through a sequence so each element is visited a bounded number of times.
type: technique
aliases: [two pointer technique]
prerequisites: [arrays]
related: [sliding-window]
tags: [arrays, two-pointers]
status: stub
show_on: []
created: 2026-11-18
updated: 2026-11-18
---

## Intuition

Instead of checking every pair (O(n^2)), keep two indices whose movement rules guarantee that no useful pair is skipped.

## How it works

Two common shapes: opposite ends moving inward (sorted array pair sum), and a fast and a slow index moving the same way (removing duplicates, cycle detection).

## Operations and complexity

Typically O(n) time and O(1) extra space, once any required sorting is paid for.

## Implementation

Stub.

## Variants

The same-direction form with a variable-size range is the `sliding-window` technique.

## When to use / signals in a problem

Sorted input, pairs or triples with a target sum, in-place partitioning, palindromes.

## Pitfalls

Forgetting that opposite-ends pointers need sorted input; moving the wrong pointer on ties.

## Notes

Stub.
