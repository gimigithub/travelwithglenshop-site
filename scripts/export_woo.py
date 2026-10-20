"""Pull everything the static shop needs from the live WordPress/WooCommerce site.
Runs on a GitHub runner (the build workspace cannot reach the shop)."""
import json, os, re, sys, time, hashlib, urllib.request, urllib.error
from urllib.parse import urlparse

BASE = "https://travelwithglenshop.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
OUT = "raw"
os.makedirs(f"{OUT}/sitemaps", exist_ok=True)
os.makedirs(f"{OUT}/images", exist_ok=True)
log = []

def get(url, binary=False):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                return (data if binary else data.decode("utf-8", "replace")), r.status, dict(r.headers)
        except urllib.error.HTTPError as e:
            if e.code in (404, 410, 401, 403):
                return None, e.code, {}
        except Exception as e:
            log.append(f"retry {attempt} {url}: {e}")
        time.sleep(3)
    return None, 0, {}

def get_all(path):
    items, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        body, status, headers = get(f"{BASE}{path}{sep}per_page=100&page={page}")
        if not body:
            log.append(f"{path} page {page}: status {status}")
            break
        try:
            chunk = json.loads(body)
        except json.JSONDecodeError:
            log.append(f"{path} page {page}: not JSON"); break
        if not isinstance(chunk, list) or not chunk:
            break
        items += chunk
        total_pages = int(headers.get("X-WP-TotalPages") or headers.get("x-wp-totalpages") or 1)
        if page >= total_pages:
            break
        page += 1
    return items

datasets = {
    "products": "/wp-json/wc/store/v1/products",
    "product_categories": "/wp-json/wc/store/v1/products/categories",
    "product_tags": "/wp-json/wc/store/v1/products/tags",
    "pages": "/wp-json/wp/v2/pages",
    "posts": "/wp-json/wp/v2/posts",
    "post_categories": "/wp-json/wp/v2/categories",
    "post_tags": "/wp-json/wp/v2/tags",
    "media": "/wp-json/wp/v2/media",
}
counts = {}
for name, path in datasets.items():
    data = get_all(path)
    counts[name] = len(data)
    with open(f"{OUT}/{name}.json", "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)

# Sitemaps: index plus every child sitemap, and a flat list of every URL Google may know
idx, _, _ = get(f"{BASE}/sitemap_index.xml")
urls = set()
if idx:
    open(f"{OUT}/sitemaps/sitemap_index.xml", "w").write(idx)
    for child in re.findall(r"<loc>([^<]+)</loc>", idx):
        name = os.path.basename(urlparse(child).path) or "child.xml"
        body, status, _ = get(child)
        if body:
            open(f"{OUT}/sitemaps/{name}", "w").write(body)
            for u in re.findall(r"<loc>([^<]+)</loc>", body):
                if urlparse(u).netloc.endswith("travelwithglenshop.com"):
                    urls.add(urlparse(u).path)
        else:
            log.append(f"sitemap {child}: {status}")
open(f"{OUT}/sitemap_paths.txt", "w").write("\n".join(sorted(urls)) + "\n")

# Images used by products, categories and pages (originals only)
img_urls = set()
for p in json.load(open(f"{OUT}/products.json")):
    for im in p.get("images", []):
        if im.get("src"): img_urls.add(im["src"])
for c in json.load(open(f"{OUT}/product_categories.json")):
    im = c.get("image") or {}
    if isinstance(im, dict) and im.get("src"): img_urls.add(im["src"])
manifest = {}
for u in sorted(img_urls):
    path = urlparse(u).path
    local = path.split("/wp-content/uploads/", 1)[-1].lstrip("/") if "/wp-content/uploads/" in path else "ext/" + hashlib.sha1(u.encode()).hexdigest()[:12] + os.path.splitext(path)[1]
    dest = f"{OUT}/images/{local}"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    data, status, _ = get(u, binary=True)
    if data:
        open(dest, "wb").write(data)
        manifest[u] = local
    else:
        log.append(f"image {u}: {status}")
json.dump(manifest, open(f"{OUT}/images_manifest.json", "w"), indent=1)

counts["sitemap_urls"] = len(urls)
counts["images"] = len(manifest)
json.dump({"exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "counts": counts, "log": log},
          open(f"{OUT}/export_report.json", "w"), indent=1)
print(json.dumps(counts, indent=1)); print("\n".join(log))
if counts["products"] == 0:
    sys.exit("No products exported")
