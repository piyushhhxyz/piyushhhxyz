# How the profile card is built

`README.md` is a single image. That image is `dark_mode.svg` / `light_mode.svg`,
regenerated every day by [`.github/workflows/build.yaml`](.github/workflows/build.yaml)
so the numbers on it never go stale.

```
assets/avatar.png ──> tools/make_ascii.py ──> assets/ascii_art.txt ─┐
                                                                    ├─> render.py ──> *.svg
config.json (the static rows) ──────────────────────────────────────┤
GitHub GraphQL ──> stats.py ──> cache/stats.json ───────────────────┘
```

## Editing the text

Everything on the right-hand panel comes from `config.json`. Add, remove or
reorder rows there; the dot leaders re-flow automatically and the card widens if
a value needs more room. `{age}` in a value is replaced with your account age.

## Changing the portrait

Drop a new photo at `assets/avatar.png` and run:

```sh
./tools/regenerate_art.sh
```

The flags in that script are tuned for the current photo. If a new one comes out
muddy, the knobs worth turning first are `--crop` (frame the head and shoulders),
`--contrast`, and `--ink` (how much of the background falls away). Run
`python3 tools/make_ascii.py --help` for the rest.

## The line count

`stats.py` walks every repository you own or contribute to and sums the
additions and deletions on commits you authored. Two things are deliberately
left out, because counting them puts the total off by more than 10x:

* **Vendored and generated directories** — any repo with `node_modules/`,
  `dist/`, `vendor/`, `.vite/` and friends checked in is dropped automatically.
* **`exclude_repos` in `config.json`** — for repos full of generated artifacts
  that no path heuristic catches, such as benchmark trajectory dumps.

Every excluded repo is printed in the workflow log, so nothing disappears
quietly. Currently ~18 repos are excluded and the remaining count is real.

## Running it locally

```sh
pip install -r requirements.txt
ACCESS_TOKEN=$(gh auth token) python3 stats.py   # writes cache/stats.json
python3 render.py                                # writes the two SVGs
```

Results are cached per repository, keyed by the commit at the tip of its default
branch, so a second run costs a handful of API calls instead of ~150. Delete
`cache/` to force a full recount.

## The token

The workflow prefers a repository secret named `ACCESS_TOKEN` (a personal access
token with `repo` scope), which lets private contributions count toward the
totals. Without it, the workflow falls back to the built-in `GITHUB_TOKEN` and
measures public activity only.
