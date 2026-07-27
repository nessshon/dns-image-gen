# DNS Image Gen

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

Image generator for TON DNS, GRAM, Getgems domains and Telegram usernames. Give it a domain — it returns a rendered WebP preview in the matching style.

## Preview

<p>
  <img src="https://dns-img.ness.uz/ness.ton.webp" width="200" alt="ness.ton">
  <img src="https://dns-img.ness.uz/ness.gram.webp" width="200" alt="ness.gram">
  <img src="https://dns-img.ness.uz/ness.t.me.webp" width="200" alt="ness.t.me">
  <img src="https://dns-img.ness.uz/ness.gg.webp" width="200" alt="ness.gg">
</p>

## API

```http
GET /{domain}.webp
```

The domain suffix picks the style — `.ton`, `.t.me`, `.gram`, `.gg`. Subdomains work too.

```http
GET /ness.ton.webp
GET /shon.ness.t.me.webp
```

## Run

```bash
docker compose up -d
```

Or without Docker:

```bash
pip install -r requirements.txt
python -m app
```

Available at `http://127.0.0.1:8000`.

## License

This repository is distributed under the [MIT License](LICENSE).
