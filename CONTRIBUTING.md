# Contributing to Is It Local

Thanks for your interest in improving **Is It Local**. This guide covers how we
branch, commit, and open pull requests.

## Getting started

1. Fork and clone the repository.
2. Copy `.env.example` to `.env` and fill in your keys (never commit `.env`).
3. Install dependencies:
   - JavaScript/TypeScript: `pnpm install`
   - Python: `ruff` via `pipx install ruff` (or your environment of choice)
4. Install git hooks: `pre-commit install`.

## Branch strategy

- `main` is always releasable. Do not commit directly to it.
- Create a topic branch off `main` using the pattern:
  - `feat/<short-description>` — new features
  - `fix/<short-description>` — bug fixes
  - `chore/<short-description>` — tooling, docs, refactors

## Commit conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(optional scope): <description>
```

Common types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`.

Example: `feat(api): add business search endpoint`

## Pull request process

1. Ensure `pnpm lint`, `pnpm test`, and `ruff check` pass locally.
2. Keep PRs focused and reasonably small.
3. Fill out the pull request template.
4. Link any related issues.
5. At least one approving review is required before merge.

## Code style

- TypeScript/Markdown: formatted with Prettier.
- Python: linted and formatted with Ruff.
- Files use `lowercase-kebab-case`; schema fields use `snake_case`.

## Reporting issues

Use the issue templates for bug reports and feature requests. Include steps to
reproduce, expected vs actual behavior, and environment details where relevant.
