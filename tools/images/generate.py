"""Generates the site photos with OpenAI gpt-image-2 and saves them as WebP in src/static/img/.

    OPENAI_API_KEY=... python3 -I tools/images/generate.py            # only missing images
    OPENAI_API_KEY=... python3 -I tools/images/generate.py --force faget-2 hero

The account only accepts 1024x1024, so every image is square; the page crops with object-fit.
PNG originals stay in tools/images/raw/ (gitignored). Needs `cwebp` (Homebrew `webp`).
Cost: about $0.165 per image at quality "high".
"""
import base64, concurrent.futures as cf, json, os, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, 'tools', 'images', 'raw')
OUT = os.path.join(ROOT, 'src', 'static', 'img')

DOG = ('The same dog in every photo: an English Cocker Spaniel with a golden-red coat, long wavy feathered ears, '
       'dark brown eyes, a happy face, wearing an olive-green harness with a matching olive-green leash.')
STYLE = ('Photorealistic candid photo, natural soft daylight, late spring, lush green, shot on a full-frame camera, '
         'shallow depth of field, warm natural colors, real-life feel, not staged. '
         'No text, no logos, no watermark. If a person appears, show only hands or legs, never a face.')

IMAGES = {
    'hero': 'Dog\'s-eye view: camera on the ground at 30 cm height, the cocker spaniel trotting straight toward the camera on a park path, ears bouncing, tall old trees and a lake softly blurred behind, in Cluj-Napoca, Romania.',
    'central-1': 'Parcul Central in Cluj-Napoca: the cocker spaniel trotting on a gravel alley beside the park lake with small rowing boats, the white historic Casino building among old trees in the background.',
    'central-2': 'The cocker spaniel sitting on a shady park alley under old plane trees, looking up at the camera, a wooden park bench behind.',
    'central-3': 'The cocker spaniel standing at the edge of a calm park lake, watching ducks on the water, leash held by a hand at the frame edge.',
    'iulius-1': 'A modern city park around a lake in Cluj-Napoca: the cocker spaniel running happily on a wide paved path along the lake, modern glass office buildings far in the background.',
    'iulius-2': 'The cocker spaniel walking on a wooden boardwalk by a lake in a modern park, reeds along the water.',
    'iulius-3': 'Close-up of the cocker spaniel sniffing colorful flowers in a park flower bed, nose deep in the flowers.',
    'feroviarilor-1': 'A small quiet city park: the cocker spaniel walking on a path under big old chestnut trees, the walker visible only from the knees down, leash slack.',
    'feroviarilor-2': 'The cocker spaniel lying relaxed on fresh green grass in a small city park, tongue out, dappled sunlight.',
    'feroviarilor-3': 'The cocker spaniel drinking water from a collapsible travel bowl held by a hand, on a park path.',
    'babes-1': 'A large city park in Cluj-Napoca next to the Someș river: the cocker spaniel trotting on a long tree-lined alley, the river glimpsed through the trees.',
    'babes-2': 'The cocker spaniel running across a wide lawn in a big city park, ears flying, tall trees behind.',
    'babes-3': 'The cocker spaniel sitting by a riverside railing in a city park, the calm Someș river and green bank behind.',
    'armatura-1': 'A modern neighbourhood park in Cluj-Napoca with wide paved paths and young trees: the cocker spaniel walking happily along the path, apartment blocks softly blurred far behind.',
    'armatura-2': 'The cocker spaniel sniffing a lawn edge next to a wide park path in a modern city park.',
    'armatura-3': 'The cocker spaniel standing on a park path looking back at the camera, tail up, modern park benches behind.',
    'vlaicu-1': 'A park between small lakes in a Cluj-Napoca neighbourhood: the cocker spaniel walking on a path along the water, reeds and willow trees.',
    'vlaicu-2': 'The cocker spaniel looking at the water from a grassy lake bank, willow branches hanging above.',
    'vlaicu-3': 'The cocker spaniel trotting on a lakeside path at golden hour, warm light on its coat.',
    'detunata-1': 'A quiet small neighbourhood park with mature trees and benches: the cocker spaniel strolling calmly on a shaded path.',
    'detunata-2': 'Close-up of the cocker spaniel resting its chin on a park bench seat, looking at the camera.',
    'detunata-3': 'The cocker spaniel sniffing fallen leaves under a big tree in a quiet park.',
    'colina-1': 'A neighbourhood park on a gentle hill: the cocker spaniel walking up a paved park path, trees on both sides.',
    'colina-2': 'The cocker spaniel sitting on grass on a small park hill, city rooftops softly blurred in the distance.',
    'colina-3': 'The cocker spaniel playing with a stick on a park lawn, mid-motion.',
    'somes-1': 'A riverside walkway along the Someș river in Cluj-Napoca: the cocker spaniel trotting on the paved path next to the river, trees along the bank.',
    'somes-2': 'The cocker spaniel standing on the grassy river bank looking at the flowing Someș river.',
    'somes-3': 'The cocker spaniel walking on a riverside path at sunset, river reflecting warm light.',
}
WIDTH = {'hero': 900}  # px of the WebP; others 720 (park card) — small cards reuse the same file


def generate(name, key):
    body = json.dumps({'model': 'gpt-image-2', 'prompt': f'{IMAGES[name]} {DOG} {STYLE}',
                       'size': '1024x1024', 'quality': 'high', 'n': 1}).encode()
    req = urllib.request.Request('https://api.openai.com/v1/images/generations', data=body,
                                 headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.load(r)
    png = os.path.join(RAW, name + '.png')
    with open(png, 'wb') as f:
        f.write(base64.b64decode(data['data'][0]['b64_json']))
    w = WIDTH.get(name, 720)
    subprocess.run(['cwebp', '-quiet', '-q', '80', '-resize', str(w), '0', png, '-o', os.path.join(OUT, name + '.webp')], check=True)
    return name, os.path.getsize(os.path.join(OUT, name + '.webp')) // 1024


def main():
    key = os.environ.get('OPENAI_API_KEY') or sys.exit('set OPENAI_API_KEY')
    args = sys.argv[1:]
    force = '--force' in args
    only = [a for a in args if a != '--force'] or list(IMAGES)
    os.makedirs(RAW, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    todo = [n for n in only if force or not os.path.exists(os.path.join(OUT, n + '.webp'))]
    print(f'{len(todo)} to make')
    with cf.ThreadPoolExecutor(4) as ex:
        futs = {ex.submit(generate, n, key): n for n in todo}
        for f in cf.as_completed(futs):
            try:
                n, kb = f.result(); print(f'{n}: {kb} KB')
            except Exception as e:
                msg = e.read().decode()[:300] if hasattr(e, 'read') else str(e)
                print(f'{futs[f]}: FAILED {msg}')


if __name__ == '__main__':
    main()
