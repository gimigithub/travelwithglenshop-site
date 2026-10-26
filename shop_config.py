"""Editable settings for the static shop. Change a line here, push, Netlify rebuilds."""

SITE = "https://travelwithglenshop.com"
AMAZON_TAG = "travelwith085-20"
GA4_ID = "G-XC0EJBMQH5"  # same property as travelwithglen.com, split by hostname
MAIN = "https://travelwithglen.com"
VERIFIED = "https://verified.travelwithglen.com"
GDFIS = "https://gdfis.com"

# Shop collections (what visitors browse). Each maps to an existing category URL so no new URLs are needed.
# guide = the travelwithglen.com hub for planners; verified = the Verified page for "who to trust on the ground".
COLLECTIONS = [
    {"key": "guides", "tip": 'Check the edition year on Amazon before you buy. A guidebook more than two years old will miss closures, new routes and price changes.', "name": "Guidebooks", "cat": "guides",
     "blurb": "Destination guides worth packing, plus the books Glen wrote himself.",
     "guide": ("/guide/", "Browse every Travel With Glen guide"),
     "verified": ("/destinations", "Vetted businesses by destination")},
    {"key": "packing", "tip": "Measure your bag first. Compression cubes save space but add weight, so check your airline's carry-on weight limit as well as its size.", "name": "Packing and Organization", "cat": "accessories",
     "blurb": "Cubes, pouches, pillows and organizers that keep a carry-on under control.",
     "guide": ("/budget-travel-guides/", "Budget travel guides"),
     "verified": ("/collections/glen-recommended", "Places Glen recommends")},
    {"key": "tech", "tip": 'Check the plug type for every country on your route. Most of Europe uses Type C/F; the UK uses Type G; Costa Rica uses the same Type A/B as the US.', "name": "Tech and Power", "cat": "technology",
     "blurb": "Chargers, plug adapters and a travel router for staying connected abroad.",
     "guide": ("/budget-travel-guides/", "Budget travel guides"),
     "verified": ("/collections/digital-nomad-friendly", "Digital-nomad-friendly spots")},
    {"key": "outdoor", "tip": 'Pack for the wet season even in the dry months. A dry bag and a water filter earn their space on almost any river, beach or hike day.', "name": "Outdoor and Adventure", "cat": "outdoor-equipment",
     "blurb": "Dry bags, water filters, first aid and daypacks for hikes and river days.",
     "guide": ("/adventure-travel-guide/", "Adventure travel guide"),
     "verified": ("/collections/hidden-gems", "Hidden gems in the Verified Network")},
    {"key": "care", "tip": 'Carry-on liquids are capped at 3.4 oz (100 ml) per container in one quart-size bag in the US. Solid sticks and wipes skip that limit.', "name": "Personal Care To Go", "cat": "personal-care-kits",
     "blurb": "TSA-size toiletries, travel shavers, folding brushes and deodorant wipes.",
     "guide": ("/budget-travel-guides/", "Budget travel guides"),
     "verified": ("/collections/glen-verified", "Glen-verified businesses")},
    {"key": "apparel", "tip": 'Check the size chart on the listing, not just your usual size. Fit varies a lot between brands sold on Amazon.', "name": "Travel Apparel", "cat": "apparel",
     "blurb": "Comfortable layers, jeans and shirts that pack well.",
     "guide": ("/best-time-to-visit-costa-rica-2026/", "When to go (and what to pack) for Costa Rica"),
     "verified": ("/collections/glen-recommended", "Places Glen recommends")},
    {"key": "merch", "tip": 'Printed on demand and shipped by Redbubble, so check their delivery estimate if you need it before a trip.', "name": "Travel With Glen Merch", "cat": "travel-with-glen",
     "blurb": "Official Travel With Glen designs, printed on demand.",
     "guide": ("/guanacaste-guide/", "Glen's Guanacaste guide"),
     "verified": ("/directory", "Browse the Verified Network")},
]

# Category slug -> collection key (categories not listed fall back to keyword rules, then "packing").
CAT_TO_COLLECTION = {
    "guides": "guides", "accessories": "packing", "travel-gear": "packing",
    "technology": "tech", "electronics-gadgets": "tech", "networking-connectivity": "tech",
    "portable-wifi-routers": "tech", "wifi-routers": "tech",
    "outdoor-equipment": "outdoor", "personal-care-kits": "care", "toothbrush-and-toothpaste": "care",
    "travel-kits": "care",
    "apparel": "apparel", "clothing": "apparel", "women": "apparel", "jackets": "apparel", "shirts": "apparel",
    "tops": "apparel", "tees-blouses": "apparel", "pants-leggings": "apparel", "casual-pants": "apparel",
    "stretch-flex-pants": "apparel", "shoes-jewelry": "apparel", "blouses-button-down-shirts": "apparel",
    "trendy-styles": "apparel", "stylish-comfort": "apparel",
    "travel-with-glen": "merch", "christmas": "merch", "christmas-clothing": "merch", "holiday-gift-ideas": "merch",
    "premium-oversized-sweatshirt": "merch", "twg-tropical-christmas": "merch", "travel-inspired-apparel": "merch",
}
# Ordered keyword rules for products with no useful category (52 were "Uncategorized").
KEYWORD_RULES = [
    (("shaver", "razor", "comb", "brush", "deodorant", "antiperspirant", "toiletr", "body wash", "shower gel", "toothbrush"), "care"),
]

# Products dropped from the catalog: they return 410 Gone. Off-topic for a travel shop
# (listed for 410 in the Oct 20 plan). Remove an id here to bring a product back.
RETIRED_PRODUCT_IDS = {
    2228,  # tactical handgun case
    2406, 2404, 2399, 2397, 2395, 2393, 2391, 2389,  # self-help and trivia books
}

# Duplicate listings: id -> id of the product page that replaces it (301).
DUPLICATES = {
    2081: 2055,  # BAGAIL cubes, the "variable" copy was misconfigured
    2366: 2362,  # Glen's Florida Keys Travel Guide 2025: ASIN B0DLTDL8PZ is gone from Amazon (404, Oct 22 2026); 301 to Bargain Traveler's Handbook until a new edition is live
}

# Fixes for links in the WordPress data.
ASIN_OVERRIDES = {
    1839: "B0CBJKLGDB",  # amzn.to/3NSz3Nf resolved Oct 20
    1785: "B07SLGHB24",  # amzn.to/3UFuzNL resolved Oct 20
    1699: "B09N72FMH5",  # amzn.to/3AFb2Ga resolved Oct 20 (GL.iNet Opal travel router)
    2256: "B0DZ1PKCWT",  # B0BY2NZK9Y 404 on Oct 22 2026; same slim 10000mAh charger with built-in cables
    2572: "B0DSL1HJNR",  # B0DNFQB78J 404 on Oct 22 2026; same mini dual-head shaver, new listing
}
# Products with no Amazon link at all (were set up as "sellable"): link to a tagged Amazon search until an ASIN is added above.
SEARCH_FALLBACK = {
    1812: "siliteelon women's stain shield dress shirt wrinkle free",
    2453: "bath and body works travel size shower gel",  # B0D4SGVS3Z 404 on Oct 22 2026, no same listing
    2581: "mini portable electric shaver travel usb c",  # B0CXHFTRM5 404 on Oct 22 2026, no same listing
}

# Glen's own books get a "By Glen" badge.
GLEN_BOOK_IDS = {2366, 2364, 2362}

# Guidebook -> matching travelwithglen.com hub, by keyword in the title (first match wins).
GUIDE_KEYWORDS = [
    (("costa rica",), "/where-to-stay-in-costa-rica-2026-guide/", "Where to stay in Costa Rica"),
    (("paris", "barcelona", "italy", "spain", "portugal", "scandinavia", "ireland", "croatia", "amsterdam"), "/europe-guide/", "Europe travel guide"),
    (("japan",), "/asia-guide/", "Asia travel guide"),
    (("colombia", "machu picchu"), "/south-america-travel-guide/", "South America travel guide"),
    (("mexico city", "puerto rico"), "/central-america-guide/", "Central America and Caribbean guide"),
    (("florida", "usa", "50 states", "road atlas", "montreal", "united states"), "/america-guide/", "United States travel guide"),
    (("bargain", "budget"), "/budget-travel-guides/", "Budget travel guides"),
]

# Old WordPress pages: where they go now.
PAGE_REDIRECTS = {
    "/cart/": "/shop/", "/checkout/": "/shop/", "/my-account/": "/shop/", "/shop-2/": "/shop/",
    "/refunds/": "/terms-and-conditions/", "/customer-assurance-policies/": "/terms-and-conditions/",
    "/mission/": "/about/", "/gallery/": "/", "/author/globe-trotter/": "/about/",
    "/brand/travel-with-glen-llc/": "/shop/", "/product-category/uncategorized/": "/shop/",
    "/2024/11/06/": "/blog/",
}
PAGES_GONE = ["/testimonials/", "/63-2/", "/64-2/", "/elementor-hf/blog-page-header/"]

CONTACT = {
    "email": "sales@travelwithglenshop.com",
    "phone": "(877) 221-7615",
    "address": "100 East New York Avenue, Suite 103 PMB1010, DeLand, FL 32724",
}

# ---------- Travel kits ----------
# A kit is a curated packing page, not a bundled product: each item links to Amazon on its own.
# "id" = a product already in the catalog. "search" = an item not in the catalog yet; it links to a tagged
# Amazon search until Glen picks a specific listing (then add it to the catalog and switch to "id").
# "why" is the one-line reason it is in the kit. Glen: replace these with your own words where you can.
KITS = [
    {"slug": "costa-rica", "name": "Costa Rica Travel Kit",
     "title": "Costa Rica Packing Kit: What to Bring for Rainforest, Beach and Trail",
     "desc": "Glen's Costa Rica packing kit: rain and river gear, sun and bug protection, trail and wildlife gear, and the guidebooks worth reading first.",
     "lede": "Everything on Glen's Costa Rica list in one place, grouped by what the day throws at you: rain, river, sun, bugs and trail.",
     "intro": "Costa Rica packs differently from a city trip. You can get sun, a downpour and a muddy trail in the same afternoon, especially in the green season (roughly May to November). This kit covers those days. Buy only what your itinerary needs.",
     "skip": ["A plug adapter. Costa Rica uses the same Type A/B outlets and 120V power as the US.",
              "Heavy jeans and dress clothes. Quick-dry layers work better almost everywhere outside San José.",
              "Full-size toiletries. Pharmacies and supermarkets are easy to find in towns."],
     "guides": [("/guanacaste-guide/", "Glen's free Guanacaste guide"), ("/where-to-stay-in-costa-rica-2026-guide/", "Where to stay in Costa Rica"), ("/best-time-to-visit-costa-rica-2026/", "Best time to visit Costa Rica")],
     "verified": ("/destinations", "Vetted businesses by destination"),
     "sections": [
        {"name": "Rain and river days", "items": [
            {"id": 2206, "why": "Keeps a phone, passport and camera dry on boat tours, river floats and sudden storms."},
            {"id": 2182, "why": "For river crossings and wet trails when you do not want to change shoes."},
            {"search": "packable rain jacket lightweight travel", "name": "Packable rain jacket", "why": "Green season rain usually comes in the afternoon. A jacket that folds into its own pocket earns its space."},
            {"search": "water shoes quick dry hiking", "name": "Quick-dry water shoes", "why": "Rocky beaches, waterfalls and river entries are easier on your feet with these."}]},
        {"name": "Sun, bugs and heat", "items": [
            {"id": 2212, "why": "Long sleeves with UPF 50 cover you from sun and bugs at the same time."},
            {"search": "reef safe mineral sunscreen spf 50", "name": "Reef-safe mineral sunscreen", "why": "Bring more than you think. Sunscreen costs much more in beach towns."},
            {"search": "picaridin insect repellent travel size", "name": "Insect repellent (picaridin)", "why": "For dusk on the coast and any rainforest walk."},
            {"search": "quick dry microfiber travel towel", "name": "Quick-dry travel towel", "why": "Light, dries fast in humid air, and doubles as a beach blanket."}]},
        {"name": "Trails and wildlife", "items": [
            {"search": "lightweight waterproof hiking boots", "name": "Lightweight waterproof hiking boots", "why": "Arenal, Monteverde and Rincón de la Vieja trails get muddy. Break them in before the trip."},
            {"search": "compact binoculars for travel bird watching", "name": "Compact binoculars", "why": "Sloths, toucans and monkeys are often high in the canopy. A small pair makes the guided walks far better."},
            {"id": 2170, "why": "Safe water on long hikes and in remote spots, and less plastic."},
            {"id": 2220, "why": "Blisters, cuts and scrapes on the trail. Pack it in your daypack, not your suitcase."},
            {"search": "rechargeable headlamp lightweight", "name": "Rechargeable headlamp", "why": "Night walks are one of the best wildlife experiences in the country."}]},
        {"name": "Pack and power", "items": [
            {"id": 2116, "why": "Separates wet, dirty and clean clothes, which matters in the humidity."},
            {"id": 2450, "why": "TSA-size bottles for a carry-on only trip."},
            {"id": 2248, "why": "Long days of photos and maps drain a phone fast."},
            {"id": 2131, "why": "Keeps your passport, cards and boarding passes in one place."}]},
        {"name": "Read before you go", "items": [
            {"id": 2340, "why": "Full country guide for planning regions and routes."},
            {"id": 2362, "why": "Glen's own book on traveling well for less."}]},
     ]},
]
