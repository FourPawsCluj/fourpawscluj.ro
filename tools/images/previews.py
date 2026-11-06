"""Tiny blurred previews of every photo, shown while the real photo loads.

Writes src/previews.json: {"central-1": "data:image/webp;base64,...", ...} for each
src/static/img/*.webp. tools/build.py puts them in the page as the photo's background.
Run again after adding or replacing a photo. Needs cwebp (Homebrew `webp`).

    python3 -I tools/images/previews.py
"""
import base64, glob, json, os, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMG = os.path.join(ROOT, 'src', 'static', 'img')
OUT = os.path.join(ROOT, 'src', 'previews.json')

out = {}
with tempfile.TemporaryDirectory() as tmp:
    for f in sorted(glob.glob(os.path.join(IMG, '*.webp'))):
        name = os.path.splitext(os.path.basename(f))[0]
        t = os.path.join(tmp, 'p.webp')
        subprocess.run(['cwebp', '-quiet', '-resize', '16', '0', '-q', '40', '-m', '6', f, '-o', t], check=True)
        with open(t, 'rb') as fh:
            out[name] = 'data:image/webp;base64,' + base64.b64encode(fh.read()).decode()
with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(out, fh, indent=0, sort_keys=True)
    fh.write('\n')
print(f'{len(out)} previews, {os.path.getsize(OUT)} bytes → {os.path.relpath(OUT, ROOT)}')
