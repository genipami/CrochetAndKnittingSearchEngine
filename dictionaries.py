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