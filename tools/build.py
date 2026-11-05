"""Builds the site into _site/ (what GitHub Pages publishes).

    python3 -I tools/build.py

Inputs: src/page.html (one template for both languages), src/spots.json (map parks),
tools/map/map.json (map shapes from tools/map/gen.py), src/static/ (icons, robots, CNAME…).
Text in the template is written {{Romanian||English}}; @@NAME@@ marks values filled in here.
"""
import math, datetime, html, json, os, re, shutil, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_site')
SITE = 'https://fourpawscluj.ro'
PHONE = '40746048445'
VIEWBOX = (100, 30, 880, 490)  # x, y, w, h: the city, without the forests
PAW = ('M12 13.5c-2.6 0-5.5 2.6-5.5 5 0 1.6 1.3 2.5 2.8 2.5 1.2 0 1.8-.6 2.7-.6s1.5.6 2.7.6c1.5 0 2.8-.9 2.8-2.5 '
       '0-2.4-2.9-5-5.5-5ZM6.2 12.3c1.3-.4 1.9-2 1.4-3.5-.5-1.6-1.9-2.5-3.2-2.1-1.3.4-1.9 2-1.4 3.5.5 1.6 1.9 2.5 '
       '3.2 2.1Zm11.6 0c1.3.4 2.7-.5 3.2-2.1.5-1.5-.1-3.1-1.4-3.5-1.3-.4-2.7.5-3.2 2.1-.5 1.5.1 3.1 1.4 3.5ZM9.4 '
       '8.4c1.4 0 2.4-1.5 2.4-3.3S10.8 2 9.4 2 7 3.4 7 5.1s1 3.3 2.4 3.3Zm5.2 0c1.4 0 2.4-1.5 2.4-3.3S16 2 14.6 '
       '2s-2.4 1.4-2.4 3.1 1 3.3 2.4 3.3Z')
SOCIAL = [  # (name, url): shown as icons in the footer and as sameAs in the structured data
    ('Instagram', 'https://www.instagram.com/fourpawscluj/'),
    ('LinkedIn', 'https://www.linkedin.com/in/fourpawscluj'),
]
ICONS = {
    'Instagram': '<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/>'
                 '<circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.5" cy="6.5" r="1.3" fill="currentColor"/>',
    'Facebook': '<path fill="currentColor" d="M13.5 22v-8h2.7l.4-3.2h-3.1V8.8c0-.9.3-1.6 1.6-1.6h1.7V4.4c-.3 0-1.3-.1-2.5-.1-2.5 0-4.1 1.5-4.1 4.2v2.3H7.4V14h2.8v8z"/>',
    'LinkedIn': '<path fill="currentColor" d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zm7 0h3.8v1.6h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.2c0-1.2 0-2.8-1.7-2.8s-2 1.3-2 2.7V21h-4z"/>',
}


def social_links():
    return ''.join(f'<a class="soc" href="{u}" rel="noopener me" target="_blank" aria-label="{n}">'
                   f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[n]}</svg></a>' for n, u in SOCIAL)


PRICES = [  # (ro name, en name, lei, minutes) — keep in step with the price cards in page.html
    ('Prima plimbare', 'Trial walk', 30, 30), ('Plimbare scurtă', 'Short walk', 40, 30),
    ('Plimbare lungă', 'Long walk', 60, 60), ('Tura mare', 'Big walk', 80, 90),
    ('Pachet 10 plimbări', '10-walk pack', 350, 300),
    ('Vizită scurtă', 'Short visit', 40, 30), ('Vizită de o oră', 'One-hour visit', 60, 60),
    ('2 vizite pe zi', '2 visits a day', 100, 120), ('Oră în plus', 'Extra hour', 20, 60),
]


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


def wa(text):
    return f'https://wa.me/{PHONE}?text=' + urllib.parse.quote(text)


def pick(src, lang):
    i = 0 if lang == 'ro' else 1
    return re.sub(r'\{\{(.*?)\|\|(.*?)\}\}', lambda m: m.group(i + 1), src, flags=re.S)


LABEL = {  # where a spot's name sits; set "label" in src/spots.json when the default overlaps something
    None: '<text x="22" y="6">{name}</text></g>',
    'left': '<text x="-22" y="6" text-anchor="end">{name}</text></g>',
    'below': '<text x="0" y="40" text-anchor="middle">{name}</text></g>',
}


LON0, LON1, LAT0, LAT1 = 23.505, 23.665, 46.700, 46.800  # same map area as tools/map/gen.py


def project(lat, lon, m):
    return (lon - LON0) / (LON1 - LON0) * m['w'], (LAT1 - lat) / (LAT1 - LAT0) * m['h']


def pen_marks(m, pens, lang):
    """Dog pens (OSM leisure=dog_park): small lime paws under the park dots, nudged off a park dot they would cover."""
    dots = [r['c'] for r in m['routes'].values()]
    out = []
    for k, p in pens.items():
        x, y = project(p['lat'], p['lon'], m)
        x, y = x + p.get('dx', 0), y + p.get('dy', 0)  # set dx/dy in src/pens.json when a park name covers the paw
        for cx, cy in dots:
            d = math.hypot(x - cx, y - cy)
            if d < 32:
                ux, uy = ((x - cx) / d, (y - cy) / d) if d > 1 else (-.6, .8)
                x, y = cx + ux * 32, cy + uy * 32
        name = html.escape(p['name'])
        out.append(f'<g class="pen" data-p="{k}" tabindex="0" role="button" aria-label="{"Țarc câini" if lang == "ro" else "Dog pen"}: {name}" '
                   f'transform="translate({x:.1f} {y:.1f})"><circle class="hit" r="22"/><circle class="pring" r="11"/>'
                   f'<use href="#paw" x="-7" y="-7" width="14" height="14"/></g>')
    chips = ''.join(f'<button type="button" data-p="{k}"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#paw"/></svg>'
                    f'{html.escape(p["name"])}</button>' for k, p in sorted(pens.items(), key=lambda kv: kv[1]['name']))
    return '\n'.join(out), chips


def map_parts(m, spots):
    defs, routes, marks, chips = [], [], [], []
    for i, (k, r) in enumerate(m['routes'].items()):
        name = html.escape(spots[k]['name'])
        defs.append(f'<path id="r-{k}" d="{r["d"]}"/>'
                    f'<mask id="m-{k}" maskUnits="userSpaceOnUse" x="-200" y="-200" width="1400" height="1400">'
                    f'<path class="route-mask" pathLength="1" d="{r["d"]}"/></mask>')
        routes.append(f'<path class="route-base" mask="url(#m-{k})" d="{r["d"]}"/>'
                      f'<g class="walker" aria-hidden="true"><circle r="10"/><path transform="translate(-6 -6) scale(.5)" d="{PAW}"/>'
                      f'<animateMotion begin="indefinite" dur="{(12 + i * 2) * (2 if r.get("open") else 1)}s" repeatCount="indefinite"'
                      f'{" keyPoints=\"0;1;0\" keyTimes=\"0;.5;1\" calcMode=\"linear\"" if r.get("open") else ""}><mpath href="#r-{k}"/></animateMotion></g>')
        x, y = r['c']
        marks.append(f'<g class="spot" data-k="{k}" tabindex="0" role="button" aria-label="{name}" transform="translate({x} {y})">'
                     f'<circle class="hit" r="34"/><circle class="pulse" r="16"/><circle class="ring" r="14"/><circle class="core" r="5"/>'
                     + LABEL.get(spots[k].get('label'), LABEL[None]).format(name=name))
        chips.append(f'<button type="button" data-k="{k}">{name}</button>')
    return ''.join(defs), '\n'.join(routes), '\n'.join(marks), ''.join(chips)


def jsonld(lang, url):
    return json.dumps({
        '@context': 'https://schema.org', '@type': 'LocalBusiness', '@id': SITE + '/#business',
        'name': 'Four Paws Cluj', 'url': url, 'image': SITE + '/og-image.png',
        'telephone': '+' + PHONE, 'priceRange': '20–350 RON',
        'description': 'Plimbări pentru câini și vizite la domiciliu pentru animale în Cluj-Napoca.' if lang == 'ro' else 'Dog walking and pet home visits in Cluj-Napoca.',
        'areaServed': [{'@type': 'City', 'name': 'Cluj-Napoca'}, {'@type': 'City', 'name': 'Florești'}],
        'sameAs': [u for _, u in SOCIAL],
        'makesOffer': [{'@type': 'Offer', 'name': ro if lang == 'ro' else en, 'price': lei, 'priceCurrency': 'RON'}
                       for ro, en, lei, _ in PRICES],
    }, ensure_ascii=False)


def build():
    m = json.loads(read('tools', 'map', 'map.json'))
    spots = json.loads(read('src', 'spots.json'))
    pens = json.loads(read('src', 'pens.json'))
    if set(spots) != set(m['routes']):
        sys.exit(f'spots.json {sorted(spots)} and map.json routes {sorted(m["routes"])} differ')
    defs, routes, marks, chips = map_parts(m, spots)
    tpl = read('src', 'page.html')
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, 'src', 'static'), OUT)
    for lang, path in (('ro', ''), ('en', 'en/')):
        url = f'{SITE}/{path}'
        hello = 'Bună! Aș vrea o plimbare pentru câinele meu.' if lang == 'ro' else "Hi! I'd like a walk for my dog."
        pens_svg, pen_chips = pen_marks(m, pens, lang)
        vals = {
            'URL': url, 'SITE': SITE, 'ROOT': '/', 'HOME': '/' + path,
            'OTHER': '/en/' if lang == 'ro' else '/', 'WA': html.escape(wa(hello)),
            'WAVISIT': html.escape(wa('Bună! Aș vrea o vizită la domiciliu pentru animalul meu.' if lang == 'ro'
                                      else "Hi! I'd like a home visit for my pet.")),
            'VIEWBOX': ' '.join(map(str, VIEWBOX)), 'ROUTEDEFS': defs, 'ROUTES': routes,
            'SPOTS': marks, 'PENS': pens_svg, 'PENCHIPS': pen_chips, 'PENSJSON': json.dumps(pens, ensure_ascii=False), 'CHIPS': chips, 'PAW': PAW, 'SOCIALLINKS': social_links(),
            'SPOTSJSON': json.dumps(spots, ensure_ascii=False), 'JSONLD': jsonld(lang, url),
            'YEAR': str(datetime.date.today().year),
            **{'L_' + k: v for k, v in m['layers'].items()},
        }
        page = pick(tpl, lang)
        page = re.sub(r'@@(\w+)@@', lambda x: vals[x.group(1)], page)
        os.makedirs(os.path.join(OUT, path), exist_ok=True)
        with open(os.path.join(OUT, path, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(page)
        print(f'{path or "/"}index.html  {len(page.encode()) // 1024} KB')
    today = datetime.date.today().isoformat()
    alt = ''.join(f'<xhtml:link rel="alternate" hreflang="{h}" href="{SITE}/{p}"/>' for h, p in (('ro', ''), ('en', 'en/')))
    urls = ''.join(f'<url><loc>{SITE}/{p}</loc><lastmod>{today}</lastmod>{alt}</url>' for p in ('', 'en/'))
    with open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                f'xmlns:xhtml="http://www.w3.org/1999/xhtml">{urls}</urlset>\n')


if __name__ == '__main__':
    build()
