WEIGHT_ALIASES = {
    "lace": "lace", "thread": "lace", "cobweb": "lace",
    "fingering": "fingering", "sock": "fingering",
    "sport": "sport",
    "dk": "dk", "double knit": "dk",
    "worsted": "worsted", "aran": "aran",
    "bulky": "bulky", "chunky": "bulky",
    "super bulky": "super bulky", "jumbo": "super bulky",
}

STITCH_KEYWORDS = {
    # Crochet stitches
    "single crochet": "single crochet (sc)", "sc": "single crochet (sc)",
    "half double crochet": "half double crochet (hdc)", "hdc": "half double crochet (hdc)",
    "double crochet": "double crochet (dc)", "dc": "double crochet (dc)",
    "treble crochet": "treble crochet (tr)", "tr": "treble crochet (tr)",
    "slip stitch": "slip stitch (sl st)", "sl st": "slip stitch (sl st)",
    "shell": "shell", "v-stitch": "v-stitch", "v stitch": "v-stitch",
    "granny": "granny", "moss stitch": "moss/linen stitch", "linen stitch": "moss/linen stitch",
    "puff": "puff stitch", "bobble": "bobble", "popcorn": "popcorn",
    "waffle": "waffle", "star stitch": "star stitch",
    "alpine": "alpine stitch", "basketweave": "basketweave",
    "cluster": "cluster stitch", "spike stitch": "spike stitch",
    "front post": "front post stitch", "back post": "back post stitch",
    "crossed dc": "crossed double crochet", "camel stitch": "camel stitch", "x-stitch": "x-stitch",

    # Knitting stitches
    "garter": "garter stitch",
    "stockinette": "stockinette stitch", "stocking stitch": "stockinette stitch",
    "reverse stockinette": "reverse stockinette",
    "1x1 rib": "1x1 rib", "2x2 rib": "2x2 rib", "ribbing": "ribbing",
    "seed stitch": "seed stitch", "moss stitch (knit)": "moss stitch", "moss stitch knit": "moss stitch",
    "broken rib": "broken rib", "double seed": "double seed",
    "fisherman's rib": "fisherman's rib", "fishermen's rib": "fisherman's rib",
    "brioche stitch": "brioche stitch",
    "cable": "cable", "cables": "cable",
    "lace": "lace", "eyelet": "eyelet lace",
    "twisted stitch": "twisted stitch",
    "slip stitch pattern": "slip stitch texture",
    "waffle stitch knit": "waffle (knit)", "basketweave knit": "basketweave (knit)",
}

TECHNIQUE_ATTRS = {
    # construction / shaping
    "in-the-round": "in the round",
    "flat": "worked flat",
    "top-down": "top-down",
    "bottom-up": "bottom-up",
    "seamed": "seamed",
    "seamless": "seamless",
    "modular": "modular",
    "join-as-you-go": "join-as-you-go",
    "raglan": "raglan",
    "contiguous": "contiguous shoulder",
    "short-rows": "short rows",
    "c2c": "c2c",
    "corner-to-corner": "c2c",

    # colorwork / texture techniques
    "colorwork": "colorwork",
    "fair-isle": "fair isle",
    "stranded": "stranded colorwork",
    "intarsia": "intarsia",
    "brioche": "brioche",
    "mosaic": "mosaic",
    "tapestry-crochet": "tapestry crochet",
    "filet": "filet crochet",
    "overlay-crochet": "overlay crochet",
    "entrelac": "entrelac",
    "duplicate-stitch": "duplicate stitch",
    "slip-stitch-colorwork": "slip-stitch colorwork",
    "twined": "twined knitting",
    "cables": "cables",
    "lace": "lace",

    # charts & directions
    "chart": "charted",
    "written-pattern": "written",
    "charted-and-written": "charted & written",

    # finishing / special
    "kitchener": "kitchener stitch",
    "three-needle-bind-off": "three-needle bind-off",
    "mattress-stitch": "mattress stitch",
    "blocking": "blocking",
    "steek": "steek",
}

TECHNIQUE_KEYWORDS = {
    # construction
    "in the round": "in the round",
    "worked flat": "worked flat",
    "top-down": "top-down", "top down": "top-down",
    "bottom-up": "bottom-up", "bottom up": "bottom-up",
    "seamless": "seamless", "seamed": "seamed",
    "modular": "modular",
    "join as you go": "join-as-you-go",
    "raglan": "raglan",
    "contiguous": "contiguous shoulder",
    "short rows": "short rows",
    "german short rows": "short rows",
    "w&amp;t": "short rows",
    "c2c": "c2c", "corner to corner": "c2c",

    # color/texture
    "colorwork": "colorwork",
    "fair isle": "fair isle",
    "stranded": "stranded colorwork",
    "intarsia": "intarsia",
    "brioche": "brioche",
    "mosaic": "mosaic",
    "tapestry crochet": "tapestry crochet",
    "filet crochet": "filet crochet",
    "overlay crochet": "overlay crochet",
    "entrelac": "entrelac",
    "duplicate stitch": "duplicate stitch",
    "slip-stitch colorwork": "slip-stitch colorwork",
    "twined": "twined knitting",
    "cable": "cables", "cables": "cables",
    "lace": "lace",

    # chart/written
    "charted": "charted",
    "written": "written",
    "charted &amp; written": "charted & written",

    # finishing / special
    "kitchener": "kitchener stitch",
    "three needle bind off": "three-needle bind-off",
    "mattress stitch": "mattress stitch",
    "blocking": "blocking",
    "steek": "steek",
}

US_HOOK_MM = {
    "B-1": 2.25, "C-2": 2.75, "D-3": 3.25, "E-4": 3.5, "F-5": 3.75,
    "G-6": 4.0,
    "7": 4.5, "H-8": 5.0, "I-9": 5.5, "J-10": 6.0, "K-10.5": 6.5,
    "L-11": 8.0, "M/N-13": 9.0, "N/P-15": 10.0, "P": 15.0, "Q": 16.0, "S": 19.0,
}

US_LETTER_BASE = {
    "B": 2.25, "C": 2.75, "D": 3.25, "E": 3.5, "F": 3.75,
    "G": 4.0, "H": 5.0, "I": 5.5, "J": 6.0, "K": 6.5, "L": 8.0, "M": 9.0, "N": 10.0,
    "P": 15.0, "Q": 16.0, "S": 19.0
}

EQUIV_MAP = {
    "single crochet": "single_crochet", "sc": "single_crochet",
    "double crochet (uk)": "single_crochet", "dc (uk)": "single_crochet",

    "half double crochet": "half_double_crochet", "hdc": "half_double_crochet",
    "htr": "half_double_crochet",

    "double crochet": "double_crochet", "dc": "double_crochet",
    "treble (uk)": "double_crochet", "tr (uk)": "double_crochet",

    "treble crochet": "treble_crochet", "tr": "treble_crochet", 
    "trc": "treble_crochet", "double treble": "treble_crochet",

    "slip stitch": "slip_stitch", "sl st": "slip_stitch",
    "slst": "slip_stitch", "ss": "slip_stitch",

    "magic ring": "magic_ring", "magic circle": "magic_ring",
    "adjustable ring": "magic_ring", "mr": "magic_ring",

    "bobble": "bobble", "bo": "bobble",
    "puff stitch": "puff", "puff": "puff", "pf": "puff",
    "popcorn stitch": "popcorn", "pc": "popcorn",
    "cluster": "cluster", "cl": "cluster",

    "v stitch": "v_stitch", "v-stitch": "v_stitch",
    "shell stitch": "shell", "shell": "shell", "sh": "shell",

    "increase": "increase", "inc": "increase",
    "2sc in same stitch": "increase",
    "decrease": "decrease", "dec": "decrease",
    "tog": "decrease", "sc2tog": "decrease",
    "dc2tog": "decrease",

    "repeat": "repeat", "rep": "repeat", "rpt": "repeat",
    "round": "round", "rnd": "round", "rd": "round",
    "row": "row", "rows": "row",

    "join": "join", "jn": "join",
    "skip": "skip", "sk": "skip",
    "space": "space", "sp": "space",

    "chain": "chain", "ch": "chain",
    "ch space": "chain_space", "ch-sp": "chain_space",

    "hook": "hook", "yarn": "yarn",
    "tension": "gauge", "gauge": "gauge",
    "fasten off": "fasten_off"
}

DOMAIN_STOP = {
    "pattern", "finished", "approx", "approximate", "cm", "copyright",
    "instructions", "materials", "notes"
}

CUSTOM_WORDS = [
    # Crochet abbreviations
    "sc", "dc", "hdc", "tr", "slst", "slip", "inc", "dec", "yo", "ch",
    "fsc", "fpdc", "bpdc", "fpdc", "bptr", "fptr", "blo", "flo",

    # Knitting abbreviations
    "k", "p", "kfb", "k2tog", "ssk", "psso", "tbl", "m1", "m1l", "m1r",
    "yo", "wyif", "wyib", "p2tog", "k3tog", "cdd", "stst", "st", "sts",
    "yo", "pm", "sm", "rm", "sl",

    # Yarn weights
    "lace", "fingering", "sport", "dk", "worsted", "aran", "bulky", "jumbo", "medium",

    # Materials
    "wool", "cotton", "acrylic", "merino", "alpaca", "mohair",
    "cashmere", "nylon", "silk", "bamboo", "linen", "hemp", "chenille",
    "tweed", "superwash",

    # Tools / notions
    "hook", "needle", "dpn", "dpns", "circulars", "marker", "markers",
    "tapestry", "gauge", "swatch", "block", "blocking", "pom", "pompom",

    # Item categories
    "beanie", "bonnet", "beret", "slouch", 
    "mittens", "shawl", "wrap", "cowl", "snood",
    "pullover", "vest",
    "tee", "tank", "poncho", "shrug",
    "afghan", "throw", "lapghan",
    "booties", "slippers", "legwarmers",
    "earwarmer", "balaclava", "cushion",
    "amigurumi", "bag", "tote",

    # Stitch terms
    "rib", "ribbing", "stockinette", "garter", "seed", "moss",
    "waistcoat", "herringbone", "granny", "bobble", "puff", "cluster",
    "shell", "vstitch", "wattle", "suzette", "linen", "purl", "knit",
    "brioche", "fairisle", "intarsia", "cable", "lace", "stitch",

    # Construction / technique words
    "topdown", "bottomup", "seamless", "raglan", "yoke",
    "fade", "marling", "colorwork", "stranded",

    # Sizes / descriptors
    "newborn", "preemie", "toddler", "adult", "onesize",

    # Yarn companies
    "malabrigo", "drops", "scheepjes", "lionbrand", "caron", "bernat",
    "paintbox", "hobbi", "hobbii", "cascade", "rowan",
    "katia", "rico", "novita", "purlsoho", "rios"

    # Other pattern vocabulary
    "skein", "ball", "hank", "yardage", "notions", "motif",
]

QUERY_SETS:list = [
        ["beanie",
        "scarf",
        "shawl",
        "mittens",
        "socks",
        "blanket",
        "cowl",
        "cardigan",
        "vest",
        "poncho",
        "headband",
        "amigurumi",
        "baby hat",
        "crochet bag",
        "knit sweater"],
        ["merino",
        "cotton yarn",
        "acrylic bulky yarn",
        "superwash wool",
        "chenille yarn",
        "velvet yarn",
        "alpaca yarn",
        "worsted weight",
        "dk cotton",
        "fingering wool",
        "super bulky",
        "lightweight cotton hat"],
        ["malabrigo rios",
        "lion brand wool ease",
        "caron simply soft",
        "paintbox dk",
        "scheepjes whirl",
        "katia bambi",
        "bernat velvet",
        "drops paris",
        "drops air",
        "purl soho line weight"],
        ["ribbed",
        "stockinette",
        "garter stitch",
        "brioche",
        "waistcoat stitch",
        "granny square",
        "bobble stitch",
        "puff stitch",
        "cable knit",
        "lace pattern",
        "ribbed brim",
        "colorwork",
        "marling",
        "fade"],
        ["newborn hat",
        "adult size beanie",
        "oversized sweater",
        "easy crochet pattern",
        "intermediate knitting project",
        "top-down raglan",
        "seamless cardigan",
        "quick beginner project",
        "lace shawl intermediate",
        "crochet in the round"],
        ["bulky yarn ribbed beanie",
        "cotton baby blanket crochet",
        "super bulky winter hat",
        "worsted weight cable beanie",
        "dk weight lace shawl",
        "merino fingering colorwork socks",
        "top down raglan sweater knit",
        "crochet velvet scrunchie",
        "half double crochet baby hat",
        "cowl with bobble stitch"],
        ["simple crochet beanie with pompom for beginner",
        "knitted socks with heel flap and gusset in sport yarn",
        "colorwork mitten pattern using worsted wool",
        "crochet amigurumi animal easy pattern",
        "cable knit sweater with raglan shaping top down",
        "warm winter scarf knit in bulky weight merino",
        "baby cardigan with buttons crochet pattern",
        "oversized drop shoulder sweater knit",
        "crochet hat pattern using velvet yarn",
        "knit shawl with fade effect using fingering yarn"],
        ["I'm looking for a quick crochet hat pattern",
        "show me a knitting pattern for a warm chunky scarf",
        "what's a good beginner crochet blanket?",
        "pattern for a cute amigurumi animal",
        "knit sweater for men using worsted yarn",
        "crochet socks pattern for beginners",
        "pattern for a cozy winter hat",
        "I need a lightweight summer shawl",
        "how to crochet a simple beanie",
        "pattern for colorwork mittens"],
        ["crohchet beany",
        "knitted shalw",
        "amigurumy bear",
        "worstd yarn hat",
        "cable knit scraf",
        "chennile scrunchie",
        "bulky yran scarf",
        "merno wool socks",
        "grany sqare",
        "crochet baby hat"]  
    ]

SET_1 = [
    {"query": "beanie", "filters": {"fiber_art": None}},
    {"query": "scarf", "filters": {"fiber_art": None}},
    {"query": "shawl", "filters": {"fiber_art": None}},
    {"query": "mittens", "filters": {"fiber_art": None}},
    {"query": "socks", "filters": {"fiber_art": None}},
    {"query": "blanket", "filters": {"fiber_art": None}},
    {"query": "cowl", "filters": {"fiber_art": None}},
    {"query": "cardigan", "filters": {"fiber_art": None}},
    {"query": "vest", "filters": {"fiber_art": None}},
    {"query": "poncho", "filters": {"fiber_art": None}},
    {"query": "headband", "filters": {"fiber_art": None}},
    {"query": "amigurumi", "filters": {"fiber_art": None}},
    {"query": "baby hat", "filters": {"fiber_art": None}},
    {"query": "crochet bag", "filters": {"fiber_art": None}},
    {"query": "knit sweater", "filters": {"fiber_art": None}},
]

SET_2 = [
    {"query": "merino", "filters": {"materials_any": ["merino"]}},
    {"query": "cotton yarn", "filters": {"materials_any": ["cotton"]}},
    {"query": "acrylic bulky yarn", "filters": {"materials_any": ["acrylic"], "yarn_weight": "bulky"}},
    {"query": "superwash wool", "filters": {"materials_any": ["wool"]}},
    {"query": "chenille yarn", "filters": {"materials_any": ["chenille"]}},
    {"query": "velvet yarn", "filters": {"materials_any": ["velvet"]}},
    {"query": "alpaca yarn", "filters": {"materials_any": ["alpaca"]}},
    {"query": "worsted weight", "filters": {"yarn_weight": "worsted"}},
    {"query": "dk cotton", "filters": {"yarn_weight": "dk", "materials_any": ["cotton"]}},
    {"query": "fingering wool", "filters": {"yarn_weight": "fingering", "materials_any": ["wool"]}},
    {"query": "super bulky", "filters": {"yarn_weight": "super bulky"}},
    {"query": "lightweight cotton hat", "filters": {"materials_any": ["cotton"], "yarn_weight": "lace"}},
]

SET_3 = [
    {"query": "malabrigo rios",        "filters": {"materials_any": ["merino"], "yarn_weight": "worsted"}},
    {"query": "lion brand wool ease",  "filters": {"materials_any": ["wool", "acrylic"]}},
    {"query": "caron simply soft",     "filters": {"materials_any": ["acrylic"]}},
    {"query": "paintbox dk",           "filters": {"yarn_weight": "dk"}},
    {"query": "scheepjes whirl",       "filters": {"yarn_weight": "fingering"}},
    {"query": "katia bambi",           "filters": {"materials_any": ["chenille"]}},
    {"query": "bernat velvet",         "filters": {"materials_any": ["velvet"]}},
    {"query": "drops paris",           "filters": {"materials_any": ["cotton"]}},
    {"query": "drops air",             "filters": {"materials_any": ["alpaca", "wool"]}},
    {"query": "purl soho line weight", "filters": {"yarn_weight": "lace"}},
]

SET_4 = [
    {"query": "ribbed",            "filters": {"stitches_any": ["rib"], "fiber_art": None}},
    {"query": "stockinette",       "filters": {"stitches_any": ["stockinette"], "fiber_art": "knitting"}},
    {"query": "garter stitch",     "filters": {"stitches_any": ["garter"], "fiber_art": "knitting"}},
    {"query": "brioche",           "filters": {"techniques_any": ["brioche"], "fiber_art": "knitting"}},
    {"query": "waistcoat stitch",  "filters": {"stitches_any": ["waistcoat"], "fiber_art": "crochet"}},
    {"query": "granny square",     "filters": {"techniques_any": ["granny square"], "fiber_art": "crochet"}},
    {"query": "bobble stitch",     "filters": {"stitches_any": ["bobble"]}},
    {"query": "puff stitch",       "filters": {"stitches_any": ["puff"]}},
    {"query": "cable knit",        "filters": {"techniques_any": ["cables"], "fiber_art": "knitting"}},
    {"query": "lace pattern",      "filters": {"techniques_any": ["lace"]}},
    {"query": "ribbed brim",       "filters": {"stitches_any": ["rib"]}},
    {"query": "colorwork",         "filters": {"techniques_any": ["colorwork"]}},
    {"query": "marling",           "filters": {"techniques_any": ["marling"]}},
    {"query": "fade",              "filters": {"techniques_any": ["fade"]}},
]

SET_5 = [
    {"query": "newborn hat",               "filters": {"fiber_art": None}},
    {"query": "adult size beanie",         "filters": {"fiber_art": None}},
    {"query": "oversized sweater",         "filters": {"fiber_art": None}},
    {"query": "easy crochet pattern",      "filters": {"fiber_art": "crochet"}},
    {"query": "intermediate knitting project", "filters": {"fiber_art": "knitting"}},
    {"query": "top-down raglan",           "filters": {"techniques_any": ["raglan", "top-down"], "fiber_art": "knitting"}},
    {"query": "seamless cardigan",         "filters": {"techniques_any": ["seamless"], "fiber_art": None}},
    {"query": "quick beginner project",    "filters": {}},
    {"query": "lace shawl intermediate",   "filters": {"techniques_any": ["lace"]}},
    {"query": "crochet in the round",      "filters": {"techniques_any": ["in the round"], "fiber_art": "crochet"}},
]

SET_6 = [
    {"query": "bulky yarn ribbed beanie",
     "filters": {"yarn_weight": "bulky", "stitches_any": ["rib"]}},
    {"query": "cotton baby blanket crochet",
     "filters": {"fiber_art": "crochet", "materials_any": ["cotton"]}},
    {"query": "super bulky winter hat",
     "filters": {"yarn_weight": "super bulky"}},
    {"query": "worsted weight cable beanie",
     "filters": {"yarn_weight": "worsted", "techniques_any": ["cables"]}},
    {"query": "dk weight lace shawl",
     "filters": {"yarn_weight": "dk", "techniques_any": ["lace"]}},
    {"query": "merino fingering colorwork socks",
     "filters": {"materials_any": ["merino"], "yarn_weight": "fingering", "techniques_any": ["colorwork"]}},
    {"query": "top down raglan sweater knit",
     "filters": {"fiber_art": "knitting", "techniques_any": ["raglan", "top-down"]}},
    {"query": "crochet velvet scrunchie",
     "filters": {"fiber_art": "crochet", "materials_any": ["velvet"]}},
    {"query": "half double crochet baby hat",
     "filters": {"fiber_art": "crochet", "stitches_any": ["half double crohet (hdc)"]}},
    {"query": "cowl with bobble stitch",
     "filters": {"stitches_any": ["bobble"]}},
]

SET_7 = [
    {"query": "simple crochet beanie with pompom for beginner",
     "filters": {"fiber_art": "crochet"}},
    {"query": "knitted socks with heel flap and gusset in sport yarn",
     "filters": {"fiber_art": "knitting", "yarn_weight": "sport"}},
    {"query": "colorwork mitten pattern using worsted wool",
     "filters": {"fiber_art": "knitting", "techniques_any": ["colorwork"], "yarn_weight": "worsted"}},
    {"query": "crochet amigurumi animal easy pattern",
     "filters": {"fiber_art": "crochet"}},
    {"query": "cable knit sweater with raglan shaping top down",
     "filters": {"fiber_art": "knitting", "techniques_any": ["cables", "raglan", "top-down"]}},
    {"query": "warm winter scarf knit in bulky weight merino",
     "filters": {"fiber_art": "knitting", "yarn_weight": "bulky", "materials_any": ["merino"]}},
    {"query": "baby cardigan with buttons crochet pattern",
     "filters": {"fiber_art": "crochet"}},
    {"query": "oversized drop shoulder sweater knit",
     "filters": {"fiber_art": "knitting"}},
    {"query": "crochet hat pattern using velvet yarn",
     "filters": {"fiber_art": "crochet", "materials_any": ["velvet"]}},
    {"query": "knit shawl with fade effect using fingering yarn",
     "filters": {"fiber_art": "knitting", "yarn_weight": "fingering", "techniques_any": ["fade"]}},
]

SET_8 = [
    {"query": "I'm looking for a quick crochet hat pattern",
     "filters": {"fiber_art": "crochet"}},
    {"query": "show me a knitting pattern for a warm chunky scarf",
     "filters": {"fiber_art": "knitting", "yarn_weight": "bulky"}},
    {"query": "what's a good beginner crochet blanket?",
     "filters": {"fiber_art": "crochet"}},
    {"query": "pattern for a cute amigurumi animal",
     "filters": {"fiber_art": "crochet"}},
    {"query": "knit sweater for men using worsted yarn",
     "filters": {"fiber_art": "knitting", "yarn_weight": "worsted"}},
    {"query": "crochet socks pattern for beginners",
     "filters": {"fiber_art": "crochet"}},
    {"query": "pattern for a cozy winter hat",
     "filters": {}},
    {"query": "I need a lightweight summer shawl",
     "filters": {"yarn_weight": "lace"}},
    {"query": "how to crochet a simple beanie",
     "filters": {"fiber_art": "crochet"}},
    {"query": "pattern for colorwork mittens",
     "filters": {"techniques_any": ["colorwork"]}},
]

SET_9 = [
    {"query": "crohchet beany",          "filters": {"fiber_art": "crochet"}},
    {"query": "knitted shalw",           "filters": {"fiber_art": "knitting"}},
    {"query": "amigurumy bear",          "filters": {"fiber_art": "crochet"}},
    {"query": "worstd yarn hat",         "filters": {"yarn_weight": "worsted"}},
    {"query": "cable knit scraf",        "filters": {"fiber_art": "knitting", "techniques_any": ["cables"]}},
    {"query": "chennile scrunchie",      "filters": {"materials_any": ["chenille"]}},
    {"query": "bulky yran scarf",        "filters": {"yarn_weight": "bulky"}},
    {"query": "merno wool socks",        "filters": {"materials_any": ["merino"], "fiber_art": "knitting"}},
    {"query": "grany sqare",             "filters": {"fiber_art": "crochet", "techniques_any": ["granny square"]}},
    {"query": "crochet baby hat",        "filters": {"fiber_art": "crochet"}},
]

QUERY_SETS_WITH_FILTERS = [SET_1, SET_2, SET_3, SET_4, SET_5, SET_6, SET_7, SET_8, SET_9]