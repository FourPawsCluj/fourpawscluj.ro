# DESIGN.md: fourpawscluj.ro

Visual and content spec for the site. The approved look is `design/prototype.html` (map style C, watercolor). Open it in a browser next to this file: where the two disagree, this file wins and the prototype gets fixed.

Approved by Dan on 2026-11-04: map style C, dog's-eye hero, walk report, paw trail, the prices below.

## Idea in one line

A one-page dog-walking site for Cluj-Napoca built around a top-down watercolor map of the city with walk routes through public parks and along the Someș. Calm, warm and fast. All motion is on the map; the rest of the page does not move.

Style source: [Pawluxe](https://pawluxe-pets.framer.website/services/pet-grooming) colors and type, with its effects removed. Map idea: our own. [My Dog Company](https://www.mydogcompany.com/) was liked for its look and rejected for being slow; nothing heavy from it.

## Colors

| Token | Hex | Use |
|---|---|---|
| `--olive` | `#1B2F04` | headings, main buttons, map dots, dark price card |
| `--lime` | `#C1F585` | highlights, button text on olive, dot rings |
| `--orange` | `#FF8200` | WhatsApp booking buttons, walk routes, walking paw |
| `--cream` | `#FFF7F0` | page background |
| `--ink` | `#1F2937` | body text |
| `--muted` | `#5B6152` | secondary text |
| WhatsApp green | `#25D366` | floating WhatsApp button only |

Map, style C:

| Layer | Hex |
|---|---|
| land | `#FBF3E6` |
| parks | `#B9E58C` |
| forests | `#8CCB6A` |
| river, lakes | `#8FCBE6` |
| roads | `#FFFAF2` at 55% opacity |

Light theme only.

## Type

- Headings: **Bricolage Grotesque** 800 (600 for small headings), tight letter-spacing (-0.02em to -0.03em), line-height ~1.02.
- Body: **DM Sans** 400/500/700, 16px base, line-height 1.55.
- Hero headline: `clamp(46px, 7.4vw, 104px)`. Section headings: `clamp(34px, 5vw, 60px)`.
- Fonts from Google Fonts with `display=swap`. Later: self-host as woff2, both families, Latin + Latin Extended subsets (Romanian ă â î ș ț).

## Shape

- Corner radius 22px on large blocks (map, hero image, price cards), 12–18px on small ones, full pill on buttons and tags.
- No borders except the outline language button. No shadows except the floating WhatsApp button, the hover card and the park card.

## Page, top to bottom

1. **Nav**: paw logo in a lime circle + name; RO/EN switch; "Programează pe WhatsApp" button (hidden on phones because the floating button covers it).
2. **Hero, dog's-eye view**: headline "Cluj, văzut de la *30 cm.*" with "30 cm." on a lime highlight. One line under it, then the orange WhatsApp button showing the number. Right side: a photo taken at dog height (30 cm off the ground).
3. **Map, "Traseele noastre"**: see the Map section below.
4. **Walk report, "Raport după fiecare plimbare"** (no route map or distance: Dan has no GPS tracking): text on the left; on the right, a phone frame showing a sample WhatsApp message with a photo from the walk, dog name, park, time, pills "Pipi ✓ Caca ✓ Apă ✓", a short note, and blue ticks.
5. **Home visits, "Vizite la domiciliu"** (`#vizite`, added 2026-11-05 at Emilia's request): text on the left, orange "Vreau o vizită" button (WhatsApp: "Bună! Aș vrea o vizită la domiciliu pentru animalul meu."); on the right a white card "Ce fac la o vizită" with a checklist; below both, a row of 5 photos with captions (pisici, păsări, iepuri, hamsteri, reptile; 3 per row on phones). The hero line links to it.
6. **About, "Despre mine"** (`#despre`): Emilia's short bio (2 paragraphs, from her own text) + 4 experience cards (câini și pisici, păsări 16 ani, iepuri, reptile). Photos: `emilia-1..4.webp`, her real photos (one large, three small, all square) edited with gpt-image-2 on 2026-11-05 at Dan's request: clothes recolored olive with logos removed, backgrounds cream and green; face, pose and animals kept. Metadata stripped. Never an AI-made photo of her from nothing. Desktop: photos left, text and cards (2×2) right; phone: photos first.
7. **Prices**: two rows of cards, "Plimbări câini" and "Vizite la domiciliu", see Content. The "Plimbare lungă" card is olive with lime text (the one to look at first).
8. **Footer**: © year, name, "Cluj-Napoca", phone, "Date hartă © contribuitorii OpenStreetMap" (required by the map data license).
9. **Floating WhatsApp button**: bottom right, always visible.
10. **Paw trail**: small paws down the right edge of the page, every 70px, alternating left/right, turned 180° ±12° so the toes point down (the animal walks down the page as you scroll). Gray `#CFCFCF` by default; a paw turns black `#111` once it is above 60% of the screen height, and goes back to gray when you scroll up. 0.35s color change. Decoration only (`aria-hidden`).

## Map

- **Drawing**: inline SVG made from OpenStreetMap data (river Someșul Mic, named parks, forests, lakes, main and secondary roads), simplified to about 95 KB, cropped to the city (viewBox `100 30 880 490`). No map library, no map images from other servers, no API key. Built with `tools/map/` (see CLAUDE.md).
- **Style C watercolor**: the fills (forests, parks, water, river) get an SVG filter: `feTurbulence` (fractal noise, base frequency 0.035, 3 octaves) → `feDisplacementMap` (scale 9) → slight blur blended back in. A paper grain layer (fine noise, multiply, 50%) sits over the whole map. Roads stay sharp. Parks and roads fade under the watercolor.
- **Routes**: one dotted orange loop per spot (2px dots, 9px gaps, 4px wide). Each loop follows the park shape; small parks get a larger loop so it reads at full map size.
- **Motion** (the only motion on the page):
  - When 35% of the map is on screen, all routes draw themselves in 2.6s (CSS `stroke-dashoffset` through a mask).
  - After that, an orange circle with a white paw walks each loop (SVG `animateMotion`, 12–24s per loop, each loop a different speed).
  - The dots pulse softly (2.4s).
  - With `prefers-reduced-motion`, routes are drawn at once, no walking paw, no pulse.
- **Dots**: olive center, lime ring, park name next to it with a land-colored halo. Hit area 34 units so fingers can tap it. Keyboard focusable; Enter or Space opens the card.
- **Hover** (mouse only): small white card above the dot with a photo, name, length and price.
- **Click or tap**: park card. On a computer it slides in on the right inside the map; on a phone it rises from the bottom of the screen. It shows: name, 2–3 tags, 3 photos (one large, two small), one-line description, price + length, and an orange "Vreau plimbarea asta" button that opens WhatsApp with the message already filled in ("Bună! Aș vrea o plimbare în {park} ({length}).", English version when the page is in English). Closes with ×, Esc, or by opening another park.
- **Dog pens** (added 2026-11-05): 13 small lime circles with an olive paw (r 11), one per OpenStreetMap `leisure=dog_park` in the city, under the park dots and without names or routes. Tap or Enter opens the same card in "pen mode": name "Țarc câini · {street}", tags (neighborhood, țarc împrejmuit, fără lesă), one line, WhatsApp button; no photos, no price. A legend line under the park buttons explains them; under it, one lime pill button per pen (paw + street, A–Z) opens the same card. Data: `src/pens.json` (lat/lon from OSM, street names from Nominatim); `dx`/`dy` there moves a paw that a park name covers.
- **Park buttons**: a row of pill buttons under the map, one per park, doing the same as the dots. Needed on phones, where the whole map is shown small.
- **Spots**, public places only, never a home address:

| Spot | Length | Price | Tags |
|---|---|---|---|
| Parcul Central | 30 min | 40 lei | lac, alei umbrite, câini mici și seniori |
| Parcul Babeș | 60 min | 60 lei | alei lungi, lângă Someș, câini energici |
| Parcul Feroviarilor | 30 min | 40 lei | aproape de centru, liniștit |
| Parcul Armătura | 30 min | 40 lei | Mărăști, alei largi |
| Iulius Parc | 30 min | 40 lei | lac, teren plat, mult spațiu |
| Parcul Aurel Vlaicu | 60 min | 60 lei | lacuri, Gheorgheni, tură lungă |
| Parcul Detunata | 30 min | 40 lei | Gheorgheni, liniștit, câini mici și seniori |
| Parcul Colina | 30 min | 40 lei | Mănăștur, umbră |
| Malul Someșului | 60 min | 60 lei | pe malul râului, dus-întors, câini energici |

  City only: Dan does not walk in Hoia or Făget forests (2026-11-04). "Malul Someșului" is an open path (there and back), so its walking paw goes out and back instead of looping. Park texts live in `src/spots.json`; `"label": "left"` or `"below"` moves the name where the default (right of the dot) would overlap or run off the map.

## Content

- **Contact**: phone and WhatsApp **0746 048 445**; link `https://wa.me/40746048445?text=…`. Always write the number in full so visitors can read it and copy it.
- **Location**: only "Cluj-Napoca". No street, no neighborhood of the walker, no home.
- **Prices** (pickup and drop-off included; travel in Cluj-Napoca and Florești included; outside them, e.g. Apahida or Luna, +30 lei for every 10 km, set by Emilia on 2026-11-05):

| RO | EN | Price | Note |
|---|---|---|---|
| Prima plimbare | Trial walk | 30 lei | 30 min, ca să ne cunoaștem |
| Plimbare scurtă | Short walk | 40 lei | 30 min |
| Plimbare lungă | Long walk | 60 lei | 60 min |
| Tura mare | Big walk | 80 lei | 90 min prin parcuri, pentru câinii energici |
| Pachet 10 plimbări | 10-walk pack | 350 lei | 10 × 30 min, economisești 50 lei |

  Home visits (any pet; set by Emilia on 2026-11-05). Brushing and cutting out matted fur for cats and dogs are included in every visit price:

| RO | EN | Price | Note |
|---|---|---|---|
| Vizită scurtă | Short visit | 40 lei | 30 min |
| Vizită de o oră | One-hour visit | 60 lei | o vizită pe zi, 60 min |
| 2 vizite pe zi | 2 visits a day | 100 lei | câte o oră, dimineața și seara |
| Oră în plus | Extra hour | 20 lei | pentru o vizită mai lungă de o oră |

  Walk prices set from Cluj prices on 2026-11-04: 30 min at 30–50 lei, 60 min at 50–70 lei. Dan may change them.
- **Tone**: warm, short, direct; second person singular ("câinele tău"). Romanian first; English is a full translation, not a summary.

## Photos

- Now: 16 AI photos (OpenAI gpt-image-2, Dan's call on 2026-11-04) of one golden-red English Cocker Spaniel with an olive-green harness and leash: `hero` (dog's-eye view) and `{park}-1…3` for each map spot. Files: `src/static/img/*.webp`; prompts and the generator: `tools/images/generate.py`.
- Home-visit photos `pet-{cat,bird,rabbit,hamster,reptile}.webp` (480 px, AI, 2026-11-05): indoors, hands only, no street view through windows. Replace with Emilia's real photos of her own animals under the same names.
- Same dog, same harness in every dog photo; people only as hands or legs, never faces; late spring, natural light.
- Replace them with real photos from Dan's walks as they come in, same file names: an AI photo read as a real client costs visitor trust if found out.
- Size: square, WebP, hero 900 px, park photos 720 px, each under 120 KB. Park photos load only when a park card or hover card opens.

## Speed and access

- Whole page under 300 KB before photos; no JavaScript framework; one small inline script.
- No horizontal scroll at 400px width; 20px side padding.
- Text contrast at least 4.5:1 (olive on cream and lime on olive both pass).
- Every control reachable by keyboard; the map has an `aria-label`, and each dot has a role and a name.
