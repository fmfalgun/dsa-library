---
slug: arrays
kind: concept
title: Arrays
summary: A contiguous block of same-sized elements addressed by index in constant time.
type: data-structure
aliases: [array, list (fixed-size)]
complexity:
  access: {time: "O(1)", space: "O(1)"}
  insert-middle: {time: "O(n)", space: "O(1)"}
  search-unsorted: {time: "O(n)", space: "O(1)"}
tags: [arrays]
status: stub
show_on: [portfolio]
created: 2026-11-18
updated: 2026-11-24
---

## Intuition

Elements sit next to each other in memory, so the address of element `i` is `base + i * size`. That is why indexing is O(1) and why inserting in the middle is O(n): everything after the gap must shift.

## How it works

A fixed block of memory; dynamic arrays (Python `list`, C++ `vector`) over-allocate and re-allocate when full, giving amortized O(1) appends.

## Operations and complexity

See the complexity table in the front matter.

## Implementation

Stub: use the language's built-in array or dynamic array.

## Variants

Stub: 2D arrays, circular buffers, sparse arrays.

## When to use / signals in a problem

Input is a sequence and positions matter; many problems add a window, two indices or a prefix array on top.

## Pitfalls

Off-by-one at the ends, mutating while iterating, assuming O(1) insert at the front.

## Notes

Stub: extend with cache-locality notes.
