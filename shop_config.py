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
    {"key": "guides", "name": "Guidebooks", "cat": "guides",
     "blurb": "Destination guides worth packing, plus the books Glen wrote himself.",
     "guide": ("/guide/", "Browse every Travel With Glen guide"),
     "verified": ("/destinations", "Vetted businesses by destination")},
    {"key": "packing", "name": "Packing and Organization", "cat": "accessories",
     "blurb": "Cubes, pouches, pillows and organizers that keep a carry-on under control.",
     "guide": ("/budget-travel-guides/", "Budget travel guides"),
     "verified": ("/collections/glen-recommended", "Places Glen recommends")},
    {"key": "tech", "name": "Tech and Power", "cat": "technology",
     "blurb": "Chargers, plug adapters and a travel router for staying connected abroad.",
     "guide": ("/budget-travel-guides/", "Budget travel guides"),
     "verified": ("/collections/digital-nomad-friendly", "Digital-nomad-friendly spots")},
    {"key": "outdoor", "name": "Outdoor and Adventure", "cat": "outdoor-equipment",
     "blurb": "Dry bags, water filters, first aid and daypacks for hikes and river days.",
     "guide": ("/adventure-travel-guide/", "Adventure travel guide"),
     "verified": ("/collections/hidden-gems", "Hidden gems in the Verified Network")},
    {"key": "care", "name": "Personal Care To Go", "cat": "personal-care-kits",
     "blurb": "TSA-size toiletries, travel shavers, folding brushes and deodorant wipes.",
     "guide": ("/budget-travel-guides/", "Budget travel guides"),
     "verified": ("/collections/glen-verified", "Glen-verified businesses")},
    {"key": "apparel", "name": "Travel Apparel", "cat": "apparel",
     "blurb": "Comfortable layers, jeans and shirts that pack well.",
     "guide": ("/best-time-to-visit-costa-rica-2026/", "When to go (and what to pack) for Costa Rica"),
     "verified": ("/collections/glen-recommended", "Places Glen recommends")},
    {"key": "merch", "name": "Travel With Glen Merch", "cat": "travel-with-glen",
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
DUPLICATES = {2081: 2055}  # BAGAIL cubes, the "variable" copy was misconfigured

# Fixes for links in the WordPress data.
ASIN_OVERRIDES = {
    1839: "B0CBJKLGDB",  # amzn.to/3NSz3Nf resolved Oct 20
    1785: "B07SLGHB24",  # amzn.to/3UFuzNL resolved Oct 20
    1699: "B09N72FMH5",  # amzn.to/3AFb2Ga resolved Oct 20 (GL.iNet Opal travel router)
}
# Products with no Amazon link at all (were set up as "sellable"): link to a tagged Amazon search until an ASIN is added above.
SEARCH_FALLBACK = {1812: "siliteelon women's stain shield dress shirt wrinkle free"}

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
