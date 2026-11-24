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

### 2026-11-24 — Worked example, full operations table, six lenses

**Worked example.** `a = [5, 1, 4, 2]`, 4-byte ints, `base = 1000`: addresses 1000, 1004, 1008, 1012. `a[3]` is `1000 + 3 * 4 = 1012`, one multiply and one add. `insert(1, 9)` shifts indices 3, 2, 1 one slot right (from the back, so nothing is overwritten), then writes 9, giving `[5, 9, 1, 4, 2]`: n - i = 3 moves. A 2-D row-major `a[i][j]` with R rows and C columns sits at `base + (i * C + j) * size`.

**Operations** (n = length; the dynamic column is covered in dynamic-array):

| Operation | Static array | Dynamic array |
| --- | --- | --- |
| read/write `a[i]` | O(1) | O(1) |
| append at end | not supported | O(1) amortized, O(n) worst |
| insert/delete at i | O(n - i) | O(n - i) |
| search unsorted | O(n) | O(n) |
| search sorted (binary search) | O(log n) | O(log n) |
| space | O(n) | O(n), capacity at most about 2n with doubling |

**Interview prep.** One-line explanation: contiguous memory, so indexing is O(1) by address arithmetic, but changing the structure in the middle is O(n) because of shifting. Patterns that run on arrays:

| Signal in the problem | Pattern |
| --- | --- |
| sorted input, pair or triple sum | two-pointers |
| contiguous subarray under a limit | sliding-window |
| many range-sum queries | prefix sums |
| many range updates, then reads | difference array |
| maximum subarray sum | Kadane's algorithm |
| values in 1..n, find missing or duplicate | cyclic sort, or index as hash (negate `a[v - 1]`) |
| partition by 2 or 3 keys in place | Dutch national flag |
| first or last position where a monotone condition holds | binary search |
| next greater or smaller element | monotonic stack |

Common follow-ups: O(1) extra space or in place; sorted, duplicates or negatives; data too big for memory or arriving as a stream; overflow of sums.

**Competitive programming.**
- 256 MB holds about 6.4e7 32-bit ints or 3.2e7 64-bit ones; `int[5000][5000]` is 100 MB.
- C++ global arrays are zero-initialised and not limited by stack size; a large local array overflows the stack (runtime error).
- Prefix array with a sentinel: `p[0] = 0`, `p[i + 1] = p[i] + a[i]`, sum of `a[l..r]` = `p[r + 1] - p[l]`, no special case for `l = 0`.
- Coordinate compression: values up to 1e9 but only n distinct, so sort, dedupe and map to indices 0..n-1.
- Counting array instead of sorting or hashing when the value range is up to about 1e7.
- Python: read input with `sys.stdin.buffer`, build lists with comprehensions, use `itertools.accumulate` for prefix sums.

**Theory and proofs.**
- O(1) access relies on the RAM model: address arithmetic and reading any cell are unit cost.
- Searching an unsorted array is Ω(n) by an adversary argument: if fewer than n cells are read, the adversary places the target in an unread cell or nowhere, and both answers are consistent with what was read.
- Searching a sorted array is Ω(log n) comparisons: the decision tree needs n + 1 leaves (n positions plus "absent"), so its depth is at least log2(n + 1).
- Amortized O(1) append for dynamic arrays is proved in dynamic-array and amortized-analysis.

**Real-world systems.**

| Where | How arrays are used |
| --- | --- |
| Operating systems | page tables indexed by virtual page number, file descriptor tables, interrupt vector table |
| Networking | NIC receive and transmit ring buffers (circular arrays indexed mod size) |
| Databases | column stores such as Apache Arrow and Parquet keep each column as a typed array; B-tree nodes are sorted arrays of keys |
| Compilers and runtimes | stack frames, `switch` jump tables, bytecode arrays, vtables |
| Structures built on arrays | binary heap, open-addressing hash table, circular deque, Fenwick tree, segment tree |
| GPUs and ML | tensors are flat arrays plus shape and stride metadata (NumPy, PyTorch) |

**Memory and performance.**
- A cache line is 64 bytes (16 ints). A sequential scan uses every byte fetched, and the hardware prefetcher detects the stride. A linked list has the same O(n) traversal but jumps to scattered addresses, often 10x or more slower in practice.
- Row-major (C, C++, NumPy default) vs column-major (Fortran, MATLAB, Julia): the inner loop should walk the contiguous dimension. In C, `for i: for j: a[i][j]` is sequential; swapping the loops strides a whole row per step.
- Array of structs vs struct of arrays: separate `xs[]`, `ys[]`, `zs[]` win when a loop touches one field, and vectorise better.
- Contiguous same-typed data allows SIMD: 4 to 16 elements per instruction with AVX2 or AVX-512, often auto-vectorised by the compiler.
- A Python `list` is an array of pointers to objects, so values are not contiguous; `array.array` and NumPy store raw values, about 4 to 8 times smaller and cache-friendly.

**Dynamic arrays.** Growth factors, resize rules and the 1.5x vs 2x argument are in dynamic-array.

**More pitfalls.**
- Mixing half-open `[l, r)` and closed `[l, r]` ranges; pick one convention per problem.
- Python `[[0] * m] * n` makes n references to the same row; use `[[0] * m for _ in range(n)]`.
- Python `a[-1]` silently returns the last element, hiding bugs where an index reaches -1.
- `int` overflow on sums in C++ and Java; use 64-bit types.

**Often confused with.** Linked list (O(1) splice, no O(1) indexing); Python `list` (a dynamic array of pointers); `array.array` and NumPy arrays (typed and contiguous).
