"""
RTU Study Programme AI Recommender
utils.py — Universal taxonomy, tag mapping constants, and helper utilities.

This module defines the canonical vocabulary that the UI and scoring engine share.
All programme tags (from 4 different source formats) are mapped to this taxonomy.
"""

from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL INTEREST DOMAINS
# ─────────────────────────────────────────────────────────────────────────────
INTEREST_DOMAINS: dict[str, dict] = {
    "it_programming": {
        "label": "💻 IT & Programmēšana",
        "label_en": "IT & Programming",
        "description": "Datorzinātne, programmēšana, kiberdrošība, tīkli",
    },
    "electronics_telecom": {
        "label": "📡 Elektronika & Telekomunikācijas",
        "label_en": "Electronics & Telecommunications",
        "description": "Elektroniskās sistēmas, telekomunikācijas, sakari",
    },
    "mechanics_engineering": {
        "label": "⚙️ Mehānika & Mašīnbūve",
        "label_en": "Mechanics & Mechanical Engineering",
        "description": "Mašīnbūve, mehānika, ražošanas tehnoloģijas",
    },
    "transport_aviation": {
        "label": "✈️ Transports & Aviācija",
        "label_en": "Transport & Aviation",
        "description": "Aviācija, autotransports, loģistika, transporta sistēmas",
    },
    "construction_civil": {
        "label": "🏗️ Būvniecība & Inženierija",
        "label_en": "Construction & Civil Engineering",
        "description": "Būvniecība, infrastruktūra, civīlā inženierija",
    },
    "chemistry_biotech": {
        "label": "🧪 Ķīmija & Biotehnoloģija",
        "label_en": "Chemistry & Biotechnology",
        "description": "Ķīmija, biotehnoloģija, materiālu zinātne",
    },
    "environment_sustainability": {
        "label": "🌿 Vide & Ilgtspēja",
        "label_en": "Environment & Sustainability",
        "description": "Vides zinātne, ilgtspēja, klimata pārmaiņas",
    },
    "robotics_automation": {
        "label": "🤖 Robotika & Automatizācija",
        "label_en": "Robotics & Automation",
        "description": "Robotika, automatizācija, mechatronika, vadības sistēmas",
    },
    "art_design": {
        "label": "🎨 Māksla & Dizains",
        "label_en": "Art & Design",
        "description": "Industrijālais dizains, grafiskais dizains, vizuālā māksla",
    },
    "architecture": {
        "label": "🏛️ Arhitektūra",
        "label_en": "Architecture",
        "description": "Arhitektūra, pilsētplānošana, interjers",
    },
    "business_management": {
        "label": "📊 Bizness & Vadība",
        "label_en": "Business & Management",
        "description": "Uzņēmējdarbība, vadība, ekonomika, finanses, loģistika",
    },
    "data_science_ai": {
        "label": "🧠 Datu Zinātne & AI",
        "label_en": "Data Science & Artificial Intelligence",
        "description": "Mākslīgais intelekts, datu analīze, mašīnmācīšanās",
    },
    "energy_power": {
        "label": "⚡ Enerģētika & Elektrotehnika",
        "label_en": "Energy & Electrical Engineering",
        "description": "Elektroenerģētika, viedie tīkli, atjaunojamā enerģija",
    },
    "maritime": {
        "label": "⚓ Jūrniecība & Ūdenstransports",
        "label_en": "Maritime & Water Transport",
        "description": "Jūras transports, navigācija, kuģniecība",
    },
    "education_research": {
        "label": "🔬 Izglītība & Zinātne",
        "label_en": "Education & Research",
        "description": "Pedagoģija, zinātne, pētniecība, akadēmiskā karjera",
    },
    "medical_technology": {
        "label": "🏥 Medicīnas Tehnoloģija",
        "label_en": "Medical Technology",
        "description": "Medicīnas fizika, biomedicīna, veselības tehnoloģijas",
    },
    "software_engineering": {
        "label": "🖥️ Programmatūras Inženierija",
        "label_en": "Software Engineering",
        "description": "Programmatūras izstrāde, sistēmu arhitektūra, DevOps",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL STRENGTH TAGS
# ─────────────────────────────────────────────────────────────────────────────
STRENGTH_TAGS: dict[str, dict] = {
    "mathematics": {"label": "📐 Matemātika", "label_en": "Mathematics"},
    "physics": {"label": "⚛️ Fizika", "label_en": "Physics"},
    "chemistry": {"label": "🧪 Ķīmija", "label_en": "Chemistry"},
    "biology": {"label": "🌱 Bioloģija", "label_en": "Biology"},
    "programming": {"label": "💻 Programmēšana", "label_en": "Programming / Coding"},
    "creativity": {"label": "💡 Radošums", "label_en": "Creativity"},
    "drawing_design": {"label": "✏️ Zīmēšana & Vizuālā Māksla", "label_en": "Drawing & Visual Art"},
    "languages": {"label": "🌍 Svešvalodas", "label_en": "Foreign Languages"},
    "analytical_thinking": {"label": "🔍 Analītiskā Domāšana", "label_en": "Analytical Thinking"},
    "technical_thinking": {"label": "🔧 Tehniskā Domāšana", "label_en": "Technical / Engineering Thinking"},
    "communication": {"label": "🗣️ Komunikācija", "label_en": "Communication & Presentation"},
    "leadership": {"label": "👥 Vadīšana & Organizācija", "label_en": "Leadership & Organization"},
    "research": {"label": "🔬 Pētniecība & Analīze", "label_en": "Research & Analysis"},
    "practical_skills": {"label": "🛠️ Praktiskās Iemaņas", "label_en": "Practical / Hands-on Skills"},
    "economics_finance": {"label": "💰 Ekonomika & Finanses", "label_en": "Economics & Finance"},
    "social_sciences": {"label": "🤝 Sociālās Zinātnes", "label_en": "Social Sciences"},
}

# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL PERSONALITY TRAITS
# ─────────────────────────────────────────────────────────────────────────────
PERSONALITY_TRAITS: dict[str, dict] = {
    "analytical": {
        "label": "🧩 Analītisks",
        "description": "Patīk loģiska problēmu risināšana un sistēmiska domāšana",
    },
    "creative": {
        "label": "🎨 Radošs",
        "description": "Patīk jaunas idejas, radīšana un inovatīvs domāšanas veids",
    },
    "practical": {
        "label": "🔧 Praktiski orientēts",
        "description": "Patīk konkrēti, taustāmi rezultāti un roku darbs",
    },
    "scientific": {
        "label": "🔬 Zinātniski orientēts",
        "description": "Patīk teorija, eksperimenti un dziļa izpratne par tēmu",
    },
    "social": {
        "label": "👥 Sociāli orientēts",
        "description": "Patīk strādāt ar cilvēkiem, palīdzēt un komunicēt",
    },
    "technical": {
        "label": "⚙️ Tehniski orientēts",
        "description": "Patīk tehnoloģijas, sistēmas un inženiertehniskā domāšana",
    },
    "entrepreneurial": {
        "label": "🚀 Uzņēmīgs",
        "description": "Patīk uzņēmējdarbība, iniciatīva un jaunu projektu vadīšana",
    },
    "independent": {
        "label": "🦅 Patstāvīgs",
        "description": "Patīk strādāt neatkarīgi un pašam pieņemt lēmumus",
    },
    "team_player": {
        "label": "🤝 Komandas spēlētājs",
        "description": "Patīk grupu darbs, sadarbība un kopēju mērķu sasniegšana",
    },
    "precise": {
        "label": "🎯 Precīzs",
        "description": "Uzmanīgs pret detaļām, pedantisks un rūpīgs",
    },
    "international": {
        "label": "🌍 Starptautiski orientēts",
        "description": "Interesē globālā skatuve, darbs ārzemēs un starptautiska vide",
    },
    "adventurous": {
        "label": "⚡ Aktīvs & Darbmīlīgs",
        "description": "Gatavs darbam jebkuros apstākļos, mīl izaicinājumus",
    },
    "sustainability_conscious": {
        "label": "🌱 Ekoloģiski apzinīgs",
        "description": "Rūpējas par vidi, ilgtspēju un nākotnes paaudzēm",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL INDUSTRY SECTORS
# ─────────────────────────────────────────────────────────────────────────────
INDUSTRY_SECTORS: dict[str, dict] = {
    "IT": {"label": "💻 IT & Tehnoloģijas", "label_en": "IT & Technology"},
    "engineering_manufacturing": {"label": "🏭 Rūpniecība & Ražošana", "label_en": "Manufacturing & Industry"},
    "construction": {"label": "🏗️ Būvniecība", "label_en": "Construction"},
    "transport_logistics": {"label": "🚛 Transports & Loģistika", "label_en": "Transport & Logistics"},
    "energy": {"label": "⚡ Enerģētika", "label_en": "Energy"},
    "environment": {"label": "🌿 Vide & Klimats", "label_en": "Environment & Climate"},
    "chemistry_pharma": {"label": "💊 Ķīmija & Farmācija", "label_en": "Chemistry & Pharma"},
    "biomedicine": {"label": "🏥 Biomedicīna & Veselība", "label_en": "Biomedicine & Health"},
    "telecom": {"label": "📡 Telekomunikācijas & Mediji", "label_en": "Telecom & Media"},
    "robotics_automation": {"label": "🤖 Robotika & Automatizācija", "label_en": "Robotics & Automation"},
    "art_culture": {"label": "🎭 Māksla & Kultūra", "label_en": "Arts & Culture"},
    "business_finance": {"label": "💼 Bizness & Finanses", "label_en": "Business & Finance"},
    "education_research": {"label": "🎓 Izglītība & Pētniecība", "label_en": "Education & Research"},
    "design_media": {"label": "🖥️ Dizains & Mediji", "label_en": "Design & Media"},
    "maritime_sector": {"label": "⚓ Jūrniecība", "label_en": "Maritime"},
    "law_public_admin": {"label": "⚖️ Tiesības & Valsts pārvalde", "label_en": "Law & Public Administration"},
}

# ─────────────────────────────────────────────────────────────────────────────
# TAG-TO-CANONICAL MAPPING DICTIONARIES
# Maps raw tags from all 4 JSON formats → canonical keys above
# ─────────────────────────────────────────────────────────────────────────────

DOMAIN_MAP: dict[str, str] = {
    # ── rtu_programs.json (academic) ──────────────────────────────────────
    "it_un_programmeeshana": "it_programming",
    "elektronika_un_telekomunikacijas": "electronics_telecom",
    "mehaanika_un_maashiinbuuve": "mechanics_engineering",
    "butransports_un_aviacija": "transport_aviation",
    "buuvenieciba": "construction_civil",
    "kiiimija_un_biotehnoloGija": "chemistry_biotech",
    "kiiimija_un_biotehnoloģija": "chemistry_biotech",
    "materiaalu_zinatne": "chemistry_biotech",
    "vides_zinatne_un_ilgtspeejiba": "environment_sustainability",
    "robotika_un_automatizacija": "robotics_automation",
    "maaksla_un_dizains": "art_design",
    "arhitektura": "architecture",
    "bizness_un_vadiba": "business_management",
    "tiesibas": "law_public_admin",
    "valodas_un_kulturas": "education_research",
    "radosa_industrija": "art_design",
    "datu_zinatne_un_mi": "data_science_ai",
    # ── rtu_bmf_programs.json (BMF professional) ─────────────────────────
    "inzenierija": "mechanics_engineering",
    "elektronika_it": "electronics_telecom",
    "celtnieciba": "construction_civil",
    "dizains": "art_design",
    "transports": "transport_aviation",
    "energetika": "energy_power",
    "medicinas_tehnologija": "medical_technology",
    "jurnieciiba": "maritime",
    # ── rtu_programs_DITEF_IVF_prof.json (English slugs) ─────────────────
    "power_engineering": "energy_power",
    "smart_grids": "energy_power",
    "energy_systems": "energy_power",
    "electrical_engineering": "energy_power",
    "renewable_energy": "environment_sustainability",
    "automation": "robotics_automation",
    "sustainability": "environment_sustainability",
    "control_systems": "robotics_automation",
    "smart_electronic_systems": "electronics_telecom",
    "electronic_engineering": "electronics_telecom",
    "it_security": "it_programming",
    "cybersecurity": "it_programming",
    "software_engineering": "software_engineering",
    "computer_science": "it_programming",
    "information_technology": "it_programming",
    "networking": "it_programming",
    "cloud_computing": "it_programming",
    "data_analytics": "data_science_ai",
    "machine_learning": "data_science_ai",
    "artificial_intelligence": "data_science_ai",
    "telematics": "electronics_telecom",
    "telecommunications": "electronics_telecom",
    "embedded_systems": "electronics_telecom",
    "transport_electronics": "transport_aviation",
    "transport_telecommunications": "transport_aviation",
    "transport_electronic_systems": "transport_aviation",
    "transport": "transport_aviation",
    "aviation": "transport_aviation",
    "automotive": "transport_aviation",
    "engineering": "mechanics_engineering",
    "industrial_design": "art_design",
    "product_design": "art_design",
    "architecture_design": "architecture",
    "urban_planning": "architecture",
    "civil_engineering": "construction_civil",
    "structural_engineering": "construction_civil",
    "building_engineering": "construction_civil",
    "environmental_engineering": "environment_sustainability",
    "heat_engineering": "energy_power",
    "hvac": "energy_power",
    "mechatronics": "robotics_automation",
    "robotics": "robotics_automation",
    "biomedical_engineering": "medical_technology",
    "medical_physics": "medical_technology",
    "chemistry": "chemistry_biotech",
    "materials_science": "chemistry_biotech",
    "polymer_chemistry": "chemistry_biotech",
    "business_administration": "business_management",
    "entrepreneurship": "business_management",
    "economics": "business_management",
    "logistics": "business_management",
    "maritime_transport": "maritime",
    "ship_engineering": "maritime",
    "navigation": "maritime",
    # ── rezekne / liepaja (free-text Latvian tags) ────────────────────────
    "programmeesana": "it_programming",
    "programmesana": "it_programming",
    "programmēšana": "it_programming",
    "datorzin": "it_programming",
    "datorzinātne": "it_programming",
    "informācijas tehnoloģijas": "it_programming",
    "it": "it_programming",
    "kiberdrošība": "it_programming",
    "ekonomika": "business_management",
    "finanses": "business_management",
    "bizness": "business_management",
    "grāmatvedība": "business_management",
    "projektu vadība": "business_management",
    "uzņēmējdarbība": "business_management",
    "mārketings": "business_management",
    "vadība": "business_management",
    "loģistika": "business_management",
    "nekustamais īpašums": "business_management",
    "vide": "environment_sustainability",
    "ekoloģija": "environment_sustainability",
    "skolotājs": "education_research",
    "pedagoģija": "education_research",
    "izglītība": "education_research",
    "sociālais darbs": "education_research",
    "psiholoģija": "education_research",
    "dizains_mediji": "art_design",
    "māksla": "art_design",
    "dizains": "art_design",
    "arhitektūra": "architecture",
}

STRENGTH_MAP: dict[str, str] = {
    # Latvian (rtu_programs.json)
    "matemātika": "mathematics",
    "matematika": "mathematics",
    "fizika": "physics",
    "ķīmija": "chemistry",
    "kimija": "chemistry",
    "bioloģija": "biology",
    "biologija": "biology",
    "programmēšana": "programming",
    "programmesana": "programming",
    "radošums": "creativity",
    "radosums": "creativity",
    "zīmēšana": "drawing_design",
    "zimesana": "drawing_design",
    "valodas": "languages",
    "analītiskā domāšana": "analytical_thinking",
    "analitiska domašana": "analytical_thinking",
    "tehniskā domāšana": "technical_thinking",
    "komunik": "communication",
    "vadīšana": "leadership",
    "vadisana": "leadership",
    "pētniecība": "research",
    "petnieciba": "research",
    "dizains": "drawing_design",
    # BMF slugs
    "matematika": "mathematics",
    "fizika": "physics",
    "programmesana": "programming",
    "rada": "creativity",
    "zimesana": "drawing_design",
    "lieriskas_prasmes": "practical_skills",
    "analitika": "analytical_thinking",
    "organizesana": "leadership",
    # English (DITEF)
    "mathematics": "mathematics",
    "physics": "physics",
    "programming": "programming",
    "problem_solving": "analytical_thinking",
    "systems_thinking": "analytical_thinking",
    "engineering": "technical_thinking",
    "collaborative": "communication",
    "creativity": "creativity",
    "design": "drawing_design",
    "sustainability": "research",
    "research": "research",
    "analytical": "analytical_thinking",
    "technical": "technical_thinking",
    "practical": "practical_skills",
    "communication": "communication",
    "leadership": "leadership",
    "drawing": "drawing_design",
    "languages": "languages",
    # Rezekne free text
    "analīze": "analytical_thinking",
    "organizācija": "leadership",
    "komunikācija": "communication",
    "rokdarbs": "practical_skills",
    "ekonomika": "economics_finance",
    "finanses": "economics_finance",
    "sociālā darba iemaņas": "social_sciences",
}

PERSONALITY_MAP: dict[str, str] = {
    # rtu_programs.json
    "analitisks": "analytical",
    "analītisks": "analytical",
    "radošs": "creative",
    "rados": "creative",
    "praktiski orientēts": "practical",
    "praktiski_orientets": "practical",
    "zinātniski orientēts": "scientific",
    "zinatniski_orientets": "scientific",
    "sociāli orientēts": "social",
    "sociali_orientets": "social",
    "tehniski orientēts": "technical",
    "tehniski_orientets": "technical",
    "uzņēmīgs": "entrepreneurial",
    "uznemigs": "entrepreneurial",
    "humanitāri orientēts": "entrepreneurial",
    "humanitari_orientets": "entrepreneurial",
    "starptautiski orientēts": "international",
    "starptautiski_orientets": "international",
    "komandas spēlētājs": "team_player",
    "komandas_speletajs": "team_player",
    "patstāvīgs": "independent",
    "patstāvigs": "independent",
    # BMF keys
    "analytisks": "analytical",
    "radoss": "creative",
    "praktisks": "practical",
    "leadership": "entrepreneurial",
    "pedants": "precise",
    "avanturists": "adventurous",
    "avant": "adventurous",
    # English (DITEF)
    "technical": "technical",
    "analytical": "analytical",
    "collaborative": "team_player",
    "sustainability_conscious": "sustainability_conscious",
    "creative": "creative",
    "innovative": "creative",
    "practical": "practical",
    "independent": "independent",
    "precise": "precise",
    "international": "international",
    # Rezekne free text
    "analītisks": "analytical",
    "organizēts": "precise",
    "precīzs": "precise",
    "sistēmātisks": "analytical",
    "komunikabls": "social",
    "atbildīgs": "precise",
}

SECTOR_MAP: dict[str, str] = {
    # rtu_programs.json sectors
    "it": "IT",
    "aviācija_un_transports": "transport_logistics",
    "aviacija_un_transports": "transport_logistics",
    "ražošana_un_rūpniecība": "engineering_manufacturing",
    "razosana_un_rupnieciba": "engineering_manufacturing",
    "būvniecība": "construction",
    "buvnieciba": "construction",
    "enerģētika": "energy",
    "energetika": "energy",
    "vide_un_klimats": "environment",
    "ķīmija_un_farmācija": "chemistry_pharma",
    "kimija_un_farmacija": "chemistry_pharma",
    "biomedicīna": "biomedicine",
    "biomedicina": "biomedicine",
    "sakari_un_telekomunikācijas": "telecom",
    "sakari_un_telekomunikacijas": "telecom",
    "robotika_un_automatizācija": "robotics_automation",
    "robotika_un_automatizacija": "robotics_automation",
    "māksla_un_kultūra": "art_culture",
    "maaksla_un_kultura": "art_culture",
    "bizness_un_finanses": "business_finance",
    "tieslietas": "law_public_admin",
    "izglītība_un_pētniecība": "education_research",
    "izglitiba_un_petnieciba": "education_research",
    "dizains_un_mediji": "design_media",
    # BMF / DITEF / Rezekne free text
    "transports un loģistika": "transport_logistics",
    "rūpnieciskā ražošana": "engineering_manufacturing",
    "izglītība un zinātne": "education_research",
    "autosports": "transport_logistics",
    "avi": "transport_logistics",
    "starptautiskie uzņēmumi": "transport_logistics",
    "komercdarb": "business_finance",
    "finanšu anal": "business_finance",
    "grāmatved": "business_finance",
    "valsts pārvalde": "law_public_admin",
    "pašvaldība": "law_public_admin",
    "sociālais": "education_research",
    "pedagoģija": "education_research",
    "vide": "environment",
    "enerģija": "energy",
    "jūrniecība": "maritime_sector",
    "kuģniecība": "maritime_sector",
    "arhitektūra": "construction",
    "dizains": "design_media",
    # English (DITEF) sectors
    "manufacturing": "engineering_manufacturing",
    "construction": "construction",
    "transport": "transport_logistics",
    "logistics": "transport_logistics",
    "energy": "energy",
    "environment": "environment",
    "telecom": "telecom",
    "robotics": "robotics_automation",
    "automation": "robotics_automation",
    "biomedical": "biomedicine",
    "design": "design_media",
    "media": "design_media",
    "education": "education_research",
    "research": "education_research",
    "law": "law_public_admin",
    "public administration": "law_public_admin",
}

# ─────────────────────────────────────────────────────────────────────────────
# TAG NORMALISATION HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _map_tag(tag: str, mapping: dict[str, str]) -> Optional[str]:
    """
    Try to map a raw tag string to a canonical key.
    First tries exact match (case-insensitive), then substring match.
    """
    if not tag:
        return None
    tag_lower = tag.lower().strip()
    # Exact match
    if tag_lower in mapping:
        return mapping[tag_lower]
    # Try original case
    if tag in mapping:
        return mapping[tag]
    # Substring match: return the canonical key for the first keyword found
    for raw_key, canonical in mapping.items():
        if raw_key.lower() in tag_lower or tag_lower in raw_key.lower():
            return canonical
    return None


def map_to_canonical_domain(tag: str) -> Optional[str]:
    """Map any raw interest-domain tag to canonical domain key."""
    result = _map_tag(tag, DOMAIN_MAP)
    if result:
        return result
    # Fallback: check if it's already a canonical key
    if tag in INTEREST_DOMAINS:
        return tag
    return None


def map_to_canonical_strength(tag: str) -> Optional[str]:
    """Map any raw strength/subject tag to canonical key."""
    result = _map_tag(tag, STRENGTH_MAP)
    if result:
        return result
    if tag in STRENGTH_TAGS:
        return tag
    return None


def map_to_canonical_personality(tag: str) -> Optional[str]:
    """Map any raw personality tag to canonical key."""
    result = _map_tag(tag, PERSONALITY_MAP)
    if result:
        return result
    if tag in PERSONALITY_TRAITS:
        return tag
    return None


def map_to_canonical_sector(tag: str) -> Optional[str]:
    """Map any raw career-sector tag to canonical key."""
    result = _map_tag(tag, SECTOR_MAP)
    if result:
        return result
    if tag in INDUSTRY_SECTORS:
        return tag
    return None


def map_tags(tags: list, map_fn) -> list[str]:
    """Map a list of raw tags using the given mapping function, filtering None."""
    result = []
    for tag in (tags or []):
        mapped = map_fn(str(tag))
        if mapped and mapped not in result:
            result.append(mapped)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE NORMALISATION
# ─────────────────────────────────────────────────────────────────────────────

def normalize_language_code(lang: str) -> str:
    """Normalize various language representations to short codes."""
    if not lang:
        return "lv"
    lang_l = lang.lower().strip()
    if lang_l in ("lv", "latviesu", "latvian", "latviešu", "latvia"):
        return "lv"
    if lang_l in ("en", "anglu", "english", "eng", "anglų", "angļu"):
        return "en"
    if lang_l in ("ru", "krievu", "russian", "rus", "krievų"):
        return "ru"
    return lang_l


def normalize_languages(langs_raw) -> list[str]:
    """Normalize a list/string of languages to short codes."""
    if not langs_raw:
        return ["lv"]
    if isinstance(langs_raw, str):
        langs_raw = [langs_raw]
    codes = list({normalize_language_code(l) for l in langs_raw})
    return sorted(codes)


LANG_LABELS = {"lv": "🇱🇻 Latviešu", "en": "🇬🇧 Angļu", "ru": "🇷🇺 Krievu"}


# ─────────────────────────────────────────────────────────────────────────────
# DIFFICULTY NORMALISATION
# ─────────────────────────────────────────────────────────────────────────────

DIFFICULTY_LEVELS = {
    "low": "⭐ Zema",
    "medium": "⭐⭐ Vidēja",
    "medium_high": "⭐⭐⭐ Vidēji augsta",
    "high": "⭐⭐⭐⭐ Augsta",
}


def normalize_difficulty(raw: str) -> str:
    """Normalize various difficulty strings to canonical level."""
    if not raw:
        return "medium"
    r = str(raw).lower().strip()
    if any(k in r for k in ("zem", "low")):
        return "low"
    if any(k in r for k in ("augst_vid", "vid_augst", "videj_augst", "videja-augsta",
                             "medium_high", "medium-high", "high-medium")):
        return "medium_high"
    if any(k in r for k in ("augst", "high")):
        return "high"
    if any(k in r for k in ("vid", "medium")):
        return "medium"
    # Numeric intensity mapping (DITEF uses 1-5 scale)
    try:
        n = float(r)
        if n >= 4.5:
            return "high"
        if n >= 3:
            return "medium_high"
        if n >= 2:
            return "medium"
        return "low"
    except ValueError:
        pass
    return "medium"


# ─────────────────────────────────────────────────────────────────────────────
# MISC HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def safe_get(d: dict, *keys, default=None):
    """Safely traverse nested dicts: safe_get(d, 'a', 'b', 'c')."""
    current = d
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is None:
            return default
    return current


def coerce_int(value, default: int = 0) -> int:
    """Convert value to int safely."""
    if isinstance(value, (int, float)):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def coerce_float(value, default: Optional[float] = None) -> Optional[float]:
    """Convert value to float safely."""
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def flatten_str(value) -> str:
    """Extract a string from str, dict, or list."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("lv", "") or value.get("en", "") or ""
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    return str(value) if value is not None else ""


def extract_budget_places(bp) -> int:
    """Normalize budget_places to a single integer total."""
    if bp is None:
        return 0
    if isinstance(bp, int):
        return bp
    if isinstance(bp, dict):
        return sum(coerce_int(v) for v in bp.values() if isinstance(v, (int, float, str)))
    if isinstance(bp, list):
        total = 0
        for item in bp:
            if isinstance(item, dict):
                total += coerce_int(item.get("count", item.get("places", 0)))
            elif isinstance(item, (int, float)):
                total += int(item)
        return total
    return 0


def extract_fee(fee_raw) -> Optional[float]:
    """Normalize annual fee to a float."""
    if fee_raw is None:
        return None
    if isinstance(fee_raw, (int, float)):
        return float(fee_raw)
    if isinstance(fee_raw, dict):
        # Take the minimum non-null value
        vals = [coerce_float(v) for v in fee_raw.values() if v is not None]
        vals = [v for v in vals if v is not None and v > 0]
        return min(vals) if vals else None
    return coerce_float(fee_raw)


def extract_duration(dur_raw) -> int:
    """Normalize duration_years to an integer."""
    if isinstance(dur_raw, int):
        return dur_raw
    if isinstance(dur_raw, float):
        return int(dur_raw)
    if isinstance(dur_raw, dict):
        vals = [coerce_int(v) for v in dur_raw.values() if v]
        return min(vals) if vals else 4
    return 4  # RTU bachelor default


def get_label(mapping: dict, key: str, field: str = "label") -> str:
    """Get label from taxonomy mapping, fallback to key."""
    entry = mapping.get(key, {})
    if isinstance(entry, dict):
        return entry.get(field, key)
    return key
