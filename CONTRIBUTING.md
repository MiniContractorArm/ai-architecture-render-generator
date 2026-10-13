# Contributing to ai-architecture-render-generator

Thanks for wanting to bolt a new renderer onto the host. The whole point of
this repo is that the **core host stays thin** and every interesting piece of
behavior lives in an extension module. If your patch makes `core/host.py`
bigger, it's probably in the wrong place.

## Ground rules

- Python 3.12+. We target Windows 10/11 as the primary desktop, but the host
  runs headless on Linux for CI.
- One feature, one extension. New renderer? New `extensions/render_<name>/`.
  New prompt grammar? New `extensions/grammar_<name>/`.
- The host never imports an extension directly. It only talks to the
  `RenderPlugin` protocol in `contracts/plugin_api.py`. If you need a new
  capability, widen the contract *first*, then implement it.
- Type hints are required on anything that crosses a module boundary. `mypy
  --strict` runs in CI on `core/`, `contracts/`, and `services/`.

## Layout

```
core/         host loop, scheduler, registry, loader
contracts/    the plugin protocol + shared dataclasses
extensions/   drop-in renderers, grammars, exporters
services/     long-lived side services (model broker, cache, telemetry)
handlers/     CLI + IPC command handlers
models/       pydantic request/response models
utils/        logging, paths, hashing, image helpers
config/       default config + schema
tests/        pytest suite
```

## Adding a renderer extension

1. Copy `extensions/render_stub/` to `extensions/render_<yours>/`.
2. Implement `RenderPlugin` from `contracts/plugin_api.py`.
3. Fill in `manifest.toml` — `id`, `version`, `api_version`, `entrypoint`.
4. Drop a golden image test in `tests/` that renders a fixed prompt and
   compares against a stored hash. CI will fail if you drift the output.

## Running the suite

```
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
```

## Style

- `ruff` for lint, `black` for format, `mypy --strict` on the typed surface.
- No print debugging. Use `utils/logging_setup.py`.
- No silent `except:`. Catch specifically, log, re-raise or return a typed
  error result.

## License

By contributing you agree your work is licensed under the repo's MIT license.