# dsa-library

Placeholder README, replaced in step 9.

<!-- rules:start -->
| Rule | Severity | Check |
| --- | --- | --- |
| D1 | error | Every content file is `concepts/`, `problems/` or `discussions/` + `<slug>.md`; filename = `slug`; slug matches the format; no other files in those folders |
| D2 | error | Slugs are unique across all kinds; no slug equals a key in `redirects.json` |
| D3 | error | Front matter parses and passes its JSON Schema; `kind` matches the folder; required fields present; unknown keys only with an `x_` prefix |
| D4 | error | Only the seven link fields from section 7 are used, each on its allowed kind |
| D5 | error | Every link target exists, or resolves through a redirect (resolving is a warning); the target is of the right kind for that field |
| D6 | error | No cycles in `prerequisites`, `variant_of` or `follow_up_of`; no self-links in any field |
| D7 | error | A symmetric pair (`related`, `similar`) is not stored in both files |
| D8 | error | No duplicate entries inside a link, tag or alias list |
| D9 | error | Each `(source, source_id)` pair is unique; the slug prefix matches `source`; `url` matches the source's pattern |
| D10 | error | A discussion's `about` has at least 2 distinct items after resolving redirects |
| D11 | error | Topic keys are unique unless one file of the pair names the other in `distinct_from` |
| D12 | warning | One discussion's link set is a strict subset of another's |
| D13 | warning | Link-set Jaccard >= 0.75, or question/title similarity >= 0.85 |
| D14 | error | Aliases are unique, lowercase-unique, and never equal to an existing slug or title of another item |
| D15 | error | `show_on` values are in `config/sites.json`; `tags` are in `config/tags.json` |
| D16 | error | `api/v1/` and the README rule list are exactly what the generator produces now (`--check` mode) |
| D17 | error offline / warning online | `xrefs` match `<alias>:<path>` with a registered alias (offline); the target exists (online, CI only) |
| D18 | error | Redirect sources have no file; redirect targets exist; no chains or loops (A->B->C must be written as A->C) |
| D19 | error | `created` <= `updated`; both are valid dates, not in the future; a discussion's slug date equals `created` |
| D20 | error | No secrets in content, config, docs or templates; no file over 1 MB in content folders |
<!-- rules:end -->
