# CLAUDE.md - A4S

A4S is an orchestration system for AI agents.

## Development Guidelines

- Always use uv instead of python or pip
- After making changes, run `uv run ruff format` and `uv run ruff check --fix` to format and lint the code.

## Style Guide

- Do not use f-strings for logging. Use %s instead.
- Add docstrings for public methods with Args, Returns, and Raises sections (if applicable).
- Do not add docstrings for private methods.
