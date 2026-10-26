"""Static build for travelwithglenshop.com. Run: python3 build.py  ->  dist/
Reads raw/export.json (live WooCommerce export), data_images.json and shop_config.py."""
import html, json, os, re, shutil
from datetime import date
from urllib.parse import quote_plus, urlparse

import shop_config as C

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
D = json.load(open(os.path.join(ROOT, "raw/export.json")))
IMAGES = json.load(open(os.path.join(ROOT, "data_images.json")))
TODAY = date.today().isoformat()
YEAR = date.today().year

def esc(s): return html.escape(html.unescape(str(s or "")), quote=True)
def txt(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()
def path_of(url): return urlparse(url).path or "/"
def utm(url, campaign):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}utm_source=shop&utm_medium=crosslink&utm_campaign={campaign}"

# ---------- categories ----------
CATS = {c["id"]: c for c in D["product_categories"]}
CAT_BY_SLUG = {c["slug"]: c for c in D["product_categories"]}
def cat_path(c): return path_of(c["permalink"])
def ancestors(cid):
    out = []
    while cid and cid in CATS:
        out.append(cid); cid = CATS[cid]["parent"]
    return out
COLL = {c["key"]: c for c in C.COLLECTIONS}

# ---------- products ----------
def amazon_link(p):
    pid = p["id"]
    if pid in C.ASIN_OVERRIDES:
        return f"https://www.amazon.com/dp/{C.ASIN_OVERRIDES[pid]}?tag={C.AMAZON_TAG}", "Amazon"
    if pid in C.SEARCH_FALLBACK:
        return f"https://www.amazon.com/s?k={quote_plus(C.SEARCH_FALLBACK[pid])}&tag={C.AMAZON_TAG}", "Amazon"
    u = p["add_to_cart"]["url"] or ""
    m = re.search(r"/(?:dp|gp/product|gp/aw/d)/([A-Z0-9]{10})", u)
    if "amazon." in u and m:
        return f"https://www.amazon.com/dp/{m.group(1)}?tag={C.AMAZON_TAG}", "Amazon"
    if "redbubble.com" in u:
        return u, "Redbubble"
    raise SystemExit(f"Product {pid} has no usable outbound link: {u}")

def collection_for(p):
    for c in p["categories"]:
        for aid in ancestors(c["id"]):
            k = C.CAT_TO_COLLECTION.get(CATS[aid]["slug"])
            if k: return k
    name = txt(p["name"]).lower()
    for words, key in C.KEYWORD_RULES:
        if any(w in name for w in words): return key
    return "packing"

def guide_for(p, coll):
    if coll["key"] == "guides":
        name = txt(p["name"]).lower()
        for words, href, label in C.GUIDE_KEYWORDS:
            if any(w in name for w in words): return href, label
    return coll["guide"]

def bullets(p, n=4):
    t = txt(p["short_description"])
    t = re.sub(r"^About this item\s*", "", t, flags=re.I)
    parts = [x.strip(" ;.") for x in re.split(r";\s+|\.\s+(?=[A-Z])|\s•\s", t) if len(x.strip()) > 25]
    junk = re.compile(r"return|refund|shipping option|drop off|previous page|next page|click|add to cart|customer service|warranty|guarantee|satisf|contact us|store|brand story|from the brand", re.I)
    parts = [x for x in parts if not junk.search(x)]
    out = []
    for x in parts[:n]:
        out.append(x if len(x) <= 190 else x[:187].rsplit(" ", 1)[0] + "...")
    return out

PRODUCTS, RETIRED = [], []
for p in D["products"]:
    if p["id"] in C.RETIRED_PRODUCT_IDS:
        RETIRED.append(p); continue
    if p["id"] in C.DUPLICATES:
        continue
    p["_path"] = path_of(p["permalink"])
    p["_name"] = txt(p["name"])
    p["_coll"] = collection_for(p)
    p["_link"], p["_merchant"] = amazon_link(p)
    p["_imgs"] = IMAGES.get(f"p{p['id']}", [])
    PRODUCTS.append(p)
BY_ID = {p["id"]: p for p in D["products"]}

def products_in_cat(cid):
    slug = CATS[cid]["slug"]
    coll_key = next((c["key"] for c in C.COLLECTIONS if c["cat"] == slug), None)
    out = []
    for p in PRODUCTS:
        cats = {a for c in p["categories"] for a in ancestors(c["id"])}
        if cid in cats or (coll_key and p["_coll"] == coll_key):
            out.append(p)
        elif slug in ("travel-kits",) and p["_coll"] == "care":
            out.append(p)
    return out

# ---------- layout ----------
NAV = [(f"{CAT_BY_SLUG[c['cat']]['permalink']}", c["name"].split(" and ")[0].replace("Travel With Glen ", "")) for c in C.COLLECTIONS[:5]]

def layout(title, desc, path, body, noindex=False, jsonld=None, og_image=None, extra_head=""):
    canon = C.SITE + path
    ogi = C.SITE + (og_image or "/logo-twg.webp")
    nav = "".join(f'<a href="{path_of(h)}">{esc(l)}</a>' for h, l in NAV)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0F4D3A">
<script async src="https://www.googletagmanager.com/gtag/js?id={C.GA4_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{C.GA4_ID}');</script>
<script>try{{var t=localStorage.getItem('twg-theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}</script>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="{'noindex, follow' if noindex else 'index, follow, max-image-preview:large'}">
<meta property="og:site_name" content="Travel With Glen Shop"><meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{ogi}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Source+Sans+3:wght@400;600;700&display=swap">
<link rel="stylesheet" href="/global.css"><link rel="stylesheet" href="/shop.css">
{extra_head}
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap">
<a href="/" class="brand" aria-label="Travel With Glen Shop home"><img class="brand-logo" src="/logo-twg.webp" alt="" width="44" height="44"><span class="brand-name">Travel With Glen <span class="shop-word">Shop</span></span></a>
<nav class="nav" aria-label="Main"><a href="/shop/">All gear</a><a href="/kits/">Kits</a>{nav}
<button type="button" class="theme-toggle" id="theme-toggle" aria-label="Switch between light and dark mode"><svg class="i-moon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/></svg><svg class="i-sun" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>
<a href="{utm(C.MAIN + '/guide/', 'nav')}" class="nav-cta">Plan a trip</a>
</nav></div></header>
<div class="disclosure-bar">As an Amazon Associate, Travel With Glen earns from qualifying purchases. Links go to Amazon or Redbubble; we never take payment here. <a href="/affiliate-disclosure/">Details</a></div>
<main id="main">
{body}
</main>
{footer()}
<script>
(function(){{var b=document.getElementById('theme-toggle');if(b)b.addEventListener('click',function(){{var r=document.documentElement;var c=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{{localStorage.setItem('twg-theme',n)}}catch(e){{}}}});
document.addEventListener('click',function(e){{var a=e.target.closest&&e.target.closest('a[data-aff]');if(a&&window.gtag)gtag('event','affiliate_click',{{merchant:a.dataset.aff,product_id:a.dataset.pid||'',collection:a.dataset.coll||'',link_url:a.href}});}});}})();
</script>
</body></html>"""

def footer():
    return f"""<footer class="site-footer"><div class="wrap cols">
<div class="col"><span style="display:flex;align-items:center;gap:10px"><img src="/logo-twg.webp" alt="" width="48" height="48" style="border-radius:50%;background:#fff"><strong style="font-family:var(--display);font-size:20px">Travel With Glen Shop</strong></span>
<span>Gear and guidebooks Glen points travelers to. Every purchase happens on Amazon or Redbubble.</span></div>
<div class="col"><strong>The Travel With Glen network</strong>
<a href="{utm(C.MAIN + '/', 'footer')}">travelwithglen.com: where to go, when, where to stay</a>
<a href="{utm(C.VERIFIED + '/directory', 'footer')}">Verified Network: vetted local businesses</a>
<a href="/">Travel With Glen Shop: what to bring</a>
<a href="{utm(C.GDFIS + '/', 'footer')}">gdfis.com: how Glen builds it (for creators)</a></div>
<div class="col"><strong>Shop</strong><a href="/shop/">All gear</a><a href="/kits/">Travel kits</a>{''.join(f'<a href="{path_of(CAT_BY_SLUG[c["cat"]]["permalink"])}">{esc(c["name"])}</a>' for c in C.COLLECTIONS)}<a href="/blog/">Gear notes</a></div>
<div class="col"><strong>About</strong><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/affiliate-disclosure/">Affiliate disclosure</a><a href="/privacy-policy/">Privacy</a><a href="/terms-and-conditions/">Terms</a></div>
</div><div class="wrap legal">&copy; {YEAR} Travel With Glen LLC. As an Amazon Associate, Travel With Glen earns from qualifying purchases.</div></footer>"""

def img_tag(im, alt, cls="", eager=False, sizes="(max-width: 700px) 50vw, 280px"):
    if not im: return f'<div class="noimg {cls}" aria-hidden="true"></div>'
    return f'<img class="{cls}" src="{im["src"]}" alt="{esc(alt)}" width="{im["w"]}" height="{im["h"]}" loading="{"eager" if eager else "lazy"}" decoding="async">'

def buy_button(p, cls="btn btn-accent", label=None):
    label = label or f"View on {p['_merchant']}"
    return (f'<a class="{cls}" href="{esc(p["_link"])}" target="_blank" rel="sponsored nofollow noopener" '
            f'data-aff="{p["_merchant"].lower()}" data-pid="{p["id"]}" data-coll="{p["_coll"]}">{label} &rarr;</a>')

def card(p):
    badge = '<span class="badge">By Glen</span>' if p["id"] in C.GLEN_BOOK_IDS else ""
    im = p["_imgs"][0] if p["_imgs"] else None
    return (f'<article class="pcard">{badge}<a href="{p["_path"]}" class="pcard-img">{img_tag(im, p["_name"])}</a>'
            f'<div class="pcard-body"><a href="{p["_path"]}" class="pcard-title">{esc(short_name(p["_name"]))}</a>'
            f'{buy_button(p, "pcard-buy", "View on " + p["_merchant"])}</div></article>')

def short_name(n, limit=78):
    n = re.split(r"\s[|–]\s|,\s(?=[A-Z0-9])", n)[0]
    return n if len(n) <= limit else n[:limit].rsplit(" ", 1)[0] + "..."

def grid(ps): return '<div class="pgrid">' + "".join(card(p) for p in ps) + "</div>"

def crumbs_html(items):
    return '<nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(
        f'<a href="{h}">{esc(l)}</a>' if h else f"<span>{esc(l)}</span>" for h, l in items) + "</nav>"

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": html.unescape(l), "item": C.SITE + (h or "")}
        for i, (h, l) in enumerate(items) if h is not None]}

def flywheel_box(coll, guide=None, campaign="shop"):
    g_href, g_label = guide or coll["guide"]
    v_href, v_label = coll["verified"]
    return f"""<aside class="flywheel">
<div><span class="eyebrow">Planning the trip?</span><a href="{utm(C.MAIN + g_href, campaign)}">{esc(g_label)} &rarr;</a><small>Free guides on travelwithglen.com</small></div>
<div><span class="eyebrow">Need someone local you can trust?</span><a href="{utm(C.VERIFIED + v_href, campaign)}">{esc(v_label)} &rarr;</a><small>The Travel With Glen Verified Network</small></div>
</aside>"""

# ---------- writers ----------
WRITTEN, SITEMAP = [], []
def write(path, content, sitemap=True, lastmod=None):
    fp = os.path.join(DIST, path.lstrip("/"), "index.html") if path.endswith("/") else os.path.join(DIST, path.lstrip("/"))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w").write(content)
    WRITTEN.append(path)
    if sitemap: SITEMAP.append((path, lastmod or TODAY))


# ---------- home hero, carousel, motion (carried over from the WordPress/Elementor home page) ----------
HAS_VIDEO = os.path.exists(os.path.join(ROOT, "assets", "video", "shop-intro.mp4"))
HOME_HEAD = ('<link rel="preload" as="image" href="/img/hero/taormina-street.webp">'
    + '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Londrina+Shadow&family=Open+Sans:wdth,wght@75,400;75,600&display=swap">')

# Slides from the old home carousel, each now pointing at the collection it shows.
CAROUSEL = [
    ("gear-11", "Leather bags and travel accessories", "apparel"),
    ("gear-12", "Backpacks and boots on the trail", "outdoor"),
    ("gear-13", "Personal care and comfort for the road", "care"),
    ("gear-14", "Layers, boots and a bag for every day out", "apparel"),
    ("gear-15", "Friends, shoes and a camera at the ready", "tech"),
    ("gear-16", "Luggage lined up and ready to go", "packing"),
    ("gear-17", "Tech, chargers and gadgets for the trip", "tech"),
]

def home_hero():
    # Same sequence as the old Elementor hero: logo-reveal video plays once, then fades to the
    # Taormina street photo while the welcome copy slides in.
    video = ('<video class="vh-video" id="vh-video" muted playsinline preload="auto" poster="/video/shop-intro-poster.webp" aria-hidden="true">'
             '<source src="/video/shop-intro.mp4" type="video/mp4"></video>' if HAS_VIDEO else '')
    return f"""<section class="video-hero" id="video-hero"><img class="vh-bg" src="/img/hero/taormina-street.webp" alt="" width="1600" height="900" fetchpriority="high">{video}<div class="vh-shade"></div>
<div class="wrap vh-copy">
<span class="vh-kicker vh-in" style="--d:0s">Welcome to</span>
<h1 class="vh-title vh-in" style="--d:.15s">Travel With Glen Shop</h1>
<p class="vh-sub vh-in" style="--d:.35s">Your adventure starts here!</p>
<div class="row vh-in" style="--d:.55s"><a class="btn btn-accent" href="/shop/">Browse all gear</a><a class="btn btn-ghost vh-ghost" href="{utm(C.MAIN + '/guide/', 'home')}">Plan the trip first</a></div>
</div></section>"""

def home_carousel_intro():
    return """<section class="gear-intro"><div class="wrap narrow">
<h2 class="gi-title" data-anim="left">Gear up for your next adventure</h2>
<p data-anim="right">The gear and guidebooks Glen points travelers to, from packing cubes and plug adapters to the destination guides worth carrying. Every link goes to Amazon or Redbubble, so you buy with their shipping and returns.</p>
</div></section>"""

def home_carousel():
    slides = "".join(
        f'<a class="gc-slide{" is-on" if i == 0 else ""}" href="{path_of(CAT_BY_SLUG[COLL[k]["cat"]]["permalink"])}" aria-label="{esc(cap)}: shop {esc(COLL[k]["name"])}" {"" if i == 0 else "tabindex=-1 aria-hidden=true"}>'
        f'<img src="/img/hero/{f}.webp" alt="" width="1280" height="720" loading="{"eager" if i == 0 else "lazy"}" decoding="async">'
        f'<span class="gc-cap"><strong>{esc(COLL[k]["name"])}</strong>{esc(cap)}</span></a>'
        for i, (f, cap, k) in enumerate(CAROUSEL) if k in COLL)
    dots = "".join(f'<button type="button" class="gc-dot{" is-on" if i == 0 else ""}" aria-label="Show slide {i+1}"></button>' for i in range(len(CAROUSEL)))
    return f"""<section class="gear-carousel"><div class="wrap">
<h2 class="gc-title" data-anim="zoom">Travel gear and accessories that elevate your journeys</h2>
<div class="gc" id="gc" data-anim="zoom" aria-roledescription="carousel" aria-label="Featured travel gear">{slides}
<button type="button" class="gc-nav gc-prev" aria-label="Previous slide">&#8249;</button><button type="button" class="gc-nav gc-next" aria-label="Next slide">&#8250;</button>
<div class="gc-dots">{dots}</div></div>
</div></section>
<script>
(function(){{
var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
/* hero: logo video plays once, fades to the street photo, then the copy slides in (immediately for reduced motion) */
var hero=document.getElementById('video-hero'),v=document.getElementById('vh-video'),shown=false;
function reveal(){{if(!shown){{shown=true;hero.classList.add('is-ready');}}}}
function finish(){{hero.classList.add('video-done');reveal();}}
if(reduce||!v){{finish();}}else{{hero.classList.add('video-on');v.addEventListener('ended',finish);v.addEventListener('error',finish,true);setTimeout(finish,9000);var p=v.play&&v.play();if(p&&p.catch)p.catch(finish);}}
/* entrance animations */
var els=document.querySelectorAll('[data-anim]');
if(reduce||!('IntersectionObserver' in window)){{els.forEach(function(e){{e.classList.add('in')}})}}else{{var io=new IntersectionObserver(function(es){{es.forEach(function(x){{if(x.isIntersecting){{x.target.classList.add('in');io.unobserve(x.target);}}}})}},{{threshold:.15}});els.forEach(function(e){{io.observe(e)}});}}
/* carousel: auto-advance every 5s, pause on hover/focus, arrows and dots */
var gc=document.getElementById('gc');if(!gc)return;var s=gc.querySelectorAll('.gc-slide'),d=gc.querySelectorAll('.gc-dot'),i=0,t=null;
function go(n){{s[i].classList.remove('is-on');s[i].setAttribute('aria-hidden','true');s[i].tabIndex=-1;d[i].classList.remove('is-on');i=(n+s.length)%s.length;s[i].classList.add('is-on');s[i].removeAttribute('aria-hidden');s[i].removeAttribute('tabindex');d[i].classList.add('is-on');}}
function play(){{if(!reduce&&!t)t=setInterval(function(){{go(i+1)}},5000);}}function stop(){{clearInterval(t);t=null;}}
gc.querySelector('.gc-prev').onclick=function(){{go(i-1)}};gc.querySelector('.gc-next').onclick=function(){{go(i+1)}};
d.forEach(function(b,k){{b.onclick=function(){{go(k)}}}});
gc.addEventListener('mouseenter',stop);gc.addEventListener('mouseleave',play);gc.addEventListener('focusin',stop);gc.addEventListener('focusout',play);
document.addEventListener('visibilitychange',function(){{document.hidden?stop():play()}});play();
}})();
</script>"""

def build():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    shutil.copytree(os.path.join(ROOT, "assets"), DIST)
    shutil.copy(os.path.join(ROOT, "shop.css"), DIST)

    # Home
    tiles = "".join(
        f'<a class="ctile" href="{path_of(CAT_BY_SLUG[c["cat"]]["permalink"])}">'
        f'{img_tag((products_for_coll(c["key"])[0]["_imgs"] or [None])[0] if products_for_coll(c["key"]) else None, "", "ctile-img")}'
        f'<strong>{esc(c["name"])}</strong><span>{esc(c["blurb"])}</span><em>{len(products_for_coll(c["key"]))} picks</em></a>'
        for c in C.COLLECTIONS if products_for_coll(c["key"]))
    glen_books = [BY_ID[i] for i in sorted(C.GLEN_BOOK_IDS) if i in BY_ID and BY_ID[i] in PRODUCTS]
    body = home_hero() + home_carousel_intro() + f"""<section class="section"><div class="wrap"><h2 class="h2" data-anim="left">Shop by what you need</h2><div class="ctiles" data-anim="zoom">{tiles}</div></div></section>
<section class="section section-sand"><div class="wrap"><h2 class="h2">Travel kits</h2><p>Packing lists built around a trip. Start with the <a href="/kits/costa-rica/">Costa Rica Travel Kit</a>: rain, river, sun, bugs and trail in one list.</p><p><a class="btn btn-forest" href="/kits/">See all kits</a></p></div></section>""" + home_carousel() + f"""
<section class="section section-sand"><div class="wrap"><h2 class="h2">Books by Glen</h2><p>Written from the road, published under the Travel With Glen name.</p>{grid(glen_books)}</div></section>
<section class="section"><div class="wrap"><h2 class="h2">Guidebooks worth packing</h2>{grid([p for p in products_for_coll('guides') if p['id'] not in C.GLEN_BOOK_IDS][:8])}
<p><a class="btn btn-forest" href="{path_of(CAT_BY_SLUG['guides']['permalink'])}">All guidebooks</a></p></div></section>
<section class="section section-sand"><div class="wrap">{flywheel_box(COLL['guides'], ('/guide/', 'Start with a destination guide'), 'home')}</div></section>"""
    org = {"@context": "https://schema.org", "@type": "WebSite", "name": "Travel With Glen Shop", "url": C.SITE + "/",
           "publisher": {"@type": "Organization", "name": "Travel With Glen LLC", "url": C.MAIN + "/"}}
    write("/", layout("Travel With Glen Shop | Travel Gear and Guidebooks", "Travel gear and guidebooks Glen recommends, from packing cubes and plug adapters to destination guides. Links go to Amazon and Redbubble.", "/", body, jsonld=org, extra_head=HOME_HEAD))

    # /shop/
    sections = "".join(
        f'<section class="coll" id="{c["key"]}"><div class="head-row"><h2 class="h2">{esc(c["name"])}</h2>'
        f'<a href="{path_of(CAT_BY_SLUG[c["cat"]]["permalink"])}">See all {len(products_for_coll(c["key"]))}</a></div>'
        f'{grid(products_for_coll(c["key"]))}</section>' for c in C.COLLECTIONS if products_for_coll(c["key"]))
    items = [("/", "Home"), ("/shop/", "All gear")]
    write("/shop/", layout("All Travel Gear | Travel With Glen Shop", f"All {len(PRODUCTS)} travel picks in one place: guidebooks, packing, tech, outdoor, personal care and apparel.", "/shop/",
        f'<div class="wrap page-pad">{crumbs_html(items)}<h1 class="h1">All travel gear</h1><p class="lede">{len(PRODUCTS)} picks, grouped by what they solve.</p>{sections}</div>', jsonld=crumbs_ld(items)))

    # Category pages (all 34 old URLs; empty ones redirect)
    for c in D["product_categories"]:
        if c["slug"] == "uncategorized": continue
        ps = products_in_cat(c["id"])
        if not ps:
            REDIRECTS.append((cat_path(c), "/shop/", 301)); continue
        coll = next((x for x in C.COLLECTIONS if x["cat"] == c["slug"]), None) or COLL[C.CAT_TO_COLLECTION.get(c["slug"], "packing")]
        name = esc(c["name"])
        chain = [CATS[a] for a in reversed(ancestors(c["id"]))]
        items = [("/", "Home"), ("/shop/", "All gear")] + [(cat_path(x), txt(x["name"])) for x in chain]
        intro = coll["blurb"] if coll["cat"] == c["slug"] else f"{len(ps)} travel picks in {txt(c['name'])}."
        title = (coll["name"] if coll["cat"] == c["slug"] else txt(c["name"]))
        body = (f'<div class="wrap page-pad">{crumbs_html(items)}<h1 class="h1">{esc(title)}</h1><p class="lede">{esc(intro)}</p>'
                f'{grid(ps)}{flywheel_box(coll, campaign="cat-" + c["slug"])}</div>')
        write(cat_path(c), layout(f"{title} | Travel With Glen Shop", f"{intro} Handpicked by Travel With Glen; buy on Amazon.", cat_path(c), body,
              noindex=len(ps) < 2, jsonld=crumbs_ld(items)), sitemap=len(ps) >= 2)

    # Product pages
    for p in PRODUCTS:
        coll = COLL[p["_coll"]]
        g = guide_for(p, coll)
        main_cat = CAT_BY_SLUG[coll["cat"]]
        items = [("/", "Home"), (path_of(main_cat["permalink"]), coll["name"]), (p["_path"], short_name(p["_name"], 60))]
        gallery = "".join(img_tag(im, p["_name"] if i == 0 else "", "gimg", eager=(i == 0)) for i, im in enumerate(p["_imgs"]))
        bl = bullets(p) if p["_merchant"] == "Redbubble" else []
        quick = ('<h2 class="h3">About this design</h2><ul class="quick">' + "".join(f"<li>{esc(b)}</li>" for b in bl) + "</ul>") if bl else ""
        quick += f'<div class="tip"><strong>Before you buy</strong><p>{esc(coll["tip"])}</p></div>'
        badge = '<span class="badge badge-inline">By Glen</span>' if p["id"] in C.GLEN_BOOK_IDS else ""
        related = [x for x in products_for_coll(p["_coll"]) if x["id"] != p["id"]][:4]
        body = f"""<div class="wrap page-pad">{crumbs_html(items)}
<div class="pdp"><div class="gallery">{gallery or img_tag(None, '')}</div>
<div class="pdp-info">{badge}<h1 class="h1 pdp-title">{esc(p['_name'])}</h1>
<p class="pdp-why">In Glen's {esc(coll['name'].lower())} picks. {esc(coll['blurb'])}</p>
{buy_button(p)}
<p class="small-note">Price, stock, shipping and returns are handled by {p['_merchant']}. Check the current price there.</p>
{quick}</div></div>
{flywheel_box(coll, g, 'product')}
{('<h2 class="h2">More ' + esc(coll['name'].lower()) + '</h2>' + grid(related)) if related else ''}
</div>"""
        desc = f"{short_name(p['_name'], 110)}. A Travel With Glen pick in {coll['name'].lower()}; view it on {p['_merchant']}."
        write(p["_path"], layout(f"{short_name(p['_name'], 60)} | Travel With Glen Shop", desc, p["_path"], body,
              jsonld=crumbs_ld(items), og_image=(p["_imgs"][0]["src"] if p["_imgs"] else None)))

    # Blog and posts
    posts = sorted(D["posts"], key=lambda x: x["date"], reverse=True)
    items = [("/", "Home"), ("/blog/", "Gear notes")]
    lst = "".join(f'<li><a href="{path_of(po["link"])}"><strong>{esc(po["title"])}</strong></a><small>{po["date"][:10]}</small></li>' for po in posts)
    write("/blog/", layout("Gear Notes | Travel With Glen Shop", "Short gear notes and gift lists from Travel With Glen.", "/blog/",
          f'<div class="wrap page-pad">{crumbs_html(items)}<h1 class="h1">Gear notes</h1><ul class="postlist">{lst}</ul>'
          f'<p>For full destination guides, head to <a href="{utm(C.MAIN + "/blog/", "blog")}">travelwithglen.com</a>.</p></div>', jsonld=crumbs_ld(items)))
    for po in posts:
        content = clean_post(po["content"])
        pi = items + [(path_of(po["link"]), txt(po["title"]))]
        write(path_of(po["link"]), layout(f"{txt(po['title'])} | Travel With Glen Shop", po.get("meta_desc") or txt(po["content"])[:150], path_of(po["link"]),
              f'<div class="wrap page-pad">{crumbs_html(pi)}<article class="article"><h1 class="h1">{esc(po["title"])}</h1><p class="meta">{po["date"][:10]}</p>'
              f'<div class="prose">{content}</div></article>{flywheel_box(COLL["packing"], campaign="post")}</div>', jsonld=crumbs_ld(pi)), lastmod=po["modified"][:10])

    # Static pages
    for path, title, desc, body in static_pages():
        write(path, layout(f"{title} | Travel With Glen Shop", desc, path, f'<div class="wrap page-pad narrow"><h1 class="h1">{esc(title)}</h1><div class="prose">{body}</div></div>'))

    # 404
    tiles404 = "".join(f'<a class="btn btn-ghost" href="{path_of(CAT_BY_SLUG[c["cat"]]["permalink"])}">{esc(c["name"])}</a>' for c in C.COLLECTIONS)
    open(os.path.join(DIST, "404.html"), "w").write(layout("Page not found | Travel With Glen Shop", "This page is not here.", "/404.html",
        f'<div class="wrap page-pad narrow"><h1 class="h1">That page is gone</h1><p class="lede">The shop moved and some old items were retired. Here is where the gear lives now.</p><div class="row wraprow">{tiles404}</div>'
        f'<p><a class="btn btn-accent" href="/shop/">Browse all gear</a></p></div>', noindex=True))

    build_kits()
    write_redirects(); write_sitemap()
    open(os.path.join(DIST, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {C.SITE}/sitemap.xml\n")
    print(f"Built {len(WRITTEN)} pages, {len(PRODUCTS)} products, {len(RETIRED)} retired, {len(REDIRECTS)} redirect rules")

# ---------- travel kits ----------
def kit_item(item, kit_slug):
    coll = "kit-" + kit_slug
    if "id" in item:
        p = BY_ID[item["id"]]
        name, link, merch, pid = short_name(p["_name"]), p["_link"], p["_merchant"], str(p["id"])
        im = p["_imgs"][0] if p["_imgs"] else None
        title = f'<a href="{p["_path"]}" class="kit-name">{esc(name)}</a>'
        badge = '<span class="badge badge-inline">By Glen</span>' if p["id"] in C.GLEN_BOOK_IDS else ""
    else:
        name, merch, pid, im, badge = item["name"], "Amazon", "search:" + item["search"], None, ""
        link = f"https://www.amazon.com/s?k={quote_plus(item['search'])}&tag={C.AMAZON_TAG}"
        title = f'<span class="kit-name">{esc(name)}</span>'
    label = "See options on Amazon" if "search" in item else f"View on {merch}"
    btn = (f'<a class="pcard-buy" href="{esc(link)}" target="_blank" rel="sponsored nofollow noopener" '
           f'data-aff="{merch.lower()}" data-pid="{esc(pid)}" data-coll="{coll}">{label} &rarr;</a>')
    return (f'<li class="kit-item"><div class="kit-thumb">{img_tag(im, "", "kit-img")}</div>'
            f'<div class="kit-text">{badge}{title}<p>{esc(item["why"])}</p></div><div class="kit-buy">{btn}</div></li>')

def kit_asins(kit):
    out = []
    for s in kit["sections"]:
        for it in s["items"]:
            if "id" in it and BY_ID[it["id"]]["_coll"] != "guides":
                m = re.search(r"/dp/([A-Z0-9]{10})", BY_ID[it["id"]]["_link"])
                if m: out.append(m.group(1))
    return out

def cart_link(asins):
    q = "&".join(f"ASIN.{i}={a}&Quantity.{i}=1" for i, a in enumerate(asins, 1))
    return f"https://www.amazon.com/gp/aws/cart/add.html?AssociateTag={C.AMAZON_TAG}&{q}"

def build_kits():
    if not getattr(C, "KITS", None): return
    cards = []
    for k in C.KITS:
        path = f"/kits/{k['slug']}/"
        n = sum(len(s["items"]) for s in k["sections"])
        items = [("/", "Home"), ("/kits/", "Travel kits"), (path, k["name"])]
        secs = "".join(f'<section class="kit-sec"><h2 class="h2">{esc(s["name"])}</h2><ul class="kit-list">'
                       + "".join(kit_item(it, k["slug"]) for it in s["items"]) + "</ul></section>" for s in k["sections"])
        asins = kit_asins(k)
        cart = (f'<p class="kit-cart"><a class="btn btn-accent" href="{esc(cart_link(asins))}" target="_blank" rel="sponsored nofollow noopener" '
                f'data-aff="amazon" data-pid="cart" data-coll="kit-{k["slug"]}">Add the {len(asins)} gear picks to your Amazon cart &rarr;</a>'
                f'<small>You review everything in your Amazon cart before buying. Remove what you already own.</small></p>') if asins else ""
        skip = "".join(f"<li>{esc(x)}</li>" for x in k["skip"])
        g_links = "".join(f'<li><a href="{utm(C.MAIN + h, "kit-" + k["slug"])}">{esc(l)} &rarr;</a></li>' for h, l in k["guides"])
        v_href, v_label = k["verified"]
        body = f"""<div class="wrap page-pad">{crumbs_html(items)}
<h1 class="h1">{esc(k['name'])}</h1><p class="lede">{esc(k['lede'])}</p>
<p>{esc(k['intro'])}</p>{cart}
<nav class="kit-toc" aria-label="Kit sections">{''.join(f'<a href="#s{i}">{esc(s["name"])}</a>' for i, s in enumerate(k["sections"]))}</nav>
{secs.replace('<section class="kit-sec">', '<section class="kit-sec">', 1)}
<section class="kit-sec tip"><strong>Leave these at home</strong><ul>{skip}</ul></section>
<aside class="flywheel"><div><span class="eyebrow">Planning the trip?</span><ul class="kit-guides">{g_links}</ul><small>Free guides on travelwithglen.com</small></div>
<div><span class="eyebrow">Need someone local you can trust?</span><a href="{utm(C.VERIFIED + v_href, 'kit-' + k['slug'])}">{esc(v_label)} &rarr;</a><small>The Travel With Glen Verified Network</small></div></aside>
</div>"""
        for i in range(len(k["sections"])):
            body = body.replace('<section class="kit-sec"><h2', f'<section class="kit-sec" id="s{i}"><h2', 1)
        ld = [crumbs_ld(items), {"@context": "https://schema.org", "@type": "ItemList", "name": k["name"], "numberOfItems": n,
              "itemListElement": [{"@type": "ListItem", "position": j + 1, "name": html.unescape(it.get("name") or short_name(BY_ID[it["id"]]["_name"]))}
                                  for j, it in enumerate([it for s in k["sections"] for it in s["items"]])]}]
        write(path, layout(f"{k['title']} | Travel With Glen Shop", k["desc"], path, body, jsonld=ld))
        cards.append(f'<a class="ctile" href="{path}"><strong>{esc(k["name"])}</strong><span>{esc(k["lede"])}</span><em>{n} items</em></a>')
    items = [("/", "Home"), ("/kits/", "Travel kits")]
    write("/kits/", layout("Travel Kits: Packing Lists by Trip | Travel With Glen Shop", "Ready-made packing kits from Travel With Glen, built around the trips Glen covers.", "/kits/",
          f'<div class="wrap page-pad">{crumbs_html(items)}<h1 class="h1">Travel kits</h1><p class="lede">Packing lists built around a trip, not a product category. Pick your trip, take what you need.</p><div class="ctiles">{"".join(cards)}</div></div>',
          jsonld=crumbs_ld(items)))

_coll_cache = {}
def products_for_coll(key):
    if key not in _coll_cache:
        ps = [p for p in PRODUCTS if p["_coll"] == key]
        ps.sort(key=lambda p: (p["id"] not in C.GLEN_BOOK_IDS, -p["id"]))
        _coll_cache[key] = ps
    return _coll_cache[key]

def clean_post(h):
    h = re.sub(r'<a href="https?://(?:www\.)?theinsidersviews\.com[^"]*">(.*?)</a>', r"\1", h)
    def fix(m):
        u = m.group(1)
        a = re.search(r"amazon\.com/.*?/(?:dp|gp/product)/([A-Z0-9]{10})", u)
        if a: return f'href="https://www.amazon.com/dp/{a.group(1)}?tag={C.AMAZON_TAG}" rel="sponsored nofollow noopener" target="_blank"'
        if u.startswith("https://travelwithglenshop.com"): return f'href="{path_of(u)}"'
        if u.startswith("https://travelwithglen.com"): return f'href="{utm(u, "post")}"'
        return m.group(0)
    return re.sub(r'href="([^"]+)"', fix, h)

def static_pages():
    c = C.CONTACT
    return [
        ("/about/", "About the shop", "Why Travel With Glen Shop exists and how it works.", f"""
<p>I'm Glen. I run <a href="{utm(C.MAIN + '/', 'about')}">Travel With Glen</a>: the YouTube channel, the destination guides, the Roku channel and the <a href="{utm(C.VERIFIED + '/directory', 'about')}">Verified Network</a> of local businesses.</p>
<p>People ask me what to pack, which guidebook to buy and what actually works on the road. This shop is that list in one place. It is a catalog, not a store: every link goes to Amazon (or Redbubble for Travel With Glen designs), so you buy with their shipping, returns and current prices.</p>
<p>Some links earn me a small commission at no extra cost to you. That income helps keep the free guides and videos going. Three of the books here are mine: the Bargain Traveler's Handbook, the Machu Picchu insider's guide and the Florida Keys guide.</p>
<h2>Where to go next</h2>
<ul><li><a href="{utm(C.MAIN + '/guide/', 'about')}">Destination guides</a> for where to go, when, and where to stay.</li>
<li><a href="{utm(C.VERIFIED + '/directory', 'about')}">The Verified Network</a> for vetted businesses on the ground.</li>
<li><a href="/shop/">All gear</a> when you are ready to pack.</li></ul>"""),
        ("/contact/", "Contact", "How to reach Travel With Glen Shop.", f"""
<p>Questions about a pick, or a product you think belongs on the list? Get in touch.</p>
<p><strong>Email:</strong> <a href="mailto:{c['email']}">{c['email']}</a><br><strong>Phone:</strong> {c['phone']}<br><strong>Mail:</strong> {c['address']}</p>
<p>Orders, shipping and returns are handled by Amazon or Redbubble. For an order problem, contact the seller through your account on that site.</p>"""),
        ("/affiliate-disclosure/", "Affiliate disclosure", "How Travel With Glen Shop earns money.", """
<p>Travel With Glen Shop is a catalog of products Travel With Glen recommends. We do not sell anything directly and never take payment on this site.</p>
<p><strong>As an Amazon Associate, Travel With Glen earns from qualifying purchases.</strong> When you click a product link and buy on Amazon, Amazon may pay us a commission. The price you pay is the same.</p>
<p>Travel With Glen designs are sold through Redbubble, which pays the designer a share of each sale.</p>
<p>Product details, prices and availability come from the seller and can change at any time. Check the seller's page before you buy.</p>"""),
        ("/privacy-policy/", "Privacy policy", "What Travel With Glen Shop collects and why.", f"""
<p>Last updated {TODAY}.</p>
<h2>What we collect</h2><p>This site does not have accounts, a cart or a checkout, and it does not collect payment details. We use Google Analytics 4 to understand which pages are useful. It sets cookies and records anonymized usage data such as pages viewed, approximate location and device type, plus clicks on outbound product links.</p>
<h2>When you leave for a seller</h2><p>Links to Amazon and Redbubble take you to their sites, where their privacy policies apply. Amazon may set a cookie that tells it a purchase came from our link.</p>
<h2>If you contact us</h2><p>If you email us, we use your address only to reply.</p>
<h2>Your choices</h2><p>You can block or delete cookies in your browser, or use Google's opt-out add-on for Analytics. Questions: <a href="mailto:{c['email']}">{c['email']}</a>.</p>
<p>Travel With Glen LLC, {c['address']}.</p>"""),
        ("/terms-and-conditions/", "Terms and conditions", "Terms for using Travel With Glen Shop.", f"""
<p>Last updated {TODAY}.</p>
<p>Travel With Glen Shop (travelwithglenshop.com) is operated by Travel With Glen LLC. It is a catalog of recommended products. We do not sell, ship or return products.</p>
<h2>Purchases</h2><p>All purchases happen on the seller's site (Amazon or Redbubble) under that seller's terms, prices, shipping and return policies. For refunds or returns, contact the seller.</p>
<h2>Information on this site</h2><p>We try to keep product information accurate, but details come from sellers and can change. Recommendations are our opinion, not a guarantee of fitness for any purpose.</p>
<h2>Commissions</h2><p>Some links are affiliate links. See the <a href="/affiliate-disclosure/">affiliate disclosure</a>.</p>
<h2>Contact</h2><p><a href="mailto:{c['email']}">{c['email']}</a>, {c['address']}.</p>"""),
    ]

REDIRECTS = []
EXPECT = {}
def write_redirects():
    lines = ["# Generated by build.py. Old WordPress/WooCommerce URLs.", "# Retired products (off-topic): 410 Gone"]
    for p in RETIRED:
        lines.append(f"{path_of(p['permalink'])} /404.html 410"); EXPECT[path_of(p["permalink"])] = (410, None)
    lines.append("# Duplicate listings")
    for old, new in C.DUPLICATES.items():
        o, n = path_of(BY_ID[old]["permalink"]), path_of(BY_ID[new]["permalink"])
        lines.append(f"{o} {n} 301"); EXPECT[o] = (301, n)
    lines.append("# Old pages")
    for o, n in C.PAGE_REDIRECTS.items():
        lines.append(f"{o} {n} 301"); EXPECT[o] = (301, n)
    for o in C.PAGES_GONE:
        lines.append(f"{o} /404.html 410"); EXPECT[o] = (410, None)
    for o, n, s in REDIRECTS:
        lines.append(f"{o} {n} {s}"); EXPECT[o] = (s, n)
    lines.append("# Product tags -> the collection of the first live product with that tag")
    for t in D["product_tags"]:
        o = path_of(t.get("link") or f"/product-tag/{t['slug']}/")
        target = "/shop/"
        for p in PRODUCTS:
            if any(x["slug"] == t["slug"] for x in p["tags"]):
                target = path_of(CAT_BY_SLUG[COLL[p["_coll"]]["cat"]]["permalink"]); break
        lines.append(f"{o} {target} 301"); EXPECT[o] = (301, target)
    lines.append("# Blog taxonomy -> /blog/")
    for t in D["post_tags"] + D["post_categories"]:
        o = path_of(t["link"]); lines.append(f"{o} /blog/ 301"); EXPECT[o] = (301, "/blog/")
    lines += ["/tag/* /blog/ 301", "/category/* /blog/ 301", "/product-tag/* /shop/ 301",
              "/feed/ / 301", "/comments/feed/ / 301", "/product/*/feed/ /shop/ 301",
              "/sitemap_index.xml /sitemap.xml 301", "/product-sitemap.xml /sitemap.xml 301", "/page-sitemap.xml /sitemap.xml 301",
              "/product_cat-sitemap.xml /sitemap.xml 301", "/post-sitemap.xml /sitemap.xml 301"]
    open(os.path.join(DIST, "_redirects"), "w").write("\n".join(lines) + "\n")
    for w in WRITTEN: EXPECT.setdefault(w, (200, None))
    json.dump({k: list(v) for k, v in sorted(EXPECT.items())}, open(os.path.join(ROOT, "url_expectations.json"), "w"), indent=0)

def write_sitemap():
    urls = "".join(f"<url><loc>{C.SITE}{p}</loc><lastmod>{m}</lastmod></url>" for p, m in SITEMAP)
    open(os.path.join(DIST, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')

if __name__ == "__main__":
    build()
