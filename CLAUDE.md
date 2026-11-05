# fourpawscluj.ro

One-page website for dog walking and pet home visits (cats, birds, rabbits, hamsters, reptiles) in Cluj-Napoca; the "Despre mine" section presents Emilia. Visitors book by WhatsApp; there is no form, no account, no backend. Hosted on GitHub Pages at https://fourpawscluj.ro.

Before any visual or text change, read `DESIGN.md`: it holds the colors, type, page order, map behavior, prices and copy.

## How the site is made

Plain static HTML + CSS + one small inline vanilla JS script. No framework, no npm. One Python script (stdlib only) builds the site into `_site/`:

```bash
python3 -I tools/build.py                                # → _site/index.html, _site/en/index.html, sitemap.xml + src/static/*
python3 -m http.server 8765 --bind 127.0.0.1 --directory _site   # preview at http://127.0.0.1:8765/
```

- `src/page.html`: the one template for both languages. Text is written `{{Romanian||English}}` (works in text and attributes); `@@NAME@@` marks values `tools/build.py` fills in (map shapes, routes, links, JSON-LD).
- `src/spots.json`: the map parks (name, price, RO/EN length, tags, description). Its keys must match the routes in `tools/map/map.json`; the build stops if they differ.
- `src/static/`: copied as is: icons, `og-image.png` (share preview), `site.webmanifest`, `robots.txt`, `404.html`, `CNAME`, `.nojekyll`.
- Prices are in two places that must agree: the price cards in `src/page.html` and `PRICES` in `tools/build.py` (structured data for Google).
- `_site/` is never committed; GitHub Actions builds it.

## Deploy

Push to `main` → `.github/workflows/pages.yml` runs the build and publishes `_site/`. In the repo's Settings → Pages, "Source" must be set to **GitHub Actions**, and the custom domain to `fourpawscluj.ro` with HTTPS enforced.

## Rules the site must keep

- **Location**: write only "Cluj-Napoca". No street, address or home location anywhere: text, map, structured data or photo metadata (strip EXIF GPS from photos).
- **Contact**: phone and WhatsApp `0746 048 445`; links `https://wa.me/40746048445?text=<url-encoded message>` and `tel:+40746048445`. Every booking button opens WhatsApp with a message already filled in.
- **Map credit**: the footer keeps the © OpenStreetMap contributors link; the map data license requires it.
- **Motion lives on the map only** (routes drawing, walking paw, dot pulse) plus the paw trail color change. Every animation has a `prefers-reduced-motion` fallback.
- **Map layers**: the watercolor map is one still SVG; routes and dots are a second SVG on top, so animation never re-renders the watercolor filter. Keep anything that moves in the top SVG.
- **Speed**: each page under 300 KB before photos (now ~131 KB); photos WebP/AVIF under 120 KB, lazy below the hero.
- Photos: `src/static/img/{hero,<park>-1..3}.webp`, made by `tools/images/generate.py` (gpt-image-2; key `OPENAI_API_KEY`, Dan uses the one in `~/Documents/dev/products/resortbuggy/.env`). Real photos replace them under the same names.

## Map data (`tools/map/`)

`tools/map/map.json` is committed, so the build never needs the internet. To change the map area or the parks:

```bash
tools/map/fetch.sh                                            # OpenStreetMap layers → tools/map/osm/ (gitignored)
python3 -I tools/map/gen.py tools/map/osm tools/map/map.json      # simplify into SVG paths + walk routes
```

- `fetch.sh`: the Overpass server often answers "at capacity"; the script retries small queries, so give it a few minutes.
- `gen.py` holds the map area (`LON0…LAT1`) and the walk spots (`spots`). To add a park: add it there with its exact OSM name, regenerate, then add the same key to `src/spots.json`.
- `make.py` + `template.html` rebuild only `design/prototype.html` (the approved prototype, kept for reference).

## Images

- Tab icon and home-screen icons come from `src/static/favicon.svg` and `tools/icons/square.svg` via `rsvg-convert` (Homebrew `librsvg`).
- `src/static/og-image.png` is a 1200×630 screenshot of `tools/icons/og.html`.

## Check before pushing

At 1360px and 400px wide, on `/` and `/en/`: no horizontal scroll, routes draw, map dots and park buttons open the park card (bottom sheet on phone), WhatsApp links carry the right language, no console errors.
