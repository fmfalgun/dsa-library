# Content format

Every item is a UTF-8 Markdown file that starts with YAML front matter between
two `---` lines. The schemas in `schema/` are strict: an unknown key is an
error, except keys starting with `x_`, which are allowed and copied to
`extra` in the index.

Start a new file with `python ci/sync_index.py --new <kind> <slug>`, then fill
in every `TODO`. The checker reports the leftovers.

## Kinds and where they live

| Kind | Folder | Holds | Must not hold |
| --- | --- | --- | --- |
| concept | `concepts/` | How a data structure, algorithm, technique, pattern, paradigm or maths idea works | Walkthroughs of specific problems |
| problem | `problems/` | One problem: own-words summary, constraints, approaches, solution | Re-explanations of a concept: link it with `uses` |
| discussion | `discussions/` | One question or insight spanning two or more items | Anything about a single item |

## Slugs

The slug is the permanent ID and the filename without `.md`. Format
`^[a-z0-9]+(-[a-z0-9]+)*$`, at most 80 characters, unique across all kinds.

| Kind | Pattern | Example |
| --- | --- | --- |
| concept | `<name>` | `segment-tree` |
| problem with an ID | `<source>-<id>-<title>` | `leetcode-0239-sliding-window-maximum`, `codeforces-4a-watermelon` |
| problem without an ID | `<source>-<title>` | `interview-lru-with-ttl` |
| discussion | `<yyyy-mm-dd>-<title>` (date equals `created`) | `2026-11-17-why-greedy-fails-coin-change` |

LeetCode IDs are zero-padded to 4 digits; other judges' IDs are lowercased
(`4A` becomes `4a`). A2OJ ladder problems use their real judge as `source`
(usually `codeforces`) and record the ladder in `found_via`. Allowed sources
and URL patterns are in `config/sources.json`.

## Fields common to all kinds

| Field | Required | Rules |
| --- | --- | --- |
| `slug` | yes | Equals the filename |
| `kind` | yes | `concept`, `problem` or `discussion`; matches the folder |
| `title` | yes | At most 120 characters |
| `summary` | yes | One sentence, at most 200 characters |
| `tags` | no | Each in `config/tags.json` |
| `status` | yes | Per kind, below |
| `show_on` | no (default `[]`) | Values from `config/sites.json`; empty means hidden |
| `xrefs` | no | `<repo-alias>:<path>`, alias registered in `config/repos.json` |
| `refs` | no | List of `{label, url}` |
| `created` / `updated` | yes | `YYYY-MM-DD`; `created` never changes; `updated` is not earlier; neither in the future |

## Concept

Extra fields: `type` (required: `data-structure`, `algorithm`, `technique`,
`pattern`, `paradigm`, `math`), `aliases`, `complexity` (map of operation to
`{time, space}`), `prerequisites`, `variant_of`, `related`.
`status`: `stub`, `draft`, `solid`.

Body sections, in order: Intuition, How it works, Operations and complexity,
Implementation, Variants, When to use / signals in a problem, Pitfalls, Notes.

## Problem

Extra fields: `source` (required), `source_id` and `url` (required for judges),
`found_via`, `difficulty`, `uses` (required, at least one concept), `similar`,
`follow_up_of`, `languages`. `status`: `unsolved`, `attempted`, `solved`, `revisit`.

Body sections, in order: Problem in my own words, Constraints, Key
observation, Approaches, Solution, Edge cases and pitfalls, What this problem
teaches. Never paste the full statement: the summary plus `url` is enough.

## Discussion

Extra fields: `question` (required, one line, at most 200 characters, ends
with `?`), `about` (required, at least 2 slugs of any kind), `distinct_from`
(list of `{slug, reason}`, reason at least 10 characters), `sources`.
`status`: `open`, `answered`, `superseded`.

Body sections, in order: Question, Short answer, Reasoning / proof,
Counter-examples, Takeaways, then one dated section per follow-up (newest last).

## Links live in front matter only

Do not write links in the Markdown body as if they were relations. The only
relations are the front-matter fields in [RELATIONS.md](RELATIONS.md); mention
other items in prose by plain slug if you must.

## Published difference from the file

In `index.json` an item's `url` is the published `.md` address. A problem's
judge link is published as `problem_url` (see `DECISIONS.md`, decision 13).
