# dsa-library

Everything I learn about data structures and algorithms, stored as linked
Markdown files. Every idea lives in exactly one file, every link is stored
once, and a generated JSON index serves the whole graph to any site or tool.

Consumer URL: <https://fmfalgun.github.io/dsa-library/api/v1/index.json>
(slim list: `.../api/v1/search.json`). Consumer guide: [docs/INTEGRATION.md](docs/INTEGRATION.md).

## Setup

1. Install the commit hook (first step, always): `git config core.hooksPath ci/hooks`
2. Create the virtual environment: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
3. Optional: put a `gitleaks` binary at `.tools/bin/gitleaks` (or on `PATH`); the hook uses it for a token scan.
4. Check everything: `.venv/bin/python ci/sync_index.py` then `.venv/bin/python -m pytest`

The hook is never bypassed. Fix what it reports.

## Layout

```
concepts/     one file per concept            problems/     one file per problem
discussions/  cross-cutting discussions       solutions/    optional runnable code
api/v1/       GENERATED, never edit by hand   schema/       JSON Schemas (source)
config/       sites, sources, repos, tags, redirects
templates/    skeletons for new items         docs/         format, relations, integration, authoring, decisions
ci/           sync_index.py, dsa_lib/, hooks/ tests/        pytest + one failing fixture per rule
```

The three content folders and `tests/fixtures/` deliberately hold more than 9
files; see "Directory-size rule" in [docs/DECISIONS.md](docs/DECISIONS.md) for
the reasons, limits and mitigations.

## Add an item

1. `python ci/sync_index.py --new <concept|problem|discussion> <slug>`
2. Fill the front matter and the body sections (see [docs/CONTENT_FORMAT.md](docs/CONTENT_FORMAT.md)). Use plain front-matter links only ([docs/RELATIONS.md](docs/RELATIONS.md)).
3. `python ci/sync_index.py` (validates, then writes `api/v1/` and the rule list below)
4. `git add . && git commit -m "dsa: <summary>" && git push` (the hook runs the same checks)

Other commands: `--check` (fail if generated files are stale), `--online`
(also verify cross-repo `xrefs`, warnings only), `--explain <slug>` (show an
item's links in both directions and look-alike warnings).

## Known concern: prose is not in the JSON

`index.json` holds metadata and links only, not the Markdown bodies, so a
consumer that wants an item's explanation has to fetch the `.md` file. We
accepted that on purpose. If it becomes a real problem, we will consider a
per-item `api/v1/items/<slug>.json` that includes the body (a minor-version
addition). See [docs/INTEGRATION.md](docs/INTEGRATION.md).

## Validation rules

Generated from `ci/dsa_lib/rules.py`; do not edit between the markers.

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
