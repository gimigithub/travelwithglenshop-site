"""Download product and category images from the Jetpack CDN into assets/img.
Up to 4 images per product, resized to 1000px wide by the CDN. Runs on a GitHub runner."""
import json, os, re, time, urllib.request
from urllib.parse import urlparse, urlencode
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"
d = json.load(open("raw/export.json"))
os.makedirs("assets/img/p", exist_ok=True); os.makedirs("assets/img/c", exist_ok=True)
manifest, fails = {}, []
def fetch(src, dest_base):
    base = src.split("?")[0]
    ext = os.path.splitext(urlparse(base).path)[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"): ext = ".jpg"
    url = base + "?" + urlencode({"w": 1000, "ssl": 1})
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            dest = dest_base + ext
            open(dest, "wb").write(data)
            return dest
        except Exception as e:
            err = str(e); time.sleep(2)
    fails.append(f"{src}: {err}")
for p in d["products"]:
    out = []
    for i, im in enumerate(p["images"][:4]):
        got = fetch(im["src"], f"assets/img/p/{p['id']}-{i}")
        if got: out.append(got)
    manifest[f"p{p['id']}"] = out
for c in d["product_categories"]:
    if c.get("image"):
        got = fetch(c["image"], f"assets/img/c/{c['id']}")
        if got: manifest[f"c{c['id']}"] = [got]
json.dump({"images": manifest, "fails": fails}, open("raw/images_manifest.json", "w"), indent=1)
print(sum(len(v) for v in manifest.values()), "images,", len(fails), "failures")
for f in fails[:20]: print(f)
