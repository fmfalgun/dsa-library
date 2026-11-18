# Integration guide for consumers

`dsa-library` is a publisher. It depends on no other repo to build, and no repo
depends on it. Other repos read its published JSON at runtime.

## URLs (fixed)

- `https://fmfalgun.github.io/dsa-library/api/v1/index.json`: the full graph
- `https://fmfalgun.github.io/dsa-library/api/v1/search.json`: slim list for search boxes
- `https://fmfalgun.github.io/dsa-library/api/v1/schema/*.json`: JSON Schemas

GitHub Pages serves these with permissive cross-origin headers, so a consumer
site can fetch them directly from the browser.

## Rules for consumers

1. Read only the JSON. Never parse the Markdown front matter.
2. Ignore unknown fields: minor versions only add fields.
3. Slugs never disappear. A renamed or merged slug stays in `redirects`.
4. Visibility is respected by consumers, not enforced. Show an item only when
   its `show_on` lists your site; the JSON contains every item. Nothing private
   belongs in this public repo.
5. Detect changes by comparing `content_hash`, or by listening for the optional
   `dsa-library-updated` repository_dispatch event.
6. A breaking change goes to a new `api/vN/`; `api/v1/` keeps being generated
   for at least 90 days after, with a `deprecated` notice in its index.

## Versioning

| Change | Bump | Where |
| --- | --- | --- |
| New items, edits to content | none (`content_hash` changes) | `api/v1/` |
| New optional field, link type, tag, site or source | minor (1.0 to 1.1) | `api/v1/` |
| Field removed or renamed, meaning or structure changed | major | new `api/v2/` |

## Example

```js
const BASE = "https://fmfalgun.github.io/dsa-library/api/v1/";
const idx = await (await fetch(BASE + "index.json")).json();
const resolve = s => idx.redirects[s] ?? s;
const shown = Object.entries(idx.items)
  .filter(([, it]) => it.show_on.includes("portfolio"));
```

## Known limitation: item prose is not in the JSON

`index.json` carries metadata and links, not the Markdown body. A consumer that
wants to render an item's explanation must fetch the `.md` file at the item's
`url`, which conflicts with rule 1. This was accepted on purpose (see
`DECISIONS.md`, decision 10). If it becomes a problem, the planned fix is a
per-item `api/v1/items/<slug>.json` that includes the body: a minor-version
addition that breaks nothing.

## Outbound references and notifications

`xrefs` point at records in other repos (for example library-data people).
Other repos are never edited to add reverse links; a consumer joins them itself.
`.github/workflows/notify.yml` can send `repository_dispatch` to repos with
`notify: true` in `config/repos.json`. It is off by default and needs a
`DISPATCH_TOKEN` secret.
