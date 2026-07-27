from __future__ import annotations

import nox

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True


@nox.session
def lint(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--group", "lint", "--no-install-project", external=True)
    session.run("ruff", "check", ".")


@nox.session(name="format")
def format_(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--group", "format", "--no-install-project", external=True)
    session.run("black", ".")


@nox.session
def format_check(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--group", "format", "--no-install-project", external=True)
    session.run("black", "--check", ".")


@nox.session
def typecheck(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--group", "type-check", external=True)
    session.run("pyright")
