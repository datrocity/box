# box

Experiment-first research catalog for scientists. Give research results a persistent, queryable identity tied to the params and code that produced them.

`box` is a small Python library shaped as a computing primitive, not an organizing tool. Lineage, versioning, smart caching, and meta-analysis fall out of a handful of explicit calls in the flow of normal notebook code.

## 1. Why box?

Every research project rediscovers the same problem: after enough experiments, `results/` turns into `run3_final.csv`, `run3_final_FIXED.csv`, `sweep_lr0.01/`, and a git history that no longer matches what actually produced any of them. Six months later, nobody — including you — can answer "which params made this plot?" or "what code produced this array?"

`box` answers that by giving every saved result an explicit identity: which **project** it belongs to, which **experiment** (a name plus the exact params) produced it, which git commit and author, and when. That identity travels with the file rather than living in a database you might lose. A compact "business card" of it — project, experiment, params, git commit, author, timestamp — is embedded directly in the data file itself whenever the format allows (parquet metadata, PNG text chunks, CSV comment lines), and the full record always lives in a small JSON file (`manifest.json`) saved right next to it. Nothing proprietary: `ls` the folder, `cat` the manifest, copy either file anywhere.

**Lineage** falls out for free: everything you `load()` inside an experiment is recorded as that experiment's cumulative inputs, and gets stamped into the manifest of anything you `save()` afterward. You can always ask "what fed into this?" without maintaining that trail by hand.

On disk, it looks like this:

    catalog/walker/                                    <- project
      global/                                          <- project-scope shared artifacts
        processed_input/
          v1.parquet
          v1.manifest.json
      2026-08-15__baseline__a3f18d02/                  <- experiment folder
        params.json
        manifest.json
        result/
          v1.parquet
          v1.manifest.json

Every experiment folder is self-contained: `params.json` reconstructs the params, and every artifact carries its own manifest, so a folder survives being copied or moved.

## 2. Projects, experiments, params, save/load

Four nouns, and you already know three of them:

- **Project** — a named workspace, one per research effort, rooted at a folder you choose.
- **Experiment** — one named run with frozen params. Identity is `(project, name, params)`: call it again with the same params and you reopen the same experiment; change a param and you get a new one.
- **Artifact** — anything you save (a DataFrame, an array, an image, a dict).
- **Version** — automatic. Saving identical data again doesn't create a new file, it just appends a run record; different data gets the next `v{N}`.

```python
import box

project = box.init("walker", datastore="./catalog")
exp = project.experiment("baseline", lr=0.01, prior="uniform")

# params flow from the experiment object -- no need to re-declare them
result = simulate(lr=exp.lr, prior=exp.prior)
exp.save(result, "result")

# ... later, even in a different session ...
exp.load("result")               # latest version
exp.load("result", version=1)    # a specific one, e.g. to reproduce an old plot
```

A **project-scope** save/load (`project.save(...)` / `project.load(...)`) works the same way, for things shared across every experiment — a preprocessed dataset, say — rather than belonging to one run.

`box` picks a storage format from the data's type:

| Python type | On-disk format | Notes |
|---|---|---|
| `pandas.DataFrame` | `.parquet` | default; preserves dtypes exactly |
| `pandas.DataFrame` | `.csv` | opt-in via `format="csv"`, human-readable |
| `numpy.ndarray` | `.npy` | |
| `dict` | `.json` | |
| `PIL.Image.Image` | `.png` | |

More types will be added over time. If you need one that isn't here, [open a GitHub issue](https://github.com/datrocity/box/issues).

See `notebook/01_walkthrough.ipynb` for a full walkthrough.

## 3. RunSets: meta-analysis across experiments

Once you've run a grid of experiments, `project.runs()` gives you a filterable, iterable view over all of them — this is where you stop hunting through folders and start querying:

```python
runs = project.runs()
hits = runs.where(lr=0.01, prior="uniform")

summary = hits.summarize(
    final_loss=lambda r: r.load("result")["loss"].iloc[-1],
)

# same experiment name, different params (the common grid pattern) --
# load_all returns pairs, so same-name runs never collide
for run, result in hits.load_all("result"):
    plot(result, label=f"lr={run.params['lr']}")
```

`where()` filters by exact param match; `frame()` / `summarize()` return a DataFrame with one row per run.

## 4. Caching with `@compute_or_load`

Expensive steps that don't change across a sweep — preprocessing, a slow simulation setup — shouldn't rerun for every experiment. `compute_or_load` is a decorator: the first call computes and saves, every later call (in this run or a future one) just loads:

```python
@project.compute_or_load("processed_input")    # project scope: shared across all experiments
def preprocess():
    return expensive_preprocessing()

data = preprocess()   # computed once, then just loaded from disk

@exp.compute_or_load("preprocessed")         # experiment scope: local to this one run
def local_step():
    ...
```

`compute_or_load` is just a shorthand for a `has()`/`load()`/`save()` check you could write yourself — spelled out manually, `preprocess()` above is:

```python
if project.has("processed_input"):
    data = project.load("processed_input")
else:
    data = expensive_preprocessing()
    project.save(data, "processed_input")
```

## 5. AI assistant support

`box` ships two skills (`box/skills/*.md`) that teach an AI coding assistant (Claude Code, Cursor, etc.) to use the library correctly:

- **Writing box code** — the four-noun API above, so an assistant writes `project.experiment(...)` / `exp.save(...)` correctly instead of guessing.
- **Importing messy data** — a guided workflow for turning a folder of years-old, inconsistently named CSVs, plots, and configs into a proper box catalog: the assistant inventories the folder, proposes a plan grouping files into candidate experiments, and only imports after you approve it.

Install them after `pip install box`:

    box install-skills                        # copies to ~/.claude/skills/box/
    box install-skills --dest ~/.some/place   # or a custom directory

For non-Claude tools, point the assistant at `AGENTS.md` in the source repo, or `python -c "import box; print(box.skills_path())"` if you'd rather symlink.

## Development

    make setup        # create poetry env
    make test          # run tests
    make lint          # ruff
    make format        # ruff format

## Requirements

Python 3.11+. Depends on numpy, pandas, pillow, pyarrow, joblib.

## License

BSD 3-Clause.
