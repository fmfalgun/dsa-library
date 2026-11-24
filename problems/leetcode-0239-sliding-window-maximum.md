---
slug: leetcode-0239-sliding-window-maximum
kind: problem
title: Sliding Window Maximum
summary: Maximum of every window of size k in an array.
source: leetcode
source_id: "239"
url: https://leetcode.com/problems/sliding-window-maximum/
found_via: [neetcode-150]
difficulty: Hard
uses: [monotonic-deque, sliding-window]
languages: [python]
tags: [arrays, sliding-window]
status: solved
show_on: [portfolio]
created: 2026-11-18
updated: 2026-11-24
---

## Problem in my own words

Given an array of integers and a window size `k`, slide the window from the left end to the right end one step at a time. Return the largest value inside the window at every position.

## Constraints

Array length up to about 10^5, so an O(n * k) answer can time out. Check the judge page for the exact limits.

## Key observation

An element that is smaller than a newer element in the same window can never be the answer again, because the newer one outlives it. Only a decreasing sequence of candidates needs to be kept.

## Approaches

### Brute force

Take the maximum of each window directly. O(n * k) time, O(1) extra space.

### Heap with lazy deletion

Push `(-value, index)`, and discard heap tops whose index left the window. O(n log n) time, O(n) space.

### Optimal: monotonic deque

Keep indices in a deque with decreasing values; the front is the window maximum. O(n) time, O(k) space.

## Solution

```python
from collections import deque


def max_sliding_window(nums: list[int], k: int) -> list[int]:
    """Return the maximum of every length-k window of nums.

    Keeps a deque of indices whose values decrease from front to back, so
    the front is always the current window's maximum. O(n) time, O(k) space.
    """
    window: deque[int] = deque()
    result: list[int] = []
    for index, value in enumerate(nums):
        while window and nums[window[-1]] <= value:
            window.pop()
        window.append(index)
        if window[0] <= index - k:
            window.popleft()
        if index >= k - 1:
            result.append(nums[window[0]])
    return result
```

## Edge cases and pitfalls

- `k = 1`: every element is its own window maximum.
- `k` equal to the array length: one answer.
- Remove from the front by index, not by value: duplicate values are common.

## What this problem teaches

The `monotonic-deque` turns "maximum of a sliding window" into amortized O(1) per step, which a plain `sliding-window` sum cannot do because a maximum cannot be subtracted back out.
