# Lunarr

Lunarr provides your AI stand-in at work. Personal agents learn your context, answer on your behalf, and collaborate with each other so decisions never stall.

## Quick Start

Bring your own API Key (Google, OpenAI, OpenRouter, etc) and add one of them in .env.

```bash
cp api/.env.example api/.env
make up
```

## Development

Ensure you have the following tools installed:

- [uv](https://docs.astral.sh/uv/)

```bash
make setup-dev
```

Run the development services:

```bash
make dev-up
```
