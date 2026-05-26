"""
RTU Study Programme AI Recommender
app.py — Main Streamlit application entry point.

Run with:
    streamlit run app.py

Environment variables (set in .env or system):
    GEMINI_API_KEY  — Google Gemini API key (free tier)
    RTU_DATASET_DIR — Optional custom dataset directory path
"""

import os
import sys
from pathlib import Path

# Load .env before anything else
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st
import pandas as pd

# ── Page config (must be the first Streamlit call) ─────────────────────────
st.set_page_config(
    page_title="RTU Studiju Programmu AI Ieteicējs",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.rtu.lv",
        "Report a bug": None,
        "About": "RTU Study Programme AI Recommender — v1.0",
    },
)

# ── Project imports (after path setup) ────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_all_programmes, extract_taxonomy
from scoring import rank_programmes, score_all_programmes, breakdown_summary
from ai_explanations import generate_ai_explanation
from ui_components import (
    render_hero, render_stats_bar, render_result_card,
    render_comparison_table, render_programme_table,
    render_empty_results, loading_spinner_context,
)
from utils import (
    INTEREST_DOMAINS, STRENGTH_TAGS, PERSONALITY_TRAITS, INDUSTRY_SECTORS,
    LANG_LABELS, DIFFICULTY_LEVELS,
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — modern, polished look
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
        color: white;
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label { color: #e0e7ff !important; }

    /* Cards */
    [data-testid="stExpander"] {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        margin-bottom: 6px;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover { transform: translateY(-1px); }

    /* Metrics */
    [data-testid="stMetric"] {
        background: #f8fafc;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #e2e8f0;
    }
    [data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    [data-testid="stMetricValue"] { font-size: 0.95rem !important; font-weight: 700 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* Hide Streamlit watermark */
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INITIALISATION
# ─────────────────────────────────────────────────────────────────────────────

def _init_session():
    defaults = {
        "programmes": [],
        "load_stats": {},
        "taxonomy": {},
        "results": [],
        "saved_programmes": set(),
        "saved_programme_data": {},
        "last_scores": {},
        "search_done": False,
        "student_profile": {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING (cached)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner="Ielāde datu kopu…")
def _load_data() -> tuple[list, dict, dict]:
    programmes, stats = load_all_programmes()
    taxonomy = extract_taxonomy(programmes)
    return programmes, stats, taxonomy


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar(programmes: list[dict], taxonomy: dict) -> dict:
    """Render sidebar with filters. Returns filter dict."""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding:10px 0 20px 0;">
              <div style="font-size:2.5rem;">🎓</div>
              <div style="font-size:1.1rem; font-weight:700; color:white;">RTU Ieteicējs</div>
              <div style="font-size:0.7rem; color:#a5b4fc; margin-top:2px;">
                Riga Technical University
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("### 🔧 Filtri")

        # Faculty filter
        faculties = sorted({p.get("faculty", "") for p in programmes if p.get("faculty")})
        selected_faculties = st.multiselect(
            "🏛️ Fakultāte",
            options=faculties,
            default=[],
            placeholder="Visas fakultātes",
            key="filter_faculties",
        )

        # Language filter
        lang_opts = {"lv": "🇱🇻 Latviešu", "en": "🇬🇧 Angļu", "ru": "🇷🇺 Krievu"}
        selected_langs = st.multiselect(
            "🌐 Studiju valoda",
            options=list(lang_opts.keys()),
            format_func=lambda k: lang_opts[k],
            default=[],
            placeholder="Visas valodas",
            key="filter_langs",
        )

        # Location filter
        all_locations = sorted({
            loc for p in programmes
            for loc in (p.get("locations") or [])
        })
        selected_locations = st.multiselect(
            "📍 Atrašanās vieta",
            options=all_locations,
            default=[],
            placeholder="Visas vietas",
            key="filter_locations",
        )

        # Program type filter
        prog_types = sorted({p.get("program_type", "") for p in programmes if p.get("program_type")})
        selected_types = st.multiselect(
            "📚 Programmas tips",
            options=prog_types,
            default=[],
            placeholder="Visi tipi",
            key="filter_types",
        )

        st.markdown("---")
        st.markdown("### ⚡ Ātrās opcijas")

        no_exam = st.toggle("✅ Tikai bez iestājpārbaudījuma", value=False)
        budget_only = st.toggle("🎓 Tikai ar budžeta vietām", value=False)

        st.markdown("---")

        # Saved programmes count
        n_saved = len(st.session_state.get("saved_programmes", set()))
        if n_saved > 0:
            st.markdown(
                f"<div style='color:#86efac; font-weight:600;'>❤️ {n_saved} saglabātas programmas</div>",
                unsafe_allow_html=True,
            )
            if st.button("🗑️ Notīrīt saglabātās", key="clear_saved"):
                st.session_state["saved_programmes"] = set()
                st.session_state["saved_programme_data"] = {}
                st.rerun()

        st.markdown("---")
        st.caption("📂 Datu kopa: RTU bakalaura programmas")
        st.caption(f"📦 {len(programmes)} programmas ielādētas")

    return {
        "faculties": selected_faculties or None,
        "languages": selected_langs or None,
        "locations": selected_locations or None,
        "program_types": selected_types or None,
        "no_exam_only": no_exam,
        "budget_only": budget_only,
    }


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT PROFILE FORM
# ─────────────────────────────────────────────────────────────────────────────

def render_student_form(programmes: list[dict], taxonomy: dict) -> dict | None:
    """
    Render the student profile form.
    Returns student profile dict on submission, None otherwise.
    """
    st.markdown("### 📝 Aizpildi savu profilu")
    st.caption("Jo precīzāk aizpildi, jo labāki ieteikumi. Visi lauki ir neobligāti.")

    with st.form("student_profile_form", clear_on_submit=False):
        # ── Row 1: Interests & Strengths ─────────────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**💡 1. Interešu jomas** (izvēlies līdz 5)")
            interests = st.multiselect(
                "Kas tevi interesē visvairāk?",
                options=list(INTEREST_DOMAINS.keys()),
                format_func=lambda k: INTEREST_DOMAINS[k]["label"],
                max_selections=5,
                key="form_interests",
                label_visibility="collapsed",
            )

            st.markdown("**💪 2. Stiprās puses & Mācību priekšmeti**")
            strengths = st.multiselect(
                "Kuros priekšmetos esi stiprāks?",
                options=list(STRENGTH_TAGS.keys()),
                format_func=lambda k: STRENGTH_TAGS[k]["label"],
                max_selections=6,
                key="form_strengths",
                label_visibility="collapsed",
            )

        with col2:
            st.markdown("**🧠 3. Personības tips** (izvēlies līdz 4)")
            personality = st.multiselect(
                "Kā Tu raksturotu sevi?",
                options=list(PERSONALITY_TRAITS.keys()),
                format_func=lambda k: PERSONALITY_TRAITS[k]["label"],
                max_selections=4,
                key="form_personality",
                label_visibility="collapsed",
            )

            st.markdown("**🏭 4. Vēlamās nozares**")
            sectors = st.multiselect(
                "Kurās nozarēs vēlies strādāt?",
                options=list(INDUSTRY_SECTORS.keys()),
                format_func=lambda k: INDUSTRY_SECTORS[k]["label"],
                max_selections=5,
                key="form_sectors",
                label_visibility="collapsed",
            )

        st.divider()

        # ── Row 2: Preferences ────────────────────────────────────────────
        col3, col4, col5 = st.columns(3)

        with col3:
            st.markdown("**🌐 5. Vēlamā studiju valoda**")
            preferred_language = st.selectbox(
                "Studiju valoda",
                options=["lv", "en", "ru", "any"],
                format_func=lambda k: {
                    "lv": "🇱🇻 Latviešu",
                    "en": "🇬🇧 Angļu",
                    "ru": "🇷🇺 Krievu",
                    "any": "🌍 Jebkura",
                }[k],
                key="form_language",
                label_visibility="collapsed",
            )

            st.markdown("**📊 6. Vēlamā grūtības pakāpe**")
            preferred_difficulty = st.select_slider(
                "Grūtības pakāpe",
                options=["low", "medium", "medium_high", "high"],
                value="medium",
                format_func=lambda k: DIFFICULTY_LEVELS.get(k, k),
                key="form_difficulty",
                label_visibility="collapsed",
            )

        with col4:
            st.markdown("**🔢 7. Vai patīk matemātika?**")
            math_friendly = st.toggle(
                "Matemātika ir stiprā puse", key="form_math", value=False
            )

            st.markdown("**🎨 8. Vai patīk radošs darbs / dizains?**")
            creative = st.toggle(
                "Radošums ir svarīgs", key="form_creative", value=False
            )

            st.markdown("**🔬 9. Vai interesē pētnieciskās studijas?**")
            research = st.toggle(
                "Vēlos pētnieciskās studijas", key="form_research", value=False
            )

        with col5:
            st.markdown("**🌍 10. Starptautiskas iespējas?**")
            international = st.toggle(
                "Vēlos studēt / strādāt ārzemēs", key="form_intl", value=False
            )

            st.markdown("**📝 11. Iestājpārbaudījumi**")
            exam_ok = st.toggle(
                "Esmu gatavs iestājpārbaudījumam", key="form_exam", value=True
            )

            st.markdown("**🤝 12. Darba stils**")
            teamwork = st.select_slider(
                "Komandas darbs ↔ Patstāvīgs darbs",
                options=["team", "both", "independent"],
                value="both",
                format_func=lambda k: {
                    "team": "👥 Komandas darbs",
                    "both": "🔄 Abos labi",
                    "independent": "🦅 Patstāvīgs",
                }[k],
                key="form_teamwork",
                label_visibility="collapsed",
            )

        # ── Career text ───────────────────────────────────────────────────
        st.markdown("**🚀 13. Karjeras mērķi (brīvs teksts)**")
        career_text = st.text_area(
            "Apraksti savas karjeras idejas (neobligāti):",
            placeholder="Piemēram: 'Vēlos kļūt par datorsistēmu inženieri un strādāt AI jomā' vai 'Interesē arhitektūra un ilgtspējīga būvniecība'",
            max_chars=300,
            height=80,
            key="form_career_text",
            label_visibility="collapsed",
        )

        st.divider()

        # ── Submit button ─────────────────────────────────────────────────
        c_btn1, c_btn2, c_btn3 = st.columns([2, 2, 1])
        with c_btn2:
            submitted = st.form_submit_button(
                "🔍 Atrast manai personībai atbilstošas programmas!",
                use_container_width=True,
                type="primary",
            )
        with c_btn3:
            load_test = st.form_submit_button("📋 Ielādēt testa profilu", use_container_width=True)

    if load_test:
        _load_test_profile()
        st.rerun()

    if submitted:
        profile = {
            "interests": interests,
            "strengths": strengths,
            "personality": personality,
            "sectors": sectors,
            "preferred_language": preferred_language,
            "preferred_difficulty": preferred_difficulty,
            "math_friendly": math_friendly,
            "creative": creative,
            "research_oriented": research,
            "international": international,
            "exam_ok": exam_ok,
            "teamwork": teamwork,
            "career_text": career_text,
        }
        return profile

    return None


def _load_test_profile():
    """Load a random test profile from test_profiles.json."""
    import json
    import random
    test_file = Path(__file__).parent / "test_profiles.json"
    try:
        with open(test_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        profiles = data.get("profiles", [])
        if profiles:
            chosen = random.choice(profiles)
            profile = chosen.get("profile", {})
            # Map to session state keys
            mapping = {
                "form_interests": "interests",
                "form_strengths": "strengths",
                "form_personality": "personality",
                "form_sectors": "sectors",
                "form_language": "preferred_language",
                "form_difficulty": "preferred_difficulty",
                "form_math": "math_friendly",
                "form_creative": "creative",
                "form_research": "research_oriented",
                "form_intl": "international",
                "form_exam": "exam_ok",
                "form_teamwork": "teamwork",
                "form_career_text": "career_text",
            }
            for form_key, profile_key in mapping.items():
                if profile_key in profile:
                    st.session_state[form_key] = profile[profile_key]
            st.toast(f"✅ Testa profils ielādēts: {chosen.get('name', 'Nezināms')}")
    except Exception as e:
        st.toast(f"⚠️ Neizdevās ielādēt testa profilu: {e}", icon="⚠️")


# ─────────────────────────────────────────────────────────────────────────────
# RESULTS RENDERER
# ─────────────────────────────────────────────────────────────────────────────

def render_results(student: dict, programmes: list[dict], filters: dict):
    """Score programmes and render the top 3 result cards."""
    with loading_spinner_context("🔍 Aprēķina atbilstību visām programmām…"):
        top_results = rank_programmes(student, programmes, top_n=3, filters=filters)
        all_scored = score_all_programmes(student, programmes, filters=filters)

    # Store scores in session state
    scores_map = {r["programme"].get("id", ""): r["score"] for r in all_scored}
    st.session_state["last_scores"] = scores_map

    if not top_results:
        st.warning(
            "⚠️ Nav atrasta neviena programma ar pašreizējiem filtriem. "
            "Mēģini mainīt filtrus vai ievadīt vairāk profila informāciju."
        )
        return

    # Score stats
    top_score = top_results[0]["score"] if top_results else 0
    avg_score = sum(r["score"] for r in top_results) / len(top_results) if top_results else 0

    st.success(
        f"✅ Atrasta labākā atbilstība: **{top_score:.0f}%** "
        f"(vidēji top-3: {avg_score:.0f}%)"
    )

    # Confidence indicator
    if top_score >= 75:
        st.markdown(
            "🟢 **Augsta pārliecība** — Profils labi atbilst šīm programmām.",
            unsafe_allow_html=False,
        )
    elif top_score >= 50:
        st.markdown("🟡 **Vidēja pārliecība** — Laba atbilstība ar dažiem kompromisiem.")
    else:
        st.markdown(
            "🟠 **Zema pārliecība** — Apsver papildinot profilu vai mainīt preferences."
        )

    st.divider()

    # Render each card
    for rank_i, result in enumerate(top_results, start=1):
        prog = result["programme"]
        score = result["score"]
        breakdown = result["breakdown"]
        bd_summary = breakdown_summary(breakdown)

        # Generate AI explanation (with fallback)
        with st.spinner(f"✨ Ģenerē AI paskaidrojumu #{rank_i}…"):
            explanation, is_ai = generate_ai_explanation(
                student_profile=student,
                programme=prog,
                scoring_breakdown=breakdown,
            )

        render_result_card(
            rank=rank_i,
            programme=prog,
            score=score,
            breakdown=breakdown,
            ai_explanation=explanation,
            is_ai=is_ai,
            summary=bd_summary,
            on_save=_save_programme,
        )


def _save_programme(prog_id: str, programme: dict):
    """Toggle save state for a programme."""
    saved = st.session_state.get("saved_programmes", set())
    saved_data = st.session_state.get("saved_programme_data", {})
    if prog_id in saved:
        saved.discard(prog_id)
        saved_data.pop(prog_id, None)
        st.toast("Programma noņemta no saglabātajām.", icon="🗑️")
    else:
        saved.add(prog_id)
        saved_data[prog_id] = programme
        st.toast(f"'{programme.get('name', prog_id)}' saglabāta!", icon="❤️")
    st.session_state["saved_programmes"] = saved
    st.session_state["saved_programme_data"] = saved_data
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# COMPARE TAB
# ─────────────────────────────────────────────────────────────────────────────

def render_compare_tab():
    """Render the comparison view."""
    saved_data = st.session_state.get("saved_programme_data", {})
    scores = st.session_state.get("last_scores", {})
    saved_list = list(saved_data.values())

    if not saved_list:
        st.info(
            "👆 Saglabā programmas no rezultātiem, noklikšķinot uz '🤍 Saglabāt', "
            "un tad atgriezies šeit, lai salīdzinātu."
        )
        return

    st.markdown(f"### ⚖️ Salīdzinājums ({len(saved_list)} programmas)")
    from ui_components import render_comparison_table
    render_comparison_table(saved_list, scores)


# ─────────────────────────────────────────────────────────────────────────────
# ALL PROGRAMMES TAB
# ─────────────────────────────────────────────────────────────────────────────

def render_all_programmes_tab(programmes: list[dict]):
    """Render searchable table of all programmes."""
    st.markdown("### 📋 Visas RTU Bakalaura Programmas")

    # Search bar
    search = st.text_input(
        "🔍 Meklēt programmu pēc nosaukuma vai apraksta",
        placeholder="Piemēram: 'datorzinātne', 'aviation', 'arhitektūra'...",
        key="search_bar",
    )

    filtered = programmes
    if search:
        search_l = search.lower()
        filtered = [
            p for p in programmes
            if (
                search_l in (p.get("name") or "").lower()
                or search_l in (p.get("name_en") or "").lower()
                or search_l in (p.get("description") or "").lower()
                or search_l in (p.get("faculty") or "").lower()
                or any(search_l in kw.lower() for kw in p.get("keywords", []))
            )
        ]

    st.caption(f"Rāda {len(filtered)} no {len(programmes)} programmām")

    # Sort options
    sort_col, _ = st.columns([2, 3])
    with sort_col:
        sort_by = st.selectbox(
            "Kārtot pēc:",
            ["Atbilstība %" , "Nosaukums A–Z", "Gada maksa ↑", "Budžeta vietas ↓"],
            key="sort_by",
        )

    scores = st.session_state.get("last_scores", {})

    if sort_by == "Atbilstība %" and scores:
        filtered = sorted(filtered, key=lambda p: scores.get(p.get("id", ""), 0), reverse=True)
    elif sort_by == "Nosaukums A–Z":
        filtered = sorted(filtered, key=lambda p: p.get("name", ""))
    elif sort_by == "Gada maksa ↑":
        filtered = sorted(filtered, key=lambda p: p.get("annual_fee_eur") or 0)
    elif sort_by == "Budžeta vietas ↓":
        filtered = sorted(filtered, key=lambda p: p.get("budget_places", 0), reverse=True)

    from ui_components import render_programme_table
    render_programme_table(filtered, scores if scores else None)


# ─────────────────────────────────────────────────────────────────────────────
# ABOUT TAB
# ─────────────────────────────────────────────────────────────────────────────

def render_about_tab():
    """Render the about / help tab."""
    st.markdown(
        """
## ℹ️ Par šo rīku

**RTU Studiju Programmu AI Ieteicējs** palīdz vidusskolas skolēniem izvēlēties
piemērotākās RTU bakalaura studiju programmas, pamatojoties uz:

- Personīgajām interesēm un stiprajām pusēm
- Personības tipu un darba stilu
- Karjeras mērķiem un nozares preferences
- Studiju valodu un grūtības pakāpes preferenci

---

### 🏗️ Kā tas strādā

**1. Datu ielāde**
Sistēma automātiski ielādē visas JSON programmu datnes no `datasets/` mapes.
Tiek atbalstīti visi 4 RTU datu formāti ar dažādām shēmām.

**2. Profila aizpildīšana**
Students aizpilda interaktīvu formu ar savām interesēm, spējām un preferncēm.

**3. Svērtā vērtēšana**
Katra programma saņem vērtējumu, pamatojoties uz 13 faktoriem:

| Faktors | Svars | Sods |
|---------|-------|------|
| Interešu jomas | +4 uz sakritību | — |
| Stiprās puses | +3 uz sakritību | — |
| Personība | +2 uz sakritību | — |
| Nozares | +3 uz sakritību | — |
| Studiju valoda | +2 | −20% (nav pieejama) |
| Grūtības pakāpe | +2 | −10% (par grūtu) |
| Pētnieciskā | +2 | — |
| Starptautisks | +2 | — |
| Radošais komponents | +2 | — |
| Matemātika | +2 | −8% (nemīl, bet intensīva) |
| Iestājpārbaudījums | +2 | −15% (neatbilst) |
| Komandas darbs | +1 | — |

**4. AI Paskaidrojums**
Gemini API ģenerē personalizētu paskaidrojumu katrai top-3 programmai.
Ja API nav pieejams, tiek ģenerēts lokāls paskaidrojums.

---

### 🚀 Kā palaist lokāli

```bash
# 1. Klonē projektu
git clone <repo-url>
cd rtu-study-recommender

# 2. Instalē atkarības
pip install -r requirements.txt

# 3. Konfigurē API atslēgu
cp .env.example .env
# Rediģē .env un pievieno savu GEMINI_API_KEY

# 4. Palaid
streamlit run app.py
```

---

### 📁 Jaunu programmu pievienošana

Lai pievienotu jaunas RTU programmas:
1. Izveido JSON datni ar programmu datiem (jebkurā no 4 atbalstītajiem formātiem)
2. Ieliec datni `datasets/` mapē
3. Restartē lietotni — datne tiks automātiski atklāta un ielādēta

---

### ⚠️ Ierobežojumi

- Dati balstīti uz 2026. gada RTU programmu aprakstiem
- AI paskaidrojums ir informatīvs — vienmēr pārbaudi aktuālo info RTU mājas lapā
- Ieteikumi ir orientējoši — galīgo izvēli veic students
""",
        unsafe_allow_html=False,
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    _init_session()

    # ── Load data ─────────────────────────────────────────────────────────
    programmes, stats, taxonomy = _load_data()

    if not programmes:
        st.error(
            "❌ Nav atrasta neviena programma! "
            "Pārliecinies, ka `datasets/` mapē ir RTU JSON datnes."
        )
        st.info(
            "**Kā pievienot datnes:**\n"
            "1. Atver `rtu-study-recommender/datasets/` mapi\n"
            "2. Iekopē RTU JSON datnes no `C:\\Users\\ernes\\Downloads\\rtu programmas\\`\n"
            "3. Restartē lietotni"
        )
        st.stop()

    # ── Hero ──────────────────────────────────────────────────────────────
    from ui_components import render_hero, render_stats_bar
    render_hero()

    # ── Sidebar (filters) ─────────────────────────────────────────────────
    filters = render_sidebar(programmes, taxonomy)

    # ── Main content tabs ─────────────────────────────────────────────────
    tab_search, tab_compare, tab_all, tab_about = st.tabs([
        "🔍 Atrast Programmu",
        "⚖️ Salīdzināt",
        "📋 Visas Programmas",
        "ℹ️ Par Rīku",
    ])

    # ── TAB 1: Search ─────────────────────────────────────────────────────
    with tab_search:
        render_stats_bar(stats, len(programmes))
        st.divider()

        profile = render_student_form(programmes, taxonomy)

        if profile:
            st.session_state["student_profile"] = profile
            st.session_state["search_done"] = True

        if st.session_state.get("search_done") and st.session_state.get("student_profile"):
            st.markdown("---")
            st.markdown("## 🏆 Tavai personībai atbilstošākās programmas")
            render_results(
                student=st.session_state["student_profile"],
                programmes=programmes,
                filters=filters,
            )
        elif not st.session_state.get("search_done"):
            from ui_components import render_empty_results
            render_empty_results()

    # ── TAB 2: Compare ────────────────────────────────────────────────────
    with tab_compare:
        render_compare_tab()

    # ── TAB 3: All programmes ─────────────────────────────────────────────
    with tab_all:
        render_all_programmes_tab(programmes)

    # ── TAB 4: About ──────────────────────────────────────────────────────
    with tab_about:
        render_about_tab()


if __name__ == "__main__":
    main()
