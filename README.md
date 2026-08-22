# box

Experiment-first research catalog for scientists. Give research results a persistent, queryable identity tied to the params and code that produced them.

`box` is a small Python library shaped as a computing primitive, not an organizing tool. Lineage, versioning, smart caching, and meta-analysis fall out of a handful of explicit calls in the flow of normal notebook code.

## Quickstart

    import pandas as pd
    import box

    proj = box.init("walker", datastore="./catalog")

    # Shared preprocessing, cached across experiments
    @proj.compute_or_load("processed_input")
    def preprocess():
        return expensive_preprocessing()

    data = preprocess()

    # A grid of experiments
    for lr in [0.01, 0.02, 0.05]:
        exp = proj.experiment("baseline", lr=lr, prior="uniform")
        exp.save(simulate(exp.lr, exp.prior), "result")

    # Meta-analysis
    runs = proj.runs()
    runs.where(prior="uniform").summarize(
        final_loss=lambda r: r.load("result")["loss"].iloc[-1],
    )

See `notebook/01_walkthrough.ipynb` for a full walkthrough.

## AI assistants (Claude Code, Cursor, etc.)

`box` ships two skills in `box/skills/` that teach an assistant the four-noun API and the messy-data import workflow. After `pip install box`:

    box install-skills                        # copies to ~/.claude/skills/box/
    box install-skills --dest ~/.some/place   # or a custom directory

For non-Claude tools, point the assistant at `AGENTS.md` (in the source repo). The same content is available via `python -c "import box; print(box.skills_path())"` if you'd rather symlink than copy.

## On-disk layout

    catalog/walker/                                    <- project
      global/                                          <- project-scope shared artifacts
        processed_input/
          v1.parquet
          v1.manifest.yml
      2026-08-15__baseline__a3f18d02/                  <- experiment folder
        params.yaml
        manifest.yml
        result/
          v1.parquet
          v1.manifest.yml

Every experiment folder is self-contained: `ls` shows every artifact that run produced; `params.yaml` lets you reconstruct the params; every artifact carries its own manifest so it survives being moved.

## Development

    make setup        # create hatch env
    make test         # run tests
    make lint         # ruff
    make format       # ruff format

## Requirements

Python 3.11+. Depends on pyyaml, numpy, pandas, pillow, pyarrow, joblib.

## License

BSD 3-Clause.
