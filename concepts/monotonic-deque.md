---
slug: monotonic-deque
kind: concept
title: Monotonic deque
summary: A double-ended queue kept sorted so the front always holds the window's maximum or minimum.
type: data-structure
aliases: [monotone queue]
prerequisites: [arrays]
complexity:
  push: {time: "O(1) amortized", space: "O(k)"}
  query-front: {time: "O(1)", space: "O(1)"}
tags: [arrays, stacks-queues, sliding-window]
status: draft
show_on: []
created: 2026-11-18
updated: 2026-11-18
---

## Intuition

If a newer element is at least as large as an older one, the older one can never be the maximum of any window that still contains the newer one, because the newer one leaves later. So drop the older element for good.

## How it works

Store indices, not values. For a maximum deque: before pushing index `i`, pop from the back while `a[back] <= a[i]`; push `i`; pop from the front while the front index has left the window. The front is the maximum.

## Operations and complexity

Each index is pushed once and popped once, so n operations cost O(n) in total: amortized O(1) each. Space is at most the window size k.

## Implementation

Use `collections.deque` in Python or `std::deque` in C++.

## Variants

Use `>=` and the opposite comparison for a minimum deque; the same shape with a stack (no front removal) is the monotonic stack.

## When to use / signals in a problem

A moving window and a query for its maximum or minimum, or any DP transition of the form `max over the last k states`.

## Pitfalls

- Storing values loses the index you need for expiry.
- Mixing `<` and `<=` changes how ties are handled; both work for the maximum but pick one and be consistent.

## Notes

Used by `sliding-window` when the summary is not invertible.
