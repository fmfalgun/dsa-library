# Authoring workflow (the Claude DSA project)

The Claude project creates new files or appends sections to existing ones, and
never changes the links in existing files.

## Inputs Claude reads

Upload these as project knowledge and refresh them after each push:

- `api/v1/index.json` (or `search.json` once the index gets too large)
- `config/sources.json`, `config/tags.json`, `config/sites.json`
- `docs/CONTENT_FORMAT.md`

## On `/save`, Claude must

1. Split the session into items: concepts first, then problems, then discussions.
2. For each item, look up its slug, `(source, source_id)`, aliases and topic key
   in the index.
   - Item is new: create a file from the matching `templates/` skeleton.
   - Item exists: output an "add section" patch for that file with the new
     sections and a new `updated` date. Never output a second file.
3. Store symmetric links only in the new file. Store only outgoing links. Never
   write `api/` or `config/redirects.json`.
4. Use only tags already in `config/tags.json`. Propose a new tag separately as
   a one-line patch to that file.
5. End with a checklist: files created, patches to apply, guessed values to
   confirm, and the commands

   ```
   python ci/sync_index.py
   git add . && git commit -m "dsa: <summary>" && git push
   ```

## Before saving a discussion

Search `index.json` for the topic key (the sorted, `|`-joined `about` slugs) and
for questions that mean the same thing. If one exists, add a dated section to it
instead of creating a file. If the topic only looks similar, add `distinct_from`
with a reason of at least 10 characters.

## Templates

`templates/*.md` match the body sections in `CONTENT_FORMAT.md`. Claude fills
them; `python ci/sync_index.py --new <kind> <slug>` copies them.

## Commit hook

The pre-commit hook blocks secrets, checks for force-based commands in scripts,
validates content and regenerates `api/` and the README rule list. It is never
bypassed: fix the cause.
