"""Convert fetched images in assets/img to WebP (max 900px wide) and rewrite the manifest."""
import json, os
from PIL import Image
m = json.load(open("raw/images_manifest.json"))
out = {}
for key, paths in m["images"].items():
    new = []
    for p in paths:
        dest = os.path.splitext(p)[0] + ".webp"
        if not os.path.exists(dest):
            im = Image.open(p)
            if im.mode not in ("RGB", "RGBA"): im = im.convert("RGBA")
            if im.width > 900: im = im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS)
            im.save(dest, "WEBP", quality=78, method=6)
        w, h = Image.open(dest).size
        new.append({"src": "/" + dest.replace("assets/", ""), "w": w, "h": h})
        if p != dest and os.path.exists(p): os.remove(p)
    out[key] = new
json.dump(out, open("data_images.json", "w"), indent=1)
print(sum(len(v) for v in out.values()), "webp")
