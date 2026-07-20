# Contributing

Thank you for your interest in this project!
Below you'll find everything you need to know to become a contributor.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local setup](#local-setup)
- [Running tests](#running-tests)
- [Commit conventions](#commit-conventions)
- [Branch workflow](#branch-workflow)
- [Before submitting a PR](#before-submitting-a-pr)
- [Reporting issues](#reporting-issues)
- [Code style](#code-style)

## Prerequisites

Make sure you have the following installed locally:

- [Docker](https://www.docker.com/) and Docker Compose
- Git

## Local setup

Follow the [Quick Start (Docker)](README.md#quick-start-docker) section in the README:

1. Clone the repo and set up your environment
2. Fill in `.env` based on `.env.example`
3. Start the stack
4. Open the app locally

## Running tests

Tests require a dedicated test database and container.
See the [Running Tests](README.md#running-tests) section in the README for setup instructions.

## Commit conventions

This project follows [Conventional Commits](https://www.conventionalcommits.org/).

- Permitted types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `release`
- Write messages in English, in the imperative mood (e.g. `fix: resolve login bug`)
- Keep the first line under 50 characters, with no trailing period

## Branch workflow

1. Create a new branch from `main`, named `feature/...` or `fix/...`
2. Make your changes and commit them following the conventions above
3. Open a Pull Request against `main`
4. Once the PR is approved and merged, delete the branch

## Before submitting a PR

- [ ] All tests pass locally (`pytest -v`)
- [ ] New functionality is covered by tests
- [ ] CI is green
- [ ] Commit messages follow the conventions above

## Reporting issues

Found a bug or have a suggestion? Please open a [GitHub Issue](https://github.com/LyapinAlexey/Weather/issues) with a clear description and, if applicable, steps to reproduce.

## Code style

Linting and formatting are not yet enforced via pre-commit hooks or CI (planned for a future update).
In the meantime, please try to keep your code style consistent with the existing codebase.