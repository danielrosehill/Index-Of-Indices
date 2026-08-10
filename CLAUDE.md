# CLAUDE.md — Subindices

Meta-index of Daniel's own indexing repositories. Formerly named
`Index-Of-Indices`; the old name still resolves via GitHub's rename redirect,
so external references to it are not necessarily broken — but new references
should use `Subindices`.

## The two halves

| File | Role |
| --- | --- |
| `README.md` | **Source of truth.** Human-facing list, one H3 per index repo. |
| `indices.json` | **Generated.** Machine-readable mirror, consumed downstream. |

`indices.json` is read by the master index repo — `danielrosehill/Index`,
`scripts/sync-indexing-repos.py` — which writes it to `indexing-repos.json`
and `private/indexing-repos.md` there and renders the "Index of Indexes"
section of its README. Only the `url` field is actually consumed downstream;
`title` and `description` are display-only.

## Adding an index repo

1. Add an H3 block to `README.md`, in the existing shape:

   ```markdown
   ### Repo-Name-Index

   One-sentence description.

   [![View Repo](https://img.shields.io/badge/View-Repo-blue?style=flat&logo=github)](https://github.com/danielrosehill/Repo-Name-Index)
   ```

2. Run `python3 scripts/build-indices-json.py`.
3. Commit both files together.

Never hand-edit `indices.json`. The parser keys on the exact block shape
above: H3 heading = repo slug, blank line, description paragraph, blank line,
View Repo badge. It warns if a heading and its link disagree.
`--check` exits non-zero when the JSON is stale, for use in CI.

## Scope

This indexes **Daniel's own project indexes**. Repos named `*-Resources`
generally index *external* material rather than his own projects and belong
in `Resources-Lists-Index` instead — that boundary is deliberate, so do not
"fix" their absence here.

Private index repos are deliberately absent: this repo is public.

## Known trap — verify links, don't assume

A renamed GitHub repo keeps answering on its old slug via redirect, so a stale
entry looks healthy. Check the resolved name, not the status code:

```bash
jq -r '.indices[].url' indices.json | sed 's|.*/||' | while read r; do
  fn=$(gh api "repos/danielrosehill/$r" --jq '.full_name' 2>/dev/null)
  [ -z "$fn" ] && echo "DEAD  $r"
  [ -n "$fn" ] && [ "$fn" != "danielrosehill/$r" ] && echo "MOVED $r -> $fn"
done
```

This is how the 2026-08-10 audit found `Ideas-Index` had been deleted
outright (404) while `Awesome-List-Repos-Index`, `Claude-Code-Repos-Index`
and `Github-Master-Index` had all been renamed and were still listed under
their old slugs in `indices.json`.
