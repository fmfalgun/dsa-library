---
slug: amortized-analysis
kind: concept
title: Amortized analysis
summary: Bounds the average cost per operation over a worst-case sequence, so rare expensive steps are paid for by many cheap ones.
type: math
aliases: [amortised analysis, amortized cost]
tags: [complexity, proofs]
status: stub
show_on: [portfolio]
created: 2026-11-24
updated: 2026-11-24
---

## Intuition

Some operations are usually cheap but occasionally expensive, like an append that triggers a resize. Amortized analysis proves that any sequence of m operations costs at most m times some bound, even though a single operation may exceed it. Unlike average-case analysis, it uses no probability: the bound holds for every input sequence.

## How it works

Three standard methods:

- Aggregate: bound the total cost T(m) of any m operations, then the amortized cost is T(m) / m.
- Accounting (banker's): charge each operation a fixed fee; cheap operations store credit that later pays for expensive ones. Credit must never go negative.
- Potential: define a potential Phi(state) that never drops below its starting value. Amortized cost = actual cost + Phi(after) - Phi(before). The sum of amortized costs bounds the sum of actual costs.

Worked example, dynamic array with doubling (n elements, capacity cap):

- Aggregate: n appends copy 1 + 2 + 4 + ... < 2n elements in total, plus n writes, so O(n) total and O(1) each.
- Potential: Phi = 2n - cap. An append without a resize costs 1 and raises Phi by 2, so amortized cost 3. An append with a resize (n = cap) costs n + 1, and Phi goes from 2n - n = n to 2(n + 1) - 2n = 2, so amortized cost n + 1 + 2 - n = 3. Every append is amortized O(1).

## Operations and complexity

Standard amortized bounds:

| Structure / operation | Amortized | Worst single |
| --- | --- | --- |
| dynamic-array append (doubling) | O(1) | O(n) |
| binary counter increment | O(1) | O(log n) |
| stack with multipop, per operation | O(1) | O(n) |
| union-find with path compression and union by rank | O(alpha(n)) | O(log n) |

## Implementation

Not code: a proof technique. To use it, pick a potential that grows during cheap steps and drops by about the cost of each expensive step.

## Variants

Aggregate, accounting and potential methods (above). Self-adjusting structures such as splay trees are analysed with the potential method.

## When to use / signals in a problem

- A loop looks like O(n^2) but each element enters and leaves a structure at most once (monotonic stack or deque, two pointers): the total is O(n).
- Rebuilds or resizes that happen geometrically less often.

## Pitfalls

- Amortized O(1) is not worst-case O(1): one operation can still be slow, which matters for latency-critical code.
- Amortized is not average case: no randomness is involved.
- A potential that can go negative breaks the proof.
- Shrinking a dynamic array at half full breaks the bound (push/pop at the boundary resizes every time); shrink at a quarter.

## Notes

Created as a link target from the arrays session on 2026-11-24. Only the dynamic-array example was explored; the other table rows are standard textbook results not worked through yet.
