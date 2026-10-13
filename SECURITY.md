# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | yes       |
| 0.3.x   | security-only |
| < 0.3   | no        |

## Reporting a vulnerability

Open a **private** security advisory on GitHub, or email
`security@ai-architecture-render-generator.dev` with:

- A description of the issue and its impact.
- A minimal reproduction (prompt, extension id, host version).
- Whether the issue requires a malicious extension to be dropped into
  `plugins/local/`.

We aim to acknowledge within 72 hours.

## Threat model

The host loads **unsigned** extension modules from `plugins/local/` and from
installed `extensions/` packages. This is by design — it's a hobbyist
renderer host, and the plugin surface is the point. Consequences:

- A malicious extension runs with the host's privileges. Only drop
  extensions you trust into `plugins/local/`.
- The model broker (`services/model_broker.py`) will fetch weights from a
  configured mirror. Pin the mirror in `config/default.toml` if you care
  about supply chain.
- The IPC handler (`handlers/ipc_handler.py`) listens on a loopback named
  pipe by default. Do not bind it to a public interface.

## Hardening checklist for packagers

- Ship with `config/default.toml` pointing at a pinned model mirror.
- Sign your release artifacts.
- Set `host.allow_unsigned_extensions = false` if you bundle a curated set.