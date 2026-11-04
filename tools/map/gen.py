import json, math, sys, os
D = sys.argv[1]  # osm dir
OUT = sys.argv[2]
LON0, LON1, LAT0, LAT1 = 23.505, 23.665, 46.700, 46.800
W = 1000
K = math.cos(math.radians((LAT0+LAT1)/2))
H = W * (LAT1-LAT0) / ((LON1-LON0)*K)
def P(lat, lon):
    return ((lon-LON0)/(LON1-LON0)*W, (LAT1-lat)/(LAT1-LAT0)*H)

def dp(pts, eps):
    if len(pts) < 3: return pts
    (x1,y1),(x2,y2) = pts[0], pts[-1]
    dx, dy = x2-x1, y2-y1; L = math.hypot(dx,dy) or 1e-9
    md, mi = 0, 0
    for i in range(1,len(pts)-1):
        x,y = pts[i]
        d = abs(dy*x-dx*y+x2*y1-y2*x1)/L if (dx or dy) else math.hypot(x-x1,y-y1)
        if d > md: md, mi = d, i
    if md > eps:
        return dp(pts[:mi+1],eps)[:-1] + dp(pts[mi:],eps)
    return [pts[0], pts[-1]]

def fmt(pts, close=False):
    s = 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
    return s + ('Z' if close else '')

def load(n): return json.load(open(os.path.join(D, n+'.json')))['elements']

def geom(g): return [P(p['lat'], p['lon']) for p in g if p]

def stitch(segs):
    rings = []
    segs = [s[:] for s in segs if len(s) > 1]
    while segs:
        r = segs.pop(0)
        changed = True
        while changed and r[0] != r[-1]:
            changed = False
            for i,s in enumerate(segs):
                if s[0] == r[-1]: r += s[1:]; segs.pop(i); changed=True; break
                if s[-1] == r[-1]: r += s[::-1][1:]; segs.pop(i); changed=True; break
        rings.append(r)
    return rings

def polys(e):
    if e['type'] == 'way': return [geom(e['geometry'])]
    outer = [geom(m['geometry']) for m in e.get('members',[]) if m.get('role') in ('outer','') and m.get('geometry')]
    return stitch(outer)

def inview(pts):
    return any(-50 < x < W+50 and -50 < y < H+50 for x,y in pts)

def area(r):
    return abs(sum(r[i][0]*r[i-1][1]-r[i-1][0]*r[i][1] for i in range(len(r))))/2

def centroid(r):
    xs=[p[0] for p in r]; ys=[p[1] for p in r]
    return sum(xs)/len(xs), sum(ys)/len(ys)

layers = {}
# woods / forests: one path
wd, named = [], {}
for e in load('woods'):
    for r in polys(e):
        if len(r) < 4 or not inview(r) or area(r) < 60: continue
        s = dp(r, 1.2)
        if len(s) >= 3: wd.append(fmt(s, True))
        n = e.get('tags',{}).get('name')
        if n: named.setdefault(n, []).append(r)
layers['woods'] = ''.join(wd)
pk, parks = [], {}
for e in load('parks'):
    for r in polys(e):
        if len(r) < 4 or not inview(r): continue
        pk.append(fmt(dp(r, 0.6), True))
        parks.setdefault(e['tags']['name'], []).append(r)
layers['parks'] = ''.join(pk)
wt = []
for e in load('water'):
    for r in polys(e):
        if len(r) >= 4 and inview(r) and area(r) > 4: wt.append(fmt(dp(r,0.6), True))
layers['water'] = ''.join(wt)
rv = []
for e in load('river'):
    g = geom(e['geometry'])
    if inview(g): rv.append(fmt(dp(g, 0.8)))
layers['river'] = ''.join(rv)
def roads(name, eps):
    out = []
    for e in load(name):
        g = geom(e['geometry'])
        if inview(g): out.append(fmt(dp(g, eps)))
    return out
big, mid = [], []
for e in load('roads'):
    g = geom(e['geometry'])
    if not inview(g): continue
    (big if e['tags'].get('highway') in ('trunk','primary') else mid).append(fmt(dp(g,0.8)))
layers['roads1'] = ''.join(big)
layers['roads2'] = ''.join(mid)
layers['roads3'] = ''.join(roads('tert', 0.9))

# walk routes: a smoothed loop inside each chosen area
def loop(r, scale, n=40):
    cx, cy = centroid(r)
    s = dp(r, 3)
    # resample angularly around centroid for a clean loop
    pts = []
    for i in range(n):
        a = 2*math.pi*i/n
        best = None
        for j in range(len(s)):
            (x1,y1),(x2,y2) = s[j-1], s[j]
            # ray-segment intersection
            dx, dy = math.cos(a), math.sin(a)
            ex, ey = x2-x1, y2-y1
            den = dx*ey - dy*ex
            if abs(den) < 1e-9: continue
            t = ((x1-cx)*ey - (y1-cy)*ex)/den
            u = ((x1-cx)*dy - (y1-cy)*dx)/den
            if t > 0 and 0 <= u <= 1 and (best is None or t < best): best = t
        if best: pts.append((dx*best, dy*best))
    mr = sum(math.hypot(x,y) for x,y in pts)/len(pts)
    k = max(scale, 30/mr) if mr else scale
    pts = [(cx+x*k, cy+y*k) for x,y in pts]
    # smooth
    sm = []
    for i in range(len(pts)):
        a,b,c = pts[i-1], pts[i], pts[(i+1)%len(pts)]
        sm.append(((a[0]+2*b[0]+c[0])/4, (a[1]+2*b[1]+c[1])/4))
    return fmt(sm, True), (cx, cy)

# walk spots: city parks only (Dan does not walk in Hoia or Făget forests)
spots = [
  ('central', 'Parcul Central Simion Bărnuțiu', 0.72),
  ('babes', 'Parcul Sportiv Universitar prof. dr. Iuliu Hațieganu', 0.72),
  ('feroviarilor', 'Parcul Feroviarilor', 0.72),
  ('armatura', 'Parcul Armătura', 0.72),
  ('iulius', 'Iulius Parc', 0.72),
  ('vlaicu', 'Parcul Aurel Vlaicu', 0.72),
  ('detunata', 'Parcul Detunata', 0.72),
  ('colina', 'Parcul Colina', 0.72),
]
routes = {}
for key, name, sc in spots:
    rs = parks.get(name)
    if not rs: sys.exit('missing park in OSM data: ' + name)
    r = max(rs, key=area)
    d, c = loop(r, sc)
    routes[key] = {'d': d, 'c': [round(c[0],1), round(c[1],1)]}
    print(key, 'centre', [round(c[0]), round(c[1])])

# riverside walk: an open path along the Someș, in Grigorescu, west of Parcul Rozelor
X0, X1 = 130, 295
riv = max((geom(e['geometry']) for e in load('river') if e.get('tags',{}).get('name') == 'Someșul Mic'),
          key=lambda g: sum(1 for x, y in g if X0 <= x <= X1))
seg = [(x, y) for x, y in riv if X0 <= x <= X1]
if seg[0][0] > seg[-1][0]: seg.reverse()
seg = dp(seg, 1.5)
seg = [seg[0]] + [((a[0]+2*b[0]+c[0])/4, (a[1]+2*b[1]+c[1])/4 + 7) for a, b, c in zip(seg, seg[1:], seg[2:])] + [seg[-1]]
seg[0] = (seg[0][0], seg[0][1] + 7); seg[-1] = (seg[-1][0], seg[-1][1] + 7)
mid = seg[len(seg)//2]
routes['somes'] = {'d': fmt(seg), 'c': [round(mid[0],1), round(mid[1],1)], 'open': True}
print('somes centre', [round(mid[0]), round(mid[1])], 'points', len(seg))
json.dump({'w': W, 'h': round(H,1), 'layers': layers, 'routes': routes}, open(OUT,'w'), ensure_ascii=False)
print('H', round(H), {k: len(v) for k,v in layers.items()})
