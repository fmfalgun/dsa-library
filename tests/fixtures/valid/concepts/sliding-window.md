---
slug: sliding-window
kind: concept
title: Sliding window
summary: Maintain a contiguous range and update its answer incrementally as the range moves.
type: technique
aliases: [moving window]
prerequisites: [arrays]
related: [two-pointers]
complexity:
  slide-one-step: {time: "O(1) amortized", space: "O(1)"}
tags: [arrays, strings, sliding-window]
status: draft
show_on: []
created: 2026-11-18
updated: 2026-11-18
---

## Intuition

When the question is about every contiguous range of some kind, consecutive ranges share almost all their elements. Reuse the previous answer: add the element that enters, remove the one that leaves.

## How it works

Keep `left` and `right` indices and a summary of the elements between them (a sum, a count map, a deque). Extend `right` one step at a time; move `left` forward while the window breaks the condition (variable size) or after every step (fixed size).

## Operations and complexity

Each index moves at most n times, so the whole scan is O(n) time. Space depends on the summary: O(1) for a sum, O(k) for a count map or deque.

## Implementation

Fixed size k: build the first window, then loop `i` from `k` to `n - 1`, adding `a[i]` and removing `a[i - k]`.

## Variants

- Fixed-size window.
- Variable-size window (longest or shortest range satisfying a condition).
- Windows whose summary is not invertible (maximum, minimum): use a `monotonic-deque`.

## When to use / signals in a problem

"Subarray" or "substring", "every window of size k", "longest/shortest range such that...", and all elements non-negative when sums are involved.

## Pitfalls

- Variable windows with negative numbers: shrinking no longer restores validity, so use prefix sums instead.
- Off-by-one when removing `a[i - k]`.

## Notes

Closely related to `two-pointers`: a variable window is two pointers moving the same way.
