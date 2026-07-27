# DNS Image Gen

![Python Versions](https://img.shields.io/badge/Python-3.10+-black?color=FFE873&labelColor=3776AB)
[![License](https://img.shields.io/github/license/nessshon/dns-image-gen)](https://github.com/nessshon/dns-image-gen/blob/master/LICENSE)
[![Donate](https://img.shields.io/badge/Donate-TON-blue)](https://tonviewer.com/UQCZq3_Vd21-4y4m7Wc-ej9NFOhh_qvdfAkAYAOHoQ__Ness)

### Image generator for TON DNS, Telegram usernames, GRAM and Getgems domains

Give it a domain, get back a rendered preview in the matching style.  
Built for link previews, social cards, bots and marketplaces.

## Preview

<p>
  <img src="https://dns-img.ness.uz/ness.ton.webp" width="200">
  <img src="https://dns-img.ness.uz/ness.gram.webp" width="200">
  <img src="https://dns-img.ness.uz/ness.t.me.webp" width="200">
  <img src="https://dns-img.ness.uz/ness.gg.webp" width="200">
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
