---
slug: dynamic-array
kind: concept
title: Dynamic array
summary: An array that over-allocates and copies into a larger block when full, giving amortized O(1) append at the end.
type: data-structure
aliases: [resizable array, growable array, vector]
complexity:
  access: {time: "O(1)", space: "O(1)"}
  append: {time: "O(1) amortized, O(n) worst", space: "O(1) amortized"}
  pop-end: {time: "O(1) amortized", space: "O(1)"}
  insert-middle: {time: "O(n)", space: "O(1)"}
variant_of: arrays
prerequisites: [amortized-analysis]
tags: [arrays, complexity]
status: draft
show_on: [portfolio]
created: 2026-11-24
updated: 2026-11-24
---

## Intuition

A plain array cannot grow in place, because the memory right after it may already be taken. A dynamic array keeps a length `n` and a larger capacity `cap`. Appends fill the spare slots for free. When `n == cap`, it allocates a block `r` times bigger (usually 1.5 or 2), copies everything over and frees the old block. The rare O(n) copy is spread over the many cheap appends before it.

## How it works

State: a backing array of size `cap`, and `n` slots in use.

- `append(x)`: if `n == cap`, resize to `r * cap`; write `x` at index `n`; `n += 1`.
- `pop()`: `n -= 1`; if `n <= cap / 4`, resize to `cap / 2`.
- `insert(i, x)`: grow if full, shift `a[i..n-1]` one slot right (from the back), write `x`.

Trace with doubling, starting at cap 1: append 5, 1, 4, 2 grows cap 1 -> 2 -> 4. `insert(1, 9)` finds it full, grows to 8, shifts 3 elements and gives `[5, 9, 1, 4, 2]`. Three pops leave `n = 2 <= 8 / 4`, so it shrinks to cap 4.

## Operations and complexity

n = number of elements, r = growth factor.

| Operation | Time | Notes |
| --- | --- | --- |
| read/write `a[i]` | O(1) | address arithmetic, as in arrays |
| append | O(1) amortized, O(n) worst | worst case is the resize copy |
| pop at end | O(1) amortized | with the shrink-at-quarter rule |
| insert/delete at i | O(n - i) | shifting dominates |
| space | O(n) | capacity at most about r * n |

Doubling: over n appends the copies total 1 + 2 + 4 + ... < 2n, so total work is O(n). Any r > 1 gives total copies at most n / (r - 1). Growing by a constant c instead gives O(n^2) total, so O(n) per append. The potential-method proof is in amortized-analysis.

## Implementation

```python
class DynArray:
    def __init__(self):
        self.n, self.cap, self.a = 0, 1, [None]

    def _resize(self, cap):
        b = [None] * cap
        for i in range(self.n):
            b[i] = self.a[i]
        self.a, self.cap = b, cap

    def append(self, x):
        if self.n == self.cap:
            self._resize(2 * self.cap)
        self.a[self.n] = x
        self.n += 1

    def insert(self, i, x):
        if not 0 <= i <= self.n:
            raise IndexError
        if self.n == self.cap:
            self._resize(2 * self.cap)
        for j in range(self.n, i, -1):
            self.a[j] = self.a[j - 1]
        self.a[i] = x
        self.n += 1

    def pop(self):
        if self.n == 0:
            raise IndexError
        self.n -= 1
        x = self.a[self.n]
        self.a[self.n] = None
        if 0 < self.n <= self.cap // 4:
            self._resize(self.cap // 2)
        return x

    def __getitem__(self, i):
        if not 0 <= i < self.n:
            raise IndexError
        return self.a[i]
```

Verified by running the trace above on Python 3.13.

## Variants

Growth factors used by real implementations:

| Implementation | Growth |
| --- | --- |
| CPython `list` | about 1.125 * n + 6 (measured on 3.13: resizes at sizes 1, 5, 9, 17, 25, 33) |
| GCC/Clang `std::vector` | 2x |
| MSVC `std::vector` | 1.5x |
| Java `ArrayList` | 1.5x |
| Go slices | 2x up to 256 elements, then tapering toward 1.25x |

Only the CPython row was measured; the others are from memory and worth checking against the current sources.

Related structures built the same way: circular buffer / array deque (grows like this, indexes mod cap), and the gap buffer used by text editors.

## When to use / signals in a problem

- You need indexing plus growth at the end and do not know n in advance.
- Stacks: push and pop at the end are both O(1) amortized.
- Building an output list element by element.
- If n is known up front, preallocate (`[0] * n` in Python, `reserve(n)` in C++) to skip every resize.

## Pitfalls

- Amortized is not worst case: one append can cost O(n), which matters for hard real-time code.
- Shrinking at half full makes push/pop at the boundary resize every time (thrashing). Shrink at a quarter.
- In C++, a resize moves the buffer, so pointers, references and iterators into a `vector` can dangle after `push_back`.
- Insert or pop at the front is still O(n): `list.insert(0, x)` and `list.pop(0)` in Python. Use `collections.deque` for a queue.
- A Python `list` holds pointers to objects, so the values are not contiguous; `array.array` or NumPy store raw values.

## Notes

Why 1.5 instead of 2: with a growth factor below the golden ratio (about 1.618), the freed old blocks can eventually add up to enough space to reuse for a new block; with 2x they never do. The argument is sound, but how much it helps depends on the allocator, and I am not sure it matters much with modern allocators.
