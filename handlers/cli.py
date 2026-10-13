"""`aarg` CLI. Thin wrapper over the host."""
from __future__ import annotations

from pathlib import Path

import typer
from rich import print as rprint

from config.loader import load_config
from core.host import Host
from models.render_request import RenderRequest

app = typer.Typer(add_completion=False, help="ai-architecture-render-generator host CLI")


def _host() -> Host:
    repo_root = Path(__file__).resolve().parents[1]
    return Host(load_config(repo_root), repo_root)


@app.command()
def render(
    brief: str = typer.Argument(..., help="Architecture brief."),
    renderer: str = typer.Option(None, "--renderer", "-r"),
    seed: int = typer.Option(0, "--seed"),
    out: Path = typer.Option(Path("renders"), "--out", "-o"),
) -> None:
    """Render a single brief."""
    host = _host()
    host.boot()
    result = host.render(RenderRequest(brief=brief, renderer=renderer, seed=seed, output_dir=out))
    host.shutdown()
    if not result.ok:
        rprint(f"[red]render failed:[/red] {result.error}")
        raise typer.Exit(code=1)
    for art in result.artifacts:
        rprint(f"[green]{art}[/green]")


@app.command("list-plugins")
def list_plugins() -> None:
    """List registered renderers."""
    host = _host()
    host.boot()
    for pid in host._registry.ids():  # noqa: SLF001 — CLI is inside the trust boundary
        manifest = host._registry.manifest(pid)  # noqa: SLF001
        rprint(f"[cyan]{pid}[/cyan] v{manifest.version} — {manifest.description}")
    host.shutdown()
</instructions>