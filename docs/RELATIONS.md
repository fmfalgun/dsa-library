# Relation model

Every link is written once, in the front matter of the file that owns it. The
generator computes every reverse link. Saving a new item therefore never
requires editing an existing file.

```
discussion --about--> problem | concept | discussion   (2 or more)
problem    --uses---> concept
problem    --similar (symmetric)--> problem
problem    --follow_up_of--------->  problem
concept    --prerequisites-------->  concept
concept    --variant_of----------->  concept
concept    --related (symmetric)--> concept
```

| Field | Stored in | Points to | Cardinality | Reverse name in index | Graph rule |
| --- | --- | --- | --- | --- | --- |
| `uses` | problem | concept | many | `used_by` | none |
| `similar` | problem | problem | many | `similar` (both sides) | symmetric, no self-link |
| `follow_up_of` | problem | problem | one | `follow_ups` | no cycles |
| `prerequisites` | concept | concept | many | `required_by` | no cycles |
| `variant_of` | concept | concept | one | `variants` | no cycles |
| `related` | concept | concept | many | `related` (both sides) | symmetric, no self-link |
| `about` | discussion | any kind | 2 or more | `discussed_in` | none |

No other link fields exist. A new relation type needs a spec change, schema
updates and a minor version bump.

## Ownership

The more specific item owns the link and points to the more general one.

## Symmetric links

`related` and `similar` are one fact between two items, so store the link in
only one file: the one created later (the target must already exist). Never
edit the older file. The checker fails if both files carry the pair (D7). It
does not guess which file is newer.

## Redirects

`config/redirects.json` maps `old-slug` to `new-slug` and is never pruned.
Write `A -> C`, never `A -> B -> C` (D18). Links to an old slug resolve to the
new one in the index, with a warning (D5) so the link can be updated.

## Cross-repo references

`xrefs` use `<alias>:<path>`, e.g. `library-data:people/edsger-w-dijkstra`.
The alias must be in `config/repos.json`. The path resolves to
`<base_url>data/<path>.json`. Online checks only warn.

## Duplicate discussions

The topic key is the `about` list after redirects, de-duplicated, sorted and
joined with `|`. Two discussions with the same key fail D11 unless one names the
other in `distinct_from` with a reason. Subset (D12) and look-alike (D13)
overlaps only warn, and are not raised for pairs declared distinct.

To merge duplicates: keep the older file, move the other's unique content into
it as new sections, union `about`, `sources` and `tags`, delete the other file,
add `"<deleted>": "<survivor>"` to `config/redirects.json`, update `updated`,
run the sync script. A merge is the one action that edits existing files and
is always done on purpose.
