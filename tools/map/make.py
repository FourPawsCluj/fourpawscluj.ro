import json, sys, os, urllib.parse
B = os.path.dirname(os.path.abspath(sys.argv[0]))
m = json.load(open(os.path.join(B, 'map.json')))
t = open(os.path.join(B, 'template.html')).read()
SPOTS = {
 'central': {'name': 'Parcul Central', 'price': 40, 'lx': 22, 'ly': 6,
   'ro': {'dur': '30 min', 'tags': ['lac', 'alei umbrite', 'câini mici și seniori'], 'desc': 'Tura clasică: în jurul lacului și pe aleile umbrite de lângă Casino. Liniștit dimineața devreme.'},
   'en': {'dur': '30 min', 'tags': ['lake', 'shady paths', 'small & senior dogs'], 'desc': 'The classic loop: around the lake and along the shady paths by the Casino. Quiet early in the morning.'}},
 'iulius': {'name': 'Iulius Parc', 'price': 40, 'lx': 22, 'ly': 6,
   'ro': {'dur': '30 min', 'tags': ['lac', 'teren plat', 'mult spațiu'], 'desc': 'Alei largi în jurul lacului Gheorgheni, teren plat, bun pentru câinii care trag de lesă.'},
   'en': {'dur': '30 min', 'tags': ['lake', 'flat', 'lots of space'], 'desc': 'Wide paths around Lake Gheorgheni, flat ground, good for dogs that pull on the leash.'}},
 'feroviarilor': {'name': 'Parcul Feroviarilor', 'price': 40, 'lx': 22, 'ly': 6,
   'ro': {'dur': '30 min', 'tags': ['aproape de centru', 'liniștit'], 'desc': 'Parc mic și liniștit, potrivit pentru o plimbare rapidă la prânz.'},
   'en': {'dur': '30 min', 'tags': ['near the centre', 'quiet'], 'desc': 'Small, quiet park, good for a quick lunchtime walk.'}},
 'hoia': {'name': 'Pădurea Hoia', 'price': 60, 'lx': 22, 'ly': 6,
   'ro': {'dur': '60 min', 'tags': ['pădure', 'câini energici', 'umbră vara'], 'desc': 'O oră prin pădure, pe poteci cu umbră. Pentru câinii care au nevoie să alerge.'},
   'en': {'dur': '60 min', 'tags': ['forest', 'energetic dogs', 'shade in summer'], 'desc': 'An hour in the forest on shady trails. For dogs that need to run.'}},
 'faget': {'name': 'Pădurea Făget', 'price': 80, 'lx': 22, 'ly': 6,
   'ro': {'dur': '90 min', 'tags': ['pădure', 'tura lungă', 'câini energici'], 'desc': 'Tura lungă: 90 de minute în Făget, cu transport inclus. Câinele ajunge acasă fericit și obosit.'},
   'en': {'dur': '90 min', 'tags': ['forest', 'long walk', 'energetic dogs'], 'desc': 'The long one: 90 minutes in Făget, transport included. Your dog comes home happy and tired.'}},
}
L = m['layers']
for k, v in L.items(): t = t.replace('d="L_' + k + '"', f'id="L-{k}" d="{v}"', 1).replace('d="L_' + k + '"', f'd="{v}"')
defs, routes, spots = [], [], []
for i, (k, r) in enumerate(m['routes'].items()):
    defs.append(f'<path id="r-{k}" d="{r["d"]}"/>')
    defs.append(f'<mask id="m-{k}" maskUnits="userSpaceOnUse" x="-200" y="-200" width="1400" height="1400"><path class="route-mask" pathLength="1" d="{r["d"]}"/></mask>')
    routes.append(f'<path class="route-base" mask="url(#m-{k})" d="{r["d"]}"/>')
    routes.append(f'<g class="walker"><circle r="10"/><path transform="translate(-6 -6) scale(.5)" d="M12 13.5c-2.6 0-5.5 2.6-5.5 5 0 1.6 1.3 2.5 2.8 2.5 1.2 0 1.8-.6 2.7-.6s1.5.6 2.7.6c1.5 0 2.8-.9 2.8-2.5 0-2.4-2.9-5-5.5-5ZM6.2 12.3c1.3-.4 1.9-2 1.4-3.5-.5-1.6-1.9-2.5-3.2-2.1-1.3.4-1.9 2-1.4 3.5.5 1.6 1.9 2.5 3.2 2.1Zm11.6 0c1.3.4 2.7-.5 3.2-2.1.5-1.5-.1-3.1-1.4-3.5-1.3-.4-2.7.5-3.2 2.1-.5 1.5.1 3.1 1.4 3.5ZM9.4 8.4c1.4 0 2.4-1.5 2.4-3.3S10.8 2 9.4 2 7 3.4 7 5.1s1 3.3 2.4 3.3Zm5.2 0c1.4 0 2.4-1.5 2.4-3.3S16 2 14.6 2s-2.4 1.4-2.4 3.1 1 3.3 2.4 3.3Z"/><animateMotion begin="indefinite" dur="{12 + i*3}s" repeatCount="indefinite"><mpath href="#r-{k}"/></animateMotion></g>')
    x, y = r['c']; s = SPOTS[k]
    spots.append(f'<g class="spot" data-k="{k}" tabindex="0" role="button" aria-label="{s["name"]}" transform="translate({x} {y})"><circle class="hit" r="34"/><circle class="pulse" r="16"/><circle class="ring" r="14"/><circle class="core" r="5"/><text x="{s["lx"]}" y="{s["ly"]}">{s["name"]}</text></g>')
cx, cy = m['routes']['central']['c']
mini = (f'<svg viewBox="{cx-70} {cy-45} 140 90"><use href="#L-parks" class="parks"/><use href="#L-water" class="water"/><use href="#L-river" class="river"/>'
        f'<use href="#L-roads2" class="roads2"/><use href="#L-roads1" class="roads1"/><use href="#r-central" style="fill:none;stroke:#FF8200;stroke-width:3;stroke-linecap:round"/>'
        f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="#1B2F04"/></svg>')
grid = ''.join(f'<line x1="{x}" y1="-200" x2="{x}" y2="1200"/>' for x in range(0, 1001, 100)) + ''.join(f'<line x1="-200" y1="{y}" x2="1200" y2="{y}"/>' for y in range(0, 1001, 100))
wa = 'https://wa.me/40746048445?text=' + urllib.parse.quote('Bună! Aș vrea o plimbare pentru câinele meu.')
t = (t.replace('MAP_W', str(m['w'])).replace('MAP_H', str(m['h'])).replace('ROUTE_DEFS', '\n'.join(defs))
      .replace('@@ROUTES@@', '\n'.join(routes)).replace('@@SPOTSJSON@@', json.dumps(SPOTS, ensure_ascii=False)).replace('@@SPOTS@@', '\n'.join(spots))
      .replace('MINI_MAP', mini).replace('GRID', grid).replace('WA_LINK', wa))
open(sys.argv[1], 'w').write(t)
print(len(t))
